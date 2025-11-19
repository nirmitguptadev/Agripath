from django.test import TestCase, Client
from django.contrib.auth.models import User
from unittest.mock import patch, Mock
import json


class IntegrationTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='+919876543210')
        self.user.profile.name = 'Test User'
        self.user.profile.location = 'Delhi'
        self.user.profile.save()
        
    def test_complete_user_flow(self):
        """Test complete user authentication and profile setup flow"""
        # Test session setup for OTP verification
        session = self.client.session
        session['phone_number'] = '+919876543210'
        session['otp'] = 123456
        session.save()
        
        response = self.client.post('/accounts/login/verify/', {
            'otp': '123456'
        })
        self.assertEqual(response.status_code, 302)
        
    @patch('core.views.MODEL')
    @patch('core.views.get_weather_data')
    def test_ai_chat_integration(self, mock_weather, mock_model):
        """Test complete AI chat integration"""
        self.client.force_login(self.user)
        
        # Mock weather response
        mock_weather.return_value = ({
            'city': 'Delhi',
            'temperature': 25,
            'description': 'clear sky',
            'humidity': 60,
            'wind_speed': 5
        }, None)
        
        # Mock AI responses
        mock_responses = [
            Mock(text='weather'),  # Classification
            Mock(text='Delhi'),    # City extraction
            Mock(text='आज दिल्ली में मौसम साफ है, तापमान 25°C है।')  # Final response
        ]
        mock_model.generate_content.side_effect = mock_responses
        
        # Test weather query
        data = {'text': 'Delhi ka mausam kaisa hai?'}
        response = self.client.post(
            '/process/',
            json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertIn('response', response_data)
        
        # Verify chat history is maintained
        session = self.client.session
        self.assertIn('chat_history', session)
        self.assertEqual(len(session['chat_history']), 2)  # User + AI response
        
    @patch('home.views.get_current_weather_data')
    @patch('home.views.get_alerts_and_forecast')
    def test_weather_page_integration(self, mock_forecast, mock_weather):
        """Test weather page with API integration"""
        self.client.force_login(self.user)
        
        # Mock weather data
        mock_weather.return_value = ({
            'lat': 28.6139, 'lon': 77.2090,
            'city': 'Delhi', 'temperature': 25,
            'description': 'clear sky', 'humidity': 60,
            'pressure': 1013, 'wind_speed': 5, 'visibility': 10000
        }, None)
        
        mock_forecast.return_value = ({
            'forecast': [{
                'date': 1640995200,
                'max_temp': 25, 'min_temp': 15,
                'description': 'clear sky', 'icon': '01d',
                'humidity': 60, 'pressure': 1013, 'wind_speed': 5
            }],
            'alerts': []
        }, None)
        
        response = self.client.get('/home/Weather')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Delhi')
        
    @patch('home.views.POLICY_MODEL')
    def test_policies_page_integration(self, mock_model):
        """Test policies page with AI integration"""
        self.client.force_login(self.user)
        
        mock_response = Mock()
        mock_response.text = '''[
            {
                "name": "प्रधानमंत्री किसान सम्मान निधि",
                "description": "किसानों को आर्थिक सहायता",
                "benefits": "6000 रुपये प्रति वर्ष",
                "link": "https://pmkisan.gov.in"
            }
        ]'''
        mock_model.generate_content.return_value = mock_response
        
        response = self.client.get('/home/Policies')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'प्रधानमंत्री किसान सम्मान निधि')
        
    def test_session_management(self):
        """Test session management across requests"""
        self.client.force_login(self.user)
        
        # Set initial chat history
        session = self.client.session
        session['chat_history'] = [{'role': 'user', 'parts': ['test message']}]
        session.save()
        
        # Verify session persists
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        
        # Clear chat history
        response = self.client.post('/api/clear-chat/')
        self.assertEqual(response.status_code, 200)
        
        # Verify history is cleared
        session = self.client.session
        self.assertNotIn('chat_history', session)
        
    def test_error_handling_integration(self):
        """Test error handling across the application"""
        self.client.force_login(self.user)
        
        # Test invalid JSON in process_voice
        response = self.client.post(
            '/process/',
            'invalid json',
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
        
        # Test missing text in process_voice
        response = self.client.post(
            '/process/',
            json.dumps({}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
        
    def test_middleware_integration(self):
        """Test profile completion middleware"""
        # Create user without complete profile
        incomplete_user = User.objects.create_user(username='+919999999999')
        incomplete_user.profile.location = ''  # Incomplete profile
        incomplete_user.profile.save()
        
        self.client.force_login(incomplete_user)
        
        # Should redirect to profile setup for incomplete profiles
        response = self.client.get('/')
        # Middleware should handle this appropriately