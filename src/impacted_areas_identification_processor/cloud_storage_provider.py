"""Available Cloud Storage providers"""

from enum import Enum


class CloudStorageProvider(Enum):
    """
    Available Cloud Storage providers
    """
    AWS = "AWS_S3"
    AZURE = "AZURE_BLOB_STORAGE"
