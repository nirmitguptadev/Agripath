import json
import re
import requests
import google.generativeai as genai
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.conf import settings

# --- Configure GenAI for this app ---
try:
    genai.configure(api_key=settings.GEMINI_API_KEY)
    # Using flash model for speed
    POLICY_MODEL = genai.GenerativeModel('gemini-2.5-flash-lite') 
except Exception as e:
    print(f"Error configuring Gemini in home/views: {e}")
    POLICY_MODEL = None

OPENWEATHER_API_KEY = getattr(settings, 'OPENWEATHER_API_KEY', None)

def get_current_weather_data(city_name):
    if not OPENWEATHER_API_KEY: return None, "Weather API key not configured."
    base_url = "http://api.openweathermap.org/data/2.5/weather"
    params = {'q': city_name, 'appid': OPENWEATHER_API_KEY, 'units': 'metric', 'lang': 'hi'}
    try:
        response = requests.get(base_url, params=params)
        if response.status_code == 404: return None, f"City '{city_name}' not found."
        response.raise_for_status()
        data = response.json()
        return {
            "lat": data["coord"]["lat"],
            "lon": data["coord"]["lon"],
            "city": data.get("name"), 
            "temperature": data["main"]["temp"],
            "description": data["weather"][0]["description"], 
            "humidity": data["main"]["humidity"],
            "pressure": data["main"]["pressure"], # <-- ADDED
            "wind_speed": data["wind"]["speed"], # <-- ADDED
            "visibility": data.get("visibility") # <-- ADDED (in meters)
        }, None
    except requests.exceptions.RequestException as e:
        print(f"🔴 Weather API request error: {e}")
        return None, "Could not connect to the current weather service."

# Update get_alerts_and_forecast to capture wind/pressure/humidity/min/max temp for forecast
def get_alerts_and_forecast(lat, lon):
    if not OPENWEATHER_API_KEY: return {'forecast': [], 'alerts': []}, "API key missing."
    
    base_url = "http://api.openweathermap.org/data/2.5/forecast"
    params = {
        'lat': lat, 
        'lon': lon, 
        'appid': OPENWEATHER_API_KEY, 
        'units': 'metric', 
        'lang': 'hi'
    }

    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        data = response.json()
        
        forecast = []
        processed_dates = set()
        for item in data.get('list', []):
            date_str = item['dt_txt'].split(' ')[0]
            time_str = item['dt_txt'].split(' ')[1]
            
            # Use noon data (most reliable daily representation)
            if date_str not in processed_dates and time_str == '12:00:00':
                forecast.append({
                    'date': item.get('dt'),
                    'max_temp': item['main']['temp_max'],
                    'min_temp': item['main']['temp_min'],
                    'description': item['weather'][0]['description'],
                    'icon': item['weather'][0]['icon'],
                    'humidity': item['main']['humidity'],
                    'pressure': item['main']['pressure'], # <-- ADDED
                    'wind_speed': item['wind']['speed'] # <-- ADDED
                })
                processed_dates.add(date_str)
            
            if len(forecast) >= 5:
                break
            
        alerts = [] # Alerts are NOT available in the free tier

        return {'forecast': forecast, 'alerts': alerts}, None

    except requests.exceptions.RequestException as e:
        print(f"🔴 OpenWeatherMap Forecast API request error: {e}")
        return {'forecast': [], 'alerts': []}, "Could not connect to the forecast service."

def get_alerts_and_forecast(lat, lon):
    if not OPENWEATHER_API_KEY: return {'forecast': [], 'alerts': []}, "API key missing."
    
    # [FIXED] Use the Free Tier 5-Day / 3-Hour Forecast API endpoint
    base_url = "http://api.openweathermap.org/data/2.5/forecast"
    params = {
        'lat': lat, 
        'lon': lon, 
        'appid': OPENWEATHER_API_KEY, 
        'units': 'metric', 
        'lang': 'hi'
    }

    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        data = response.json()
        
        forecast = []
        # The free API returns data every 3 hours. We will only take the data for 
        # noon (12:00) each day to simulate a daily forecast for the next 5 days.
        processed_dates = set()
        for item in data.get('list', []):
            date_str = item['dt_txt'].split(' ')[0] # 'YYYY-MM-DD'
            time_str = item['dt_txt'].split(' ')[1] # 'HH:MM:SS'
            
            # Check if this is a new day and is close to noon (12:00:00)
            if date_str not in processed_dates and time_str == '12:00:00':
                forecast.append({
                    'date': item.get('dt'),
                    'max_temp': item['main']['temp_max'],
                    'min_temp': item['main']['temp_min'],
                    'description': item['weather'][0]['description'],
                    'icon': item['weather'][0]['icon'],
                    'humidity': item['main']['humidity']
                })
                processed_dates.add(date_str)
            
            # Stop after 5 days
            if len(forecast) >= 5:
                break
            
        # [ALERTS REMOVED] The free API does not include severe weather alerts
        alerts = [] 

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
        location = None

    if not location:
        return render(request, 'policies.html', {
            'error': 'कृपया अपनी प्रोफाइल में अपना स्थान (Location) अपडेट करें ताकि हम आपके लिए योजनाएं ढूंढ सकें।'
        })

    if not POLICY_MODEL:
        return render(request, 'policies.html', {
            'error': 'AI सेवा अनुपलब्ध है। कृपया थोड़ी देर बाद प्रयास करें।'
        })

    # [MODIFIED] The prompt now asks for a government link.
    prompt = f"""
    Act as an expert on Indian government agricultural schemes.
    List the top 4 most beneficial, currently active government schemes for farmers in: {location}, India.
    Include both Central and State specific schemes for this region.
    Provide the output in concise Hindi.

    Strictly output ONLY a raw JSON list of objects. Do not use Markdown formatting (no ```json).
    Follow this exact format, finding the most relevant official government link for each scheme:
    [
        {{
            "name": "योजना का नाम (Scheme Name)",
            "description": "यह योजना क्या है और किसके लिए है (1-2 वाक्य)",
            "benefits": "मुख्य लाभ (जैसे सब्सिडी राशि, बीमा, आदि)",
            "link": "https://official-government-link.gov.in"
        }}
    ]
    """

    try:
        response = POLICY_MODEL.generate_content(prompt)
        text = response.text.strip()
        text = re.sub(r'^```json', '', text)
        text = re.sub(r'^```', '', text)
        text = re.sub(r'```$', '', text)
        
        policies_data = json.loads(text)
        
        return render(request, 'policies.html', {
            'location': location,
            'policies': policies_data
        })

    except Exception as e:
        print(f"Error fetching/parsing policies: {e}")
        text = locals().get('text', 'No raw response text captured.')
        print(f"Raw AI response: {text}")
        return render(request, 'policies.html', {
            'error': f'{location} के लिए योजनाओं को लोड करने में समस्या आई। कृपया पुनः प्रयास करें।'
        })



def Fertilizer(request):
    return render(request,'SFR.html')

def about(request):
    return render(request,'about.html')

