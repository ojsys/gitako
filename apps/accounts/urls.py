from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenVerifyView
from .views import (
    UserViewSet, RegisterView, FarmerListView, 
    SupplierListView, OfftakerListView
)

router = DefaultRouter()
router.register(r'users', UserViewSet)

urlpatterns = [
    path('acc', include(router.urls)),
    path('register/', RegisterView.as_view(), name='register'),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    path('farmers/', FarmerListView.as_view(), name='farmer-list'),
    path('suppliers/', SupplierListView.as_view(), name='supplier-list'),
    path('offtakers/', OfftakerListView.as_view(), name='offtaker-list'),
]