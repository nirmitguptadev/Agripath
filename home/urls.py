from django.contrib import admin
from django.urls import path
from home import views

urlpatterns = [
    path('', views.index, name= 'Home'),
    path('Bihar', views.Bihar, name= 'Bihar'),
    path('Policies', views.Policies, name= 'Policies'),
    path('about', views.about, name= 'about'),
    path('UttarPradesh',views.Uttar,name= 'Uttar Pradesh'),
    path('Haryana',views.Har,name= 'Haryana'),
    
]