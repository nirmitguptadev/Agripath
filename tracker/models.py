from django.db import models
from django.contrib.auth.models import User
from dictionary.models import Crop
from datetime import date, timedelta

# Average days from sowing to harvest for common crops.
# Used as fallback when no crop FK with growth_duration is set.
CROP_GROW_DAYS = {
    # Cereals
    'Wheat': 120, 'Rice': 130, 'Paddy': 130, 'Maize': 90, 'Bajra': 85,
    'Jowar': 110, 'Ragi': 120, 'Barley': 110,
    # Pulses
    'Gram': 100, 'Moong': 65, 'Urad': 75, 'Masoor': 110, 'Masur': 110,
    'Arhar': 160, 'Tur': 160, 'Rajma': 90, 'Moth': 80, 'Horse Gram': 90,
    # Oilseeds
    'Mustard': 110, 'Soyabean': 100, 'Groundnut': 120, 'Sunflower': 90,
    'Sesame': 80, 'Castor Seed': 150, 'Linseed': 120, 'Niger Seed': 90,
    'Safflower': 120, 'Cotton': 180,
    # Vegetables
    'Tomato': 75, 'Onion': 120, 'Potato': 90, 'Brinjal': 70,
    'Cauliflower': 75, 'Cabbage': 80, 'Capsicum': 75, 'Bhindi': 55,
    'Cucumber': 55, 'Peas': 70, 'Carrot': 80, 'Radish': 40,
    'Beet Root': 70, 'Spinach': 40, 'Methi': 30, 'Drumstick': 180,
    'Cluster Beans': 60, 'Bottle Gourd': 60, 'Bitter Gourd': 60,
    # Spices
    'Turmeric': 270, 'Garlic': 150, 'Ginger': 240, 'Chilli': 90,
    'Coriander': 45, 'Dill': 50,
    # Fruits
    'Banana': 300, 'Mango': 365, 'Guava': 180, 'Orange': 365,
    'Papaya': 210, 'Grapes': 180, 'Pomegranate': 180, 'Apple': 180,
    'Watermelon': 80, 'Muskmelon': 75, 'Coconut': 365, 'Arecanut': 365,
    # Cash Crops
    'Sugarcane': 330, 'Sugarcane Jaggery': 330,
}

# Minimum progress % implied by each growth phase (acts as a floor).
PHASE_FLOOR = {
    'Sowing': 0, 'Germination': 10, 'Vegetative': 25,
    'Flowering': 50, 'Fruiting': 65, 'Maturation': 85,
}


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

    health = models.CharField(
        max_length=20,
        choices=[('Healthy', 'Healthy'), ('Attention', 'Attention'), ('At Risk', 'At Risk')],
        default='Healthy'
    )
    emoji = models.CharField(max_length=10, default='🌿', help_text="Emoji for visual identification")

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
        # 1. Prefer FK crop's growth_duration
        if self.crop and self.crop.growth_duration:
            try:
                return int(self.crop.growth_duration.split()[0])
            except:
                pass
        # 2. Static lookup by custom name
        name = self.crop_name_custom.strip().title()
        return CROP_GROW_DAYS.get(name, 120)

    @property
    def progress_percent(self):
        if self.total_days > 0:
            time_pct = min(100, max(0, (self.days_elapsed / self.total_days) * 100))
        else:
            time_pct = 0
        # Phase acts as a floor — manual override can only push progress forward
        phase_floor = PHASE_FLOOR.get(self.growth_phase, 0)
        return max(time_pct, phase_floor)

    @property
    def days_remaining(self):
        phase_floor = PHASE_FLOOR.get(self.growth_phase, 0)
        time_pct = min(100, max(0, (self.days_elapsed / self.total_days) * 100)) if self.total_days > 0 else 0
        effective_pct = max(time_pct, phase_floor)
        return max(0, int(self.total_days * (1 - effective_pct / 100)))

    @property
    def days_since_last_log(self):
        last = self.logs.order_by('-date').first()
        if not last:
            # No logs at all — use days since planting, capped at 5
            return min(5, (date.today() - self.planting_date).days)
        from django.utils import timezone
        now = timezone.now()
        return (now - last.date).days

    def auto_update_health(self):
        """Degrade health based on inactivity. Never auto-upgrade (farmer must do that manually)."""
        days = self.days_since_last_log
        new_health = self.health
        if days >= 5:
            new_health = 'At Risk'
        elif days >= 2:
            new_health = 'Attention'
        # Only save if degrading, never auto-upgrade
        RANK = {'Healthy': 0, 'Attention': 1, 'At Risk': 2}
        if RANK.get(new_health, 0) > RANK.get(self.health, 0):
            self.health = new_health
            self.save(update_fields=['health'])


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

    @property
    def is_overdue(self):
        return not self.is_completed and self.due_date < date.today()

    @property
    def due_date_label(self):
        delta = (self.due_date - date.today()).days
        if delta == 0:
            return "Today"
        elif delta == 1:
            return "Tomorrow"
        elif delta == -1:
            return "Yesterday"
        elif delta > 1:
            return f"In {delta} days"
        else:
            return f"{abs(delta)} days ago"


class ActivityLog(models.Model):
    crop_tracker = models.ForeignKey(CropTracker, related_name='logs', on_delete=models.CASCADE)
    activity_type = models.CharField(max_length=50)
    details = models.CharField(max_length=255, blank=True)
    date = models.DateTimeField(auto_now_add=True)  # DateTimeField for accurate timesince

    class Meta:
        ordering = ['-date', '-id']

    def __str__(self):
        return f"{self.activity_type} on {self.date}"
