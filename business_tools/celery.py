import os
from celery import Celery

# Which Django settings file to use
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'business_tools.settings')

# Create the Celery app
app = Celery('business_tools')

# Read Celery config from Django settings.py
app.config_from_object('django.conf:settings', namespace='CELERY')

# Find tasks from all apps automatically
app.autodiscover_tasks()