<div id="top"></div>
<!-- PROJECT SHIELDS -->
<!--
*** See the bottom of this document for the declaration of the reference variables
*** https://www.markdownguide.org/basic-syntax/#reference-style-links
-->


<!-- PROJECT LOGO -->
<br>
<div align="center">
  <a href="https://github.com/GEOSYS">
    <img src="https://earthdailyagro.com/wp-content/uploads/2022/01/Logo.svg" alt="Logo" width="400" height="200">
  </a>
  
  <h1>Impacted Areas Identification</h1>

  <p>
    Learn how to use &lt;geosys/&gt; platform capabilities in your own business workflow! Build your processor and learn how to run them on your platform.
    <br>
    <a href="https://earthdailyagro.com/"><strong>Who we are</strong></a>
  </p>

  <p>
    <a href="https://github.com/GEOSYS/GeosysPy/issues">Report Bug</a>
    ·
    <a href="https://github.com/GEOSYS/GeosysPy/issues">Request Feature</a>
  </p>
</div>

<div align="center"></div>

<div align="center">
  
[![LinkedIn][linkedin-shield]][linkedin-url]
[![Twitter][twitter-shield]][twitter-url]
[![Youtube][youtube-shield]][youtube-url]
[![Issues][issues-shield]][issues-url]
[![MIT License][license-shield]][license-url]

</div>


<!-- TABLE OF CONTENTS -->
<details open>
  <summary>Table of Contents</summary>
  
- [About The Project](#about-the-project)
- [Getting Started](#getting-started)
  - [Prerequisite](#prerequisite)
  - [Installation](#installation)
- [Usage](#usage)
  - [Usage with Jupyter Notebook](#usage-with-jupyter-notebook)
  - [Run the example inside a Docker container](#run-the-example-inside-a-docker-container)
- [Project Organization](#project-organization)
- [Resources](#resources)
- [Support development](#support-development)
- [License](#license)
- [Contact](#contact)
- [Copyrights](#copyrights)
   
</details>


<!-- ABOUT THE PROJECT -->
## About The Project

<p> The aim of this project is to help our customers valuing &ltgeosys/&gt platform capabilities to build their own analytic of interest. </p>

The purpose of this example is to assess the impact of an event on an area of interest (i.e drought, fire, high precipitations). Once the date of event and the threshold are set, a difference map based on the required products (NDVI, EVI etc.) is provided. This allows to better locate the impacted areas, thus support in the decision making process to recover from the event.

It highlights the ability to retrieve a product time series in [xarray](https://docs.xarray.dev/en/stable/) format. 

This directory allows you to run this example both through a notebook and as a local application on your machine. 
 

<p align="right">(<a href="#top">back to top</a>)</p>


<!-- GETTING STARTED -->
## Getting Started

### Prerequisite

 <p align="left">
Use of this project requires valids credentials from the &ltgeosys/&gt platform . If you need to get trial access, please register <a href=https://earthdailyagro.com/geosys-registration/>here</a>.
</p>

To be able to run this example, you will need to have following tools installed:

1. Install Conda: please install Conda on your computer. You can download and install it by following the instructions provided on the [official Conda website](https://conda.io/projects/conda/en/latest/user-guide/install/index.html)

2. Install Docker Desktop: please install Docker Desktop on your computer. You can download and install it by following the instructions provided on the [official Docker Desktop website](https://docs.docker.com/desktop/)

3. Install Jupyter Notebook: please install jupyter Notebook on your computer following the instructions provided on the [official Jupyter website](https://jupyter.org/install)

4. Install Git: please install Github on your computer. You can download and install it by visiting <a href=https://desktop.github.com/>here</a> and following the provided instructions


This package has been tested on Python 3.9.7.

<p align="right">(<a href="#top">back to top</a>)</p>


### Installation

To set up the project, follow these steps:

1. Clone the project repository:
    
    ```
    git clone https://github.com/GEOSYS/impacted-areas-identification

    ```


2. Change the directory:

    ```
    cd impacted-areas-identification
    ```
3. Fill the environment variable (.env)

Ensure that you populate the .env file with your Geosys APIs credentials. If you haven't acquired the credentials yet, please [click](https://earthdailyagro.com/geosys-registration) here to obtain them.

```
API_CLIENT_ID = <your client id>
API_CLIENT_SECRET = <your client id>
API_USERNAME = <your username>
API_PASSWORD = <your password>
```

To access and use our Catalog STAC named "Skyfox," please ensure that you have the following environment variables set in your .env file:

```
SKYFOX_URL = https://api.eds.earthdaily.com/archive/v1/stac/v1
SKYFOX_AUTH_URL = <skyfox auth url>
SKYFOX_CLIENT_ID =  <your client id>
SKYFOX_SECRET = <your client id>
```

<p align="right">(<a href="#top">back to top</a>)</p>


<!-- USAGE -->
## Usage


### Usage with Jupyter Notebook

To use the project with Jupyter Notebook, follow these steps:


1. Create a Conda environment:

    ```
    conda create -y --name demo
    ```


2. Activate the Conda environment:

    ```
    conda activate demo
    ```


3. Install the project dependencies. You can do this by running the following command in your terminal:

    ```
    conda install -y pip
    pip install -r requirements.txt
    pip install ipykernel
    ```
4. Set up the Jupyter Notebook kernel for the project:

    ```
    python -m ipykernel install --user --name demo --display-name example1
    ```
5. Open the example notebook (impacted_areas_identification.ipynb) by clicking on it.



6. Select the "Kernel" menu and choose "Change Kernel". Then, select "example1" from the list of available kernels.


7. Run the notebook cells to execute the code example.

<p align="right">(<a href="#top">back to top</a>)</p>

### Run the example inside a Docker container

To set up and run the project using Docker, follow these steps:

1. Build the Docker image locally:

    ```
    docker build --tag example1 .
    ```

2. Run the Docker container:
    
    ```
    docker run -d --name example1_container -p 8081:80 example1
    ```

3. Access the API by opening a web browser and navigating to the following URL:
    
    ```
    http://127.0.0.1:8081/docs
    ```


This URL will open the Swagger UI documentation, click on the "Try it out" button under each POST endpoint and enter the request parameters and body

#### POST /impacted-area-based-on-map-reference:

Parameters:
  - Vegetation Index, ex: "NDVI"

Body Example:

```json
{ 
  "geometry": "POLYGON((-55.08964959 -12.992576790000001, -55.095571910000004 -12.99349674, -55.09265364 -13.014153310000001, -55.07111016 -13.01013924, -55.07428588 -12.98914779, -55.08261147 -12.99098782, -55.08115233 -13.00152544, -55.08724632 -13.00269622, -55.08819045 -13.0037834, -55.08956371 -13.00369981, -55.08819045 -13.00202724, -55.08964959 -12.992576790000001))",
  "eventDate": "2021-06-07",
  "threshold": -0.15
}
```

#### POST /impacted-area-based-on-stac:


Parameters:
  - Vegetation Index, ex: "NDVI"

Body Example:

```json
{
  "sensor_collection": "sentinel-2-l2a",
  "mask_collection": "sentinel-2-l2a-cog-ag-cloud-mask",
  "mask_band": [
    "agriculture-cloud-mask"
  ],
  "bands": [
    "red",
    "green",
    "blue",
    "nir"
  ],
  "geometry": "POLYGON((-93.91666293144225 44.46111651063736,-93.94000887870787 44.52430217873475,-93.979834318161 44.518427330078396,-94.01004672050475 44.50814491947311,-94.001806974411 44.471407214671636,-93.99425387382506 44.44641235787428,-93.96953463554381 44.45327475656579,-93.91666293144225 44.46111651063736))",
  "eventDate": "2021-06-07",
  "threshold": -0.15
}
```

<p align="right">(<a href="#top">back to top</a>)</p>

<!-- PROJECT ORGANIZATION -->
## Project Organization


    ├── README.md         
    ├── notebooks          
    ├── requirements.txt    
    ├── environment.yml   
    │
    ├── setup.py           
    ├───src                
    │   ├───main.py 
    │   ├───api
    │   │   ├── files
    │   │   │   └── favicon.svg
    │   │   ├── __init__.py
    │   │   └── api.py
    │   └───vegetation_index_impacted_areas_identificator
    │       ├── __init__.py
    │       ├── utils.py
    │       ├── vegetation_index.py
    │       ├── vegetation_index_calculator.py
    │       └── impacted_areas_identification.py
    └── tests         

<p align="right">(<a href="#top">back to top</a>)</p>

<!-- RESOURCES -->
## Resources 
The following links will provide access to more information:
- [EarthDaily agro developer portal  ](https://developer.geosys.com/)
- [Pypi package](https://pypi.org/project/geosyspy/)
- [Analytic processor template](https://github.com/GEOSYS/Analytic-processor-template)

<p align="right">(<a href="#top">back to top</a>)</p>

<!-- CONTRIBUTING -->
## Support development

If this project has been useful, that it helped you or your business to save precious time, don't hesitate to give it a star.

<p align="right">(<a href="#top">back to top</a>)</p>

## License

Distributed under the [MIT License](https://github.com/GEOSYS/Studies-and-Analysis/blob/main/LICENSE). 

<p align="right">(<a href="#top">back to top</a>)</p>

## Contact

For any additonal information, please [email us](mailto:sales@earthdailyagro.com).

<p align="right">(<a href="#top">back to top</a>)</p>

## Copyrights

© 2023 Geosys Holdings ULC, an Antarctica Capital portfolio company | All Rights Reserved.

<p align="right">(<a href="#top">back to top</a>)</p>

<!-- MARKDOWN LINKS & IMAGES -->
<!-- https://www.markdownguide.org/basic-syntax/#reference-style-links -->
<!-- List of available shields https://shields.io/category/license -->
<!-- List of available shields https://simpleicons.org/ -->
[contributors-shield]: https://img.shields.io/github/contributors/github_username/repo.svg?style=social
[NETcore-shield]: https://img.shields.io/badge/.NET%20Core-6.0-green
[NETcore-url]: https://github.com/dotnet/core
[contributors-url]: https://github.com/github_username/repo/graphs/contributors
[forks-shield]: https://img.shields.io/github/forks/github_username/repo.svg?style=plastic&logo=appveyor
[forks-url]: https://github.com/github_username/repo/network/members
[stars-shield]: https://img.shields.io/github/stars/impacted-areas-identification/repo.svg?style=plastic&logo=appveyor
[stars-url]: https://github.com/github_username/repo/stargazers
[issues-shield]: https://img.shields.io/github/issues/GEOSYS/impacted-areas-identification/repo.svg?style=social
[issues-url]: https://github.com/GEOSYS/impacted-areas-identification/issues
[license-shield]: https://img.shields.io/badge/License-MIT-yellow.svg
[license-url]: https://opensource.org/licenses/MIT
[linkedin-shield]: https://img.shields.io/badge/-LinkedIn-black.svg?style=social&logo=linkedin
[linkedin-url]: https://www.linkedin.com/company/earthdailyagro/mycompany/
[twitter-shield]: https://img.shields.io/twitter/follow/EarthDailyAgro?style=social
[twitter-url]: https://img.shields.io/twitter/follow/EarthDailyAgro?style=social
[youtube-shield]: https://img.shields.io/youtube/channel/views/UCy4X-hM2xRK3oyC_xYKSG_g?style=social
[youtube-url]: https://img.shields.io/youtube/channel/views/UCy4X-hM2xRK3oyC_xYKSG_g?style=social
[language-python-shiedl]: https://img.shields.io/badge/python-3.9-green?logo=python
[language-python-url]: https://pypi.org/ 
[GitStars-shield]: https://img.shields.io/github/stars/GEOSYS?style=social
[GitStars-url]: https://img.shields.io/github/stars/GEOSYS?style=social
[CITest-shield]: https://img.shields.io/github/workflow/status/GEOSYS/impacted-areas-identification/Continous%20Integration
[CITest-url]: https://img.shields.io/github/workflow/status/GEOSYS/impacted-areas-identification/Continous%20Integration
