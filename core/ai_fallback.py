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
                return "Sorry, an error occurred while connecting to AI."
    
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
            return "Sorry, an error occurred while connecting to AI."
    
    return "Sorry, my AI connection is not working properly."

def _format_treatment(treatment):
    """Convert crop.health treatment dict into an HTML list."""
    if not treatment:
        return ''
    items = []
    for key in ('biological', 'chemical', 'prevention'):
        entries = treatment.get(key) or []
        if isinstance(entries, str):
            entries = [entries]
        for entry in entries:
            if entry:
                label = key.capitalize()
                items.append(f'<li><strong>{label}:</strong> {entry}</li>')
    return ''.join(items)


def analyze_plant_image(image_path, user_type='Farmer'):
    """
    Primary: crop.health by Kindwise (ML classifier — no hallucination).
    Fallback: Gemini Vision if crop.health is unconfigured or returns low confidence.
    """
    crop_health_key = getattr(settings, 'CROP_HEALTH_API_KEY', None)

    if crop_health_key:
        try:
            import base64 as _b64
            from kindwise import CropHealthApi
            with open(image_path, 'rb') as _f:
                image_b64 = _b64.b64encode(_f.read())
            api = CropHealthApi(api_key=crop_health_key)
            identification = api.identify(
                image_b64,
                details=['treatment', 'description', 'cause', 'local_name'],
                language=['en'],
            )

            result = getattr(identification, 'result', None)
            # disease suggestions are under result.disease; crop identity under result.crop
            disease_obj = getattr(result, 'disease', None)
            suggestions = getattr(disease_obj, 'suggestions', []) or []

            if suggestions:
                top = suggestions[0]
                confidence = getattr(top, 'probability', 0) or 0
                name = getattr(top, 'name', 'Unknown')
                details = getattr(top, 'details', None) or {}

                if isinstance(details, dict):
                    local_name = details.get('local_name') or ''
                    description = details.get('description') or ''
                    cause = details.get('cause') or ''
                    treatment = details.get('treatment') or {}
                else:
                    local_name = getattr(details, 'local_name', '') or ''
                    description = getattr(details, 'description', '') or ''
                    cause = getattr(details, 'cause', '') or ''
                    treatment = getattr(details, 'treatment', {}) or {}

                confidence_pct = int(confidence * 100)

                if confidence >= 0.35:
                    is_healthy = 'healthy' in name.lower()
                    badge_color = '#16a34a' if is_healthy else '#dc2626'
                    badge_text = 'Healthy' if is_healthy else 'Disease Detected'

                    treatment_html = _format_treatment(treatment) if not is_healthy else ''

                    other_html = ''
                    if len(suggestions) > 1 and not is_healthy:
                        others = [f"{getattr(s,'name','?')} ({int((getattr(s,'probability',0) or 0)*100)}%)" for s in suggestions[1:3]]
                        other_html = f'<p style="color:#64748b;font-size:0.9em;">Other possibilities: {", ".join(others)}</p>'

                    html = f'''
<div class="diagnosis-result">
  <div style="display:flex;align-items:center;gap:0.75rem;margin-bottom:1rem;">
    <span style="background:{badge_color};color:white;padding:3px 12px;border-radius:99px;font-size:0.8rem;font-weight:700;">{badge_text}</span>
    <span style="color:#64748b;font-size:0.85rem;">Confidence: {confidence_pct}%</span>
  </div>
  <h3>Diagnosis</h3>
  <p><strong>{name}</strong>{" ("+local_name+")" if local_name else ""}</p>
  {"<h3>Description</h3><p>"+description+"</p>" if description else ""}
  {"<h3>Cause</h3><p>"+cause+"</p>" if cause else ""}
  {"<h3>Treatment</h3><ul>"+treatment_html+"</ul>" if treatment_html else ""}
  {other_html}
  <p style="color:#94a3b8;font-size:0.75rem;margin-top:1rem;">Identified by crop.health ML classifier &mdash; 23 crops, 288 diseases &amp; pests.</p>
</div>'''
                    return html.strip()

        except ImportError:
            print("kindwise package not installed. Run: pip install kindwise-api-client")
        except Exception as e:
            print(f"Crop Health API error: {e}")

    # Fallback: Vision AI (Gemini → Groq)
    import base64 as _b64
    with open(image_path, 'rb') as _f:
        image_b64 = _b64.b64encode(_f.read()).decode('utf-8')

    persona_context = (
        "Commercial Farmer focused on crop yield and scalability"
        if user_type == 'Farmer'
        else "Hobby plant enthusiast focused on plant aesthetics, indoor care, and simple home remedies"
    )
    prompt = (
        f"You are an expert plant pathologist. Analyze this plant image.\n"
        f"1. Identify the plant and any disease/deficiency visible.\n"
        f"2. If healthy, say 'The plant appears healthy.'\n"
        f"3. If sick, state the disease name, symptoms observed, and 2-3 remedies.\n"
        f"Context: {persona_context}.\n"
        f"Format response as HTML using <h3>, <p>, <ul>, <li> tags only. No markdown."
    )

    # Try Gemini Vision
    if GEMINI_MODEL:
        try:
            import PIL.Image, io as _io
            img = PIL.Image.open(_io.BytesIO(_b64.b64decode(image_b64)))
            response = GEMINI_MODEL.generate_content([prompt, img])
            text = re.sub(r'```(?:html)?', '', response.text).strip()
            return text
        except Exception as e:
            err = str(e).lower()
            if 'quota' in err or 'limit' in err or 'resource_exhausted' in err or '429' in err:
                print("Gemini vision quota exceeded, falling back to Groq vision")
            else:
                print(f"Gemini vision error: {e}")
                return "Sorry, an error occurred while analyzing the image. Please try again later."

    # Try Groq Vision (llama-4-scout supports image input)
    if GROQ_CLIENT:
        try:
            response = GROQ_CLIENT.chat.completions.create(
                model="meta-llama/llama-4-scout-17b-16e-instruct",
                messages=[{
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_b64}"}},
                    ],
                }],
                max_tokens=1500,
            )
            text = response.choices[0].message.content
            text = re.sub(r'```(?:html)?', '', text).strip()
            return text
        except Exception as e:
            print(f"Groq vision error: {e}")

    return "Sorry, all AI vision services are currently unavailable. Please try again later."


def get_agronomic_info(crop_name):
    """
    Fetches structured agronomic info (sowing, fertilizers, diseases) for a crop using AI.
    """
    if not GEMINI_MODEL and not GROQ_CLIENT:
        return "AI models not configured."
        
    prompt = f"""
    You are an expert Indian agronomist. Provide structured farming information for the crop '{crop_name}' specifically tailored to the Indian agricultural context (e.g. referencing typical Indian states, Indian climates, Kharif/Rabi seasons, etc.).
    Provide the response strictly as valid HTML (do NOT use markdown code blocks like ```html).
    Use <h3> for the headers and <ul>/<li> for the bullet points.
    
    Include exactly these 4 sections:
    <div class="agronomy-card">
        <h3>Sowing Period & Seasons in India</h3>
        <ul>...</ul>
        <h3>Fertilizer Requirements</h3>
        <ul>...</ul>
        <h3>Common Diseases & Pests (Indian Subcontinent)</h3>
        <ul>...</ul>
        <h3>Water & Irrigation</h3>
        <ul>...</ul>
    </div>
    """
    
    try:
        if GEMINI_MODEL:
            response = GEMINI_MODEL.generate_content(prompt)
            text = response.text
        else:
            response = GROQ_CLIENT.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=1000
            )
            text = response.choices[0].message.content
            
        text = re.sub(r'```html\n?', '', text)
        text = re.sub(r'```\n?', '', text)
        return text.strip()
    except Exception as e:
        print(f"Agronomy Extractor Error: {e}")
        return "<p>Agronomic data unavailable at the moment.</p>"
