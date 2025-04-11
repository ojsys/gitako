from django.db import models
from django.core.cache import cache

class SingletonModel(models.Model):
    """Abstract base model for Singleton pattern models."""
    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)
        # Clear the cache after saving
        cache.clear()

    def delete(self, *args, **kwargs):
        pass

    @classmethod
    def load(cls):
        obj, created = cls.objects.get_or_create(pk=1)
        return obj


class SiteSettings(SingletonModel):
    """Site-wide settings for the Gitako application."""
    site_name = models.CharField(max_length=100, default="Gitako")
    site_description = models.TextField(blank=True, null=True)
    
    # Logo and Favicon
    logo = models.ImageField(upload_to='site/logo/', blank=True, null=True)
    favicon = models.ImageField(upload_to='site/favicon/', blank=True, null=True)
    
    # Hero Section
    hero_title = models.CharField(max_length=200, default="Smart Farm Management")
    hero_subtitle = models.TextField(default="Gitako helps you manage your farm operations efficiently, track activities, monitor inventory, and maximize profits with data-driven insights.")
    
    # Contact Information
    contact_email = models.EmailField(blank=True, null=True)
    contact_phone = models.CharField(max_length=20, blank=True, null=True)
    
    # Social Media Links
    facebook_url = models.URLField(blank=True, null=True)
    twitter_url = models.URLField(blank=True, null=True)
    instagram_url = models.URLField(blank=True, null=True)
    linkedin_url = models.URLField(blank=True, null=True)
    
    # Footer Text
    footer_text = models.CharField(max_length=200, default="© Gitako. All rights reserved.")
    
    # Analytics
    google_analytics_id = models.CharField(max_length=50, blank=True, null=True)
    
    # SEO
    meta_keywords = models.TextField(blank=True, null=True)
    meta_description = models.TextField(blank=True, null=True)
    
    # Maintenance Mode
    maintenance_mode = models.BooleanField(default=False)
    maintenance_message = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return "Site Settings"
    
    class Meta:
        verbose_name = "Site Settings"
        verbose_name_plural = "Site Settings"


class HeroSlider(models.Model):
    """Hero slider images for the homepage."""
    title = models.CharField(max_length=200)
    subtitle = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='site/hero_slider/')
    button_text = models.CharField(max_length=50, blank=True, null=True)
    button_url = models.CharField(max_length=200, blank=True, null=True)
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return self.title
    
    class Meta:
        ordering = ['order']
        verbose_name = "Hero Slider"
        verbose_name_plural = "Hero Sliders"


class Feature(models.Model):
    """Features displayed on the homepage."""
    title = models.CharField(max_length=100)
    description = models.TextField()
    icon = models.CharField(max_length=50, help_text="Material icon name (e.g., 'landscape')")
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return self.title
    
    class Meta:
        ordering = ['order']
        verbose_name = "Feature"
        verbose_name_plural = "Features"


class Testimonial(models.Model):
    """Customer testimonials displayed on the homepage."""
    name = models.CharField(max_length=100)
    position = models.CharField(max_length=100)
    image = models.ImageField(upload_to='site/testimonials/')
    content = models.TextField()
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['order']
        verbose_name = "Testimonial"
        verbose_name_plural = "Testimonials"


class Statistic(models.Model):
    """Statistics displayed on the homepage."""
    label = models.CharField(max_length=100)
    value = models.CharField(max_length=50)
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.label}: {self.value}"
    
    class Meta:
        ordering = ['order']
        verbose_name = "Statistic"
        verbose_name_plural = "Statistics"