# SG GPT Project

### Creating Virtual Environment with Requirements
Make python and pip commands run python3 and pip3 and install virtualenv if you don't have it already.
```bash
sudo apt-get update
sudo apt-get install python3-pip python-is-python3 build-essential
python -m pip install virtualenv
```

Create virtual environment.

```bash
python -m virtualenv .venv
```

Activate virtual environment.

```bash
source .venv/bin/activate
```

You can deactivate virtual environment with the following command.

```bash
deactivate
```

### Installation of requirements

Install requirements with the last version of pip

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

<!-- ### Models
- Run [this](./app/src/model_downloader.py) code to download the model/s.

Download required model/s and put it in `models` folder.  
For now only NER model is used. -->

<!-- ### Other Requirements
Put the secret key and db info (that is needed to generate token and database access) in `.env` file in root. (Like in `.env.example`) -->

### Full Structure
```python
.
├── README.md                            # Project overview and instructions for use.
├── data                                 # Directory for data-related files.
│   ├── docs                             # Documentation files related to data.
│   │   ├── example.txt                  # Example text file, likely for testing or reference.
│   │   └── info.MD                      # Markdown file with additional documentation or notes.
│   ├── images                           # Directory for storing image assets.
│   │   ├── favicon.ico                  # Favicon for the project, used in web interfaces.
│   │   └── logo.png                     # Logo image file for branding or UI purposes.
│   ├── models                           # Directory for storing machine learning models or related files.
│   └── processed                        # Directory for processed data outputs.
│       └── data.csv                     # Processed data in CSV format, likely for analysis or training.
├── docker                               # Docker-related configurations and scripts.
│   ├── Dockerfile                       # Dockerfile for building the project's container.
│   ├── azure-pipelines.yml              # CI/CD pipeline configuration for Azure.
│   ├── docker-build.sh                  # Shell script to automate Docker builds.
│   └── docker-compose.yml               # Docker Compose file for defining multi-container Docker applications.
├── requirements.txt                     # Python dependencies required for the project.
└── src                                  # Main source code directory.
    ├── application                      # Contains high-level application logic.
    │   └── services                     # Service layer of the application.
    │       └── llm_services.py          # Implementation of large language model (LLM) services.
    ├── domain                           # Contains core business logic and domain models.
    │   └── models                       # Directory for domain-specific data models.
    │       └── data_models.py           # Implementation of domain data models.
    ├── infra                            # Infrastructure-related code, particularly for database handling.
    │   └── database                     # Database-related configurations and utilities.
    │       ├── db_config.py             # Configuration settings for the database connection.
    │       ├── db_engine.py             # Code to set up and manage the database engine.
    │       ├── db_models.py             # Database models, likely using an ORM like SQLAlchemy.
    │       └── db_test.py               # Test cases for database interactions.
    ├── main.py                          # Main entry point for the application.
    ├── presentation                     # Contains code related to presentation layers like APIs and UIs.
    │   ├── api                          # API-related presentation logic.
    │   │   └── serve_api.py             # Code to serve the API, possibly using FastAPI or Flask.
    │   └── ui                           # UI-related presentation logic.
    │       └── gradio_ui.py             # Gradio
```


### Running the app from terminal
```bash
python -m src.main
```
