# src/n8nmermaid/api/routers/report.py
"""API Router for V2 analysis report generation."""

import logging

from fastapi import APIRouter, HTTPException, status

from n8nmermaid.api.helpers import run_api_orchestration_v2
from n8nmermaid.api.schemas import (
    ApiErrorDetail,
    ApiReportRequest,
    ApiReportResponse,
)

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post(
    "/",
    response_model=ApiReportResponse,
    summary="Generate Analysis Report",
    description="""
Analyzes the provided n8n workflow JSON and generates a textual report.

- **workflow_data**: The complete JSON object of your n8n workflow.
- **params**: Parameters to control the report generation:
    - `report_types`: A list of report sections to include
      (e.g., `["stats", "credentials"]`).
      Available types: `stats`, `credentials`, `agents`, `node_parameters`,
      `analysis_json`. Note: `analysis_json` cannot be combined with other types.
    - `output_format`: Format of the report ('text', 'markdown', 'json').
      Default: 'text'. Note: Currently only 'text' is fully supported for
      combined reports, 'analysis_json' always returns JSON.

Returns the generated report content as a single string
(or JSON string if `analysis_json` is requested).
""",
    responses={
        status.HTTP_400_BAD_REQUEST: {"model": ApiErrorDetail,
                               "description": "Analysis or Orchestration Error"},
        status.HTTP_422_UNPROCESSABLE_ENTITY: {"model": ApiErrorDetail,
                                         "description": "Invalid Input Data"},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ApiErrorDetail,
                                          "description": "Internal Server Error"},
    },
)
async def generate_report_endpoint(
    request_body: ApiReportRequest
) -> ApiReportResponse:
    """
    Handles requests to generate analysis reports.

    Args:
        request_body: The request body containing workflow data and report parameters.

    Returns:
        An ApiReportResponse containing the generated report string.

    Raises:
        HTTPException: If errors occur during processing.
    """
    logger.info("Received request for /v2/report endpoint.")
    try:
        result: str | dict[str, str] = await run_api_orchestration_v2(
            request_body=request_body, command="generate_report"
        )

        if not isinstance(result, str):
            logger.error("Report generation returned unexpected type: %s",
                      type(result).__name__)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error: "
                "Report generator returned unexpected format.",
            )

        return ApiReportResponse(report=result)

    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        logger.exception("Unexpected error in /v2/report endpoint.")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An internal server error occurred: {e}",
        ) from e
