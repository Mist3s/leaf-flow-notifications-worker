# leaf-flow-notifications-worker

Celery worker для отправки уведомлений Leaf Flow через Telegram.

## Возможности

- 📱 **Уведомления пользователю** — личные сообщения клиентам (если есть `telegram_id`)
- 👨‍💼 **Уведомления администратору** — сообщения в админский чат с поддержкой тредов/топиков
- 🔄 **Автоматические ретраи** — до 5 повторных попыток при ошибках Telegram API
- ⌨️ **Inline-кнопки** — интерактивные клавиатуры для быстрых действий

## Архитектура

```
┌─────────────┐       ┌─────────┐       ┌──────────────────┐       ┌──────────────┐
│   Backend   │──────▶│  Redis  │◀──────│  Celery Worker   │──────▶│ Telegram API │
│  (FastAPI)  │       │ (broker)│       │ (этот сервис)    │       │              │
└─────────────┘       └─────────┘       └──────────────────┘       └──────────────┘
```

- **Backend (FastAPI)** публикует задачу в Redis через Celery `send_task(...)`
- **Redis** выступает брокером очереди
- **Этот сервис (Celery worker)** читает задачи из Redis и отправляет уведомления в Telegram Bot API

## Celery Tasks

| Task name | Описание |
|-----------|----------|
| `notifications.send_notification.order.admin` | Уведомление о заказе в админский чат |
| `notifications.send_notification.order.user` | Уведомление о заказе пользователю |

### Payload contract

Payload — JSON-serializable dict, соответствующий `NotificationsOrderEntity`:

```python
{
    "order_id": "12345",
    "telegram_id": 123456789,        # опционально, для user-уведомлений
    "old_status": "created",         # created | processing | paid | fulfilled | cancelled
    "new_status": "processing",
    "phone": "+7 999 123-45-67",
    "customer_name": "Иван Иванов",
    "total": "1500.00",              # Decimal как строка
    "delivery_method": "courier",    # pickup | courier | cdek
    "comment": "Комментарий",        # опционально
    "email": "client@example.com",   # опционально
    "address": "ул. Примерная, 1",   # опционально
    "status_comment": "Готов",       # опционально, комментарий к статусу
    "admin_chat_id": -1001234567890, # опционально
    "thread_id": 123                 # опционально, ID топика/треда
}
```

## Переменные окружения

Создайте `.env` файл в корне проекта:

```env
# Telegram (обязательные)
TELEGRAM_BOT_TOKEN=your_bot_token
ADMIN_CHAT_ID=-1001234567890

# Telegram (опциональные)
TELEGRAM_HTTP_TIMEOUT_SECONDS=10.0
TELEGRAM_HTTP_CONNECT_TIMEOUT_SECONDS=5.0

# Redis / Celery (опциональные, есть defaults)
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_BROKER_DB=0
REDIS_BACKEND_DB=1

# Или override полными URL
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/1

# Celery настройки
CELERY_QUEUE=notifications
CELERY_VISIBILITY_TIMEOUT=1800
```

## Локальный запуск

### 1. Запуск Redis

```bash
docker run --rm -p 6379:6379 redis:7-alpine
```

### 2. Установка зависимостей

```bash
python -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install -e .
```

### 3. Запуск воркера

```bash
celery -A notifications_worker.app worker -l info --concurrency 2
```

Или через Python:

```bash
python -m notifications_worker
```

Указать конкретную очередь:

```bash
celery -A notifications_worker.app worker -l info -Q notifications --concurrency 2
```

## Docker

### Сборка образа

```bash
docker build -t leaf-flow-notifications-worker .
```

### Запуск контейнера

```bash
docker run --rm \
  -e TELEGRAM_BOT_TOKEN=your_token \
  -e ADMIN_CHAT_ID=-1001234567890 \
  -e REDIS_HOST=redis \
  --network your_network \
  leaf-flow-notifications-worker
```

### Docker Compose пример

```yaml
services:
  notifications-worker:
    build: .
    environment:
      - TELEGRAM_BOT_TOKEN=${TELEGRAM_BOT_TOKEN}
      - ADMIN_CHAT_ID=${ADMIN_CHAT_ID}
      - REDIS_HOST=redis
    depends_on:
      - redis
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data

volumes:
  redis_data:
```

## Интеграция с Backend

Backend публикует задачи по имени (не требует импорта воркера):

```python
from celery import Celery

celery = Celery("leaf_flow_client", broker="redis://localhost:6379/0")

# Уведомление администратору
payload = entity.model_dump(mode="json")
celery.send_task(
    "notifications.send_notification.order.admin",
    args=[payload],
)

# Уведомление пользователю
celery.send_task(
    "notifications.send_notification.order.user",
    args=[payload],
)
```

## Логика уведомлений

### Уведомления администратору

- Отправляются в `ADMIN_CHAT_ID`
- Если в payload передан `thread_id` — сообщение уходит в указанный топик
- Новый заказ (статус `created → created`) — полная карточка с данными клиента
- Смена статуса — краткое уведомление с новым статусом
- К сообщению добавляются inline-кнопки: «Подробнее» и «Изменить статус»

### Уведомления пользователю

- Отправляются только если в payload есть `telegram_id`
- Новый заказ — приветственное сообщение
- Смена статуса — информация о новом статусе с эмодзи и комментарием (если есть)
- К сообщению добавляются inline-кнопки: «Подробнее» и «Чат по заказу»

## Структура проекта

```
src/notifications_worker/
├── app.py                # Celery app
├── celeryconfig.py       # Конфигурация Celery
├── __main__.py           # Entrypoint для python -m
├── domain/
│   ├── entities.py       # Pydantic-модели (NotificationsOrderEntity)
│   └── enums.py          # OrderStatus, DeliveryMethod
├── infra/
│   ├── settings.py       # Настройки из .env
│   └── telegram/
│       ├── client.py     # HTTP-клиент Telegram API
│       ├── errors.py     # Исключения Telegram
│       ├── keyboards.py  # Inline-клавиатуры
│       └── models.py     # Telegram-модели
├── services/
│   ├── dispatcher.py     # Диспетчеризация уведомлений
│   └── templates.py      # Шаблоны сообщений
└── tasks/
    └── notifications.py  # Celery tasks
```

## Важные замечания

- **Сериализация** — payload должен быть JSON-serializable. `Decimal` передавайте как строку (`mode="json"` в Pydantic).
- **Visibility timeout** — настройте `CELERY_VISIBILITY_TIMEOUT` больше, чем максимальное время выполнения задачи.
- **Идемпотентность** — для включения ретраев рекомендуется передавать уникальный `event_id` в payload.
- **Обработка ошибок** — при ошибках Telegram API (rate limit, 5xx) задача автоматически повторяется (до 5 раз с интервалом 10 сек).

## Разработка

```bash
# Установка dev-зависимостей
pip install -e ".[dev]"

# Линтинг
ruff check src/
ruff format src/

# Type checking
mypy src/
```

## Требования

- Python ≥ 3.12
- Redis
- Telegram Bot Token