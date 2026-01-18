from dataclasses import dataclass
from typing import Any


@dataclass(slots=True)
class InlineKeyboardButton:
    text: str
    callback_data: str

    def to_dict(self) -> dict[str, Any]:
        return {"text": self.text, "callback_data": self.callback_data}


@dataclass(slots=True)
class InlineKeyboardMarkup:
    inline_keyboard: list[list[InlineKeyboardButton]]

    def to_dict(self) -> dict[str, Any]:
        return {
            "inline_keyboard": [
                [btn.to_dict() for btn in row]
                for row in self.inline_keyboard
            ]
        }
