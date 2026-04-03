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
        GEMINI_MODEL = genai.GenerativeModel('gemini-2.5-flash')
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

def analyze_plant_image(image_path, user_type='Farmer'):
    """
    Analyzes a plant image using Gemini Vision to detect diseases and suggest remedies.
    """
    if not GEMINI_MODEL:
        return "AI मॉडल कॉन्फ़िगर नहीं है।"

    try:
        import PIL.Image
        img = PIL.Image.open(image_path)
        
        persona_context = "Commercial Farmer focused on crop yield and scalability" if user_type == 'Farmer' else "Hobby plant enthusiast focused on plant aesthetics, indoor care, and simple home remedies"
        
        prompt = f"""
        You are an expert plant pathologist. Analyze this image of a plant.
        1. Identify the plant and any disease/deficiency visible.
        2. If healthy, say "The plant appears healthy."
        3. If sick, list the name of the disease, symptoms observed, and 2-3 organic/chemical remedies.
        
        Context: The user asking is a {persona_context}. Tailor your advice to them.
        
        Provide the response in Hindi, formatted as HTML (no markdown blocks, just tags).
        Use <h3> for headings, <p> for text, and <ul>/<li> for lists.
        The structure should be:
        <div class="diagnosis-result">
            <h3>रोग की पहचान (Diagnosis)</h3>
            <p>...details...</p>
            <h3>लक्षण (Symptoms)</h3>
            <ul>...</ul>
            <h3>उपचार (Treatment)</h3>
            <ul>...</ul>
        </div>
        """
        
        response = GEMINI_MODEL.generate_content([prompt, img])
        
        # Clean up markdown code blocks if present
        text = response.text
        text = re.sub(r'```html', '', text)
        text = re.sub(r'```', '', text)
        return text.strip()
        
    except Exception as e:
        print(f"Plant Doctor Error: {e}")
        return "क्षमा करें, छवि का विश्लेषण करते समय त्रुटि हुई। कृपया बाद में प्रयास करें।"
