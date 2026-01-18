from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Redis / Celery
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_broker_db: int = 0
    redis_backend_db: int = 1

    celery_broker_url: str | None = None
    celery_result_backend: str | None = None

    celery_queue: str = "notifications"
    celery_visibility_timeout: int = 60 * 30

    # Telegram
    telegram_bot_token: str
    admin_chat_id: int

    telegram_http_timeout_seconds: float = 10.0
    telegram_http_connect_timeout_seconds: float = 5.0

    @property
    def broker_url(self) -> str:
        return self.celery_broker_url or f"redis://{self.redis_host}:{self.redis_port}/{self.redis_broker_db}"

    @property
    def result_backend_url(self) -> str:
        return self.celery_result_backend or f"redis://{self.redis_host}:{self.redis_port}/{self.redis_backend_db}"


settings = Settings()
