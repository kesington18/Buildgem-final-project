#!/bin/sh
# Runs the Celery worker in the background and the API in the foreground (one free service).
celery -A app.core.celery_app.celery_app worker --loglevel=info --concurrency=1 --pool=solo &
exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
