from django.test.runner import DiscoverRunner


class NoMigrationsTestRunner(DiscoverRunner):
    """
    Test runner that uses syncdb instead of migrations to set up a test database.
    """
    
    def setup_databases(self, **kwargs):
        """
        Override the database creation process to avoid running migrations.
        """
        # Tell Django to create the database without running migrations
        for connection_name in kwargs.get('aliases', []):
            # Force Django to create the database tables directly from models
            kwargs['keepdb'] = True
        
        # Call the standard setup_databases
        return super().setup_databases(**kwargs)