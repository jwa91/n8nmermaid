# src/n8nmermaid/api/helpers.py
"""Helper functions specifically for the FastAPI endpoints."""

import logging

from fastapi import HTTPException, status

from n8nmermaid.api.schemas import ApiMermaidRequest, ApiReportRequest
from n8nmermaid.core.orchestrator_v2 import OrchestratorErrorV2, process_v2
from n8nmermaid.models_v2.request_v2_models import (
    AnalysisRequestV2,
    MermaidGenerationParamsV2,
    ReportGenerationParamsV2,
    RequestCommand,
)

logger = logging.getLogger(__name__)


async def run_api_orchestration_v2(
    request_body: ApiMermaidRequest | ApiReportRequest,
    command: RequestCommand
) -> str | dict[str, str]:
    """
    Runs the V2 orchestration process based on API request data.

    Constructs the core AnalysisRequestV2 from the API request body,
    invokes the process_v2 function, and handles potential errors by
    raising appropriate HTTPExceptions.

    Args:
        request_body: The parsed request body (ApiMermaidRequest or ApiReportRequest).
        command: The specific command being executed.

    Returns:
        The result from the orchestrator (Mermaid dict or report string).

    Raises:
        HTTPException: If validation, orchestration, or unexpected errors occur.
    """
    logger.debug("Running API orchestration helper for command: %s", command)

    mermaid_params: MermaidGenerationParamsV2 | None = None
    report_params: ReportGenerationParamsV2 | None = None

    if isinstance(request_body, ApiMermaidRequest):
        mermaid_params = request_body.params
    elif isinstance(request_body, ApiReportRequest):
        report_params = request_body.params
    else:
        logger.error("Invalid request body type passed to API helper: %s",
                  type(request_body).__name__)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error: Invalid request data.",
        )

    try:
        analysis_request = AnalysisRequestV2(
            workflow_data=request_body.workflow_data,
            command=command,
            mermaid_params=mermaid_params if mermaid_params is not None
                       else MermaidGenerationParamsV2(),
            report_params=report_params,
        )
        logger.debug("Constructed AnalysisRequestV2, calling process_v2...")

        result = process_v2(request=analysis_request)
        logger.info("API Orchestration successful for command: %s", command)
        return result

    except OrchestratorErrorV2 as e:
        logger.error("Orchestration failed: %s", e, exc_info=False)
        logger.debug("Orchestration error details:", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=f"Analysis Error: {e}"
        ) from e
    except ValueError as e:
        logger.error("Validation error during API request processing: %s",
                  e, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Invalid input: {e}",
        ) from e
    except Exception as e:
        logger.exception("An unexpected error occurred during API orchestration.")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An internal server error occurred: {e}",
        ) from e
