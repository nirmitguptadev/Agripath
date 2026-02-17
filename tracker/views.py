from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import CropTracker
from .forms import CropTrackerForm, CropUpdateForm
from .recommendation_engine import get_hybrid_recommendations
from dictionary.models import Crop
from django.db.models import Sum
from django.db import models

@login_required
def tracker_dashboard(request):
    # 1. Active Crops
    active_crops = CropTracker.objects.filter(user=request.user, status='Active').order_by('-planting_date')
    
    # 2. Completed Crops (History)
    completed_crops = CropTracker.objects.filter(user=request.user, status='Completed').order_by('-harvest_date')
    
    # Calculate Total Profit
    total_profit = sum(c.profit for c in completed_crops)

    # 3. Recommendations using hybrid approach
    try:
        location = request.user.profile.location
    except:
        location = None
    
    recommendations = get_hybrid_recommendations(request.user, location, limit=6) if location else []

    # Financial Aggregates for Chart
    active_crops_cost = active_crops.aggregate(Sum('cost'))['cost__sum'] or 0
    completed_crops_cost = completed_crops.aggregate(Sum('cost'))['cost__sum'] or 0
    total_revenue = completed_crops.aggregate(Sum('revenue'))['revenue__sum'] or 0

    # Explicitly cast to float/int to ensure they are primitives and not Django wrappers
    active_crops_cost = float(active_crops_cost)
    completed_crops_cost = float(completed_crops_cost)
    total_revenue = float(total_revenue)
    total_profit = float(total_profit)

    # Debugging types
    print(f"DEBUG: active_crops_cost: {type(active_crops_cost)} = {active_crops_cost}")
    print(f"DEBUG: total_profit: {type(total_profit)} = {total_profit}")

    return render(request, 'tracker/dashboard.html', {
        'active_crops': active_crops,
        'completed_crops': completed_crops,
        'total_profit': total_profit,
        'recommendations': recommendations,
        'location': location,
        'active_crops_cost': active_crops_cost,
        'completed_crops_cost': completed_crops_cost,
        'total_revenue': total_revenue
    })

@login_required
def add_crop(request):
    if request.method == 'POST':
        form = CropTrackerForm(request.POST)
        if form.is_valid():
            crop_tracker = form.save(commit=False)
            crop_tracker.user = request.user
            # Save the location where this crop is being grown (snapshot)
            if hasattr(request.user, 'profile') and request.user.profile.location:
                crop_tracker.location = request.user.profile.location
            crop_tracker.save()
            return redirect('tracker_dashboard')
    else:
        form = CropTrackerForm()
    
    return render(request, 'tracker/add_crop.html', {'form': form})

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
        'crop': crop_tracker
    })
