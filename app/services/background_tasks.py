from app.core.celery_app import celery_app

@celery_app.task
def ping():
    print("pong - celery task executed")
    return "pong"