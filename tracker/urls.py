from django.urls import path
from . import views

urlpatterns = [
    path('', views.tracker_dashboard, name='tracker_dashboard'),
    path('add/', views.add_crop, name='add_tracked_crop'),
    path('update/<int:tracker_id>/', views.update_crop, name='update_tracked_crop'),
    path('add-financial/<int:tracker_id>/', views.add_financial_entry, name='add_financial_entry'),
    path('add-task/<int:tracker_id>/', views.add_task, name='add_task'),
    path('toggle-task/<int:task_id>/', views.toggle_task, name='toggle_task'),
]
