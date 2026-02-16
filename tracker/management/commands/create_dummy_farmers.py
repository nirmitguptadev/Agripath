from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from accounts.models import Profile
from tracker.models import CropTracker
from dictionary.models import Crop
from datetime import date, timedelta
from decimal import Decimal

class Command(BaseCommand):
    help = 'Create 5 dummy farmers in Kanpur with realistic crop data'

    def handle(self, *args, **kwargs):
        # Dummy farmers data
        farmers = [
            {'username': 'rajesh_kanpur', 'name': 'Rajesh Kumar', 'age': 45, 'phone': '+919876543210'},
            {'username': 'priya_farmer', 'name': 'Priya Singh', 'age': 38, 'phone': '+919876543211'},
            {'username': 'amit_agri', 'name': 'Amit Verma', 'age': 52, 'phone': '+919876543212'},
            {'username': 'sunita_crops', 'name': 'Sunita Devi', 'age': 41, 'phone': '+919876543213'},
            {'username': 'vikram_farm', 'name': 'Vikram Yadav', 'age': 35, 'phone': '+919876543214'},
        ]

        # Crop data: (crop_name, planting_date_offset, harvest_date_offset, quantity, cost, revenue)
        crop_scenarios = {
            'rajesh_kanpur': [
                ('Wheat', -180, -90, 500, 45000, 72000),
                ('Rice', -270, -180, 400, 38000, 65000),
                ('Sugarcane', -365, -270, 300, 55000, 85000),
            ],
            'priya_farmer': [
                ('Rice', -200, -110, 450, 42000, 68000),
                ('Potato', -150, -90, 350, 28000, 48000),
                ('Wheat', -300, -210, 480, 43000, 70000),
            ],
            'amit_agri': [
                ('Sugarcane', -400, -310, 320, 58000, 92000),
                ('Wheat', -220, -130, 520, 47000, 75000),
                ('Mustard', -160, -80, 280, 22000, 38000),
            ],
            'sunita_crops': [
                ('Potato', -190, -100, 380, 30000, 52000),
                ('Rice', -280, -190, 420, 40000, 66000),
                ('Wheat', -350, -260, 490, 44000, 71000),
            ],
            'vikram_farm': [
                ('Wheat', -240, -150, 510, 46000, 73000),
                ('Mustard', -170, -90, 290, 23000, 39000),
                ('Potato', -320, -230, 360, 29000, 50000),
            ],
        }

        for farmer_data in farmers:
            # Create user
            user, created = User.objects.get_or_create(
                username=farmer_data['username'],
                defaults={'first_name': farmer_data['name'].split()[0]}
            )
            
            if created:
                user.set_password('farmer123')
                user.save()
                self.stdout.write(self.style.SUCCESS(f"Created user: {farmer_data['username']}"))
            
            # Create/update profile
            profile, _ = Profile.objects.get_or_create(user=user)
            profile.name = farmer_data['name']
            profile.age = farmer_data['age']
            profile.phone_number = farmer_data['phone']
            profile.location = 'Kanpur'
            profile.save()
            
            # Create crop tracking records
            for crop_name, plant_offset, harvest_offset, qty, cost, revenue in crop_scenarios[farmer_data['username']]:
                try:
                    crop_obj = Crop.objects.get(name=crop_name)
                except Crop.DoesNotExist:
                    crop_obj = None
                
                planting_date = date.today() + timedelta(days=plant_offset)
                harvest_date = date.today() + timedelta(days=harvest_offset)
                
                CropTracker.objects.get_or_create(
                    user=user,
                    crop=crop_obj,
                    crop_name_custom=crop_name if not crop_obj else '',
                    planting_date=planting_date,
                    defaults={
                        'harvest_date': harvest_date,
                        'quantity': Decimal(qty),
                        'unit': 'kg',
                        'cost': Decimal(cost),
                        'revenue': Decimal(revenue),
                        'status': 'Completed',
                        'growth_phase': 'Maturation',
                    }
                )
            
            self.stdout.write(self.style.SUCCESS(f"Added crops for {farmer_data['name']}"))
        
        self.stdout.write(self.style.SUCCESS('Successfully created 5 dummy farmers in Kanpur with crop data!'))
