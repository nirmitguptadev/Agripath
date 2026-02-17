import re
import google.generativeai as genai
from groq import Groq
from django.conf import settings

# Configure APIs
GEMINI_API_KEY = getattr(settings, 'GEMINI_API_KEY', None)
GROQ_API_KEY = getattr(settings, 'GROQ_API_KEY', None)

GEMINI_MODEL = None
GROQ_CLIENT = None

if GEMINI_API_KEY:
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        GEMINI_MODEL = genai.GenerativeModel('gemini-1.5-flash')
    except Exception as e:
        print(f"Gemini config error: {e}")

if GROQ_API_KEY:
    try:
        GROQ_CLIENT = Groq(api_key=GROQ_API_KEY)
    except Exception as e:
        print(f"Groq config error: {e}")

def generate_ai_response(prompt_content):
    """Try Gemini first, fallback to Groq if quota exceeded"""
    
    # Try Gemini
    if GEMINI_MODEL:
        try:
            if isinstance(prompt_content, list):
                response = GEMINI_MODEL.generate_content(prompt_content)
            else:
                response = GEMINI_MODEL.generate_content(prompt_content)
            raw_text = response.text
            cleaned_text = re.sub(r'[!@#$*_-]', '', raw_text)
            return cleaned_text.strip()
        except Exception as e:
            error_str = str(e).lower()
            if 'quota' in error_str or 'limit' in error_str or 'resource_exhausted' in error_str:
                print("Gemini quota exceeded, switching to Groq")
            else:
                print(f"Gemini error: {e}")
                return "क्षमा करें, AI से कनेक्ट करते समय एक त्रुटि हुई।"
    
    # Fallback to Groq
    if GROQ_CLIENT:
        try:
            if isinstance(prompt_content, list):
                messages = []
                for item in prompt_content:
                    role = item.get('role', 'user')
                    if role == 'model':
                        role = 'assistant'
                    content = ' '.join(item.get('parts', []))
                    messages.append({"role": role, "content": content})
            else:
                messages = [{"role": "user", "content": str(prompt_content)}]
            
            response = GROQ_CLIENT.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=messages,
                temperature=0.7,
                max_tokens=2000
            )
            raw_text = response.choices[0].message.content
            cleaned_text = re.sub(r'[!@#$*_-]', '', raw_text)
            return cleaned_text.strip()
        except Exception as e:
            print(f"Groq error: {e}")
            return "क्षमा करें, AI से कनेक्ट करते समय एक त्रुटि हुई।"
    
    return "क्षमा करें, मेरा AI कनेक्शन ठीक से काम नहीं कर रहा है।"
