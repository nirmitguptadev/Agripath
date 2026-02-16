from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from home.views import get_current_weather_data
from tracker.models import CropTracker
from django.db.models import Sum

@login_required
def dashboard(request):
    try:
        location = request.user.profile.location
    except:
        location = None
    
    # Weather data
    weather_data = None
    if location:
        weather_data, _ = get_current_weather_data(location)
    
    # Tracker stats
    active_crops_count = CropTracker.objects.filter(user=request.user, status='Active').count()
    total_profit = CropTracker.objects.filter(user=request.user, status='Completed').aggregate(
        profit=Sum('revenue') - Sum('cost')
    )['profit'] or 0
    
    context = {
        'location': location,
        'weather_data': weather_data,
        'active_crops_count': active_crops_count,
        'total_profit': total_profit,
    }
    
    return render(request, 'dashboard.html', context)
