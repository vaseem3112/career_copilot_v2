"""
Celery worker entry point.

Start worker:
    celery -A celery_worker.celery worker --loglevel=info

Start beat (periodic tasks):
    celery -A celery_worker.celery beat --loglevel=info

Start both together (dev only):
    celery -A celery_worker.celery worker --beat --loglevel=info
"""
import os
from app import create_app
from app.extensions import celery

app = create_app(os.getenv("FLASK_ENV", "development"))
app.app_context().push()
