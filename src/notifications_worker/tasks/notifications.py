from pydantic import ValidationError

from notifications_worker.app import celery_app
from notifications_worker.domain.entities import NotificationsOrderEntity
from notifications_worker.infra.telegram.errors import TelegramRetryableError
from notifications_worker.services.dispatcher import (
    dispatch_order_notification_user,
    dispatch_order_notification_admin
)


@celery_app.task(name="notifications.send_notification.order.admin", bind=True, max_retries=5)
def send_notification_order_admin(self, payload: dict) -> None:
    try:
        entity = NotificationsOrderEntity.model_validate(payload)
        dispatch_order_notification_admin(entity=entity)

    except ValidationError:
        # контракт сломан
        raise

    except TelegramRetryableError as exc:
        raise self.retry(exc=exc, countdown=10)


@celery_app.task(name="notifications.send_notification.order.user", bind=True, max_retries=5)
def send_notification_order_user(self, payload: dict) -> None:
    try:
        entity = NotificationsOrderEntity.model_validate(payload)
        dispatch_order_notification_user(entity=entity)

    except Exception as exc:
        raise self.retry(exc=exc, countdown=10)
