from django.urls import path
from .views import CropListView, CropDetailView

urlpatterns = [
    path('', CropListView.as_view(), name='crop_list'),
    path('<int:pk>/', CropDetailView.as_view(), name='crop_detail'),
]
