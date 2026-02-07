from io import BytesIO

import boto3
from botocore.config import Config

from notifications_worker.infra.settings import settings as s3_settings


class S3Client:
    """Клиент для загрузки файлов в S3."""

    def __init__(self) -> None:
        self._client = boto3.client(
            "s3",
            endpoint_url=s3_settings.s3_endpoint,
            aws_access_key_id=s3_settings.s3_access_key,
            aws_secret_access_key=s3_settings.s3_secret_key,
            region_name=s3_settings.s3_region,
            use_ssl=s3_settings.s3_use_ssl,
            config=Config(signature_version="s3v4"),
        )
        self._bucket = s3_settings.s3_bucket

    def upload(self, key: str, data: bytes, content_type: str) -> None:
        """Загрузить файл в S3."""
        self._client.put_object(
            Bucket=self._bucket,
            Key=key,
            Body=BytesIO(data),
            ContentType=content_type,
        )


s3_client = S3Client()
