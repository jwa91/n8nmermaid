#!/bin/bash

# Exit immediately if a command exits with a non-zero status.
set -e

# --- Configuration ---
# Ensure this input file exists and is accessible from the script's execution location
INPUT_FILE="example/example.json"
# Base output directory
OUTPUT_BASE_DIR="output"

# --- Generate Timestamp for this Test Run ---
TIMESTAMP=$(date +'%Y%m%d_%H%M%S')
# Main directory for all outputs of this specific run
MAIN_TEST_RUN_DIR="${OUTPUT_BASE_DIR}/CLI_report_test_${TIMESTAMP}"

# --- Ensure main output directory for this run exists ---
echo "INFO: Creating main output directory for this run: ${MAIN_TEST_RUN_DIR}"
mkdir -p "${MAIN_TEST_RUN_DIR}"
echo "--------------------"

# --- Test Case 1: Single 'stats' report (default format: text) ---
echo "INFO: Running Test 1: Single 'stats' report..."
TEST_DIR="${MAIN_TEST_RUN_DIR}/1_stats_text"
mkdir -p "${TEST_DIR}"
uv run n8nmermaid report --type stats "${INPUT_FILE}" > "${TEST_DIR}/stats_report.txt"
echo "INFO: Test 1 Done. Output in ${TEST_DIR}/"
echo "--------------------"

# --- Test Case 2: Single 'credentials' report (default format: text) ---
echo "INFO: Running Test 2: Single 'credentials' report..."
TEST_DIR="${MAIN_TEST_RUN_DIR}/2_credentials_text"
mkdir -p "${TEST_DIR}"
uv run n8nmermaid report --type credentials "${INPUT_FILE}" > "${TEST_DIR}/credentials_report.txt"
echo "INFO: Test 2 Done. Output in ${TEST_DIR}/"
echo "--------------------"

# --- Test Case 3: Single 'agents' report (default format: text) ---
echo "INFO: Running Test 3: Single 'agents' report..."
TEST_DIR="${MAIN_TEST_RUN_DIR}/3_agents_text"
mkdir -p "${TEST_DIR}"
uv run n8nmermaid report --type agents "${INPUT_FILE}" > "${TEST_DIR}/agents_report.txt"
echo "INFO: Test 3 Done. Output in ${TEST_DIR}/"
echo "--------------------"

# --- Test Case 4: Single 'analysis_json' report ---
echo "INFO: Running Test 4: Single 'analysis_json' report..."
TEST_DIR="${MAIN_TEST_RUN_DIR}/4_analysis_json"
mkdir -p "${TEST_DIR}"
uv run n8nmermaid report --type analysis_json "${INPUT_FILE}" > "${TEST_DIR}/analysis.json"
echo "INFO: Test 4 Done. Output in ${TEST_DIR}/"
echo "--------------------"

# --- Test Case 5: Combined 'stats' + 'credentials' report (text) ---
echo "INFO: Running Test 5: Combined 'stats' + 'credentials' report..."
TEST_DIR="${MAIN_TEST_RUN_DIR}/5_stats_creds_text"
mkdir -p "${TEST_DIR}"
uv run n8nmermaid report --type stats --type credentials "${INPUT_FILE}" > "${TEST_DIR}/combined_report.txt"
echo "INFO: Test 5 Done. Output in ${TEST_DIR}/"
echo "--------------------"

# --- Test Case 6: Combined 'stats' + 'agents' report (text) ---
echo "INFO: Running Test 6: Combined 'stats' + 'agents' report..."
TEST_DIR="${MAIN_TEST_RUN_DIR}/6_stats_agents_text"
mkdir -p "${TEST_DIR}"
uv run n8nmermaid report --type stats --type agents "${INPUT_FILE}" > "${TEST_DIR}/combined_report.txt"
echo "INFO: Test 6 Done. Output in ${TEST_DIR}/"
echo "--------------------"

# --- Test Case 7: Combined 'credentials' + 'agents' report (text) ---
echo "INFO: Running Test 7: Combined 'credentials' + 'agents' report..."
TEST_DIR="${MAIN_TEST_RUN_DIR}/7_creds_agents_text"
mkdir -p "${TEST_DIR}"
uv run n8nmermaid report --type credentials --type agents "${INPUT_FILE}" > "${TEST_DIR}/combined_report.txt"
echo "INFO: Test 7 Done. Output in ${TEST_DIR}/"
echo "--------------------"

# --- Test Case 8: Combined 'stats' + 'credentials' + 'agents' report (text) ---
echo "INFO: Running Test 8: Combined 'stats' + 'credentials' + 'agents' report..."
TEST_DIR="${MAIN_TEST_RUN_DIR}/8_stats_creds_agents_text"
mkdir -p "${TEST_DIR}"
uv run n8nmermaid report --type stats --type credentials --type agents "${INPUT_FILE}" > "${TEST_DIR}/combined_report.txt"
echo "INFO: Test 8 Done. Output in ${TEST_DIR}/"
echo "--------------------"

# --- Test Case 9: Explicit format (text) - Should be same as default ---
# This also tests if passing --format works correctly
echo "INFO: Running Test 9: Explicit format 'text'..."
TEST_DIR="${MAIN_TEST_RUN_DIR}/9_stats_explicit_text"
mkdir -p "${TEST_DIR}"
uv run n8nmermaid report --type stats --format text "${INPUT_FILE}" > "${TEST_DIR}/stats_report.txt"
echo "INFO: Test 9 Done. Output in ${TEST_DIR}/"
echo "--------------------"

# --- Test Case 10 (Optional): Single 'node_parameters' report ---
echo "INFO: Running Test 10: Single 'node_parameters' report..."
TEST_DIR="${MAIN_TEST_RUN_DIR}/10_node_params_text"
mkdir -p "${TEST_DIR}"
uv run n8nmermaid report --type node_parameters "${INPUT_FILE}" > "${TEST_DIR}/node_params_report.txt"
echo "INFO: Test 10 Done. Output in ${TEST_DIR}/"
echo "--------------------"

# --- Note on Failure Tests ---
# The CLI commands for invalid combinations (like --type analysis_json --type stats)
# or missing types should now fail due to the validation added.
# Because 'set -e' is active, running those commands here would stop the script.
# If you want to explicitly test *that they fail*, you would need to temporarily
# disable 'set -e' or run the command in a subshell and check the exit code, e.g.:
# (uv run n8nmermaid report --type analysis_json --type stats "${INPUT_FILE}" > /dev/null 2>&1) && exit 1 || echo "INFO: Test failed as expected."

echo "INFO: All CLI report test commands executed successfully."
echo "INFO: Outputs for this run are in: ${MAIN_TEST_RUN_DIR}"