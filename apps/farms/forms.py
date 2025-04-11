from django import forms
from .models import Farm, Field

class FarmForm(forms.ModelForm):
    class Meta:
        model = Farm
        fields = ['name', 'location', 'size', 'size_unit', 'farm_type', 'description', 'image']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }

class FieldForm(forms.ModelForm):
    class Meta:
        model = Field
        fields = ['name', 'size', 'size_unit', 'soil_type', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }