# AgriPath: AI-Powered Smart Farming Platform
## Project Progress Report

---

## Abstract

AgriPath is a full-stack web application designed to empower Indian farmers and hobby gardeners through artificial intelligence, real-time data, and multi-modal inputs. The platform integrates a conversational AI advisor, an image-based plant disease detection engine, live wholesale market price feeds, hyper-local weather intelligence, and a crop growth tracker into a single bilingual interface. The system leverages Google Gemini, Groq Llama, and the Kindwise crop.health ML classifier to deliver accurate, hallucination-resistant agricultural guidance. Deployed on Render with a PostgreSQL backend in production, AgriPath targets the gap between complex agricultural data and accessible, actionable advice at the farm level.

---

## Table of Contents

1. Introduction
   - 1.1 Objective of the Project
   - 1.2 Brief Description of the Project
   - 1.3 Technology Used
     - 1.3.1 Hardware Requirements
     - 1.3.2 Software Requirements
   - 1.4 Organization Profile
2. Design Description
   - 2.1 Flow Chart
   - 2.2 Data Flow Diagrams (DFDs)
   - 2.3 Entity Relationship Diagram (E-R Diagram)
3. Project Description
   - 3.1 Database
   - 3.2 Table Description
   - 3.3 File/Database Design
4. Input/Output Form Design
5. Testing and Tools Used
6. Implementation and Maintenance
7. Conclusion and Future Work
8. Outcome
9. Bibliography

---

# 1. Introduction

## 1.1 Objective of the Project

The primary objective of AgriPath is to build an intelligent, accessible digital assistant for Indian farmers that:

1. Provides **real-time crop market prices** (mandi rates) sourced directly from the Government of India's Agmarknet API, enabling farmers to make informed selling decisions.
2. Delivers **AI-powered plant disease diagnosis** through image analysis using a purpose-built machine learning classifier, minimizing the risk of incorrect AI-generated diagnoses (hallucinations).
3. Generates **personalised crop management tasks and advisories** based on live weather data, current growth phase, and crop type.
4. Aggregates **government agricultural schemes and subsidies** relevant to the user's state and crop portfolio.
5. Supports **bilingual interaction** (English and Hindi) via both text and voice interfaces, making the platform accessible to farmers who are not fluent in English.
6. Tracks **crop growth, financial inputs, and projected profitability** across an entire growing season.

## 1.2 Brief Description of the Project

AgriPath is a Django-based web platform that serves two distinct user personas: **Pro Farmer** (commercial agricultural users) and **Hobby Gardener** (urban/peri-urban home garden enthusiasts). The platform dynamically adapts its UI, AI responses, and available features based on the active persona.

**Key modules include:**

- **Dashboard:** Central hub displaying live weather, a scrolling mandi price ticker, weather alert banners, and quick-access widgets for all major features.
- **AI Plant Doctor:** A multimodal image analysis tool. Users upload a photograph of a diseased plant. The system first queries the Kindwise crop.health ML API (trained on 23 crop families and 288 disease/pest categories) for a structured, high-confidence diagnosis. If crop.health is unavailable, the system falls back to Google Gemini Vision and then to Groq's Llama-4-Scout vision model.
- **Crop Tracker:** A lifecycle management tool for tracking active crops. Users record planting dates, growth phases, area under cultivation, yield estimates, revenue, and expenses. The system calculates real-time progress percentage, days to harvest, and profit/loss.
- **AI Advisor (Chatbot):** A floating, site-wide conversational AI assistant backed by Google Gemini, with Groq Llama as a fallback. Supports both English and Hindi. Intent classification routes queries to specialised handlers for weather, crop recommendations, market prices, and government schemes.
- **Weather Forecast:** 5-day season-aware weather forecast using OpenWeatherMap, with alerts calibrated to Indian agricultural seasons (Kharif, Rabi, Zaid).
- **Crop Dictionary:** An encyclopedia of 100+ crops with agronomic details, growth duration, soil requirements, and disease profiles.
- **Government Policies:** AI-curated listings of central and state government agricultural schemes, organised by category (crop insurance, financial aid, technology subsidies, welfare).
- **Authentication:** Passwordless mobile OTP login via Twilio.

## 1.3 Technology Used

### 1.3.1 Hardware Requirements

| Component | Minimum Specification |
|---|---|
| Processor | Intel Core i3 (8th Gen) or equivalent |
| RAM | 4 GB DDR4 |
| Storage | 20 GB available disk space |
| Network | Broadband internet (required for all API integrations) |
| Display | 1280 × 720 resolution or higher |
| Mobile Device | Any smartphone with a camera and modern browser (for plant photo uploads and OTP login) |

> *Note: AgriPath is a cloud-hosted web application. End-users access it via browser and require no local installation. The above specifications apply to the development/server environment.*

### 1.3.2 Software Requirements

**Development Environment:**

| Category | Technology | Version |
|---|---|---|
| Operating System | Windows 10/11 | — |
| Programming Language | Python | 3.12.3 |
| Web Framework | Django | 5.2.2 |
| Virtual Environment | venv | — |
| Package Manager | pip | 24.x |
| Version Control | Git | 2.x |
| IDE | Visual Studio Code | Latest |

**Backend Libraries:**

| Library | Purpose | Version |
|---|---|---|
| django-environ | Environment variable management | 0.12.0 |
| gunicorn | WSGI HTTP server for production | 23.0.0 |
| whitenoise | Static file serving | 6.11.0 |
| dj-database-url | Database URL parsing | 3.0.1 |
| psycopg2-binary | PostgreSQL adapter | 2.9.11 |
| pillow | Image processing (plant photo resize) | 11.3.0 |
| django-phonenumber-field | Phone number field validation | 8.3.0 |
| twilio | SMS OTP authentication | 9.8.3 |

**AI and API Libraries:**

| Library | Purpose | Version |
|---|---|---|
| google-generativeai | Google Gemini API client | 0.8.5 |
| groq | Groq LLM API client (Llama models) | 1.0.0 |
| kindwise-api-client | crop.health plant disease detection | 0.8.1 |
| requests | HTTP API calls (weather, mandi, news) | 2.32.3 |
| aiohttp | Async HTTP for news aggregation | 3.13.0 |
| cloudinary | Media file cloud storage | 1.41.0 |

**Data and Testing Libraries:**

| Library | Purpose | Version |
|---|---|---|
| pandas | Data manipulation for mandi prices | 2.3.3 |
| scikit-learn | ML utilities | 1.7.2 |
| pytest / pytest-django | Unit and integration testing | 7.4.3 / 4.7.0 |
| pytest-cov | Code coverage reporting | 4.1.0 |
| factory-boy | Test fixture generation | 3.3.0 |
| coverage | Coverage analysis | 7.11.0 |

**External APIs:**

| API | Provider | Purpose |
|---|---|---|
| Gemini Flash / Pro | Google AI | Conversational AI, image analysis, scheme generation |
| Llama 3.1-8B Instant | Groq | Text AI fallback |
| Llama 4 Scout 17B | Groq | Vision AI fallback |
| crop.health | Kindwise | ML-based plant disease identification |
| OpenWeatherMap | OpenWeather | Current weather and 5-day forecast |
| Agmarknet | data.gov.in (Govt. of India) | Live wholesale crop mandi prices |
| NewsData.io | NewsData | Agricultural news feed |
| Twilio | Twilio | Mobile OTP for passwordless login |
| Cloudinary | Cloudinary | Cloud media storage |
| Google Translate Widget | Google | Client-side EN ↔ HI translation |

## 1.4 Organization Profile

**Project:** AgriPath — AI-Powered Smart Farming Platform  
**Repository:** github.com/nirmitguptadev/Agripath  
**License:** MIT  
**Type:** Independent academic/portfolio project  
**Domain:** AgriTech / Artificial Intelligence / Web Development  
**Target Geography:** India (primary), with multilingual extensibility  

AgriPath was developed as a full-stack application addressing the digital divide in Indian agriculture. India has approximately 146 million farm holdings, the majority operated by smallholder farmers with limited access to timely, accurate market and agronomic information. AgriPath's mission is to consolidate this information into a single, mobile-friendly, AI-enhanced interface.

---

# 2. Design Description

## 2.1 Flow Chart

### User Authentication Flow

```
Start
  │
  ▼
User visits AgriPath
  │
  ├─ Not Logged In ──► Login Page ──► Enter Mobile Number
  │                                         │
  │                                         ▼
  │                                  OTP sent via Twilio
  │                                         │
  │                                         ▼
  │                                  User enters OTP
  │                                         │
  │                              ┌──────────┴──────────┐
  │                              │ Valid?              │
  │                          Yes │                     │ No
  │                              ▼                     ▼
  │                     Profile Complete?      Re-enter OTP
  │                    ┌────────┴────────┐
  │                 No │                 │ Yes
  │                    ▼                 ▼
  │             Force Profile      Dashboard
  │             Completion
  │
  └─ Logged In ──────────────► Dashboard
```

### AI Plant Doctor Flow

```
User uploads plant image
  │
  ▼
Image saved to temp buffer (in-memory)
  │
  ▼
Image resized to max 800×800 px
  │
  ▼
Temp file written and closed
  │
  ▼
Is CROP_HEALTH_API_KEY configured?
  ├─ YES ──► Call Kindwise crop.health API (base64 image)
  │              │
  │     ┌────────┴────────────┐
  │     │ Confidence ≥ 35%?  │
  │  YES│                     │NO (low confidence)
  │     ▼                     │
  │  Return structured        │
  │  HTML diagnosis           │
  │  (disease + treatment)    │
  │                           │
  └─ NO ◄────────────────────┘
  │
  ▼
Try Google Gemini Vision
  ├─ SUCCESS ──► Return Gemini HTML response
  │
  └─ QUOTA / ERROR ──► Try Groq Llama-4-Scout Vision
                              │
                    ┌─────────┴─────────┐
                    │ SUCCESS           │ ERROR
                    ▼                   ▼
            Return Groq       "Service unavailable"
            HTML response      error message
  │
  ▼
Temp file deleted
  │
  ▼
Diagnosis rendered on plant_doctor.html
```

### Crop Tracker Flow

```
User adds new crop
  │
  ▼
Set planting date, crop type, area, phase
  │
  ▼
System calculates total_days from crop.growth_duration
  │
  ▼
Each day (on dashboard load):
  │
  ├─ days_elapsed = today − planting_date
  ├─ time_pct    = (days_elapsed / total_days) × 100
  ├─ phase_floor = PHASE_FLOOR[growth_phase]
  └─ progress%   = max(time_pct, phase_floor)
  │
  ▼
days_remaining = total_days × (1 − progress% / 100)
  │
  ▼
AI generates weather-aware + phase-aware tasks
  │
  ▼
Tasks displayed on tracker dashboard
```

## 2.2 Data Flow Diagrams (DFDs)

### Level 0 DFD (Context Diagram)

```
                      ┌─────────────────┐
  Farmer / Gardener ──►                 ──► Dashboard, Diagnosis,
                      │    AgriPath     │   Tracker, Advisories
  Mobile OTP ─────────►    Platform     │
                      │                 ◄── Weather API
  Crop Images ────────►                 ◄── Mandi API
                      └─────────────────┘   AI APIs
```

### Level 1 DFD

```
                     ┌─────────────────────────────────────────────┐
                     │                  AgriPath                   │
                     │                                             │
  User ──(login)───► │ [1.0 Auth Module] ──► Session/Profile DB   │
                     │                                             │
  User ──(image)───► │ [2.0 Plant Doctor] ──► crop.health API     │
                     │                    ──► Gemini/Groq API     │
                     │                    ◄── Diagnosis Result    │
                     │                                             │
  User ──(query)───► │ [3.0 AI Advisor]   ──► Gemini/Groq API    │
                     │                    ──► Weather API         │
                     │                    ──► Mandi API           │
                     │                    ◄── AI Response         │
                     │                                             │
  User ──(crop)────► │ [4.0 Tracker]      ──► CropTracker DB      │
                     │                    ──► FinancialEntry DB   │
                     │                    ◄── Progress/Tasks      │
                     │                                             │
                     │ [5.0 Dashboard]    ──► OpenWeatherMap API  │
                     │                    ──► Mandi API           │
                     │                    ──► News API            │
                     │                    ◄── Aggregated View     │
                     └─────────────────────────────────────────────┘
```

## 2.3 Entity Relationship Diagram (E-R Diagram)

```
┌─────────────────┐         ┌─────────────────────┐
│      User       │         │       Profile        │
│─────────────────│  1   1  │─────────────────────│
│ id (PK)         │────────►│ id (PK)              │
│ username        │         │ user (FK → User)     │
│ email           │         │ user_type            │
│ password        │         │ name                 │
└─────────────────┘         │ age                  │
         │                  │ location             │
         │                  │ phone_number         │
         │ 1                │ language             │
         │                  │ profile_picture      │
         ▼ N                └─────────────────────┘
┌─────────────────────────┐
│      CropTracker         │         ┌──────────────────┐
│─────────────────────────│  N   1  │      Crop         │
│ id (PK)                 │────────►│──────────────────│
│ user (FK → User)        │         │ id (PK)           │
│ crop (FK → Crop, null)  │         │ name              │
│ crop_name_custom        │         │ display_name      │
│ planting_date           │         │ growth_duration   │
│ growth_phase            │         │ description       │
│ status                  │         │ soil_type         │
│ area_acres              │         │ season            │
│ yield_per_acre          │         └──────────────────┘
│ harvest_date            │
│ phase_updated_date      │
│─────────────────────────│
│ [Properties]            │
│ days_elapsed            │
│ total_days              │
│ progress_percent        │
│ days_remaining          │
└──────────┬──────────────┘
           │ 1
           │
           ▼ N
┌──────────────────────────┐
│      FinancialEntry       │
│──────────────────────────│
│ id (PK)                  │
│ crop_tracker (FK)        │
│ entry_type (Rev/Exp)     │
│ amount                   │
│ description              │
│ date                     │
└──────────────────────────┘
```

---

# 3. Project Description

## 3.1 Database

AgriPath uses **SQLite** for local development and **PostgreSQL** for production deployment on Render. The database connection is managed via `dj-database-url` which parses the `DATABASE_URL` environment variable. Django's ORM (Object Relational Mapper) is used exclusively — no raw SQL queries are written, ensuring portability across both database backends.

Django's built-in session framework stores per-user state including:
- Conversation history for the AI chatbot
- AI tips cache (keyed by crop and version)
- Weather alert cache (1-hour TTL stored in `sessionStorage` client-side)

## 3.2 Table Description

### Table 1: auth_user (Django Built-in)

| Field | Type | Description |
|---|---|---|
| id | INTEGER (PK) | Auto-incremented primary key |
| username | VARCHAR(150) | Unique username |
| email | VARCHAR(254) | Email address |
| password | VARCHAR(128) | Hashed password (unused — OTP auth) |
| is_active | BOOLEAN | Account active status |
| date_joined | DATETIME | Registration timestamp |

### Table 2: accounts_profile

| Field | Type | Description |
|---|---|---|
| id | INTEGER (PK) | Auto-incremented primary key |
| user_id | INTEGER (FK) | Foreign key to auth_user |
| user_type | VARCHAR(20) | 'Farmer' or 'Hobbyist' |
| name | VARCHAR(100) | Full display name |
| age | SMALLINT | User age (optional) |
| location | VARCHAR(100) | City/district for weather lookups |
| phone_number | VARCHAR(20) | Mobile number (unique, for OTP) |
| language | VARCHAR(10) | 'en-us' or 'hi' |
| profile_picture | VARCHAR(255) | Cloudinary image path |

### Table 3: tracker_croptracker

| Field | Type | Description |
|---|---|---|
| id | INTEGER (PK) | Auto-incremented primary key |
| user_id | INTEGER (FK) | Foreign key to auth_user |
| crop_id | INTEGER (FK, null) | Foreign key to dictionary_crop |
| crop_name_custom | VARCHAR(100) | User-entered crop name |
| planting_date | DATE | Date crop was sown |
| growth_phase | VARCHAR(50) | Current phase (Sowing/Vegetative/Flowering/Maturity/Harvest) |
| status | VARCHAR(20) | 'Active' or 'Completed' |
| area_acres | DECIMAL(6,2) | Cultivated area in acres |
| yield_per_acre | DECIMAL(8,2) | Expected yield per acre (kg) |
| harvest_date | DATE (null) | Actual harvest date (if completed) |
| phase_updated_date | DATE (null) | Date of last manual phase change |

### Table 4: tracker_financialentry

| Field | Type | Description |
|---|---|---|
| id | INTEGER (PK) | Auto-incremented primary key |
| crop_tracker_id | INTEGER (FK) | Foreign key to tracker_croptracker |
| entry_type | VARCHAR(20) | 'Revenue' or 'Expense' |
| amount | DECIMAL(12,2) | Transaction amount in INR |
| description | VARCHAR(255) | Entry description |
| date | DATE | Transaction date |

### Table 5: dictionary_crop

| Field | Type | Description |
|---|---|---|
| id | INTEGER (PK) | Auto-incremented primary key |
| name | VARCHAR(100) | Internal crop identifier |
| display_name | VARCHAR(100) | Human-readable crop name |
| growth_duration | VARCHAR(50) | Duration string (e.g., "120 days") |
| description | TEXT | Agronomic description |
| soil_type | VARCHAR(100) | Preferred soil conditions |
| season | VARCHAR(50) | Kharif / Rabi / Zaid |

## 3.3 File/Database Design

### Project Directory Structure

```
mypage/                          ← Django project root
├── mypage/                      ← Project settings package
│   ├── settings.py              ← All configuration, API keys via environ
│   ├── urls.py                  ← Root URL routing
│   └── wsgi.py                  ← WSGI entry point
│
├── core/                        ← Shared utilities app
│   ├── ai_fallback.py           ← AI chain: Gemini → Groq, Plant Doctor logic
│   ├── mandi_api.py             ← Agmarknet API integration
│   ├── news_api.py              ← NewsData.io integration
│   └── views.py                 ← AI chatbot, persona prompts
│
├── home/                        ← Main dashboard app
│   ├── dashboard_view.py        ← Dashboard data aggregation view
│   ├── views.py                 ← Plant Doctor, Weather, Policies, toggle
│   └── urls.py                  ← /home/ URL patterns
│
├── accounts/                    ← Authentication app
│   ├── models.py                ← Profile model
│   ├── views.py                 ← OTP login/logout
│   └── middleware.py            ← Profile completion enforcement
│
├── tracker/                     ← Crop tracker app
│   ├── models.py                ← CropTracker, FinancialEntry models
│   ├── views.py                 ← Tracker dashboard, tasks, AI tips
│   └── forms.py                 ← Crop add/update forms
│
├── dictionary/                  ← Crop encyclopedia app
│   ├── models.py                ← Crop model
│   └── views.py                 ← Crop list, detail views
│
├── templates/                   ← All HTML templates
│   ├── base.html                ← Base layout (navbar, footer, chatbot)
│   ├── dashboard.html           ← Main dashboard
│   ├── plant_doctor.html        ← AI Plant Doctor page
│   ├── tracker/
│   │   ├── dashboard.html       ← Tracker dashboard
│   │   ├── add_crop.html        ← Add crop form
│   │   └── update_crop.html     ← Edit crop form
│   └── ...                      ← Other feature templates
│
├── static/                      ← CSS, JS, images
├── media/                       ← Temp uploads (plant images)
├── requirements.txt             ← Python dependencies
├── Procfile                     ← Render/Heroku process definition
├── build.sh                     ← Production build script
└── .env                         ← Environment variables (not committed)
```

---

# 4. Input/Output Form Design

### Form 1: OTP Login

**Input Fields:**
- Mobile Number (PhoneNumberField, validated against E.164 format)

**Process:** Twilio sends a 6-digit OTP via SMS.

**Output:** Redirect to OTP verification form → Dashboard (or profile setup if new user).

---

### Form 2: Profile Setup / Edit

**Input Fields:**

| Field | Type | Validation |
|---|---|---|
| Name | Text | Required, max 100 chars |
| Age | Number | Optional, positive integer |
| Location | Text | Required for weather features |
| User Type | Select | Farmer / Hobbyist |
| Profile Picture | Image Upload | Optional, stored on Cloudinary |
| Phone Number | PhoneNumber | Unique, E.164 format |

**Output:** Profile saved; redirect to dashboard.

---

### Form 3: Add Crop (Tracker)

**Input Fields:**

| Field | Type | Description |
|---|---|---|
| Crop | Select/Text | Picker from supported list or custom name |
| Planting Date | Date | Date crop was sown |
| Growth Phase | Select | Sowing / Vegetative / Flowering / Maturity / Harvest |
| Area (acres) | Decimal | Land area under cultivation |
| Yield per Acre | Decimal | Expected harvest in kg/acre |

**Output:** New CropTracker record; redirect to tracker dashboard.

---

### Form 4: AI Plant Doctor

**Input Fields:**
- Plant Image (JPEG/PNG, any resolution — auto-resized to 800×800 px server-side)

**Process:**
1. Image read into memory buffer (no blocking file handle)
2. Resized using Pillow in-memory
3. Written to temp file and immediately closed
4. Passed to AI pipeline (crop.health → Gemini → Groq)
5. Temp file deleted after analysis

**Output (Disease Detected):**
```
┌─────────────────────────────────────────────────┐
│  [Disease Detected]  Confidence: 78%            │
│                                                 │
│  Diagnosis                                      │
│  Tomato Late Blight (Phytophthora infestans)    │
│                                                 │
│  Description                                    │
│  A water mold causing rapid tissue death...     │
│                                                 │
│  Cause                                          │
│  Cool, moist conditions favour spore spread...  │
│                                                 │
│  Treatment                                      │
│  • Biological: Apply Trichoderma viride...      │
│  • Chemical: Copper-based fungicide spray...    │
│  • Prevention: Avoid overhead irrigation...     │
│                                                 │
│  Other possibilities: Septoria Leaf Spot (12%) │
│                                                 │
│  Identified by crop.health ML classifier —      │
│  23 crops, 288 diseases & pests.                │
└─────────────────────────────────────────────────┘
```

**Output (Healthy Plant):**
```
┌─────────────────────────────────────────────────┐
│  [Healthy]  Confidence: 92%                     │
│                                                 │
│  Diagnosis                                      │
│  Healthy Tomato                                 │
│                                                 │
│  Description                                    │
│  No signs of disease or pest damage detected.  │
└─────────────────────────────────────────────────┘
```

---

### Form 5: Add Financial Entry

**Input Fields:**

| Field | Type | Description |
|---|---|---|
| Entry Type | Select | Revenue / Expense |
| Amount | Decimal | Amount in INR (₹) |
| Description | Text | Notes (e.g., "Fertilizer purchase") |
| Date | Date | Transaction date |

**Output:** FinancialEntry saved; updated profit/loss shown on tracker dashboard.

---

# 5. Testing and Tools Used

## Testing Approach

AgriPath uses a structured testing framework built on **pytest** with the **pytest-django** plugin, enabling fast isolated unit and integration tests without running a full Django server.

## Test Modules

| Module | File | Coverage Area |
|---|---|---|
| Crop Tracker | `tests/test_tracker.py` | CropTracker model, progress calculation, financial entries |
| Mandi API | `tests/test_mandi_api.py` | Price fetching, caching, error handling |
| Authentication | `tests/test_auth.py` | OTP login, profile middleware, redirects |
| AI Fallback | `tests/test_ai.py` | Gemini mock, Groq fallback, Plant Doctor |
| Views | `tests/test_views.py` | HTTP responses, form validation, redirects |

## Testing Tools

| Tool | Version | Purpose |
|---|---|---|
| pytest | 7.4.3 | Test runner |
| pytest-django | 4.7.0 | Django-aware test utilities |
| pytest-cov | 4.1.0 | Code coverage measurement |
| pytest-mock | 3.12.0 | Mocking external API calls |
| factory-boy | 3.3.0 | Test data factories (User, Profile, CropTracker) |
| responses | 0.24.1 | HTTP request mocking for API tests |
| coverage | 7.11.0 | Coverage report generation |

## Running Tests

```bash
# Activate virtual environment
.agripath\Scripts\activate

# Run all tests with coverage
pytest --cov=. --cov-report=term-missing

# Run specific module
pytest tests/test_tracker.py -v
```

## Key Test Scenarios

1. **Progress Calculation:** Verify `progress_percent` returns correct values for time-based vs. manual phase-change scenarios.
2. **AI Fallback Chain:** Mock Gemini quota error and confirm Groq is invoked; mock both failures and confirm error message is returned.
3. **Plant Doctor File Handling:** Confirm temp file is created, used, and deleted without `PermissionError` on Windows.
4. **OTP Authentication:** Test valid OTP grants access; invalid OTP returns error; expired OTP is rejected.
5. **Mandi Price Caching:** Confirm second call within cache window does not make a new API request.

---

# 6. Implementation and Maintenance

## Deployment Architecture

AgriPath is deployed on **Render** (cloud PaaS) using the following production stack:

```
Internet
    │
    ▼
Render Load Balancer (HTTPS/TLS)
    │
    ▼
Gunicorn WSGI Server (4 workers)
    │
    ▼
Django Application
    │
    ├──► PostgreSQL (Render Managed DB)
    ├──► Cloudinary (Media files — profile pics, no temp files in prod)
    └──► WhiteNoise (Compressed static files — CSS, JS, images)
```

## Environment Configuration

All sensitive values are stored as **environment variables** — never hardcoded:

```
SECRET_KEY            Django cryptographic key
DEBUG                 False in production
DATABASE_URL          PostgreSQL connection string
GEMINI_API_KEY        Google Gemini API key
GROQ_API_KEY          Groq API key
CROP_HEALTH_API_KEY   Kindwise crop.health API key
OPENWEATHER_API_KEY   OpenWeatherMap API key
MANDI_API_KEY         data.gov.in Agmarknet key
NEWSDATA_API_KEY      NewsData.io key
TWILIO_ACCOUNT_SID    Twilio credentials
TWILIO_AUTH_TOKEN
TWILIO_PHONE_NUMBER
CLOUDINARY_CLOUD_NAME Cloudinary credentials
CLOUDINARY_API_KEY
CLOUDINARY_API_SECRET
ALLOWED_HOSTS         Comma-separated list of valid hostnames
CSRF_TRUSTED_ORIGINS  Trusted origins for CSRF protection
```

## Security Measures

- `SESSION_COOKIE_SECURE = True` (HTTPS-only cookies)
- `CSRF_COOKIE_SECURE = True`
- `SECURE_SSL_REDIRECT = True`
- `SECURE_HSTS_SECONDS = 31536000` (1-year HSTS)
- `SECURE_HSTS_INCLUDE_SUBDOMAINS = True`
- `SECURE_PROXY_SSL_HEADER` set for Render's reverse proxy

## Maintenance

- **Static files:** Collected via `python manage.py collectstatic` during `build.sh` and served by WhiteNoise with compression.
- **Database migrations:** Applied automatically in `build.sh` via `python manage.py migrate`.
- **API key rotation:** All keys are environment variables; rotation requires no code changes.
- **Dependency updates:** `requirements.txt` is pinned to exact versions for reproducibility.

---

# 7. Conclusion and Future Work

## Conclusion

AgriPath successfully demonstrates the integration of multiple AI services, real-time data APIs, and full-stack web development into a coherent agricultural advisory platform. The three-tier AI fallback architecture (crop.health ML → Gemini Vision → Groq Vision) for plant disease detection significantly reduces the risk of hallucinations compared to relying solely on a general-purpose LLM. The bilingual interface (English/Hindi) and dual-persona mode (Pro Farmer / Hobby Gardener) make the platform accessible to a diverse Indian user base.

The crop tracker's time-based progress model, combined with manual phase override support, provides farmers with a realistic, continuously updating view of their crop lifecycle without requiring daily manual input.

## Future Work

1. **Offline Support (PWA):** Progressive Web App capabilities for use in low-connectivity rural areas. Cache weather forecasts and crop tasks locally.
2. **Soil Health Integration:** API integration with ICAR's soil health card portal to enrich crop recommendations with user-specific soil nutrient data.
3. **Voice-First Interface:** Expand the existing Web Speech API integration to support full voice navigation, enabling use by farmers with limited literacy.
4. **Multi-language Expansion:** Extend the translation framework to support Marathi, Punjabi, Telugu, and Tamil — major farming languages beyond Hindi.
5. **Satellite Imagery:** Integrate ISRO's Bhuvan satellite API or NASA MODIS data for field-level crop health monitoring using NDVI indices.
6. **Predictive Yield Modelling:** Apply the scikit-learn dependency (already in requirements) to build yield prediction models trained on historical yield, weather, and soil data.
7. **SMS / WhatsApp Alerts:** Use Twilio's WhatsApp API to push critical weather and pest alerts directly to farmers who may not visit the web app daily.
8. **Marketplace Module:** Allow farmers to list produce directly with verified buyers, closing the loop between price information and sales.

---

# 8. Outcome

**Deployment:** AgriPath is deployed as a live web application at `https://agripath.onrender.com` (Render cloud platform). The application is publicly accessible with full feature availability including AI diagnostics, mandi prices, weather forecasting, and bilingual support.

**Intellectual Property:** The project is released under the MIT License (open source). The codebase is publicly hosted at `github.com/nirmitguptadev/Agripath`, enabling peer review, contribution, and academic citation.

**Research Contribution:** The plant disease detection pipeline implements a novel multi-tier fallback architecture that combines a specialised ML classifier (Kindwise crop.health — 23 crops, 288 disease categories) with general-purpose vision LLMs (Gemini, Groq Llama-4-Scout), providing a practical framework for reducing AI hallucinations in high-stakes agricultural diagnosis applications.

---

# 9. Bibliography

1. Django Software Foundation. *Django Documentation — Version 5.2*. 2024. https://docs.djangoproject.com/en/5.2/

2. Google AI. *Gemini API Documentation*. 2024. https://ai.google.dev/gemini-api/docs

3. Groq Inc. *Groq API Documentation and Rate Limits*. 2025. https://console.groq.com/docs

4. Kindwise. *crop.health API — AI Crop Disease Identification*. 2024. https://crop.kindwise.com

5. OpenWeather. *OpenWeatherMap API Documentation*. 2024. https://openweathermap.org/api

6. Government of India — Ministry of Agriculture. *Agmarknet — Agricultural Marketing Information Network*. https://agmarknet.gov.in

7. Twilio Inc. *Twilio Verify API Documentation*. 2024. https://www.twilio.com/docs/verify

8. Cloudinary. *Django SDK Documentation*. 2024. https://cloudinary.com/documentation/django_integration

9. Meta AI. *Llama 4 Scout Model Card*. 2025. https://ai.meta.com/blog/llama-4/

10. ICAR — Indian Council of Agricultural Research. *Crop Production Statistics — India*. https://icar.org.in

11. Whitenoise Documentation. *Radically simplified static file serving for Python web apps*. http://whitenoise.evans.io/en/stable/

12. pytest-django. *pytest-django Documentation*. https://pytest-django.readthedocs.io/en/latest/

---

*End of Report*
