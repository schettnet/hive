# esite/celery_app.py

import os

from celery import Celery

# Set default Django settings
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "esite.settings.production")

app = Celery("esite")
app.config_from_object("django.conf.settings", namespace="CELERY")
app.autodiscover_tasks()