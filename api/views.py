from rest_framework import viewsets, status
from rest_framework.decorators import api_view, action
from rest_framework.response import Response
from django.utils import timezone
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Sum, Count, Q
from decimal import Decimal
import csv
import json
import hashlib

from .models import Product, Order, AdminSettings
from .serializers import ProductSerializer, OrderSerializer


# Admin PIN (stored securely in settings)
ADMIN_PIN = "1234"  # Change this in production!


def verify_admin_pin(pin):
    """Verify admin PIN"""
    return pin == ADMIN_PIN


@api_view(['GET'])
def product_list(request):
    """Get all active products"""
    products = Product.objects.filter(active=True)
    serializer = ProductSerializer(products, many=True)
    return Response(serializer.data)


@api_view(['GET', 'POST'])
def product_manage(request):
    """Manage products (admin only)"""
    pin = request.headers.get('X-Admin-Pin') or request.GET.get('pin')
    
    if not verify_admin_pin(pin):
        return Response({'error': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)
    
    if request.method == 'GET':
        products = Product.objects.all()
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        serializer = ProductSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT', 'DELETE'])
def product_detail(request, pk):
    """Update or delete a product (admin only)"""
    pin = request.headers.get('X-Admin-Pin') or request.GET.get('pin')
    
    if not verify_admin_pin(pin):
        return Response({'error': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)
    
    try:
        product = Product.objects.get(pk=pk)
    except Product.DoesNotExist:
        return Response({'error': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)
    
    if request.method == 'PUT':
        serializer = ProductSerializer(product, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        product.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET', 'POST'])
@csrf_exempt
def order_list(request):
    """List orders or create new order"""
    if request.method == 'GET':
        orders = Order.objects.all()
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        # Check if user already has an active order (reserved or picked)
        phone_number = request.data.get('phoneNumber')
        if phone_number:
            existing_order = Order.objects.filter(
                phone_number=phone_number,
                status__in=['reserved', 'picked']
            ).first()
            
            if existing_order:
                return Response({
                    'error': 'You already have an active order. Please complete or cancel it first.',
                    'existingOrderId': existing_order.order_id
                }, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = OrderSerializer(data=request.data)
        if serializer.is_valid():
            order = serializer.save()
            
            # Send Telegram notification (non-blocking)
            try:
                from .telegram_bot import send_order_notification
                send_order_notification(order)
            except Exception as e:
                print(f"Telegram notification failed: {e}")
            
            return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def order_detail(request, order_id):
    """Get order details"""
    try:
        order = Order.objects.get(order_id=order_id)
        serializer = OrderSerializer(order)
        return Response(serializer.data)
    except Order.DoesNotExist:
        return Response({'error': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@csrf_exempt
def order_cancel(request, order_id):
    """Cancel an order"""
    try:
        order = Order.objects.get(order_id=order_id)
        
        if order.status in ['cancelled', 'completed']:
            return Response({'error': 'Order cannot be cancelled'}, status=status.HTTP_400_BAD_REQUEST)
        
        if order.cancel():
            return Response({'message': 'Order cancelled successfully', 'orderId': order_id})
        else:
            return Response({'error': 'Failed to cancel order'}, status=status.HTTP_400_BAD_REQUEST)
    
    except Order.DoesNotExist:
        return Response({'error': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
def order_pick(request, order_id):
    """Mark order as picked (admin only)"""
    pin = request.headers.get('X-Admin-Pin') or request.data.get('pin')
    
    if not verify_admin_pin(pin):
        return Response({'error': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)
    
    try:
        order = Order.objects.get(order_id=order_id)
        
        if order.mark_picked():
            # Send Telegram update
            try:
                from .telegram_bot import send_order_picked_notification
                send_order_picked_notification(order)
            except Exception as e:
                print(f"Telegram notification failed: {e}")
            
            return Response({'message': 'Order marked as picked', 'orderId': order_id})
        else:
            return Response({'error': 'Order cannot be picked'}, status=status.HTTP_400_BAD_REQUEST)
    
    except Order.DoesNotExist:
        return Response({'error': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
def order_complete(request, order_id):
    """Mark order as completed (admin only)"""
    pin = request.headers.get('X-Admin-Pin') or request.data.get('pin')
    
    if not verify_admin_pin(pin):
        return Response({'error': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)
    
    try:
        order = Order.objects.get(order_id=order_id)
        
        if order.mark_completed():
            return Response({'message': 'Order marked as completed', 'orderId': order_id})
        else:
            return Response({'error': 'Order cannot be completed'}, status=status.HTTP_400_BAD_REQUEST)
    
    except Order.DoesNotExist:
        return Response({'error': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
def admin_stats(request):
    """Get admin dashboard statistics"""
    pin = request.headers.get('X-Admin-Pin') or request.GET.get('pin')
    
    if not verify_admin_pin(pin):
        return Response({'error': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)
    
    today = timezone.now().date()
    
    stats = {
        'totalProducts': Product.objects.filter(active=True).count(),
        'todayRevenue': Order.objects.filter(
            created_at__date=today,
            status='completed'
        ).aggregate(Sum('total_amount'))['total_amount__sum'] or 0,
        'todayOrders': Order.objects.filter(created_at__date=today).count(),
        'lowStockItems': Product.objects.filter(stock__lte=5, active=True).count(),
        'activeOrders': Order.objects.filter(status__in=['reserved', 'picked']).count(),
        'completedOrders': Order.objects.filter(status='completed').count(),
        'cancelledOrders': Order.objects.filter(status='cancelled').count(),
    }
    
    return Response(stats)


@api_view(['GET'])
def admin_low_stock(request):
    """Get low stock products"""
    pin = request.headers.get('X-Admin-Pin') or request.GET.get('pin')
    
    if not verify_admin_pin(pin):
        return Response({'error': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)
    
    threshold = int(request.GET.get('threshold', 5))
    products = Product.objects.filter(stock__lte=threshold, active=True)
    serializer = ProductSerializer(products, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def admin_active_orders(request):
    """Get active orders (reserved or picked)"""
    pin = request.headers.get('X-Admin-Pin') or request.GET.get('pin')
    
    if not verify_admin_pin(pin):
        return Response({'error': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)
    
    orders = Order.objects.filter(status__in=['reserved', 'picked'])
    serializer = OrderSerializer(orders, many=True)
    return Response(serializer.data)


@api_view(['POST'])
def admin_verify_pin(request):
    """Verify admin PIN"""
    pin = request.data.get('pin')
    
    if verify_admin_pin(pin):
        return Response({'success': True, 'message': 'PIN verified'})
    else:
        return Response({'success': False, 'error': 'Invalid PIN'}, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['GET'])
def export_data(request):
    """Export data as CSV"""
    pin = request.headers.get('X-Admin-Pin') or request.GET.get('pin')
    
    if not verify_admin_pin(pin):
        return Response({'error': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)
    
    export_type = request.GET.get('type', 'products')
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{export_type}_{timezone.now().strftime("%Y%m%d")}.csv"'
    
    writer = csv.writer(response)
    
    if export_type == 'products':
        writer.writerow(['ID', 'Name', 'Category', 'Price', 'Stock', 'Active'])
        products = Product.objects.all()
        for p in products:
            writer.writerow([p.id, p.name, p.category, p.price, p.stock, p.active])
    
    elif export_type == 'orders':
        writer.writerow(['Order ID', 'Customer', 'Phone', 'Room', 'Total', 'Status', 'Created'])
        orders = Order.objects.all()
        for o in orders:
            writer.writerow([
                o.order_id, o.customer_name, o.phone_number, o.room_number,
                o.total_amount, o.status, o.created_at.strftime('%Y-%m-%d %H:%M:%S')
            ])
    
    return response


@api_view(['POST'])
def bulk_update_products(request):
    """Bulk update products (admin only)"""
    pin = request.headers.get('X-Admin-Pin') or request.data.get('pin')
    
    if not verify_admin_pin(pin):
        return Response({'error': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)
    
    updates = request.data.get('updates', [])
    updated = 0
    
    for update in updates:
        try:
            product = Product.objects.get(id=update['id'])
            for key, value in update.items():
                if key != 'id' and hasattr(product, key):
                    setattr(product, key, value)
            product.save()
            updated += 1
        except Product.DoesNotExist:
            pass
    
    return Response({'message': f'{updated} products updated'})


@api_view(['POST'])
def clear_database(request):
    """Clear all data (admin only - DANGEROUS!)"""
    pin = request.headers.get('X-Admin-Pin') or request.data.get('pin')
    
    if not verify_admin_pin(pin):
        return Response({'error': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)
    
    confirm = request.data.get('confirm')
    
    if confirm != 'DELETE_ALL_DATA':
        return Response({'error': 'Confirmation required'}, status=status.HTTP_400_BAD_REQUEST)
    
    Product.objects.all().delete()
    Order.objects.all().delete()
    
    return Response({'message': 'All data cleared'})


@csrf_exempt
def telegram_webhook(request):
    """Handle Telegram webhook for button callbacks"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    try:
        data = json.loads(request.body)
        
        # Handle callback query (button press)
        if 'callback_query' in data:
            callback = data['callback_query']
            callback_data = callback['data']
            
            # Parse callback data (format: "pick_ORDER_ID")
            if callback_data.startswith('pick_'):
                order_id = callback_data.split('_')[1]
                
                try:
                    order = Order.objects.get(order_id=order_id)
                    
                    if order.mark_picked():
                        # Send success response
                        from .telegram_bot import answer_callback_query, edit_message
                        answer_callback_query(callback['id'], f"Order {order_id} marked as PICKED")
                        edit_message(
                            callback['message']['chat']['id'],
                            callback['message']['message_id'],
                            f"✅ Order {order_id} - PICKED"
                        )
                        
                        return JsonResponse({'success': True})
                    else:
                        from .telegram_bot import answer_callback_query
                        answer_callback_query(callback['id'], "Order cannot be picked")
                        return JsonResponse({'error': 'Cannot pick order'})
                
                except Order.DoesNotExist:
                    from .telegram_bot import answer_callback_query
                    answer_callback_query(callback['id'], "Order not found")
                    return JsonResponse({'error': 'Order not found'})
        
        return JsonResponse({'success': True})
    
    except Exception as e:
        print(f"Webhook error: {e}")
        return JsonResponse({'error': str(e)}, status=500)
