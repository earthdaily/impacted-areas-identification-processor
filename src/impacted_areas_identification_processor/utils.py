"""utils class"""

import json
import os
import shutil
import tempfile
from datetime import datetime

import xarray
from byoa.cloud_storage import aws_s3, azure_blob_storage
from byoa.telemetry.log_manager import log_manager
from byoa.telemetry.log_manager.log_manager import LogManager
from shapely import wkt
from shapely.geometry import shape

from impacted_areas_identification_processor.cloud_storage_provider import (
    CloudStorageProvider,
)

logger_manager = LogManager.get_instance()


def dataset_to_zarr_format(dataset: xarray.Dataset):
    """
    Save a xarray.Dataset as zarr format in a temporary folder.
    Output zarr path : "Year-Month-Day_Hour-Minute-Second_impacted-area-datacube.zarr"

    Args:
        - dataset: the Dataset to save

    Returns:
        The complete zarr path
    """
    logger = log_manager.LogManager.get_instance()

    # Make a valid path whatever the OS
    zarr_path = os.path.join(
        tempfile.gettempdir(),
        datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + "_impacted-area-datacube.zarr",
    )
    logger.info("ImpactedArea:save_dataset_to_temporary_zarr: path is " + zarr_path)

    # save dataset and return complete zarr path
    dataset.to_zarr(zarr_path)
    return zarr_path


def is_valid_wkt(geometry):
    """check if the geometry is a valid WKT
    Args:
        geometry : A string representing the geometry

    Returns:
        boolean (True/False)

    """
    try:
        wkt.loads(geometry)
        return True
    except ValueError:
        return False


def convert_to_wkt(geometry):
    """convert a geometry (WKT or geoJson) to WKT
    Args:
        geometry : A string representing the geometry (WKT or geoJson)

    Returns:
        a valid WKT

    """

    try:
        # Check if the geometry is a valid WKT
        if is_valid_wkt(geometry):
            # Return the WKT
            return geometry
        # Check if the geometry is a valid GeoJSON
        geojson_data = json.loads(geometry)
        geom = shape(geojson_data)
        return geom.wkt
    except ValueError as e:
        # Geometry is not a valid GeoJSON
        raise ValueError(f"Geometry is not a valid WKT or GeoJSON: {e}") from e


def upload_to_cloud_storage(
    cloud_storage_provider: CloudStorageProvider,
    zarr_path: str,
    aws_s3_bucket: str,
):
    """
    Uploads data to the specified cloud storage provider.

    Args:
        cloud_storage_provider (CloudStorageProvider): The cloud storage provider (AWS or Azure).
        zarr_path (str): The path to the data to be uploaded.
        aws_s3_bucket (str, optional): The AWS S3 bucket name. Required only if cloud_storage_provider is AWS.

    Returns:
        dict or None: A dictionary containing the storage link if the upload is successful,
                      otherwise None.

    Notes:
        This function uploads data to the specified cloud storage provider based on the provider type.
        If the upload fails, it returns None.
    """
    try:
        if cloud_storage_provider == CloudStorageProvider.AWS:
            if aws_s3_bucket is None:
                aws_s3_bucket = os.getenv("AWS_BUCKET_NAME")
            if aws_s3.write_folder_to_aws_s3(zarr_path, aws_s3_bucket):
                logger_manager.info("Analytics DataCube uploaded to AWS S3")
                return aws_s3.get_s3_uri_path(zarr_path, aws_s3_bucket)
        elif cloud_storage_provider == CloudStorageProvider.AZURE:
            if azure_blob_storage.upload_directory_to_azure_blob_storage(zarr_path):
                logger_manager.info("Analytics DataCube uploaded to Azure Blob Storage")
                return azure_blob_storage.get_azure_blob_url_path(zarr_path)

    except Exception as exc:
        logger_manager.error(
            f"Error while uploading folder to {cloud_storage_provider.value}: {exc}"
        )
        raise RuntimeError(
            f"Error while uploading folder to {cloud_storage_provider.value}: {exc}"
        ) from exc


def delete_local_directory(path: str):
    """
    Delete a local directory if it exists.

    Args:
        path (str): The path of the directory to delete.
    """
    # Remove local csv file
    if os.path.exists(path):
        logger_manager.info("Delete local directory after upload")
        shutil.rmtree(path)
    else:
        logger_manager.info("File not present.")


def check_cloud_storage_provider_credentials(
    cloud_storage_provider: CloudStorageProvider,
):
    """
    Check the credentials for the specified cloud storage provider.

    Args:
        cloud_storage_provider (CloudStorageProvider): The cloud storage provider (AWS or Azure).

    Raises:
        HTTPException: If the credentials for the specified cloud storage provider are missing.
    """
    # Check Azure credentials
    if cloud_storage_provider == CloudStorageProvider.AZURE:
        if not (
            os.getenv("AZURE_ACCOUNT_NAME")
            and os.getenv("AZURE_SAS_CREDENTIAL")
            and os.getenv("AZURE_BLOB_CONTAINER_NAME")
        ):
            raise ValueError("Missing Azure credentials")

    # Check AWS credentials
    if cloud_storage_provider == CloudStorageProvider.AWS:
        if not (os.getenv("AWS_ACCESS_KEY_ID") and os.getenv("AWS_SECRET_ACCESS_KEY")):
            raise ValueError("Missing AWS credentials")


def get_enum_member_from_name(enum_class, name):
    """
    Retrieves an enum member by its name from an enumerated class.

    Args:
        enum_class (type): The enumerated class to retrieve the member from.
        name (str): The name of the enum member to retrieve.

    Returns:
        Enum: The enum member corresponding to the specified name.

    Raises:
        ValueError: If no enum member matching the name is found.
    """
    for member in enum_class.__members__.values():
        if member.name == name:
            return member
    raise ValueError(f"No matching enum member found for name {name}")
