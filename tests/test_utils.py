from django.test import TestCase
from unittest.mock import patch, Mock
import requests
from core.views import generate_gemini_response, get_weather_data
from home.views import get_current_weather_data, get_alerts_and_forecast


class GeminiUtilsTest(TestCase):
    @patch('core.views.MODEL')
    def test_generate_gemini_response_success(self, mock_model):
        """Test successful Gemini API response"""
        mock_response = Mock()
        mock_response.text = 'Test response with *special* characters!'
        mock_model.generate_content.return_value = mock_response
        
        result = generate_gemini_response('test prompt')
        # Should remove special characters
        self.assertEqual(result, 'Test response with special characters')
        
    @patch('core.views.MODEL', None)
    def test_generate_gemini_response_no_model(self):
        """Test Gemini response when model not configured"""
        result = generate_gemini_response('test prompt')
        self.assertIn('क्षमा करें', result)
        
    @patch('core.views.MODEL')
    def test_generate_gemini_response_exception(self, mock_model):
        """Test Gemini response with API exception"""
        mock_model.generate_content.side_effect = Exception('API Error')
        
        result = generate_gemini_response('test prompt')
        self.assertIn('क्षमा करें', result)


class WeatherUtilsTest(TestCase):
    @patch('requests.get')
    def test_get_weather_data_success(self, mock_get):
        """Test successful weather API response"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'name': 'Delhi',
            'main': {'temp': 25, 'humidity': 60},
            'weather': [{'description': 'clear sky'}],
            'wind': {'speed': 5}
        }
        mock_get.return_value = mock_response
        
        with patch('core.views.OPENWEATHER_API_KEY', 'test_key'):
            result, error = get_weather_data('Delhi')
            
        self.assertIsNone(error)
        self.assertEqual(result['city'], 'Delhi')
        self.assertEqual(result['temperature'], 25)
        
    @patch('requests.get')
    def test_get_weather_data_city_not_found(self, mock_get):
        """Test weather API with city not found"""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response
        
        with patch('core.views.OPENWEATHER_API_KEY', 'test_key'):
            result, error = get_weather_data('InvalidCity')
            
        self.assertIsNone(result)
        self.assertIn('not found', error)
        
    def test_get_weather_data_no_api_key(self):
        """Test weather API without API key"""
        with patch('core.views.OPENWEATHER_API_KEY', None):
            result, error = get_weather_data('Delhi')
            
        self.assertIsNone(result)
        self.assertIn('not configured', error)
        
    @patch('requests.get')
    def test_get_weather_data_request_exception(self, mock_get):
        """Test weather API with request exception"""
        mock_get.side_effect = requests.exceptions.RequestException('Network error')
        
        with patch('core.views.OPENWEATHER_API_KEY', 'test_key'):
            result, error = get_weather_data('Delhi')
            
        self.assertIsNone(result)
        self.assertIn('Could not connect', error)


class HomeWeatherUtilsTest(TestCase):
    @patch('requests.get')
    def test_get_current_weather_data_success(self, mock_get):
        """Test successful current weather data retrieval"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'coord': {'lat': 28.6139, 'lon': 77.2090},
            'name': 'Delhi',
            'main': {'temp': 25, 'humidity': 60, 'pressure': 1013},
            'weather': [{'description': 'clear sky'}],
            'wind': {'speed': 5},
            'visibility': 10000
        }
        mock_get.return_value = mock_response
        
        with patch('home.views.OPENWEATHER_API_KEY', 'test_key'):
            result, error = get_current_weather_data('Delhi')
            
        self.assertIsNone(error)
        self.assertEqual(result['city'], 'Delhi')
        self.assertEqual(result['lat'], 28.6139)
        self.assertEqual(result['lon'], 77.2090)
        
    @patch('requests.get')
    def test_get_alerts_and_forecast_success(self, mock_get):
        """Test successful forecast data retrieval"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'list': [
                {
                    'dt': 1640995200,
                    'dt_txt': '2022-01-01 12:00:00',
                    'main': {
                        'temp_max': 25,
                        'temp_min': 15,
                        'humidity': 60,
                        'pressure': 1013
                    },
                    'weather': [{'description': 'clear sky', 'icon': '01d'}],
                    'wind': {'speed': 5}
                }
            ]
        }
        mock_get.return_value = mock_response
        
        with patch('home.views.OPENWEATHER_API_KEY', 'test_key'):
            result, error = get_alerts_and_forecast(28.6139, 77.2090)
            
        self.assertIsNone(error)
        self.assertEqual(len(result['forecast']), 1)
        self.assertEqual(result['forecast'][0]['max_temp'], 25)