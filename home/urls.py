from django.contrib import admin
from django.urls import path
from home import views


urlpatterns = [
    

    path('Policies', views.Policies, name= 'Policies'),
    path('about', views.about, name= 'about'),
    
    path('Weather', views.Weather, name='Weather'),
    path('Fertilizer',views.Fertilizer,name= 'Fertilizer'),
    

    
]