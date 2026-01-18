from typing import Any

from notifications_worker.domain.entities import NotificationsOrderEntity
from notifications_worker.infra.settings import settings
from notifications_worker.infra.telegram.client import tg
from notifications_worker.infra.telegram.errors import TelegramNonRetryableError
from notifications_worker.services.templates import (
    render_order_message_admin,
    notify_new_order_user,
    notify_update_status_order_user,
    notify_update_status_order_admin
)
from notifications_worker.infra.telegram.keyboards import order_actions, admin_order_details_button


def dispatch_order_notification_admin(entity: NotificationsOrderEntity) -> None:
    admin_chat_id = settings.admin_chat_id
    admin_thread_id = entity.thread_id
    admin_text, reply_markup = _render_admin_message_and_markup(entity)
    _send_admin(admin_chat_id, admin_text, thread_id=admin_thread_id, reply_markup=reply_markup)


def dispatch_order_notification_user(entity: NotificationsOrderEntity) -> None:
    if not entity.telegram_id:
        return

    user_text, reply_markup = _render_user_message_and_markup(entity)

    try:
        _send_user_best_effort(chat_id=entity.telegram_id, text=user_text, reply_markup=reply_markup)
    except TelegramNonRetryableError as exc:
        print("User notification skipped (non-retryable): %s chat_id=%s", exc, entity.telegram_id)
        return


def _render_admin_message_and_markup(
        e: NotificationsOrderEntity,
) -> tuple[str, dict[str, Any] | None]:
    """
    Chooses admin text depending on status change.
    Adds inline keyboard if available.
    """
    if _is_new_order(e):
        text = render_order_message_admin(e)
    else:
        text = notify_update_status_order_admin(e)

    kb = admin_order_details_button(e.order_id)
    reply_markup = kb.to_dict() if hasattr(kb, "to_dict") else kb

    return text, reply_markup


def _render_user_message_and_markup(
    e: NotificationsOrderEntity,
) -> tuple[str, dict[str, Any] | None]:
    """
    Chooses user text depending on status change.
    Adds inline keyboard if available.
    """
    if _is_new_order(e):
        text = notify_new_order_user(e)
    else:
        text = notify_update_status_order_user(e)

    kb = order_actions(e.order_id)
    reply_markup = kb.to_dict() if hasattr(kb, "to_dict") else kb

    return text, reply_markup


def _is_new_order(e: NotificationsOrderEntity) -> bool:
    # Common heuristic: created -> created (initial notification)
    return (e.old_status == "created") and (e.new_status == "created")


def _send_admin(chat_id: int, text: str, *, thread_id: int | None, reply_markup: dict[str, Any] | None) -> None:
    """
    Admin is required.
    """
    tg.send_message(
        chat_id=chat_id,
        text=text,
        thread_id=thread_id,
        parse_mode="HTML",
        reply_markup=reply_markup
    )


def _send_user_best_effort(chat_id: int, text: str, *, reply_markup: dict[str, Any] | None) -> None:
    """
    User is required.
    """
    tg.send_message(
        chat_id=chat_id,
        text=text,
        parse_mode="HTML",
        reply_markup=reply_markup,
    )
