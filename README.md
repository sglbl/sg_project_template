# SG Project Template
<!-- Author: @sglbl -->

A clean, modular Python application template using **Clean Architecture** (Onion Architecture), **Streamlit UI**, **FastAPI REST API**, **Typer CLI**, **PostgreSQL / SQLModel**, and **Marimo Notebooks**.

<div align="center" style="margin: 30px 0;">
  <img src="https://user-images.githubusercontent.com/74038190/212284100-561aa473-3905-4a80-b561-0d28506553ee.gif" width="800">
</div>

## 🚀 Quick Start

### 1. Prerequisites & Virtual Environment

Ensure you have [`uv`](https://sglbl.notion.site/UV-149a7f36b84480b0b4f4f074883bcd42) installed:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Create and activate the Python virtual environment:

```bash
uv venv
source .venv/bin/activate
```

Install project dependencies:

```bash
uv sync
```

Fill the `.env` file with your actual values:
```bash
# Generate .env.example from Config Settings SSOT (Source of Truth)
./run export-env
# Copy .env.example to .env and edit it.
cp .env.example .env
```

---

## ⚡ Running the Application

You can execute all CLI commands directly using the root executable `./run` (or `python -m src.main`):

### Core Application Services
```bash
# Display CLI help menu & all available commands
./run --help

# Launch Streamlit UI presentation app
./run ui

# Launch FastAPI REST API server (port 8000)
./run api

# Check environment configuration, DB, & S3 status
./run status

# Display project version
./run version
```

### MLOps Pipelines (MLflow, DVC & RustFS S3)
```bash
# 0. Data Version Control (DVC) backed by RustFS S3 storage
dvc status                           # Check data tracking status
dvc push                             # Push raw data to RustFS S3 bucket
dvc pull                             # Pull raw data from RustFS S3 bucket

# 1. Ingest raw data, validate schema, and create train/test parquet splits
./run ingest

# 2. Train model, log metrics/params to MLflow, export ONNX, and upload to RustFS
./run train

# 2b. Train with automated Optuna hyperparameter optimization
./run train --tune

# 3. Run Evidently data drift evaluation between reference and current data
./run drift

# 4. Convert trained model binary (.pkl) to ONNX format
./run export-onnx --model-path data/models/random_forest.pkl

# 5. Execute quick CLI model prediction with feature JSON
./run predict --features '{"sepal_length": 5.1, "sepal_width": 3.5, "petal_length": 1.4, "petal_width": 0.2}'
```

#### 📈 Model Benchmarks: Baseline vs. Tuned (Optuna)

The table below demonstrates the real-world impact of automated hyperparameter optimization using Optuna on the stratified test split (30 samples):

| Benchmark Metric | `./run train` (Untuned Baseline) | `./run train --tune` (Optuna Optimization) | Delta / Improvement |
| :--- | :--- | :--- | :--- |
| **Optimization Method** | Fixed default hyperparameters | Bayesian Optimization (10 Optuna trials) | Automated tuning |
| **Hyperparameters** | `n_estimators=50`<br>`max_depth=8`<br>`min_samples_split=2` | `n_estimators=35`<br>`max_depth=10`<br>`min_samples_split=6` | Regularized leaf splits |
| **Accuracy** | **`0.9000`** (90.00%) | **`0.9667`** (96.67%) | **+6.67%** |
| **Test Set Accuracy** | **27 / 30** correct (3 errors) | **29 / 30** correct (1 error) | **66.7% error reduction** |
| **Precision (Weighted)** | `0.9024` | `0.9697` | **+6.73%** |
| **Recall (Weighted)** | `0.9000` | `0.9667` | **+6.67%** |
| **F1 Score (Weighted)** | `0.8997` | `0.9666` | **+6.69%** |
| **MLflow Model Registry** | Version Tagged (e.g. `v6`) | Version Tagged (e.g. `v7`) | Automated versioning |

##### 🧠 What These Results Mean

1. **Error Reduction & Boundary Generalization**:
   - The untuned baseline (`./run train`) splits leaf nodes down to `min_samples_split=2`, making individual decision trees fit too tightly around borderline training points. It misclassifies 3 test samples on the difficult boundary between *Versicolor* and *Virginica*.
   - The tuned model (`./run train --tune`) discovers that increasing `min_samples_split` to `6` constrains the trees from overfitting individual points. This creates smoother decision boundaries, cutting test errors from 3 down to 1.
2. **Transparent MLOps Lineage in MLflow**:
   - Both models, their exact parameter payloads, metrics, `.pkl` binaries, and ONNX exports are independently tracked in MLflow (`http://localhost:5100`).
   - The better-performing model version can be promoted through stages (`Staging` ➔ `Production`) or designated via model aliases without code changes.

---

## 🐳 Docker Compose Stack

Run the complete containerized stack (including UI, API, notebooks, and all backing infrastructure) with a single command:

```bash
docker compose up -d --build
```


You can execute all CLI commands directly using the root executable `./run` (or `python -m src.main`).

### 📦 Container Dependencies for `./run` Commands
Some commands operate purely offline on your local filesystem, while others interact with backing infrastructure:

| Command | Required Container Service | How to Start |
| :--- | :--- | :--- |
| `./run ingest`, `./run predict`, `./run export-onnx` | **None** (100% local on disk) | Runs standalone |
| `./run train`, `./run train --tune` | **MLflow** (`http://localhost:5100`) | `docker compose up -d mlflow` |
| `dvc push`, `dvc pull` | **RustFS S3** (`http://localhost:9010`) | `docker compose up -d rustfs` |
| `./run status` | **PostgreSQL & RustFS** | `docker compose up -d postgres rustfs` |
| `./run ui`, `./run api` (local dev) | Backing DB & MLflow services | `docker compose up -d postgres rustfs mlflow` |

> [!TIP]
> **Recommended for local development**: Spin up only the backing infrastructure in Docker so you can run and iterate on `./run` commands or scripts locally:
> ```bash
> docker compose up -d postgres rustfs mlflow
> ```

| Service | Local URL | Credentials / Notes |
| :--- | :--- | :--- |
| **Streamlit UI** | [http://localhost:8501](http://localhost:8501) | Model Serving Sandbox & Drift Monitoring |
| **FastAPI REST API** | [http://localhost:8100/docs](http://localhost:8100/docs) | Interactive Swagger API documentation |
| **MLflow Server** | [http://localhost:5100](http://localhost:5100) | Experiment Tracking & Model Registry |
| **RustFS S3 Console** | [http://localhost:9011](http://localhost:9011) | User: `rustfsadmin` \| Pass: `rustfsadmin` |
| **RustFS S3 API** | `http://localhost:9010` | S3 protocol endpoint for SDKs & pipelines |
| **Marimo Notebook** | [http://localhost:2719](http://localhost:2719) | Interactive notebook workspace |
| **PostgreSQL** | `localhost:5433` | User: `postgres` \| DB: `postgres` |

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
pdoc3 --skip-errors --html -o docs/_html/ src --force
```

---

## 🏗️ Project Architecture & Layout

```bash
.
├── run                                         # Root executable wrapper script for CLI commands
├── compose.yaml                                # Docker Compose configuration (MLflow, RustFS, Postgres, API, UI)
├── pyproject.toml                              # Project metadata & dependencies
├── README.md                                   # Project instructions & overview
├── data/                                       # Data storage & runtime outputs
│   ├── raw/                                    # Immutable raw CSV/Parquet files
│   ├── processed/                              # Transformed & split training datasets
│   ├── models/                                 # Serialized trained models (.onnx, .pkl)
│   └── reports/                                # Evidently drift reports (.html)
├── docs/                                       # Architecture blueprints & roadmaps
│   ├── images/                                 # Architecture diagrams (onion-architecture.png)
│   ├── MLOPS_ROADMAP.md                        # 2026 MLOps architectural specification
│   └── MLOPS_RATING.md                         # MLOps maturity assessment & scorecard (8.8/10)
├── notebooks/                                  # Root-level Marimo & Jupyter exploratory notebooks
│   ├── README.md                               # Marimo usage guide
│   ├── explore_marimo.py                       # Interactive Plotly analytics notebook
│   └── trial.ipynb                             # Jupyter notebook
├── src/                                        # Application source code (Clean Architecture)
│   ├── main.py                                 # Application CLI entrypoint (Typer commands)
│   ├── main_api.py                             # FastAPI application server launcher
│   ├── main_ui.py                              # Streamlit dashboard launcher
│   ├── version.py                              # Application version string (__version__)
│   ├── config.py                               # Centralized configuration & pydantic-settings
│   ├── application/                            # Application use cases, pipelines & services
│   │   ├── utils.py                            # Pipeline & application helper utilities
│   │   ├── pipelines/                          # Data, training, export & evaluation workflows
│   │   │   ├── ingest.py                       # Data loader, Pandera schema validation & split
│   │   │   ├── train.py                        # Model training loop, Optuna tuning & evaluation
│   │   │   ├── export.py                       # Model serialization & ONNX runtime conversion
│   │   │   └── evaluate.py                     # Metric calculation & statistical drift detection
│   │   └── services/                           # Application orchestration services
│   │       ├── ml_service.py                   # Orchestrates ingest -> train -> eval -> register
│   │       └── inference_service.py            # Low-latency inference engine backed by ONNX Runtime
│   ├── domain/                                 # Core domain models, schemas & contracts
│   │   ├── models/                             # Domain entities & business data classes
│   │   │   ├── llm_models.py                   # LLM configurations & prompt domain models
│   │   │   ├── ml_entities.py                  # Model & dataset registry domain dataclasses
│   │   │   └── sql_models.py                   # SQLModel relational table definitions
│   │   ├── repo_interfaces/                    # Protocol interfaces (structural duck typing)
│   │   │   ├── tracker_repository.py           # Protocol for MLflow/W&B experiment tracking
│   │   │   ├── registry_repository.py          # Protocol for model registry lifecycle operations
│   │   │   ├── storage_repository.py           # Protocol for S3/RustFS artifact & model storage
│   │   │   └── vectordb_repository.py          # Protocol for vector search & embeddings
│   │   └── schemas/                            # Boundary contracts & Pydantic validation schemas
│   │       ├── common.py                       # Generic API response envelopes & error schemas
│   │       └── ml_schemas.py                   # Prediction requests, responses & drift payloads
│   ├── infra/                                  # Infrastructure implementations & external adapters
│   │   ├── logging.py                          # Structured Loguru logger initialization
│   │   ├── supabase_client.py                  # Supabase client adapter & configuration
│   │   ├── ml/                                 # MLOps storage & tracking implementations
│   │   │   ├── feature_store.py                # DuckDB analytical feature storage implementation
│   │   │   ├── mlflow_tracker.py               # MLflow tracker & registry with fast socket probe
│   │   │   └── storage.py                      # S3 / RustFS remote object storage provider
│   │   ├── serving/                            # Model inference engines
│   │   │   └── onnx_engine.py                  # High-performance ONNX Runtime inference engine
│   │   ├── postgres/                           # PostgreSQL engine & connection management
│   │   │   ├── database_async.py               # Async SQLAlchemy session & engine
│   │   │   ├── database_sync.py                # Synchronous SQLAlchemy session & engine
│   │   │   ├── db_operations.py                # Database migrations & schema management
│   │   │   └── vectordb/                       # Vector DB drivers (Async, Sync, Cursor, Monad)
│   │   │       ├── vdb_async.py                # Async pgvector operations
│   │   │       ├── vdb_sync.py                 # Synchronous pgvector operations
│   │   │       ├── vdb_monad.py                # Monadic result pgvector handlers
│   │   │       └── vdb_with_cursor.py          # Raw cursor pgvector operations
│   │   └── persistence/                        # Concrete repository adapters
│   │       ├── pgvector_repository.py          # PostgreSQL pgvector repository
│   │       └── qdrant_repository.py            # Qdrant vector database repository
│   └── presentation/                           # Presentation layer (CLI, REST API, UI)
│       ├── bootstrap.py                        # Dependency container & service bootstrap
│       ├── cli.py                              # Typer CLI subcommands (train, eval, export, drift)
│       ├── dependencies.py                     # FastAPI dependency injection providers
│       ├── rest/                               # FastAPI web service
│       │   ├── serve_api.py                    # FastAPI application setup, CORS & router mount
│       │   └── routers/                        # API route controllers
│       │       ├── items.py                    # Generic CRUD item routes
│       │       └── ml.py                       # Machine Learning routes (/predict, /models/active)
│       └── ui/                                 # Streamlit frontend application
│           ├── app_ui.py                       # Multi-tab dashboard (Registry, Drift, Prediction)
│           ├── assets.py                       # Frontend static asset loader
│           ├── sidebar.py                      # Sidebar navigation & service health monitor
│           └── assets/                         # Custom CSS styles, logo & favicon assets
└── tests/                                      # Pytest test suite & static type verification
    ├── conftest.py                             # Test fixtures & test DB session setup
    ├── test_api.py                             # Generic REST API endpoints test suite
    ├── test_db.py                              # PostgreSQL & async database tests
    ├── test_ml_api.py                          # ML REST API endpoint test suite
    ├── test_ml_pipeline.py                     # ML pipeline, ONNX export & drift test suite
    ├── test_static.py                          # Static type checker & code validation suite
    └── test_ui.py                              # Streamlit UI smoke & component test suite
```
