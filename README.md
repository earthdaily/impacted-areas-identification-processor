<div id="top"></div>
<!-- PROJECT SHIELDS -->
<!--
*** See the bottom of this document for the declaration of the reference variables
*** https://www.markdownguide.org/basic-syntax/#reference-style-links
-->


<!-- PROJECT LOGO -->
<br />
<p align="center">
  <a href="https://github.com/GEOSYS">
    <img src="https://earthdailyagro.com/wp-content/uploads/2022/01/Logo.svg" alt="Logo" width="400" height="200">
  </a>

  <h1 align="center">Impacted Areas Identification</h1>

  <p align="center">
    Learn how to use &ltgeosys/&gt platform capabilities in your own business workflow! Build your processor and learn how to run them on your platform.
    <br />
    <a href="https://earthdailyagro.com/"><strong>Who we are</strong></a>
    <br />
    <br />
    <a href="https://github.com/GEOSYS/GeosysPy/issues">Report Bug</a>
    ·
    <a href="https://github.com/GEOSYS/GeosysPy/issues">Request Feature</a>
  </p>
</p>

<div align="center">
</div>

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
  * [Prerequisite](#prerequisite)
  * [Installation](#installation)
- [Usage](#usage)
  * [Run the example inside a Docker container](#run-the-example-inside-a-docker-container)
  * [Usage with Jupyter Notebook](#usage-with-jupyter-notebook)
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

It highlights the ability to retrieve a product time series in [xarray](https://docs.xarray.dev/en/stable/) format, exported in zarr file on a cloud storage provider (AWS S3/AZURE BLOB STORAGE)

This directory allows you to run this example both through a notebook and as a local application on your machine. 
 

<p align="right">(<a href="#top">back to top</a>)</p>


<!-- GETTING STARTED -->
## Getting Started

### Prerequisite

To be able to run this example, you will need to have following tools to be installed



1. Install Git

    Please install Git on your computer. You can download and install it by visiting the [official Git website]    (https://git-scm.com/book/en/v2/Getting-Started-Installing-Git) and following the provided instructions

2. Install Conda

    Please install Conda on your computer. You can download and install it by following the instructions provided on the [official Conda website](https://conda.io/projects/conda/en/latest/user-guide/install/index.html)

3. Install Docker Desktop

    Please install Docker Desktop on your computer. You can download and install it by following the instructions provided on the [official Docker Desktop website](https://docs.docker.com/desktop/)

4. Install Jupyter Notebook

    Please install jupyter Notebook on your computer. You can install it by following the instructions provided on the [official Jupyter website](https://jupyter.org/install)


Make sure you have valid credentials. If you need to get trial access, please register [here](https://earthdailyagro.com/geosys-api/#get-started).



This package has been tested on Python 3.9.7.

<p align="right">(<a href="#top">back to top</a>)</p>


### Installation

To set up the project, follow these steps:

1. Clone the project repository:

    ```
    git clone http://github.com/GEOSYS/impacted-areas-identification-processor
    ```


2. Change the directory:

    ```
    cd impacted-areas-identification-processor
    ```

<p align="right">(<a href="#top">back to top</a>)</p>

## Usage

### Usage with Jupyter Notebook

To use the project with Jupyter Notebook, follow these steps:


1. Create a Conda environment:

    To create a Conda environment, ensure first you have installed Conda on your computer. You can download and install it by following the instructions provided on the official Conda website. 

    
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
    python -m ipykernel install --user --name demo --display-name demo
    ```
5. Open jupyter and then the example notebook (impacted_areas_identification_processor.ipynb) by clicking on it.



6. Select the "Kernel" menu and choose "Change Kernel". Then, select "demo" from the list of available kernels.


7. Run the notebook cells to execute the code example.

<p align="right">(<a href="#top">back to top</a>)</p>

### Run the example inside a Docker container

To set up and run the project using Docker, follow these steps:


1. Create an environment file at root directory. You must specify following values to make the tool run:
    ```
   # geosys identity server information  
   IDENTITY_SERVER_URL = https://identity.geosys-na.com/v2.1/connect/token
   
   # optional (to check token validity)
   # CIPHER_CERTIFICATE_PUBLIC_KEY =
   
   # optional (to use credentials from .env file)
   # API_CLIENT_ID = 
   # API_CLIENT_SECRET = 
   # API_USERNAME = 
   # API_PASSWORD =  
   
   # AWS credentials 
   AWS_ACCESS_KEY_ID = 
   AWS_SECRET_ACCESS_KEY =
   # optional
   #AWS_BUCKET_NAME = 
   
   # Azure credentials
   AZURE_ACCOUNT_NAME = 
   AZURE_BLOB_CONTAINER_NAME = 
   AZURE_SAS_CREDENTIAL =
    
   # Example input file path to run the processor in local 
   INPUT_JSON_PATH=data/processor_input_example.json
    ```

2. Build the Docker image locally:
    ```
    docker build -t template2 .
    ```
3. Run the Docker container:

- Processor Mode


    ```
     docker run -d --name template_container template2 
    ```
    Some options can be provided to the processor:
   <br> --input_path: Path to the input data file
   <br> --bearer_token: Geosys Api bearer token value
   <br> --aws_s3_bucket_name: AWS S3 Bucket name 
   <br> --cloud_storage_provider: Cloud storage provider to store the zarr file (AWS/AZURE)
   <br> --entity_id: Provide an entity_id value added to the zarr output file
   <br> --metrics: Display bandwitdh & time metrics in results (bool)


For example:
    ```
     docker run -d --name template_container template --aws_s3_bucket_name byoa-demo
    ```
   - Processor with API Mode
    
    ```
     docker run -e RUN_MODE_ENV=API -d --name template_container -p 8081:80 template 
    ```

4. Access the API by opening a web browser and navigating to the following URL:
    
    ```
    http://127.0.0.1:8081/docs
    ```

   his URL will open the Swagger UI documentation, click on the "Try it out" button for the POST endpoint.
<br>- Select first a cloud storage provider to store the zarr file produced as output (AWS or Azure Blob Storage)
<br>- You can specify a value for the AWS S3 bucket where the file will be stored (default value can be set in env file: AWS_BUCKET_NAME).
<br>- Select then one indicator value to build the result in zarr format.
<br>- As example, you can then enter the following request body (polygon can be wkt or geojson)

   
   Body Example for impacted_areas_identification_processor endpoint:
   
   ```json
   {
  "polygon": "POLYGON((-93.96113724989586 44.473577981244325,-93.95521493239097 44.474925388980246,-93.95049424452476 44.473057383559784,-93.94929261488609 44.4702093257966,-93.94903512282066 44.46641169924883,-93.95272584242515 44.46604417388972,-93.96010728163414 44.46616668259985,-93.96233887953453 44.46849429924204,-93.96113724989586 44.473577981244325))",
  "eventDate": "2022-09-15",
  "minDuration": 10,
  "threshold": -0.15
}
   ```

4. Closing the Docker container:

    To delete the container when it is not needed anymore run : 
    ```
    docker stop demo
    ```

<!-- PROJECT ORGANIZATION -->
## Project Organization

    ├── README.md          <- The top-level README for developers using this project.
    ├── notebooks          <- Jupyter notebooks. Naming convention is a number (for ordering),
    │                         the creator's initials, and a short `-` delimited description, e.g.
    │                         `1.0-jqp-initial-data-exploration`.
    │
    ├── requirements.txt   <- The requirements file for reproducing the analysis environment, e.g.
    │                         generated with `pip freeze > requirements.txt`
    ├── environment.yml    <- The conda requirements file for reproducing the analysis environment, e.g.
    │                         generated with `conda env export > environment.yml`, or manually
    │
    ├── pyproject.toml     <- Makes project pip installable (pip install -e .) so src can be imported
    ├── MANIFEST.in        <- Used to include/exclude files for package genration. 
    ├───src                <- Source code for use in tis project.
    │   ├───main.py 
    │   ├───api
    │   │   ├── files
    │   │   │   └── favicon.svg
    │   │   ├── __init__.py
    │   │   └── api.py
    │   ├───data
    │   │   └── processor_input_example.json
    │   ├───data
    │   │   ├── __init__.py 
    │   │   ├── input_schema.py   
    │   │   └── output_schema.py
    │   ├───utils
    │   │   ├── __init__.py 
    │   │   ├── file_utils.py   
    │   │   └── logging.py
    │   └───impacted_areas_identification_processor
    │       ├── __init__.py
    │       └── impacted_areas_identification_processor.py
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
[stars-shield]: https://img.shields.io/github/stars/impacted-areas-identification-processor/repo.svg?style=plastic&logo=appveyor
[stars-url]: https://github.com/github_username/repo/stargazers
[issues-shield]: https://img.shields.io/github/issues/GEOSYS/impacted-areas-identification-processor/repo.svg?style=social
[issues-url]: https://github.com/GEOSYS/impacted-areas-identification-processor/issues
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
[CITest-shield]: https://img.shields.io/github/workflow/status/GEOSYS/impacted-areas-identification-processor/Continous%20Integration
[CITest-url]: https://img.shields.io/github/workflow/status/GEOSYS/impacted-areas-identification-processor/Continous%20Integration






