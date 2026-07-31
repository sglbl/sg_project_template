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
        serve_api.run_api()
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

    console.print(table)


if __name__ == "__main__":
    app()
