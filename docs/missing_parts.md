Listed directory sg_project_template
Viewed ARCHITECTURE.md:1-331
Listed directory .github
Listed directory workflows
Viewed cml_train_eval.yaml:1-74
Viewed compose.yaml:1-136
Viewed MLOPS_ROADMAP.md:1-181
Viewed serve_api.py:1-57
Searched for "kubernetes"
Viewed MLOPS_RATING.md:1-97

Your application (`sg_project_template`) is **directly related** to this entire ecosystem. In fact, it is designed as a **production-grade MLOps template using Clean Architecture**. 

Here is how your codebase maps to these topics, followed by a breakdown of what the missing concepts are and where they fit in production.

---

## 1. Status Overview: What’s in your code vs. what’s missing

| Category | Concept | Status in Your Codebase | Where / How |
| :--- | :--- | :---: | :--- |
| **Software Eng.** | **REST APIs** | ✅ **In Code** | [src/presentation/rest/serve_api.py](file:///Users/sglbl/codes/sg_project_template/src/presentation/rest/serve_api.py) & [src/presentation/rest/routers/ml.py](file:///Users/sglbl/codes/sg_project_template/src/presentation/rest/routers/ml.py) (FastAPI). |
| | **Async Programming** | ✅ **In Code** | Async request lifecycle, lifespan hooks, and async database drivers in [src/infra/postgres/database_async.py](file:///Users/sglbl/codes/sg_project_template/src/infra/postgres/database_async.py). |
| | **Microservices** | 🟡 **Partial** | Multi-container setup ([compose.yaml](file:///Users/sglbl/codes/sg_project_template/compose.yaml) runs API, UI, MLflow, RustFS, Postgres, Prometheus, Grafana). It’s a modular service stack, but not a full distributed microservices mesh. |
| | **Event-Driven Architectures** | ❌ **Not in Code** | Direct synchronous HTTP/REST calls are used instead of message brokers (Kafka/RabbitMQ/SQS). |
| **MLOps** | **Experiment Tracking** | ✅ **In Code** | [src/infra/ml/mlflow_tracker.py](file:///Users/sglbl/codes/sg_project_template/src/infra/ml/mlflow_tracker.py) backed by [src/domain/repo_interfaces/tracker_repository.py](file:///Users/sglbl/codes/sg_project_template/src/domain/repo_interfaces/tracker_repository.py) (MLflow logging metrics, parameters, artifacts). |
| | **Model Registry & Versioning** | ✅ **In Code** | [src/infra/ml/mlflow_tracker.py](file:///Users/sglbl/codes/sg_project_template/src/infra/ml/mlflow_tracker.py) with stage transitions (`Staging`, `Production`, `Archived`) in [src/domain/models/ml_entities.py](file:///Users/sglbl/codes/sg_project_template/src/domain/models/ml_entities.py). |
| | **Pipeline Orchestration** | ❌ **Not in Code** | Pipeline runs are driven by CLI commands ([src/application/services/ml_service.py](file:///Users/sglbl/codes/sg_project_template/src/application/services/ml_service.py)) and GitHub Actions, not a dedicated DAG orchestrator (Airflow, Step Functions, Dagster). |
| **Containers** | **Docker** | ✅ **In Code** | Multi-stage Dockerfiles ([docker/app.Dockerfile](file:///Users/sglbl/codes/sg_project_template/docker/app.Dockerfile), [docker/marimo.Dockerfile](file:///Users/sglbl/codes/sg_project_template/docker/marimo.Dockerfile)) and multi-service [compose.yaml](file:///Users/sglbl/codes/sg_project_template/compose.yaml). |
| | **Kubernetes (K8s)** | ❌ **Not in Code** | No Helm charts or Kubernetes manifests (`deployment.yaml`, `service.yaml`). Everything runs on single-node Docker Compose. |
| **Big Data** | **Databricks** | ❌ **Not in Code** | Datasets are processed locally via Pandas, Polars, Pandera, and DuckDB; no distributed Spark clusters. |
| **CI/CD DevOps**| **Automated Testing Pipelines** | ✅ **In Code** | [.github/workflows/cml_train_eval.yaml](file:///Users/sglbl/codes/sg_project_template/.github/workflows/cml_train_eval.yaml) runs `pytest` suites and automated CML pull-request evaluation reports. |
| | **GitOps Workflows** | ❌ **Not in Code** | No declarative cluster sync tools (e.g., ArgoCD, Flux CD). |
| | **Infrastructure as Code (IaC)**| ❌ **Not in Code** | No Terraform (`.tf`) or AWS CDK definitions for cloud infrastructure. |
| | **Blue-Green / Canary Deploy** | ❌ **Not in Code** | Deployments replace the single API container; no gradual traffic splitting. |

---

## 2. What are the missing concepts exactly?

Here is what each missing topic is, why companies use it, and how it relates to your project:

### 1. Event-Driven Architectures (EDA)
* **What it is:** In your current app, communication is **request-response** (Client $\rightarrow$ HTTP POST `/predict` $\rightarrow$ Model calculates $\rightarrow$ returns JSON). In an **event-driven architecture**, systems communicate asynchronously by emitting and listening to **events** via a message broker (e.g., Apache Kafka, RabbitMQ, AWS SQS/SNS).
* **Why use it:** Decoupling high-load systems. For example, instead of waiting 100ms for a real-time prediction, a client publishes an event (`TransactionCreated`), and multiple microservices consume it independently (e.g., Fraud Detection model, Notification Service, Audit Logger).
* **How it would fit:** Replacing or complementing the `/predict` FastAPI endpoint with a background consumer listening to a Kafka topic or RabbitMQ queue.

### 2. Pipeline Orchestration (Airflow, Step Functions, Dagster, Prefect)
* **What it is:** A platform to define, schedule, monitor, and retry multi-step data/ML workflows as **Directed Acyclic Graphs (DAGs)**.
* **Why use it:** Right now, your pipelines (`ingest` $\rightarrow$ `train` $\rightarrow$ `export` $\rightarrow$ `evaluate`) are run sequentially by local CLI commands or a GitHub Actions runner. If step 3 fails on a 50GB dataset, CLI scripts cannot easily resume from the failed step, distribute tasks across different worker machines, handle complex dependency schedules, or alert on failures.
* **How it would fit:** Converting your pipelines in [src/application/pipelines/](file:///Users/sglbl/codes/sg_project_template/src/application/pipelines) into tasks in an **Apache Airflow DAG** or **AWS Step Functions state machine**.

### 3. Kubernetes (K8s) (Basic Level)
* **What it is:** An open-source system for automating deployment, scaling, and management of containerized applications across a cluster of servers.
* **Why use it:** Docker Compose runs containers on a **single machine**. If that machine dies or traffic surges from 10 to 10,000 requests/second, Docker Compose cannot automatically spin up new instances on other servers. Kubernetes manages:
  * **Pods & Deployments:** Running and restarting multiple replicas of your API.
  * **Horizontal Pod Autoscaling (HPA):** Scaling up replicas when CPU/memory or inference queue exceeds a threshold.
  * **Self-healing:** Replacing crashed containers automatically.
* **How it would fit:** Converting your `api` service in [compose.yaml](file:///Users/sglbl/codes/sg_project_template/compose.yaml) into Kubernetes manifests or deploying it with **KServe** for autoscaling ML model inference.

### 4. Databricks (Basic Level)
* **What it is:** A cloud-based unified data analytics platform built around **Apache Spark**, **Delta Lake**, and managed MLflow.
* **Why use it:** When datasets grow from megabytes/gigabytes into hundreds of gigabytes or terabytes, single-node Python (Pandas/DuckDB) runs out of RAM (OOM errors). Databricks distributes data transformations and model training across clusters of distributed virtual machines.
* **How it would fit:** Running the heavy feature engineering and distributed model training on a Databricks cluster, while logging artifacts back to your MLflow registry.

### 5. GitOps Workflows (ArgoCD, Flux)
* **What it is:** An operational framework where **Git is the single source of truth** for your infrastructure and deployment state.
* **Why use it:** Instead of having a CI script run `docker deploy` or `kubectl apply` with sensitive cloud credentials inside GitHub Actions, an in-cluster agent (like ArgoCD) continuously monitors your Git repository. When a new image tag or config is merged into Git, ArgoCD pulls the change and reconciles the live cluster state.
* **How it would fit:** When your [.github/workflows/cml_train_eval.yaml](file:///Users/sglbl/codes/sg_project_template/.github/workflows/cml_train_eval.yaml) trains a new model and updates the production image tag, ArgoCD detects the Git commit and rolls out the new container.

### 6. Infrastructure as Code (IaC: Terraform, AWS CDK)
* **What it is:** Managing cloud resources (VPCs, S3 buckets, RDS PostgreSQL databases, Kubernetes clusters) through machine-readable definition files rather than clicking manually in AWS/GCP web consoles.
  * **Terraform:** Declarative syntax (HCL) that works across all cloud providers.
  * **AWS CDK:** Allows writing infrastructure definitions using programming languages (Python, TypeScript).
* **Why use it:** Repeatability, version control, and disaster recovery. You can destroy and recreate your entire production cloud stack with one command (`terraform apply`).
* **How it would fit:** A `terraform/` directory defining the AWS S3 bucket (replacing local RustFS), cloud PostgreSQL (replacing local Docker Postgres), and EKS (Kubernetes) cluster.

### 7. Blue-Green and Canary Deployments
* **What they are:** Advanced deployment strategies designed to release software or ML models with zero downtime and minimal risk:
  * **Blue-Green:** You run two identical production environments. *Blue* is live (v1.0). You deploy *Green* (v2.0). Once tested, the router instantly flips 100% of traffic from Blue to Green. If anything breaks, you flip back immediately.
  * **Canary:** You route a small percentage of real user traffic (e.g., 5%) to the new model (v2.0), while 95% remains on v1.0. You monitor metrics, latency, and drift. If healthy, you gradually ramp traffic to 25%, 50%, and 100%.
* **Why use it:** In ML, a newly trained model might pass unit tests but degrade user conversion or encounter unexpected production data drift. Canary deployments let you catch bad models before all users are affected.