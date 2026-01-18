from notifications_worker.infra.telegram.models import InlineKeyboardMarkup, InlineKeyboardButton


def order_actions(order_id: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Подробнее", callback_data=f"order:{order_id}")],
            [InlineKeyboardButton(text="Чат по заказу", callback_data=f"chat:order:{order_id}")],
        ]
    )


def admin_order_details_button(order_id: str) -> InlineKeyboardMarkup:
    """Клавиатура с кнопками для администратора"""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📋 Подробнее", callback_data=f"admin:order:{order_id}")],
            [InlineKeyboardButton(text="✏️ Изменить статус", callback_data=f"admin:status:{order_id}")]
        ]
    )
