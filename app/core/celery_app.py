from celery import Celery
from app.config import settings

celery_app = Celery(
    "worker",
    broker=settings.redis_url,
    backend=settings.redis_url,
)

celery_app.conf.update(
    # Upstash requires TLS (rediss://) — this tells Celery's Redis
    # transport not to verify a cert chain, which Upstash's setup doesn't need
    broker_use_ssl={"ssl_cert_reqs": "none"},
    redis_backend_use_ssl={"ssl_cert_reqs": "none"},
    include=["app.services.background_tasks"],

    broker_connection_retry_on_startup=True,

    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],

    timezone="UTC",
    enable_utc=True,

    task_acks_late=True,          # if the worker crashes mid-task, redeliver it instead of losing it
    worker_prefetch_multiplier=1, # don't let one slow task block others queued behind it
    task_default_retry_delay=30,  # if Pxxl is briefly unreachable, wait 30s before retrying
)