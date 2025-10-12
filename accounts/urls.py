from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.request_otp, name='request_otp'),
    path('login/verify/', views.verify_otp, name='verify_otp'),
    path('profile/setup/', views.setup_profile, name='setup_profile'),
    path('logout/', views.custom_logout, name='logout'),
    path('profile/', views.view_profile, name='view_profile'),
]