from setuptools import find_packages, setup
with open('VERSION') as fh:
    version = fh.readline()

setup(
    name='vegetation_index_impacted_areas_identificator',
    packages = find_packages('src'),
    package_dir={"":"src"},
    version=version,
    description='Impacted Areas Identificator with fast API',
    author='EarthDaily Agro',
)
