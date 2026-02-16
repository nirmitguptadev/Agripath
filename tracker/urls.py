from django.urls import path
from . import views

urlpatterns = [
    path('', views.tracker_dashboard, name='tracker_dashboard'),
    path('add/', views.add_crop, name='add_tracked_crop'),
    path('update/<int:tracker_id>/', views.update_crop, name='update_tracked_crop'),
]
