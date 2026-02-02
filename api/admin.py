from django.contrib import admin
from .models import Product, Order, AdminSettings


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'category', 'price', 'stock', 'active', 'created_at']
    list_filter = ['category', 'active']
    search_fields = ['name', 'category']
    list_editable = ['stock', 'active']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_id', 'customer_name', 'phone_number', 'total_amount', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['order_id', 'customer_name', 'phone_number']
    readonly_fields = ['order_id', 'created_at', 'expires_at']


@admin.register(AdminSettings)
class AdminSettingsAdmin(admin.ModelAdmin):
    list_display = ['key', 'value', 'updated_at']
