# accounts/middleware.py
from django.shortcuts import redirect
from django.urls import reverse

class ProfileCompletionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            # Check if the profile is incomplete (location is missing)
            if not request.user.profile.location:
                # Allow access to the setup page and logout page
                allowed_paths = [reverse('setup_profile'), reverse('logout')]
                if request.path not in allowed_paths:
                    return redirect('setup_profile')

        response = self.get_response(request)
        return response