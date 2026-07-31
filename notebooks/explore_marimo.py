import marimo

__generated_with = "0.23.15"
app = marimo.App(
    width="full",
    app_title="SG Project Template — Interactive Analytics & Plotly Exploration",
    auto_download=["ipynb"],
)


@app.cell
def _():
    import marimo as mo
    import plotly.express as px

    return mo, px


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # SG Project Template — Interactive Analytics & Plotly Exploration (Polars)

    Welcome to the interactive **Marimo** analysis dashboard for **SG Project Template**.

    ### Dashboard Features:
    - ⚡ **Polars Powered Data Processing**: High-performance Polars DataFrames for metrics manipulation.
    - 📈 **Interactive Plotly Charts**: Time series trends, performance distributions, and aggregated model benchmarks.
    - 🎛️ **Reactive Controls**: Adjust sample sizes, model selections, and primary metrics in real-time.
    - 🏗️ **Clean Architecture Integration**: Seamless imports from `src.config` and `src.infra.logging`.
    """)
    return


@app.cell
def _(mo):
    mo.md("""
    ## 1. Project Configuration & Setup
    """)
    return


@app.cell
def _():
    import sys
    from pathlib import Path

    # Ensure project root is in sys.path when executed in marimo
    _PROJECT_ROOT = Path(__file__).resolve().parent.parent
    if str(_PROJECT_ROOT) not in sys.path:
        sys.path.insert(0, str(_PROJECT_ROOT))

    from src.config import settings
    from src.infra.logging import setup_logger

    setup_logger(level=settings.LOG_LEVEL)
    return (settings,)


@app.cell
def _(mo, settings):
    mo.md(f"""
    ### Environment Status
    - **Database Host**: `{settings.DB_HOST}:{settings.DB_PORT}`
    - **Database Name**: `{settings.DB_NAME}`
    - **Log Level**: `{settings.LOG_LEVEL}`
    """)
    return


@app.cell
def _(mo):
    mo.md("""
    ## 2. Interactive Analytics Controls
    """)
    return


@app.cell
def _(mo):
    sample_slider = mo.ui.slider(start=20, stop=300, step=10, value=100, label="Sample Data Points per Model")
    model_selector = mo.ui.multiselect(
        options=["llama3.1", "gemma", "gpt-4o-mini"],
        value=["llama3.1", "gemma", "gpt-4o-mini"],
        label="Select Models to Compare",
    )
    metric_selector = mo.ui.dropdown(
        options=["latency_ms", "tokens_per_sec", "memory_mb"],
        value="latency_ms",
        label="Primary Metric",
    )

    mo.hstack([sample_slider, model_selector, metric_selector])
    return model_selector, sample_slider, metric_selector


@app.cell
def _(model_selector, sample_slider):
    import uuid
    from datetime import datetime, timedelta
    import numpy as np
    import polars as pl

    np.random.seed(42)

    selected_models = model_selector.value if model_selector.value else ["llama3.1"]
    n_per_model = sample_slider.value
    total_samples = n_per_model * len(selected_models)

    endpoints = ["/v1/chat/completions", "/v1/embeddings", "/v1/items"]
    endpoint_weights = [0.6, 0.25, 0.15]

    model_profiles = {
        "llama3.1": {"base_latency": 140, "latency_std": 25, "tokens_base": 45, "mem_mb": 4096, "cost_per_1k": 0.0015},
        "gemma": {"base_latency": 95, "latency_std": 15, "tokens_base": 65, "mem_mb": 2048, "cost_per_1k": 0.0008},
        "gpt-4o-mini": {"base_latency": 110, "latency_std": 18, "tokens_base": 55, "mem_mb": 1024, "cost_per_1k": 0.0005},
    }

    start_time = datetime.now() - timedelta(hours=2)
    time_deltas = np.sort(np.random.uniform(0, 7200, total_samples))

    data_rows = []
    for idx in range(total_samples):
        model_name = selected_models[idx % len(selected_models)]
        profile = model_profiles.get(model_name, model_profiles["llama3.1"])

        req_id = f"req_{idx+1:04d}_{uuid.uuid4().hex[:4]}"
        timestamp = (start_time + timedelta(seconds=float(time_deltas[idx]))).strftime("%Y-%m-%d %H:%M:%S")
        endpoint = str(np.random.choice(endpoints, p=endpoint_weights))

        latency = max(15.0, round(float(np.random.normal(profile["base_latency"], profile["latency_std"])), 2))
        tokens = max(5, int(np.random.normal(profile["tokens_base"], 10)))
        mem_mb = max(512.0, round(float(profile["mem_mb"] + np.random.normal(0, 150)), 1))
        status = str(np.random.choice(["200 OK", "429 Rate Limit", "500 Error"], p=[0.92, 0.05, 0.03]))
        cost = round(float((tokens / 1000.0) * profile["cost_per_1k"]), 6)

        data_rows.append(
            {
                "request_id": req_id,
                "timestamp": timestamp,
                "model": model_name,
                "endpoint": endpoint,
                "latency_ms": latency,
                "tokens_per_sec": tokens,
                "memory_mb": mem_mb,
                "cost_usd": cost,
                "status": status,
            }
        )

    df_metrics = pl.DataFrame(data_rows).sort("timestamp", descending=True)
    return datetime, df_metrics, np, pl, timedelta, uuid


@app.cell
def _(mo):
    mo.md("""
    ## 3. Plotly Visualizations & Benchmarks
    """)
    return


@app.cell
def _(df_metrics, metric_selector, mo, px):
    metric_name_line = metric_selector.value

    # 1. Time-series Line Chart (Polars DataFrame)
    fig_line = px.line(
        df_metrics,
        x="timestamp",
        y=metric_name_line,
        color="model",
        title=f"📈 Time-Series Trend ({metric_name_line})",
        labels={metric_name_line: metric_name_line.replace("_", " ").title(), "timestamp": "Timestamp"},
        template="plotly_dark",
    )
    fig_line.update_layout(height=450, margin=dict(l=20, r=20, t=50, b=20))

    mo.ui.plotly(fig_line)
    return fig_line, metric_name_line


@app.cell
def _(df_metrics, metric_selector, mo, px):
    metric_name_box = metric_selector.value

    # 2. Box Plot Distribution (Polars DataFrame)
    fig_box = px.box(
        df_metrics,
        x="model",
        y=metric_name_box,
        color="model",
        points="all",
        title=f"📊 Distribution & Outliers by Model ({metric_name_box})",
        template="plotly_dark",
    )
    fig_box.update_layout(height=450, margin=dict(l=20, r=20, t=50, b=20))

    mo.ui.plotly(fig_box)
    return fig_box, metric_name_box


@app.cell
def _(df_metrics, mo, pl, px):
    # 3. Model Benchmark Summary Bar Chart (Polars Group-By Aggregation)
    df_summary = (
        df_metrics.group_by("model")
        .agg(
            pl.col("latency_ms").mean().alias("avg_latency_ms"),
            pl.col("tokens_per_sec").mean().alias("avg_tokens_sec"),
            pl.col("memory_mb").mean().alias("avg_memory_mb"),
            pl.len().alias("total_requests"),
        )
    )

    fig_bar = px.bar(
        df_summary,
        x="model",
        y="avg_latency_ms",
        color="model",
        text_auto=".1f",
        title="⚡ Average Latency Comparison (ms)",
        template="plotly_dark",
    )
    fig_bar.update_layout(height=450, margin=dict(l=20, r=20, t=50, b=20))

    mo.ui.plotly(fig_bar)
    return df_summary, fig_bar


@app.cell
def _(mo):
    mo.md("""
    ## 4. Live API Request Log (Polars)
    """)
    return


@app.cell
def _(df_metrics, mo):
    mo.ui.table(df_metrics, pagination=True)
    return


if __name__ == "__main__":
    app.run()
