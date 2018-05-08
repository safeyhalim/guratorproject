"""
WSGI config for guratorproject project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.9/howto/deployment/wsgi/
"""

#functions to interface with the operating system(Win, OS, Linux)
import os
from django.core.wsgi import get_wsgi_application

# mapping object, representing the string environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "guratorproject.settings")

application = get_wsgi_application()
