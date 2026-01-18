from typing import Literal

DeliveryMethod = Literal["pickup", "courier", "cdek"]
OrderStatus = Literal["created", "processing", "paid", "fulfilled", "cancelled"]
