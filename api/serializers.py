from rest_framework import serializers
from .models import Product, Order


class ProductSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()
    
    class Meta:
        model = Product
        fields = ['id', 'name', 'category', 'price', 'stock', 'image', 'active', 'created_at', 'updated_at']
    
    def get_image(self, obj):
        """Return full URL for image or None"""
        if obj.image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.image.url)
            return obj.image.url
        return None


class OrderSerializer(serializers.ModelSerializer):
    orderId = serializers.CharField(source='order_id', read_only=True)
    customerName = serializers.CharField(source='customer_name')
    phoneNumber = serializers.CharField(source='phone_number')
    roomNumber = serializers.CharField(source='room_number')
    totalAmount = serializers.DecimalField(source='total_amount', max_digits=10, decimal_places=2, read_only=True)
    createdAt = serializers.DateTimeField(source='created_at', read_only=True)
    expiresAt = serializers.DateTimeField(source='expires_at', read_only=True)
    pickedAt = serializers.DateTimeField(source='picked_at', read_only=True)
    completedAt = serializers.DateTimeField(source='completed_at', read_only=True)
    cancelledAt = serializers.DateTimeField(source='cancelled_at', read_only=True)

    class Meta:
        model = Order
        fields = [
            'orderId', 'customerName', 'phoneNumber', 'roomNumber', 
            'notes', 'items', 'totalAmount', 'status', 
            'createdAt', 'expiresAt', 'pickedAt', 'completedAt', 'cancelledAt'
        ]
        read_only_fields = ['orderId', 'totalAmount', 'status', 'createdAt', 'expiresAt', 'pickedAt', 'completedAt', 'cancelledAt']

    def validate_items(self, value):
        """Validate items structure"""
        if not isinstance(value, list) or len(value) == 0:
            raise serializers.ValidationError("Items must be a non-empty list")
        
        for item in value:
            if not all(key in item for key in ['productId', 'name', 'price', 'qty']):
                raise serializers.ValidationError("Each item must have productId, name, price, and qty")
            
            if item['qty'] <= 0:
                raise serializers.ValidationError("Quantity must be positive")
        
        return value

    def validate_phoneNumber(self, value):
        """Validate phone number"""
        if not value.isdigit() or len(value) != 10:
            raise serializers.ValidationError("Phone number must be exactly 10 digits")
        return value

    def create(self, validated_data):
        """Create order and deduct stock"""
        items = validated_data['items']
        
        # Calculate total amount (ensure values are numeric)
        total_amount = sum(float(item['price']) * int(item['qty']) for item in items)
        validated_data['total_amount'] = total_amount
        
        # Check stock availability
        for item in items:
            try:
                product = Product.objects.get(id=item['productId'])
                if product.stock < int(item['qty']):
                    raise serializers.ValidationError(
                        f"Insufficient stock for {product.name}. Available: {product.stock}"
                    )
            except Product.DoesNotExist:
                raise serializers.ValidationError(f"Product with ID {item['productId']} not found")
        
        # Create order
        order = Order.objects.create(**validated_data)
        
        # Deduct stock
        for item in items:
            product = Product.objects.get(id=item['productId'])
            product.stock -= int(item['qty'])
            product.save()
        
        return order
