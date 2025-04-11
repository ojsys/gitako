"""
ASGI config for gitako project.
"""

import os

from django.core.asgi import get_asgi_application

# Use development settings for local development
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gitako.settings.dev')

application = get_asgi_application()
