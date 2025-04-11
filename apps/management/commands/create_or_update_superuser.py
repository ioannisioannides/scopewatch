"""
Management command to create or update a superuser from environment variables.

This command creates a superuser with credentials from environment variables,
or updates an existing one if it already exists. It looks for credentials with
different prefixes based on the environment (PROD_ or DEV_).
"""

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django.db import IntegrityError

from scopewatch.config import config, is_production

User = get_user_model()


class Command(BaseCommand):
    """
    Django management command to create or update a superuser with environment variables.

    This is particularly useful for automated environments like CI/CD pipelines
    or Docker deployments where you want to ensure an admin user exists.
    """

    help = "Create or update a superuser using environment variables"

    def handle(self, *args, **options):
        # Determine environment to use correct prefix for environment variables
        prefix = "PROD_" if is_production() else "DEV_"

        # Get credentials using the appropriate prefix
        username = config(f"{prefix}ADMIN_USERNAME", default=None)
        password = config(f"{prefix}ADMIN_PASSWORD", default=None)
        email = config(f"{prefix}ADMIN_EMAIL", default=None)

        # For backwards compatibility, check without prefix if not found
        if username is None:
            username = config("ADMIN_USERNAME", default=None)
        if password is None:
            password = config("ADMIN_PASSWORD", default=None)
        if email is None:
            email = config("ADMIN_EMAIL", default=None)

        if not all([username, password, email]):
            env_type = "Production" if is_production() else "Development"
            self.stdout.write(
                self.style.WARNING(
                    f"Admin user environment variables not set for {env_type} environment.\n"
                    f"Set {prefix}ADMIN_USERNAME, {prefix}ADMIN_PASSWORD, {prefix}ADMIN_EMAIL variables."
                )
            )
            return

        try:
            user = User.objects.get(username=username)
            user.email = email
            user.set_password(password)
            user.save()
            self.stdout.write(self.style.SUCCESS(f"Updated existing superuser: {username}"))
        except User.DoesNotExist:
            try:
                User.objects.create_superuser(username=username, email=email, password=password)
                self.stdout.write(self.style.SUCCESS(f"Created new superuser: {username}"))
            except IntegrityError as exc:
                raise CommandError(f"Could not create superuser: {username}") from exc
