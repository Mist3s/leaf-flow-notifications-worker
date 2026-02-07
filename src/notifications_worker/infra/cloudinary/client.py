import logging

import cloudinary
import cloudinary.uploader
import httpx

from notifications_worker.infra.settings import settings as cloudinary_settings

logger = logging.getLogger(__name__)

# Инициализация Cloudinary
cloudinary.config(
    cloud_name=cloudinary_settings.cloudinary_cloud_name,
    api_key=cloudinary_settings.cloudinary_api_key,
    api_secret=cloudinary_settings.cloudinary_api_secret,
    secure=True,
)

# Конфигурация вариантов
VARIANTS_CONFIG: dict[str, dict[str, int]] = {
    "thumb": {"width": 150, "height": 150, "quality": 80},
    "md": {"width": 600, "height": 600, "quality": 85},
    "lg": {"width": 1200, "height": 1200, "quality": 90},
}


def _build_eager_transformations() -> list[dict[str, object]]:
    """Построить список eager transformations."""
    return [
        {
            "width": cfg["width"],
            "height": cfg["height"],
            "crop": "fit",
            "quality": cfg["quality"],
            "format": "webp",
        }
        for cfg in VARIANTS_CONFIG.values()
    ]


def fetch_and_transform(image_url: str, public_id: str) -> dict[str, object]:
    """
    Cloudinary скачивает изображение по URL и создаёт варианты.

    Args:
        image_url: Публичный URL оригинала в S3
        public_id: Уникальный ID для Cloudinary (temp/leaf-flow/{product_id}/{image_id})

    Returns:
        Результат upload с eager URLs
    """
    logger.info("Cloudinary fetching: %s", image_url)

    result: dict[str, object] = cloudinary.uploader.upload(
        image_url,
        public_id=public_id,
        eager=_build_eager_transformations(),
        eager_async=False,
        resource_type="image",
        overwrite=True,
    )
    return result


def download_variant(url: str) -> bytes:
    """Скачать трансформированный вариант из Cloudinary CDN."""
    with httpx.Client(timeout=60) as client:
        response = client.get(url)
        response.raise_for_status()
        return response.content


def delete_from_cloudinary(public_id: str) -> None:
    """Удалить изображение из Cloudinary после обработки."""
    try:
        cloudinary.uploader.destroy(public_id, resource_type="image")
        logger.info("Deleted from Cloudinary: %s", public_id)
    except Exception:
        logger.warning("Failed to delete from Cloudinary: %s", public_id, exc_info=True)


def parse_eager_results(eager: list[dict[str, object]]) -> dict[str, dict[str, object]]:
    """
    Распарсить результаты eager transformations.

    Returns:
        {"thumb": {"url": "...", "width": 150, "height": 100}, ...}
    """
    results: dict[str, dict[str, object]] = {}
    variant_names = list(VARIANTS_CONFIG.keys())

    for i, item in enumerate(eager):
        if i >= len(variant_names):
            break
        variant_name = variant_names[i]
        results[variant_name] = {
            "url": item["secure_url"],
            "width": item["width"],
            "height": item["height"],
        }

    return results
