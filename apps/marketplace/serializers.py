from rest_framework import serializers
from .models import Product, InputProduct, ProduceProduct, ProductImage, Order, OrderItem, Review

class ProductImageSerializer(serializers.ModelSerializer):
    """Serializer for product images"""
    class Meta:
        model = ProductImage
        fields = ['id', 'image', 'is_primary', 'caption', 'uploaded_at']
        read_only_fields = ['uploaded_at']

class ProductSerializer(serializers.ModelSerializer):
    """Base serializer for products"""
    images = ProductImageSerializer(many=True, read_only=True)
    
    class Meta:
        model = Product
        fields = [
            'id', 'name', 'description', 'product_type', 'category', 
            'subcategory', 'is_active', 'created_at', 'updated_at', 'images'
        ]
        read_only_fields = ['created_at', 'updated_at']

class InputProductSerializer(serializers.ModelSerializer):
    """Serializer for input products"""
    product = ProductSerializer()
    supplier_name = serializers.CharField(source='supplier.username', read_only=True)
    is_in_stock = serializers.BooleanField(read_only=True)
    current_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    
    class Meta:
        model = InputProduct
        fields = [
            'product', 'supplier', 'supplier_name', 'brand', 'manufacturer',
            'price', 'discount_price', 'unit', 'stock_quantity', 'min_order_quantity',
            'usage_instructions', 'safety_information', 'is_in_stock', 'current_price'
        ]
        read_only_fields = ['supplier']
    
    def create(self, validated_data):
        product_data = validated_data.pop('product')
        product_data['product_type'] = 'input'
        
        # Create the product
        product = Product.objects.create(**product_data)
        
        # Set the supplier to the current user
        validated_data['supplier'] = self.context['request'].user
        
        # Create the input product
        input_product = InputProduct.objects.create(product=product, **validated_data)
        return input_product

class ProduceProductSerializer(serializers.ModelSerializer):
    """Serializer for produce products"""
    product = ProductSerializer()
    farmer_name = serializers.CharField(source='farmer.username', read_only=True)
    farm_name = serializers.CharField(source='farm.name', read_only=True)
    crop_name = serializers.CharField(source='crop.name', read_only=True)
    is_available = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = ProduceProduct
        fields = [
            'product', 'farmer', 'farmer_name', 'farm', 'farm_name', 'crop', 'crop_name',
            'variety', 'grade', 'harvest_date', 'price_per_unit', 'available_quantity',
            'unit', 'min_order_quantity', 'available_from', 'available_until',
            'status', 'organic', 'certification', 'is_available'
        ]
        read_only_fields = ['farmer']
    
    def create(self, validated_data):
        product_data = validated_data.pop('product')
        product_data['product_type'] = 'produce'
        
        # Create the product
        product = Product.objects.create(**product_data)
        
        # Set the farmer to the current user
        validated_data['farmer'] = self.context['request'].user
        
        # Create the produce product
        produce_product = ProduceProduct.objects.create(product=product, **validated_data)
        return produce_product

class OrderItemSerializer(serializers.ModelSerializer):
    """Serializer for order items"""
    product_name = serializers.CharField(source='product.name', read_only=True)
    
    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'product_name', 'quantity', 'unit_price', 'total_price']
        read_only_fields = ['total_price']

class OrderSerializer(serializers.ModelSerializer):
    """Serializer for orders"""
    items = OrderItemSerializer(many=True, read_only=True)
    buyer_name = serializers.CharField(source='buyer.username', read_only=True)
    seller_name = serializers.CharField(source='seller.username', read_only=True)
    
    class Meta:
        model = Order
        fields = [
            'id', 'order_number', 'order_type', 'buyer', 'buyer_name', 
            'seller', 'seller_name', 'order_date', 'total_amount',
            'shipping_address', 'shipping_city', 'shipping_state', 
            'shipping_country', 'shipping_phone', 'estimated_delivery_date',
            'actual_delivery_date', 'status', 'payment_status', 
            'payment_method', 'payment_reference', 'buyer_notes',
            'seller_notes', 'created_at', 'updated_at', 'items'
        ]
        read_only_fields = [
            'order_number', 'order_date', 'created_at', 'updated_at',
            'buyer', 'seller'
        ]

class OrderCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating orders"""
    items = serializers.ListField(
        child=serializers.DictField(),
        write_only=True
    )
    
    class Meta:
        model = Order
        fields = [
            'order_type', 'seller', 'total_amount',
            'shipping_address', 'shipping_city', 'shipping_state', 
            'shipping_country', 'shipping_phone', 'estimated_delivery_date',
            'buyer_notes', 'items'
        ]
    
    def create(self, validated_data):
        items_data = validated_data.pop('items')
        
        # Set the buyer to the current user
        validated_data['buyer'] = self.context['request'].user
        
        # Create the order
        order = Order.objects.create(**validated_data)
        
        # Create order items
        for item_data in items_data:
            product_id = item_data.get('product')
            quantity = item_data.get('quantity')
            unit_price = item_data.get('unit_price')
            
            product = Product.objects.get(id=product_id)
            
            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=quantity,
                unit_price=unit_price
            )
        
        return order

class ReviewSerializer(serializers.ModelSerializer):
    """Serializer for product reviews"""
    user_name = serializers.CharField(source='user.username', read_only=True)
    product_name = serializers.CharField(source='product.name', read_only=True)
    
    class Meta:
        model = Review
        fields = [
            'id', 'product', 'product_name', 'user', 'user_name',
            'order_item', 'rating', 'title', 'comment',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at', 'user']
    
    def create(self, validated_data):
        # Set the user to the current user
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)