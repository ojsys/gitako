from rest_framework import viewsets, permissions, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q
from .models import Product, InputProduct, ProduceProduct, ProductImage, Order, OrderItem, Review
from .serializers import (
    ProductSerializer, InputProductSerializer, ProduceProductSerializer,
    ProductImageSerializer, OrderSerializer, OrderCreateSerializer,
    OrderItemSerializer, ReviewSerializer
)

class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write permissions are only allowed to the owner
        if hasattr(obj, 'supplier'):
            return obj.supplier == request.user
        elif hasattr(obj, 'farmer'):
            return obj.farmer == request.user
        elif hasattr(obj, 'user'):
            return obj.user == request.user
        
        return False

class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for Product model (read-only)"""
    queryset = Product.objects.filter(is_active=True)
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['product_type', 'category', 'subcategory']
    search_fields = ['name', 'description', 'category', 'subcategory']
    ordering_fields = ['name', 'created_at']

class InputProductViewSet(viewsets.ModelViewSet):
    """ViewSet for InputProduct model"""
    serializer_class = InputProductSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['product__category', 'brand', 'manufacturer']
    search_fields = ['product__name', 'product__description', 'brand', 'manufacturer']
    ordering_fields = ['price', 'stock_quantity', 'product__created_at']
    
    def get_queryset(self):
        """
        Return all active input products.
        If user is a supplier, also include their inactive products.
        """
        queryset = InputProduct.objects.filter(product__is_active=True)
        
        # If user is a supplier, include their inactive products
        if self.request.user.user_type == 'supplier':
            supplier_products = InputProduct.objects.filter(supplier=self.request.user, product__is_active=False)
            queryset = queryset | supplier_products
        
        return queryset
    
    @action(detail=False, methods=['get'])
    def my_products(self, request):
        """Get all input products for the current supplier"""
        if request.user.user_type != 'supplier':
            return Response(
                {"detail": "Only suppliers can access this endpoint."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        queryset = InputProduct.objects.filter(supplier=request.user)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def upload_image(self, request, pk=None):
        """Upload an image for an input product"""
        input_product = self.get_object()
        
        if 'image' not in request.FILES:
            return Response(
                {'image': ['No image provided.']},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if this is the first image (make it primary)
        is_primary = not ProductImage.objects.filter(product=input_product.product).exists()
        
        # Create the product image
        image = ProductImage.objects.create(
            product=input_product.product,
            image=request.FILES['image'],
            is_primary=is_primary,
            caption=request.data.get('caption', '')
        )
        
        serializer = ProductImageSerializer(image)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class ProduceProductViewSet(viewsets.ModelViewSet):
    """ViewSet for ProduceProduct model"""
    serializer_class = ProduceProductSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['product__category', 'crop', 'status', 'organic']
    search_fields = ['product__name', 'product__description', 'variety', 'grade']
    ordering_fields = ['price_per_unit', 'available_quantity', 'available_from']
    
    def get_queryset(self):
        """
        Return all active and available produce products.
        If user is a farmer, also include their inactive/unavailable products.
        """
        queryset = ProduceProduct.objects.filter(
            product__is_active=True,
            status='available'
        )
        
        # If user is a farmer, include their inactive/unavailable products
        if self.request.user.user_type == 'farmer':
            farmer_products = ProduceProduct.objects.filter(
                farmer=self.request.user
            ).exclude(
                product__is_active=True,
                status='available'
            )
            queryset = queryset | farmer_products
        
        return queryset
    
    @action(detail=False, methods=['get'])
    def my_products(self, request):
        """Get all produce products for the current farmer"""
        if request.user.user_type != 'farmer':
            return Response(
                {"detail": "Only farmers can access this endpoint."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        queryset = ProduceProduct.objects.filter(farmer=request.user)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def upload_image(self, request, pk=None):
        """Upload an image for a produce product"""
        produce_product = self.get_object()
        
        if 'image' not in request.FILES:
            return Response(
                {'image': ['No image provided.']},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if this is the first image (make it primary)
        is_primary = not ProductImage.objects.filter(product=produce_product.product).exists()
        
        # Create the product image
        image = ProductImage.objects.create(
            product=produce_product.product,
            image=request.FILES['image'],
            is_primary=is_primary,
            caption=request.data.get('caption', '')
        )
        
        serializer = ProductImageSerializer(image)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class OrderViewSet(viewsets.ModelViewSet):
    """ViewSet for Order model"""
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['order_type', 'status', 'payment_status']
    search_fields = ['order_number', 'buyer_notes', 'seller_notes']
    ordering_fields = ['order_date', 'total_amount', 'created_at']
    
    def get_serializer_class(self):
        if self.action == 'create':
            return OrderCreateSerializer
        return OrderSerializer
    
    def get_queryset(self):
        """
        Return orders where the user is either the buyer or seller.
        """
        user = self.request.user
        return Order.objects.filter(Q(buyer=user) | Q(seller=user))
    
    @action(detail=False, methods=['get'])
    def as_buyer(self, request):
        """Get all orders where the user is the buyer"""
        queryset = Order.objects.filter(buyer=request.user)
        serializer = OrderSerializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def as_seller(self, request):
        """Get all orders where the user is the seller"""
        queryset = Order.objects.filter(seller=request.user)
        serializer = OrderSerializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def update_status(self, request, pk=None):
        """Update the status of an order"""
        order = self.get_object()
        
        # Check if the user is the seller
        if order.seller != request.user:
            return Response(
                {"detail": "Only the seller can update the order status."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Update the status
        status_value = request.data.get('status')
        if not status_value:
            return Response(
                {"status": ["This field is required."]},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        order.status = status_value
        order.save()
        
        serializer = OrderSerializer(order)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def update_payment(self, request, pk=None):
        """Update the payment status of an order"""
        order = self.get_object()
        
        # Check if the user is the seller
        if order.seller != request.user:
            return Response(
                {"detail": "Only the seller can update the payment status."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Update the payment status
        payment_status = request.data.get('payment_status')
        if not payment_status:
            return Response(
                {"payment_status": ["This field is required."]},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        order.payment_status = payment_status
        order.payment_method = request.data.get('payment_method', order.payment_method)
        order.payment_reference = request.data.get('payment_reference', order.payment_reference)
        order.save()
        
        serializer = OrderSerializer(order)
        return Response(serializer.data)

class ReviewViewSet(viewsets.ModelViewSet):
    """ViewSet for Review model"""
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['product', 'rating']
    search_fields = ['title', 'comment']
    ordering_fields = ['rating', 'created_at']
    
    def get_queryset(self):
        return Review.objects.all()
    
    @action(detail=False, methods=['get'])
    def my_reviews(self, request):
        """Get all reviews written by the current user"""
        queryset = Review.objects.filter(user=request.user)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
