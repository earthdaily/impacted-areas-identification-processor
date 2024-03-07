"""outpout schema class"""

from typing import Optional

from pydantic import BaseModel


class Metrics(BaseModel):
    """
    Metrics for the output.

    Attributes:
        execution_time (Optional[str]): The execution time.
        data_generation_network_use (Optional[str]): Network use for datacube generation.
        data_upload_network_use (Optional[str]): Network use for datacube upload.
    """

    execution_time: Optional[str] = None
    data_generation_network_use: Optional[str] = None
    data_upload_network_use: Optional[str] = None


class Results(BaseModel):
    """
    Results of the processor

    Attributes:
        before_event_date (str):  A string representing the date before event date.
        after_event_date (str):  A string representing the date after event date.
        impacted_area_percentage (str): A string representing the percentage of impacted area.
        impacted_area (str): A string representing the impacted area.
    """

    before_event_date: str
    after_event_date: str
    impacted_area_percentage: str
    impacted_area: str


class OutputModel(BaseModel):
    """
    Output model containing storage links, and metrics.

    Attributes:
        storage_links (str): The link of the output path.
        results (Results): results of the processor
        metrics (Optional[Metrics]): Metrics for the output.
    """

    storage_links: str
    results: Results
    metrics: Optional[Metrics] = None  # type: ignore
