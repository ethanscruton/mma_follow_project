from __future__ import absolute_import, unicode_literals
import os

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mma_project.settings')
app = Celery('mma_project')

from decouple import config
from celery import Celery

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.

app.config_from_object('django.conf:settings', namespace='CELERY')
# Load task modules from all registered Django apps.

app.autodiscover_tasks()
app.conf.update(BROKER_URL=config('REDIS_URL'))

@app.task
def add(x, y):
    return x + y