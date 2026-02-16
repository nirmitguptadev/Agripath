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


PERSONA_PROMPT = {
    'role': 'user', 
    'parts': [
        "आप 'AgriPath' नाम के एक मित्रवत और जानकार AI कृषि मित्र हैं। आपकी बोली सरल और स्पष्ट हिंदी में है, जैसे आप गाँव के किसी किसान मित्र से बात कर रहे हों। अपने उत्तरों को स्वाभाविक, संक्षिप्त और संवादी रखें।"
    ]
}
PERSONA_ACK = {'role': 'model', 'parts': ['जी, मैं समझ गया। मैं एक किसान मित्र की तरह सरल हिंदी में बात करूँगा।']}


def handle_weather_query(user_prompt, history):
    city_extraction_prompt = f"इस वाक्य से केवल शहर का नाम निकालें: '{user_prompt}'. केवल एक शब्द में उत्तर दें।"
    city_name = generate_ai_response(city_extraction_prompt).strip()

    if not city_name or "क्षमा करें" in city_name or len(city_name.split()) > 3:
        return "मैं आपका शहर समझ नहीं पाया। क्या आप कृपया फिर से बता सकते हैं।"

    weather_data, error = get_weather_data(city_name)
    if error:
        return f"मुझे '{city_name}' नाम کا شہر नहीं मिला। कृपया शहर का नाम जांच लें।"

    final_prompt_list = [
        PERSONA_PROMPT,
        PERSONA_ACK,
        *history,
        {'role': 'user', 'parts': [f"""
        यहाँ '{city_name}' का वास्तविक मौसम डेटा है:
        - तापमान: {weather_data['temperature']}°C
        - विवरण: {weather_data['description']}
        - नमी (Humidity): {weather_data['humidity']}%
        इस डेटा के आधार पर, किसान को एक सरल और स्वाभाविक सारांश (1-2 वाक्यों में) प्रदान करें।
        """]}
    ]
    return generate_ai_response(final_prompt_list)

def handle_crop_recommendation(user_prompt, history):
    final_prompt_list = [
        PERSONA_PROMPT,
        PERSONA_ACK,
        {'role': 'user', 'parts': ['जब आप फसलों की सूची सुझाते हैं, तो हर फसल का नाम एक नई लाइन पर दें। सूची बनाने के लिए किसी भी बुलेट पॉइंट या नंबरिंग का प्रयोग न करें।']},
        {'role': 'model', 'parts': ['जी, मैं हर फसल का नाम एक नई लाइन पर दूंगा, बिना किसी निशान के।']},
        *history
    ]
    return generate_ai_response(final_prompt_list)

def handle_government_scheme(user_prompt, history):
    final_prompt_list = [
        PERSONA_PROMPT,
        PERSONA_ACK,
        *history
    ]
    return generate_ai_response(final_prompt_list)

def handle_general_conversation(user_prompt, history):
    final_prompt_list = [
        PERSONA_PROMPT,
        PERSONA_ACK,
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
    fallback_greeting = "नमस्ते! मैं आपकी मदद के लिए तैयार हूँ।"
    greeting_prompt = "आप AgriPath नाम के एक AI कृषि सहायक हैं। एक किसान के लिए एक छोटा, स्वाभाविक और मैत्रीपूर्ण नमस्ते हिंदी में उत्पन्न करें। केवल एक वाक्य।"
    greeting_text = generate_ai_response(greeting_prompt)
    if "क्षमा करें" in greeting_text:
        return JsonResponse({'greeting': fallback_greeting})
    return JsonResponse({'greeting': greeting_text})

@csrf_exempt
def process_voice(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request method'}, status=405)

    try:
        data = json.loads(request.body)
        user_prompt = data.get('text')
        if not user_prompt:
            return JsonResponse({'error': 'No text provided'}, status=400)

        history = request.session.get('chat_history', [])
        history.append({'role': 'user', 'parts': [user_prompt]})

        classifier_prompt = f"""User query: "{user_prompt}". Classify this into: 'weather', 'crop_recommendation', 'government_scheme', 'general_conversation'. Respond only with the category name."""
        category = generate_ai_response(classifier_prompt).strip().lower()

        conversation_context = list(history)
        
        final_response_text = ""
        if 'weather' in category:
            final_response_text = handle_weather_query(user_prompt, conversation_context)
        elif 'crop' in category:
            final_response_text = handle_crop_recommendation(user_prompt, conversation_context)
        elif 'scheme' in category or 'yojana' in category or 'sarkari' in category:
            final_response_text = handle_government_scheme(user_prompt, conversation_context)
        else:
            final_response_text = handle_general_conversation(user_prompt, conversation_context)

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