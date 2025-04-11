import sys

from django.conf import settings
from django.db import connections
from django.test.runner import DiscoverRunner


class NoMigrationsTestRunner(DiscoverRunner):
    """
    Test runner that completely avoids Django's migration system and
    manually creates the database schema based on the application models.
    """

    def __init__(self, *args, **kwargs):
        self.check_migrations = kwargs.pop("check_migrations", False)
        super().__init__(*args, **kwargs)

    def setup_databases(self, **kwargs):
        """Custom database setup that creates tables directly from models."""
        # If migration checking is enabled, use the default behavior
        if self.check_migrations:
            print(
                "Migration integrity checking enabled - using Django's migration system..."
            )
            return super().setup_databases(**kwargs)

        # Store database configuration for teardown
        self.old_config = []

        # Set up each database
        for alias in connections:
            connection = connections[alias]

            # Store database creation info for teardown
            self.old_config.append(
                (
                    alias,
                    connection.settings_dict["NAME"],
                    connection.creation._get_test_db_name(),
                )
            )

            # Create test database
            if alias == "default":
                print(f"Creating test database '{connection.settings_dict['NAME']}'...")
                sys.stdout.flush()

                # Close existing connection
                connection.close()

                # Force create test database
                test_database_name = connection.creation._get_test_db_name()
                connection.settings_dict["NAME"] = test_database_name
                connection.creation._create_test_db(
                    verbosity=self.verbosity, autoclobber=True
                )

                # Create tables directly from models
                print("Creating tables directly from application models...")
                sys.stdout.flush()
                connection.introspection.installed_models = (
                    lambda c: []
                )  # Bypass introspection checks

                # Get all apps in order
                from django.apps import apps

                for app_config in apps.get_app_configs():
                    print(f"Processing models from {app_config.label}...", end=" ")
                    sys.stdout.flush()

                    # Create tables for each model
                    with connection.schema_editor() as schema_editor:
                        for model in app_config.get_models():
                            try:
                                if not model._meta.managed:
                                    continue
                                print(
                                    f"Creating table for {model.__name__}...", end=" "
                                )
                                schema_editor.create_model(model)
                                print("Done", end=" ")
                            except Exception as e:
                                print(f"Error: {str(e)}", end=" ")
                    print("Done")
                    sys.stdout.flush()

                print("Database setup complete.")

        return self.old_config

    def teardown_databases(self, old_config, **kwargs):
        """Preserve test databases for faster test runs."""
        # If migration checking is enabled, use the default behavior
        if self.check_migrations:
            return super().teardown_databases(old_config, **kwargs)

        # Intentionally do nothing to preserve the test database
        print("Preserving test database for faster future test runs.")
        return


class MigrationCheckingTestRunner(NoMigrationsTestRunner):
    """
    Test runner that uses Django's migration system to verify migration integrity.
    This runner is slower but validates that migrations work correctly.
    """

    def __init__(self, *args, **kwargs):
        kwargs["check_migrations"] = True
        super().__init__(*args, **kwargs)
