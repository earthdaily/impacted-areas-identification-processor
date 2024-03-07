""" Processor class """

import os
import time
import warnings
from datetime import datetime
from typing import List, Optional, Tuple

import numpy as np
import pandas as pd
import psutil
import xarray as xr
from byoa.telemetry.log_manager.log_manager import LogManager
from dateutil.relativedelta import relativedelta
from geosyspy import Geosys
from geosyspy.utils.constants import Env, Region, SatelliteImageryCollection
from pyproj import Geod
from shapely import wkt
from xarray import DataArray

from impacted_areas_identification_processor.cloud_storage_provider import CloudStorageProvider
from impacted_areas_identification_processor.utils import (
    check_cloud_storage_provider_credentials,
    dataset_to_zarr_format,
    delete_local_directory,
    get_enum_member_from_name,
    upload_to_cloud_storage,
)
from impacted_areas_identification_processor.vegetation_index import VegetationIndex
from schemas.output_schema import Metrics, OutputModel, Results
from utils.file_utils import validate_data

warnings.simplefilter(action="ignore", category=UserWarning)
logger = LogManager.get_instance()


class ImpactedAreasIdentificationProcessor:
    """ImpactedAreasIdentificationProcessor is the main client class processor to build the impacted area datacube output

    `client = Geosys(api_client_id, api_client_secret, api_username, api_password, env, region)`

    Parameters:
        input_data: dict of input data
        enum_env: 'Env.PROD' or 'Env.PREPROD'
        enum_region: 'Region.NA'
        priority_queue: 'realtime' or 'bulk'
        bearer_token: optional geosys identity server token to access geosys api
        entity_id: optional entity id to build the output path
        metrics: bool to provie metrics info in output (bandwitdh, duration)
        cloud_storage_provider: AWS S3/Azure Blob Storage
        clean_local_file: keep or delete temporary local file (zarr file)
    """

    def __init__(
        self,
        input_data,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
        bearer_token: Optional[str] = None,
        entity_id: Optional[str] = None,
        aws_s3_bucket: Optional[str] = None,
        enum_env: Env = Env.PROD,
        enum_region: Region = Region.NA,
        priority_queue: str = "realtime",
        metrics: bool = False,
        cloud_storage_provider: CloudStorageProvider = CloudStorageProvider.AWS,
        clean_local_file=True,
    ):
        validate_data(input_data, "input")
        self.input_data = input_data
        self.priority_queue: str = priority_queue
        self.__client: Geosys = Geosys(
            client_id,
            client_secret,
            username,
            password,
            enum_env,
            enum_region,
            priority_queue,
            bearer_token,
        )
        self.entity_id = entity_id
        self.metrics = metrics
        self.cloud_storage_provider = cloud_storage_provider
        self.aws_s3_bucket = aws_s3_bucket
        self.clean_local_file = clean_local_file
        self.zarr_path = None

    def prepare_data(self):
        """data preparation"""

        # Check if cloud storage provider credentials have been set
        check_cloud_storage_provider_credentials(self.cloud_storage_provider)
        logger.info("data_prepared")

    def predict(self, input_data):
        """
        predict data
        Args:
            input_data (dict): dict of input data

        Returns:
        (str,str,str,DataArray)
        """
        input_data_event_date = datetime.strptime(
            input_data["parameters"]["eventDate"], "%Y-%m-%d"
        ).date()
        event_date = datetime(
            input_data_event_date.year,
            input_data_event_date.month,
            input_data_event_date.day,
        )

        vi_before_event_date, vi_after_event_date, vi_difference_filtered = (
            self.identify_vi_impacted_area_based_on_map_reference(
                input_data["parameters"]["polygon"],
                event_date,
                input_data["parameters"]["minDuration"],
                input_data["parameters"]["threshold"],
                get_enum_member_from_name(VegetationIndex, input_data["indicator"]),
            )
        )

        impacted_area, impacted_area_percentage = self.calculate_impacted_area(
            input_data["parameters"]["polygon"], vi_difference_filtered
        )

        before_event_date = vi_before_event_date.time.values
        after_event_date = vi_after_event_date.time.values
        if isinstance(before_event_date, np.ndarray) or before_event_date.size > 1:
            before_event_date = before_event_date[-1]
        if isinstance(after_event_date, np.ndarray) or after_event_date.size > 1:
            after_event_date = after_event_date[0]

        before_event_date = f"{pd.DatetimeIndex([before_event_date])[0].year}-{pd.DatetimeIndex([before_event_date])[0].month}-{pd.DatetimeIndex([before_event_date])[0].day}"
        after_event_date = f"{pd.DatetimeIndex([after_event_date])[0].year}-{pd.DatetimeIndex([after_event_date])[0].month}-{pd.DatetimeIndex([after_event_date])[0].day}"
        impacted_area_percentage = f"{impacted_area_percentage:.2f} %"
        impacted_area = f"{impacted_area:12.3f} m²"

        return (
            before_event_date,
            after_event_date,
            impacted_area_percentage,
            impacted_area,
            vi_difference_filtered,
        )

    def trigger(self):
        """trigger the processor
        Returns:
            output_schema object
        """
        logger.info("Processor triggered")
        start_time = time.time()

        bandwidth_init = psutil.net_io_counters().bytes_sent + psutil.net_io_counters().bytes_recv

        self.prepare_data()
        (
            before_event_date,
            after_event_date,
            impacted_area_percentage,
            impacted_area,
            datacube,
        ) = self.predict(self.input_data)
        datacube = datacube.load()
        zarr_path = dataset_to_zarr_format(datacube)

        if self.entity_id:
            # Rename zarr file
            new_name = f"{self.entity_id}_{os.path.basename(zarr_path)}"
            new_path = os.path.join(os.path.dirname(zarr_path), new_name)
            os.rename(zarr_path, new_path)
            zarr_path = new_path

        # bandwidth use retrieval
        bandwidth_generation = (
            psutil.net_io_counters().bytes_sent + psutil.net_io_counters().bytes_recv
        )

        # upload zarr file on the chosen cloud storage provider
        cloud_storage_link = upload_to_cloud_storage(
            self.cloud_storage_provider, zarr_path, self.aws_s3_bucket
        )

        self.zarr_path = zarr_path
        if self.clean_local_file:
            # delete tmp files
            delete_local_directory(zarr_path)

        # bandwidth_upload retrieval
        bandwidth_upload = (
            psutil.net_io_counters().bytes_sent + psutil.net_io_counters().bytes_recv
        )

        # format result
        result = OutputModel(
            storage_links=cloud_storage_link,
            results=Results(
                after_event_date=after_event_date,
                before_event_date=before_event_date,
                impacted_area_percentage=impacted_area_percentage,
                impacted_area=impacted_area,
            ),
        )

        # adding metrics
        if self.metrics:
            metrics = Metrics(
                execution_time=f"{int(np.round((time.time() - start_time) / 60))} minutes {int(np.round(np.round((time.time() - start_time)) % 60))} seconds",
                data_generation_network_use=f"{np.round((bandwidth_generation - bandwidth_init) / 1024. / 1024. / 1024. * 8, 3)} Gb",
                data_upload_network_use=f"{np.round((bandwidth_upload - bandwidth_generation) / 1024. / 1024. / 1024. * 8, 3)} Gb",
            )
            result.metrics = metrics

        # validate output data
        # validate_data(result.model_dump(), "output")

        return result.model_dump()

    def get_image_coverage_info_based_on_map_reference(self, polygon: str, event_date: datetime):
        """
        Retrieves image coverage information and references based on a map reference and event date.

        Parameters:
        - geometry: The geometry representing the map reference for the image coverage.
        - event_date: The event date for which the image coverage information is retrieved.

        Returns:
        - coverage_info_df: A DataFrame containing the image coverage information.
        - images_references: A list of image references corresponding to the coverage.
        """
        start_date = event_date + relativedelta(months=-6)
        end_date = event_date + relativedelta(months=6)
        end_date = min(end_date, datetime.today())
        return self.__client.get_satellite_coverage_image_references(
            polygon,
            start_date,
            end_date,
            collections=[
                SatelliteImageryCollection.SENTINEL_2,
                SatelliteImageryCollection.LANDSAT_8,
                SatelliteImageryCollection.LANDSAT_9,
            ],
        )

    def find_nearest_dates(
        self, event_date: datetime, min_duration: int, date_list: List[datetime]
    ) -> dict[str, datetime]:
        """
        Finds the nearest superior and inferior dates to the given event date from a list of dates.

        Parameters:
        - event_date: The event date for which the nearest dates are determined.
        - min_duration: Minimum number of days between dates to find the nearest dates.
        - date_list: A list of dates to search for the nearest superior and inferior dates.

        Returns:
        - dict: A dictionary containing the nearest superior and inferior dates.
            - "before_event_date": The nearest inferior date to the event date.
            - "after_event_date": The nearest superior date to the event date.
        """

        list_inferior = filter(lambda x: x < event_date.date(), date_list)
        nearest_superior = min(filter(lambda x: x > event_date.date(), date_list))

        for date_before in list_inferior:
            difference = nearest_superior - date_before
            if difference.days >= min_duration:
                nearest_inferior = date_before
                break
        if "nearest_inferior" not in locals():
            nearest_inferior = max(filter(lambda x: x < event_date.date(), date_list))
        print(nearest_inferior, nearest_superior)
        return {
            "before_event_date": nearest_inferior,
            "after_event_date": nearest_superior,
        }

    def get_vi_image_time_series(
        self,
        polygon: str,
        start_date: datetime,
        end_date: datetime,
        indicator: VegetationIndex,
    ) -> DataArray:
        """
        Retrieves the time series of the specified vegetation index satellite images within the specified time range and geometry.

        Parameters:
        - geometry (str): The geometry representing the area of interest for the VI image time series.
        - start_date (datetime): The start date of the time range for which the VI images are retrieved.
        - end_date (datetime): The end date of the time range for which the VI images are retrieved.
        - indicator (VegetationIndex); vegetation index

        Returns:
        - vi_image_time_series: The time series of the specified vegetation index satellite images within the specified time range and geometry.
        """

        vi_image_time_series = self.__client.get_satellite_image_time_series(
            polygon,
            start_date,
            end_date,
            collections=[
                SatelliteImageryCollection.SENTINEL_2,
                SatelliteImageryCollection.LANDSAT_8,
                SatelliteImageryCollection.LANDSAT_9,
            ],
            indicators=[indicator],
        )

        if len(vi_image_time_series.coords.keys()) == 0:
            raise ValueError(f"No {indicator} images time series found !")
        return vi_image_time_series

    def calculate_and_filter_vi_difference_by_threshold(
        self,
        vi_index_for_image_before_event_date,
        vi_index_for_image_after_event_date,
        threshold,
    ) -> xr.DataArray:
        """
        Calculates the difference between two Vegetation Index (VI) images and filters the result based on a threshold value.

        This function first computes the difference between the VI after the event date and the VI before the event date.
        It filters this difference to keep only those pixels where the difference is less than the provided threshold.

        Parameters:
        - vi_index_for_image_before_event_date: A xarray representing the VI image before the event date.
        - vi_index_for_image_after_event_date: A xarray representing the VI image after the event date.
        - threshold: The threshold value for filtering the VI difference. Only pixels with a VI difference less than this threshold are kept in the output.

        Returns:
        - vi_difference_result: A xarray representing the filtered VI difference.
        """
        ds_after = vi_index_for_image_after_event_date.squeeze().drop(
            [var for var in ["time", "band"] if var in vi_index_for_image_after_event_date.coords]
        )
        ds_before = vi_index_for_image_before_event_date.squeeze().drop(
            [var for var in ["time", "band"] if var in vi_index_for_image_before_event_date.coords]
        )
        vi_difference_result = (ds_after - ds_before).where(
            ~np.logical_or(np.isnan(ds_before), np.isnan(ds_after))
        )
        vi_difference_result = vi_difference_result.assign_coords(
            geometry_size_px=sum(sum(vi_difference_result.notnull())).values
        )
        return vi_difference_result.where(vi_difference_result < threshold)

    def identify_vi_impacted_area_based_on_map_reference(
        self,
        polygon: str,
        event_date: datetime,
        min_duration: int,
        threshold: float,
        indicator: VegetationIndex,
    ) -> tuple[DataArray, DataArray, DataArray]:
        """
        Identifies the vegetation index (VI) impacted area based on a map reference.

        Parameters:
        - geometry (str): The geometry representing the geometry in Well-Known Text (WKT) format.
        - event_date (datetime): The event date for which the analysis is performed.
        - min_duration (int) : Minimum days number between two dates to perform the analysis.
        - threshold (float): The threshold value used for filtering the vegetation index difference.
            indicator (VegetationIndex): The vegetation index.

        Returns:
        - indicator (VegetationIndex): The vegetation index.
        - vi_image_before_event_date (xArray): The VI image before the event date.
        - vi_image_after_event_date (xArray): The VI  image after the event date.
        - impacted_area (xArray): The filtered VI difference based on the provided threshold.


        Note:
        This method relies on other helper methods to obtain the necessary data for the analysis.

        Usage:
        1. Call the method `identify_vi_impacted_area_based_on_map_reference` on an instance of the ImpactedAreasIdentificator class.
        2. Provide the geometry representing the map reference.
        3. Specify the event date for analysis.
        4. Set the threshold value for filtering the vegetation index difference.
        5. Retrieve the resulting VI images and the impacted area.

        Example:
        geometry = "example_polygon"
        event_date = datetime.datetime(2023, 5, 15)
        threshold = 0.5

        # Call the method to identify VI impacted area
        vi_image_before, vi_image_after, impacted_area = client.identify_vi_impacted_area_based_on_map_reference(geometry, event_date, threshold, indicator)
        """

        coverage_info_df, images_references = self.get_image_coverage_info_based_on_map_reference(
            polygon, event_date
        )
        image_date_list = pd.to_datetime(coverage_info_df["image.date"]).dt.date
        nearest_event_date = self.find_nearest_dates(event_date, min_duration, image_date_list)

        vi_images_nearest_event_date = self.get_vi_image_time_series(
            polygon,
            nearest_event_date["before_event_date"],
            nearest_event_date["after_event_date"],
            indicator.value,
        )

        vi_image_before_event_date = vi_images_nearest_event_date.sel(
            time=str(nearest_event_date["before_event_date"])
        )[indicator.value]
        vi_image_after_event_date = vi_images_nearest_event_date.sel(
            time=str(nearest_event_date["after_event_date"])
        )[indicator.value]
        impacted_area = self.calculate_and_filter_vi_difference_by_threshold(
            vi_image_before_event_date, vi_image_after_event_date, threshold
        )

        return vi_image_before_event_date, vi_image_after_event_date, impacted_area

    def calculate_geometry_area(self, polygon: str) -> float:
        """
        Calculates the area of a given geometry represented by a geometry in WKT format.

        Parameters:
        - geometry (str): The geometry string representing the geometry for which the area is calculated.

        Returns:
        - area (float): The area of the geometry.
        """
        geod = Geod(ellps="WGS84")
        poly = wkt.loads(polygon)
        return abs(geod.geometry_area_perimeter(poly)[0])

    def calculate_impacted_area(
        self, polygon: str, impacted_area: DataArray
    ) -> Tuple[float, float]:
        """
        Calculates the impacted area based on a geometry and an impacted area DataFrame.

        Parameters:
        - geometry (str): The geometry string representing the geometry of the impacted area.
        - impacted_area (DataArray): A DataFrame representing the impacted area.

        Returns:
        - impacted_area (float): The calculated impacted area.
        - impacted_area_percentage (float): The percentage of the geometry covered by the impacted area.
        """
        geometry_area = self.calculate_geometry_area(polygon)
        impacted_area_percentage = (
            sum(sum(impacted_area.notnull())) / impacted_area.geometry_size_px.values
        ) * 100
        impacted_area = geometry_area * impacted_area_percentage / 100
        return impacted_area, impacted_area_percentage
