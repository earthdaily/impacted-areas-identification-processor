from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.openapi.docs import get_swagger_ui_html
from geosyspy.utils.constants import *
from pydantic import BaseModel
import os
import xarray as xr
import numpy as np
import datetime as dt
import json
from vegetation_index_impacted_areas_identificator.impacted_areas_identification import *
from datetime import datetime

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
    polygon: str
    eventDate: dt.date
    threshold: float

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
    ndvi_before_event_date, ndvi_after_event_date, ndvi_difference_filtered = client.identify_vi_impacted_area_based_on_map_reference (item.polygon, event_date, item.threshold)
    impacted_area, impacted_area_percentage = client.calculate_impacted_area(item.polygon, ndvi_difference_filtered)
    ndvi_after_event_date_json = json.dumps(xr.where(np.isnan(ndvi_after_event_date), None, ndvi_after_event_date).to_dict(), default=serialize_datetime)
    return {
        "Impacted area": '{:.3f} m²'.format(impacted_area),
        "Impacted area percentage": '{:.2f} %'.format(impacted_area_percentage),
        "Impacted area ndvi": ndvi_after_event_date_json
    }

