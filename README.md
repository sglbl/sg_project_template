# SG Project Template
<!-- Author: @sglbl -->

A clean, modular Python application template using **Clean Architecture** (Onion Architecture), **Streamlit UI**, **FastAPI REST API**, **Typer CLI**, **PostgreSQL / SQLModel**, and **Marimo Notebooks**.

---

## 🚀 Quick Start

### 1. Prerequisites & Virtual Environment

Ensure you have [`uv`](https://sglbl.notion.site/UV-149a7f36b84480b0b4f4f074883bcd42) installed:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Create and activate the Python 3.12 virtual environment:

```bash
uv venv --python 3.12
source .venv/bin/activate
```

Install project dependencies:

```bash
uv sync
```

---

## ⚡ Running the Application

You can execute commands directly using the root executable `./run` or `python -m src.main`:

```bash
# Display CLI help menu & options
./run
# (or python -m src.main)

# Launch Streamlit UI
./run ui

# Launch FastAPI REST API server (port 8001)
./run api

# Check environment & DB status
./run status

# Display project version
./run version
```

---

## 📊 Interactive Marimo Notebooks

Exploratory notebooks are placed in the root [`notebooks/`](notebooks) directory to keep `src/` clean:

```bash
# Edit interactive Marimo notebook in browser
marimo edit notebooks/explore_marimo.py

# Serve notebook as a standalone web app
marimo run notebooks/explore_marimo.py
```

---

## 🧪 Testing & Static Verification

Run static type checks and unit test suite:

```bash
# Run unit tests and Pyright type verification
pytest -m "not integration"

# Run full test suite including live service checks
pytest
```

---

## 📚 HTML Documentation Generation

Generate HTML documentation from docstrings using `pdoc3`:

```bash
pdoc3 --html -o data/_docs/ src --force
```

---

## 🏗️ Project Architecture & Layout

```
.
├── run                                 # Root executable wrapper script for CLI commands
├── pyproject.toml                      # Project metadata & dependencies
├── README.md                           # Project instructions & overview
├── data/                               # Application assets, configs, and sample inputs
├── notebooks/                          # Root-level Marimo & Jupyter exploratory notebooks
│   ├── README.md                       # Marimo usage guide
│   ├── explore_marimo.py              # Interactive Plotly analytics notebook
│   └── trial.ipynb                     # Jupyter notebook
├── src/                                # Application source code (Clean Architecture)
│   ├── main.py                         # Application CLI entrypoint
│   ├── version.py                      # Application version string (__version__)
│   ├── config.py                       # Configuration & pydantic-settings
│   ├── application/                    # Application use cases & helper utilities
│   │   └── utils.py                    # Helper utilities
│   ├── domain/                         # Core domain logic, models, & repository interfaces
│   │   ├── models/                     # SQLModel & data classes
│   │   ├── schemas/                    # Pydantic schemas (ResponseMessage, etc.)
│   │   └── repo_interfaces/            # Abstractions for persistence repositories
│   ├── infra/                          # Infrastructure & external adapters
│   │   ├── logging.py                  # Loguru logging setup
│   │   ├── postgres/                   # Postgres DB operations & async/sync engines
│   │   └── persistence/                # Repository implementations (pgvector, qdrant)
│   └── presentation/                   # Presentation layer (UI, REST API, CLI)
│       ├── cli.py                      # Typer CLI application commands
│       ├── bootstrap.py                # Service dependency container
│       ├── dependencies.py             # FastAPI dependency checks & response examples
│       ├── rest/                       # FastAPI REST API routers & server runner
│       └── ui/                         # Streamlit UI app, sidebar, and assets
└── tests/                              # Pytest test suite & static type verification
    ├── conftest.py                     # Test fixtures
    ├── test_static.py                  # Pyright static type checker suite
    ├── test_ui.py                      # Streamlit UI helper tests
    ├── test_api.py                     # REST API test suite
    └── test_db.py                      # Database integration tests
```
