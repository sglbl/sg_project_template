"""Object storage client for RustFS, MinIO, and AWS S3 implementing IStorageRepository."""

import os
import shutil
from pathlib import Path
from loguru import logger

from src.config import settings
from src.domain.repo_interfaces.storage_repository import IStorageRepository


class S3StorageProvider(IStorageRepository):
    """Storage provider targeting S3-compatible endpoints (RustFS, MinIO, S3) with local fallback."""

    def __init__(
        self,
        endpoint_url: str = "",
        access_key: str = "",
        secret_key: str = "",
        bucket_name: str = "artifacts",
    ) -> None:
        self.endpoint_url = endpoint_url or settings.RUSTFS_ENDPOINT_URL or settings.MINIO_ENDPOINT_URL
        self.access_key = access_key or settings.RUSTFS_ACCESS_KEY or settings.AWS_ACCESS_KEY_ID
        self.secret_key = secret_key or settings.RUSTFS_SECRET_KEY or settings.AWS_SECRET_ACCESS_KEY
        self.bucket_name = bucket_name
        self.local_root = Path(settings.DATA_RAW_DIR).parent

    def upload_file(self, local_path: str, remote_key: str) -> str:
        """Upload a local file to storage bucket or local fallback path."""
        if not os.path.exists(local_path):
            raise FileNotFoundError(f"Source file not found: {local_path}")

        try:
            # S3 client attempt if boto3 is installed
            import boto3
            s3_client = boto3.client(
                "s3",
                endpoint_url=self.endpoint_url,
                aws_access_key_id=self.access_key,
                aws_secret_access_key=self.secret_key,
            )
            s3_client.upload_file(local_path, self.bucket_name, remote_key)
            dest_url = f"s3://{self.bucket_name}/{remote_key}"
            logger.info(f"Uploaded {local_path} to S3/RustFS at {dest_url}")
            return dest_url
        except Exception as e:
            logger.warning(f"S3/RustFS upload failed: {e}. Falling back to local storage.")
            dest_path = self.local_root / "remote_cache" / remote_key
            dest_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(local_path, dest_path)
            return str(dest_path)

    def download_file(self, remote_key: str, local_path: str) -> str:
        """Download remote key to local path."""
        out_path = Path(local_path)
        out_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            import boto3
            s3_client = boto3.client(
                "s3",
                endpoint_url=self.endpoint_url,
                aws_access_key_id=self.access_key,
                aws_secret_access_key=self.secret_key,
            )
            s3_client.download_file(self.bucket_name, remote_key, str(out_path))
            logger.info(f"Downloaded s3://{self.bucket_name}/{remote_key} to {local_path}")
            return str(out_path)
        except Exception as e:
            logger.warning(f"S3/RustFS download failed: {e}. Searching local cache.")
            cached = self.local_root / "remote_cache" / remote_key
            if cached.exists():
                shutil.copy2(cached, out_path)
                return str(out_path)
            raise FileNotFoundError(f"Remote key '{remote_key}' not found locally or in remote storage")

    def exists(self, remote_key: str) -> bool:
        """Check if remote object exists."""
        try:
            import boto3
            s3_client = boto3.client(
                "s3",
                endpoint_url=self.endpoint_url,
                aws_access_key_id=self.access_key,
                aws_secret_access_key=self.secret_key,
            )
            s3_client.head_object(Bucket=self.bucket_name, Key=remote_key)
            return True
        except Exception:
            cached = self.local_root / "remote_cache" / remote_key
            return cached.exists()
