"""impacted_area_identification_processor main"""

import argparse
import os

from dotenv import load_dotenv
from geosyspy.geosys import Env, Region
from geosyspy.utils.jwt_validator import check_token_validity

from impacted_areas_identification_processor.cloud_storage_provider import (
    CloudStorageProvider,
)
from impacted_areas_identification_processor.processor import (
    ImpactedAreasIdentificationProcessor,
)
from utils.file_utils import load_input_data


def main(
    input_path=None,
    bearer_token=None,
    aws_s3_bucket=None,
    metrics: bool = False,
    entity_id=None,
    cloud_storage_provider=CloudStorageProvider.AWS,
):
    """_summary_

    Args:
        input_path (str, optional): path of the input file. Defaults to None.
        bearer_token (str, optional): bearer token to connect ro geosys API. Defaults to None.
        aws_s3_bucket (str, optional): bucket name to store the output file. Defaults to None.
        metrics (bool, optional): Whether to display bandwidth and time metrics. Defaults to False.
        entity_id(str, optional): Identification of the entity. Defaults to None.
        cloud_storage_provider (CloudStorageProvider, optional): The cloud storage provider to use
            for storing the output file. It should be one of the values from the CloudStorageProvider enum
            (AWS or AZURE). Defaults to CloudStorageProvider.AWS.


    Returns:
        output_schema: an instance of output schema
    """
    load_dotenv()
    environment = os.getenv("APP_ENVIRONMENT", "local")

    if environment == "local":
        input_data = load_input_data(os.getenv("INPUT_JSON_PATH"))

    elif environment in ["integration", "validation", "production"]:
        if not input_path:
            raise ValueError(
                f"No input path provided in the '{environment}' environment."
            )
        input_data = load_input_data(input_path)
    else:
        raise ValueError(f"Unrecognized environment: {environment}")

    api_client_id = os.getenv("API_CLIENT_ID")
    api_client_secret = os.getenv("API_CLIENT_SECRET")
    api_username = os.getenv("API_USERNAME")
    api_password = os.getenv("API_PASSWORD")
    public_certificate_key = os.getenv("CIPHER_CERTIFICATE_PUBLIC_KEY")
    if public_certificate_key is not None:
        public_certificate_key = public_certificate_key.replace("\\n", "\n")

    # Check token validity
    if bearer_token and (
        public_certificate_key is not None
        and not check_token_validity(bearer_token, public_certificate_key)
    ):
        raise ValueError("Not Authorized")

    processor = ImpactedAreasIdentificationProcessor(
        input_data=input_data,
        client_id=api_client_id,
        client_secret=api_client_secret,
        username=api_username,
        password=api_password,
        enum_env=Env.PROD,
        enum_region=Region.NA,
        bearer_token=bearer_token,
        entity_id=entity_id,
        metrics=metrics,
        cloud_storage_provider=cloud_storage_provider,
        aws_s3_bucket=aws_s3_bucket,
    )

    result = processor.trigger()
    print(f"result: {result}")
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--input_path", type=str, help="Path to the input data", default=None
    )
    parser.add_argument(
        "--cloud_storage_provider",
        type=CloudStorageProvider,
        help="Cloud Storage Provider",
        default=CloudStorageProvider.AWS,
    )
    parser.add_argument(
        "--bearer_token", type=str, help="Geosys Api bearer token", default=None
    )
    parser.add_argument(
        "--aws_s3_bucket", type=str, help="AWS S3 Bucket name", default=None
    )
    parser.add_argument(
        "--metrics", type=bool, help="Display bandwitdh & time metrics ", default=False
    )
    parser.add_argument(
        "--entity_id",
        type=str,
        help="Provide an entity_id value added to the zarr output file",
        default=None,
    )
    args = parser.parse_args()

    main(
        args.input_path,
        args.bearer_token,
        args.aws_s3_bucket,
        args.metrics,
        args.entity_id,
        args.cloud_storage_provider,
    )
