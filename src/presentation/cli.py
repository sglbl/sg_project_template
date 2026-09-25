"""CLI interface powered by Typer and Rich."""

import sys
from pathlib import Path
import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from src.version import __version__
from src.config import settings
from src.infra.logging import setup_logger

app = typer.Typer(
    name="sg-project-template",
    help="SG Project Template CLI",
    add_completion=False,
    no_args_is_help=True,
)
console = Console()


@app.callback()
def main_callback() -> None:
    """Initialize logging configuration."""
    setup_logger(level=settings.LOG_LEVEL)


@app.command()
def version() -> None:
    """Show the application version and status."""
    console.print(
        Panel.fit(
            f"[bold green]SG Project Template[/bold green] v{__version__}\n"
            "[dim]Python 3.12+ Clean Architecture Template[/dim]",
            title="Version Info",
            border_style="cyan",
        )
    )


@app.command()
def api(
    host: str = typer.Option("0.0.0.0", help="Host to bind API server"),
    port: int = typer.Option(8000, help="Port for API server"),
) -> None:
    """Run the REST API presentation server."""
    console.print(f"[bold blue]Starting API server on {host}:{port}...[/bold blue]")
    try:
        from src.presentation.rest import serve_api
        serve_api.run_api(host=host, port=port)
    except Exception as e:
        console.print(f"[bold red]Failed to start API server:[/bold red] {e}")
        raise typer.Exit(code=1)


@app.command()
def ui(
    port: int = typer.Option(8501, help="Port for Streamlit server"),
    host: str = typer.Option("0.0.0.0", help="Host address for Streamlit server"),
) -> None:
    """Run the Streamlit UI presentation server."""
    console.print(f"[bold green]Starting Streamlit UI on {host}:{port}...[/bold green]")
    import subprocess

    cmd = [
        "streamlit",
        "run",
        "src/presentation/ui/app_ui.py",
        "--server.address",
        host,
        "--server.port",
        str(port),
    ]
    try:
        subprocess.run(cmd, check=True)
    except Exception as e:
        console.print(f"[bold red]Failed to start Streamlit UI:[/bold red] {e}")
        raise typer.Exit(code=1)


@app.command()
def status() -> None:
    """Display environment and configuration status table."""
    table = Table(title="Application Status & Environment")
    table.add_column("Property", style="cyan", no_wrap=True)
    table.add_column("Value", style="magenta")

    from src.config import settings
    table.add_row("Database Host", settings.DB_HOST)
    table.add_row("Database Port", settings.DB_PORT)
    table.add_row("Database Name", settings.DB_NAME)
    table.add_row("Log Level", settings.LOG_LEVEL)
    table.add_row("MLflow Tracking URI", settings.MLFLOW_TRACKING_URI)
    table.add_row("MinIO / RustFS Endpoint", settings.MINIO_ENDPOINT_URL)
    table.add_row("Model Artifacts Dir", settings.MODEL_ARTIFACTS_DIR)

    console.print(table)


@app.command()
def ingest(
    data_path: str = typer.Option("data/raw/iris.csv", "--data-path", "-d", help="Path to raw CSV/Parquet file"),
    target_col: str = typer.Option("target", "--target-col", "-t", help="Target label column name"),
    dataset_name: str = typer.Option("dataset", "--name", "-n", help="Dataset identifier"),
    test_size: float = typer.Option(0.2, "--test-size", "-s", help="Ratio for test split (0.05 - 0.5)"),
) -> None:
    """Ingest raw data, validate schema, and create train/test parquet splits."""
    import polars as pl
    from pathlib import Path
    from src.application.pipelines.ingest import DataIngestionPipeline

    # Auto-generate sample dataset if default path doesn't exist
    path_obj = Path(data_path)
    if not path_obj.exists() and "iris" in data_path:
        from sklearn.datasets import load_iris
        path_obj.parent.mkdir(parents=True, exist_ok=True)
        iris = load_iris(as_frame=True)
        df_iris = iris.frame.copy()
        df_iris.columns = [c.replace(" (cm)", "").replace(" ", "_") for c in df_iris.columns]
        df_iris.to_csv(data_path, index=False)
        console.print(f"[dim yellow]Created sample iris dataset at {data_path}[/dim yellow]")

    console.print(f"[bold cyan]Ingesting dataset from {data_path}...[/bold cyan]")
    try:
        pipeline = DataIngestionPipeline()
        df = pipeline.load_data(data_path)
        pipeline.validate_schema(df, target_col=target_col)
        train_path, test_path, metadata = pipeline.split_and_save(
            df, target_col=target_col, test_size=test_size, dataset_name=dataset_name
        )

        table = Table(title=f"Dataset Ingested: {metadata.name}")
        table.add_column("Property", style="cyan")
        table.add_column("Value", style="green")
        table.add_row("Version (Hash)", metadata.version)
        table.add_row("Total Rows", str(metadata.num_rows))
        table.add_row("Features", f"{metadata.num_features} ({', '.join(metadata.feature_names)})")
        table.add_row("Train Split", train_path)
        table.add_row("Test Split", test_path)
        console.print(table)
    except Exception as e:
        console.print(f"[bold red]Ingestion failed:[/bold red] {e}")
        raise typer.Exit(code=1)


@app.command()
def train(
    train_path: str = typer.Option(None, "--train-path", help="Path to train parquet split"),
    test_path: str = typer.Option(None, "--test-path", help="Path to test parquet split"),
    target_col: str = typer.Option("target", "--target-col", "-t", help="Target column name"),
    model_name: str = typer.Option("random_forest", "--model-name", "-m", help="Model name"),
    tune: bool = typer.Option(False, "--tune", help="Optimize hyperparameters using Optuna"),
    export_onnx: bool = typer.Option(True, "--export-onnx/--no-onnx", help="Convert trained model to ONNX format"),
) -> None:
    """Train model, log metrics/artifacts to MLflow, and export to ONNX."""
    from pathlib import Path
    from src.application.services.ml_service import MLService
    from src.infra.ml.mlflow_tracker import MLflowTracker

    # If splits are not provided, auto-prepare sample dataset
    if not train_path or not test_path:
        default_train = Path("data/processed/dataset_train.parquet")
        default_test = Path("data/processed/dataset_test.parquet")
        if not default_train.exists():
            console.print("[dim]No train/test splits found. Running default ingestion...[/dim]")
            from src.application.pipelines.ingest import DataIngestionPipeline
            from sklearn.datasets import load_iris
            iris = load_iris(as_frame=True)
            df_iris = iris.frame.copy()
            df_iris.columns = [c.replace(" (cm)", "").replace(" ", "_") for c in df_iris.columns]
            sample_csv = Path("data/raw/iris.csv")
            sample_csv.parent.mkdir(parents=True, exist_ok=True)
            df_iris.to_csv(sample_csv, index=False)
            pipe = DataIngestionPipeline()
            df_pl = pipe.load_data(str(sample_csv))
            tr_p, te_p, _ = pipe.split_and_save(df_pl, target_col="target", dataset_name="dataset")
            train_path, test_path = tr_p, te_p
        else:
            train_path, test_path = str(default_train), str(default_test)

    console.print(f"[bold cyan]Training model '{model_name}' (Optuna tuning: {tune})...[/bold cyan]")
    try:
        tracker = MLflowTracker()
        ml_service = MLService(tracker=tracker, registry=tracker)
        pkl_path, onnx_path, metadata = ml_service.run_training(
            train_path=train_path,
            test_path=test_path,
            target_col=target_col,
            model_name=model_name,
            tune=tune,
            export_onnx=export_onnx,
        )

        table = Table(title=f"Training Results: {model_name}")
        table.add_column("Metric / Property", style="cyan")
        table.add_column("Value", style="green")
        for k, v in metadata.metrics.items():
            table.add_row(k.capitalize(), f"{v:.4f}")
        table.add_row("Pickle Artifact", pkl_path)
        if onnx_path:
            table.add_row("ONNX Model", onnx_path)
        table.add_row("Registry Version", metadata.version)
        table.add_row("Stage", metadata.stage.value)
        console.print(table)
    except Exception as e:
        console.print(f"[bold red]Training failed:[/bold red] {e}")
        raise typer.Exit(code=1)


@app.command()
def drift(
    ref_path: str = typer.Option("data/processed/dataset_train.parquet", "--ref-path", "-r", help="Reference baseline data path"),
    cur_path: str = typer.Option("data/processed/dataset_test.parquet", "--cur-path", "-c", help="Current data path to check"),
    report_name: str = typer.Option("drift_report", "--report-name", "-n", help="Report file name"),
) -> None:
    """Run Evidently data drift analysis between reference and current datasets."""
    from src.application.pipelines.evaluate import ModelEvaluationPipeline

    console.print(f"[bold cyan]Running Evidently data drift analysis...[/bold cyan]")
    try:
        eval_pipe = ModelEvaluationPipeline()
        drift_detected, drift_share, html_path = eval_pipe.run_drift_analysis(
            reference_data_path=ref_path,
            current_data_path=cur_path,
            report_name=report_name,
        )

        status_style = "bold red" if drift_detected else "bold green"
        status_text = "DRIFT DETECTED" if drift_detected else "NO DRIFT"

        table = Table(title="Evidently Drift Analysis Summary")
        table.add_column("Property", style="cyan")
        table.add_column("Value", style=status_style)
        table.add_row("Drift Status", status_text)
        table.add_row("Drift Share", f"{drift_share:.2%}")
        table.add_row("HTML Report", html_path)
        console.print(table)
    except Exception as e:
        console.print(f"[bold red]Drift check failed:[/bold red] {e}")
        raise typer.Exit(code=1)


@app.command(name="export-onnx")
def export_onnx_cmd(
    model_pkl: str = typer.Option("data/models/random_forest.pkl", "--model-pkl", "-m", help="Path to pickled model artifact"),
    output_onnx: str = typer.Option(None, "--out", "-o", help="Destination ONNX model path"),
) -> None:
    """Export a trained scikit-learn model to ONNX runtime format."""
    from src.application.pipelines.export import ModelExportPipeline

    console.print(f"[bold cyan]Exporting {model_pkl} to ONNX format...[/bold cyan]")
    try:
        export_pipe = ModelExportPipeline()
        onnx_path = export_pipe.export_to_onnx(model_pkl_path=model_pkl, output_onnx_path=output_onnx)
        console.print(
            Panel.fit(
                f"[bold green]Successfully exported ONNX model![/bold green]\n"
                f"[dim]Output path: {onnx_path}[/dim]",
                title="ONNX Export",
                border_style="green",
            )
        )
    except Exception as e:
        console.print(f"[bold red]ONNX export failed:[/bold red] {e}")
        raise typer.Exit(code=1)


@app.command()
def predict(
    features_json: str = typer.Option('{"sepal_length": 5.1, "sepal_width": 3.5, "petal_length": 1.4, "petal_width": 0.2}', "--features", "-f", help="JSON dictionary of features"),
    model_path: str = typer.Option(None, "--model-path", "-m", help="Optional path to model (.onnx or .pkl)"),
) -> None:
    """Execute prediction using InferenceService."""
    import json
    from src.application.services.inference_service import InferenceService
    from src.domain.schemas.ml_schemas import PredictRequest

    try:
        feat_dict = json.loads(features_json)
        service = InferenceService(model_path=model_path)
        req = PredictRequest(features=feat_dict)
        res = service.predict(req)

        table = Table(title="Inference Result")
        table.add_column("Property", style="cyan")
        table.add_column("Value", style="green")
        table.add_row("Prediction", str(res.prediction))
        table.add_row("Model Name", res.model_name)
        table.add_row("Model Version", res.model_version)
        table.add_row("Latency", f"{res.execution_time_ms} ms")
        console.print(table)
    except Exception as e:
        console.print(f"[bold red]Prediction failed:[/bold red] {e}")
        raise typer.Exit(code=1)


if __name__ == "__main__":
    app()
