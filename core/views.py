from django.shortcuts import render
from django.http import JsonResponse
# from django.views.decorators.csrf import csrf_exempt # Keep CSRF protection if possible
from django.views.decorators.http import require_http_methods
import json
import datetime
import random
import requests # Import the requests library
import re # Import the regular expression library

# Your OpenWeatherMap API Key
OWM_API_KEY = "be2251445f1416c5fa4698a4a939b328"

# --- Helper function to get weather ---
def get_weather(city):
    if not city:
        return "कृपया मौसम जानने के लिए शहर का नाम बताएं।" # Please specify a city name

    base_url = "http://api.openweathermap.org/data/2.5/weather"
    params = {
        'q': city,
        'appid': OWM_API_KEY,
        'units': 'metric', # Get temperature in Celsius
        'lang': 'hi'      # Request Hindi descriptions
    }
    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status() # Raises an HTTPError for bad responses (4XX or 5XX)
        data = response.json()

        # Check if the API returned valid data
        if data.get("cod") != 200:
            error_message = data.get("message", "अज्ञात त्रुटि")
            print(f"OpenWeatherMap API Error for city '{city}': {error_message}")
            # Try to provide a more user-friendly message for common errors
            if data.get("cod") == "404":
                 return f"क्षमा करें, मुझे '{city}' शहर नहीं मिला।"
            else:
                 return f"मौसम की जानकारी प्राप्त करने में एक समस्या हुई: {error_message}"

        # Extract information
        description = data['weather'][0]['description']
        temp = round(data['main']['temp']) # Round temperature to nearest whole number
        feels_like = round(data['main']['feels_like'])
        humidity = data['main']['humidity']
        city_name_from_api = data['name'] # Use the name returned by the API

        # Format the response in Hindi
        weather_response = (
            f"{city_name_from_api} में अभी मौसम: {description}. "
            f"तापमान {temp}°C है, लेकिन {feels_like}°C जैसा महसूस हो रहा है। "
            f"हवा में नमी {humidity}% है।"
        )
        return weather_response

    except requests.exceptions.RequestException as e:
        print(f"Network or API request error: {e}")
        return "क्षमा करें, मौसम सेवा से संपर्क करने में असमर्थ। कृपया अपनी इंटरनेट जांचें या बाद में प्रयास करें।"
    except (KeyError, IndexError) as e:
        print(f"Error parsing weather data: {e}")
        print("Received data:", data) # Log the problematic data
        return "मौसम डेटा को समझने में त्रुटि हुई।"
    except Exception as e: # Catch any other unexpected errors
         print(f"An unexpected error occurred during weather fetch: {e}")
         return "मौसम की जानकारी प्राप्त करते समय एक अप्रत्याशित त्रुटि हुई।"


# --- Main function to process commands ---
def process_hindi_command(text):
    text_lower = text.lower().strip() # Convert to lower case and remove leading/trailing spaces
    response = "माफ़ कीजिये, मैं आपकी बात पूरी तरह समझ नहीं पाया।" # Default response

    # Simple Keyword Spotting NLU

    # --- Greetings ---
    if any(greet in text_lower for greet in ["नमस्ते", "हेलो", "हैलो", "नमस्कार"]):
        response = random.choice(["नमस्ते! आप कैसे हैं?", "नमस्कार! क्या सहायता कर सकता हूँ?", "हेलो!"])

    # --- Time ---
    elif "समय" in text_lower and ("क्या" in text_lower or "बताओ" in text_lower or "कितना हुआ" in text_lower):
        now = datetime.datetime.now()
        current_time = now.strftime("%I:%M %p") # Use %I for 12-hour format, %p for AM/PM
        response = f"अभी समय है {current_time}"

    # --- Date ---
    elif any(date_word in text_lower for date_word in ["तारीख", "दिनांक", "आज क्या दिन है"]):
         now = datetime.datetime.now()
         # You might need to set locale for full Hindi month names on the server
         # import locale
         # try:
         #     locale.setlocale(locale.LC_TIME, 'hi_IN.UTF-8')
         # except locale.Error:
         #      print("Warning: Hindi locale 'hi_IN.UTF-8' not available. Using default.")
         # current_date = now.strftime("%d %B %Y") # Requires Hindi locale support on server
         current_date = now.strftime("%d/%m/%Y") # Safer default format
         response = f"आज तारीख है {current_date}"

    # --- Assistant Identity ---
    elif "आपका नाम क्या है" in text_lower or "तुम कौन हो" in text_lower:
         response = random.choice(["मेरा नाम सहायक है। मैं आपकी मदद के लिए यहाँ हूँ।", "आप मुझे सहायक कह सकते हैं।"])

    # --- Weather ---
    elif "मौसम" in text_lower:
        # Try to extract city name using simple patterns
        city = None
        # Pattern 1: "दिल्ली में मौसम" or "जयपुर का मौसम"
        match = re.search(r"(.+?)\s+(?:में|का)\s+मौसम", text_lower)
        if match:
            city = match.group(1).strip()
        else:
            # Pattern 2: "मौसम बताओ दिल्ली का" or "मौसम कैसा है जयपुर में"
            match = re.search(r"मौसम\s+(?:बताओ|कैसा है)\s+(?:.*?)\s*(\w+)", text_lower)
            if match:
                city = match.group(1).strip()
            else:
                # Pattern 3: Simplest - Assume city is the word before "मौसम" if patterns fail
                 words = text_lower.split()
                 try:
                     weather_index = words.index("मौसम")
                     if weather_index > 0:
                         city = words[weather_index - 1]
                 except ValueError:
                     # "मौसम" wasn't found as a separate word, maybe part of another word.
                     pass # Fall through to asking for city

        if city:
            print(f"Extracted city for weather: {city}") # For debugging
            response = get_weather(city)
        else:
            # If no city could be extracted, ask for it
            response = "आप किस शहर का मौसम जानना चाहते हैं?"

    # --- Jokes ---
    elif any(joke_word in text_lower for joke_word in ["मजाक", "जोक", "चुटकुला"]):
        jokes_hindi = [
            "टीचर: अगर पृथ्वी के अंदर LAVA है तो बाहर क्या है? स्टूडेंट: बाहर ओप्पो और वीवो है सर!",
            "ग्राहक: भैयाजी, इस आईने की गारंटी क्या है? दुकानदार: आप इसे यहां से ले जाकर गिरा मत देना, तब तक की गारंटी है!",
            "संता: यार बंता, मेरा सिर दर्द कर रहा है। बंता: अरे इसमें क्या? मेरा तो पूरा शरीर ही 'दर्द' का बना है!",
            "पति: ये कैसी दाल बनाई है? ना नमक है, ना मिर्च! पत्नी: अरे गुस्सा क्यों होते हो जी? इसे बनाते समय मैं आपको ही याद कर रही थी, तो सोचा कहीं आपके गुस्से जैसा तीखा ना हो जाए!",
        ]
        response = random.choice(jokes_hindi)

    # --- How are you? ---
    elif any(how_are_you in text_lower for how_are_you in ["कैसे हो", "क्या हाल है", "सब ठीक"]):
         response = random.choice(["मैं ठीक हूँ, पूछने के लिए धन्यवाद!", "मैं बढ़िया हूँ, आपकी क्या सेवा कर सकता हूँ?", "सब कुशल मंगल!"])

    # --- Gratitude ---
    elif any(thanks in text_lower for thanks in ["धन्यवाद", "शुक्रिया", "थैंक यू"]):
        response = random.choice(["कोई बात नहीं!", "आपकी मदद करके खुशी हुई।", "स्वागत है!"])

    # --- Add more commands here using elif ---
    # elif "लाइट बंद करो" in text_lower:
    #     # Add logic to interact with smart home devices (requires more setup)
    #     response = "ठीक है, लाइट बंद कर रहा हूँ।"

    return response

# --- Django Views (Keep as before) ---

# Basic view to render the HTML page
def index(request):
    return render(request, 'core.html')

# API endpoint to handle voice commands
@require_http_methods(["POST"])
def process_voice(request):
    try:
        # Ensure CSRF token is validated if not using @csrf_exempt
        # (The JS code sends the token, so Django should validate it by default)
        data = json.loads(request.body)
        user_text = data.get('text', '')

        if not user_text:
            return JsonResponse({'error': 'No text provided'}, status=400)

        print(f"Received text: {user_text}") # Log received text

        # Process the command
        assistant_response = process_hindi_command(user_text)

        print(f"Sending response: {assistant_response}") # Log the response

        # Return the response as JSON
        return JsonResponse({'response': assistant_response})

    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
         print(f"Error processing voice command: {e}") # Log the error server-side
         return JsonResponse({'error': 'An internal error occurred'}, status=500)