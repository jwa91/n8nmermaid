# n8nmermaid API

## Overview

This directory contains the FastAPI interface for `n8nmermaid` V2, providing HTTP endpoints to generate Mermaid diagrams and analysis reports from n8n workflow JSON.

It uses the core logic from `src/n8nmermaid/core/`. For detailed analysis/generation concepts, see the [main project README.md](../../../README.md).

## Endpoints

### 1. Health Check

- **GET /**
- **Summary:** Checks if the API is running.
- **Response:** `{"message": "n8n-mermaid API V2 is running."}`

### 2. Generate Mermaid Diagram(s)

- **POST /v2/mermaid**
- **Summary:** Generates Mermaid flowchart syntax.
- **Request Body:** JSON object with `workflow_data` (required, the n8n workflow JSON) and optional `params` (object, see `MermaidGenerationParamsV2` in main README/schemas for options like `direction`, `subgraph_display_mode`).
- **Response:** JSON object `{ "diagrams": { "main": "...", ... } }` containing the generated diagram strings. Additional keys appear if `subgraph_display_mode` is `separate_clusters`.
- **Errors:** 400 (Analysis Fail), 422 (Invalid Input), 500 (Server Error).

### 3. Generate Analysis Report

- **POST /v2/report**
- **Summary:** Generates a textual analysis report.
- **Request Body:** JSON object with `workflow_data` (required) and required `params` (object, see `ReportGenerationParamsV2` in main README/schemas, must include `report_types` list like `["stats"]` or `["analysis_json"]`; optionally `output_format`).
- **Response:** JSON object `{ "report": "..." }` containing the generated report string (or JSON string for `analysis_json` type).
- **Errors:** 400 (Analysis Fail), 422 (Invalid Input), 500 (Server Error).

## Running the API

1.  **Install:** Follow the main README instructions (including `.[dev]` dependencies).
2.  **Start Server:** From the project root:
    ```bash
    uvicorn n8nmermaid.api.main:app --reload --port 8000
    ```
3.  **Access:** API at `http://localhost:8000`, interactive docs at `http://localhost:8000/docs`.

## Usage Examples (cURL)

**Generate Default Mermaid Diagram:**

```bash
curl -X POST http://localhost:8000/v2/mermaid \
-H "Content-Type: application/json" \
-d '{
  "workflow_data": { /* ... your full n8n workflow JSON ... */ }
}'
```

**Generate Statistics Report (Text):**

```bash
curl -X POST http://localhost:8000/v2/report \
-H "Content-Type: application/json" \
-d '{
  "workflow_data": { /* ... your full n8n workflow JSON ... */ },
  "params": {
    "report_types": ["stats"]
  }
}'
```

## Core Logic

The underlying analysis and generation logic resides in `src/n8nmermaid/core/`. See the [invalid URL removed] for implementation details.
