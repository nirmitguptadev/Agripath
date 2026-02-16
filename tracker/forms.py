from django import forms
from .models import CropTracker

class CropTrackerForm(forms.ModelForm):
    class Meta:
        model = CropTracker
        fields = [
            'crop', 'crop_name_custom', 'quantity', 'unit', 
            'planting_date', 'growth_phase', 'cost', 'strategy'
        ]
        widgets = {
            'planting_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'crop': forms.Select(attrs={'class': 'form-select'}),
            'growth_phase': forms.Select(attrs={'class': 'form-select'}),
            'unit': forms.TextInput(attrs={'class': 'form-control'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control'}),
            'cost': forms.NumberInput(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'strategy': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'crop_name_custom': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Only if not in list'}),
        }

class CropUpdateForm(forms.ModelForm):
     class Meta:
        model = CropTracker
        fields = [
            'growth_phase', 'cost', 'revenue', 'status', 'strategy', 'harvest_date'
        ]
        widgets = {
            'harvest_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'growth_phase': forms.Select(attrs={'class': 'form-select'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'cost': forms.NumberInput(attrs={'class': 'form-control'}),
            'revenue': forms.NumberInput(attrs={'class': 'form-control'}),
            'strategy': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
