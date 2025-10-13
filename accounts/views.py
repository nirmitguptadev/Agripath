# accounts/views.py
import random
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from twilio.rest import Client
from django.conf import settings
from .forms import PhoneForm, OTPForm, ProfileEditForm # <-- Ensure this import is correct
from .models import Profile

# --- Twilio Client Initialization ---
def get_twilio_client():
    if settings.TWILIO_ACCOUNT_SID and settings.TWILIO_AUTH_TOKEN:
        return Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
    return None

# --- Main Login Flow ---

def request_otp(request):
    if request.method == 'POST':
        form = PhoneForm(request.POST)
        if form.is_valid():
            phone_number = form.cleaned_data['phone_number']
            otp = random.randint(100000, 999999)

            # Store phone number and OTP in session
            request.session['phone_number'] = str(phone_number)
            request.session['otp'] = otp
            print(f"Generated OTP for {phone_number}: {otp}") # For debugging

            # Send OTP via Twilio
            client = get_twilio_client()
            if client:
                try:
                    client.messages.create(
                        body=f'Your AgriPath verification code is: {otp}',
                        from_=settings.TWILIO_PHONE_NUMBER,
                        to=str(phone_number)
                    )
                except Exception as e:
                    print(f"Twilio Error: {e}")
                    # Handle SMS sending failure (e.g., show an error message)

            return redirect('verify_otp')
    else:
        form = PhoneForm()
    return render(request, 'accounts/request_otp.html', {'form': form})


def verify_otp(request):
    phone_number = request.session.get('phone_number')
    session_otp = request.session.get('otp')

    if not phone_number or not session_otp:
        return redirect('request_otp')

    if request.method == 'POST':
        form = OTPForm(request.POST)
        if form.is_valid():
            user_otp = int(form.cleaned_data['otp'])
            if user_otp == session_otp:
                # OTP is correct. Log the user in.
                # Use the phone number as the username.
                user, created = User.objects.get_or_create(username=phone_number)

                if created:
                    # If new user, link profile to the user
                    profile = user.profile
                    profile.phone_number = phone_number
                    profile.save()

                login(request, user)
                # Clear session data
                del request.session['phone_number']
                del request.session['otp']
                return redirect('setup_profile')
            else:
                form.add_error('otp', 'Invalid OTP. Please try again.')
    else:
        form = OTPForm()
    return render(request, 'accounts/verify_otp.html', {'form': form})


@login_required
def setup_profile(request):
    profile = request.user.profile
    
    # Check if the profile is already complete (based on location being set)
    # If the user somehow navigated back here but has a location, redirect them away.
    if profile.location and not request.GET.get('force'):
        return redirect('ai')

    if request.method == 'POST':
        # [MODIFIED] Use the full ProfileEditForm for comprehensive setup
        form = ProfileEditForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('index') 
    else:
        # Pass the full form for the user to complete all details
        form = ProfileEditForm(instance=profile)
        
    return render(request, 'accounts/setup_profile.html', {'form': form})

def custom_logout(request):
    logout(request)
    return redirect('request_otp')

@login_required
def view_profile(request):
    profile = request.user.profile
    
    if request.method == 'POST':
        # Handles form submission for editing profile (including file upload)
        form = ProfileEditForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            # Redirect back to the profile page to see changes
            return redirect('view_profile') 
    else:
        # Handles initial GET request
        form = ProfileEditForm(instance=profile)
        
    # Pass both the profile object (for display) and the form (for editing)
    return render(request, 'accounts/profile_detail.html', {
        'profile': profile,
        'form': form
    })
