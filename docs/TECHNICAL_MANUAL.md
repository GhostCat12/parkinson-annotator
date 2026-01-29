# Technical Manual

## Project Overview

Parkinson’s Annotator is a Python-based software application, developed to support Clinical Scientists annotating genetic variants associated with Parkinson’s disease. The system allows users to upload and query variant data through a web-based interface.

The application is implemented as a Flask web application, with SQLAlchemy used for database management. It also integrates external variant resources (e.g. VariantValidator, ClinVar), bioinformatic tools for data extraction (e.g. NCBI Entrez), and is supported by custom utility modules (e.g. clinvar_fetch.py, variantvalidator_fetch.py).


## Project Structure

The Parkinson's Annotator project follows a modular structure. The main directories and files are organised as follows:

```
parkinson-annotator/
├── docs/   
│   ├── DOCKER.md
│   ├── INSTALLATION.md
│   ├── TECHNICAL_MANUAL.md
│   └── USER_MANUAL.md 
├── src/
│   ├── logs/
│   │   └── parkinsons_annotator.log             
│   └── parkinsons_annotator/
│       ├── modules/
│       │   ├── data_extraction.py
│       │   ├── database_search.py
│       │   ├── db.py
│       │   ├── models.py
│       │   └── routes.py
│       ├── static/
│       │   ├── search.js
│       │   └── style.css
│       ├── templates/
│       │   ├── base.html
│       │   ├── about.html
│       │   └── index.html
│       ├──  utils/
│       │   ├── clinvar_fetch.py
│       │   ├── data_checks.py
│       │   └── variantvalidator_fetch.py
│       ├── logger.py
│       └── main.py
├── tests/
├── uploads/
├── .dockerignore
├── .env.example
├── .gitignore
├── Dockerfile                        
├── Jenkinsfile                       
├── README.md 
├── compose.yml
├── environment.yml                   
├── jenkins_pipeline_console_log.txt                        
└── pyproject.toml                                
```

| Directory/File                      | Description                                                  |
|-------------------------------------|--------------------------------------------------------------|
| `docs/`                             | Project documentation (e.g. installation, user, technical, Docker)  |
| `src/logs/`                         | Log directory created automatically by the logging system (not tracked by Git) |
| `parkinsons_annotator.log`          | Rotating log file (not tracked by Git)                       |
| `src/parkinsons_annotator/`         | Main application source code                                 |
| `modules/`                          | Core application modules (e.g. database, routes, data extraction)     |
| `static/`                        | Static assets for the web interface (CSS and JavaScript)               |
| `templates/`                        | HTML templates used by the Flask web interface               |
| `utils/`                            | Helper functions for external API access and validation      |
| `logger.py`                         | Logging configuration                                        |
| `main.py`                           | Application entry point                                      |
| `tests/`                            | Automated tests                                              |
| `uploads/`                          | Directory for user-uploaded files                            |
| `.dockerignore`                     | Specifies files/directories to be excluded from Docker build context  |
| `.env.example`                      | Template file showing required environment variables         |
| `.gitignore`                        | Specifies files/directories to be excluded from version control (Git) |
| `Dockerfile`                        | Docker build instructions                                    |
| `Jenkinsfile`                       | Defines Jenkins CI pipeline                                  |
| `README.md`                         | Project overview, usage instructions, and key information    |
| `compose.yml`                       | Docker compose configuration for containerisation            |
| `environment.yml`                   | Conda environment specification                              |
| `jenkins_pipeline_console_log.txt`  | Saved Jenkins build output                                   |
| `pyproject.toml`                    | Python project dependencies and build configuration          |


## Key Dependencies

The key dependencies required for Parkinson’s Annotator are:

| Package            | Version    | Purpose                        |
|--------------------|------------|--------------------------------|
| Python             | 3.13+      | Programming language           |
| Flask              | 3.1.2      | Web application framework      |
| SQLAlchemy         | 2.0.44     | Database ORM                   |
| pandas             | 2.3.3      | Data manipulation              |
| requests           | 2.32.5     | HTTP requests                  |
| python-dotenv      | 1.2.1      | Environment variable loading   |
| biopython          | 1.86       | NCBI Entrez API access         |
| markdown           | 3.10       | Converts markdown text to HTML |
| pytest             | 8.4.2      | Testing framework (dev only)   |
| pytest-cov         | 7.0.0      | Test coverage (dev only)       |

See `pyproject.toml` for the complete and up-to-date list of runtime and development dependencies, and `environment.yml` for creating the base Python environment.


## Installation

The instructions for installing this applicaton can be found in [INSTALLATION.md](./INSTALLATION.md).


## Configuration 

After installing Parkinson's Annotator, the application must be configured using environment variables defined in a `.env` file, located in the project root directory. This approach allows sensitive or environment-specific values to be managed separately from the source code.

To initialise the configuration, copy the provided `.env.example` file and rename it to `.env`:
```sh
cp .env.example .env
```

Next, update the `.env` file with the key configuration options outlined below:

| Variable         | Description                                         | Default                    |
|------------------|-----------------------------------------------------|--------------------------- |
| `DB_NAME`        | Name of the SQLite database file                    | "parkinsons_data.db"       |
| `ENTREZ_EMAIL`   | Email address for NCBI Entrez API access (required) | "your@email.com"           |


> **Note:**
>
> - The `ENTREZ_EMAIL` variable is required by NCBI to identify users of the Entrez API.
> - Any changes to database configuration or API credentials should be applied to the `.env` file before running the application.


## Running the Application 

After creating and activating the Conda environment, installing the dependencies, and configuring the environment variables (as outlined in [INSTALLATION.md](./INSTALLATION.md)), run the application using the following command in the project root directory: 

```sh
parkinsons-annotator
```

The application will be available at [http://127.0.0.1:5000](http://127.0.0.1:5000) when running from source installation.

For Docker-based deployment, see [DOCKER.md](./DOCKER.md).

For instructions on how to use the application, see [USER_MANUAL.md](./USER_MANUAL.md).


## Logging

The Parkinson's Annotator application includes a logging system to support debugging and error reporting during development and execution. Logging is configured in the `logger.py` file, and the standard Python logging levels are used (e.g. `DEBUG`, `INFO`, `WARNING`, `ERROR`).

The application writes log messages to 2 destinations:

1. **Console output:**
    
    - Displays log messages during runtime  
    - Configured at the `DEBUG` level for detailed information

2. **Log file:**
    - Stored in the `logs/` directory
    - File name: `parkinsons_annotator.log`
    - Configured at the `WARNING` level, with the following behaviour:
        - Maximum log file size: **500 KB**
        - Number of backup files retained: **2**
        - When the maximum size is reached, older logs are rotated automatically, to ensure logging does not consume excessive disk space.

Logging behaviour can be adjusted by editing the configuration in `logger.py`.


## Testing

Automated tests are located in the `tests/` directory, and use the [pytest](https://docs.pytest.org/en/stable/) framework.

> **Note:** 
>
>The testing and coverage dependencies (`pytest`, `pytest-cov`) are not installed by default with:  
>`conda env create -f environment.yml`.
>`conda activate parkinsons-env`.
>  
>Developers must install these optional dependencies separately:
>
> ```
> pip install -e '.[dev]'
> ```
>
> This will install all packages listed under `[project.optional-dependencies].dev` in the `pyproject.toml`.

To run all tests with coverage, after activating your Conda environment and installing the testing and coverage dependencies, run the following command from the `tests/` directory:

```sh
cd tests  

pytest --cov=parkinsons_annotator
```
Test coverage reports are displayed in the terminal.  

Any new tests should be added to the `tests/` directory as individual Python files, named according to the pattern `test_<module>.py`. Tests should be written using the [pytest](https://docs.pytest.org/en/stable/) framework, with clear, well-described test functions for the appropriate module or feature.


## Continuous Integration (CI)

Automated build and testing verification is managed via [Jenkins](https://www.jenkins.io/).  
The continuous integration (CI) workflow is defined within the `Jenkinsfile`, which includes the following stages:

- Retrieving the source code from the repository
- Setting up the Conda environment
- Installing required project dependencies
- Executing the automated test suite with coverage reporting

Any changes to the CI workflow should be implemented within the `Jenkinsfile`, and validated before merging.










