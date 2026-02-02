from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
import os


class Command(BaseCommand):
    help = 'Create admin user from environment variables'

    def handle(self, *args, **options):
        User = get_user_model()
        
        username = os.environ.get('DJANGO_ADMIN_USERNAME', 'admin')
        email = os.environ.get('DJANGO_ADMIN_EMAIL', 'admin@example.com')
        password = os.environ.get('DJANGO_ADMIN_PASSWORD')
        
        if not password:
            self.stdout.write(
                self.style.WARNING('DJANGO_ADMIN_PASSWORD not set, skipping admin creation')
            )
            return
        
        # Check if user already exists
        if User.objects.filter(username=username).exists():
            self.stdout.write(
                self.style.SUCCESS(f'Admin user "{username}" already exists')
            )
            # Update password if user exists
            user = User.objects.get(username=username)
            user.set_password(password)
            user.email = email
            user.is_staff = True
            user.is_superuser = True
            user.save()
            self.stdout.write(
                self.style.SUCCESS(f'Updated password for admin user "{username}"')
            )
        else:
            # Create new superuser
            User.objects.create_superuser(
                username=username,
                email=email,
                password=password
            )
            self.stdout.write(
                self.style.SUCCESS(f'Successfully created admin user "{username}"')
            )
