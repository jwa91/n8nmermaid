# src/n8nmermaid/cli/helpers.py
"""Helper functions for the V2 CLI commands."""

import logging
import sys
from pathlib import Path
from typing import Any

import typer

from n8nmermaid.core.generators.mermaid_v2.helpers import sanitize_filename
from n8nmermaid.core.orchestrator_v2 import OrchestratorErrorV2, process_v2
from n8nmermaid.models_v2.request_v2_models import (
    AnalysisRequestV2,
    MermaidGenerationParamsV2,
    ReportGenerationParamsV2,
    RequestCommand,
)
from n8nmermaid.utils import loaders

logger = logging.getLogger(__name__)


def _handle_orchestration_error(err: Exception, context: str):
    """Logs and reports orchestration errors."""
    logger.error("%s failed: %s", context, err, exc_info=False)
    logger.debug("%s error details:", context, exc_info=True)
    typer.echo(f"Error: {err}", err=True)
    raise typer.Exit(code=1) from err


def _handle_unexpected_error(err: Exception, context: str):
    """Logs and reports unexpected errors."""
    logger.exception("An unexpected error occurred during %s.", context)
    typer.echo(f"An unexpected error occurred: {err}", err=True)
    raise typer.Exit(code=1) from err


def _load_workflow_data(filepath: Path) -> dict[str, Any]:
    """Loads workflow data from a file, handling errors."""
    logger.debug("Loading workflow file: %s", filepath)
    try:
        workflow_data = loaders.load_workflow_from_file(filepath)
        if workflow_data is None:
            logger.critical(
                "Failed to load workflow JSON from %s (returned None).", filepath
            )
            typer.echo(
                f"Error: Could not load or parse workflow file: {filepath}",
                err=True,
            )
            raise typer.Exit(code=1)
        return workflow_data
    except Exception as e:
        logger.critical(
            "Failed during workflow file loading from %s: %s", filepath, e
        )
        typer.echo(
            f"Error: Could not load workflow file: {filepath}. Reason: {e}",
            err=True,
        )
        raise typer.Exit(code=1) from e


def _build_analysis_request(
    workflow_data: dict[str, Any],
    command: RequestCommand,
    mermaid_params: MermaidGenerationParamsV2 | None,
    report_params: ReportGenerationParamsV2 | None,
) -> AnalysisRequestV2:
    """Constructs the V2 analysis request."""
    logger.debug("Constructing AnalysisRequestV2...")
    try:
        effective_mermaid_params = (
            mermaid_params
            if mermaid_params is not None
            else MermaidGenerationParamsV2()
        )
        request = AnalysisRequestV2(
            workflow_data=workflow_data,
            command=command,
            mermaid_params=effective_mermaid_params,
            report_params=report_params,
        )
        return request
    except Exception as e:
        logger.error("Failed to create AnalysisRequestV2: %s", e, exc_info=True)
        typer.echo(
            f"Error: Invalid parameters for request construction: {e}", err=True
        )
        raise typer.Exit(code=1) from e


def _handle_mermaid_output(result: str | dict[str, str], output_dir: Path | None):
    """Handles output for the generate_mermaid command."""
    if not isinstance(result, dict):
        logger.error(
            "OrchestratorV2 returned unexpected type (%s) for generate_mermaid.",
            type(result).__name__,
        )
        typer.echo("Error: Unexpected output format from generator.", err=True)
        raise typer.Exit(code=1)

    if output_dir:
        save_diagrams_to_dir(result, output_dir)
    else:
        main_diagram = result.get("main", "")
        if main_diagram:
            typer.echo(main_diagram.strip())
        else:
            logger.warning(
                "OrchestratorV2 returned dict, but 'main' key missing/empty."
            )
            typer.echo(
                "Error: Failed to retrieve main diagram content.", err=True
            )
            raise typer.Exit(code=1)


def _handle_report_output(result: str | dict[str, str]):
    """Handles output for the generate_report command."""
    if isinstance(result, str):
        typer.echo(result.strip())
    else:
        logger.error(
            "OrchestratorV2 returned unexpected type (%s) for generate_report.",
            type(result).__name__,
        )
        typer.echo("Error: Unexpected output format for report.", err=True)
        raise typer.Exit(code=1)


def run_orchestration_v2(
    filepath: Path,
    command: RequestCommand,
    mermaid_params: MermaidGenerationParamsV2 | None = None,
    report_params: ReportGenerationParamsV2 | None = None,
    output_dir: Path | None = None,
):
    """
    Handles the core V2 process: load data, build request, run orchestrator.

    Manages output based on the command and whether `output_dir` is specified.
    Uses V2 analysis and generation components.

    Args:
        filepath: Path to the input workflow JSON file.
        command: The command to execute ('generate_mermaid' or 'generate_report').
        mermaid_params: Parameters for V2 Mermaid generation (if applicable).
        report_params: Parameters for V2 report generation (if applicable).
        output_dir: Optional directory to save output files to (Mermaid only).

    Raises:
        typer.Exit: On critical errors like file loading or orchestration failure.
    """
    workflow_data = _load_workflow_data(filepath)

    request = _build_analysis_request(
        workflow_data, command, mermaid_params, report_params
    )

    logger.debug("Calling V2 core process function...")
    try:
        result: str | dict[str, str] = process_v2(request=request)
        logger.info("OrchestrationV2 successful.")

        if command == "generate_mermaid":
            _handle_mermaid_output(result, output_dir)
        elif command == "generate_report":
            _handle_report_output(result)
        else:
            logger.error("Reached unexpected state in V2 output handling.")
            raise typer.Exit(code=1)

    except OrchestratorErrorV2 as e:
        _handle_orchestration_error(e, "OrchestrationV2")
    except Exception as e:
        _handle_unexpected_error(e, "V2 orchestration")


def save_diagrams_to_dir(diagrams: dict[str, str], output_dir: Path):
    """
    Saves multiple Mermaid diagrams to files in a specified directory.

    Uses sanitize_filename helper to create safe filenames from dict keys.
    Ensures directory exists and handles potential write errors.

    Args:
        diagrams: Dictionary where keys are identifiers (e.g., "main", sanitized
            cluster names) and values are Mermaid diagram strings.
        output_dir: The directory Path object to save files into.

    Raises:
        typer.Exit: If the directory cannot be created or files written.
    """
    try:
        output_dir.mkdir(parents=True, exist_ok=True)
        logger.info("Saving output diagrams to directory: %s", output_dir)
        saved_files = 0
        write_errors = 0

        for key, diagram_string in diagrams.items():
            if not diagram_string or not diagram_string.strip():
                logger.warning("Skipping empty diagram string for key '%s'.", key)
                continue

            safe_filename_base = sanitize_filename(key, default=f"diagram_{key}")
            output_file = output_dir / f"{safe_filename_base}.mmd"

            try:
                with open(output_file, "w", encoding="utf-8") as f:
                    f.write(diagram_string)
                logger.debug("Saved diagram to %s", output_file)
                saved_files += 1
            except OSError as io_err:
                logger.error(
                    "Failed to write diagram file %s: %s", output_file, io_err
                )
                typer.echo(f"Error: Could not write file {output_file}", err=True)
                write_errors += 1

        if write_errors == 0 and saved_files > 0:
            typer.echo(
                f"Successfully saved {saved_files} diagram(s) to '{output_dir}/'",
                file=sys.stderr,
            )
        elif saved_files > 0:
            msg = (
                f"Saved {saved_files} diagram(s) to '{output_dir}/' "
                f"with {write_errors} errors."
            )
            typer.echo(msg, file=sys.stderr, err=True)
        elif write_errors > 0:
            typer.echo(
                f"Failed to save any diagrams due to {write_errors} errors.",
                err=True,
            )
        else:
            typer.echo(
                "No diagrams were generated or available to save.", file=sys.stderr
            )

        if write_errors > 0:
            raise typer.Exit(code=1)

    except Exception as dir_err:
        logger.exception(
            "Failed to create or write to output directory %s", output_dir
        )
        typer.echo(
            f"Error: Could not use output directory {output_dir}. "
            f"Reason: {dir_err}",
            err=True,
        )
        raise typer.Exit(code=1) from dir_err
