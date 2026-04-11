from django.contrib import admin
from django.urls import path
from home import views
from home.dashboard_view import dashboard


urlpatterns = [
    path('', dashboard, name='dashboard'),
    path('Policies', views.Policies, name= 'Policies'),
    path('about', views.about, name= 'about'),
    
    path('Weather', views.Weather, name='Weather'),
    path('plant-doctor/', views.plant_doctor, name='plant_doctor'),
    path('Fertilizer',views.Fertilizer,name= 'Fertilizer'),
    path('toggle-persona/', views.toggle_persona, name='toggle_persona'),
    path('api/weather-alerts/', views.api_weather_alerts, name='api_weather_alerts'),
]