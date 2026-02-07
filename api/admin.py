from django.contrib import admin
from django.utils.html import format_html
from .models import Product, Order, AdminSettings


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['id', 'image_preview', 'name', 'category', 'price', 'stock', 'active', 'created_at']
    list_filter = ['category', 'active', 'created_at']
    search_fields = ['name', 'category']
    list_editable = ['stock', 'active', 'price']
    readonly_fields = ['image_preview_large', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Product Information', {
            'fields': ('name', 'category', 'price', 'stock')
        }),
        ('Image', {
            'fields': ('image', 'image_preview_large')
        }),
        ('Status', {
            'fields': ('active',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def image_preview(self, obj):
        """Display small image preview in list view"""
        if obj.image:
            return format_html(
                '<img src="{}" style="width: 50px; height: 50px; object-fit: cover; border-radius: 4px;" />',
                obj.image.url
            )
        return format_html('<span style="color: #999;">No image</span>')
    image_preview.short_description = 'Image'
    
    def image_preview_large(self, obj):
        """Display large image preview in detail view"""
        if obj.image:
            return format_html(
                '<img src="{}" style="max-width: 300px; max-height: 300px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);" />',
                obj.image.url
            )
        return format_html('<span style="color: #999;">No image uploaded</span>')
    image_preview_large.short_description = 'Current Image'


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_id', 'customer_name', 'phone_number', 'total_amount', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['order_id', 'customer_name', 'phone_number']
    readonly_fields = ['order_id', 'created_at', 'expires_at']


@admin.register(AdminSettings)
class AdminSettingsAdmin(admin.ModelAdmin):
    list_display = ['key', 'value', 'updated_at']
