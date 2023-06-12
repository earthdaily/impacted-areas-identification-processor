from typing import Tuple
import pandas as pd
from dateutil.relativedelta import relativedelta
from geosyspy import Geosys
import datetime
from geosyspy.utils.constants import *
from pyproj import Geod
from shapely import wkt
import logging
import sys

from vegetation_index_impacted_areas_identificator.vegetation_index import VegetationIndex

class ImpactedAreasIdentificator:
    """
       ImpactedAreasIdentificator is a class that identifies and analyzes impacted areas based on vegetation index (ex: NDVI).

       Parameters:
       - client_id (str): The client ID used for authentication.
       - client_secret (str): The client secret used for authentication.
       - username (str): The username for authentication.
       - password (str): The password for authentication.
       - enum_env (enumerate): The enumeration representing the environment from which the data are retrieved.
       - enum_region (enumerate): 'Region.NA' or 'Region.EU'
       - priority_queue (str, optional): The priority queue to be used for the analysis ('realtime' or 'bulk'). Defaults to "realtime".

       Usage:
       1. Create an instance of the ImpactedAreasIdentificator class by providing the required parameters.
       2. Use the instance to identify and analyze impacted areas based on the provided parameters.

       Example:
       client_id = "example_client_id"
       client_secret = "example_client_secret"
       username = "example_username"
       password = "example_password"
       enum_env = enumerate(["env1", "env2", "env3"])
       enum_region = enumerate(["region1", "region2", "region3"])

       # Create an instance of ImpactedAreasIdentificator
       client = ImpactedAreasIdentificator(client_id, client_secret, username, password, enum_env, enum_region)

       # Use the instance to identify and analyze impacted areas based on map reference or catalogue Stac
       client.identify_vi_impacted_area_based_on_map_reference()

       """

    def __init__(self, client_id: str,
                 client_secret: str,
                 username: str,
                 password: str,
                 enum_env: enumerate,
                 enum_region: enumerate,
                 priority_queue: str = "realtime",
                 ):

        self.region: str = enum_region.value
        self.env: str = enum_env.value
        self.priority_queue: str = priority_queue
        self.__client: Geosys = Geosys(client_id, client_secret, username, password, enum_env, enum_region,
                                       priority_queue)
        root_logger = logging.getLogger()
        root_logger.setLevel(logging.ERROR)
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(logging.ERROR)
        root_logger.addHandler(handler)

    def identify_vi_impacted_area_based_on_map_reference(self, polygon: str,
                                                         event_date: datetime,
                                                         threshold: float,
                                                         indicator: VegetationIndex):
        """
        Identifies the vegetation index (VI) impacted area based on a map reference.

        Parameters:
        - polygon (str): The polygon representing the geometry in Well-Known Text (WKT) format.
        - event_date (datetime): The event date for which the analysis is performed.
        - threshold (float): The threshold value used for filtering the vegetation index difference.
        - indicator (VegetationIndex); vegetation index

        Returns:
        - vi_image_before_event_date (xArray): The VI image before the event date.
        - vi_image_after_event_date (xArray): The VI  image after the event date.
        - impacted_area (xArray): The filtered VI difference based on the provided threshold.


        Note:
        This method relies on other helper methods to obtain the necessary data for the analysis.

        Usage:
        1. Call the method `identify_vi_impacted_area_based_on_map_reference` on an instance of the ImpactedAreasIdentificator class.
        2. Provide the polygon representing the map reference.
        3. Specify the event date for analysis.
        4. Set the threshold value for filtering the vegetation index difference.
        5. Retrieve the resulting VI images and the impacted area.

        Example:
        polygon = "example_polygon"
        event_date = datetime.datetime(2023, 5, 15)
        threshold = 0.5

        # Call the method to identify VI impacted area
        vi_image_before, vi_image_after, impacted_area = client.identify_vi_impacted_area_based_on_map_reference(polygon, event_date, threshold, indicator)
        """

        coverage_info_df, images_references = self.get_image_coverage_info_based_on_map_reference(polygon, event_date)
        image_date_list = pd.to_datetime(coverage_info_df['image.date']).dt.date
        nearest_event_date = self.find_nearest_dates(event_date.date(), image_date_list)

        vi_images_nearest_event_date = self.get_vi_image_time_series(polygon,
                                                                     nearest_event_date["before_event_date"],
                                                                     nearest_event_date["after_event_date"],
                                                                     indicator)

        vi_image_before_event_date = \
            vi_images_nearest_event_date.sel(time=str(nearest_event_date["before_event_date"]))[indicator]
        vi_image_after_event_date = \
            vi_images_nearest_event_date.sel(time=str(nearest_event_date["after_event_date"]))[indicator]
        impacted_area = self.calculate_and_filter_vi_difference_by_threshold(vi_image_before_event_date,
                                                                             vi_image_after_event_date,
                                                                             threshold)

        return vi_image_before_event_date, vi_image_after_event_date, impacted_area

    def identify_vi_impacted_area_based_on_stac_images(self):
        pass

    def find_nearest_dates(self,
                           event_date: datetime,
                           date_list: [datetime]):
        """
        Finds the nearest superior and inferior dates to the given event date from a list of dates.

        Parameters:
        - event_date: The event date for which the nearest dates are determined.
        - date_list: A list of dates to search for the nearest superior and inferior dates.

        Returns:
        - dict: A dictionary containing the nearest superior and inferior dates.
            - "before_event_date": The nearest inferior date to the event date.
            - "after_event_date": The nearest superior date to the event date.
        """
        nearest_superior = min(filter(lambda x: x > event_date, date_list))
        nearest_inferior = max(filter(lambda x: x < event_date, date_list))
        return {"before_event_date": nearest_inferior, "after_event_date": nearest_superior}

    def get_image_coverage_info_based_on_map_reference(self,
                                                       polygon: str,
                                                       event_date: datetime):
        """
        Retrieves image coverage information and references based on a map reference and event date.

        Parameters:
        - polygon: The polygon representing the map reference for the image coverage.
        - event_date: The event date for which the image coverage information is retrieved.

        Returns:
        - coverage_info_df: A DataFrame containing the image coverage information.
        - images_references: A list of image references corresponding to the coverage.
        """
        start_date = event_date + relativedelta(months=-6)
        end_date = event_date + relativedelta(months=6)
        return self.__client.get_satellite_coverage_image_references(polygon, start_date, end_date,
                                                                     collections=[SatelliteImageryCollection.SENTINEL_2,
                                                                                  SatelliteImageryCollection.LANDSAT_8,
                                                                                  SatelliteImageryCollection.LANDSAT_9])


    def calculate_and_filter_vi_difference_by_threshold(self,
                                                        vi_index_for_image_before_event_date,
                                                        vi_index_for_image_after_event_date,
                                                        threshold):
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
        vi_difference_result = vi_index_for_image_after_event_date.squeeze().drop(
            ['time', 'band']) - vi_index_for_image_before_event_date.squeeze().drop(['time', 'band'])
        return vi_difference_result.where(vi_difference_result < threshold)


    def get_vi_image_time_series(self, polygon: str,
                                 startDate: datetime,
                                 endDate: datetime,
                                 indicator: VegetationIndex):
        """
        Retrieves the time series of the specified vegetation index satellite images within the specified time range and polygon.

        Parameters:
        - polygon (str): The polygon representing the area of interest for the VI image time series.
        - startDate (datetime): The start date of the time range for which the VI images are retrieved.
        - endDate (datetime): The end date of the time range for which the VI images are retrieved.
        - indicator (VegetationIndex); vegetation index

        Returns:
        - vi_image_time_series: The time series of the specified vegetation index satellite images within the specified time range and polygon.
        """

        return self.__client.get_satellite_image_time_series(polygon,
                                                             startDate,
                                                             endDate,
                                                             collections=[SatelliteImageryCollection.SENTINEL_2,
                                                                          SatelliteImageryCollection.LANDSAT_8,
                                                                          SatelliteImageryCollection.LANDSAT_9],
                                                             indicators=[indicator])


    def calculate_geometry_area(self,
                                polygon: str) -> float:
        """
        Calculates the area of a given geometry represented by a polygon in WKT format.

        Parameters:
        - polygon (str): The polygon string representing the geometry for which the area is calculated.

        Returns:
        - area (float): The area of the geometry.
        """
        geod = Geod(ellps="WGS84")
        poly = wkt.loads(polygon)
        return abs(geod.geometry_area_perimeter(poly)[0])

    def calculate_impacted_area(self,
                                polygon: str,
                                impacted_area: pd.DataFrame) -> Tuple[float, float]:
        """
                Calculates the impacted area based on a polygon and an impacted area DataFrame.

                Parameters:
                - polygon (str): The polygon string representing the geometry of the impacted area.
                - impacted_area (pd.DataFrame): A DataFrame representing the impacted area.

                Returns:
                - impacted_area (float): The calculated impacted area.
                - impacted_area_percentage (float): The percentage of the geometry covered by the impacted area.
                """
        geometry_area = self.calculate_geometry_area(polygon)
        impacted_area_percentage = (sum(sum(impacted_area.notnull())) / impacted_area.size) * 100
        impacted_area = geometry_area * impacted_area_percentage / 100
        return impacted_area, impacted_area_percentage

