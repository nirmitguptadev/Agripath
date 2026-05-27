from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from home.views import (
    get_current_weather_data, 
    get_alerts_and_forecast,
    _is_rain,
    _is_storm,
    _is_rain_or_storm,
    get_seasonal_thresholds
)
from tracker.models import CropTracker
from django.db.models import Sum
from core.mandi_api import get_mandi_prices, DEFAULT_CROPS
from core.news_api import get_agri_news


@login_required
def dashboard(request):
    try:
        location = request.user.profile.location
    except:
        location = None

    # Weather data + forecast
    weather_data = None
    weather_alerts = []
    if location:
        weather_data, _ = get_current_weather_data(location)
        if weather_data:
            forecast_data, _ = get_alerts_and_forecast(weather_data['lat'], weather_data['lon'])
            forecast = forecast_data.get('forecast', [])

            def rain_msg(label):
                return f'{label}: Rain Expected — Delay fertilizer/pesticide spraying'

            def storm_msg(label):
                return f'{label}: Thunderstorm — Support crops, secure loose equipment'

            def heat_high_msg(label, t):
                return f'{label}: High Heat ({t:.0f}°C) — Irrigate early morning'

            def heat_mod_msg(label, t):
                return f'{label}: Moderate Heat ({t:.0f}°C) — Irrigate in the evening'

            def frost_msg(label, t):
                return f'{label}: Frost Warning ({t:.0f}°C) — Cover susceptible crops'

            def cold_msg(label, t):
                return f'{label}: Cold Weather ({t:.0f}°C) — Protect nursery seedlings'

            def humidity_msg(label, h):
                return f'{label}: High Humidity ({h}%) — Monitor for fungal diseases'

            for i, day in enumerate(forecast):
                day_label = 'Today' if i == 0 else ('Tomorrow' if i == 1 else f'in {i} Days')
                icon = day['icon']
                fmax = day['max_temp']
                fmin = day['min_temp']
                fhum = day['humidity']
                
                high_heat, severe_heat, cold_warning, frost_danger = get_seasonal_thresholds(day['date'])

                if _is_storm(icon):
                    weather_alerts.append({'icon': '⛈️', 'msg': storm_msg(day_label), 'level': 'danger'})
                elif _is_rain(icon):
                    weather_alerts.append({'icon': '🌧️', 'msg': rain_msg(day_label), 'level': 'warning'})

                if fmax >= severe_heat:
                    weather_alerts.append({'icon': '🔥', 'msg': heat_high_msg(day_label, fmax), 'level': 'danger'})
                elif fmax >= high_heat:
                    weather_alerts.append({'icon': '☀️', 'msg': heat_mod_msg(day_label, fmax), 'level': 'warning'})

                if fmin <= frost_danger:
                    weather_alerts.append({'icon': '🧊', 'msg': frost_msg(day_label, fmin), 'level': 'danger'})
                elif fmin <= cold_warning:
                    weather_alerts.append({'icon': '❄️', 'msg': cold_msg(day_label, fmin), 'level': 'warning'})

                if fhum >= 90 and not _is_rain_or_storm(icon):
                    weather_alerts.append({'icon': '🍄', 'msg': humidity_msg(day_label, fhum), 'level': 'info'})

    # Tracker stats
    active_crops = CropTracker.objects.filter(user=request.user, status='Active')
    active_crops_count = active_crops.count()
    from tracker.models import FinancialEntry
    all_financials = FinancialEntry.objects.filter(crop_tracker__user=request.user)
    t_rev = all_financials.filter(entry_type='Revenue').aggregate(Sum('amount'))['amount__sum'] or 0
    t_exp = all_financials.filter(entry_type='Expense').aggregate(Sum('amount'))['amount__sum'] or 0
    total_profit = float(t_rev) - float(t_exp)

    # ── Live Mandi prices ─────────────────────────────────────────────────
    # Only fetch prices for the user's active tracked crops + a small mainstream
    # baseline. Do NOT fetch the full SUPPORTED_CROP_META list — that list is
    # only used as a picker UI and should never drive API calls.
    mandi_prices = {}
    try:
        user_crops = list(
            active_crops.values_list('crop_name_custom', flat=True).distinct()
        )
        user_crops = [c.strip().title() for c in user_crops if c and c.strip()]
        combined = list(dict.fromkeys(user_crops + DEFAULT_CROPS))
        from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeout
        with ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(get_mandi_prices, combined)
            try:
                mandi_prices = future.result(timeout=5)
            except (FuturesTimeout, Exception):
                mandi_prices = {}
    except Exception as e:
        print(f"Mandi prices error: {e}")

    from core.mandi_api import prices_are_fallback as mandi_is_fallback
    news_items = get_agri_news()

    context = {
        'location': location,
        'weather_data': weather_data,
        'weather_alerts': weather_alerts,
        'active_crops_count': active_crops_count,
        'total_profit': total_profit,
        'mandi_prices': mandi_prices,
        'mandi_is_fallback': mandi_is_fallback,
        'news_items': news_items,
    }

    return render(request, 'dashboard.html', context)
