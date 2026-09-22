"""Domain interface protocol for Object Storage (RustFS / MinIO / S3 / Local)."""

from typing import Protocol


class IStorageRepository(Protocol):
    def upload_file(self, local_path: str, remote_key: str) -> str:
        """Upload a local file to storage and return destination URL/key."""
        ...

    def download_file(self, remote_key: str, local_path: str) -> str:
        """Download a remote file key to local destination path."""
        ...

    def exists(self, remote_key: str) -> bool:
        """Check if remote object exists in storage."""
        ...
