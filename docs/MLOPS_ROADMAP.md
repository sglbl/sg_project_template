# 🚀 2026 Modern MLOps Transformation Blueprint

This document specifies the exact package additions, architecture modifications, data & artifact management conventions, and GitHub CI/CD workflows required to upgrade `sg_project_template` into a **2026 production-grade MLOps template**.

---

## 📦 1. Package Additions (`pyproject.toml`)

Install the following packages using `uv add` to equip the scaffold with experiment tracking, data versioning, model optimization, drift detection, and automated CML pipelines:

```bash
# Core Experiment Tracking & Registry
uv add --group=mlops "mlflow>=2.15.0" "optuna>=3.6.0"

# Data Versioning & Feature Store
uv add --group=mlops "dvc[s3]>=3.50.0" "pandera[polars]>=0.20.0"

# Drift Monitoring & Validation
uv add --group=mlops "evidently>=0.4.30"

# Model Training & High-Speed Serving Runtime
uv add --group=mlops "scikit-learn>=1.5.0" "xgboost>=2.1.0" "onnx>=1.16.0" "onnxruntime>=1.18.0"
```

---

## 🏛️ 2. Clean / Onion Architecture Integration (`src/`)

All MLOps code strictly follows the repository standards in `.agents/AGENTS.md`:
- **No `__init__.py` files** anywhere in `src/`.
- All internal imports use explicit `src.X` prefixes.
- Loguru logger and Pydantic Settings (`UPPERCASE` environment variables).

```bash
src/
├── domain/
│   ├── entities/
│   │   ├── dataset.py            # Dataset schemas, splits & version metadata
│   │   ├── model.py              # Model metrics, version status & registry tags
│   │   └── prediction.py         # Prediction request & response domain schemas
│   └── repo_interfaces/
│       ├── tracker.py            # Abstract Base Class for MLflow/W&B tracking
│       ├── registry.py           # Abstract Base Class for Model Registry
│       ├── feature_store.py      # Abstract Base Class for DuckDB/Polars feature store
│       └── storage.py            # Abstract Base Class for Artifact & Data storage (S3/MinIO)
├── application/
│   ├── pipelines/
│   │   ├── ingest.py             # Data loader, validation with Pandera & feature creation
│   │   ├── train.py              # Training loop, Optuna tuning & evaluation
│   │   ├── evaluate.py           # Model quality checks, metric logging & drift detection
│   │   └── export.py             # Serialization & ONNX model format conversion
│   └── services/
│       ├── ml_service.py         # Orchestrates data ingestion -> train -> eval -> register
│       └── inference_service.py     # Production inference engine backed by ONNX Runtime
├── infra/
│   ├── ml/
│   │   ├── mlflow_tracker.py     # MLflow implementation of tracker & registry
│   │   ├── dvc_storage.py        # DVC & MinIO/S3 data management provider
│   │   └── feature_store.py      # DuckDB analytical feature storage implementation
│   └── serving/
│       └── onnx_engine.py        # High-performance ONNX inference engine
└── presentation/
    ├── cli.py                    # Typer commands (train, eval, export, drift, sync-data)
    ├── rest/
    │   └── routes/ml.py          # FastAPI model endpoints (/v1/predict, /v1/models/active)
    └── ui/
        └── app_ui.py             # Streamlit Dashboard (Registry, Drift, Prediction Sandbox)
```

### 🏛️ 2.1 Architectural Rationale: Domain Protocols, Dataclasses & BaseModels

#### Why Repository Interfaces (`typing.Protocol`) in MLOps?
In standard CRUD apps, interfaces can sometimes feel verbose. However, in **MLOps, interfaces are crucial**:
1. **Lightweight Unit Tests without Mocking Infrastructure**: Pipelines (`train.py`, `evaluate.py`) can be tested using an in-memory 10-line `DummyTracker` in milliseconds, without spinning up MLflow or Docker.
2. **Vendor Independence**: Switching from MLflow to Weights & Biases (W&B), or from local RustFS to AWS S3, requires only writing a single new provider file under `src/infra/`. Zero pipeline or business logic changes.
3. **Zero Runtime Overhead (`typing.Protocol`)**: Unlike `abc.ABC`, Python `Protocol` uses **structural typing (duck typing)**. Classes do not need to explicitly inherit from the interface. Static type checkers (`pyright`, `mypy`) validate contracts during CI/CD with **0% runtime cost**.

#### When to use `dataclass` vs `pydantic.BaseModel`:
- **`dataclass` (Domain Entities in `src/domain/models/`)**: Pure internal Python data structures (`ModelMetadata`, `DatasetMetadata`). They have no serialization overhead, require no Pydantic runtime parsing, and represent core business models.
- **`pydantic.BaseModel` (Schemas in `src/domain/schemas/`)**: External boundary contracts (`PredictRequest`, `PredictResponse`). They provide runtime input validation, type coercion, JSON serialization/deserialization, and automatic OpenAPI documentation generation for FastAPI.

#### Naming Conventions in `src/domain/`:
- **Avoid syntax-based names** (e.g. `data_classes.py`, `pydantic_schemas.py`): The folder name (`models/`, `schemas/`) already conveys the construct type.
- **Use domain-capability names**:
  - `src/domain/models/llm_models.py` (LLM configs and prompts)
  - `src/domain/models/ml_entities.py` (Model, Dataset & Evaluation domain entities)
  - `src/domain/schemas/common.py` (Generic API response envelopes)
  - `src/domain/schemas/ml_schemas.py` (Prediction and drift check API payloads)

---

## 📊 3. Data & Artifacts Management Structure

```bash
data/
├── raw/                # Ingested datasets (Tracked via DVC: dvc add data/raw)
├── processed/          # Validated & cleaned tabular data
└── features/           # DuckDB / Parquet feature store files
artifacts/
├── models/             # Local binary models (.pkl, .onnx)
├── metrics/            # Training metrics JSON summary
└── reports/            # Evidently data drift & model evaluation HTML/JSON reports
```

---

## 💾 3.1 Storage Strategy: RustFS / MinIO (S3-Compatible) vs. NAS

### What is MinIO and RustFS?
- **MinIO**: A widely-used open-source **S3-compatible Object Store** (written in Go) that runs locally or in Docker. It provides local AWS S3 bucket endpoints (`s3://...` at `http://localhost:9000`).
- **RustFS (e.g., Garage FS)**: A modern, ultra-high-performance **S3-compatible Object Store** written in **Rust**. It provides the exact same S3 API as MinIO and AWS S3, but with lower memory overhead, zero garbage collection pauses, and faster I/O.
- **Key Takeaway**: MinIO and RustFS are drop-in S3-compatible alternatives to each other. Both allow MLflow and DVC to use cloud-native `s3://` URLs locally without needing code changes when deploying to AWS/GCP S3.

### Why RustFS / MinIO over NAS?
- **Cloud Native (`s3://` API standard)**: DVC and MLflow communicate natively via S3 protocol (`s3://dvc-data` and `s3://mlflow-artifacts`).
- **High Speed & Low RAM**: Eliminates slow NFS file-locking overhead when handling millions of small parquet files or image batches.
- **100% Containerized**: Runs in `compose.yaml` with zero dependency on host file system network mounts.

### Environment Setup (`.env`)
```env
# S3 / RustFS / MinIO Storage Configuration
AWS_ACCESS_KEY_ID=minioadmin
AWS_SECRET_ACCESS_KEY=minioadmin
AWS_ENDPOINT_URL=http://localhost:9000
MLFLOW_S3_ENDPOINT_URL=http://localhost:9000
DVC_S3_ENDPOINT_URL=http://localhost:9000
```


## ⚡ 4. CLI Commands (`python -m src.main`)

```bash
# Data ingestion & schema validation
python -m src.main ingest --data-path data/raw/sample.csv

# Train model & log to MLflow
python -m src.main train --experiment-name iris-baseline --tune

# Evaluate model & detect data/concept drift
python -m src.main eval --model-uri models:/iris-baseline/1 --report-out artifacts/reports

# Export model to ONNX runtime format
python -m src.main export-onnx --model-path artifacts/models/model.pkl --out artifacts/models/model.onnx

# Run production REST API & Streamlit Dashboard
python -m src.main api
python -m src.main ui
```

---

## 🔄 5. Continuous Machine Learning (CML) & GitHub Actions

Create `.github/workflows/cml_train_eval.yaml`:

```yaml
name: MLOps Training & Evaluation Pipeline

on:
  push:
    branches: [ main, mlops ]
  pull_request:
    branches: [ main ]

jobs:
  train-and-eval:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: iterative/setup-cml@v1
      - uses: astral-sh/setup-uv@v3
        with:
          version: "latest"

      - name: Install Dependencies
        run: uv sync --frozen

      - name: Execute Model Training & Evaluation
        run: |
          uv run python -m src.main train
          uv run python -m src.main eval

      - name: Publish CML Report to PR
        env:
          REPO_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: |
          echo "## 📈 Model Training & Evaluation Report" > report.md
          echo "### Performance Metrics" >> report.md
          cat artifacts/metrics/summary.md >> report.md
          
          echo "### Data & Concept Drift" >> report.md
          cml-publish artifacts/reports/drift_plot.png --md >> report.md

          cml comment create report.md
```

---

## 🐳 6. Multi-Service Infrastructure (`compose.yaml`)

```yaml
name: sgproject-mlops

services:
  api:
    build:
      context: .
      dockerfile: docker/ui.Dockerfile
    command: python -m src.main api
    ports:
      - "8000:8000"
    environment:
      - MLFLOW_TRACKING_URI=http://mlflow:5000
      - DB_HOST=postgres

  ui:
    build:
      context: .
      dockerfile: docker/ui.Dockerfile
    ports:
      - "8501:8501"
    environment:
      - MLFLOW_TRACKING_URI=http://mlflow:5000

  marimo:
    build:
      context: .
      dockerfile: docker/marimo.Dockerfile
    ports:
      - "2719:2718"

  mlflow:
    image: ghcr.io/mlflow/mlflow:v2.15.0
    container_name: mlflow_server
    ports:
      - "5000:5000"
    command: mlflow server --backend-store-uri postgresql://postgres:postgres@postgres:5432/mlflow --default-artifact-root s3://mlflow-artifacts/ --host 0.0.0.0

  # S3 Object Storage Service (MinIO or RustFS)
  minio:
    image: minio/minio:RELEASE.2024-05-28T17-19-04Z
    container_name: s3_storage_server
    ports:
      - "9000:9000"
      - "9001:9001"
    environment:
      - MINIO_ROOT_USER=minioadmin
      - MINIO_ROOT_PASSWORD=minioadmin
    command: server /data --console-address ":9001"

  postgres:
    image: postgres:16-alpine
    environment:
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=postgres
      - POSTGRES_DB=postgres
    ports:
      - "5432:5432"
```

---

## ✅ Implementation Steps Checklist

- [ ] **Step 1:** Add dependencies to `pyproject.toml` (`mlflow`, `optuna`, `dvc`, `pandera`, `evidently`, `onnxruntime`, `scikit-learn`, `xgboost`).
- [ ] **Step 2:** Extend `src/config.py` with ML settings (`MLFLOW_TRACKING_URI`, `MINIO_ENDPOINT_URL`, `MODEL_ARTIFACTS_DIR`).
- [ ] **Step 3:** Define domain interfaces (`src/domain/repo_interfaces/tracker.py`, `registry.py`, `feature_store.py`).
- [ ] **Step 4:** Implement pipeline modules (`src/application/pipelines/ingest.py`, `train.py`, `evaluate.py`, `export.py`).
- [ ] **Step 5:** Implement ML services & providers (`src/infra/ml/mlflow_tracker.py`, `src/infra/serving/onnx_engine.py`).
- [ ] **Step 6:** Add CLI commands to `src/presentation/cli.py` (`train`, `eval`, `export-onnx`, `drift`).
- [ ] **Step 7:** Add prediction routes in `src/presentation/rest/routes/ml.py` and UI tabs in `src/presentation/ui/app_ui.py`.
- [ ] **Step 8:** Add CML GitHub Action workflow (`.github/workflows/cml_train_eval.yaml`).
- [ ] **Step 9:** Update `compose.yaml` with MLflow & MinIO containers.
