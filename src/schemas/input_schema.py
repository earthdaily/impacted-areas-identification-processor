"""Input schema class"""

from pydantic import BaseModel


class Parameters(BaseModel):
    """
    Parameters class

    Attributes:
        polygon (str): A string representing the polygon for spatial filtering.
        eventDate (str): A string representing the event date.
        minDuration (int): An integer representing the minimal duration.
        threshold (float): A float representing the threshold to identify the imapacted area
    """

    polygon: str
    eventDate: str
    minDuration: int
    threshold: float


class InputModel(BaseModel):
    """
    Input model class

    Attributes:
        parameters (Parameters): An instance of the Parameters class containing task parameters.
        indicator (str): A string representing indicator for data analysis.
    """

    parameters: Parameters
    indicator: str
