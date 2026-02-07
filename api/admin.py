from django.contrib import admin
from django.utils.html import format_html
from django import forms
from .models import Product, Order, AdminSettings
import base64


class ProductAdminForm(forms.ModelForm):
    """Custom form to handle image file upload and convert to base64"""
    image_file = forms.ImageField(required=False, label='Upload Image')
    
    class Meta:
        model = Product
        fields = '__all__'
        widgets = {
            'image': forms.HiddenInput()  # Hide the base64 field
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Remove the image field from display since we use image_file
        if 'image' in self.fields:
            self.fields['image'].widget = forms.HiddenInput()
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        
        # Convert uploaded image to base64
        if self.cleaned_data.get('image_file'):
            image_file = self.cleaned_data['image_file']
            image_data = image_file.read()
            base64_encoded = base64.b64encode(image_data).decode('utf-8')
            
            # Detect image format
            content_type = image_file.content_type or 'image/jpeg'
            instance.image = f"data:{content_type};base64,{base64_encoded}"
        
        if commit:
            instance.save()
        return instance


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    form = ProductAdminForm
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
            'fields': ('image_file', 'image_preview_large')
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
                obj.image
            )
        return format_html('<span style="color: #999;">No image</span>')
    image_preview.short_description = 'Image'
    
    def image_preview_large(self, obj):
        """Display large image preview in detail view"""
        if obj.image:
            return format_html(
                '<img src="{}" style="max-width: 300px; max-height: 300px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);" />',
                obj.image
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
