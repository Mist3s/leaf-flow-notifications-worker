import logging

from celery import shared_task

from notifications_worker.domain.entities import ImageUploadedEntity
from notifications_worker.infra.leafflow.client import leafflow_client
from notifications_worker.infra.s3.client import s3_client
from notifications_worker.services.image_processor import process_image_with_cloudinary

logger = logging.getLogger(__name__)


@shared_task(
    name="images.create_variants",
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_backoff_max=300,
    retry_kwargs={"max_retries": 3},
)
def create_variants(self, payload: dict) -> dict:  # type: ignore[type-arg]
    """
    Создать варианты изображения через Cloudinary.

    Flow:
    1. Cloudinary fetch оригинал по URL + eager transformations
    2. Скачать варианты (thumb, md, lg) из Cloudinary CDN
    3. Загрузить варианты в S3
    4. Сохранить метаданные через LeafFlow API
    5. Удалить временное изображение из Cloudinary

    Args:
        payload: Данные события ImageUploadedEvent

    Returns:
        {"image_id": 123, "variants_created": ["thumb", "md", "lg"]}
    """
    entity = ImageUploadedEntity.model_validate(payload)

    logger.info(
        "[image_id=%d] Starting processing for product %s",
        entity.image_id,
        entity.product_id,
    )

    # 1-2. Обрабатываем через Cloudinary
    variants = process_image_with_cloudinary(
        original_url=entity.original_url,
        original_key=entity.original_key,
        product_id=entity.product_id,
        image_id=entity.image_id,
    )

    if not variants:
        msg = "No variants created"
        raise ValueError(msg)

    # 3. Загружаем варианты в S3
    for data, meta in variants:
        logger.info("[image_id=%d] Uploading to S3: %s", entity.image_id, meta.storage_key)
        s3_client.upload(
            key=meta.storage_key,
            data=data,
            content_type="image/webp",
        )

    # 4. Сохраняем метаданные через LeafFlow API
    for _, meta in variants:
        leafflow_client.save_image_variant(entity.image_id, meta)

    created_variants = [meta.variant for _, meta in variants]
    logger.info(
        "[image_id=%d] Successfully created variants: %s",
        entity.image_id,
        created_variants,
    )

    return {
        "image_id": entity.image_id,
        "variants_created": created_variants,
    }
