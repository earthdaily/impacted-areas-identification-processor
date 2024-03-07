""" Vegeation Index class"""

from enum import Enum


class VegetationIndex(Enum):
    """
    Available Index values
    """

    NDVI = "ndvi"
    EVI = "evi"
    GNDVI = "gndvi"
    NDWI = "ndwi"
    CVI = "cvi"
    CVIn = "cvin"
    LAI = "lai"
