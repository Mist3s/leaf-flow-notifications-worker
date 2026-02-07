import logging

from notifications_worker.domain.entities import ImageVariantResult
from notifications_worker.infra.cloudinary.client import (
    VARIANTS_CONFIG,
    delete_from_cloudinary,
    download_variant,
    fetch_and_transform,
    parse_eager_results,
)

logger = logging.getLogger(__name__)


def process_image_with_cloudinary(
    original_url: str,
    original_key: str,
    product_id: str,
    image_id: int,
) -> list[tuple[bytes, ImageVariantResult]]:
    """
    Обработать изображение через Cloudinary.

    1. Cloudinary скачивает оригинал по URL и создаёт варианты
    2. Worker скачивает готовые варианты из Cloudinary CDN
    3. Удаляет временное изображение из Cloudinary

    Args:
        original_url: Публичный URL оригинала
        original_key: Ключ S3 для формирования путей вариантов
        product_id: ID продукта
        image_id: ID изображения

    Returns:
        Список кортежей (данные_варианта, метаданные)
    """
    public_id = f"temp/leaf-flow/{product_id}/{image_id}"

    try:
        # 1. Cloudinary fetch + transform
        logger.info("Processing image via Cloudinary: %s", original_url)
        upload_result = fetch_and_transform(original_url, public_id)

        eager = upload_result.get("eager")
        if not eager or not isinstance(eager, list):
            msg = "Cloudinary eager transformations failed"
            raise ValueError(msg)

        # 2. Парсим результаты
        eager_results = parse_eager_results(eager)

        # 3. Скачиваем каждый вариант из Cloudinary CDN
        results: list[tuple[bytes, ImageVariantResult]] = []

        # Извлекаем базовый путь из original_key
        # public/products/pu-erh/123/original.jpg -> public/products/pu-erh/123
        base_path = "/".join(original_key.rsplit("/", 1)[:-1])

        for variant_name in VARIANTS_CONFIG:
            if variant_name not in eager_results:
                logger.warning("Variant %s not in eager results", variant_name)
                continue

            variant_info = eager_results[variant_name]

            logger.info("Downloading %s from Cloudinary CDN", variant_name)
            variant_data = download_variant(str(variant_info["url"]))

            storage_key = f"{base_path}/{variant_name}.webp"

            meta = ImageVariantResult(
                variant=variant_name,
                storage_key=storage_key,
                format="webp",
                width=int(variant_info["width"]),  # type: ignore[arg-type]
                height=int(variant_info["height"]),  # type: ignore[arg-type]
                byte_size=len(variant_data),
            )

            results.append((variant_data, meta))
            logger.info(
                "Prepared %s: %dx%d, %d bytes",
                variant_name,
                meta.width,
                meta.height,
                meta.byte_size,
            )

        return results

    finally:
        # 4. Удаляем из Cloudinary (освобождаем квоту)
        delete_from_cloudinary(public_id)
