import os

from celery import Celery


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ZooMind.settings")

app = Celery("ZooMind")

app.config_from_object("django.conf:settings", namespace="CELERY")

app.autodiscover_tasks()