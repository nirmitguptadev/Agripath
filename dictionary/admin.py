from django.contrib import admin
from .models import Crop, Disease

class DiseaseInline(admin.StackedInline):
    model = Disease
    extra = 1

@admin.register(Crop)
class CropAdmin(admin.ModelAdmin):
    list_display = ('name', 'scientific_name', 'sowing_season', 'average_price')
    search_fields = ('name', 'scientific_name')
    inlines = [DiseaseInline]

@admin.register(Disease)
class DiseaseAdmin(admin.ModelAdmin):
    list_display = ('name', 'crop', 'symptoms')
    search_fields = ('name', 'crop__name')
    list_filter = ('crop',)
