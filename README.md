# AgriPath AI Assistant: Full-Stack Conversational AgriTech Platform

![AgriPath AI Assistant Banner](https://placehold.co/800x200/004d40/a5d6a7?text=AgriPath+AI+Assistant)

AgriPath is a modern, location-aware conversational AI platform built using **Django** and the **Google Gemini API**. Its primary goal is to provide Indian farmers with instant, accurate agricultural advisory services, year-round crop planning, and localized government scheme information through a simple, secure chat interface.

## ✨ Key Project Innovations

### 1. Integrated AI & Machine Learning
*   **ML Crop Advisory:** Implemented a **Random Forest Classifier (scikit-learn)**, trained on a public dataset, to predict the top suitable crops based on a comprehensive input feature set (NPK, pH, Rainfall, and real-time Temperature/Humidity).
*   **Year-Round Planning:** Utilizes the Gemini API to take the ML-predicted crops and generate a detailed, context-aware **Year-Round Planting Calendar** and maintenance advisory.

### 2. Robust User Experience & Security
*   **Mobile OTP Authentication:** Custom, secure login flow using **Twilio** for mobile OTP verification, a standard requirement for accessibility in rural markets.
*   **Forced Profile Setup:** Custom Django Middleware enforces a single-time profile completion (Name, Age, and **Geolocation**) before the user can access the main AI features.
*   **Persistent Context:** Chat history is stored in the **Django Session Framework**, ensuring conversations persist across page refreshes until the user initiates a "New Chat."

### 3. Geospatial & API Orchestration
*   **Localized Features:** Integrates the user's saved location to provide hyper-local **Real-time Weather Forecasts (OpenWeatherMap)** and dynamically filtered **Government Policy** lookups.
*   **Unified Interface:** All features (Chat, Weather, Policies, Advisory) are consolidated into a single, intuitive, and mobile-friendly UI with a dark-green gradient theme.

---

## 🛠️ Technology Stack

*   **Backend Framework:** Python (Django 5.x)
*   **AI/ML:** Google Gemini API, scikit-learn, Pandas, joblib
*   **Database:** PostgreSQL (Production on Render), SQLite (Development)
*   **Authentication:** `django.contrib.auth`, Twilio
*   **APIs:** OpenWeatherMap, Twilio
*   **Deployment:** Render, Gunicorn, `dj-database-url`

---

## ⚙️ Local Development Setup

### Prerequisites
1.  Python 3.11+
2.  Twilio Account (for OTP)
3.  Gemini API Key, OpenWeatherMap API Key

### 1. Clone the Repository and Setup Environment

```bash
# Clone the repository
git clone https://github.com/YourUsername/AgriPath-AI-Assistant.git
cd AgriPath-AI-Assistant

# Create and activate the virtual environment
python -m venv dvenv
.\dvenv\Scripts\activate  # Windows
# source dvenv/bin/activate # macOS/Linux
