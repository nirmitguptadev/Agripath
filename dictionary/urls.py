from django.urls import path
from .views import CropListView, CropDetailView, populate_database

urlpatterns = [
    path('', CropListView.as_view(), name='crop_list'),
    path('<int:pk>/', CropDetailView.as_view(), name='crop_detail'),
    path('populate-data/', populate_database, name='populate_database'),  # Temporary - remove after use
]
