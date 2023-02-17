from flask import Flask
from flask_cors import CORS
from flasgger import Swagger
from celery.schedules import crontab
import os

from exts import celery


def create_app():
    app = Flask(__name__)

    CORS(app)


    # celery config
    app.config["CELERY_BROKER_URL"] = os.environ.get("CELERY_BROKER_URL", "amqp://guest:guest@localhost:5672")
    app.config["CELERY_RESULT_BACKEND"] = os.environ.get("CELERY_RESULT_BACKEND", "redis://localhost:6379")

    return app


def create_celery(app):
    TaskBase = celery.Task

    class ContextTask(TaskBase):
        abstract = True

        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    # configure Celery
    celery.conf.update(
        CELERY_BROKER_URL=app.config["CELERY_BROKER_URL"],
        CELERY_RESULT_BACKEND=app.config["CELERY_RESULT_BACKEND"],
        CELERY_RESULT_PERSISTENT=True,
        CELERY_ACCEPT_CONTENT=["json"],
        CELERY_TASK_SERIALIZER="json",
        CELERY_RESULT_SERIALIZER="json",
        CELERY_IGNORE_RESULT=False,
        CELERY_TRACK_STARTED=True,
        CELERYBEAT_SCHEDULE={
            "every-hour-celery-data-clear": {
                "task": "src.tasks.clear_celery_folder",
                "schedule": crontab(minute="0", hour="*/1"),
                "args": ()
            },
        }
    )
    celery.Task = ContextTask

    return celery
