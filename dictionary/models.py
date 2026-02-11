from django.db import models

class Crop(models.Model):
    name = models.CharField(max_length=100, unique=True)
    scientific_name = models.CharField(max_length=100)
    overview = models.TextField()
    header_image = models.ImageField(upload_to='crop_headers/', blank=True, null=True)
    wikipedia_url = models.URLField(blank=True, null=True, help_text="Link to Wikipedia article")

    # 1. Botanical & Taxonomical Profile
    family = models.CharField(max_length=100, blank=True, help_text="e.g., Solanaceae")
    varieties = models.TextField(blank=True, help_text="Popular local and global breeds")
    growth_habit = models.CharField(max_length=100, blank=True, help_text="e.g., Annual shrub, Perennial tree")
    pollination = models.CharField(max_length=100, blank=True, help_text="e.g., Self-pollinated, Cross-pollinated")

    # 2. Cultivation & Agronomy
    soil_ph = models.CharField(max_length=50, blank=True, help_text="e.g., 6.0 - 7.0")
    soil_type = models.CharField(max_length=100, blank=True, help_text="e.g., Well-drained loamy soil")
    climatic_req = models.TextField(blank=True, help_text="Temp, Humidity, Rainfall")
    sowing_window = models.CharField(max_length=100, blank=True, help_text="Specific seasons (Kharif/Rabi) and months")
    seed_rate_spacing = models.TextField(blank=True, help_text="Seeds per acre and spacing")
    water_req = models.TextField(blank=True, help_text="Irrigation frequency and critical stages")

    # 3. Nutrient & Soil Health
    fertilizer_schedule = models.TextField(blank=True, help_text="NPK requirements and schedule")
    micronutrients = models.TextField(blank=True, help_text="Deficiency signs and management")
    crop_rotation = models.TextField(blank=True, help_text="Preceding and succeeding crops")

    # 4. Pest & Weed Management
    major_pests = models.TextField(blank=True, help_text="List of major insect pests")
    weed_control = models.TextField(blank=True, help_text="Herbicides and manual weeding")
    ipm_practices = models.TextField(blank=True, help_text="Integrated Pest Management strategies")

    # 5. Harvest & Post-Harvest
    maturity_signs = models.TextField(blank=True, help_text="Physical indicators of maturity")
    harvesting_method = models.TextField(blank=True, help_text="Manual or mechanical details")
    yield_expectations = models.CharField(max_length=100, blank=True, help_text="e.g., 20-25 tonnes/ha")
    storage_req = models.TextField(blank=True, help_text="Temp, humidity, and shelf-life")
    processing_value = models.TextField(blank=True, help_text="Value-added products")

    # Summary Fields (Keep for Cards/Quick Stats)
    sowing_season = models.CharField(max_length=100, help_text="Short season name (e.g. Kharif)")
    harvesting_season = models.CharField(max_length=100)
    growth_duration = models.CharField(max_length=100)
    average_price = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Disease(models.Model):
    crop = models.ForeignKey(Crop, on_delete=models.CASCADE, related_name='diseases')
    name = models.CharField(max_length=100)
    symptoms = models.TextField()
    medicine_protection = models.TextField(help_text="Preventative measures")
    medicine_cure = models.TextField(help_text="Curative medicines")
    image = models.ImageField(upload_to='disease_images/', blank=True, null=True)

    def __str__(self):
        return f"{self.name} ({self.crop.name})"
