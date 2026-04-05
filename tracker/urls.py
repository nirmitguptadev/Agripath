from django.urls import path
from . import views

urlpatterns = [
    path('', views.tracker_dashboard, name='tracker_dashboard'),
    path('add/', views.add_crop, name='add_tracked_crop'),
    path('update/<int:tracker_id>/', views.update_crop, name='update_tracked_crop'),
    path('edit/<int:tracker_id>/', views.update_crop_details, name='edit_crop_details'),
    
    # Quick Actions
    path('log-activity/<int:tracker_id>/', views.add_quick_log, name='add_quick_log'),
    path('update-health/<int:tracker_id>/', views.update_health, name='update_health'),
    path('harvest/<int:tracker_id>/', views.harvest_crop, name='harvest_crop'),
    
    path('add-task/', views.add_task, name='add_task'),
    path('add-suggested-task/', views.add_suggested_task, name='add_suggested_task'),
    path('toggle-task/<int:task_id>/', views.toggle_task, name='toggle_task'),
    path('add-financial/', views.add_financial_entry, name='add_financial_entry'),
    path('check-custom-crop/', views.check_custom_crop, name='check_custom_crop'),
]
