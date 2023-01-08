from __future__ import absolute_import
from celery import Celery
from celery import current_app
from celery.signals import after_task_publish
from django.conf import settings
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'djangoProject1.settings')

app = Celery('djangoProject1')

app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)


@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))


@after_task_publish.connect
def update_sent_state(sender=None, headers=None, **kwargs):
    # the task may not exist if sent using `send_task` which
    # sends tasks by name, so fall back to the default result backend
    # if that is the case.
    task = current_app.tasks.get(sender)
    backend = task.backend if task else current_app.backend
    backend.store_result(headers['id'], None, "ACCEPTED")
