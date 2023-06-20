

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
        return 2.5 * ((image['nir'] - image['red']) / (image['nir'] + 6 * image['red'] - 7.5 * image['blue'] + 1)).rename("EVI")


class GNDVI (VegetationIndexCalculator):
    def calculate(self, image):
        return ((image['nir'] - image['green']) / (image['nir'] + image['green'])).rename("GNDVI")

class CVI (VegetationIndexCalculator):
    def calculate(self, image):
        return (image['nir']*(image['red']/image['green'])).rename("CVI")