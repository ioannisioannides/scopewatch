"""
Management command to create or update a superuser from environment variables.

This command creates a superuser with credentials from environment variables,
or updates an existing one if it already exists.
"""

from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model
from django.db import IntegrityError

from scopewatch.config import config

User = get_user_model()

class Command(BaseCommand):
    """
    Django management command to create or update a superuser with environment variables.
    
    This is particularly useful for automated environments like CI/CD pipelines
    or Docker deployments where you want to ensure an admin user exists.
    """
    
    help = 'Create or update a superuser using environment variables'
    
    def handle(self, *args, **options):
        username = config('ADMIN_USERNAME', default=None)
        password = config('ADMIN_PASSWORD', default=None)
        email = config('ADMIN_EMAIL', default=None)
        
        if not all([username, password, email]):
            self.stdout.write(self.style.WARNING(
                'Admin user environment variables not set. '
                'Set ADMIN_USERNAME, ADMIN_PASSWORD, ADMIN_EMAIL to create a superuser.'
            ))
            return
            
        try:
            user = User.objects.get(username=username)
            user.email = email
            user.set_password(password)
            user.save()
            self.stdout.write(self.style.SUCCESS(f'Updated existing superuser: {username}'))
        except User.DoesNotExist:
            try:
                User.objects.create_superuser(username=username, email=email, password=password)
                self.stdout.write(self.style.SUCCESS(f'Created new superuser: {username}'))
            except IntegrityError:
                raise CommandError(f'Could not create superuser: {username}')