from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from tracker.models import CropTracker
from dictionary.models import Crop
from datetime import date

User = get_user_model()

class CropTrackerTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password')
        self.client = Client()
        self.client.login(username='testuser', password='password')
        
        self.crop = Crop.objects.create(name='Tomato', scientific_name='Solanum lycopersicum')

    def test_profit_calculation(self):
        tracker = CropTracker.objects.create(
            user=self.user,
            crop=self.crop,
            quantity=10,
            planting_date=date(2023, 1, 1),
            cost=1000,
            revenue=5000,
            status='Completed',
            growth_phase='Harvested'
        )
        self.assertEqual(tracker.profit, 4000)

    def test_dashboard_view(self):
        response = self.client.get('/tracker/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tracker/dashboard.html')

    def test_add_crop_view(self):
        response = self.client.get('/tracker/add/')
        self.assertEqual(response.status_code, 200)
        
        data = {
            'crop': self.crop.id,
            'quantity': 5,
            'unit': 'Acres',
            'planting_date': '2023-05-01',
            'growth_phase': 'Sowing',
            'cost': 500,
            'strategy': 'Test Strategy'
        }
        response = self.client.post('/tracker/add/', data)
        self.assertRedirects(response, '/tracker/')
        self.assertEqual(CropTracker.objects.count(), 1)

    def test_update_crop_view(self):
        tracker = CropTracker.objects.create(
            user=self.user,
            crop=self.crop,
            quantity=10,
            planting_date=date(2023, 1, 1),
            cost=1000
        )
        
        data = {
            'growth_phase': 'Harvested',
            'status': 'Completed',
            'cost': 1200,
            'revenue': 6000,
            'harvest_date': '2023-06-01',
            'strategy': 'Updated Strategy'
        }
        response = self.client.post(f'/tracker/update/{tracker.id}/', data)
        self.assertRedirects(response, '/tracker/')
        
        tracker.refresh_from_db()
        self.assertEqual(tracker.status, 'Completed')
        self.assertEqual(tracker.revenue, 6000)
        self.assertEqual(tracker.cost, 1200)
