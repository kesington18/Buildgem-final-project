from time import timezone

import celery
from celery import Celery
from app.config import settings

celery_app = Celery(
    "worker",
    broker=settings.redis_url,
    backend=settings.redis_url,
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
    # If a worker crashes mid-send, redeliver the task instead of losing it
    task_acks_late=True,
    # don't let one slow task block others queued behind it
    worker_prefetch_multiplier=1,
    # if Pxxl is briefly unreachable, wait 30s before retrying
    task_default_retry_delay=30,  # seconds
)
