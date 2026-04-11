# AgriPath — AI-Powered Smart Farming Platform

AgriPath is a full-stack agricultural advisory platform built with **Django** and the **Google Gemini API**, designed to help Indian farmers make data-driven decisions. It combines real-time market prices, hyper-local weather intelligence, government scheme discovery, and a bilingual AI voice assistant into a single unified interface.

---

## 🌟 Features

### 📊 Dashboard
The central hub of the platform. At a glance:
- **Live Mandi Price Ticker** — Real-time wholesale crop prices scrolling across the bottom of the screen, sourced from the Government of India's Agmarknet API.
- **Weather Summary Widget** — Current temperature, conditions, and a 5-day forecast for your saved location.
- **Smart Weather Alert Banner** — A toast notification that slides in on dashboard load with a draining timer bar. Automatically dismisses after 7 seconds or can be manually closed. Only appears on the dashboard.
- **Crop Tracker Summary** — A quick overview of your currently tracked crops and their health status.
- **Farmer / Hobbyist Mode Toggle** — Switches the UI and AI advisor context between a commercial farmer and a home gardener persona.

---

### ⛈️ Weather Forecast (`/home/Weather`)
- Current conditions: temperature, humidity, wind speed, pressure, and visibility.
- 5-day detailed forecast with weather icons.
- **Season-aware Weather Alerts** displayed in a full-grid panel:
  - Alert thresholds adjust dynamically based on the month (Winter / Summer / Monsoon).
  - Alert types: Thunderstorm ⛈️, Rain 💧, High Heat 🔥, Severe Heat 🔥🔥, Frost ❄️, Abnormal Cold 🧊.
  - Uses **true daily max/min temperatures** aggregated across all 3-hour API slots — not just noon readings — ensuring peak afternoon heat is never missed.

---

### 🤖 AI Assistant (`/ai/` + Sidebar on every page)
A fully bilingual conversational assistant available site-wide via a floating button, and as a dedicated full-screen page.

- **Intent Classification:** Queries are auto-classified into `weather`, `crop_recommendation`, `government_scheme`, `market_price`, or `general_conversation` and routed to specialized handlers.
- **Live Market Price Queries:** Ask "What is the mandi price of wheat?" or "गेहूं का भाव क्या है?" — the assistant extracts the crop name, fetches live Agmarknet data, and responds conversationally.
- **Bilingual EN / HI Support:**
  - **Speech-to-Text** switches between `en-US` and `hi-IN` recognition based on the active language toggle.
  - **Text-to-Speech** speaks in the correct dialect.
  - When in Hindi mode, the AI is instructed to generate fully native Hindi responses.
- **Persistent Chat Memory** via Django Sessions — conversation context is maintained until the user starts a "New Chat".

---

### 🌾 Mandi Price Tracker (`/tracker/`)
- Add and track crops with full financial records.
- **Smart Crop Picker:** Distinguishes between market-supported crops (with live Agmarknet price data) and custom crops.
- Financial entries calculate projected revenue and profit using yield-per-acre metrics and live market prices.
- Activity logs and health status tracking per crop.

---

### 🩺 AI Plant Doctor (`/home/plant-doctor/`)
- Upload a photo of a plant or leaf showing signs of disease.
- Powered by **Google Gemini's multimodal vision** — returns a diagnosis and treatment recommendations.

---

### 📜 Government Schemes (`/home/Policies`)
- AI-generated, location-aware listing of relevant central and state government schemes for farmers.
- Organised into four categories: Crop Insurance & Security, Financial Aid & Loans, Modern Agriculture & Technology, and Farmer Welfare.

---

### 🌍 EN ↔ HI Language Toggle
- A custom toggle in the navbar switches the entire site UI between English and Hindi via the **Google Translate widget**.
- Language preference is stored in `localStorage` and persists across sessions.
- The AI assistant, voice recognition, and TTS all read this preference and adapt automatically.
- The platform's native codebase is 100% English — all translations are handled client-side.

---

### 🔐 Authentication
- **Mobile OTP Login** via Twilio — no passwords required.
- **Forced Profile Setup Middleware** — ensures users complete their profile (name, location, user type) before accessing the platform.

---

## 🛠️ Technology Stack

| Layer | Technology |
|---|---|
| **Backend** | Python 3.11+, Django 5.x |
| **AI** | Google Gemini API (Flash / Pro) |
| **Database** | PostgreSQL (Production), SQLite (Development) |
| **Authentication** | Django Auth + Twilio Mobile OTP |
| **APIs** | OpenWeatherMap, data.gov.in (Agmarknet), Twilio |
| **Frontend** | Vanilla HTML / CSS / JS, Font Awesome, Google Fonts |
| **Voice** | Web Speech API (SpeechRecognition + SpeechSynthesis) |
| **i18n** | Google Translate Widget (client-side) |
| **Deployment** | Render, Gunicorn, `dj-database-url`, `whitenoise` |

---

## ⚙️ Local Setup

### Prerequisites
- Python 3.11+
- Twilio account (for OTP login)
- Google Gemini API Key
- OpenWeatherMap API Key
- data.gov.in API Key (for Mandi prices)

### Steps

```bash
git clone https://github.com/nirmitguptadev/Agripath.git
cd Agripath

python -m venv .agripath
.\.agripath\Scripts\activate   # Windows
# source .agripath/bin/activate  # macOS/Linux

pip install -r requirements.txt
```

Create a `.env` file in the project root:

```env
SECRET_KEY=your_django_secret_key
DEBUG=True

TWILIO_ACCOUNT_SID=your_sid
TWILIO_AUTH_TOKEN=your_token
TWILIO_PHONE_NUMBER=+1xxxxxxxxxx

GEMINI_API_KEY=your_gemini_key
OPENWEATHER_API_KEY=your_openweather_key
MANDI_API_KEY=your_data_gov_in_key
```

```bash
python manage.py migrate
python manage.py runserver
```

Visit `http://127.0.0.1:8000` and log in with your mobile number.

---

## 📄 License

MIT — see [LICENSE](LICENSE) for details.
