# accounts/forms.py
from django import forms
from phonenumber_field.formfields import PhoneNumberField
from .models import Profile

class PhoneForm(forms.Form):
    phone_number = PhoneNumberField(region="IN", label="Mobile Number") # Set region for placeholder

class OTPForm(forms.Form):
    otp = forms.CharField(max_length=6, label="OTP")

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['location']
        labels = {
            'location': 'Your City or District'
        }