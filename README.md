# n8nmermaid

[![Python Version](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
Converts n8n workflow JSON files into Mermaid flowchart syntax (V2) or generates detailed analysis reports (V2).

## Overview

`n8nmermaid` is a Python tool designed to help understand and visualize n8n workflows. It takes an n8n workflow exported as a JSON file and can perform two main actions using its V2 processing engine:

1.  **Generate Mermaid Diagrams:** Creates Mermaid flowchart syntax representing the workflow structure. This output can be used with tools that render Mermaid (like GitLab, GitHub, Obsidian, online editors) to create visual diagrams. It offers different modes for displaying complex structures like AI Agents and their associated tools (as "clusters").
2.  **Generate Analysis Reports:** Produces structured reports summarizing various aspects of the workflow, such as node statistics, credential usage, AI Agent configurations, node parameters, or the complete raw analysis data in JSON format.

The tool provides a Command Line Interface (CLI) for easy use.

## Key Features

- **n8n Workflow Analysis (V2):** Parses n8n JSON, analyzes node connections (including different types like `main`, `ai_tool`, etc.), identifies node roles (Trigger, Action, Router, Sticky Note), and detects clustered node structures (e.g., Agent setups).
- **Mermaid Diagram Generation (V2):**
  - Generates Mermaid `flowchart` syntax.
  - Supports different layout directions (`LR`, `TD`, `BT`, etc.).
  - Customizable node labels (optionally showing credentials or key parameters).
  - Multiple **Subgraph Display Modes** for handling clustered nodes:
    - `subgraph`: Shows clusters within explicit subgraph boxes in the main diagram.
    - `simple_node`: Represents clusters only by their root node (e.g., the Agent node) in the main diagram, hiding internal details.
    - `separate_clusters`: Represents clusters by their root node in the main diagram _and_ generates separate `.mmd` diagram files detailing the internal structure of each cluster (requires `--output-dir`).
- **Analysis Report Generation (V2):**
  - Generates various report types:
    - `stats`: General workflow statistics (node counts by type/group, credentials, warnings, etc.).
    - `credentials`: Lists all credentials used and the nodes using them.
    - `agents`: Details identified AI Agents (cluster roots), their models, credentials, system messages, and connected tools.
    - `node_parameters`: Lists the raw parameters for every node, grouped by node type.
    - `analysis_json`: Outputs the complete, structured analysis result (from `WorkflowAnalysisV2`) as JSON.
  - Supports different output formats (currently `text`, `markdown`, `json`).
- **Command Line Interface:** Easy-to-use CLI built with Typer.
- **Configurable Logging:** Control log level and output target (file/console) via `.env` file.

## Installation

1.  **Prerequisites:**

    - Python >= 3.11
    - `uv` (recommended for environment management and running commands) or `pip`. Install `uv` from [here](https://github.com/astral-sh/uv).

2.  **Clone the repository:**

    ```bash
    git clone [https://github.com/jwa91/n8nmermaid.git](https://github.com/jwa91/n8nmermaid.git)
    cd n8nmermaid
    ```

3.  **Install dependencies using `uv` (recommended):**

    ```bash
    # Installs dependencies listed in pyproject.toml into a virtual environment
    uv sync
    ```

    _Alternatively, using pip:_

    ```bash
    # Create and activate a virtual environment (optional but recommended)
    # python -m venv .venv
    # source .venv/bin/activate # On Windows use `.venv\Scripts\activate`

    # Install the package
    pip install .
    ```

## Usage (CLI)

The primary way to use `n8nmermaid` is via its command-line interface, invoked using `uv run n8nmermaid`.

**General Syntax:**

```bash
uv run n8nmermaid [OPTIONS] COMMAND [ARGS]...
```

You can get help for the main tool and specific commands:

```bash
uv run n8nmermaid --help
uv run n8nmermaid mermaid --help
uv run n8nmermaid report --help
```

### Commands

#### 1\. `mermaid`

Generates Mermaid flowchart syntax (V2) from an n8n workflow file.

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
- `--subgraph-direction TEXT`: Sets the direction _within_ generated subgraphs (for `subgraph` mode) or for _separate_ cluster diagrams (for `separate_clusters` mode).
  - Choices: `TD`, `LR`, `TB`, `RL`, `BT`
  - Default: `BT`
- `--show-creds`: Display used credential names on node labels.
  - Default: `False`
- `--show-params`: Display key parameters (e.g., AI model names) on node labels.
  - Default: `False`
- `--subgraph-mode TEXT`: Controls how clustered nodes (e.g., Agents + tools) are displayed.
  - Choices:
    - `subgraph`: (Default) Show clusters within explicit subgraph boxes in the main diagram.
    - `simple_node`: Represent clusters only by their root node in the main diagram, hiding internal details.
    - `separate_clusters`: Represent clusters by their root node in the main diagram _and_ generate separate diagrams detailing the internal structure of each cluster (requires `--output-dir`).
  - Default: `subgraph`
- `--output-dir DIRECTORY`: If specified, saves all generated diagrams (main + separate clusters if applicable) as individual `.mmd` files in this directory (e.g., `main.mmd`, `My_Agent_Name.mmd`). If this is used, output is _not_ printed to stdout. File names for clusters are derived from the sanitized agent root node name.
- `--help`: Show command-specific help.

**Output:**

- By default (without `--output-dir`), prints the **main** generated Mermaid diagram string to standard output (stdout).
- If `--output-dir` is used, saves files to the specified directory and prints status messages to stderr.

#### 2\. `report`

Generates various analysis reports (V2) from an n8n workflow file.

**Synopsis:**

```bash
uv run n8nmermaid report [OPTIONS] <WORKFLOW_FILE_PATH>
```

**Arguments:**

- `<WORKFLOW_FILE_PATH>`: (Required) Path to the input n8n workflow JSON file.

**Options:**

- `-t, --type TEXT`: (Required) The type(s) of report to generate. Can be specified multiple times to combine reports (e.g., `-t stats -t agents`), _except_ `analysis_json` which must be used alone.
  - Choices:
    - `stats`: Workflow statistics (node counts, creds, warnings, etc.).
    - `credentials`: Detailed report on credential usage.
    - `agents`: Detailed report on identified AI Agents (cluster roots).
    - `node_parameters`: Raw parameters for every node, grouped by type.
    - `analysis_json`: Outputs the full, structured V2 analysis result as JSON.
- `-f, --format TEXT`: Output format for the report(s).
  - Choices: `text`, `markdown`, `json`
  - Default: `text`
- `--help`: Show command-specific help.

**Output:**

- Prints the generated report content (potentially combined) to standard output (stdout).

### Examples

**1. Generate default Mermaid diagram (subgraph mode) and save to file:**

```bash
uv run n8nmermaid mermaid example/example.json > output/example_default.mmd
```

**2. Generate Mermaid with Top-Down layout and save:**

```bash
uv run n8nmermaid mermaid -d TD example/example.json > output/example_td.mmd
```

**3. Generate Mermaid showing credentials:**

```bash
uv run n8nmermaid mermaid --show-creds example/example.json > output/example_creds.mmd
```

**4. Generate a simplified Mermaid view (hiding cluster details):**

```bash
uv run n8nmermaid mermaid --subgraph-mode simple_node ./agent_workflow.json > ./output/agent_simple.mmd
```

**5. Generate a simplified main view AND separate files for cluster details:**

```bash
# Requires --output-dir
uv run n8nmermaid mermaid --subgraph-mode separate_clusters ./agent_workflow.json --output-dir ./output/agent_exploded/
# Creates files like:
# ./output/agent_exploded/main.mmd
# ./output/agent_exploded/My_First_Agent.mmd
# ./output/agent_exploded/Another_Agent.mmd
```

**6. Generate a statistics report (text format):**

```bash
uv run n8nmermaid report -t stats ./my_workflow.json
```

**7. Generate a combined statistics and agents report:**

```bash
uv run n8nmermaid report -t stats -t agents ./agent_workflow.json > ./output/stats_and_agents.txt
```

**8. Get the full analysis result as JSON:**

```bash
uv run n8nmermaid report -t analysis_json ./my_workflow.json > ./output/analysis_result.json
```

**9. Get the node parameters report:**

```bash
uv run n8nmermaid report -t node_parameters ./my_workflow.json > ./output/node_params.txt
```

## Project Structure

```
.
├── .env.example             # Example environment variables for logging
├── .gitignore
├── .pre-commit-config.yml   # Pre-commit hook configuration
├── pyproject.toml           # Project metadata and dependencies (Hatch)
├── README.md                # This file
├── ruff.toml                # Ruff linter/formatter configuration
├── scripts/                 # Utility and test execution scripts
│   ├── README.md            # Describes the scripts
│   ├── analyze_n8n_workflow_examples.py # Standalone script for param analysis
│   ├── run_cli_mermaid_tests.sh # Runs mermaid CLI tests
│   └── run_cli_report_tests.sh  # Runs report CLI tests
│   └── run_get_analyzed_jsons.sh # Generates analysis JSON for all examples
└── src/
    └── n8nmermaid/
        ├── __init__.py
        ├── api/               # (Placeholder/Empty) Potentially for a future API
        │   └── __init__.py
        ├── cli/               # Command Line Interface logic (Typer)
        │   ├── __init__.py
        │   ├── commands.py    # Defines CLI commands (mermaid, report)
        │   ├── enums.py       # Enums for CLI option choices
        │   ├── helpers.py     # Helper functions for CLI commands (orchestration, output)
        │   ├── main.py        # Main Typer application setup
        │   └── README.md      # CLI-specific documentation
        ├── core/              # Core analysis and generation logic
        │   ├── __init__.py
        │   ├── analyzer_v2/   # V2 Workflow analysis engine
        │   │   ├── __init__.py # Main V2 Analyzer class
        │   │   ├── constants.py # V2 Analyzer constants
        │   │   ├── models.py    # Pydantic models for V2 analysis results
        │   │   ├── phase_1_initial_parse.py
        │   │   ├── phase_2_connection_mapping.py
        │   │   ├── phase_3_cluster_analysis.py
        │   │   ├── phase_4_node_classification.py
        │   │   ├── phase_5_parameter_extraction.py
        │   │   └── phase_6_parameter_categorization.py
        │   ├── generators/    # Output generation modules
        │   │   ├── __init__.py
        │   │   ├── mermaid_v2/  # V2 Mermaid diagram generator
        │   │   │   ├── __init__.py
        │   │   │   ├── constants.py
        │   │   │   ├── connection_definitions.py
        │   │   │   ├── generator.py # Main V2 Mermaid Generator class
        │   │   │   ├── helpers.py
        │   │   │   └── node_definitions.py
        │   │   └── reports_v2/  # V2 Report generator
        │   │       ├── __init__.py
        │   │       ├── formatters.py # Functions to format report data
        │   │       ├── generator.py # Main V2 Report Generator class
        │   │       ├── models.py    # Pydantic models for structured report data
        │   │       ├── report_agents.py
        │   │       ├── report_credentials.py
        │   │       ├── report_node_parameters.py
        │   │       └── report_stats.py
        │   └── orchestrator_v2.py # V2 Orchestrator connecting analysis and generation
        ├── models_v2/         # Pydantic models for V2 interface and results
        │   ├── __init__.py    # Exports key V2 models
        │   └── request_v2_models.py # V2 Analysis request structure
        └── utils/             # Utility functions
            ├── __init__.py
            ├── loaders.py     # Workflow file loading
            └── logging.py     # Logging setup
```

## Core Concepts (V2)

### Analysis & Generation Flow

The core logic (V2) follows these steps when invoked by the CLI:

1.  **Load Workflow:** The input JSON file is loaded (`utils.loaders`).
2.  **Build Request:** CLI arguments are parsed and packaged into an `AnalysisRequestV2` object (`models_v2.request_v2_models`). This specifies the workflow data, the command (`generate_mermaid` or `generate_report`), and any relevant parameters (`MermaidGenerationParamsV2` or `ReportGenerationParamsV2`).
3.  **Orchestration:** The `OrchestratorV2` (`core.orchestrator_v2`) receives the `AnalysisRequestV2`.
4.  **Analysis:** The `OrchestratorV2` invokes the `WorkflowAnalyzerV2` (`core.analyzer_v2`).
    - The analyzer runs through multiple phases (parsing, connection mapping, cluster analysis, classification, parameter extraction, categorization) to process the raw workflow data.
    - The result is a structured `WorkflowAnalysisV2` object (`core.analyzer_v2.models`).
5.  **Generation:** Based on the `command` in the request, the `OrchestratorV2` selects the appropriate V2 generator:
    - `generate_mermaid`: Instantiates `MermaidGeneratorV2` (`core.generators.mermaid_v2`) with the analysis results and mermaid parameters. The generator creates the Mermaid string(s).
    - `generate_report`: Instantiates `ReportGeneratorV2` (`core.generators.reports_v2`) with the analysis results and report parameters. The generator produces structured data for the requested report types and then formats them into a single string. (Note: `analysis_json` type bypasses the report generator and directly serializes the `WorkflowAnalysisV2` result in the orchestrator).
6.  **Return Output:** The orchestrator returns the generated Mermaid diagram(s) (as a dictionary) or the formatted report string.
7.  **CLI Output:** The CLI helper functions (`cli.helpers`) handle printing the result to stdout or saving Mermaid diagrams to files.

### Subgraph Display Modes (`--subgraph-mode`)

This option significantly affects how nodes identified as belonging to a "cluster" (typically an AI Agent setup detected via non-`main` connections like `ai_tool`, `ai_languageModel`) are visualized in the _main_ Mermaid diagram:

- **`subgraph` (Default):**
  - The cluster's "root" node (usually the Agent node) and all its connected sub-nodes (tools, LLMs, etc.) are placed inside an explicit Mermaid `subgraph` block.
  - Links entering or leaving the cluster point to/from the subgraph block itself.
  - Internal connections _within_ the cluster are drawn inside the subgraph block.
- **`simple_node`:**
  - Only the cluster's root node is shown in the main diagram.
  - All sub-nodes are hidden in the main diagram.
  - Any connections to/from hidden sub-nodes are visually rerouted to connect directly to the visible root node.
  - This provides a high-level overview, collapsing complex agent structures.
- **`separate_clusters`:**
  - Similar to `simple_node` in the _main_ diagram (only the root node is shown).
  - **Additionally:** For each cluster identified, a _separate_ Mermaid `.mmd` file is generated containing only the nodes and internal connections of that specific cluster.
  - This mode **requires** the `--output-dir` option to be specified.

## Logging Configuration

Logging behavior can be configured using a `.env` file in the project root directory. See `.env.example` for details.

- `N8NMERMAID_LOG_LEVEL`: Sets the minimum level for messages written to the log file (`conversion.log`). Options: `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`. Default: `INFO`.
- `LOGGING_TARGET`: Determines where logs go.
  - `FILE` (Default): Logs `N8NMERMAID_LOG_LEVEL` and above to `conversion.log`, and `WARNING` and above to the console (stderr).
  - `CONSOLE`: Logs `N8NMERMAID_LOG_LEVEL` and above _only_ to the console (stderr). No log file is created.

The log file (`conversion.log`) is overwritten on each run when `LOGGING_TARGET=FILE`.

## Development

### Setup

1.  Follow the [Installation](https://www.google.com/search?q=%23installation) steps.
2.  Install development dependencies:
    ```bash
    uv pip install -e .[dev]
    # or pip install -e .[dev]
    ```
3.  Install pre-commit hooks (optional but recommended):
    ```bash
    pre-commit install
    ```

### Linting & Formatting

This project uses Ruff for linting and formatting. Configuration is in `ruff.toml`.

- **Check formatting and linting:**
  ```bash
  ruff check .
  ruff format . --check
  ```
- **Apply fixes:**
  ```bash
  ruff check . --fix
  ruff format .
  ```
  Pre-commit hooks will automatically run these checks/fixes on staged files if installed.

## Running Tests & Scripts

The `scripts/` directory contains bash scripts to automate testing of the CLI commands and generate analysis output for examples.

- `./scripts/run_cli_mermaid_tests.sh`: Executes various `n8nmermaid mermaid` commands with different options and saves output to `output/CLI_test_<TIMESTAMP>/`.
- `./scripts/run_cli_report_tests.sh`: Executes various `n8nmermaid report` commands and saves output to `output/CLI_report_test_<TIMESTAMP>/`.
- `./scripts/run_get_analyzed_jsons.sh`: Runs `report --type analysis_json` for all workflows in `example/` and saves results to `output/analyzed_json/`.

Make sure the scripts are executable (`chmod +x scripts/*.sh`) before running them from the project root.

See `scripts/README.md` for more details on each script.
