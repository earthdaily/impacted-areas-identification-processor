from typing import Tuple
import pandas as pd
from dateutil.relativedelta import relativedelta
from geosyspy import Geosys
import datetime
import numpy as np
from geosyspy.utils.constants import *
from pyproj import Geod
from shapely import wkt


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

    def identify_vi_impacted_area_based_on_map_reference(self, polygon: str,
                                                         event_date: datetime,
                                                         threshold: float):
        """
        Identifies the vegetation index (VI) impacted area based on a map reference.

        Parameters:
        - polygon (str): The polygon representing the geometry in Well-Known Text (WKT) format.
        - event_date (datetime): The event date for which the analysis is performed.
        - threshold (float): The threshold value used for filtering the vegetation index difference.

        Returns:
        - ndvi_image_before_event_date (xArray): The NDVI image before the event date.
        - ndvi_image_after_event_date (xArray): The NDVI  image after the event date.
        - impacted_area (xArray): The filtered NDVI difference based on the provided threshold.

        Note:
        This method relies on other helper methods to obtain the necessary data for the analysis.

        Usage:
        1. Call the method `identify_vi_impacted_area_based_on_map_reference` on an instance of the ImpactedAreasIdentificator class.
        2. Provide the polygon representing the map reference.
        3. Specify the event date for analysis.
        4. Set the threshold value for filtering the vegetation index difference.
        5. Retrieve the resulting NDVI images and the impacted area.

        Example:
        polygon = "example_polygon"
        event_date = datetime.datetime(2023, 5, 15)
        threshold = 0.5

        # Call the method to identify VI impacted area
        ndvi_image_before, ndvi_image_after, impacted_area = client.identify_vi_impacted_area_based_on_map_reference(polygon, event_date, threshold)
        """
        coverage_info_df, images_references = self.get_image_coverage_info_based_on_map_reference(polygon, event_date)
        image_date_list = pd.to_datetime(coverage_info_df['image.date']).dt.date
        nearest_event_date = self.find_nearest_dates(event_date.date(), image_date_list)
        ndvi_images_nearest_event_date = self.get_ndvi_image_time_series(polygon,
                                                                         nearest_event_date["before_event_date"],
                                                                         nearest_event_date["after_event_date"])

        ndvi_image_before_event_date = \
            ndvi_images_nearest_event_date.sel(time=str(nearest_event_date["before_event_date"]))['ndvi']
        ndvi_image_after_event_date = \
            ndvi_images_nearest_event_date.sel(time=str(nearest_event_date["after_event_date"]))['ndvi']
        impacted_area = self.calculate_and_filter_ndvi_difference_by_threshold(ndvi_image_before_event_date,
                                                                               ndvi_image_after_event_date,
                                                                               threshold)

        return ndvi_image_before_event_date, ndvi_image_after_event_date, impacted_area

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

    def get_nearest_event_date_images(self, nearest_event_date: dict[str, datetime], polygon: str):

        image_before_event_date = self.get_satellite_image_time_series(polygon,
                                                                       nearest_event_date["before_event_date"])
        image_after_event_date = self.get_satellite_image_time_series(polygon,
                                                                      nearest_event_date["after_event_date"])
        return image_before_event_date, image_after_event_date

    def calculate_ndvi(self, nearest_event_date, image):

        return ((image.sel(
            time=str(nearest_event_date), band='Nir')['reflectance'] - image.sel(
            time=str(nearest_event_date), band='Red')['reflectance']) / ((
                image.sel(time=str(nearest_event_date), band='Nir')[
                    'reflectance'] +
                image.sel(time=str(nearest_event_date), band='Red')[
                    'reflectance']))).rename("NDVI")

    def calculate_and_filter_ndvi_difference_by_threshold(self,
                                                          ndvi_index_for_image_before_event_date,
                                                          ndvi_index_for_image_after_event_date,
                                                          threshold):
        ndvi_difference_result = ndvi_index_for_image_after_event_date.squeeze().drop(
            ['time', 'band']) - ndvi_index_for_image_before_event_date.squeeze().drop(['time', 'band'])
        return ndvi_difference_result.where(ndvi_difference_result < threshold)

    def get_satellite_image_time_series(self, polygon, date):
        return self.__client.get_satellite_image_time_series(polygon,
                                                             date,
                                                             date,
                                                             collections=[SatelliteImageryCollection.SENTINEL_2,
                                                                          SatelliteImageryCollection.LANDSAT_8,
                                                                          SatelliteImageryCollection.LANDSAT_9],
                                                             indicators=["Reflectance"])

    def get_ndvi_image_time_series(self, polygon: str,
                                   startDate: datetime,
                                   endDate: datetime):
        """
        Retrieves the time series of NDVI satellite images within the specified time range and polygon.

        Parameters:
        - polygon (str): The polygon representing the area of interest for the NDVI image time series.
        - startDate (datetime): The start date of the time range for which the NDVI images are retrieved.
        - endDate (datetime): The end date of the time range for which the NDVI images are retrieved.

        Returns:
        - ndvi_image_time_series: The time series of NDVI satellite images within the specified time range and polygon.
        """
        return self.__client.get_satellite_image_time_series(polygon,
                                                             startDate,
                                                             endDate,
                                                             collections=[SatelliteImageryCollection.SENTINEL_2,
                                                                          SatelliteImageryCollection.LANDSAT_8,
                                                                          SatelliteImageryCollection.LANDSAT_9],
                                                             indicators=["ndvi"])

    def check_and_resize_image_to_higher_resolution(self, ndvi_before_event_date, ndvi_after_event_date):
        if ndvi_before_event_date.shape != ndvi_after_event_date.shape:
            if ndvi_before_event_date.shape < ndvi_after_event_date.shape:
                if (
                        ndvi_before_event_date.x.min().values < 0 and ndvi_before_event_date.x.max().values < 0):
                    nx = np.linspace(ndvi_before_event_date.x.max(),
                                     ndvi_before_event_date.x.min(),
                                     ndvi_after_event_date.x.size)
                else:
                    nx = np.linspace(ndvi_before_event_date.x.min(),
                                     ndvi_before_event_date.x.max(),
                                     ndvi_after_event_date.x.size)
                if (
                        ndvi_before_event_date.y.min().values < 0 and ndvi_before_event_date.y.max().values < 0):
                    ny = np.linspace(ndvi_before_event_date.y.max(),
                                     ndvi_before_event_date.y.min(),
                                     ndvi_after_event_date.y.size)
                else:
                    ny = np.linspace(ndvi_before_event_date.y.min(),
                                     ndvi_before_event_date.y.min(),
                                     ndvi_after_event_date.y.size)
                interpolated_image = ndvi_before_event_date.interp(x=nx, y=ny, method='linear')
                interpolated_image = interpolated_image.astype(ndvi_before_event_date.dtype)
                indexed_image = interpolated_image.assign_coords(x=ndvi_after_event_date.x, y=ndvi_after_event_date.y)
                return [indexed_image, ndvi_after_event_date]

            elif (ndvi_before_event_date.shape > ndvi_after_event_date.shape):
                if (
                        ndvi_after_event_date.x.min().values < 0 and ndvi_after_event_date.x.max().values < 0):
                    nx = np.linspace(ndvi_after_event_date.x.max(),
                                     ndvi_after_event_date.x.min(),
                                     ndvi_before_event_date.x.size)
                else:
                    nx = np.linspace(ndvi_after_event_date.x.min(),
                                     ndvi_after_event_date.x.max(),
                                     ndvi_before_event_date.x.size)
                if (
                        ndvi_after_event_date.y.min().values < 0 and ndvi_after_event_date.y.max().values < 0):
                    ny = np.linspace(ndvi_after_event_date.y.max(),
                                     ndvi_after_event_date.y.min(),
                                     ndvi_before_event_date.y.size)
                else:
                    ny = np.linspace(ndvi_after_event_date.y.min(),
                                     ndvi_after_event_date.y.max(),
                                     ndvi_before_event_date.y.size)

                interpolated_image = ndvi_after_event_date.interp(x=nx, y=ny, method='linear')
                interpolated_image = interpolated_image.astype(ndvi_after_event_date.dtype)
                indexed_image = interpolated_image.assign_coords(x=ndvi_before_event_date.x, y=ndvi_before_event_date.y)
                return [ndvi_before_event_date, indexed_image]
        return [ndvi_before_event_date, ndvi_after_event_date]

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
