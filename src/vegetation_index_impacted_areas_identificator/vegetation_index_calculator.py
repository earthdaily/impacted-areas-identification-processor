

from abc import ABC, abstractmethod

class VegetationIndexCalculator(ABC):
    @abstractmethod
    def calculate(self, image):
        pass

class NDVI(VegetationIndexCalculator):
    def calculate(self, image):
        return ((image['nir'] - image['red']) / (image['nir'] + image['red'])).rename("NDVI")


class EVI(VegetationIndexCalculator):
    def calculate(self, image):
        raise NotImplementedError("EVI calculation is not implemented")


class GNDVI (VegetationIndexCalculator):
    def calculate(self, image):
        raise NotImplementedError("GNDVI calculation is not implemented")

class CVI (VegetationIndexCalculator):
    def calculate(self, image):
        raise NotImplementedError("CVI calculation is not implemented")
