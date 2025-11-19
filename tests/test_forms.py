from django.test import TestCase
from accounts.forms import PhoneForm, OTPForm, ProfileEditForm
from accounts.models import Profile
from django.contrib.auth.models import User
from phonenumber_field.phonenumber import PhoneNumber


class PhoneFormTest(TestCase):
    def test_valid_phone_number(self):
        """Test valid Indian phone number"""
        form_data = {'phone_number': '+919876543210'}
        form = PhoneForm(data=form_data)
        self.assertTrue(form.is_valid())
        
    def test_invalid_phone_number(self):
        """Test invalid phone number"""
        form_data = {'phone_number': '123'}
        form = PhoneForm(data=form_data)
        self.assertFalse(form.is_valid())
        
    def test_empty_phone_number(self):
        """Test empty phone number"""
        form_data = {'phone_number': ''}
        form = PhoneForm(data=form_data)
        self.assertFalse(form.is_valid())


class OTPFormTest(TestCase):
    def test_valid_otp(self):
        """Test valid 6-digit OTP"""
        form_data = {'otp': '123456'}
        form = OTPForm(data=form_data)
        self.assertTrue(form.is_valid())
        
    def test_long_otp(self):
        """Test OTP with more characters"""
        form_data = {'otp': '1234567'}  # Long OTP (7 chars, max is 6)
        form = OTPForm(data=form_data)
        self.assertFalse(form.is_valid())  # Should fail max_length validation
        
    def test_empty_otp(self):
        """Test empty OTP"""
        form_data = {'otp': ''}
        form = OTPForm(data=form_data)
        self.assertFalse(form.is_valid())


class ProfileEditFormTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='+919876543210')
        self.profile = self.user.profile
        
    def test_valid_profile_form(self):
        """Test valid profile form data"""
        form_data = {
            'name': 'Test User',
            'age': 25,
            'location': 'Delhi'
        }
        form = ProfileEditForm(data=form_data, instance=self.profile)
        self.assertTrue(form.is_valid())
        
    def test_invalid_age(self):
        """Test invalid age (negative)"""
        form_data = {
            'name': 'Test User',
            'age': -5,
            'location': 'Delhi'
        }
        form = ProfileEditForm(data=form_data, instance=self.profile)
        self.assertFalse(form.is_valid())
        
    def test_empty_optional_fields(self):
        """Test form with empty optional fields"""
        form_data = {
            'name': '',
            'age': '',
            'location': ''
        }
        form = ProfileEditForm(data=form_data, instance=self.profile)
        self.assertTrue(form.is_valid())
        
    def test_form_save(self):
        """Test form saves data correctly"""
        form_data = {
            'name': 'Test User',
            'age': 25,
            'location': 'Delhi'
        }
        form = ProfileEditForm(data=form_data, instance=self.profile)
        self.assertTrue(form.is_valid())
        
        saved_profile = form.save()
        self.assertEqual(saved_profile.name, 'Test User')
        self.assertEqual(saved_profile.age, 25)
        self.assertEqual(saved_profile.location, 'Delhi')