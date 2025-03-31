"""
ASGI configuration for the Scopewatch project.

This module contains the ASGI application used for serving the project
in an asynchronous environment.
"""

import os
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'scopewatch.settings')

application = get_asgi_application()
