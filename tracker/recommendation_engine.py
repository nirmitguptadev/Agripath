from django.db.models import Sum, Avg, Count, F
from .models import CropTracker
from accounts.models import Profile
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from collections import Counter

def get_location_based_recommendations(user_location, limit=6):
    """
    Get crop recommendations based on profitable crops from all users in the same location
    """
    if not user_location:
        return []
    
    # Get all completed profitable crops from users in the same location
    location_crops = CropTracker.objects.filter(
        user__profile__location__iexact=user_location,
        status='Completed',
        revenue__gt=F('cost')
    ).select_related('crop', 'user__profile')
    
    if not location_crops.exists():
        return []
    
    # Calculate profitability metrics for each crop
    crop_stats = {}
    for tracker in location_crops:
        crop_name = tracker.crop.name if tracker.crop else tracker.crop_name_custom
        if not crop_name:
            continue
            
        profit = float(tracker.revenue - tracker.cost)
        roi = (profit / float(tracker.cost)) * 100 if tracker.cost > 0 else 0
        
        if crop_name not in crop_stats:
            crop_stats[crop_name] = {
                'total_profit': 0,
                'count': 0,
                'total_roi': 0,
                'success_rate': 0
            }
        
        crop_stats[crop_name]['total_profit'] += profit
        crop_stats[crop_name]['count'] += 1
        crop_stats[crop_name]['total_roi'] += roi
    
    # Calculate averages and rank crops
    recommendations = []
    for crop_name, stats in crop_stats.items():
        avg_profit = stats['total_profit'] / stats['count']
        avg_roi = stats['total_roi'] / stats['count']
        popularity = stats['count']
        
        # Weighted score: 40% avg profit, 40% ROI, 20% popularity
        score = (avg_profit * 0.4) + (avg_roi * 0.4) + (popularity * 100 * 0.2)
        
        recommendations.append({
            'name': crop_name,
            'score': score,
            'avg_profit': avg_profit,
            'success_count': popularity,
            'is_proven': True
        })
    
    # Sort by score and return top recommendations
    recommendations.sort(key=lambda x: x['score'], reverse=True)
    return recommendations[:limit]


def get_hybrid_recommendations(user, user_location, limit=6):
    """
    Hybrid recommendation: Combine location-based collaborative filtering with ML predictions
    """
    recommendations = []
    seen = set()
    
    # 1. Get location-based recommendations (collaborative filtering)
    location_recs = get_location_based_recommendations(user_location, limit=4)
    for rec in location_recs:
        crop_lower = rec['name'].lower()
        if crop_lower not in seen:
            recommendations.append({
                'name': rec['name'],
                'is_proven': True,
                'source': 'community'
            })
            seen.add(crop_lower)
    
    # 2. Add user's own successful crops if not already included
    user_profitable = CropTracker.objects.filter(
        user=user,
        status='Completed',
        revenue__gt=F('cost')
    ).values('crop__name', 'crop_name_custom').annotate(
        avg_profit=Avg(F('revenue') - F('cost'))
    ).order_by('-avg_profit')[:2]
    
    for crop_data in user_profitable:
        crop_name = crop_data['crop__name'] or crop_data['crop_name_custom']
        if crop_name:
            crop_lower = crop_name.lower()
            if crop_lower not in seen and len(recommendations) < limit:
                recommendations.append({
                    'name': crop_name,
                    'is_proven': True,
                    'source': 'personal'
                })
                seen.add(crop_lower)
    
    # 3. Fill remaining slots with ML model predictions
    if len(recommendations) < limit:
        try:
            from core.crop_model import predict_suitable_crops, get_soil_data_by_location
            soil_data = get_soil_data_by_location(user_location)
            model_input = {
                'N': soil_data['N'], 'P': soil_data['P'], 'K': soil_data['K'],
                'temperature': soil_data['temperature'], 
                'humidity': soil_data['humidity'],
                'ph': soil_data['ph'], 
                'rainfall': soil_data['rainfall']
            }
            ai_suggestions = predict_suitable_crops(model_input)
            
            for crop_name in ai_suggestions:
                crop_lower = crop_name.lower()
                if crop_lower not in seen and len(recommendations) < limit:
                    recommendations.append({
                        'name': crop_name,
                        'is_proven': False,
                        'source': 'ai'
                    })
                    seen.add(crop_lower)
        except:
            pass
    
    return recommendations
