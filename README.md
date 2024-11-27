# Project Setup

### Installing `uv` project manager

Ensure you have `uv` installed on your system. If not, install it using the following command:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Managing the Virtual Environment

Create the `.venv` virtual environment with this command

```bash
uv venv
```

Activate the virtual environment.
```bash
# You can activate the virtual environment with the following command.
source .venv/bin/activate

# You can deactivate the virtual environment with the following command.
deactivate
```
> Next time the project workstation is opened, these commands can be used to activate/deactivate the virtual environment.

### Setting Up the Project Environment

Once `uv` is installed, use this to set up the project dependencies and environment:

```bash
uv sync
# or
uv pip install -r pyproject.toml
```

### Running the Application

Launch the application with:

```bash
uv run src/main.py
# or
python -m src.main
```
---
### Full Structure
```python
.
├── pyproject.toml                       # All project details and python dependencies required for the project.
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
└── src                                  # Main source code directory.
    ├── application                      # Contains high-level application logic.
    │   ├── utils.py                     # Helper function for the app.
    │   └── x_services                   # Service layer(s) of the application.
    ├── domain                           # Contains core business logic and domain models.
    │   └── models                       # Directory for domain-specific data models.
    │       └── data_models.py           # Implementation of domain data models with data classes.
    ├── infra                            # Infrastructure-related code, particularly for database handling.
    │   └── database                     # Database-related configurations and utilities.
    ├── main.py                          # Main entry point for the application.
    ├── presentation                     # Contains code related to presentation layers like APIs and UIs.
    │   ├── api                          # API-related presentation logic.
    │   │   └── serve_api.py             # Code to serve the API, possibly using FastAPI or Flask.
    │   └── ui                           # API and UI-related presentation logic.
    │       ├── asset.py                 # Css & Js functions needed for UI.
    │       └── gradio_ui.py             # UI Implementation
```
