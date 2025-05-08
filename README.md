# n8nmermaid

[![Python Version](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)

Converts n8n workflow JSON files into Mermaid flowchart syntax (V2) or generates detailed analysis reports (V2).

## Overview

`n8nmermaid` is a Python tool to help understand and visualize n8n workflows. It takes an n8n workflow (exported as JSON) and can perform two main actions:

1.  **Generate Mermaid Diagrams:** Creates Mermaid flowchart syntax representing the workflow structure. This output can be used with tools that render Mermaid (like GitLab, GitHub, Obsidian, online editors). It offers different modes for displaying complex structures like AI Agents and their associated tools (as "clusters").
2.  **Generate Analysis Reports:** Produces structured reports summarizing various aspects of the workflow, such as node statistics, credential usage, AI Agent configurations, node parameters, or the complete raw analysis data in JSON format.

The tool provides a Command Line Interface (CLI) for easy use and an optional FastAPI interface.

## Key Features

- **n8n Workflow Analysis (V2):** Parses n8n JSON, analyzes node connections (including `main`, `ai_tool`, etc.), identifies node roles, and detects clustered structures (e.g., Agent setups).
- **Mermaid Diagram Generation (V2):**
  - Generates Mermaid `flowchart` syntax.
  * Supports different layout directions (`LR`, `TD`, etc.).
  * Customizable node labels (optionally showing credentials or parameters).
  * Multiple **Subgraph Display Modes** (`subgraph`, `simple_node`, `separate_clusters`) for handling clusters.
- **Analysis Report Generation (V2):**
  - Generates report types: `stats`, `credentials`, `agents`, `node_parameters`, `analysis_json`.
  * Supports output formats: `text`, `markdown`, `json`.
- **Command Line Interface:** Easy-to-use CLI built with Typer.
- **FastAPI Interface:** Provides HTTP endpoints for generation (see [API README](src/n8nmermaid/api/README.md)).
- **Configurable Logging:** Set log level and output target via `.env`.

## Installation

1.  **Prerequisites:**
    - Python >= 3.11
    - `uv` (recommended) or `pip`.
2.  **Clone the repository:**
    ```bash
    git clone [https://github.com/jwa91/n8nmermaid.git](https://github.com/jwa91/n8nmermaid.git)
    cd n8nmermaid
    ```
3.  **Install dependencies (recommended with `uv`):**
    ```bash
    uv sync
    ```
    _Alternative with pip:_ `pip install .` (optionally within a virtual environment).

## Usage (CLI)

Use `n8nmermaid` via the command-line with `uv run n8nmermaid`.

**General Syntax:**

```bash
uv run n8nmermaid [OPTIONS] COMMAND [ARGS]...
```

Get help:

```bash
uv run n8nmermaid --help
uv run n8nmermaid mermaid --help
uv run n8nmermaid report --help
```

### Commands

#### 1\. `mermaid`

Generates Mermaid flowchart syntax.

**Synopsis:** `uv run n8nmermaid mermaid [OPTIONS] <WORKFLOW_FILE_PATH>`

**Key Options:**

- `<WORKFLOW_FILE_PATH>`: (Required) Path to n8n workflow JSON.
- `-d, --direction TEXT`: Main flowchart direction (`LR`, `TD`, etc.). Default: `LR`.
- `--subgraph-direction TEXT`: Direction within subgraphs/separate clusters (`BT`, `LR`, etc.). Default: `BT`.
- `--show-creds`: Display credential names on nodes.
- `--show-params`: Display key parameters on nodes.
- `--subgraph-mode TEXT`: How to display clusters (`subgraph`, `simple_node`, `separate_clusters`). Default: `subgraph`. (See [Subgraph Display Modes](https://www.google.com/search?q=%23subgraph-display-modes) below).
- `--output-dir DIRECTORY`: Save diagrams as `.mmd` files in this directory (required for `separate_clusters`). Output does _not_ go to stdout if used.

**Output:** Mermaid string to stdout (default) or files in `--output-dir`.

#### 2\. `report`

Generates analysis reports.

**Synopsis:** `uv run n8nmermaid report [OPTIONS] <WORKFLOW_FILE_PATH>`

**Key Options:**

- `<WORKFLOW_FILE_PATH>`: (Required) Path to n8n workflow JSON.
- `-t, --type TEXT`: (Required) Report type(s) (`stats`, `credentials`, `agents`, `node_parameters`, `analysis_json`). Can be specified multiple times (except `analysis_json`).
- `-f, --format TEXT`: Output format (`text`, `markdown`, `json`). Default: `text`.

**Output:** Report string to stdout.

### Examples (CLI)

```bash
# Generate default Mermaid diagram to file
uv run n8nmermaid mermaid example/example.json > output/example_default.mmd

# Generate Top-Down diagram
uv run n8nmermaid mermaid -d TD example/example.json > output/example_td.mmd

# Generate diagram showing credentials
uv run n8nmermaid mermaid --show-creds example/example.json > output/example_creds.mmd

# Generate simplified diagram (hide cluster details)
uv run n8nmermaid mermaid --subgraph-mode simple_node ./agent_workflow.json > ./output/agent_simple.mmd

# Generate simplified main diagram AND separate files for cluster details
uv run n8nmermaid mermaid --subgraph-mode separate_clusters ./agent_workflow.json --output-dir ./output/agent_exploded/

# Generate a statistics report (text format)
uv run n8nmermaid report -t stats ./my_workflow.json

# Generate a combined statistics and agents report
uv run n8nmermaid report -t stats -t agents ./agent_workflow.json > ./output/stats_and_agents.txt

# Get the full analysis report as JSON
uv run n8nmermaid report -t analysis_json ./my_workflow.json > ./output/analysis_result.json
```

## Subgraph Display Modes (`--subgraph-mode`)

This option affects how "clusters" (e.g., AI Agent + tools) are visualized in the _main_ diagram:

- **`subgraph` (Default):** Cluster nodes are placed inside an explicit `subgraph` block in the main diagram. Internal connections are visible within the block.
- **`simple_node`:** Only the cluster's "root" node (e.g., the Agent node) is shown in the main diagram. Internal details are hidden. Connections are rerouted to the root node. Good for a high-level overview.
- **`separate_clusters`:** Same as `simple_node` in the main diagram, BUT also generates _separate_ `.mmd` files for each cluster, showing its internal details. **Requires** the `--output-dir` option.

## API Usage

`n8nmermaid` also offers a FastAPI interface. See the [API README](src/n8nmermaid/api/README.md) for details on the endpoints (`/v2/mermaid`, `/v2/report`), how to start the server (`uvicorn`), and `cURL` examples.

## Logging Configuration

Configure logging via a `.env` file in the root (see `.env.example`). Set `N8NMERMAID_LOG_LEVEL` (DEBUG, INFO, etc.) and `LOGGING_TARGET` (`FILE` or `CONSOLE`).

## Project Structure

The main directories are:

- `src/n8nmermaid/`: Contains the core logic, CLI, and API code.
  - `core/`: Analysis and generation logic (V2).
  - `cli/`: Typer CLI implementation. ([README](/cli/README.md))
  - `api/`: FastAPI implementation. ([README](/n8nmermaid/api/README.md))
- `scripts/`: Helper scripts for testing and analysis. ([README](scripts/README.md))
- `example/`: Example n8n workflow JSON files.
- `output/`: Default directory for files generated by scripts..

## Development & Testing

1.  Follow the [Installation](https://www.google.com/search?q=%23installation) steps.
2.  Install dev dependencies: `uv pip install -e .[dev]`
3.  Install pre-commit hooks (recommended): `pre-commit install`
4.  Use Ruff for linting/formatting: `ruff check .`, `ruff format .` (see `ruff.toml`).
5.  Run test scripts from the root directory (make them executable first with `chmod +x`). See the [Scripts README](scripts/README.md) for details on:
    - `./scripts/run_cli_mermaid_tests.sh`
    - `./scripts/run_cli_report_tests.sh`
    - `./scripts/run_get_analyzed_jsons.sh`
