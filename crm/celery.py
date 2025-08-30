import os
from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "crm.settings")

app = Celery("crm")

# Use Redis as broker
app.conf.broker_url = "redis://localhost:6379/0"

# Load settings from Django settings with CELERY_ prefix
app.config_from_object("django.conf:settings", namespace="CELERY")

# Discover tasks.py in installed apps
app.autodiscover_tasks()
