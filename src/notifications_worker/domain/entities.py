from decimal import Decimal

from pydantic import BaseModel, ConfigDict

from notifications_worker.domain.enums import OrderStatus, DeliveryMethod


class NotificationsOrderEntity(BaseModel):
    model_config = ConfigDict(extra="forbid")

    order_id: str
    telegram_id: int | None = None
    old_status: OrderStatus
    new_status: OrderStatus
    comment: str | None = None
    phone: str
    customer_name: str
    total: Decimal
    delivery_method: DeliveryMethod
    email: str | None = None
    address: str | None = None
    status_comment: str | None = None
    admin_chat_id: int | None = None
    thread_id: int | None = None
    created_at: str


class ImageUploadedEntity(BaseModel):
    """Payload события image.uploaded."""

    image_id: int
    product_id: str
    original_url: str
    original_key: str
    original_format: str
    original_width: int
    original_height: int


class ImageVariantResult(BaseModel):
    """Результат создания варианта изображения."""

    variant: str
    storage_key: str
    format: str
    width: int
    height: int
    byte_size: int
