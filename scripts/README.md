# Scripts

## Table of Contents

- [`analyze_n8n_workflow_examples.py`](#analyze_n8n_workflow_examplespy)
- [`run_cli_mermaid_tests.sh`](#run_cli_mermaid_testssh)
- [`run_cli_report_tests.sh`](#run_cli_report_testssh)
- [`run_get_analyzed_jsons.sh`](#run_get_analyzed_jsonssh)

---

This directory contains utility and testing scripts related to the `n8nmermaid` project.

---

## `analyze_n8n_workflow_examples.py`

**Purpose:**

This Python script analyzes all n8n workflow `.json` files found within a specified folder (e.g., the `example/` directory). It extracts and flattens all node parameters defined in those workflows and generates a markdown report (`node_parameter_analysis.md`) within that same folder. This report summarizes all unique parameter keys found across all nodes and also lists the unique keys found for each specific node type.

This script operates directly on the n8n JSON files and does **not** depend on the `n8nmermaid` tool itself. It's useful for understanding the structure and variety of parameters used in example workflows.

**Usage:**

Run the script from the **root directory** of the `n8nmermaid` project, providing the path to the folder containing the workflows to analyze.

```bash
# Analyze workflows in the 'example' directory
python scripts/analyze_n8n_workflow_examples.py example/

# Analyze workflows in a custom directory
python scripts/analyze_n8n_workflow_examples.py /path/to/your/workflows/
```

**Output:**

- Prints progress information to the console.
- Creates/overwrites a `node_parameter_analysis.md` file in the analyzed folder.

---

## `run_cli_mermaid_tests.sh`

**Purpose:**

This script executes a predefined suite of test commands for the `n8nmermaid mermaid` CLI subcommand using the V2 generation logic. It's designed to help verify core functionality and different option combinations, especially after code changes.

**Usage:**

Run the script from the **root directory** of the `n8nmermaid` project.

1.  Make the script executable (only needs to be done once):
    ```bash
    chmod +x scripts/run_cli_mermaid_tests.sh
    ```
2.  Execute the script:
    ```bash
    ./scripts/run_cli_mermaid_tests.sh
    ```

**Output:**

- Prints informational messages to the console indicating which test is running.
- Creates a unique timestamped directory for each run within the `output/` folder (e.g., `output/CLI_test_YYYYMMDD_HHMMSS/`).
- Inside this timestamped directory, it creates subdirectories for each test case (e.g., `1_default_stdout/`, `2_default_dir/`) containing the generated `.mmd` file(s) for that specific test.
- The script uses `example/example.json` as the input workflow for all tests.

Refer to the script's content to see the exact commands and options being tested. You can easily modify this script to add or change test cases.

---

## `run_cli_report_tests.sh`

**Purpose:**

This script executes a predefined suite of test commands for the `n8nmermaid report` CLI subcommand using the V2 analysis and reporting logic. It tests various report types (`stats`, `credentials`, `agents`, `node_parameters`, `analysis_json`) and combinations.

**Usage:**

Run the script from the **root directory** of the `n8nmermaid` project.

1.  Make the script executable (only needs to be done once):
    ```bash
    chmod +x scripts/run_cli_report_tests.sh
    ```
2.  Execute the script:
    ```bash
    ./scripts/run_cli_report_tests.sh
    ```

**Output:**

- Prints informational messages to the console indicating which test is running.
- Creates a unique timestamped directory for each run within the `output/` folder (e.g., `output/CLI_report_test_YYYYMMDD_HHMMSS/`).
- Inside this timestamped directory, it creates subdirectories for each test case (e.g., `1_stats_text/`, `4_analysis_json/`) containing the generated report output (`.txt` or `.json`) for that specific test.
- The script uses `example/example.json` as the input workflow for all tests.

Refer to the script's content to see the exact commands and options being tested.

---

## `run_get_analyzed_jsons.sh`

**Purpose:**

This script iterates through all `.json` files in the `example/` directory and runs the `n8nmermaid report --type analysis_json` command on each one. It saves the resulting full V2 analysis JSON output for each workflow to the `output/analyzed_json/` directory. This is useful for quickly generating the structured analysis data for all examples.

**Usage:**

Run the script from the **root directory** of the `n8nmermaid` project.

1.  Make the script executable (only needs to be done once):
    ```bash
    chmod +x scripts/run_get_analyzed_jsons.sh
    ```
2.  Execute the script:
    ```bash
    ./scripts/run_get_analyzed_jsons.sh
    ```

**Output:**

- Prints informational messages to the console indicating which file is being processed.
- Creates the `output/analyzed_json/` directory if it doesn't exist.
- Saves one `.json` file for each input workflow into `output/analyzed_json/`, named like `[original_filename]_analysis.json`.

---

For general information about installing and using the main `n8nmermaid` tool, please see the main [README.md](../README.md).
