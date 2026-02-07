from notifications_worker.app import celery_app

if __name__ == "__main__":
    celery_app.worker_main([
        "worker",
        "-l", "info",
        "-Q", "notifications,images",
        "--concurrency", "4",
    ])
