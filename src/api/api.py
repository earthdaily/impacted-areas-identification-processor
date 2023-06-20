import logging
from datetime import datetime

import numpy as np
import xarray as xr
from fastapi import FastAPI
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from vegetation_index_impacted_areas_identificator.impacted_areas_identification import *
from vegetation_index_impacted_areas_identificator.utils import *

app = FastAPI(
    docs_url=None,
    title='Impacted Area Identification API',
    description='Impacted Area Identification API enables users to identify the impact of an event in a particular area. It identifies and calculates the affected areas for a given event dates and threshold',
    swagger_ui_parameters={"syntaxHighlight.theme": "obsidian"},
)
app.mount("/static", StaticFiles(directory="./api/files"), name="static")


class MapReferenceItem(BaseModel):
    polygon: str = Field(..., example= "POLYGON((-55.08964959 -12.992576790000001, -55.095571910000004 -12.99349674, -55.09265364 -13.014153310000001, -55.07111016 -13.01013924, -55.07428588 -12.98914779, -55.08261147 -12.99098782, -55.08115233 -13.00152544, -55.08724632 -13.00269622, -55.08819045 -13.0037834, -55.08956371 -13.00369981, -55.08819045 -13.00202724, -55.08964959 -12.992576790000001))")
    eventDate: dt.date = Field(..., example="2021-06-07")
    threshold: float = Field(..., example=-0.15)
class StacItem(BaseModel):
    sensor_collection: str = "sentinel-2-l2a"
    mask_collection: str = "sentinel-2-l2a-cog-ag-cloud-mask"
    mask_band: list[str] = ["agriculture-cloud-mask"]
    bands: list[str] = ["red", "green", "blue", "nir"]
    polygon: str = Field(..., example=  "POLYGON((-93.91666293144225 44.46111651063736,-93.94000887870787 44.52430217873475,-93.979834318161 44.518427330078396,-94.01004672050475 44.50814491947311,-94.001806974411 44.471407214671636,-93.99425387382506 44.44641235787428,-93.96953463554381 44.45327475656579,-93.91666293144225 44.46111651063736))")
    eventDate: dt.date = Field(..., example="2021-06-07")
    threshold: float = Field(..., example=-0.15)

class VegegetationIndexCodes:
    """
    Recreate Vegegetation Inde types enumeration dynamically, based on GeosysPy Enum VegetationIndex, to have Vegegetation Index Type codes instead of names
    """
    codes: Enum = Enum('VegegetationIndexCodes', {member: member for member in VegetationIndex.__members__.keys()})
    codes.__doc__ = "Available Vegegetation Index types"


# serialization function for datetime objects
def serialize_datetime(obj):
    if isinstance(obj, datetime):
        return obj.isoformat()

client = ImpactedAreasIdentificator(Env.PROD)

@app.get("/docs", include_in_schema=False)
async def swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url="/openapi.json",
        title="Impacted Area Api",
        swagger_favicon_url="/static/favicon.svg"
    )


@app.post("/impacted-area-based-on-map-reference")
async def impacted_areas_identification_based_on_map_reference(item:MapReferenceItem,
                                                               indicator: VegegetationIndexCodes.codes):
    event_date = dt.datetime(item.eventDate.year,item.eventDate.month, item.eventDate.day)

    try:
        selected_vi = get_enum_member_from_name(VegetationIndex, indicator.name)

        vi_before_event_date, vi_after_event_date, vi_difference_filtered = client.identify_vi_impacted_area_based_on_map_reference (item.polygon, event_date, item.threshold, selected_vi.value)
        impacted_area, impacted_area_percentage = client.calculate_impacted_area(item.polygon, vi_difference_filtered)
        vi_difference_filtered = json.dumps(xr.where(np.isnan(vi_difference_filtered), None, vi_difference_filtered).to_dict(), default=serialize_datetime)
        return {
            "Impacted area": '{:.3f} m²'.format(impacted_area),
            "Impacted area percentage": '{:.2f} %'.format(impacted_area_percentage),
            f"Impacted area {selected_vi.value}": vi_difference_filtered}
    except Exception as e:
        logging.error(f"An unexpected error occurred: {str(e)}")


@app.post("/impacted-area-based-on-stac")
async def impacted_areas_identification_based_on_stac(item:StacItem,
                                                      indicator: VegegetationIndexCodes.codes):

    event_date = dt.datetime(item.eventDate.year,item.eventDate.month, item.eventDate.day)
    skyfox_params = {
    'sensor_collection':  item.sensor_collection,
    'mask_collection':  item.mask_collection ,
    'mask_band': item.mask_band,
    'event_date': event_date,
    'geometry_wkt': item.polygon,
    'bands':  item.bands}


    try:
        selected_vi = get_enum_member_from_name(VegetationIndex, indicator.name)
        vi_before_event_date, vi_after_event_date, vi_difference_filtered = client.identify_vi_impacted_area_based_on_stac_images(skyfox_params, selected_vi, item.threshold, 10)
        impacted_area, impacted_area_percentage = client.calculate_impacted_area(item.polygon, vi_difference_filtered.compute())
        vi_difference_filtered = json.dumps(xr.where(np.isnan(vi_difference_filtered.compute()), None, vi_difference_filtered.compute()).to_dict(), default=serialize_datetime)
        logging.info(f"stac skyfox_params : {skyfox_params}")

        return {
            "Impacted area": '{:.3f} m²'.format(impacted_area),
            "Impacted area percentage": '{:.2f} %'.format(impacted_area_percentage),
            f"Impacted area {selected_vi.value}": vi_difference_filtered}
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")

