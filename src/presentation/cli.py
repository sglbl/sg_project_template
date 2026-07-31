"""CLI interface powered by Typer and Rich."""

import sys
from pathlib import Path
import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from src.version import __version__

app = typer.Typer(
    name="sg-project-template",
    help="SG Project Template CLI",
    add_completion=False,
    no_args_is_help=True,
)
console = Console()


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
    llm: str = typer.Option("llama3.1", "--llm", help="LLM model to run (e.g. gemma, llama3.1, none)"),
    embedding: str = typer.Option("bge-m3", "--embedding", help="Embedding model to run (e.g. bge-m3, nomic-embed-text-v1)"),
) -> None:
    """Run the Gradio UI presentation server."""
    console.print(f"[bold green]Starting UI application (LLM: {llm}, Embedding: {embedding})...[/bold green]")
    try:
        from src.presentation.ui.app_ui import run_ui as launch_ui
        from src.presentation.bootstrap import create_services

        services = create_services(model="postgres")
        launch_ui(services=services)
    except Exception as e:
        console.print(f"[bold red]Failed to start UI application:[/bold red] {e}")
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
