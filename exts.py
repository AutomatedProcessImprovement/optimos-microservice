from celery import Celery

celery = Celery("optimos_celery", include=['src.tasks'])