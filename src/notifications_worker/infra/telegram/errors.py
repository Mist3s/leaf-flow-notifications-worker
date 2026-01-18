from dataclasses import dataclass
from typing import Any


@dataclass(slots=True)
class TelegramAPIError(Exception):
    """
    Error returned by Telegram Bot API when HTTP status is 200 but {"ok": false}
    or when we want to preserve Telegram error details.
    """
    description: str
    error_code: int | None = None
    parameters: dict[str, Any] | None = None

    def __str__(self) -> str:
        code = f"{self.error_code} " if self.error_code is not None else ""
        return f"TelegramAPIError({code}{self.description})"


class TelegramRetryableError(Exception):
    """Transient error: should be retried (network, 429, 5xx, etc.)."""


class TelegramNonRetryableError(Exception):
    """Permanent error: should NOT be retried (bad chat id, bot blocked, etc.)."""


@dataclass(slots=True)
class TelegramRateLimited(TelegramRetryableError):
    retry_after: int | None = None

    def __str__(self) -> str:
        return f"TelegramRateLimited(retry_after={self.retry_after})"


@dataclass(slots=True)
class TelegramBadRequest(TelegramNonRetryableError):
    description: str

    def __str__(self) -> str:
        return f"TelegramBadRequest({self.description})"


@dataclass(slots=True)
class TelegramForbidden(TelegramNonRetryableError):
    description: str

    def __str__(self) -> str:
        return f"TelegramForbidden({self.description})"


@dataclass(slots=True)
class TelegramNotFound(TelegramNonRetryableError):
    description: str

    def __str__(self) -> str:
        return f"TelegramNotFound({self.description})"


@dataclass(slots=True)
class TelegramServerError(TelegramRetryableError):
    status_code: int
    body: str | None = None

    def __str__(self) -> str:
        return f"TelegramServerError(status_code={self.status_code})"


@dataclass(slots=True)
class TelegramTransportError(TelegramRetryableError):
    message: str

    def __str__(self) -> str:
        return f"TelegramTransportError({self.message})"
