"""
ASGI config for the food delivery project.

It exposes the ASGI callable as a module-level variable named
``application``. Django's ASGI documentation contains more details.
"""
import os
from django.core.asgi import get_asgi_application  # type: ignore

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
application = get_asgi_application()
