import datetime
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import CropTracker, FinancialEntry, Task, ActivityLog
from .forms import CropTrackerForm, CropUpdateForm, FinancialEntryForm, TaskForm
from dictionary.models import Crop
from django.db.models import Sum
from django.db import models
from core.mandi_api import get_mandi_prices, DEFAULT_CROPS, COMMODITY_ALIASES
from datetime import date
from django.http import JsonResponse
from decimal import Decimal
from core.ai_fallback import generate_ai_response

@login_required
def tracker_dashboard(request):
    active_crops = CropTracker.objects.filter(user=request.user, status='Active').order_by('-planting_date')
    
    # Calculate real-time investments dynamically to bypass cached database fields.
    for crop in active_crops:
        expense = FinancialEntry.objects.filter(crop_tracker=crop, entry_type='Expense').aggregate(Sum('amount'))['amount__sum'] or 0
        crop.real_cost = expense
    
    # Pre-fetch recent logs and tasks for each crop to avoid N+1 queries in template
    # (Django template can loop over crop.logs.all / crop.tasks.filter... but pre-fetching is fine.
    # We will just let the template do `crop.logs.all|slice:":3"` for simplicity.)
    
    # Fetch prices only for the user's active crops + a small mainstream baseline
    user_crops = list(active_crops.values_list('crop_name_custom', flat=True).distinct())
    user_crops = [c.strip().title() for c in user_crops if c and c.strip()]
    combined_mandi_crops = list(dict.fromkeys(user_crops + DEFAULT_CROPS))
    try:
        from concurrent.futures import ThreadPoolExecutor
        with ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(get_mandi_prices, combined_mandi_crops)
            mandi_prices, mandi_is_fallback = future.result(timeout=5)
    except Exception:
        mandi_prices, mandi_is_fallback = {}, False
    
    # Average yield in Quintals per Acre (used when unit is area-based)
    YIELD_PER_ACRE = {
        # Cereals
        'Wheat': 15, 'Rice': 18, 'Paddy(Dhan)(Common)': 18, 'Maize': 12,
        'Bajra(Pearl Millet/Cumbu)': 8, 'Jowar(Sorghum)': 8,
        'Ragi (Finger Millet)': 10, 'Barley (Jau)': 12,
        # Pulses
        'Gram': 7, 'Moong (Green Gram)(Whole)': 5, 'Urad (Black Matpe)(Whole)': 5,
        'Lentil (Masur)(Whole)': 7, 'Arhar (Tur/Red Gram)(Whole)': 6,
        'Rajma': 8, 'Moth(Whole)': 4, 'Kulthi(Horse Gram)': 5,
        # Oilseeds
        'Mustard': 6, 'Soyabean': 6, 'Groundnut': 15, 'Sunflower': 8,
        'Sesame(Gingelly)': 3, 'Castor Seed': 10, 'Linseed': 5,
        'Niger Seed (Ramtil)': 3, 'Safflower': 6, 'Cotton': 6,
        # Vegetables
        'Tomato': 100, 'Onion': 80, 'Potato': 100, 'Brinjal': 80,
        'Cauliflower': 80, 'Cabbage': 120, 'Capsicum': 80,
        'Ladyfinger(Bhindi)': 50, 'Cucumber': 80, 'Peas Green': 30,
        'Carrot': 100, 'Radish': 100, 'Beet Root': 80,
        'Spinach(Palak)': 60, 'Methi(Leaves)': 50, 'Drumstick': 40,
        'Cluster Beans': 40, 'Bottle Gourd': 80, 'Bitter Gourd': 40,
        # Spices
        'Turmeric': 25, 'Garlic': 50, 'Ginger(Dry)': 30,
        'Chilly Red': 15, 'Coriander(Leaves)': 40, 'Dill(Suva/Soya)': 6,
        # Fruits (Quintal per acre per season)
        'Banana': 250, 'Mango': 40, 'Guava': 80, 'Orange': 60,
        'Papaya': 150, 'Grapes': 100, 'Pomegranate': 60, 'Apple': 60,
        'Watermelon': 150, 'Muskmelon': 80, 'Coconut': 30,
        'Arecanut(Betelnut/Supari)': 15,
        # Cash Crops
        'Sugarcane Jaggery': 30,
    }
    
    # Calculate estimated selling price and projected profit
    for crop in active_crops:
        user_name = crop.crop_name_custom.strip().title()
        lookup_name = COMMODITY_ALIASES.get(user_name, user_name)
        if lookup_name in mandi_prices:
            m_price = mandi_prices[lookup_name]['modal']
            
            # Convert UI area/weight unit string into Quintals
            qty = float(crop.quantity)
            u = crop.unit.lower()
            if 'quintal' in u: 
                est_quintals = qty
            elif 'ton' in u: 
                est_quintals = qty * 10
            elif 'kg' in u or 'kilo' in u: 
                est_quintals = qty / 100
            else:
                yield_ac = YIELD_PER_ACRE.get(lookup_name, YIELD_PER_ACRE.get(user_name, 10))
                if 'acre' in u:
                    est_quintals = qty * yield_ac
                elif 'hectare' in u:
                    est_quintals = qty * 2.471 * yield_ac
                elif 'bigha' in u:
                    est_quintals = qty * 0.625 * yield_ac
                else:
                    est_quintals = qty * yield_ac

            crop.est_yield_quintals = est_quintals
            crop.estimated_revenue = est_quintals * float(m_price)
            crop.estimated_profit = crop.estimated_revenue - float(crop.real_cost)
        else:
            crop.est_yield_quintals = None
            crop.estimated_revenue = None
            crop.estimated_profit = None

    # Auto-update health based on inactivity (never auto-upgrades)
    for crop in active_crops:
        crop.auto_update_health()

    # --- 2. TODAY TAB (Tasks) ---
    all_pending_tasks = Task.objects.filter(crop_tracker__user=request.user, is_completed=False).order_by('due_date')
    overdue_tasks = [t for t in all_pending_tasks if t.is_overdue]
    
    # Today + Tomorrow: delta 0 or 1
    today = date.today()
    today_tomorrow_tasks = [t for t in all_pending_tasks if 0 <= (t.due_date - today).days <= 1 and not t.is_completed]
    
    # Later: delta > 1
    upcoming_tasks = [t for t in all_pending_tasks if (t.due_date - today).days > 1 and not t.is_completed]
    total_pending_tasks = len(today_tomorrow_tasks) + len(upcoming_tasks)

    completed_today_tasks = Task.objects.filter(
        crop_tracker__user=request.user, 
        is_completed=True,
    ).order_by('-due_date')[:10]

    # --- Smart Task Recommendations ---
    # Build per-crop suggestions based on health, inactivity, and growth phase.
    # AI tips are cached in session keyed by crop_id to avoid repeated API calls.

    # Fetch current weather once for the user's location
    weather_tasks = []  # global weather-based suggestions shown above crop cards
    try:
        location = request.user.profile.location
        if location and active_crops:
            from home.views import get_current_weather_data, get_alerts_and_forecast, _is_rain, _is_storm, _is_rain_or_storm
            w_data, _ = get_current_weather_data(location)
            if w_data:
                forecast_data, _ = get_alerts_and_forecast(w_data['lat'], w_data['lon'])
                forecast = forecast_data.get('forecast', [])
                current_icon = w_data['icon']
                current_temp = w_data['temperature']
                current_humidity = w_data['humidity']
                current_wind = w_data.get('wind_speed', 0)

                # --- Today's conditions ---
                if _is_storm(current_icon):
                    weather_tasks.append({'icon': '⛈️', 'title': 'Storm today — Support crops, secure equipment', 'when': 'Today', 'priority': 'high'})
                elif _is_rain(current_icon):
                    weather_tasks.append({'icon': '🌧️', 'title': 'Rain today — Do not irrigate', 'when': 'Today', 'priority': 'high'})
                    weather_tasks.append({'icon': '🚫', 'title': 'Avoid pesticide/fertilizer spray (will wash away)', 'when': 'Today', 'priority': 'high'})
                    weather_tasks.append({'icon': '🌊', 'title': 'Check field drainage', 'when': 'Today', 'priority': 'medium'})

                if current_temp >= 40:
                    weather_tasks.append({'icon': '🔥', 'title': f'Extreme heat ({current_temp:.0f}°C) — Irrigate early morning', 'when': 'Today', 'priority': 'high'})
                    weather_tasks.append({'icon': '🌿', 'title': 'Do not spray in afternoon — leaves may burn', 'when': 'Today', 'priority': 'medium'})
                elif current_temp >= 35:
                    weather_tasks.append({'icon': '☀️', 'title': f'Hot day ({current_temp:.0f}°C) — Irrigate in evening', 'when': 'Today', 'priority': 'medium'})

                if current_temp <= 5:
                    weather_tasks.append({'icon': '❄️', 'title': f'Frost possible ({current_temp:.0f}°C) — Cover crops', 'when': 'Today', 'priority': 'high'})
                elif current_temp <= 10:
                    weather_tasks.append({'icon': '🥶', 'title': f'Very cold ({current_temp:.0f}°C) — Protect nursery plants', 'when': 'Today', 'priority': 'medium'})

                if current_humidity >= 85 and not _is_rain_or_storm(current_icon):
                    weather_tasks.append({'icon': '🍄', 'title': 'High humidity — Check for fungal diseases', 'when': 'Today', 'priority': 'medium'})

                if current_wind >= 10:
                    weather_tasks.append({'icon': '💨', 'title': f'Strong wind ({current_wind:.0f} m/s) — Support tall crops', 'when': 'Today', 'priority': 'medium'})

                # --- Forecast-based suggestions (next 1–4 days) ---
                seen_conditions = set()
                for i, day in enumerate(forecast[:4], start=1):
                    day_label = f'In {i} days' if i > 1 else 'Tomorrow'
                    ficon = day['icon']
                    fmax = day['max_temp']
                    fmin = day['min_temp']
                    fhum = day['humidity']

                    if _is_rain_or_storm(ficon) and 'rain' not in seen_conditions:
                        seen_conditions.add('rain')
                        weather_tasks.append({'icon': '🌦️', 'title': f'{day_label} — Rain possible, apply fertilizer/pesticide today', 'when': day_label, 'priority': 'high'})
                        weather_tasks.append({'icon': '🌊', 'title': f'{day_label} — Clean drainage before rain', 'when': day_label, 'priority': 'medium'})

                    if fmax >= 42 and 'heat' not in seen_conditions:
                        seen_conditions.add('heat')
                        weather_tasks.append({'icon': '🌡️', 'title': f'{day_label} — Extreme heat ({fmax:.0f}°C), arrange irrigation', 'when': day_label, 'priority': 'high'})

                    if fmin <= 3 and 'frost' not in seen_conditions:
                        seen_conditions.add('frost')
                        weather_tasks.append({'icon': '🧊', 'title': f'{day_label} — Frost warning ({fmin:.0f}°C), prepare crop protection', 'when': day_label, 'priority': 'high'})

                    if fhum >= 90 and not _is_rain_or_storm(ficon) and 'humidity' not in seen_conditions:
                        seen_conditions.add('humidity')
                        weather_tasks.append({'icon': '💧', 'title': f'{day_label} — High humidity, spray fungicide', 'when': day_label, 'priority': 'medium'})

    except Exception:
        pass  # Weather is best-effort; never break the dashboard

    recommendations = []
    ai_tips_cache = request.session.get('ai_tips_v2', {})
    # Keep only current-format dict entries; drop old string entries and old 2-part keys
    ai_tips_cache = {k: v for k, v in ai_tips_cache.items() if isinstance(v, dict) and k.count('_') >= 2}
    # Clear legacy Hindi cache
    request.session.pop('ai_tips', None)

    for crop in active_crops:
        days_idle = crop.days_since_last_log
        crop_id_str = str(crop.id)

        # Count pending tasks for this crop today (used to bust AI cache when tasks are added)
        pending_task_count = Task.objects.filter(
            crop_tracker=crop, is_completed=False, due_date=date.today()
        ).count()

        # Fetch all task titles for this crop (pending + completed today) to suppress duplicates
        existing_titles = set(
            Task.objects.filter(crop_tracker=crop)
            .filter(models.Q(is_completed=False) | models.Q(due_date=date.today()))
            .values_list('title', flat=True)
        )

        # Determine suggestions — skip any whose title already exists as a task
        suggestions = []
        if crop.health == 'At Risk':
            t = f'Water {crop.display_name} immediately'
            if t not in existing_titles:
                suggestions.append({'icon': '💧', 'title': t, 'priority': 'high'})
            t = f'Check health of {crop.display_name}'
            if t not in existing_titles:
                suggestions.append({'icon': '🔍', 'title': t, 'priority': 'high'})
        elif crop.health == 'Attention':
            t = f'Water {crop.display_name}'
            if t not in existing_titles:
                suggestions.append({'icon': '💧', 'title': t, 'priority': 'medium'})
            t = f'Check {crop.display_name}'
            if t not in existing_titles:
                suggestions.append({'icon': '🔍', 'title': t, 'priority': 'medium'})

        if crop.growth_phase in ('Vegetative', 'Flowering'):
            t = f'Add fertilizer to {crop.display_name}'
            if t not in existing_titles:
                suggestions.append({'icon': '🧪', 'title': t, 'priority': 'medium'})
        if crop.growth_phase in ('Vegetative', 'Fruiting', 'Flowering'):
            t = f'Spray pesticide on {crop.display_name}'
            if t not in existing_titles:
                suggestions.append({'icon': '🐛', 'title': t, 'priority': 'low'})
        if days_idle >= 2 and not suggestions:
            t = f'Inspect {crop.display_name}'
            if t not in existing_titles:
                suggestions.append({'icon': '👁️', 'title': t, 'priority': 'low'})

        # Fetch AI tip — cache key includes pending task count so adding a task forces a fresh suggestion
        cache_key = f"{crop_id_str}_{crop.health}_{pending_task_count}"
        if cache_key not in ai_tips_cache:
            existing_str = ', '.join(existing_titles) if existing_titles else 'None'
            try:
                prompt = (
                    f"Crop: {crop.display_name}, Stage: {crop.growth_phase}, Health: {crop.health}. "
                    f"Previously added tasks: {existing_str}. "
                    f"Answer in JSON (no markdown): "
                    f'{{"tip": "Practical advice in 2 sentences in English - what signs to look for and what to do", '
                    f'"task": "A new task not in the list above (less than 15 words, in English, starting with emoji)"}}')
                import json as _json, re as _re
                raw = generate_ai_response(prompt)
                match = _re.search(r'\{.*?\}', raw, _re.DOTALL)
                parsed = _json.loads(match.group(0)) if match else {}
                tip = _re.sub(r'<[^>]+>', '', parsed.get('tip', '')).strip()
                ai_task = _re.sub(r'<[^>]+>', '', parsed.get('task', '')).strip()
            except Exception:
                tip = f"Care for {crop.display_name} regularly. Take immediate action if you see yellowing or spots on leaves."
                ai_task = f"🔍 Check leaves of {crop.display_name}"
            ai_tips_cache[cache_key] = {'tip': tip, 'task': ai_task}

        cached = ai_tips_cache[cache_key]
        ai_task = cached.get('task', '')
        if ai_task and ai_task not in existing_titles:
            suggestions.append({'icon': '🤖', 'title': ai_task, 'priority': 'ai'})

        if suggestions:
            recommendations.append({
                'crop': crop,
                'suggestions': suggestions,
                'ai_tip': cached.get('tip', ''),
            })

    request.session['ai_tips_v2'] = ai_tips_cache

    # --- 3. MONEY TAB ---
    completed_crops = CropTracker.objects.filter(user=request.user, status='Completed')
    
    all_financials = FinancialEntry.objects.filter(crop_tracker__user=request.user).order_by('-date', '-id')
    
    total_revenue = all_financials.filter(entry_type='Revenue').aggregate(Sum('amount'))['amount__sum'] or 0
    total_expense = all_financials.filter(entry_type='Expense').aggregate(Sum('amount'))['amount__sum'] or 0
    total_revenue = float(total_revenue)
    total_expense = float(total_expense)
    total_profit = total_revenue - total_expense

    # --- Chart data ---
    import json as _json
    from datetime import timedelta

    # 1. Expense by category (donut)
    expense_by_cat = (
        all_financials.filter(entry_type='Expense')
        .values('category')
        .annotate(total=Sum('amount'))
        .order_by('-total')
    )
    chart_expense_labels = _json.dumps([e['category'] for e in expense_by_cat])
    chart_expense_values = _json.dumps([float(e['total']) for e in expense_by_cat])

    # 2. Per-crop invested vs estimated revenue (bar)
    chart_crop_names = _json.dumps(
        [f"{c.emoji} {c.display_name}" for c in active_crops]
    )
    chart_crop_invested = _json.dumps([float(c.real_cost) for c in active_crops])
    chart_crop_revenue = _json.dumps(
        [float(c.estimated_revenue) if c.estimated_revenue is not None else 0 for c in active_crops]
    )

    # 3. Daily spending last 30 days (line)
    thirty_days_ago = date.today() - timedelta(days=29)
    daily_spend = (
        all_financials.filter(entry_type='Expense', date__gte=thirty_days_ago)
        .values('date')
        .annotate(total=Sum('amount'))
        .order_by('date')
    )
    chart_spend_dates = _json.dumps([str(d['date']) for d in daily_spend])
    chart_spend_values = _json.dumps([float(d['total']) for d in daily_spend])

    # All Agmarknet-verified commodity names with user-friendly name, API name, emoji
    SUPPORTED_CROP_META = [
        # Cereals
        {'name': 'Wheat',            'alias': 'Wheat',                       'emoji': '🌾', 'category': 'Cereal'},
        {'name': 'Rice',             'alias': 'Rice',                        'emoji': '🍚', 'category': 'Cereal'},
        {'name': 'Paddy',            'alias': 'Paddy(Dhan)(Common)',         'emoji': '🌿', 'category': 'Cereal'},
        {'name': 'Maize',            'alias': 'Maize',                       'emoji': '🌽', 'category': 'Cereal'},
        {'name': 'Bajra',            'alias': 'Bajra(Pearl Millet/Cumbu)',   'emoji': '🍌', 'category': 'Cereal'},
        {'name': 'Jowar',            'alias': 'Jowar(Sorghum)',              'emoji': '🌾', 'category': 'Cereal'},
        {'name': 'Ragi',             'alias': 'Ragi (Finger Millet)',        'emoji': '🌿', 'category': 'Cereal'},
        {'name': 'Barley',           'alias': 'Barley (Jau)',                'emoji': '🌾', 'category': 'Cereal'},
        # Pulses
        {'name': 'Gram',             'alias': 'Gram',                        'emoji': '🫘', 'category': 'Pulse'},
        {'name': 'Moong',            'alias': 'Moong (Green Gram)(Whole)',   'emoji': '🌱', 'category': 'Pulse'},
        {'name': 'Urad',             'alias': 'Urad (Black Matpe)(Whole)',   'emoji': '🫘', 'category': 'Pulse'},
        {'name': 'Masoor',           'alias': 'Lentil (Masur)(Whole)',       'emoji': '🫘', 'category': 'Pulse'},
        {'name': 'Arhar (Tur)',      'alias': 'Arhar (Tur/Red Gram)(Whole)', 'emoji': '🫘', 'category': 'Pulse'},
        {'name': 'Rajma',            'alias': 'Rajma',                       'emoji': '🫘', 'category': 'Pulse'},
        {'name': 'Moth',             'alias': 'Moth(Whole)',                 'emoji': '🫘', 'category': 'Pulse'},
        {'name': 'Horse Gram',       'alias': 'Kulthi(Horse Gram)',          'emoji': '🫘', 'category': 'Pulse'},
        # Oilseeds
        {'name': 'Mustard',          'alias': 'Mustard',                     'emoji': '🌻', 'category': 'Oilseed'},
        {'name': 'Soyabean',         'alias': 'Soyabean',                    'emoji': '🫘', 'category': 'Oilseed'},
        {'name': 'Groundnut',        'alias': 'Groundnut',                   'emoji': '🥜', 'category': 'Oilseed'},
        {'name': 'Sunflower',        'alias': 'Sunflower',                   'emoji': '🌻', 'category': 'Oilseed'},
        {'name': 'Sesame (Til)',      'alias': 'Sesame(Gingelly)',            'emoji': '🌿', 'category': 'Oilseed'},
        {'name': 'Castor Seed',      'alias': 'Castor Seed',                 'emoji': '🌿', 'category': 'Oilseed'},
        {'name': 'Linseed',          'alias': 'Linseed',                     'emoji': '🌿', 'category': 'Oilseed'},
        {'name': 'Niger Seed',       'alias': 'Niger Seed (Ramtil)',         'emoji': '🌿', 'category': 'Oilseed'},
        {'name': 'Safflower',        'alias': 'Safflower',                   'emoji': '🌷', 'category': 'Oilseed'},
        {'name': 'Cotton',           'alias': 'Cotton',                      'emoji': '🌸', 'category': 'Oilseed'},
        # Vegetables
        {'name': 'Tomato',           'alias': 'Tomato',                      'emoji': '🍅', 'category': 'Vegetable'},
        {'name': 'Onion',            'alias': 'Onion',                       'emoji': '🧅', 'category': 'Vegetable'},
        {'name': 'Potato',           'alias': 'Potato',                      'emoji': '🥔', 'category': 'Vegetable'},
        {'name': 'Brinjal',          'alias': 'Brinjal',                     'emoji': '🍆', 'category': 'Vegetable'},
        {'name': 'Cauliflower',      'alias': 'Cauliflower',                 'emoji': '🥦', 'category': 'Vegetable'},
        {'name': 'Cabbage',          'alias': 'Cabbage',                     'emoji': '🥦', 'category': 'Vegetable'},
        {'name': 'Capsicum',         'alias': 'Capsicum',                    'emoji': '🌶️', 'category': 'Vegetable'},
        {'name': 'Bhindi',           'alias': 'Ladyfinger(Bhindi)',          'emoji': '🫑', 'category': 'Vegetable'},
        {'name': 'Cucumber',         'alias': 'Cucumber',                    'emoji': '🥒', 'category': 'Vegetable'},
        {'name': 'Peas',             'alias': 'Peas Green',                  'emoji': '🌱', 'category': 'Vegetable'},
        {'name': 'Carrot',           'alias': 'Carrot',                      'emoji': '🥕', 'category': 'Vegetable'},
        {'name': 'Radish',           'alias': 'Radish',                      'emoji': '👀',  'category': 'Vegetable'},
        {'name': 'Beet Root',        'alias': 'Beet Root',                   'emoji': '🛒', 'category': 'Vegetable'},
        {'name': 'Spinach',          'alias': 'Spinach(Palak)',              'emoji': '🌿', 'category': 'Vegetable'},
        {'name': 'Methi',            'alias': 'Methi(Leaves)',               'emoji': '🌿', 'category': 'Vegetable'},
        {'name': 'Drumstick',        'alias': 'Drumstick',                   'emoji': '🌿', 'category': 'Vegetable'},
        {'name': 'Cluster Beans',    'alias': 'Cluster Beans',               'emoji': '🌱', 'category': 'Vegetable'},
        # Spices
        {'name': 'Turmeric',         'alias': 'Turmeric',                    'emoji': '🟡', 'category': 'Spice'},
        {'name': 'Garlic',           'alias': 'Garlic',                      'emoji': '🧄', 'category': 'Spice'},
        {'name': 'Ginger',           'alias': 'Ginger(Dry)',                 'emoji': '🫐', 'category': 'Spice'},
        {'name': 'Chilli',           'alias': 'Chilly Red',                  'emoji': '🌶️', 'category': 'Spice'},
        {'name': 'Coriander',        'alias': 'Coriander(Leaves)',           'emoji': '🌿', 'category': 'Spice'},
        {'name': 'Dill',             'alias': 'Dill(Suva/Soya)',             'emoji': '🌿', 'category': 'Spice'},
        # Fruits
        {'name': 'Banana',           'alias': 'Banana',                      'emoji': '🍌', 'category': 'Fruit'},
        {'name': 'Mango',            'alias': 'Mango',                       'emoji': '🥭', 'category': 'Fruit'},
        {'name': 'Tomato',           'alias': 'Tomato',                      'emoji': '🍅', 'category': 'Fruit'},
        {'name': 'Guava',            'alias': 'Guava',                       'emoji': '🍏', 'category': 'Fruit'},
        {'name': 'Orange',           'alias': 'Orange',                      'emoji': '🍊', 'category': 'Fruit'},
        {'name': 'Papaya',           'alias': 'Papaya',                      'emoji': '🍈', 'category': 'Fruit'},
        {'name': 'Grapes',           'alias': 'Grapes',                      'emoji': '🍇', 'category': 'Fruit'},
        {'name': 'Pomegranate',      'alias': 'Pomegranate',                 'emoji': '🍎', 'category': 'Fruit'},
        {'name': 'Apple',            'alias': 'Apple',                       'emoji': '🍎', 'category': 'Fruit'},
        {'name': 'Watermelon',       'alias': 'Watermelon',                  'emoji': '🍉', 'category': 'Fruit'},
        {'name': 'Muskmelon',        'alias': 'Muskmelon',                   'emoji': '🍈', 'category': 'Fruit'},
        {'name': 'Coconut',          'alias': 'Coconut',                     'emoji': '🥥', 'category': 'Fruit'},
        {'name': 'Arecanut',         'alias': 'Arecanut(Betelnut/Supari)',   'emoji': '🌰', 'category': 'Fruit'},
        # Cash Crops
        {'name': 'Sugarcane',        'alias': 'Sugarcane Jaggery',           'emoji': '🎋', 'category': 'Cash Crop'},
    ]

    context = {
        'active_crops': active_crops,
        'mandi_prices': mandi_prices,
        'mandi_is_fallback': mandi_is_fallback,
        'supported_crops': SUPPORTED_CROP_META,
        
        'overdue_tasks': overdue_tasks,
        'today_tomorrow_tasks': today_tomorrow_tasks,
        'upcoming_tasks': upcoming_tasks,
        'total_pending_tasks': total_pending_tasks,
        'completed_today_tasks': completed_today_tasks,
        'recommendations': recommendations,
        'weather_tasks': weather_tasks,
        
        'all_financials': all_financials,
        'total_revenue': total_revenue,
        'total_expense': total_expense,
        'total_profit': total_profit,
        'chart_expense_labels': chart_expense_labels,
        'chart_expense_values': chart_expense_values,
        'chart_crop_names': chart_crop_names,
        'chart_crop_invested': chart_crop_invested,
        'chart_crop_revenue': chart_crop_revenue,
        'chart_spend_dates': chart_spend_dates,
        'chart_spend_values': chart_spend_values,
    }
    return render(request, 'tracker/dashboard.html', context)


# -------------------------------------------------------------
# QUICK ACTIONS (Bottom Sheets & One-Tap Actions)
# -------------------------------------------------------------

@login_required
def add_crop(request):
    if request.method == 'POST':
        # Create directly from POST data
        crop_name = request.POST.get('crop_name_custom', 'Unknown')
        emoji = request.POST.get('emoji', '🌿')
        location_field = request.POST.get('location', '')
        quantity = request.POST.get('quantity', 0)
        unit = request.POST.get('unit', 'acres')
        plating_date_str = request.POST.get('planting_date') or str(date.today())
        
        CropTracker.objects.create(
            user=request.user,
            crop_name_custom=crop_name,
            emoji=emoji,
            location=location_field, # Using the 'location' field for Field Name as requested
            quantity=quantity,
            unit=unit,
            planting_date=plating_date_str,
            status='Active'
        )
    return redirect('tracker_dashboard')

@login_required
def update_crop_details(request, tracker_id):
    crop_tracker = get_object_or_404(CropTracker, id=tracker_id, user=request.user)
    if request.method == 'POST':
        crop_name = request.POST.get('crop_name_custom')
        location = request.POST.get('location')
        quantity = request.POST.get('quantity')
        unit = request.POST.get('unit')
        growth_phase = request.POST.get('growth_phase')
        
        if crop_name: crop_tracker.crop_name_custom = crop_name
        if location is not None: crop_tracker.location = location
        if quantity: crop_tracker.quantity = quantity
        if unit: crop_tracker.unit = unit
        
        if growth_phase and growth_phase != crop_tracker.growth_phase:
            crop_tracker.growth_phase = growth_phase
            from django.utils import timezone
            crop_tracker.phase_updated_date = timezone.now().date()

        crop_tracker.save()
    return redirect('tracker_dashboard')

@login_required
def update_crop(request, tracker_id):
    crop_tracker = get_object_or_404(CropTracker, id=tracker_id, user=request.user)
    if request.method == 'POST':
        form = CropUpdateForm(request.POST, instance=crop_tracker)
        if form.is_valid():
            form.save()
            return redirect('tracker_dashboard')
    else:
        form = CropUpdateForm(instance=crop_tracker)
    
    return render(request, 'tracker/update_crop.html', {
        'form': form, 
        'crop': crop_tracker,
        'financial_form': FinancialEntryForm(),
        'task_form': TaskForm(),
        'financials': crop_tracker.financials.all(),
        'tasks': crop_tracker.tasks.all(),
    })

@login_required
def add_quick_log(request, tracker_id):
    crop_tracker = get_object_or_404(CropTracker, id=tracker_id, user=request.user)
    if request.method == 'POST':
        activity_type = request.POST.get('activity_type')
        details = request.POST.get('details', '')
        if activity_type:
            ActivityLog.objects.create(
                crop_tracker=crop_tracker,
                activity_type=activity_type,
                details=details
            )
    return redirect('tracker_dashboard')

@login_required
def update_health(request, tracker_id):
    crop_tracker = get_object_or_404(CropTracker, id=tracker_id, user=request.user)
    if request.method == 'POST':
        new_health = request.POST.get('health')
        if new_health in dict(CropTracker._meta.get_field('health').choices):
            crop_tracker.health = new_health
            crop_tracker.save()
    return redirect('tracker_dashboard')

@login_required
def harvest_crop(request, tracker_id):
    crop_tracker = get_object_or_404(CropTracker, id=tracker_id, user=request.user)
    if request.method == 'POST':
        crop_tracker.status = 'Completed'
        crop_tracker.harvest_date = date.today()
        crop_tracker.save()
    return redirect('tracker_dashboard')

@login_required
def add_suggested_task(request):
    """Quick-add a pre-filled suggested task from the recommendations panel."""
    if request.method == 'POST':
        tracker_id = request.POST.get('crop_tracker_id')
        title = request.POST.get('title', '').strip()
        if tracker_id and title:
            crop_tracker = get_object_or_404(CropTracker, id=tracker_id, user=request.user)
            Task.objects.create(
                crop_tracker=crop_tracker,
                title=title,
                due_date=date.today()
            )
    return redirect('tracker_dashboard')


@login_required
def add_task(request):
    if request.method == 'POST':
        tracker_id = request.POST.get('crop_tracker_id')
        title = request.POST.get('title')
        due_date = request.POST.get('due_date') or str(date.today())
        
        if tracker_id and title:
            # Check if tracker belongs to user
            crop_tracker = get_object_or_404(CropTracker, id=tracker_id, user=request.user)
            Task.objects.create(
                crop_tracker=crop_tracker,
                title=title,
                due_date=due_date
            )
    return redirect('tracker_dashboard')

@login_required
def toggle_task(request, task_id):
    if request.method == 'POST':
        task = get_object_or_404(Task, id=task_id, crop_tracker__user=request.user)
        task.is_completed = not task.is_completed
        task.save()
    # It redirects to dashboard instead of update_crop because of new UI
    return redirect('tracker_dashboard')

@login_required
def check_custom_crop(request):
    """AJAX: check if a user-typed crop name exists in the Mandi API."""
    name = request.GET.get('name', '').strip().title()
    if not name:
        return JsonResponse({'found': False})
    
    from core.mandi_api import get_mandi_prices, COMMODITY_ALIASES
    lookup = COMMODITY_ALIASES.get(name, name)
    try:
        from concurrent.futures import ThreadPoolExecutor
        with ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(get_mandi_prices, [lookup])
            prices = future.result(timeout=4)
    except Exception:
        prices = {}
    if lookup in prices:
        return JsonResponse({
            'found': True,
            'alias': lookup,
            'price': prices[lookup]['modal'],
            'market': prices[lookup]['market'],
        })
    return JsonResponse({'found': False})


@login_required
def add_financial_entry(request):
    if request.method == 'POST':
        tracker_id = request.POST.get('crop_tracker_id')
        entry_type = request.POST.get('entry_type') # Revenue or Expense
        category = request.POST.get('category', 'Other')
        amount_str = request.POST.get('amount', 0)
        
        try:
            amount = Decimal(str(amount_str))
        except:
            amount = Decimal(0)
            
        if tracker_id and amount > 0:
            crop_tracker = get_object_or_404(CropTracker, id=tracker_id, user=request.user)
            entry = FinancialEntry.objects.create(
                crop_tracker=crop_tracker,
                entry_type=entry_type,
                category=category,
                amount=amount
            )
            # Auto-update the ledger totals
            if entry.entry_type == 'Expense':
                crop_tracker.cost += entry.amount
            else:
                crop_tracker.revenue += entry.amount
            crop_tracker.save()
            
    return redirect('tracker_dashboard')


@login_required
def delete_financial_entry(request, entry_id):
    entry = get_object_or_404(FinancialEntry, id=entry_id, crop_tracker__user=request.user)
    crop_tracker = entry.crop_tracker
    if entry.entry_type == 'Expense':
        crop_tracker.cost = max(Decimal(0), crop_tracker.cost - entry.amount)
    else:
        crop_tracker.revenue = max(Decimal(0), crop_tracker.revenue - entry.amount)
    crop_tracker.save()
    entry.delete()
    return redirect(request.META.get('HTTP_REFERER', 'tracker_dashboard'))


@login_required
def edit_financial_entry(request, entry_id):
    entry = get_object_or_404(FinancialEntry, id=entry_id, crop_tracker__user=request.user)
    if request.method == 'POST':
        new_type = request.POST.get('entry_type', entry.entry_type)
        new_category = request.POST.get('category', entry.category)
        new_description = request.POST.get('description', '')
        try:
            new_amount = Decimal(str(request.POST.get('amount', entry.amount)))
            if new_amount <= 0:
                raise ValueError
        except Exception:
            new_amount = entry.amount

        crop_tracker = entry.crop_tracker
        # Reverse old effect on crop totals
        if entry.entry_type == 'Expense':
            crop_tracker.cost = max(Decimal(0), crop_tracker.cost - entry.amount)
        else:
            crop_tracker.revenue = max(Decimal(0), crop_tracker.revenue - entry.amount)

        # Save updated entry
        entry.entry_type = new_type
        entry.category = new_category
        entry.amount = new_amount
        entry.description = new_description
        entry.save()

        # Apply new effect on crop totals
        if new_type == 'Expense':
            crop_tracker.cost += new_amount
        else:
            crop_tracker.revenue += new_amount
        crop_tracker.save()

    return redirect(request.META.get('HTTP_REFERER', 'tracker_dashboard'))
