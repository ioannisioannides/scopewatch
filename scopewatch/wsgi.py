"""
WSGI configuration for the Scopewatch project.

This module contains the WSGI application used for serving the project
in a production environment.
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'scopewatch.settings')

application = get_wsgi_application()
