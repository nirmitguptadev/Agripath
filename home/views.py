import json
import re
import requests
import google.generativeai as genai
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.conf import settings
from core.crop_model import predict_suitable_crops, get_soil_data_by_location, CROP_PREDICTOR_MODEL

# --- Configure GenAI  ---
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
            
        # [ALERTS REMOVED]
        alerts = [] 

        return {'forecast': forecast, 'alerts': alerts}, None

    except requests.exceptions.RequestException as e:
        print(f"🔴 OpenWeatherMap Forecast API request error: {e}")
        return {'forecast': [], 'alerts': []}, "Could not connect to the forecast service."
    
@login_required
def CropAdvisory(request):
    # Ensure model is loaded
    if not CROP_PREDICTOR_MODEL:
        try:
            load_and_train_model()
        except Exception as e:
            return render(request, 'crop_advisory.html', {'error': 'फसल सलाहकार मॉडल लोड नहीं हो सका।'})
    
    try:
        location = request.user.profile.location
    except:
        return render(request, 'crop_advisory.html', {'error': 'प्रोफ़ाइल स्थान आवश्यक है।'})

    if not location:
        return render(request, 'crop_advisory.html', {
            'error': 'कृपया अपनी प्रोफाइल में अपना स्थान (Location) अपडेट करें ताकि हम आपके लिए सलाह दे सकें।'
        })

    if not CROP_PREDICTOR_MODEL:
         return render(request, 'crop_advisory.html', {'error': 'फसल सलाहकार मॉडल लोड नहीं हो सका।'})

    # 1. Get Real-time Weather Data for Model Input
    current_weather, weather_error = get_current_weather_data(location)
    if weather_error or not current_weather:
         return render(request, 'crop_advisory.html', {'error': f'मौसम डेटा प्राप्त करने में विफलता: {weather_error}.'})

    # 2. Get Soil Data (Mocked/Estimated NPK, pH, Rainfall)
    soil_data = get_soil_data_by_location(location)
    
    # 3. Combine Real-time and Estimated Data for the Model Input
    model_input = {
        'N': soil_data['N'],
        'P': soil_data['P'],
        'K': soil_data['K'],
        'temperature': current_weather['temperature'],
        'humidity': current_weather['humidity'],
        'ph': soil_data['ph'],
        'rainfall': soil_data['rainfall']
    }

    # 4. Predict MULTIPLE Suitable Crops
    suitable_crops = predict_suitable_crops(model_input)
    
    if not suitable_crops:
        return render(request, 'crop_advisory.html', {'error': 'इस मिट्टी और मौसम डेटा के लिए कोई उपयुक्त फसल नहीं मिली।'})
        
    crops_list_str = ", ".join(suitable_crops)

    # 5. Use Gemini to create the Year-Round Planting Calendar
    gemini_prompt = f"""
    आप एक विशेषज्ञ भारतीय कृषि वैज्ञानिक हैं।
    आपके पास एक मॉडल से प्राप्त {location} क्षेत्र के लिए {len(suitable_crops)} सबसे उपयुक्त फसलों की सूची है: {crops_list_str}
    
    इस सूची का उपयोग करते हुए, एक संवादात्मक, हिंदी में, साल भर की बुवाई की योजना (Year-Round Planting Calendar) बनाएं।
    
    तालिका या जटिल संरचना का उपयोग न करें। प्रत्येक फसल के लिए निम्नलिखित जानकारी को एक छोटे पैराग्राफ में दें:
    1.  फसल का नाम।
    2.  बुवाई/रोपण के लिए सबसे अच्छा महीना या मौसम (जैसे "खरीफ की शुरुआत में").
    3.  मुख्य देखभाल टिप या उपयुक्त मिट्टी का प्रकार।
    """
    
    advisory_text = "क्षमा करें, सलाह देने वाला AI इस समय अनुपलब्ध है।"
    if POLICY_MODEL:
        try:
            response = POLICY_MODEL.generate_content(gemini_prompt)
            advisory_text = response.text.strip()
        except Exception as e:
            print(f"Gemini Advisory Error: {e}")

    # 6. Return the final render
    return render(request, 'crop_advisory.html', {
        'location': location,
        'suitable_crops': suitable_crops, 
        'soil_data': model_input, 
        'advisory': advisory_text
    })

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
        return render(request, 'Policies.html', {
            'error': 'कृपया अपनी प्रोफाइल में अपना स्थान (Location) अपडेट करें ताकि हम आपके लिए योजनाएं ढूंढ सकें।'
        })

    if not POLICY_MODEL:
        return render(request, 'Policies.html', {
            'error': 'AI सेवा अनुपलब्ध है। कृपया थोड़ी देर बाद प्रयास करें।'
        })

    # The prompt asks for a government link.
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
        
        return render(request, 'Policies.html', {
            'location': location,
            'policies': policies_data
        })

    except Exception as e:
        print(f"Error fetching/parsing policies: {e}")
        text = locals().get('text', 'No raw response text captured.')
        print(f"Raw AI response: {text}")
        return render(request, 'Policies.html', {
            'error': f'{location} के लिए योजनाओं को लोड करने में समस्या आई। कृपया पुनः प्रयास करें।'
        })



def Fertilizer(request):
    return render(request,'SFR.html')

def about(request):
    return render(request,'about.html')

