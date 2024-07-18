import os
from celery import Celery

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myshop.settings')

# Create a Celery instance named 'myshop'.
app = Celery('myshop')

# Configure Celery settings from the Django settings module.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Automatically discover and register tasks in Django apps.
app.autodiscover_tasks()
