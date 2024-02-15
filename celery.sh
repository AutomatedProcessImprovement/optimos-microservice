#!/bin/sh -ex
celery -A src.tasks.celery beat -l debug &
celery -A src.tasks.celery worker -l debug