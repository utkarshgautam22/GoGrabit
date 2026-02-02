from django.core.management.base import BaseCommand
from api.models import Product


class Command(BaseCommand):
    help = 'Seed database with sample products'

    def handle(self, *args, **options):
        products = [
            # Snacks
            {'name': 'Lays Classic', 'category': 'Snacks', 'price': 20, 'stock': 50, 
             'image': 'https://images.unsplash.com/photo-1566478989037-eec170784d0b?w=300'},
            {'name': 'Kurkure', 'category': 'Snacks', 'price': 10, 'stock': 60,
             'image': 'https://images.unsplash.com/photo-1621939514649-280e2ee25f60?w=300'},
            {'name': 'Bingo Mad Angles', 'category': 'Snacks', 'price': 15, 'stock': 40,
             'image': 'https://images.unsplash.com/photo-1600952841320-db92ec4047ca?w=300'},
            {'name': 'Parle-G', 'category': 'Snacks', 'price': 5, 'stock': 100,
             'image': 'https://images.unsplash.com/photo-1558961363-fa8fdf82db35?w=300'},
            
            # Beverages
            {'name': 'Coca Cola', 'category': 'Beverages', 'price': 40, 'stock': 30,
             'image': 'https://images.unsplash.com/photo-1554866585-cd94860890b7?w=300'},
            {'name': 'Sprite', 'category': 'Beverages', 'price': 40, 'stock': 30,
             'image': 'https://images.unsplash.com/photo-1625740614678-151e066dce10?w=300'},
            {'name': 'Red Bull', 'category': 'Beverages', 'price': 120, 'stock': 20,
             'image': 'https://images.unsplash.com/photo-1622543925917-763c34d1a86e?w=300'},
            {'name': 'Water Bottle', 'category': 'Beverages', 'price': 20, 'stock': 100,
             'image': 'https://images.unsplash.com/photo-1548839140-29a749e1cf4d?w=300'},
            
            # Stationery
            {'name': 'Classmate Notebook', 'category': 'Stationery', 'price': 50, 'stock': 25,
             'image': 'https://images.unsplash.com/photo-1517842645767-c639042777db?w=300'},
            {'name': 'Pen Set (5 pcs)', 'category': 'Stationery', 'price': 30, 'stock': 35,
             'image': 'https://images.unsplash.com/photo-1586075010923-2dd4570fb338?w=300'},
            {'name': 'Pencil Box', 'category': 'Stationery', 'price': 80, 'stock': 15,
             'image': 'https://images.unsplash.com/photo-1533090161767-e6ffed986c88?w=300'},
            
            # Instant Food
            {'name': 'Maggi Noodles', 'category': 'Instant Food', 'price': 12, 'stock': 80,
             'image': 'https://images.unsplash.com/photo-1569718212165-3a8278d5f624?w=300'},
            {'name': 'Cup Noodles', 'category': 'Instant Food', 'price': 30, 'stock': 40,
             'image': 'https://images.unsplash.com/photo-1617093727343-374698b1b08d?w=300'},
            {'name': 'Oats Pack', 'category': 'Instant Food', 'price': 45, 'stock': 30,
             'image': 'https://images.unsplash.com/photo-1517673132405-a56a62b18caf?w=300'},
            
            # Hygiene
            {'name': 'Hand Sanitizer', 'category': 'Hygiene', 'price': 50, 'stock': 40,
             'image': 'https://images.unsplash.com/photo-1584744982491-665216d95f8b?w=300'},
            {'name': 'Tissues Pack', 'category': 'Hygiene', 'price': 25, 'stock': 50,
             'image': 'https://images.unsplash.com/photo-1629198688000-71f23e745b6e?w=300'},
        ]

        created = 0
        for product_data in products:
            product, created_new = Product.objects.get_or_create(
                name=product_data['name'],
                defaults=product_data
            )
            if created_new:
                created += 1
                self.stdout.write(self.style.SUCCESS(f'Created: {product.name}'))
            else:
                self.stdout.write(f'Already exists: {product.name}')

        self.stdout.write(self.style.SUCCESS(f'\nSeeding complete! Created {created} new products.'))
