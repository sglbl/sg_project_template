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

cp .env.example .env
# Fill the .env with correct values
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
./dvc status                           # Check data tracking status
./dvc push                             # Push raw data to RustFS S3 bucket
./dvc pull                             # Pull raw data from RustFS S3 bucket

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

Run the full production stack with a single command:

```bash
docker compose up -d
```

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
pdoc3 --html -o data/_docs/ src --force
```

---

## 🏗️ Project Architecture & Layout

```bash
.
├── run                                 # Root executable wrapper script for CLI commands
├── compose.yaml                        # Docker Compose configuration (MLflow, RustFS, Postgres, API, UI)
├── pyproject.toml                      # Project metadata & dependencies
├── README.md                           # Project instructions & overview
├── data/                               # Data storage & runtime outputs
│   ├── raw/                            # Immutable raw CSV/Parquet files
│   ├── processed/                      # Transformed & split training datasets
│   ├── models/                         # Serialized trained models (.onnx, .pkl)
│   └── reports/                        # Evidently drift reports (.html)
├── docs/                               # Architecture blueprints & roadmaps
│   ├── images/                         # Architecture diagrams (onion-architecture.png)
│   └── MLOPS_ROADMAP.md                # 2026 MLOps architectural specification
├── notebooks/                          # Root-level Marimo & Jupyter exploratory notebooks
│   ├── README.md                       # Marimo usage guide
│   ├── explore_marimo.py               # Interactive Plotly analytics notebook
│   └── trial.ipynb                     # Jupyter notebook
├── src/                                # Application source code (Clean Architecture)
│   ├── main.py                         # Application CLI entrypoint
│   ├── version.py                      # Application version string (__version__)
│   ├── config.py                       # Configuration & pydantic-settings
│   ├── application/                    # Application use cases, pipelines & services
│   │   ├── pipelines/                  # Ingest, train, export (ONNX), evaluate (Evidently)
│   │   ├── services/                   # MLService & InferenceService orchestration
│   │   └── utils.py                    # Helper utilities
│   ├── domain/                         # Core domain logic, models, & repository interfaces
│   │   ├── models/                     # SQLModel & ML entity classes
│   │   ├── schemas/                    # Pydantic request/response schemas
│   │   └── repo_interfaces/            # Typing Protocol interfaces (Tracker, Storage, Registry)
│   ├── infra/                          # Infrastructure & external adapters
│   │   ├── logging.py                  # Loguru logging setup
│   │   ├── ml/                         # MLflowTracker, S3StorageProvider (RustFS), DuckDB
│   │   ├── serving/                    # ONNXRuntime inference engine
│   │   ├── postgres/                   # Postgres DB operations & async/sync engines
│   │   └── persistence/                # Repository implementations
│   └── presentation/                   # Presentation layer (UI, REST API, CLI)
│       ├── cli.py                      # Typer CLI application commands
│       ├── rest/                       # FastAPI REST API routers (/ml, /items) & server runner
│       └── ui/                         # Streamlit UI app, tabs, and local assets
└── tests/                              # Pytest test suite & static type verification
    ├── conftest.py                     # Test fixtures
    ├── test_ml_api.py                  # ML REST API endpoint test suite
    ├── test_ml_pipeline.py             # ML training, ONNX export & drift test suite
    ├── test_api.py                     # Item REST API test suite
    └── test_static.py                  # Pyright static type checker suite
```
