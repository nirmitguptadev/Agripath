import json
import re
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

# ... keep your other views (index, Bihar, etc.) if you still need them ...

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

