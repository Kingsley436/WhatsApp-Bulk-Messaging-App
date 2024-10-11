import os
from celery import Celery
from celery.schedules import crontab
from django.conf import settings


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'whatsapp_project.settings')

app = Celery('whatsapp_project')

app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()


app.conf.beat_schedule = {
    'send-scheduled-messages-every-minute': {
        'task': 'messaging.tasks.send_scheduled_messages',
        'schedule': crontab(),  # Executes every minute; adjust as needed
    },
}

