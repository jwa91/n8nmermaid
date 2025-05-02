# n8nmermaid CLI - Usage Guide (V2)

## Table of Contents

- [Overview](#overview)
- [Code Structure](#code-structure)
- [Design & Conventions](#design--conventions)
- [Key Dependencies & Interactions](#key-dependencies--interactions)
- [Usage](#usage)
- [Commands](#commands)
  - [1. `mermaid`](#1-mermaid)
  - [2. `report`](#2-report)
- [Examples](#examples)
- [Running Test Commands](#running-test-commands)

## Overview

`n8nmermaid` is a command-line tool designed to analyze n8n workflow JSON files. It can generate Mermaid flowchart syntax (using V2 logic) for visualizing workflows or produce various analysis reports (using V2 logic).

This guide focuses specifically on the CLI usage, assuming execution via `uv run`.

The CLI application code resides within the `src/n8nmermaid/cli/` directory and is structured into multiple files (`main.py`, `commands.py`, `helpers.py`, `enums.py`) for better organization. Usage remains unified through the main `n8nmermaid` entry point defined by the `pyproject.toml` and executed via `uv run`.

## Code Structure

The CLI code is organized as follows:

- `main.py`: Defines the main `typer.Typer` application object (`app`), sets up the main callback (e.g., for logging), and imports the command modules to register them.
- `commands.py`: Contains the functions decorated with `@app.command()` that define the actual CLI commands (`mermaid`, `report`) and their parameters using `typer.Option` and `typer.Argument`. These functions parse arguments and delegate processing to helper functions.
- `helpers.py`: Includes helper functions (`run_orchestration_v2`, `save_diagrams_to_dir`) that handle common tasks like loading input files, constructing V2 request objects, invoking the V2 orchestrator, and managing output (stdout vs. file saving).
- `enums.py`: Defines Python `Enum` classes specifically for validating choices in Typer options (e.g., directions, display modes).

## Design & Conventions

- **Typer Framework:** The CLI is built using the [Typer](https://typer.tiangolo.com/) library for robust argument parsing, type hinting, and command definition.
- **CLI Enums vs. Core Literals:** You'll notice Enums defined in `cli/enums.py` (e.g., `CliSubgraphDisplayMode`) that mirror `Literal` types in `models_v2/request_v2_models.py` (e.g., `SubgraphDisplayMode`). This separation allows Typer to leverage Enums for clear, validated `--option` choices while the core logic uses the more flexible `Literal` types internally. Command functions map the CLI Enum values to the corresponding Literal strings before passing them to the core logic via Pydantic V2 models.
- **Type Hinting & `Annotated`:** We use Python's type hints extensively. `typing.Annotated` is used with Typer options/arguments to provide both the type and metadata (like help text, validation settings) in a clean way.
- **Delegation:** Command functions in `commands.py` primarily handle argument parsing and validation. The actual work of loading files, calling the core V2 `OrchestratorV2` (via `process_v2`), and handling output is delegated to functions in `helpers.py` to keep the command definitions concise.
- **Path Handling:** File and directory paths are handled using `pathlib.Path`. Typer provides built-in validation (`exists=True`, `file_okay=True`, etc.) for path arguments/options.
- **Error Handling:** Core logic errors (`OrchestratorErrorV2`) and unexpected exceptions are caught in `helpers.py`, logged, and reported to the user via `typer.echo(..., err=True)` before exiting with a non-zero status code (`raise typer.Exit(code=1)`).

## Key Dependencies & Interactions

While this README focuses on the CLI, understanding its interaction with other parts of the project is helpful:

- **Core Logic V2:** The CLI acts as a front-end to the V2 analysis (`analyzer_v2`) and generation (`generators/mermaid_v2`, `generators/reports_v2`) logic. It uses the `process_v2` function (`core/orchestrator_v2.py`) as the primary interface to the core functionality. See the main project [README.md](../../README.md) for details on the core components.
- **Request Models V2 (`src/n8nmermaid/models_v2/request_v2_models.py`):** CLI arguments are collected and packaged into Pydantic models like `AnalysisRequestV2`, `MermaidGenerationParamsV2`, and `ReportGenerationParamsV2`. These models serve as the data contract between the CLI and the V2 orchestrator.
- **Loaders (`src/n8nmermaid/utils/loaders.py`):** Helper functions rely on utility functions to load the workflow JSON file.
- **Logging (`src/n8nmermaid/utils/logging.py`):** Logging behavior (level, target) is configured centrally and initialized in the `main.py` callback.

## Usage

The tool is typically run using `uv run` followed by the `n8nmermaid` command and its subcommands/options. The main commands are `mermaid` and `report`.

```bash
uv run n8nmermaid [OPTIONS] COMMAND [ARGS]...
```

You can get help for the main tool and specific commands:

```bash
uv run n8nmermaid --help
uv run n8nmermaid mermaid --help
uv run n8nmermaid report --help
```

## Commands

### 1. `mermaid`

Generates Mermaid flowchart syntax from an n8n workflow file.

**Synopsis:**

```bash
uv run n8nmermaid mermaid [OPTIONS] <WORKFLOW_FILE_PATH>
```

**Arguments:**

- `<WORKFLOW_FILE_PATH>`: (Required) Path to the input n8n workflow JSON file.

**Options:**

- `-d, --direction TEXT`: Sets the main flowchart direction.
  - Choices: `TD`, `LR`, `TB`, `RL`, `BT`
  - Default: `LR`
- `--subgraph-direction TEXT`: Sets the direction within generated subgraphs (both inline for `subgraph` mode and for separate cluster files in `separate_clusters` mode).
  - Choices: `TD`, `LR`, `TB`, `RL`, `BT`
  - Default: `BT`
- `--show-creds`: Display used credential names on node labels.
  - Default: `False`
- `--show-params`: Display key parameters (e.g., AI model names) on node labels. (Note: Current implementation is basic).
  - Default: `False`
- `--subgraph-mode TEXT`: Controls how clustered nodes (e.g., Agents and their tools) are displayed.
  - Choices:
    - `subgraph`: (Default) Show clusters within explicit subgraph boxes in the main diagram.
    - `simple_node`: Represent clusters only by their root node in the main diagram, hiding internal details.
    - `separate_clusters`: Represent clusters by their root node in the main diagram _and_ generate separate diagrams detailing the internal structure of each cluster (requires `--output-dir`).
  - Default: `subgraph`
- `--node-map FILE`: Path to a JSON file to override the default node information map used for classification.
- `--output-dir DIRECTORY`: If specified, saves all generated diagrams (main + separate clusters if applicable) as individual `.mmd` files in this directory (e.g., `main.mmd`, `My_Agent_Name.mmd`). If this is used, output is _not_ printed to stdout. File names for clusters are derived from the sanitized agent root node name.
- `--help`: Show command-specific help.

**Output:**

- By default (without `--output-dir`), prints the **main** generated Mermaid diagram string to standard output (stdout).
- If `--output-dir` is used, saves files to the specified directory and prints status messages to stderr.

### 2. `report`

Generates various analysis reports from an n8n workflow file.

**Synopsis:**

```bash
uv run n8nmermaid report [OPTIONS] <WORKFLOW_FILE_PATH>
```

**Arguments:**

- `<WORKFLOW_FILE_PATH>`: (Required) Path to the input n8n workflow JSON file.

**Options:**

- `-t, --type TEXT`: (Required) The type of report to generate.
  - Choices:
    - `analysis_json`: Outputs the full, structured analysis result as JSON. (**Implemented**)
    - `stats`: (Not yet implemented) Workflow statistics.
    - `credentials`: (Not yet implemented) Report on credential usage.
    - `agents`: (Not yet implemented) Report on AI Agent configurations.
  - _Must specify one._
- `--node-map FILE`: Path to a JSON file to override the default node information map used for classification.
- `--help`: Show command-specific help.

**Output:**

- Prints the generated report content to standard output (stdout).

## Examples

**1. Generate a default Mermaid diagram and save to file:**

```bash
# Saves the 'main' diagram (subgraph mode by default) to the specified file
uv run n8nmermaid mermaid example/example.json > output/example.mmd
```

**2. Generate a diagram with Top-Down layout and save:**

```bash
uv run n8nmermaid mermaid example/example.json --direction TD > output/example_td.mmd
```

**3. Generate a diagram showing credentials and save:**

```bash
uv run n8nmermaid mermaid example/example.json --show-creds > output/example_creds.mmd
```

**4. Generate a diagram showing key parameters and save:**

```bash
uv run n8nmermaid mermaid example/example.json --show-params > output/example_params.mmd
```

**5. Generate a simplified view, hiding cluster details, and save:**

```bash
# Saves the simplified 'main' diagram to the specified file
uv run n8nmermaid mermaid --subgraph-mode simple_node ./agent_workflow.json > ./output/agent_simple.mmd
```

**6. Generate a simplified main view AND separate files for each cluster's details:**

```bash
# Requires --output-dir
uv run n8nmermaid mermaid --subgraph-mode separate_clusters ./agent_workflow.json --output-dir ./output/agent_exploded/
```

_(This will create files like `./output/agent_exploded/main.mmd`, `./output/agent_exploded/My_First_Agent.mmd`, `./output/agent_exploded/Another_Agent.mmd`, etc., based on the names of the agent root nodes in the workflow)_

**7. Get the full analysis result as JSON:**

```bash
uv run n8nmermaid report --type analysis_json ./my_workflow.json > ./output/analysis_report.json
```

## Running Test Commands

A helper script is provided to run a series of test cases for the `mermaid` command, exercising various options and output modes. This is useful for verifying functionality after making changes or testing different scenarios.

**Location:** `scripts/run_cli_mermaid_tests.sh`

**Usage:**

1.  Make the script executable (if you haven't already):
    ```bash
    chmod +x scripts/run_cli_mermaid_tests.sh
    ```
2.  Run the script from the project root directory:
    ```bash
    ./scripts/run_cli_mermaid_tests.sh
    ```

The script will create a timestamped directory under `output/` (e.g., `output/CLI_test_YYYYMMDD_HHMMSS/`) and place the results of each test case in subdirectories within that run folder. It uses the `example/example.json` file as input. Refer to the script content for the specific test cases being run.
