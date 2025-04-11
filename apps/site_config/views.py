from django.shortcuts import render
from django.views.generic import TemplateView
from .models import SiteSettings, HeroSlider, Feature, Testimonial, Statistic

class HomeView(TemplateView):
    template_name = 'base/home.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Add site settings data to context if not already provided by context processor
        if 'site_settings' not in context:
            try:
                context['site_settings'] = SiteSettings.objects.get(pk=1)
            except SiteSettings.DoesNotExist:
                pass
                
        # Add hero sliders
        context['hero_sliders'] = HeroSlider.objects.filter(is_active=True).order_by('order')
        
        # Add features
        context['features'] = Feature.objects.filter(is_active=True).order_by('order')
        
        # Add testimonials
        context['testimonials'] = Testimonial.objects.filter(is_active=True).order_by('order')
        
        # Add statistics
        context['statistics'] = Statistic.objects.filter(is_active=True).order_by('order')
        
        return context