# In your 'assistant' app's views.py file

import os
import json
import requests
import google.generativeai as genai
from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

# --- API Configuration (remains the same) ---
MODEL = None
try:
    GEMINI_API_KEY = settings.GEMINI_API_KEY
    OPENWEATHER_API_KEY = settings.OPENWEATHER_API_KEY
    genai.configure(api_key=GEMINI_API_KEY)
    MODEL = genai.GenerativeModel('gemini-2.5-flash') # Using the stable model name
    print("✅ Successfully configured Gemini and Weather APIs.")
except (AttributeError, Exception) as e:
    print(f"🔴 FATAL ERROR: Could not configure API keys. Error: {e}")
    GEMINI_API_KEY = None
    OPENWEATHER_API_KEY = None

# --- Centralized Gemini Response Function (remains the same) ---
def generate_gemini_response(prompt_text):
    if not MODEL:
        print("🔴 Attempted to call Gemini, but the model is not configured.")
        return "क्षमा करें, मेरा AI कनेक्शन ठीक से काम नहीं कर रहा है।"
    try:
        response = MODEL.generate_content(prompt_text)
        return response.text
    except Exception as e:
        print(f"🔴🔴🔴 GEMINI API ERROR 🔴🔴🔴: {e}")
        return "क्षमा करें, AI से कनेक्ट करते समय एक त्रुटि हुई।"

# --- Weather Helper Function (remains the same) ---
def get_weather_data(city_name):
    # ... (no changes in this function)
    if not OPENWEATHER_API_KEY:
        return None, "Weather API key not configured."
    base_url = "http://api.openweathermap.org/data/2.5/weather"
    params = {'q': city_name, 'appid': OPENWEATHER_API_KEY, 'units': 'metric', 'lang': 'hi'}
    try:
        response = requests.get(base_url, params=params)
        if response.status_code == 404: return None, f"City '{city_name}' not found."
        response.raise_for_status()
        data = response.json()
        return {
            "city": data.get("name"), "temperature": data["main"]["temp"],
            "description": data["weather"][0]["description"], "humidity": data["main"]["humidity"],
            "wind_speed": data["wind"]["speed"],
        }, None
    except requests.exceptions.RequestException as e:
        print(f"🔴 Weather API request error: {e}")
        return None, "Could not connect to the weather service."


# ==============================================================================
#  HANDLER FUNCTIONS WITH MODIFIED PROMPTS
# ==============================================================================

def handle_weather_query(user_prompt):
    city_extraction_prompt = f"इस वाक्य से केवल शहर का नाम निकालें: '{user_prompt}'. केवल एक शब्द में उत्तर दें।"
    city_name = generate_gemini_response(city_extraction_prompt).strip()

    if not city_name or "क्षमा करें" in city_name or len(city_name.split()) > 3:
        return "कृपया एक स्पष्ट शहर का नाम बताएं ताकि मैं मौसम की जांच कर सकूं।"

    weather_data, error = get_weather_data(city_name)
    if error:
        return f"क्षमा करें, मुझे '{city_name}' शहर नहीं मिला।"

    final_prompt = f"""
    आप एक सहायक कृषि मित्र हैं। केवल हिंदी में उत्तर दें।
    एक किसान ने '{city_name}' के मौसम के बारे में पूछा है। यहाँ वास्तविक मौसम डेटा है:
    - तापमान: {weather_data['temperature']}°C
    - विवरण: {weather_data['description']}
    - नमी (Humidity): {weather_data['humidity']}%

    इस डेटा के आधार पर, किसान को एक बहुत छोटा और सीधा सारांश (1-2 वाक्यों में) प्रदान करें।
    
    # --- EDIT: Added instruction to avoid special characters ---
    कृपया अपने उत्तर में किसी भी विशेष वर्ण जैसे !,@,#,$,* आदि का प्रयोग न करें।
    """
    return generate_gemini_response(final_prompt)

def handle_crop_recommendation(user_prompt):
    final_prompt = f"""
    आप एक विशेषज्ञ भारतीय कृषि वैज्ञानिक हैं।
    एक किसान हिंदी में पूछता है: "{user_prompt}"

    उसके प्रश्न का विश्लेषण करें और केवल मुख्य फसल सिफारिशों की सूची दें। उत्तर संक्षिप्त और बिंदुवार (to-the-point) रखें।

    # --- EDIT: Added instruction to avoid special characters ---
    सूची बनाने के लिए किसी भी विशेष वर्ण जैसे * या - का प्रयोग न करें। प्रत्येक फसल का नाम एक नई लाइन पर दें।
    """
    return generate_gemini_response(final_prompt)

def handle_government_scheme(user_prompt):
    final_prompt = f"""
    आप भारत सरकार की कृषि योजनाओं के विशेषज्ञ हैं।
    एक किसान हिंदी में पूछता है: "{user_prompt}"

    उस योजना के बारे में केवल मुख्य लाभ और पात्रता बताएं। उत्तर को 2-3 वाक्यों में संक्षिप्त रखें।
    
    # --- EDIT: Added instruction to avoid special characters ---
    कृपया अपने उत्तर में किसी भी विशेष वर्ण जैसे !,@,#,$,* आदि का प्रयोग न करें।
    """
    return generate_gemini_response(final_prompt)

def handle_general_conversation(user_prompt):
    final_prompt = f"""
    आप 'AgriPath' नाम के एक AI कृषि मित्र हैं। आप केवल हिंदी में संवाद करते हैं।
    
    संक्षिप्त और सीधे तरीके से उत्तर दें। अपने उत्तरों को अधिकतम 2 वाक्यों तक सीमित रखें।

    # --- EDIT: Added instruction to avoid special characters ---
    कृपया अपने उत्तर में किसी भी विशेष वर्ण जैसे !,@,#,$,* आदि का प्रयोग न करें।

    किसान का प्रश्न: "{user_prompt}"
    आपका उत्तर:
    """
    return generate_gemini_response(final_prompt)
# ==============================================================================
#  MAIN DJANGO VIEWS (No changes needed below this line)
# ==============================================================================

def assistant_page(request):
    return render(request, 'core.html')

def get_greeting(request):
    fallback_greeting = "नमस्ते! मैं आपकी मदद के लिए तैयार हूँ।"
    # --- CHANGE: Added instruction for a short greeting ---
    greeting_prompt = "आप AgriPath नाम के एक AI कृषि सहायक हैं। एक किसान के लिए एक छोटा और मैत्रीपूर्ण नमस्ते हिंदी में उत्पन्न करें। केवल एक वाक्य।"
    greeting_text = generate_gemini_response(greeting_prompt)
    if "क्षमा करें" in greeting_text:
        return JsonResponse({'greeting': fallback_greeting})
    return JsonResponse({'greeting': greeting_text})

@csrf_exempt
def process_voice(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request method'}, status=405)
    if not MODEL:
        return JsonResponse({'response': 'क्षमा करें, मेरा AI कनेक्शन ठीक से काम नहीं कर रहा है।'}, status=500)

    try:
        data = json.loads(request.body)
        user_prompt = data.get('text')
        if not user_prompt:
            return JsonResponse({'error': 'No text provided'}, status=400)

        # --- Step 1: Classification (no changes here) ---
        classifier_prompt = f"""
        User query: "{user_prompt}".
        Classify this into: 'weather', 'crop_recommendation', 'government_scheme', 'general_conversation'.
        Respond only with the category name.
        """
        category = generate_gemini_response(classifier_prompt).strip().lower()

        # --- Step 2: Routing (no changes here) ---
        final_response_text = ""
        if 'weather' in category:
            final_response_text = handle_weather_query(user_prompt)
        elif 'crop' in category:
            final_response_text = handle_crop_recommendation(user_prompt)
        elif 'scheme' in category or 'yojana' in category or 'sarkari' in category:
            final_response_text = handle_government_scheme(user_prompt)
        else:
            final_response_text = handle_general_conversation(user_prompt)

        return JsonResponse({'response': final_response_text})

    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON in request body'}, status=400)
    except Exception as e:
        print(f"🔴 An unexpected error occurred in process_voice: {e}")
        return JsonResponse({'error': 'Sorry, an internal server error occurred.'}, status=500)