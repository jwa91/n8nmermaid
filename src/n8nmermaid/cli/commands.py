# src/n8nmermaid/cli/commands.py
"""Typer command definitions for the n8nmermaid V2 CLI."""

import subprocess
from pathlib import Path
from typing import Annotated

import typer

from n8nmermaid.models_v2.request_v2_models import (
    DEFAULT_DIRECTION_V2,
    DEFAULT_SUBGRAPH_DIRECTION_V2,
    MermaidGenerationParamsV2,
    ReportGenerationParamsV2,
)
from n8nmermaid.utils.logging import setup_logging

from .enums import (
    CliMermaidDirection,
    CliReportFormat,
    CliReportType,
    CliSubgraphDisplayMode,
)
from .helpers import run_orchestration_v2

app = typer.Typer(
    name="n8nmermaid",
    help="Analyzes n8n workflow JSON files and generates Mermaid diagrams or reports.",
    add_completion=False,
)


@app.callback()
def main_callback():
    """Main entry point setup. Called before any command. Configures logging."""
    setup_logging()

@app.command("mermaid")
def generate_mermaid_diagram_v2(
    filepath: Annotated[
        Path,
        typer.Argument(
            exists=True,
            file_okay=True,
            dir_okay=False,
            readable=True,
            resolve_path=True,
            help="Path to the n8n workflow JSON file.",
        ),
    ],
    direction: Annotated[
        CliMermaidDirection,
        typer.Option(
            "--direction", "-d", case_sensitive=False, help="Flowchart direction."
        ),
    ] = DEFAULT_DIRECTION_V2,
    subgraph_direction: Annotated[
        CliMermaidDirection,
        typer.Option(
            "--subgraph-direction",
            case_sensitive=False,
            help="Direction within subgraphs.",
        ),
    ] = DEFAULT_SUBGRAPH_DIRECTION_V2,
    show_credentials: Annotated[
        bool,
        typer.Option("--show-creds", help="Display used credential names on nodes."),
    ] = False,
    show_key_parameters: Annotated[
        bool,
        typer.Option(
            "--show-params",
            help="Display key parameters (e.g., model names) on nodes.",
        ),
    ] = False,
    subgraph_display_mode: Annotated[
        CliSubgraphDisplayMode,
        typer.Option(
            "--subgraph-mode",
            case_sensitive=False,
            help=(
                "How to display clustered nodes: 'subgraph' (default), "
                "'simple_node' (hide details), 'separate_clusters' "
                "(simple main + separate files via --output-dir)."
            ),
        ),
    ] = CliSubgraphDisplayMode.SUBGRAPH.value,
    output_dir: Annotated[
        Path | None,
        typer.Option(
            "--output-dir",
            file_okay=False,
            dir_okay=True,
            writable=True,
            resolve_path=True,
            help=(
                "Save diagrams to files (main.mmd, <cluster_name>.mmd) "
                "in this directory instead of printing to stdout."
            ),
        ),
    ] = None,
):
    """
    Generates V2 Mermaid flowchart syntax from an n8n workflow file.

    Outputs the main diagram to stdout by default. If --output-dir is specified,
    saves the main diagram and any separate cluster diagrams (if using
    --subgraph-mode separate_clusters) to individual .mmd files in that directory.
    """
    if (
        subgraph_display_mode == CliSubgraphDisplayMode.SEPARATE_CLUSTERS
        and not output_dir
    ):
        typer.echo(
            "Error: --subgraph-mode separate_clusters requires --output-dir to be set.",
            err=True,
        )
        raise typer.Exit(code=1)

    mermaid_params = MermaidGenerationParamsV2(
        direction=direction.value,
        subgraph_direction=subgraph_direction.value,
        show_credentials=show_credentials,
        show_key_parameters=show_key_parameters,
        subgraph_display_mode=subgraph_display_mode.value,
    )

    run_orchestration_v2(
        filepath=filepath,
        command="generate_mermaid",
        mermaid_params=mermaid_params,
        output_dir=output_dir,
    )


@app.command("report")
def generate_analysis_report_v2(
    filepath: Annotated[
        Path,
        typer.Argument(
            exists=True,
            file_okay=True,
            dir_okay=False,
            readable=True,
            resolve_path=True,
            help="Path to the n8n workflow JSON file.",
        ),
    ],
    report_types: Annotated[
        list[CliReportType],
        typer.Option(
            "--type",
            "-t",
            case_sensitive=False,
            help=(
                "Type(s) of V2 report to generate (e.g., stats, agents, "
                "node_parameters, analysis_json). Combine multiple, but "
                "'analysis_json' should usually be used alone."
            ),
        ),
    ],
    output_format: Annotated[
        CliReportFormat,
        typer.Option(
            "--format",
            "-f",
            case_sensitive=False,
            help="Output format for the report.",
        ),
    ] = CliReportFormat.TEXT.value,
):
    """
    Generates one or more V2 analysis reports from an n8n workflow file.

    Combine multiple --type options (e.g., --type stats --type agents).
    Outputs the combined report content to stdout.
    The 'analysis_json' and 'node_parameters' types are best used alone.
    """
    if not report_types:
        typer.echo("Error: No report types specified. Use the --type option.", err=True)
        raise typer.Exit(code=1)

    report_type_values = [rt.value for rt in report_types]

    try:
        report_params = ReportGenerationParamsV2(
            report_types=report_type_values,
            output_format=output_format.value,
        )
    except ValueError as e:
        typer.echo(f"Error: Invalid report type combination: {e}", err=True)
        raise typer.Exit(code=1) from e

    run_orchestration_v2(
        filepath=filepath,
        command="generate_report",
        report_params=report_params,
    )


@app.command("serve")
def serve_api(
    host: Annotated[
        str, typer.Option("--host", help="The host to bind the server to.")
    ] = "127.0.0.1",
    port: Annotated[
        int, typer.Option("--port", help="The port to bind the server to.")
    ] = 8000,
    reload: Annotated[
        bool,
        typer.Option(
            "--reload", help="Enable auto-reload for development."
        ),
    ] = False,
):
    """
    Starts the FastAPI development server using Uvicorn.
    """
    app_path = "src.n8nmermaid.api.main:app"
    uvicorn_command = ["uvicorn", app_path, "--host", host, "--port", str(port)]

    if reload:
        uvicorn_command.append("--reload")

    typer.echo(f"Starting Uvicorn server for {app_path} on http://{host}:{port}")
    if reload:
        typer.echo("Reloading enabled.")

    try:
        process = subprocess.run(uvicorn_command, check=False)
        if process.returncode != 0:
            msg = f"Uvicorn server exited with code {process.returncode}"
            typer.echo(msg, err=True)
    except FileNotFoundError:
        err_msg = (
            "Error: 'uvicorn' command not found. Make sure uvicorn is "
            "installed and accessible in the environment's PATH."
        )
        typer.echo(err_msg, err=True)
        typer.echo(f"Attempted command: {' '.join(uvicorn_command)}", err=True)
        raise typer.Exit(code=1) from None
    except KeyboardInterrupt:
        typer.echo("\nServer stopped.")
        raise typer.Exit() from None
    except Exception as e:
        err_msg = (
            "An unexpected error occurred while trying to start the "
            f"server: {e}"
        )
        typer.echo(err_msg, err=True)
        raise typer.Exit(code=1) from e
