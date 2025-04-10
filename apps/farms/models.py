from django.db import models
from django.conf import settings

class Farm(models.Model):
    """Model representing a farm"""
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='farms')
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    size_hectares = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Location
    address = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, blank=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    
    # Soil information
    soil_type = models.CharField(max_length=100, blank=True)
    soil_ph = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name

class Field(models.Model):
    """Model representing a field within a farm"""
    farm = models.ForeignKey(Farm, on_delete=models.CASCADE, related_name='fields')
    name = models.CharField(max_length=255)
    size_hectares = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Location
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    
    # Field characteristics
    soil_type = models.CharField(max_length=100, blank=True)
    irrigation_type = models.CharField(max_length=100, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.farm.name} - {self.name}"

class Crop(models.Model):
    """Model representing a crop type"""
    name = models.CharField(max_length=255)
    scientific_name = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)
    growing_season = models.CharField(max_length=100, blank=True)
    average_growing_period_days = models.PositiveIntegerField(null=True, blank=True)
    
    # Growing conditions
    ideal_temperature_min = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    ideal_temperature_max = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    ideal_rainfall_min = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    ideal_rainfall_max = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    ideal_soil_ph_min = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
    ideal_soil_ph_max = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name

class CropVariety(models.Model):
    """Model representing a specific variety of a crop"""
    crop = models.ForeignKey(Crop, on_delete=models.CASCADE, related_name='varieties')
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    
    # Variety characteristics
    maturity_days = models.PositiveIntegerField(null=True, blank=True)
    yield_potential = models.CharField(max_length=100, blank=True)
    disease_resistance = models.TextField(blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.crop.name} - {self.name}"
    
    class Meta:
        verbose_name_plural = "Crop varieties"

class CropCycle(models.Model):
    """Model representing a crop growing cycle in a field"""
    field = models.ForeignKey(Field, on_delete=models.CASCADE, related_name='crop_cycles')
    crop = models.ForeignKey(Crop, on_delete=models.CASCADE, related_name='crop_cycles')
    crop_variety = models.ForeignKey(CropVariety, on_delete=models.SET_NULL, null=True, blank=True, related_name='crop_cycles')
    
    # Cycle dates
    planting_date = models.DateField()
    expected_harvest_date = models.DateField(null=True, blank=True)
    actual_harvest_date = models.DateField(null=True, blank=True)
    
    # Status
    STATUS_CHOICES = [
        ('planned', 'Planned'),
        ('active', 'Active'),
        ('harvested', 'Harvested'),
        ('failed', 'Failed'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='planned')
    
    # Yield information
    expected_yield_kg = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    actual_yield_kg = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    # Notes
    notes = models.TextField(blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.crop.name} at {self.field.name} ({self.planting_date})"
    
    def save(self, *args, **kwargs):
        # Calculate expected harvest date if not provided
        if not self.expected_harvest_date and self.planting_date and self.crop.average_growing_period_days:
            from datetime import timedelta
            self.expected_harvest_date = self.planting_date + timedelta(days=self.crop.average_growing_period_days)
        
        super().save(*args, **kwargs)

class SoilTest(models.Model):
    """Model for soil test results"""
    field = models.ForeignKey(Field, on_delete=models.CASCADE, related_name='soil_tests')
    test_date = models.DateField()
    
    # Test results
    ph = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
    nitrogen_ppm = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    phosphorus_ppm = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    potassium_ppm = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    organic_matter_percentage = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    
    # Additional nutrients
    calcium_ppm = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    magnesium_ppm = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    sulfur_ppm = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    zinc_ppm = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    manganese_ppm = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    iron_ppm = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    copper_ppm = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    boron_ppm = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    
    # Physical properties
    texture = models.CharField(max_length=100, blank=True)  # sandy, loamy, clay, etc.
    cec = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)  # Cation Exchange Capacity
    
    # Test information
    laboratory = models.CharField(max_length=255, blank=True)
    test_method = models.CharField(max_length=255, blank=True)
    notes = models.TextField(blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Soil Test for {self.field.name} on {self.test_date}"
    
    class Meta:
        ordering = ['-test_date']

class WeatherRecord(models.Model):
    """Model for weather data records"""
    farm = models.ForeignKey(Farm, on_delete=models.CASCADE, related_name='weather_records')
    date = models.DateField()
    
    # Temperature
    temperature_max = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    temperature_min = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    temperature_avg = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    
    # Precipitation
    rainfall_mm = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    
    # Other weather data
    humidity_percentage = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    wind_speed_kmh = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    wind_direction = models.CharField(max_length=50, blank=True)
    
    # Source of data
    SOURCE_CHOICES = [
        ('manual', 'Manual Entry'),
        ('weather_station', 'Weather Station'),
        ('api', 'Weather API'),
    ]
    data_source = models.CharField(max_length=20, choices=SOURCE_CHOICES, default='api')
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Weather for {self.farm.name} on {self.date}"
    
    class Meta:
        ordering = ['-date']
        unique_together = ['farm', 'date']