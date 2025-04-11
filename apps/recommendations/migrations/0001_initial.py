# Generated by Django 5.2 on 2025-04-10 20:26

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('farms', '__first__'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Recommendation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('recommendation_type', models.CharField(choices=[('crop', 'Crop Recommendation'), ('fertilizer', 'Fertilizer Recommendation'), ('pest_control', 'Pest Control Recommendation'), ('irrigation', 'Irrigation Recommendation'), ('market', 'Market Recommendation'), ('general', 'General Recommendation')], max_length=20)),
                ('title', models.CharField(max_length=255)),
                ('description', models.TextField()),
                ('priority', models.CharField(choices=[('low', 'Low'), ('medium', 'Medium'), ('high', 'High'), ('urgent', 'Urgent')], default='medium', max_length=10)),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('accepted', 'Accepted'), ('rejected', 'Rejected'), ('implemented', 'Implemented')], default='pending', max_length=20)),
                ('valid_from', models.DateField(auto_now_add=True)),
                ('valid_until', models.DateField(blank=True, null=True)),
                ('user_feedback', models.TextField(blank=True)),
                ('user_rating', models.PositiveSmallIntegerField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('crop_cycle', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='recommendations', to='farms.cropcycle')),
                ('farm', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='recommendations', to='farms.farm')),
                ('field', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='recommendations', to='farms.field')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='recommendations', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='CropRecommendation',
            fields=[
                ('recommendation', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to='recommendations.recommendation')),
                ('soil_factors', models.TextField(blank=True)),
                ('climate_factors', models.TextField(blank=True)),
                ('market_factors', models.TextField(blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='FertilizerRecommendation',
            fields=[
                ('recommendation', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to='recommendations.recommendation')),
                ('nitrogen_kg_per_ha', models.DecimalField(blank=True, decimal_places=2, max_digits=8, null=True)),
                ('phosphorus_kg_per_ha', models.DecimalField(blank=True, decimal_places=2, max_digits=8, null=True)),
                ('potassium_kg_per_ha', models.DecimalField(blank=True, decimal_places=2, max_digits=8, null=True)),
                ('recommended_products', models.TextField(blank=True)),
                ('application_timing', models.CharField(blank=True, max_length=255)),
                ('application_method', models.CharField(blank=True, max_length=255)),
                ('soil_test_based', models.BooleanField(default=False)),
                ('crop_requirement_based', models.BooleanField(default=True)),
            ],
        ),
        migrations.CreateModel(
            name='IrrigationRecommendation',
            fields=[
                ('recommendation', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to='recommendations.recommendation')),
                ('water_requirement_mm', models.DecimalField(blank=True, decimal_places=2, max_digits=8, null=True)),
                ('frequency_days', models.PositiveSmallIntegerField(blank=True, null=True)),
                ('recommended_method', models.CharField(blank=True, max_length=100)),
                ('irrigation_duration', models.CharField(blank=True, max_length=100)),
                ('soil_moisture', models.CharField(blank=True, max_length=50)),
                ('weather_forecast', models.TextField(blank=True)),
                ('crop_stage', models.CharField(blank=True, max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='MarketRecommendation',
            fields=[
                ('recommendation', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to='recommendations.recommendation')),
                ('market_trends', models.TextField(blank=True)),
                ('price_forecast', models.TextField(blank=True)),
                ('recommended_timing', models.CharField(blank=True, max_length=255)),
                ('recommended_markets', models.TextField(blank=True)),
                ('potential_buyers', models.TextField(blank=True)),
                ('current_price_range', models.CharField(blank=True, max_length=100)),
                ('expected_price_range', models.CharField(blank=True, max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='PestControlRecommendation',
            fields=[
                ('recommendation', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to='recommendations.recommendation')),
                ('target_pest', models.CharField(max_length=255)),
                ('pest_pressure', models.CharField(blank=True, max_length=50)),
                ('recommended_products', models.TextField(blank=True)),
                ('application_timing', models.CharField(blank=True, max_length=255)),
                ('application_method', models.CharField(blank=True, max_length=255)),
                ('cultural_controls', models.TextField(blank=True)),
                ('biological_controls', models.TextField(blank=True)),
                ('preventive_measures', models.TextField(blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='RecommendedCrop',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('suitability_score', models.DecimalField(decimal_places=2, max_digits=5)),
                ('expected_yield', models.CharField(blank=True, max_length=100)),
                ('expected_profit', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('planting_window_start', models.DateField(blank=True, null=True)),
                ('planting_window_end', models.DateField(blank=True, null=True)),
                ('notes', models.TextField(blank=True)),
                ('crop', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='farms.crop')),
                ('crop_recommendation', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='recommendations.croprecommendation')),
            ],
            options={
                'ordering': ['-suitability_score'],
            },
        ),
        migrations.AddField(
            model_name='croprecommendation',
            name='recommended_crops',
            field=models.ManyToManyField(through='recommendations.RecommendedCrop', to='farms.crop'),
        ),
    ]
