from notifications_worker.infra.settings import settings

broker_url = settings.broker_url
result_backend = settings.result_backend_url

timezone = "UTC"
enable_utc = True

task_serializer = "json"
accept_content = ["json"]
result_serializer = "json"

task_acks_late = True
worker_prefetch_multiplier = 1

broker_transport_options = {
    "visibility_timeout": settings.celery_visibility_timeout,
}

task_default_queue = settings.celery_queue
task_default_exchange = settings.celery_queue
task_default_routing_key = settings.celery_queue

task_queues = {
    "notifications": {
        "exchange": "notifications",
        "routing_key": "notifications",
    },
    "images": {
        "exchange": "images",
        "routing_key": "images",
    },
}

task_routes = {
    "notifications.*": {"queue": "notifications"},
    "images.*": {"queue": "images"},
}
