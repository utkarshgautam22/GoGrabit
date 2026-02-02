from django.db import models
from django.utils import timezone
import random
import string


class Product(models.Model):
    """Product model for inventory management"""
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    category = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.IntegerField(default=0)
    image = models.CharField(max_length=500, blank=True, null=True)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"{self.name} - ₹{self.price}"


class Order(models.Model):
    """Order model with status tracking"""
    STATUS_CHOICES = [
        ('reserved', 'Reserved'),
        ('picked', 'Picked'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    order_id = models.CharField(max_length=4, unique=True, primary_key=True)
    customer_name = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=15)
    room_number = models.CharField(max_length=50)
    notes = models.TextField(blank=True, null=True)
    
    # Items stored as JSON (denormalized for performance)
    items = models.JSONField()
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='reserved')
    
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    picked_at = models.DateTimeField(blank=True, null=True)
    completed_at = models.DateTimeField(blank=True, null=True)
    cancelled_at = models.DateTimeField(blank=True, null=True)
    
    telegram_message_id = models.IntegerField(blank=True, null=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Order {self.order_id} - {self.customer_name}"

    def save(self, *args, **kwargs):
        if not self.order_id:
            # Generate simple order ID: 2 uppercase letters + 2 digits (e.g., AB12)
            while True:
                letters = ''.join(random.choices(string.ascii_uppercase, k=2))
                digits = ''.join(random.choices(string.digits, k=2))
                order_id = f"{letters}{digits}"
                
                # Check if this ID already exists
                if not Order.objects.filter(order_id=order_id).exists():
                    self.order_id = order_id
                    break
        
        if not self.expires_at:
            # Set expiration to 15 minutes from now
            self.expires_at = timezone.now() + timezone.timedelta(minutes=15)
        
        super().save(*args, **kwargs)

    def is_expired(self):
        """Check if order has expired"""
        return timezone.now() > self.expires_at and self.status == 'reserved'

    def cancel(self):
        """Cancel order and restore stock"""
        if self.status in ['cancelled', 'completed']:
            return False
        
        # Restore stock for all items
        for item in self.items:
            try:
                product = Product.objects.get(id=item['productId'])
                product.stock += item['qty']
                product.save()
            except Product.DoesNotExist:
                pass
        
        self.status = 'cancelled'
        self.cancelled_at = timezone.now()
        self.save()
        return True

    def mark_picked(self):
        """Mark order as picked"""
        if self.status != 'reserved':
            return False
        
        self.status = 'picked'
        self.picked_at = timezone.now()
        self.save()
        return True

    def mark_completed(self):
        """Mark order as completed"""
        if self.status not in ['reserved', 'picked']:
            return False
        
        self.status = 'completed'
        self.completed_at = timezone.now()
        self.save()
        return True


class AdminSettings(models.Model):
    """Store admin settings"""
    key = models.CharField(max_length=100, unique=True, primary_key=True)
    value = models.TextField()
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.key}: {self.value}"
