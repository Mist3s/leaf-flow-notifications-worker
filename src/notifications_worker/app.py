from celery import Celery

celery_app = Celery("notifications_worker")
celery_app.config_from_object("notifications_worker.celeryconfig")
celery_app.autodiscover_tasks(["notifications_worker.tasks"])

import notifications_worker.tasks.notifications  # noqa: F401
