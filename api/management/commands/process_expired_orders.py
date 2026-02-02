from django.core.management.base import BaseCommand
from django.utils import timezone
from api.models import Order
import time


class Command(BaseCommand):
    help = 'Process expired orders and restore stock'

    def add_arguments(self, parser):
        parser.add_argument(
            '--interval',
            type=int,
            default=300,  # 5 minutes
            help='Check interval in seconds (default: 300)'
        )

    def handle(self, *args, **options):
        interval = options['interval']
        self.stdout.write(self.style.SUCCESS(f'Starting order expiration checker (interval: {interval}s)'))
        
        while True:
            try:
                self.check_expired_orders()
                time.sleep(interval)
            except KeyboardInterrupt:
                self.stdout.write(self.style.WARNING('Stopping order expiration checker'))
                break
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error: {e}'))
                time.sleep(interval)

    def check_expired_orders(self):
        """Find and cancel expired orders"""
        now = timezone.now()
        
        # Find expired reserved orders
        expired_orders = Order.objects.filter(
            status='reserved',
            expires_at__lt=now
        )
        
        count = expired_orders.count()
        
        if count > 0:
            self.stdout.write(f'Found {count} expired order(s)')
            
            for order in expired_orders:
                # Cancel order and restore stock
                if order.cancel():
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'Cancelled order {order.order_id} - Restored stock'
                        )
                    )
                else:
                    self.stdout.write(
                        self.style.WARNING(
                            f'Failed to cancel order {order.order_id}'
                        )
                    )
        else:
            self.stdout.write(self.style.SUCCESS(f'[{now.strftime("%Y-%m-%d %H:%M:%S")}] No expired orders'))
