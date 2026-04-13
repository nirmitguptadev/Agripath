import json
import re
import requests
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.conf import settings
import os
import time
import datetime
from PIL import Image
from django.conf import settings
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from core.ai_fallback import generate_ai_response, analyze_plant_image
from core.news_api import get_agri_news

OPENWEATHER_API_KEY = getattr(settings, 'OPENWEATHER_API_KEY', None)

def _is_rain(icon): return icon[:2] in ('09', '10')
def _is_storm(icon): return icon[:2] == '11'
def _is_snow(icon): return icon[:2] == '13'
def _is_rain_or_storm(icon): return icon[:2] in ('09', '10', '11')

def get_seasonal_thresholds(dt_timestamp=None):
    if dt_timestamp:
        month = datetime.datetime.fromtimestamp(dt_timestamp).month
    else:
        month = datetime.datetime.now().month

    if month in (12, 1, 2):  # Winter
        return (30, 35, 10, 5)
    elif month in (3, 4, 5, 6):  # Summer / Pre-Monsoon
        return (38, 42, 18, 10)
    else:  # Monsoon / Post-Monsoon (7,8,9,10,11)
        return (35, 38, 15, 8)

def get_weather_style(icon_code):
    """
    Maps OpenWeatherMap icon code to FontAwesome class and color.
    """
    mapping = {
        '01d': {'icon': 'fa-sun', 'color': '#f59e0b', 'animation': 'spin-slow'},       # Clear Day - Orange
        '01n': {'icon': 'fa-moon', 'color': '#cbd5e1', 'animation': 'pulse'},          # Clear Night - Light Grey
        '02d': {'icon': 'fa-cloud-sun', 'color': '#fcd34d', 'animation': 'float'},     # Few Clouds Day
        '02n': {'icon': 'fa-cloud-moon', 'color': '#94a3b8', 'animation': 'float'},    # Few Clouds Night
        '03d': {'icon': 'fa-cloud', 'color': '#e2e8f0', 'animation': 'float'},         # Scattered Clouds
        '03n': {'icon': 'fa-cloud', 'color': '#64748b', 'animation': 'float'},
        '04d': {'icon': 'fa-cloud', 'color': '#94a3b8', 'animation': 'float'},         # Broken Clouds
        '04n': {'icon': 'fa-cloud', 'color': '#475569', 'animation': 'float'},
        '09d': {'icon': 'fa-cloud-showers-heavy', 'color': '#3b82f6', 'animation': 'pulse'}, # Shower Rain
        '09n': {'icon': 'fa-cloud-showers-heavy', 'color': '#1d4ed8', 'animation': 'pulse'},
        '10d': {'icon': 'fa-cloud-sun-rain', 'color': '#60a5fa', 'animation': 'pulse'}, # Rain Day
        '10n': {'icon': 'fa-cloud-moon-rain', 'color': '#3b82f6', 'animation': 'pulse'}, # Rain Night
        '11d': {'icon': 'fa-bolt', 'color': '#fbbf24', 'animation': 'shake'},          # Thunderstorm
        '11n': {'icon': 'fa-bolt', 'color': '#fbbf24', 'animation': 'shake'},
        '13d': {'icon': 'fa-snowflake', 'color': '#bae6fd', 'animation': 'spin'},      # Snow
        '13n': {'icon': 'fa-snowflake', 'color': '#bae6fd', 'animation': 'spin'},
        '50d': {'icon': 'fa-smog', 'color': '#94a3b8', 'animation': 'float'},          # Mist
        '50n': {'icon': 'fa-smog', 'color': '#64748b', 'animation': 'float'},
    }
    return mapping.get(icon_code, {'icon': 'fa-cloud', 'color': '#94a3b8', 'animation': ''})

def get_current_weather_data(city_name):
    if not OPENWEATHER_API_KEY: return None, "Weather API key not configured."
    base_url = "http://api.openweathermap.org/data/2.5/weather"
    params = {'q': city_name, 'appid': OPENWEATHER_API_KEY, 'units': 'metric'}
    try:
        response = requests.get(base_url, params=params)
        if response.status_code == 404: return None, f"City '{city_name}' not found."
        response.raise_for_status()
        data = response.json()
        
        # Get icon style
        icon_code = data["weather"][0]["icon"]
        icon_style = get_weather_style(icon_code)

        return {
            "lat": data["coord"]["lat"],
            "lon": data["coord"]["lon"],
            "city": data.get("name"), 
            "temperature": data["main"]["temp"],
            "description": data["weather"][0]["description"], 
            "icon": icon_code,
            "icon_style": icon_style, # Add style data
            "humidity": data["main"]["humidity"],
            "pressure": data["main"]["pressure"], 
            "wind_speed": data["wind"]["speed"], 
            "visibility": data.get("visibility") 
        }, None
    except requests.exceptions.RequestException as e:
        print(f"🔴 Weather API request error: {e}")
        return None, "Could not connect to the current weather service."

# Update get_alerts_and_forecast to capture wind/pressure/humidity/min/max temp for forecast
def get_alerts_and_forecast(lat, lon):
    if not OPENWEATHER_API_KEY: return {'forecast': [], 'alerts': []}, "API key missing."
    
    # Use the Free Tier 5-Day / 3-Hour Forecast API endpoint
    base_url = "http://api.openweathermap.org/data/2.5/forecast"
    params = {
        'lat': lat, 
        'lon': lon, 
        'appid': OPENWEATHER_API_KEY, 
        'units': 'metric'
    }

    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        data = response.json()
        
        # Aggregate ALL 3-hour slots by day to get true daily max/min temps
        # (not just noon, which misses peak afternoon heat)
        daily_data = {}
        for item in data.get('list', []):
            date_str = item['dt_txt'].split(' ')[0]  # 'YYYY-MM-DD'
            t_max = item['main']['temp_max']
            t_min = item['main']['temp_min']
            icon  = item['weather'][0]['icon']
            desc  = item['weather'][0]['description']
            hum   = item['main']['humidity']
            dt    = item.get('dt')

            if date_str not in daily_data:
                daily_data[date_str] = {
                    'date': dt,
                    'max_temp': t_max,
                    'min_temp': t_min,
                    'description': desc,
                    'icon': icon,
                    'humidity': hum,
                    # track worst icon priority: storm > rain > rest
                    'icon_priority': 0,
                }
            else:
                d = daily_data[date_str]
                if t_max > d['max_temp']: d['max_temp'] = t_max
                if t_min < d['min_temp']: d['min_temp'] = t_min
                # Upgrade icon to worst condition of the day
                prio = 2 if icon[:2] == '11' else 1 if icon[:2] in ('09', '10') else 0
                if prio > d['icon_priority']:
                    d['icon_priority'] = prio
                    d['icon'] = icon
                    d['description'] = desc

        forecast = [v for _, v in sorted(daily_data.items())][:5]
            
        # Generating actionable alerts from forecast based on REAL weather data
        alerts = []
        for i, item in enumerate(forecast):
            icon = item['icon']
            day_offset = "Today" if i == 0 else f"in {i} day{'s' if i > 1 else ''}"
            
            high_heat, severe_heat, cold_warning, frost_danger = get_seasonal_thresholds(item['date'])

            if _is_storm(icon):
                alerts.append({'message': f"⛈️ Thunderstorm expected {day_offset}. Secure equipment and support tall crops.", 'type': 'danger'})
            elif _is_rain(icon):
                alerts.append({'message': f"💧 Rain expected {day_offset}. Delay fertilizers/pesticides to prevent runoff.", 'type': 'warning'})
            
            if item['max_temp'] >= severe_heat:
                alerts.append({'message': f"🔥 Severe heat ({item['max_temp']}°C) expected {day_offset}. Extreme danger, halt field work.", 'type': 'danger'})
            elif item['max_temp'] >= high_heat:
                alerts.append({'message': f"🔥 High heat ({item['max_temp']}°C) expected {day_offset}. Irrigate early, avoid midday spraying.", 'type': 'warning'})
            
            if item['min_temp'] <= frost_danger:
                alerts.append({'message': f"❄️ Frost warning ({item['min_temp']}°C) expected {day_offset}. Protect early vegetative crops.", 'type': 'danger'})
            elif item['min_temp'] <= cold_warning:
                alerts.append({'message': f"🧊 Abnormal cold ({item['min_temp']}°C) expected {day_offset}. Monitor seedling health.", 'type': 'info'})

        return {'forecast': forecast, 'alerts': alerts}, None

    except requests.exceptions.RequestException as e:
        print(f"🔴 OpenWeatherMap Forecast API request error: {e}")
        return {'forecast': [], 'alerts': []}, "Could not connect to the forecast service."
    


@login_required
def Weather(request):
    try:
        location = request.user.profile.location
    except:
        location = None

    if not location:
        return render(request, 'weather.html', {
            'error': 'कृपया अपनी प्रोफाइल में अपना स्थान (Location) अपडेट करें।'
        })

    # Step 1: Get location coordinates and current conditions
    current_data, error = get_current_weather_data(location)
    if error:
        return render(request, 'weather.html', {'error': f'{error}'})

    lat = current_data.get('lat')
    lon = current_data.get('lon')
    
    # Step 2: Get forecast and alerts using coordinates
    weather_data, alert_error = get_alerts_and_forecast(lat, lon)

    if alert_error:
        # Render with a partial error if only the forecast/alert failed
        return render(request, 'weather.html', {
            'location': location,
            'current_data': current_data,
            'forecast': [],
            'alerts': [],
            'error': alert_error
        })

    return render(request, 'weather.html', {
        'location': location,
        'current_data': current_data,
        'forecast': weather_data.get('forecast', []),
        'alerts': weather_data.get('alerts', [])
    })

@login_required
def Policies(request):
    try:
        location = request.user.profile.location
    except:
        location = "India"

    if not location:
        return render(request, 'Policies.html', {'error': 'Location missing.'})

    categories = [
        "Crop Insurance & Security",
        "Financial Aid & Loans",
        "Modern Agriculture & Technology",
        "Farmer Welfare"
    ]

    prompt = f"""
    Act as an Indian Agriculture Expert. Provide government schemes for farmers in {location}.
    Return a JSON list with exactly these 4 'use_case' categories:
    {", ".join(categories)}

    For each category, provide 2 relevant schemes.
    
    JSON Format:
    [
      {{
        "use_case": "Heading from list above",
        "schemes": [
          {{ "name": "Scheme Name", "description": "1 sentence", "benefits": "1 sentence", "link": "URL" }}
        ]
      }}
    ]
    Output ONLY raw JSON. No markdown, no intro text.
    """

    try:
        raw_text = generate_ai_response(prompt)
        
        # 1. Clean the response
        json_match = re.search(r'\[.*\]', raw_text, re.DOTALL)
        clean_json = json_match.group(0) if json_match else raw_text
        policies_data = json.loads(clean_json)

        # 2. THE FIX: Snap gibberish back to real Hindi headings
        for i, item in enumerate(policies_data):
            # Map both 'usecase' and 'use_case'
            current_title = item.get('use_case') or item.get('usecase') or ""
            
            # If the title is gibberish or not in our list, assign from our 'categories' list
            if i < len(categories):
                item['use_case'] = categories[i]
            else:
                item['use_case'] = current_title

        return render(request, 'Policies.html', {
            'location': location,
            'policies_by_usecase': policies_data
        })

    except Exception as e:
        print(f"Error: {e}")
        return render(request, 'Policies.html', {'error': 'Failed to retrieve data from server.'})



def Fertilizer(request):
    return render(request,'SFR.html')

def about(request):
    return render(request,'about.html')


@login_required
def plant_doctor(request):
    diagnosis = None
    error = None
    
    if request.method == 'POST' and request.FILES.get('plant_image'):
        image_file = request.FILES['plant_image']
        
        # 1. Save locally temporarily
        # We need a physical file for Gemini (or at least it's easier to handle resizing)
        # Use a safe temporary directory
        temp_dir = os.path.join(settings.MEDIA_ROOT, 'temp_uploads')
        os.makedirs(temp_dir, exist_ok=True)
        
        temp_filename = f"temp_plant_{int(time.time())}_{image_file.name}"
        temp_path = os.path.join(temp_dir, temp_filename)
        
        try:
            # Save the uploaded file
            with open(temp_path, 'wb+') as destination:
                for chunk in image_file.chunks():
                    destination.write(chunk)
            
            # Resize image to max 800x800 to save bandwidth/compute
            with Image.open(temp_path) as img:
                img.thumbnail((800, 800))
                img.save(temp_path)
            
            # 2. Analyze with Gemini
            diagnosis = analyze_plant_image(temp_path)
            
        except Exception as e:
            print(f"Error processing image: {e}")
            error = "An error occurred while processing the image. Please try again."
        
        finally:
            # 3. Cleanup: Delete the file
            if os.path.exists(temp_path):
                os.remove(temp_path)
    
    return render(request, 'plant_doctor.html', {
        'diagnosis': diagnosis, 
        'error': error
    })

from django.shortcuts import redirect
from django.contrib import messages

@login_required
def toggle_persona(request):
    if request.method == 'POST':
        profile = request.user.profile
        requested_type = request.POST.get('user_type')
        if requested_type in ['Farmer', 'Hobbyist']:
            new_type = requested_type
        else:
            # Fallback toggle
            new_type = 'Hobbyist' if profile.user_type == 'Farmer' else 'Farmer'
        
        if profile.user_type != new_type:
            profile.user_type = new_type
            profile.save()
            messages.success(request, f'Switched to {new_type} mode.')
    return redirect('dashboard')

from django.http import JsonResponse

@login_required
def api_weather_alerts(request):
    try:
        location = request.user.profile.location
    except:
        location = None
        
    if not location:
        return JsonResponse({'alerts': []})
        
    current_data, error = get_current_weather_data(location)
    if error or not current_data:
        return JsonResponse({'alerts': []})
        
    lat = current_data.get('lat')
    lon = current_data.get('lon')
    weather_data, alert_error = get_alerts_and_forecast(lat, lon)
    
    if alert_error:
        return JsonResponse({'alerts': []})
        
    # We map them into single string sentences for easy marquee scroll
    alerts = weather_data.get('alerts', [])
    text_alerts = [a['message'] for a in alerts]
    
    return JsonResponse({'alerts': text_alerts})


@login_required
def news_page(request):
    news_items = get_agri_news()
    return render(request, 'news.html', {'news_items': news_items})
