from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from unittest.mock import patch, Mock
import json


class CoreViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='+919876543210')
        self.user.profile.location = 'Delhi'
        self.user.profile.save()
        
    def test_assistant_page_requires_login(self):
        """Test assistant page redirects unauthenticated users"""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 302)
        
    def test_assistant_page_authenticated(self):
        """Test assistant page loads for authenticated users"""
        self.client.force_login(self.user)
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        
    @patch('core.views.MODEL')
    def test_get_greeting(self, mock_model):
        """Test greeting API endpoint"""
        mock_response = Mock()
        mock_response.text = 'नमस्ते! मैं आपकी मदद के लिए तैयार हूँ।'
        mock_model.generate_content.return_value = mock_response
        
        response = self.client.get('/api/get-greeting/')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertIn('greeting', data)
        
    def test_clear_chat(self):
        """Test chat history clearing"""
        session = self.client.session
        session['chat_history'] = [{'role': 'user', 'parts': ['test']}]
        session.save()
        
        response = self.client.post('/api/clear-chat/')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data['status'], 'success')
        
    @patch('core.views.MODEL')
    @patch('core.views.get_weather_data')
    def test_process_voice_weather_query(self, mock_weather, mock_model):
        """Test weather query processing"""
        self.client.force_login(self.user)
        
        # Mock weather data
        mock_weather.return_value = ({
            'city': 'Delhi',
            'temperature': 25,
            'description': 'clear sky',
            'humidity': 60,
            'wind_speed': 5
        }, None)
        
        # Mock AI responses
        mock_response = Mock()
        mock_response.text = 'weather'
        mock_model.generate_content.return_value = mock_response
        
        data = {'text': 'Delhi ka mausam kaisa hai?'}
        response = self.client.post(
            '/process/',
            json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertIn('response', response_data)


class AccountsViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        
    def test_request_otp_get(self):
        """Test OTP request page loads"""
        response = self.client.get('/accounts/login/')
        self.assertEqual(response.status_code, 200)
        
    @patch('accounts.views.get_twilio_client')
    def test_request_otp_post_valid(self, mock_twilio):
        """Test valid OTP request"""
        mock_client = Mock()
        mock_twilio.return_value = mock_client
        
        data = {'phone_number': '+919876543210'}
        response = self.client.post('/accounts/login/', data)
        self.assertEqual(response.status_code, 302)
        self.assertIn('phone_number', self.client.session)
        self.assertIn('otp', self.client.session)
        
    def test_verify_otp_without_session(self):
        """Test OTP verification without session data"""
        response = self.client.get('/accounts/login/verify/')
        self.assertEqual(response.status_code, 302)
        
    def test_verify_otp_valid(self):
        """Test valid OTP verification"""
        session = self.client.session
        session['phone_number'] = '+919876543210'
        session['otp'] = 123456
        session.save()
        
        data = {'otp': '123456'}
        response = self.client.post('/accounts/login/verify/', data)
        self.assertEqual(response.status_code, 302)
        
    def test_setup_profile_requires_login(self):
        """Test profile setup requires authentication"""
        response = self.client.get('/accounts/profile/setup/')
        self.assertEqual(response.status_code, 302)
        
    def test_view_profile_requires_login(self):
        """Test profile view requires authentication"""
        response = self.client.get('/accounts/profile/')
        self.assertEqual(response.status_code, 302)


class HomeViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='+919876543210')
        self.user.profile.location = 'Delhi'
        self.user.profile.save()
        
    def test_weather_requires_login(self):
        """Test weather page requires authentication"""
        response = self.client.get('/home/Weather')
        self.assertEqual(response.status_code, 302)
        
    @patch('home.views.get_current_weather_data')
    @patch('home.views.get_alerts_and_forecast')
    def test_weather_with_location(self, mock_forecast, mock_weather):
        """Test weather page with user location"""
        self.client.force_login(self.user)
        
        mock_weather.return_value = ({
            'lat': 28.6139, 'lon': 77.2090,
            'city': 'Delhi', 'temperature': 25,
            'description': 'clear sky', 'humidity': 60
        }, None)
        
        mock_forecast.return_value = ({'forecast': [], 'alerts': []}, None)
        
        response = self.client.get('/home/Weather')
        self.assertEqual(response.status_code, 200)
        
    def test_policies_requires_login(self):
        """Test policies page requires authentication"""
        response = self.client.get('/home/Policies')
        self.assertEqual(response.status_code, 302)
        
    @patch('home.views.POLICY_MODEL')
    def test_policies_with_location(self, mock_model):
        """Test policies page with user location"""
        self.client.force_login(self.user)
        
        mock_response = Mock()
        mock_response.text = '[{"name": "Test Scheme", "description": "Test", "benefits": "Test", "link": "http://test.gov.in"}]'
        mock_model.generate_content.return_value = mock_response
        
        response = self.client.get('/home/Policies')
        self.assertEqual(response.status_code, 200)