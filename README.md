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

This directory exposes an example of code that will enable you to retrieve an impacted area from an event date and a threshold. It highlights the ability to retrieve a product time series in [xarray](https://docs.xarray.dev/en/stable/) format. 

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

    Please install jupyter Notebook on your computer. You can install it by following the instructions provided on the official Jupyter website

Make sure you have valid credentials. If you need to get trial access, please register [here](https://earthdailyagro.com/geosys-api/#get-started).



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

Ensure that you populate the .env file with your Geosys APIs credentials. If you haven't acquired the credentials yet, please [click](https://www.earthdaily.com/geosys/geosys-api/) here to obtain them.

```
API_CLIENT_ID = <your client id>
API_CLIENT_SECRET = <your client id>
API_USERNAME = <your username>
API_PASSWORD = <your password>
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


This URL will open the Swagger UI documentation, click on the "Try it out" button for the POST endpoint and  enter the request body


Example: 


```json
{ 
  "polygon": "POLYGON((-55.08964959 -12.992576790000001, -55.095571910000004 -12.99349674, -55.09265364 -13.014153310000001, -55.07111016 -13.01013924, -55.07428588 -12.98914779, -55.08261147 -12.99098782, -55.08115233 -13.00152544, -55.08724632 -13.00269622, -55.08819045 -13.0037834, -55.08956371 -13.00369981, -55.08819045 -13.00202724, -55.08964959 -12.992576790000001))",
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
    │       └── impacted_areas_identification.py
    └── tests         

<p align="right">(<a href="#top">back to top</a>)</p>

<!-- RESOURCES -->
## Resources 
The following links will provide access to more information:
- [EarthDaily agro developer portal  ](https://developer.geosys.com/)
- [Pypi package](https://pypi.org/project/geosyspy/)

<p align="right">(<a href="#top">back to top</a>)</p>

<!-- CONTRIBUTING -->
## Support development

If this project has been useful, that it helped you or your business to save precious time, don't hesitate to give it a star.

<p align="right">(<a href="#top">back to top</a>)</p>

## License

Distributed under the [GPL 3.0 License](https://www.gnu.org/licenses/gpl-3.0.en.html). 

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
[contributors-url]: https://github.com/github_username/repo/graphs/contributors
[forks-shield]: https://img.shields.io/github/forks/github_username/repo.svg?style=plastic&logo=appveyor
[forks-url]: https://github.com/github_username/repo/network/members
[stars-shield]: https://img.shields.io/github/stars/qgis-plugin/repo.svg?style=plastic&logo=appveyor
[stars-url]: https://github.com/github_username/repo/stargazers
[issues-shield]: https://img.shields.io/github/issues/GEOSYS/GeosysPy/repo.svg?style=social
[issues-url]: https://github.com/github_username/repo/issues
[license-shield]: https://img.shields.io/github/license/GEOSYS/qgis-plugin
[license-url]: https://www.gnu.org/licenses/gpl-3.0.en.html
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
[CITest-shield]: https://img.shields.io/github/workflow/status/GEOSYS/GeosysPy/Continous%20Integration
[CITest-url]: https://img.shields.io/github/workflow/status/GEOSYS/GeosysPy/Continous%20Integration
