from notifications_worker.domain.entities import NotificationsOrderEntity


def _status_emoji_emoji(status: str | None) -> str:
    """Возвращает эмодзи для статуса заказа"""
    mapping = {
        "created": "🆕",
        "processing": "⏳",
        "paid": "💰",
        "fulfilled": "✅",
        "cancelled": "❌"
    }
    return mapping.get(status or "", "📋")


def _human_status(status: str | None) -> str:
    mapping = {
        "created": "Создан",
        "processing": "В обработке",
        "paid": "Оплачен",
        "fulfilled": "Выполнен",
        "cancelled": "Отменён"
    }
    return mapping.get(status or "", status or "Неизвестно")


def _human_delivery(delivery_method: str | None) -> str:
    """Возвращает человеко-читаемый текст для способа доставки"""
    mapping = {
        "courier": "Курьер",
        "pickup": "Самовывоз"
    }
    return mapping.get(delivery_method or "", delivery_method or "Не указан")


def render_order_message_admin(e: NotificationsOrderEntity) -> str:
    delivery_method = _human_delivery(e.delivery_method)

    lines = [
        f"<b>Новый заказ</b>",
        f"📦 <b>Заказ #{e.order_id}</b>",
        f"👤 <b>Клиент:</b> {e.customer_name}",
        f"📱 <b>Телефон:</b> {e.phone}",
        f"💰 <b>Сумма:</b> {e.total}",
        f"🚚 <b>Доставка:</b> {delivery_method}",
    ]
    if e.email:
        lines.append(f"📧 <b>Email:</b> {e.email}")
    if e.address:
        lines.append(f"🗾 <b>Адрес:</b> {e.address}")
    if e.comment:
        lines.append("")
        lines.append("━━━━━━━━━━━━━━━━━━━━")
        lines.append("")
        lines.append(f"💬 <b>Комментарий:</b>\n{e.comment}")
    return "\n".join(lines)


def notify_update_status_order_admin(e: NotificationsOrderEntity) -> str:
    status_name = _human_status(e.new_status)
    lines = [
        f"✅ <b>Статус заказа обновлён</b>\n",
        f"📦 Заказ: #{e.order_id}",
        f"{status_name}",
    ]
    return "\n".join(lines)


def notify_new_order_user(e: NotificationsOrderEntity) -> str:
    lines = [
        f"✅ <b>Заказ #{e.order_id} создан</b>",
        "В ближайшее время с вами свяжется оператор. Если у вас возникнут вопросы, "
        "вы можете написать нам, нажав соответствующую кнопку ниже."
    ]
    return "\n".join(lines)


def notify_update_status_order_user(e: NotificationsOrderEntity) -> str:
    status_emoji = _status_emoji_emoji(e.new_status)
    status_text = _human_status(e.new_status)
    lines = [
        f"🔔 <b>Обновление по заказу #{e.order_id}</b>",
        f"{status_emoji} <b>Новый статус:</b> {status_text}"
    ]

    if e.status_comment:
        lines.append("")
        lines.append(f"💬 <b>Комментарий:</b>\n{e.status_comment}")

    return "\n".join(lines)
