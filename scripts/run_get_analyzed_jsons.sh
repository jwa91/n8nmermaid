#!/bin/bash

# Exit immediately if a command exits with a non-zero status.
set -e

# --- Configuration ---
# Directory containing the input n8n workflow JSON files
INPUT_DIR="example"
# Directory where the output analysis JSON files will be saved
OUTPUT_DIR="output/analyzed_json"

# --- Ensure output directory exists ---
echo "INFO: Creating output directory (if it doesn't exist): ${OUTPUT_DIR}"
mkdir -p "${OUTPUT_DIR}"
echo "--------------------"

# --- Process each example file ---
# Loop through files matching the pattern *.json in the INPUT_DIR
# Changed pattern to *.json to be more general, but you can keep example*.json if preferred
for input_file in "${INPUT_DIR}"/*.json; do
  # Check if the file exists and is a regular file
  if [ -f "$input_file" ]; then
    # Extract the base name (e.g., example.json or example1.json)
    base_name=$(basename "$input_file")
    # Extract the name without the .json extension (e.g., example or example1)
    filename_base="${base_name%.json}"

    # Construct the output filename using the new convention
    output_filename="${filename_base}_analysis.json"
    output_path="${OUTPUT_DIR}/${output_filename}"

    echo "INFO: Processing '${input_file}' -> '${output_path}'..."

    # Run the n8nmermaid command and redirect output
    # Using --format json explicitly for clarity, although it's the default for analysis_json
    uv run n8nmermaid report --type analysis_json --format json "${input_file}" > "${output_path}"

    echo "INFO: Successfully generated '${output_path}'."
    echo "--------------------"
  else
    # This handles the case where the glob doesn't match any files
    if [ "$input_file" == "${INPUT_DIR}/*.json" ]; then
        echo "WARN: No JSON files found in '${INPUT_DIR}'. Skipping."
        # Decide if you want to exit or just continue if no files are found
        # exit 1 # Uncomment to exit if no files match
    else
        # This case might occur if a non-file item matches the glob somehow (unlikely)
        echo "WARN: Skipping non-file item '${input_file}'."
    fi

  fi
done

echo "INFO: All analysis JSON generation commands executed successfully."
echo "INFO: Output files are in: ${OUTPUT_DIR}"
