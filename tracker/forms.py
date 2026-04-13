from django import forms
from .models import CropTracker, FinancialEntry, Task

class CropTrackerForm(forms.ModelForm):
    class Meta:
        model = CropTracker
        fields = [
            'crop_name_custom', 'quantity', 'unit', 
            'planting_date', 'growth_phase', 'cost', 'strategy'
        ]
        widgets = {
            'planting_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'growth_phase': forms.Select(attrs={'class': 'form-select'}),
            'unit': forms.TextInput(attrs={'class': 'form-control'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control'}),
            'cost': forms.NumberInput(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'strategy': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'crop_name_custom': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Wheat, Tomato, Sorghum', 'required': True}),
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
        
     def save(self, commit=True):
         instance = super().save(commit=False)
         if 'growth_phase' in self.changed_data:
             from django.utils import timezone
             instance.phase_updated_date = timezone.now().date()
         if commit:
             instance.save()
         return instance

class FinancialEntryForm(forms.ModelForm):
    class Meta:
        model = FinancialEntry
        fields = ['entry_type', 'category', 'amount', 'description']
        widgets = {
            'entry_type': forms.Select(attrs={'class': 'form-select'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control'}),
            'description': forms.TextInput(attrs={'class': 'form-control'}),
        }

class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['title', 'due_date']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'due_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }
