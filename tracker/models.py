from django.db import models
from django.contrib.auth.models import User
from dictionary.models import Crop
from datetime import date

class CropTracker(models.Model):
    GROWTH_PHASES = [
        ('Sowing', 'Sowing'),
        ('Germination', 'Germination'),
        ('Vegetative', 'Vegetative'),
        ('Flowering', 'Flowering'),
        ('Fruiting', 'Fruiting'),
        ('Maturation', 'Maturation'),
    ]
    
    STATUS_CHOICES = [
        ('Active', 'Active'),
        ('Completed', 'Completed'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tracked_crops')
    crop = models.ForeignKey(Crop, on_delete=models.SET_NULL, null=True, blank=True)
    crop_name_custom = models.CharField(max_length=100, blank=True, default='', help_text="Custom crop name if not in dictionary")
    
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    unit = models.CharField(max_length=50, default='kg')
    
    planting_date = models.DateField()
    harvest_date = models.DateField(null=True, blank=True)
    
    growth_phase = models.CharField(max_length=50, choices=GROWTH_PHASES, default='Sowing')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Active')
    
    cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    revenue = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Snapshot of location where this crop was grown (fixes issue when user moves)
    location = models.CharField(max_length=100, blank=True)
    
    # Field Mapping Coordinates and Acreage (Phase 2 Pro Feature)
    field_polygon = models.TextField(blank=True, help_text="GeoJSON or coordinate string for the field map")
    field_area_acres = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    strategy = models.TextField(blank=True, help_text="Notes or strategy for this crop")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-planting_date']
    
    def __str__(self):
        return f"{self.display_name} - {self.user.username}"
    
    @property
    def display_name(self):
        return self.crop.name if self.crop else self.crop_name_custom
    
    @property
    def profit(self):
        return float(self.revenue - self.cost)
    
    @property
    def days_elapsed(self):
        if self.status == 'Completed' and self.harvest_date:
            return max(0, (self.harvest_date - self.planting_date).days)
        return max(0, (date.today() - self.planting_date).days)
    
    @property
    def total_days(self):
        if self.crop and self.crop.growth_duration:
            try:
                return int(self.crop.growth_duration.split()[0])
            except:
                return 120
        return 120
    
    @property
    def progress_percent(self):
        if self.total_days > 0:
            return min(max(0, (self.days_elapsed / self.total_days) * 100), 100)
        return 0

class FinancialEntry(models.Model):
    ENTRY_TYPES = [
        ('Expense', 'Expense'),
        ('Revenue', 'Revenue'),
    ]
    
    CATEGORIES = [
        ('Seed', 'Seed'),
        ('Fertilizer', 'Fertilizer'),
        ('Pesticide', 'Pesticide'),
        ('Labor', 'Labor'),
        ('Equipment', 'Equipment'),
        ('Harvest/Sale', 'Harvest/Sale'),
        ('Other', 'Other'),
    ]
    
    crop_tracker = models.ForeignKey(CropTracker, related_name='financials', on_delete=models.CASCADE)
    entry_type = models.CharField(max_length=20, choices=ENTRY_TYPES)
    category = models.CharField(max_length=50, choices=CATEGORIES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField(auto_now_add=True)
    description = models.CharField(max_length=255, blank=True)
    
    class Meta:
        ordering = ['-date']
        
    def __str__(self):
        return f"{self.entry_type} - {self.category} : ₹{self.amount}"

class Task(models.Model):
    crop_tracker = models.ForeignKey(CropTracker, related_name='tasks', on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    due_date = models.DateField()
    is_completed = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['due_date']
        
    def __str__(self):
        return f"{self.title} - {'Done' if self.is_completed else 'Pending'}"
