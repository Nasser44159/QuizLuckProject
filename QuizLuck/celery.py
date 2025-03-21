from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

# Définit les réglages par défaut
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'QuizLuckProject.settings')

app = Celery('QuizLuckProject')

# Charge les réglages de Django
app.config_from_object('django.conf:settings', namespace='CELERY')

# Découvre automatiquement les tâches définies dans les applications
app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
