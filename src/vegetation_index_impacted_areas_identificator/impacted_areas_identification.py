import json
import os
from typing import Tuple
import geojson
import numpy as np
import pandas as pd
from dateutil.relativedelta import relativedelta
from dotenv import load_dotenv
from geosyspy import Geosys
import datetime as dt
from geosyspy.utils.constants import *
from pyproj import Geod
from shapely import wkt
from pystac_client import Client
import requests
import geopandas as gpd
import odc.stac
import rioxarray
import xarray as xr
from xarray import DataArray, Dataset

from vegetation_index_impacted_areas_identificator.vegetation_index import VegetationIndex
from vegetation_index_impacted_areas_identificator.vegetation_index_calculator import *


class ImpactedAreasIdentificator:
    """
       ImpactedAreasIdentificator is a class that identifies and analyzes impacted areas based on vegetation index (ex: NDVI).

       Parameters:
       - enum_env (enumerate): The enumeration representing the environment from which the data are retrieved.
       - enum_region (enumerate, optional): 'Region.NA' or 'Region.EU' Default is 'Region.NA'
       - priority_queue (str, optional): The priority queue to be used for the analysis ('realtime' or 'bulk'). Defaults to "realtime".

       Usage:
       1. Create an instance of the ImpactedAreasIdentificator class by providing the required parameters.
       2. Use the instance to identify and analyze impacted areas based on the provided parameters.


       # Create an instance of ImpactedAreasIdentificator
       client = ImpactedAreasIdentificator(enum_env)

       # Use the instance to identify and analyze impacted areas based on map reference or catalogue Stac
       client.identify_vi_impacted_area_based_on_map_reference()
       client.identify_vi_impacted_area_based_on_stac_images()

       """

    def __init__(self,enum_env: enumerate,
                 enum_region: enumerate = Region.NA,
                 priority_queue: str = "realtime",
                 ):
        load_dotenv()
        self.region: str = enum_region.value
        self.env: str = enum_env.value
        self.priority_queue: str = priority_queue
        self.__client: Geosys = Geosys(os.getenv('API_CLIENT_ID'),
                                       os.getenv('API_CLIENT_SECRET'),
                                       os.getenv('API_USERNAME'),
                                       os.getenv('API_PASSWORD'),
                                       enum_env,
                                       enum_region,
                                       priority_queue)

        self.__client_skyfox = self.get_skyfox_client(os.getenv("SKYFOX_URL"),
                                                      os.getenv("SKYFOX_AUTH_URL"),
                                                      os.getenv("SKYFOX_CLIENT_ID"),
                                                      os.getenv("SKYFOX_SECRET"))


    def identify_vi_impacted_area_based_on_map_reference(self, polygon: str,
                                                         event_date: dt,
                                                         min_duration:int,
                                                         threshold: float,
                                                         indicator: VegetationIndex) -> tuple[
        DataArray, DataArray, DataArray]:
        """
        Identifies the vegetation index (VI) impacted area based on a map reference.

        Parameters:
        - geometry (str): The geometry representing the geometry in Well-Known Text (WKT) format.
        - event_date (datetime): The event date for which the analysis is performed.
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

        coverage_info_df, images_references = self.get_image_coverage_info_based_on_map_reference(polygon, event_date)
        image_date_list = pd.to_datetime(coverage_info_df['image.date']).dt.date
        nearest_event_date = self.find_nearest_dates(event_date.date(),min_duration, image_date_list)

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

    def identify_vi_impacted_area_based_on_stac_images(self, skyfox_params: dict,
                                                       indicator: VegetationIndex,
                                                       threshold: float,
                                                       max_cloud_cover_percentage: int) -> tuple[Dataset, Dataset, DataArray]:
        """
        Identifies the impacted area based on STAC images using vegetation index.

        Parameters:
            max_cloud_cover_percentage: Maximum cloud cover percentage
            skyfox_params (dict): A dictionary containing Skyfox parameters including sensor collection, bands,
                                  mask collection, mask band, event date, and geometry WKT.
            indicator (VegetationIndex): The vegetation index indicator to use for analysis.
            threshold (float): The threshold value for filtering the impacted area.

        Returns:
            vi_before_event_date (xarray.Dataset): The vegetation index image before the event date.
            vi_after_event_date (xarray.Dataset): The vegetation index image after the event date.
            vi_impacted_area (xarray.Dataset): The impacted area based on the vegetation index difference and threshold.
        """
        sensor_collection = skyfox_params['sensor_collection']
        bands = skyfox_params['bands']
        mask_collection = skyfox_params['mask_collection']
        mask_band = skyfox_params['mask_band']
        event_date = skyfox_params['event_date']
        geometry_wkt = skyfox_params['geometry_wkt']
        images_datacube = self.get_free_cloud_images_using_stac_catalog(sensor_collection=sensor_collection,
                                                                        mask_collection=mask_collection,
                                                                        mask_band=mask_band,
                                                                        event_date=event_date,
                                                                        geometry_wkt=geometry_wkt,
                                                                        bands=bands)
        time_to_keep = self.get_nearest_event_date_time_indices(images_datacube, event_date, max_cloud_cover_percentage)

        vi_before_event_date, vi_after_event_date = self.calculate_vi_images_nearest_event_date(
            images_datacube, time_to_keep, indicator)
        impacted_area = self.calculate_and_filter_vi_difference_by_threshold(vi_before_event_date,
                                                                                vi_after_event_date, threshold)
        return vi_before_event_date, vi_after_event_date, impacted_area

    def find_nearest_dates(self,
                           event_date: dt,
                           min_duration:int,
                           date_list: [dt]) -> dict[str, dt]:
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
        list_inferior = filter(lambda x: x < event_date, date_list)
        nearest_superior = min(filter(lambda x: x > event_date, date_list))
        for date_before in list_inferior:
            difference = nearest_superior - date_before
            if difference.days>=min_duration:
                nearest_inferior = date_before
        if 'nearest_inferior' not in locals():
            nearest_inferior = max(filter(lambda x: x < event_date, date_list))
        return {"before_event_date": nearest_inferior, "after_event_date": nearest_superior}

    def get_image_coverage_info_based_on_map_reference(self,
                                                       polygon: str,
                                                       event_date: dt):
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
        if end_date > dt.datetime.today():
            end_date = dt.datetime.today().date()
        return self.__client.get_satellite_coverage_image_references(polygon, start_date, end_date,
                                                                     collections=[SatelliteImageryCollection.SENTINEL_2,
                                                                                  SatelliteImageryCollection.LANDSAT_8,
                                                                                  SatelliteImageryCollection.LANDSAT_9])

    def calculate_and_filter_vi_difference_by_threshold(self,
                                                        vi_index_for_image_before_event_date,
                                                        vi_index_for_image_after_event_date,
                                                        threshold) -> xr.DataArray:
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
            [var for var in ['time', 'band'] if var in vi_index_for_image_after_event_date.coords])
        ds_before = vi_index_for_image_before_event_date.squeeze().drop(
            [var for var in ['time', 'band'] if var in vi_index_for_image_before_event_date.coords])
        vi_difference_result = (ds_after - ds_before).where(~np.logical_or(np.isnan(ds_before), np.isnan(ds_after)))
        vi_difference_result = vi_difference_result.assign_coords(geometry_size_px=sum(sum(vi_difference_result.notnull())).values)
        return vi_difference_result.where(vi_difference_result < threshold)

    def get_vi_image_time_series(self, polygon: str,
                                 startDate: dt,
                                 endDate: dt,
                                 indicator: VegetationIndex) -> DataArray:
        """
        Retrieves the time series of the specified vegetation index satellite images within the specified time range and geometry.

        Parameters:
        - geometry (str): The geometry representing the area of interest for the VI image time series.
        - startDate (datetime): The start date of the time range for which the VI images are retrieved.
        - endDate (datetime): The end date of the time range for which the VI images are retrieved.
        - indicator (VegetationIndex); vegetation index

        Returns:
        - vi_image_time_series: The time series of the specified vegetation index satellite images within the specified time range and geometry.
        """

        vi_image_time_series = self.__client.get_satellite_image_time_series(polygon,
                                                             startDate,
                                                             endDate,
                                                             collections=[SatelliteImageryCollection.SENTINEL_2,
                                                                          SatelliteImageryCollection.LANDSAT_8,
                                                                          SatelliteImageryCollection.LANDSAT_9],
                                                             indicators=[indicator])

        if (len(vi_image_time_series.coords.keys()) == 0):
            raise ValueError(
                f"No {indicator} images time series found !")
        return vi_image_time_series




    def calculate_geometry_area(self,
                                polygon: str) -> float:
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

    def calculate_impacted_area(self,
                                polygon: str,
                                impacted_area: DataArray) -> Tuple[float, float]:
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
        impacted_area_percentage = (sum(sum(impacted_area.notnull())) / impacted_area.geometry_size_px.values) * 100
        impacted_area = geometry_area * impacted_area_percentage / 100
        return impacted_area, impacted_area_percentage


    def calculate_geometry_image_size(self, raw_datacube: Dataset) -> DataArray:
        """
        Calculates the size of the image for a given data cube (without null pixels).

        Parameters:
            raw_datacube (xarray.Dataset): The raw image data cube.

        Returns:
            image_size (int): The size of the image, i.e., the count of non-null pixels in the 'red' band of the data cube at the first time index.
        """
        return raw_datacube['red'].isel(time=0).notnull().sum()


    def get_skyfox_client(self, skyfox_url: str,
                          auth_url: str,
                          client_id: str,
                          secret: str):
        """
        Create a Skyfox client instance for accessing the Skyfox API.

        Parameters:
            skyfox_url (str): The URL of the Skyfox API.
            auth_url (str): The URL for authentication.
            client_id (str): The client ID for authentication.
            secret (str): The secret key for authentication.

        Returns:
            client: A Skyfox client instance authenticated with the provided credentials.
        """

        if skyfox_url is None or auth_url is None or secret is None or client_id is None:
            raise AttributeError(
                "Missing in .env : SKYFOX_URL, SKYFOX_AUTH_URL, SKYFOX_SECRET and SKYFOX_CLIENT_ID"
            )

        token_response = requests.post(
            auth_url,
            data={"grant_type": "client_credentials"},
            allow_redirects=False,
            auth=(client_id, secret),
        )
        token_response.raise_for_status()
        tokens = json.loads(token_response.text)
        client = Client.open(
            skyfox_url,
            headers={"Authorization": f"bearer {tokens['access_token']}"},
        )
        return client


    def get_raw_images_from_stac(self, sensor_collection: str,
                                 event_date: str,
                                 geometry_wkt: str,
                                 bands: list[str],
                                 config=None) -> Dataset:
        """
        Retrieves the raw images from a STAC catalog for the specified sensor collection, event date, geometry, and bands.

        Parameters:
            sensor_collection (str): The name of the sensor collection in the STAC catalog.
            event_date (str): The date of the event for which the images are retrieved 6 months before and after.
            geometry_wkt (str): The Well-Known Text (WKT) representation of the geometry for the area of interest.
            bands (str): The desired bands to retrieve from the assets.
            config (Optional): Additional configuration parameters for Stac.

        Returns:
            raw_datacube (xarray.Dataset): The raw image data cube containing the retrieved images with bands.
        """
        date = self.calculate_date_range(event_date)
        geometry_geojson = geojson.Feature(geometry=wkt.loads(geometry_wkt), properties={}).geometry

        items_collection = self.__client_skyfox.search(collections=[sensor_collection],
                                                       datetime=date,
                                                       intersects=geometry_geojson).item_collection()

        raw_datacube = self.get_clipped_images_datacube(items_collection, bands, config, geometry_wkt, geometry_geojson)
        raw_datacube["time"] = raw_datacube['time'].dt.floor('S')
        raw_datacube = raw_datacube.drop_duplicates('time')
        return raw_datacube

    def get_cloud_mask_from_stac(self, mask_collection: str,
                                 event_date: str,
                                 geometry_wkt: str,
                                 mask_band: list[str],
                                 config=None) -> Dataset:
        """
        Retrieves the cloud mask from a STAC catalog for the specified mask collection, event date, geometry, and mask band.

        Parameters:
            mask_band list[str]: The name of the band of mask collection in the STAC catalog
            mask_collection (str): The name of the mask collection in the STAC catalog.
            event_date (str): The date of the event for which the cloud mask images are retrieved before and 6 months after.
            geometry_wkt (str): The Well-Known Text (WKT) representation of the geometry for the area of interest.
            mask_band list[str]: The desired mask band to retrieve from the images.
            config (Optional): Additional configuration parameters for Stac.

        Returns:
            mask_datacube (xarray.Dataset): The cloud mask data cube containing the retrieved cloud mask images.
        """
        date = self.calculate_date_range(event_date)
        geometry_geojson = geojson.Feature(geometry=wkt.loads(geometry_wkt), properties={}).geometry

        masks_items_collection = self.__client_skyfox.search(collections=[mask_collection],
                                                             datetime=date,
                                                             intersects=geometry_geojson).item_collection()
        mask_datacube = self.get_clipped_images_datacube(masks_items_collection, mask_band, config, geometry_wkt,
                                                         geometry_geojson)

        return mask_datacube

    def apply_cloud_mask_to_raw_images_datacube(self, raw_datacube: Dataset,
                                                mask_datacube: Dataset) -> Dataset:
        """
        Applies the cloud mask to the raw image data cube.

        Parameters:
            raw_datacube (xarray.Dataset): The raw image data cube.
            mask_datacube (xarray.Dataset): The cloud mask data cube.

        Returns:
            image_free_cloud_datacube (xarray.Dataset): The raw image data cube with the cloud mask applied, where pixels with cloud cover are masked out (NAN).
        """
        image_free_cloud_datacube = raw_datacube.where(mask_datacube["agriculture-cloud-mask"] == 1)
        image_free_cloud_datacube["raw_image_size"] = self.calculate_geometry_image_size(raw_datacube)
        return image_free_cloud_datacube

    def get_free_cloud_images_using_stac_catalog(self, sensor_collection: str,
                                                 bands: list[str],
                                                 mask_collection: str,
                                                 mask_band: list[str],
                                                 event_date: str,
                                                 geometry_wkt: str) -> Dataset:
        """
        Retrieves the free cloud images using the STAC catalog for the specified sensor collection, bands, mask collection,
        mask band, event date, and geometry.

        Parameters:
            sensor_collection (str): The name of the sensor collection in the STAC catalog.
            bands list[str]: The desired bands to retrieve from the images.
            mask_collection (str): The name of the mask collection in the STAC catalog.
            mask_band list[str]: The desired mask band to retrieve from the images.
            event_date (str): The date of the event for which the images are retrieved.
            geometry_wkt (str): The Well-Known Text (WKT) representation of the geometry for the area of interest.

        Returns:
            image_free_cloud_datacube (xarray.Dataset): The raw image data cube with the cloud mask applied, where pixels with cloud cover are masked out (NAN).
        """
        raw_image_datacube = self.get_raw_images_from_stac(sensor_collection, event_date, geometry_wkt, bands,
                                                           config=None)

        cloudmask_datacube = self.get_cloud_mask_from_stac(mask_collection, event_date, geometry_wkt, mask_band,
                                                           config=None)
        return self.apply_cloud_mask_to_raw_images_datacube(raw_image_datacube, cloudmask_datacube)

    def calculate_vi_images_nearest_event_date(self, images_datacube: Dataset,
                                               time_index_to_keep: dict,
                                               indicator: VegetationIndex) -> Tuple[Dataset, Dataset]:
        """
        Calculates the vegetation index (VI) images for the nearest event date.

        Parameters:
            images_datacube (xarray.Dataset): The image data cube containing the images.
            time_index_to_keep (dict): A dictionary containing the time indices for before and after the event date.
            indicator (VegetationIndex): The vegetation index indicator to calculate.

        Returns:
            vi_image_before_eventdate (xarray.Dataset): The vegetation index image before the event date.
            vi_image_after_eventdate (xarray.Dataset): The vegetation index image after the event date.
        """
        image_after_eventdate = images_datacube.sel(time=time_index_to_keep['after_event_date'])
        image_before_eventdate = images_datacube.sel(time=time_index_to_keep['before_event_date'])
        vi_image_before_eventdate = self.calculate_vegetation_index(image_before_eventdate, indicator)
        vi_image_after_eventdate = self.calculate_vegetation_index(image_after_eventdate, indicator)
        return vi_image_before_eventdate, vi_image_after_eventdate

    def calculate_vegetation_index(self, image: Dataset,
                                   indicator: VegetationIndex) -> Dataset:
        """
        Calculates the specified vegetation index for the given image.

        Parameters:
            image (xarray.Dataset): The image for which the vegetation index is calculated.
            indicator (VegetationIndex): The vegetation index indicator to calculate.

        Returns:
            index_image (xarray.Dataset): The calculated vegetation index image.
        """
        indicator_map = {
            VegetationIndex.NDVI: NDVI(),
            VegetationIndex.EVI: EVI(),
            VegetationIndex.CVI: CVI(),
            VegetationIndex.GNDVI: GNDVI(),
            VegetationIndex.NDWI: NDWI(),
            VegetationIndex.LAI: LAI(),
        }
        index = indicator_map.get(indicator)
        if index is None:
            raise ValueError("Invalid vegetation indicator.")
        return index.calculate(image)

    def calculate_date_range(self, event_date: str) -> str:
        """
        Calculates the date range based on the provided event date.

        Parameters:
            event_date (str): The date of the event.

        Returns:
            date_range (str): The calculated date range in the format "start_date/end_date".
        """
        start_date = event_date + relativedelta(months=-6)
        end_date = event_date + relativedelta(months=6)

        if end_date > dt.datetime.today():
            end_date = dt.datetime.today().date()

        date_range = start_date.strftime("%Y-%m-%d") + "/" + end_date.strftime("%Y-%m-%d")
        return date_range

    def get_clipped_images_datacube(self, items_collection: str,
                                    selected_bands: list[str],
                                    config: str,
                                    geometry_wkt: str,
                                    geometry_geojson,
                                    resolution=10, crs="epsg:3857") -> Dataset:
        """
        Retrieves the clipped images data cube from the provided items collection.

        Parameters:
            items_collection (str): The collection of STAC items representing the images.
            selected_bands (list[str]): The selected bands to retrieve from the images.
            config (dict): Additional configuration parameters for the retrieval process.
            geometry_wkt (str): The Well-Known Text (WKT) representation of the geometry for clipping.
            geometry_geojson (GeoJSON): The geometry in GeoJSON format for clipping.
            resolution (int): The desired resolution of the clipped images.
            crs (str): The desired coordinate reference system (CRS) for the clipped images.

        Returns:
            ds_clipped (xarray.Dataset): The clipped images data cube with the selected bands, clipped to the specified geometry.
        """
        ds = odc.stac.stac_load(
            items_collection,
            bands=selected_bands,
            crs=crs,
            resolution=resolution,
            chunks={},
            stac_cfg=config,
            geopolygon=geometry_geojson
        )
        ds_clipped = ds.rio.clip([gpd.GeoDataFrame(index=[0], crs="EPSG:4326",
                                                   geometry=[wkt.loads(geometry_wkt)]).to_crs(ds.rio.crs).loc[
                                      0, 'geometry']]) \
            .where(lambda x: x != 0)
        return ds_clipped

    def get_nearest_event_date_time_indices(self, datacube: Dataset,
                                            event_date: str,
                                            max_cloud_cover_percentage: int) -> dict[str, dt]:
        """
        Returns the time indices of images with cloud cover percentage within the provided AOI and TOI.

        Args:
            datacube (xarray): A list of image data.
            event_date (str): The date of the event.
            max_cloud_cover_percentage (int): The maximum allowed cloud cover percentage.

        Returns:
            list: A dict of time indices corresponding to clear images within the specified cloud cover percentage.
        """

        time_index_to_keep = {}
        for time_value in datacube.sel(time=slice(None, (event_date + dt.timedelta(days=-1)).date())).time[::-1]:
            cloud_free_percentage = datacube['red'].sel(time=time_value).notnull().sum() / datacube["raw_image_size"]
            if cloud_free_percentage > 1 - max_cloud_cover_percentage * 0.01:
                time_index_to_keep['before_event_date'] = time_value.values
                break

        for time_value in datacube.sel(time=slice((event_date + dt.timedelta(days=1)).date(), None)).time:
            cloud_free_percentage = datacube['red'].sel(time=time_value).notnull().sum() / datacube["raw_image_size"]
            if cloud_free_percentage > max_cloud_cover_percentage * 0.01:
                time_index_to_keep['after_event_date'] = time_value.values
                break

        return time_index_to_keep
