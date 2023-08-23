import logging
from datetime import datetime

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
    geometry: str = Field(...,
                          example="POLYGON((-93.96113724989586 44.473577981244325,-93.95521493239097 44.474925388980246,-93.95049424452476 44.473057383559784,-93.94929261488609 44.4702093257966,-93.94903512282066 44.46641169924883,-93.95272584242515 44.46604417388972,-93.96010728163414 44.46616668259985,-93.96233887953453 44.46849429924204,-93.96113724989586 44.473577981244325))")
    eventDate: dt.date = Field(..., example="2022-09-15")
    minDuration : int = Field(...,example=10)
    threshold: float = Field(..., example=-0.15)


class StacItem(BaseModel):
    sensor_collection: str = "sentinel-2-l2a"
    mask_collection: str = "sentinel-2-l2a-cog-ag-cloud-mask"
    mask_band: list[str] = ["agriculture-cloud-mask"]
    bands: list[str] = ["red", "green", "blue", "nir"]
    geometry: str = Field(...,
                          example="POLYGON((-93.96113724989586 44.473577981244325,-93.95521493239097 44.474925388980246,-93.95049424452476 44.473057383559784,-93.94929261488609 44.4702093257966,-93.94903512282066 44.46641169924883,-93.95272584242515 44.46604417388972,-93.96010728163414 44.46616668259985,-93.96233887953453 44.46849429924204,-93.96113724989586 44.473577981244325))")
    eventDate: dt.date = Field(..., example="2022-09-15")
    threshold: float = Field(..., example=-0.15)


class VegegetationIndexCodes:
    """
    Recreate Vegegetation Index types enumeration dynamically, based on GeosysPy Enum VegetationIndex, to have Vegegetation Index Type codes instead of names
    """
    codes: Enum = Enum('VegegetationIndexCodes', {member: member for member in VegetationIndex.__members__.keys()})
    codes.__doc__ = "Available Vegetation Index types"


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


@app.post("/impacted-area-based-on-map-reference", tags=["Analytic Computation"])
async def impacted_areas_identification_based_on_map_reference(item: MapReferenceItem,
                                                               indicator: VegegetationIndexCodes.codes):
    event_date = dt.datetime(item.eventDate.year, item.eventDate.month, item.eventDate.day)

    try:
        selected_vi = get_enum_member_from_name(VegetationIndex, indicator.name)

        vi_before_event_date, vi_after_event_date, vi_difference_filtered = client.identify_vi_impacted_area_based_on_map_reference(
            item.geometry, event_date,item.minDuration, item.threshold, selected_vi.value)
        impacted_area, impacted_area_percentage = client.calculate_impacted_area(item.geometry, vi_difference_filtered)
        vi_difference_filtered = json.dumps(
            xr.where(np.isnan(vi_difference_filtered), None, vi_difference_filtered).to_dict(),
            default=serialize_datetime)
        return {
            "Impacted area": '{:.3f} m²'.format(impacted_area),
            "Impacted area percentage": '{:.2f} %'.format(impacted_area_percentage),
            f"Impacted area {selected_vi.value}": vi_difference_filtered}
    except Exception as e:
        logging.error(f"An unexpected error occurred: {str(e)}")
        return {f"An unexpected error occurred: {e}"}


@app.post("/impacted-area-based-on-stac", tags=["Analytic Computation"])
async def impacted_areas_identification_based_on_stac(item: StacItem,
                                                      indicator: VegegetationIndexCodes.codes):
    event_date = dt.datetime(item.eventDate.year, item.eventDate.month, item.eventDate.day)
    skyfox_params = {
        'sensor_collection': item.sensor_collection,
        'mask_collection': item.mask_collection,
        'mask_band': item.mask_band,
        'event_date': event_date,
        'geometry_wkt': item.geometry,
        'bands': item.bands}

    try:
        selected_vi = get_enum_member_from_name(VegetationIndex, indicator.name)
        vi_before_event_date, vi_after_event_date, vi_difference_filtered = client.identify_vi_impacted_area_based_on_stac_images(
            skyfox_params, selected_vi, item.threshold, 10)
        impacted_area, impacted_area_percentage = client.calculate_impacted_area(item.geometry,
                                                                                 vi_difference_filtered.compute())
        vi_difference_filtered = json.dumps(
            xr.where(np.isnan(vi_difference_filtered.compute()), None, vi_difference_filtered.compute()).to_dict(),
            default=serialize_datetime)
        return {
            "Impacted area": '{:.3f} m²'.format(impacted_area),
            "Impacted area percentage": '{:.2f} %'.format(impacted_area_percentage),
            f"Impacted area {selected_vi.value}": vi_difference_filtered}
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")
        return {f"An unexpected error occurred: {e}"}
