from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from apps.accounts.models import User
from .models import Farm, Field, Crop, CropCycle

class FarmAPITestCase(TestCase):
    """Test case for Farm API endpoints"""
    
    def setUp(self):
        """Set up test data"""
        # Create a test user
        self.user = User.objects.create_user(
            username='testfarmer',
            email='farmer@test.com',
            password='testpass123',
            user_type='farmer'
        )
        
        # Create a test farm
        self.farm = Farm.objects.create(
            name='Test Farm',
            owner=self.user,
            farm_type='crop',
            size=10.5,
            size_unit='hectare',
            location='Test Location',
            city='Test City',
            state='Test State',
            country='Test Country'
        )
        
        # Create a test field
        self.field = Field.objects.create(
            farm=self.farm,
            name='Test Field',
            size=5.0,
            size_unit='hectare',
            soil_type='loam',
            is_irrigated=True
        )
        
        # Create a test crop
        self.crop = Crop.objects.create(
            name='Test Crop',
            crop_type='grain',
            growing_season='summer',
            days_to_maturity=90
        )
        
        # Set up the API client
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        
        # URLs
        self.farms_url = reverse('farm-list')
        self.farm_detail_url = reverse('farm-detail', args=[self.farm.id])
        self.fields_url = reverse('field-list')
        self.crops_url = reverse('crop-list')
    
    def test_get_farms_list(self):
        """Test retrieving a list of farms"""
        response = self.client.get(self.farms_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['name'], 'Test Farm')
    
    def test_create_farm(self):
        """Test creating a new farm"""
        data = {
            'name': 'New Test Farm',
            'farm_type': 'livestock',
            'size': 20.0,
            'size_unit': 'acre',
            'location': 'New Location',
            'city': 'New City',
            'state': 'New State',
            'country': 'New Country'
        }
        response = self.client.post(self.farms_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Farm.objects.count(), 2)
        self.assertEqual(Farm.objects.get(name='New Test Farm').owner, self.user)
    
    def test_get_farm_detail(self):
        """Test retrieving a farm detail"""
        response = self.client.get(self.farm_detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Test Farm')
        self.assertEqual(response.data['farm_type'], 'crop')
    
    def test_update_farm(self):
        """Test updating a farm"""
        data = {'name': 'Updated Farm Name'}
        response = self.client.patch(self.farm_detail_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.farm.refresh_from_db()
        self.assertEqual(self.farm.name, 'Updated Farm Name')
    
    def test_delete_farm(self):
        """Test deleting a farm"""
        response = self.client.delete(self.farm_detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Farm.objects.count(), 0)
    
    def test_create_field(self):
        """Test creating a new field"""
        data = {
            'farm': self.farm.id,
            'name': 'New Field',
            'size': 3.5,
            'size_unit': 'hectare',
            'soil_type': 'clay',
            'is_irrigated': False
        }
        response = self.client.post(self.fields_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Field.objects.count(), 2)
        self.assertEqual(Field.objects.get(name='New Field').farm, self.farm)