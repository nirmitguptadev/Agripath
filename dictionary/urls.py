from django.urls import path
from . import views

urlpatterns = [
    path('', views.crop_list, name='crop_list'),
    path('detail/<str:title>/', views.crop_detail, name='crop_detail'),
]
