from django.contrib import admin
from .models import SiteSettings, HeroSlider, Feature, Testimonial, Statistic

@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    fieldsets = (
        ('General', {
            'fields': ('site_name', 'site_description', 'logo', 'favicon')
        }),
        ('Hero Section', {
            'fields': ('hero_title', 'hero_subtitle')
        }),
        ('Contact Information', {
            'fields': ('contact_email', 'contact_phone')
        }),
        ('Social Media', {
            'fields': ('facebook_url', 'twitter_url', 'instagram_url', 'linkedin_url')
        }),
        ('Footer', {
            'fields': ('footer_text',)
        }),
        ('SEO & Analytics', {
            'fields': ('meta_keywords', 'meta_description', 'google_analytics_id')
        }),
        ('Maintenance', {
            'fields': ('maintenance_mode', 'maintenance_message')
        }),
    )
    
    def has_add_permission(self, request):
        # Check if there's already an instance
        return not SiteSettings.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        # Prevent deletion
        return False


@admin.register(HeroSlider)
class HeroSliderAdmin(admin.ModelAdmin):
    list_display = ('title', 'order', 'is_active')
    list_editable = ('order', 'is_active')
    list_filter = ('is_active',)


@admin.register(Feature)
class FeatureAdmin(admin.ModelAdmin):
    list_display = ('title', 'icon', 'order', 'is_active')
    list_editable = ('icon', 'order', 'is_active')
    list_filter = ('is_active',)


@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = ('name', 'position', 'order', 'is_active')
    list_editable = ('order', 'is_active')
    list_filter = ('is_active',)


@admin.register(Statistic)
class StatisticAdmin(admin.ModelAdmin):
    list_display = ('label', 'value', 'order', 'is_active')
    list_editable = ('value', 'order', 'is_active')
    list_filter = ('is_active',)