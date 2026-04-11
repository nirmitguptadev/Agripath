import os
import json
import re 
import requests
from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from core.ai_fallback import generate_ai_response
from core.mandi_api import get_mandi_prices

# --- API Configuration ---
OPENWEATHER_API_KEY = getattr(settings, 'OPENWEATHER_API_KEY', None)

def get_weather_data(city_name):
    if not OPENWEATHER_API_KEY: return None, "Weather API key not configured."
    base_url = "http://api.openweathermap.org/data/2.5/weather"
    params = {'q': city_name, 'appid': OPENWEATHER_API_KEY, 'units': 'metric', 'lang': 'hi'}
    try:
        response = requests.get(base_url, params=params)
        if response.status_code == 404: return None, f"City '{city_name}' not found."
        response.raise_for_status()
        data = response.json()
        return { "city": data.get("name"), "temperature": data["main"]["temp"], "description": data["weather"][0]["description"], "humidity": data["main"]["humidity"], "wind_speed": data["wind"]["speed"], }, None
    except requests.exceptions.RequestException as e:
        print(f"Weather API request error: {e}")
        return None, "Could not connect to the weather service."

# ==============================================================================
#  HANDLER FUNCTIONS - With more natural persona and instructions
# ==============================================================================


def get_persona_prompt(user_type='Farmer', lang='en'):
    if lang == 'hi':
        if user_type == 'Farmer':
            role_desc = "आप 'AgriPath' नाम के एक मित्रवत और जानकार AI कृषि मित्र हैं। आपकी बोली सरल हिंदी में है।"
            objective = "**आपका उद्देश्य:** किसानों को खेती, मौसम, और वेबसाइट के बारे में मदद करना।"
        else:
            role_desc = "आप 'AgriPath' नाम के एक मित्रवत AI गार्डनिंग विशेषज्ञ हैं। आपकी बोली सरल हिंदी में है।"
            objective = "**आपका उद्देश्य:** हॉबी गार्डनर्स को पौधों की देखभाल और वेबसाइट के बारे में मदद करना।"
        reply_lang = "हमेशा हिंदी में बात करें (Always reply in Hindi)."
        ack = "जी, मैं समझ गया।"
    else:
        if user_type == 'Farmer':
            role_desc = "You are a friendly mapping AI agricultural assistant named 'AgriPath'. Speak simply like a farmer's companion."
            objective = "**Your Objective:** Assist farmers with farming, weather, and website features."
        else:
            role_desc = "You are a friendly AI gardening expert named 'AgriPath'."
            objective = "**Your Objective:** Assist hobby gardeners with plant care and website features."
        reply_lang = "Always reply in English."
        ack = "Yes, I understand."

    return {
        'role': 'user', 
        'parts': [
            f"""
            {role_desc}

            {objective}

            **AgriPath Website Features:**
            1. **Dashboard:** Main page with weather and active crops.
            2. **Crop Tracker:** Track ongoing field crops.
            3. **AI Plant Doctor:** Upload plant photos to diagnose disease.
            4. **AI Crop Advisory:** Best crop recommendations.
            5. **Weather:** Local forecasts and alerts.
            6. **Policies:** Gov subsidies and schemes.
            7. **Dictionary:** 100+ crop encyclopedia guides.

            **Instructions:**
            - Keep answers concise (1-3 sentences).
            - {reply_lang}
            """
        ]
    }, {'role': 'model', 'parts': [ack]}


def handle_weather_query(user_prompt, history, user_location=None, user_type='Farmer', lang='en'):
    # Simple check: if query doesn't contain common city indicators, use default location
    common_cities = ['दिल्ली', 'मुंबई', 'कोलकाता', 'चेन्नई', 'बेंगलुरु', 'हैदराबाद', 'अहमदाबाद', 'पुणे', 'जयपुर', 'लखनउ', 'कानपुर', 'delhi', 'mumbai', 'kolkata', 'chennai', 'bangalore', 'hyderabad']
    
    city_mentioned = False
    for city in common_cities:
        if city.lower() in user_prompt.lower():
            city_mentioned = True
            break
    
    if not city_mentioned:
        # No specific city mentioned, use user's location
        if user_location:
            city_name = user_location
        else:
            return "Please update your profile location or mention a city name." if lang == 'en' else "कृपया अपनी प्रोफाइल में स्थान अपडेट करें या शहर का नाम बताएं।"
    else:
        # Extract city name using AI
        city_extraction_prompt = f"Extract only the city name from this query: '{user_prompt}'. Give nothing else."
        city_name = generate_ai_response(city_extraction_prompt).strip()
        
        if not city_name or "क्षमा करें" in city_name or len(city_name.split()) > 3:
            return "I couldn't understand the city name." if lang == 'en' else "मैं शहर का नाम समझ नहीं पाया। कृपया फिर से बताएं।"

    weather_data, error = get_weather_data(city_name)
    if error:
        return f"I couldn't find weather data for '{city_name}'." if lang == 'en' else f"मुझे '{city_name}' का मौसम डेटा नहीं मिला।"

    persona, ack = get_persona_prompt(user_type, lang)
    final_prompt_list = [
        persona,
        ack,
        *history,
        {'role': 'user', 'parts': [f"""
        Here is the real weather data for '{city_name}':
        - Temp: {weather_data['temperature']}°C
        - Desc: {weather_data['description']}
        - Hum: {weather_data['humidity']}%
        Provide a very short and natural summary of this weather data.
        """]}
    ]
    return generate_ai_response(final_prompt_list)

def handle_crop_recommendation(user_prompt, history, user_type='Farmer', lang='en'):
    persona, ack = get_persona_prompt(user_type, lang)
    instruction = 'When suggesting crops, put each one on a new line without any bullets or numbers.' if lang == 'en' else 'जब आप फसलों की सूची सुझाते हैं, तो हर फसल का नाम एक नई लाइन पर दें। किसी भी बुलेट पॉइंट का प्रयोग न करें।'
    instruction_ack = 'Okay, I will list them on new lines without bullets.' if lang == 'en' else 'जी, मैं हर पौधे/फसल का नाम एक नई लाइन पर दूंगा।'
    final_prompt_list = [
        persona,
        ack,
        {'role': 'user', 'parts': [instruction]},
        {'role': 'model', 'parts': [instruction_ack]},
        *history
    ]
    return generate_ai_response(final_prompt_list)

def handle_government_scheme(user_prompt, history, user_type='Farmer', lang='en'):
    persona, ack = get_persona_prompt(user_type, lang)
    final_prompt_list = [
        persona,
        ack,
        *history
    ]
    return generate_ai_response(final_prompt_list)

def handle_market_price(user_prompt, history, user_type='Farmer', lang='en'):
    # Extract crop name
    extract_prompt = f"Extract only the crop or commodity name from this query: '{user_prompt}'. Examples: Wheat, Tomato, Onion. Give only the English name of the crop, nothing else. If it's in Hindi (e.g. 'gehu' or 'गेहूं'), translate to English (e.g. 'Wheat')."
    
    crop_name = generate_ai_response(extract_prompt).strip()
    
    if not crop_name or len(crop_name.split()) > 3:
        return "I couldn't understand the crop name." if lang == 'en' else "मैं फसल का नाम समझ नहीं पाया। कृपया फिर से बताएं।"
        
    prices = get_mandi_prices([crop_name])
    
    persona, ack = get_persona_prompt(user_type, lang)
    if not prices or len(prices) == 0:
        err = f"Sorry, I couldn't find current market price data for {crop_name}." if lang == 'en' else f"क्षमा करें, मुझे {crop_name} का मंडी भाव नहीं मिला।"
        return err
        
    price_data = list(prices.values())[0]
    display_name = list(prices.keys())[0]
    
    final_prompt_list = [
        persona,
        ack,
        *history,
        {'role': 'user', 'parts': [f"""
        Here is the real Mandi market price data for '{display_name}' (per Quintal):
        - Minimum Price: ₹{price_data['min']}
        - Maximum Price: ₹{price_data['max']}
        - Modal Price: ₹{price_data['modal']}
        - Market Location: {price_data['market']}, {price_data['state']}
        Provide a very short and natural summary of this price data.
        """]}
    ]
    return generate_ai_response(final_prompt_list)

def handle_general_conversation(user_prompt, history, user_type='Farmer', lang='en'):
    persona, ack = get_persona_prompt(user_type, lang)
    final_prompt_list = [
        persona,
        ack,
        *history
    ]
    return generate_ai_response(final_prompt_list)

# ==============================================================================
#  MAIN DJANGO VIEWS
# ==============================================================================
@login_required 
def assistant_page(request):
    history = request.session.get('chat_history', [])
    return render(request, 'core.html', {'initial_history': history})

def get_greeting(request):
    lang = request.GET.get('lang', 'en')
    fallback_greeting = "नमस्ते! मैं आपकी मदद के लिए तैयार हूँ।" if lang == 'hi' else "Hello! How can I assist you today?"
    
    user_type = 'Farmer'
    if request.user.is_authenticated:
        try:
            user_type = request.user.profile.user_type
        except Exception:
            pass

    target_audience = "एक किसान (Farmer)" if user_type == "Farmer" else "एक गार्डनिंग के शौकीन (Hobbiyst)"
    prompt_lang_instruction = "हिंदी में" if lang == 'hi' else "in English"
    
    greeting_prompt = f"You are an AI assistant named AgriPath. Generate a very short, natural and friendly greeting {prompt_lang_instruction} for a {user_type}. Only one sentence."
    
    greeting_text = generate_ai_response(greeting_prompt)
    if "क्षमा करें" in greeting_text or "Sorry" in greeting_text:
        return JsonResponse({'greeting': fallback_greeting})
    return JsonResponse({'greeting': greeting_text})

@csrf_exempt
def process_voice(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request method'}, status=405)

    try:
        data = json.loads(request.body)
        user_prompt = data.get('text')
        lang = data.get('lang', 'en')
        if not user_prompt:
            return JsonResponse({'error': 'No text provided'}, status=400)

        history = request.session.get('chat_history', [])
        history.append({'role': 'user', 'parts': [user_prompt]})

        classifier_prompt = f"""User query: "{user_prompt}". Classify this into: 'weather', 'crop_recommendation', 'government_scheme', 'market_price', 'general_conversation'. Respond only with the category name."""
        category = generate_ai_response(classifier_prompt).strip().lower()

        conversation_context = list(history)
        
        user_type = 'Farmer'
        user_location = None
        if request.user.is_authenticated:
            try:
                user_type = request.user.profile.user_type
                user_location = request.user.profile.location
            except Exception:
                pass

        final_response_text = ""
        if 'weather' in category:
            final_response_text = handle_weather_query(user_prompt, conversation_context, user_location, user_type, lang)
        elif 'crop' in category:
            final_response_text = handle_crop_recommendation(user_prompt, conversation_context, user_type, lang)
        elif 'scheme' in category or 'yojana' in category or 'sarkari' in category:
            final_response_text = handle_government_scheme(user_prompt, conversation_context, user_type, lang)
        elif 'market' in category or 'price' in category or 'mandi' in category or 'bhav' in category:
            final_response_text = handle_market_price(user_prompt, conversation_context, user_type, lang)
        else:
            final_response_text = handle_general_conversation(user_prompt, conversation_context, user_type, lang)

        history.append({'role': 'model', 'parts': [final_response_text]})
        request.session['chat_history'] = history

        return JsonResponse({'response': final_response_text})

    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON in request body'}, status=400)
    except Exception as e:
        print(f"An unexpected error occurred in process_voice: {e}")
        return JsonResponse({'error': 'Sorry, an internal server error occurred.'}, status=500)


@csrf_exempt
def clear_chat(request):
    if 'chat_history' in request.session:
        del request.session['chat_history']
    return JsonResponse({'status': 'success', 'message': 'Chat history cleared.'})