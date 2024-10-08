# SG GPT Project
<!-- @author: sglbl -->

### Creating Virtual Environment with Requirements ( _**python3.10**_+ )
Make python and pip commands run python3 and pip3 and install virtualenv if you don't have it already.
```bash
sudo apt-get update -y &&
sudo apt-get install python3-pip python-is-python3 build-essential -y &&
python -m pip install --upgrade pip &&
python -m pip install virtualenv
```

Create a virtual environment named `.venv` and activate it for the current project.

```bash
python -m virtualenv .venv && source .venv/bin/activate
```

### Activation / Deactivation 
Next time the project workstation is opened, these commands can be used to activate/deactivate the virtual environment.
```bash
# You can activate the virtual environment with the following command.
. .venv/bin/activate

# You can deactivate the virtual environment with the following command.
deactivate
```

### Requirements

Install the requirements.

```markdown
python -m pip install -r requirements.txt --extra-index-url https://download.pytorch.org/whl/cpu
```
<!-- pip install --use-deprecated=legacy-resolver -r requirements.txt
# or install without cuda
grep -iv "cuda" requirements.txt | python -m pip install --no-deps -r /dev/stdin  -->

#### Other Requirements
Put the secret key and db access info (that is needed to generate token and database access) in `.env` file in root directory. (Like the example structure in `.env.example` file)

<!-- ### Models
- Run [this](./app/src/model_downloader.py) code to download the model/s.

Download required model/s and put it in `models` folder.  
For now only NER model is used. -->

### Full Structure
```python
.
├── README.md                            # Project overview and instructions for use.
├── data                                 # Directory for data-related files.
│   ├── docs                             # Documentation files related to data.
│   ├── images                           # Directory for storing image assets.
│   ├── models                           # Directory for storing machine learning models or related files.
│   └── processed                        # Directory for processed data outputs.
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
