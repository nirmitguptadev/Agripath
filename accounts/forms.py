# accounts/forms.py
from django import forms
from phonenumber_field.formfields import PhoneNumberField
from .models import Profile

class PhoneForm(forms.Form):
    phone_number = PhoneNumberField(region="IN", label="Mobile Number") # Set region for placeholder

class OTPForm(forms.Form):
    otp = forms.CharField(max_length=6, label="OTP")

class ProfileEditForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['profile_picture', 'name', 'age', 'location']
        labels = {
            'profile_picture': 'Profile Picture',
            'name': 'Full Name',
            'age': 'Age',
            'location': 'Your City or District',
        }