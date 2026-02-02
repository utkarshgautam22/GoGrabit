from django.urls import path
from . import views

urlpatterns = [
    # Public endpoints
    path('products', views.product_list, name='product-list'),
    path('orders', views.order_list, name='order-list'),
    path('orders/<str:order_id>', views.order_detail, name='order-detail'),
    path('orders/<str:order_id>/cancel', views.order_cancel, name='order-cancel'),
    
    # Admin endpoints
    path('admin/products', views.product_manage, name='product-manage'),
    path('admin/products/<int:pk>', views.product_detail, name='product-detail'),
    path('admin/products/bulk', views.bulk_update_products, name='bulk-update'),
    path('admin/orders/<str:order_id>/pick', views.order_pick, name='order-pick'),
    path('admin/orders/<str:order_id>/complete', views.order_complete, name='order-complete'),
    path('admin/stats', views.admin_stats, name='admin-stats'),
    path('admin/low-stock', views.admin_low_stock, name='admin-low-stock'),
    path('admin/active-orders', views.admin_active_orders, name='admin-active-orders'),
    path('admin/verify-pin', views.admin_verify_pin, name='admin-verify-pin'),
    path('admin/export', views.export_data, name='export-data'),
    path('admin/clear-database', views.clear_database, name='clear-database'),
    
    # Telegram webhook
    path('telegram/webhook', views.telegram_webhook, name='telegram-webhook'),
]
