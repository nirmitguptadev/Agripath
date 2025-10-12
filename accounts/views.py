# accounts/views.py
import random
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from twilio.rest import Client
from django.conf import settings
from .forms import PhoneForm, OTPForm, ProfileForm
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
    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('ai') # Redirect to your AI homepage
    else:
        form = ProfileForm(instance=profile)
    return render(request, 'accounts/setup_profile.html', {'form': form})

def custom_logout(request):
    logout(request)
    return redirect('request_otp')

@login_required
def view_profile(request):
    # The @login_required decorator ensures only logged-in users can see this.
    # The user's profile is automatically linked via the one-to-one relationship.
    profile = request.user.profile
    return render(request, 'accounts/profile_detail.html', {'profile': profile})
