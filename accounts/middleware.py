# accounts/middleware.py
from django.shortcuts import redirect
from django.urls import reverse

class ProfileCompletionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated and not request.user.is_superuser:
            try:
                profile = request.user.profile
            except Exception:
                from accounts.models import Profile
                profile = Profile.objects.create(user=request.user)
            if not profile.location:
                allowed_paths = [reverse('setup_profile'), reverse('logout')]
                if request.path not in allowed_paths and not request.path.startswith('/admin/'):
                    return redirect('setup_profile')

        response = self.get_response(request)
        return response