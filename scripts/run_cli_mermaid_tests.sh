#!/bin/bash

# Exit immediately if a command exits with a non-zero status.
set -e

# --- Configuration ---
INPUT_FILE="example/example.json"
# Base output directory
OUTPUT_BASE_DIR="output"

# --- Generate Timestamp for this Test Run ---
TIMESTAMP=$(date +'%Y%m%d_%H%M%S')
# Main directory for all outputs of this specific run
MAIN_TEST_RUN_DIR="${OUTPUT_BASE_DIR}/CLI_test_${TIMESTAMP}"

# --- Ensure main output directory for this run exists ---
echo "INFO: Creating main output directory for this run: ${MAIN_TEST_RUN_DIR}"
mkdir -p "${MAIN_TEST_RUN_DIR}"
echo "--------------------"

# --- Test Case 1: Default (subgraph mode) to stdout (redirected) ---
echo "INFO: Running Test 1: Default mode to stdout..."
# Subdirectory within the timestamped run directory
TEST_DIR="${MAIN_TEST_RUN_DIR}/1_default_stdout"
mkdir -p "${TEST_DIR}"
uv run n8nmermaid mermaid "${INPUT_FILE}" > "${TEST_DIR}/main_stdout.mmd"
echo "INFO: Test 1 Done. Output in ${TEST_DIR}/"
echo "--------------------"

# --- Test Case 2: Default (subgraph mode) using --output-dir ---
echo "INFO: Running Test 2: Default mode to --output-dir..."
TEST_DIR="${MAIN_TEST_RUN_DIR}/2_default_dir"
# The tool's helper function creates the final directory
uv run n8nmermaid mermaid "${INPUT_FILE}" --output-dir "${TEST_DIR}"
echo "INFO: Test 2 Done. Output in ${TEST_DIR}/"
echo "--------------------"

# --- Test Case 3: Simple Node mode to stdout (redirected) ---
echo "INFO: Running Test 3: Simple Node mode to stdout..."
TEST_DIR="${MAIN_TEST_RUN_DIR}/3_simple_node_stdout"
mkdir -p "${TEST_DIR}"
uv run n8nmermaid mermaid --subgraph-mode simple_node "${INPUT_FILE}" > "${TEST_DIR}/main_stdout.mmd"
echo "INFO: Test 3 Done. Output in ${TEST_DIR}/"
echo "--------------------"

# --- Test Case 4: Simple Node mode using --output-dir ---
echo "INFO: Running Test 4: Simple Node mode to --output-dir..."
TEST_DIR="${MAIN_TEST_RUN_DIR}/4_simple_node_dir"
uv run n8nmermaid mermaid --subgraph-mode simple_node "${INPUT_FILE}" --output-dir "${TEST_DIR}"
echo "INFO: Test 4 Done. Output in ${TEST_DIR}/"
echo "--------------------"

# --- Test Case 5: Separate Clusters mode using --output-dir ---
echo "INFO: Running Test 5: Separate Clusters mode to --output-dir..."
TEST_DIR="${MAIN_TEST_RUN_DIR}/5_separate_clusters_dir"
uv run n8nmermaid mermaid --subgraph-mode separate_clusters "${INPUT_FILE}" --output-dir "${TEST_DIR}"
echo "INFO: Test 5 Done. Output in ${TEST_DIR}/"
echo "--------------------"

# --- Test Case 6: Separate Clusters mode with Options (TD, creds, params) ---
echo "INFO: Running Test 6: Separate Clusters mode with options..."
TEST_DIR="${MAIN_TEST_RUN_DIR}/6_separate_clusters_options_dir"
uv run n8nmermaid mermaid \
  --subgraph-mode separate_clusters \
  --direction TD \
  --show-creds \
  --show-params \
  "${INPUT_FILE}" \
  --output-dir "${TEST_DIR}"
echo "INFO: Test 6 Done. Output in ${TEST_DIR}/"
echo "--------------------"

# --- Test Case 7: Subgraph mode with Options (TD, creds, params) using --output-dir ---
echo "INFO: Running Test 7: Subgraph mode with options..."
TEST_DIR="${MAIN_TEST_RUN_DIR}/7_subgraph_options_dir"
uv run n8nmermaid mermaid \
  --subgraph-mode subgraph \
  --direction TD \
  --show-creds \
  --show-params \
  "${INPUT_FILE}" \
  --output-dir "${TEST_DIR}"
echo "INFO: Test 7 Done. Output in ${TEST_DIR}/"
echo "--------------------"

echo "INFO: All CLI mermaid test commands executed successfully."
echo "INFO: Outputs for this run are in: ${MAIN_TEST_RUN_DIR}"