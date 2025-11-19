from django.test import TestCase
from django.contrib.auth.models import User
from accounts.models import Profile
from phonenumber_field.phonenumber import PhoneNumber


class ProfileModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='+919876543210')
        
    def test_profile_creation(self):
        """Test profile is automatically created when user is created"""
        self.assertTrue(hasattr(self.user, 'profile'))
        self.assertIsInstance(self.user.profile, Profile)
        
    def test_profile_str_method(self):
        """Test profile string representation"""
        self.assertEqual(str(self.user.profile), '+919876543210')
        
    def test_profile_fields(self):
        """Test profile field defaults and updates"""
        profile = self.user.profile
        
        # Test defaults
        self.assertEqual(profile.name, '')
        self.assertIsNone(profile.age)
        self.assertEqual(profile.location, '')
        
        # Test updates
        profile.name = 'Test User'
        profile.age = 25
        profile.location = 'Delhi'
        profile.phone_number = PhoneNumber.from_string('+919876543210', region='IN')
        profile.save()
        
        profile.refresh_from_db()
        self.assertEqual(profile.name, 'Test User')
        self.assertEqual(profile.age, 25)
        self.assertEqual(profile.location, 'Delhi')
        self.assertEqual(str(profile.phone_number), '+919876543210')