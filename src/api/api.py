from dotenv import load_dotenv
from fastapi import FastAPI,HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.openapi.docs import get_swagger_ui_html
from geosyspy.utils.constants import *
import os
import xarray as xr
import numpy as np
import datetime as dt
import json
from vegetation_index_impacted_areas_identificator.impacted_areas_identification import *
from datetime import datetime
import logging
from pydantic import BaseModel, Field


app = FastAPI(
    docs_url=None,
    title='Impacted Area Identification API',
    description='Impacted Area Identification API enables users to identify the impact of an event in a particular area. It identifies and calculates the affected areas for a given event dates and threshold',
    swagger_ui_parameters={"syntaxHighlight.theme": "obsidian"},
)
app.mount("/static", StaticFiles(directory="./api/files"), name="static")

@app.get("/docs", include_in_schema=False)
async def swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url="/openapi.json",
        title="Impacted Area Api",
        swagger_favicon_url="/static/favicon.svg"
    )


class Item(BaseModel):
    polygon: str = Field(..., example= "POLYGON((-55.08964959 -12.992576790000001, -55.095571910000004 -12.99349674, -55.09265364 -13.014153310000001, -55.07111016 -13.01013924, -55.07428588 -12.98914779, -55.08261147 -12.99098782, -55.08115233 -13.00152544, -55.08724632 -13.00269622, -55.08819045 -13.0037834, -55.08956371 -13.00369981, -55.08819045 -13.00202724, -55.08964959 -12.992576790000001))")
    eventDate: dt.date = Field(..., example="2021-06-07")
    threshold: float = Field(..., example=-0.15)
    indicator: VegetationIndex = Field(..., example=VegetationIndex.NDVI.value)


# serialization function for datetime objects
def serialize_datetime(obj):
    if isinstance(obj, datetime):
        return obj.isoformat()


load_dotenv()

@app.post("/impacted-area", tags=["Analytic Computation"])
async def impacted_areas_identification(item:Item):
    API_CLIENT_ID = os.getenv('API_CLIENT_ID')
    API_CLIENT_SECRET = os.getenv('API_CLIENT_SECRET')
    API_USERNAME = os.getenv('API_USERNAME')
    API_PASSWORD = os.getenv('API_PASSWORD')

    client = ImpactedAreasIdentificator(API_CLIENT_ID, API_CLIENT_SECRET, API_USERNAME, API_PASSWORD, Env.PROD, Region.NA)
    event_date = dt.datetime(item.eventDate.year,item.eventDate.month, item.eventDate.day)
    try:
        vi_before_event_date, vi_after_event_date, vi_difference_filtered = client.identify_vi_impacted_area_based_on_map_reference (item.polygon, event_date, item.threshold, item.indicator.value)
        impacted_area, impacted_area_percentage = client.calculate_impacted_area(item.polygon, vi_difference_filtered)
        vi_difference_filtered = json.dumps(xr.where(np.isnan(vi_difference_filtered), None, vi_difference_filtered).to_dict(), default=serialize_datetime)
        return {
            "Impacted area": '{:.3f} m²'.format(impacted_area),
            "Impacted area percentage": '{:.2f} %'.format(impacted_area_percentage),
            f"Impacted area {item.indicator}": vi_difference_filtered}
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")

