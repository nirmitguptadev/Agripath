
import os
import django
import random
from datetime import date, timedelta
from django.conf import settings

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mypage.settings')
django.setup()

from django.contrib.auth.models import User
from dictionary.models import Crop
from tracker.models import CropTracker

def parse_growth_duration(duration_str):
    """
    Parses growth duration string like "120 days" or "90-100 days".
    Returns an integer representing average days.
    """
    try:
        # standard format "120 days" or just "120"
        parts = duration_str.split()
        if not parts:
            return 120
        
        first_part = parts[0]
        if '-' in first_part:
            start, end = map(int, first_part.split('-'))
            return (start + end) // 2
        
        return int(first_part)
    except Exception as e:
        print(f"Error parsing duration '{duration_str}': {e}. Defaulting to 120.")
        return 120

def create_more_dummy_data():
    print("Starting additional dummy data generation...")
    
    # 1. Fetch Users
    users = list(User.objects.all())
    if not users:
        print("No users found.")
        return
    
    print(f"Found {len(users)} users.")
    
    # 2. Fetch Crops
    crops = list(Crop.objects.all())
    if not crops:
        print("No crops found in dictionary.")
        return

    print(f"Found {len(crops)} crops available.")
    
    # Target Progress Percentages potential
    progress_options = [10, 30, 45, 60, 80, 95]
    
    tracker_entries_created = 0
    
    for user in users:
        # Determine location from profile
        user_location = ""
        if hasattr(user, 'profile') and user.profile.location:
             user_location = user.profile.location
        
        # Add 2 more random crops for each user
        # Avoid picking crops they already have active if possible? 
        # For simplicity, just pick 2 random ones.
        
        selected_crops = random.sample(crops, min(len(crops), 2))
        
        for crop in selected_crops:
            target_progress = random.choice(progress_options)
            
            # Calculate planting date
            total_days = parse_growth_duration(crop.growth_duration)
            days_elapsed = int((target_progress / 100.0) * total_days)
            planting_date = date.today() - timedelta(days=days_elapsed)
            
            # Determine growth phase
            if target_progress < 10: phase = 'Sowing'
            elif target_progress < 25: phase = 'Germination'
            elif target_progress < 50: phase = 'Vegetative'
            elif target_progress < 75: phase = 'Flowering'
            elif target_progress < 90: phase = 'Fruiting'
            else: phase = 'Maturation'
            
            tracker = CropTracker.objects.create(
                user=user,
                crop=crop,
                quantity=random.randint(2, 15),
                unit='acre',
                planting_date=planting_date,
                growth_phase=phase,
                status='Active',
                cost=random.randint(2000, 8000),
                revenue=0,
                location=user_location,
                strategy=f"Additional crop entry for testing."
            )
            
            print(f"Created for {user.username} (Loc: {user_location}): {crop.name}, {target_progress}%")
            tracker_entries_created += 1

    print(f"Successfully created {tracker_entries_created} additional tracker entries.")

if __name__ == '__main__':
    create_more_dummy_data()
