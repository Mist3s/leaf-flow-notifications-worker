import logging

import httpx

from notifications_worker.domain.entities import ImageVariantResult
from notifications_worker.infra.settings import settings as leafflow_settings

logger = logging.getLogger(__name__)


class LeafFlowClient:
    """Клиент для LeafFlow Internal API."""

    def __init__(self) -> None:
        self._base_url = leafflow_settings.api_base_url.rstrip("/")
        self._token = leafflow_settings.internal_token

    def _headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self._token}",
            "Content-Type": "application/json",
        }

    def save_image_variant(self, image_id: int, variant: ImageVariantResult) -> None:
        """
        Сохранить метаданные варианта изображения.

        POST /v1/internal/images/{image_id}/variants
        """
        url = f"{self._base_url}/v1/internal/images/{image_id}/variants"

        payload = {
            "variant": variant.variant,
            "storage_key": variant.storage_key,
            "format": variant.format,
            "width": variant.width,
            "height": variant.height,
            "byte_size": variant.byte_size,
        }

        with httpx.Client(timeout=30) as client:
            response = client.post(url, json=payload, headers=self._headers())
            response.raise_for_status()

        logger.info("Saved variant %s for image %d", variant.variant, image_id)


leafflow_client = LeafFlowClient()
