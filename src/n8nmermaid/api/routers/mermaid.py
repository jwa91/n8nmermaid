# src/n8nmermaid/api/routers/mermaid.py
"""API Router for V2 Mermaid diagram generation."""

import logging

from fastapi import APIRouter, HTTPException, status

from n8nmermaid.api.helpers import run_api_orchestration_v2
from n8nmermaid.api.schemas import (
    ApiErrorDetail,
    ApiMermaidRequest,
    ApiMermaidResponse,
)

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post(
    "/",
    response_model=ApiMermaidResponse,
    summary="Generate Mermaid Diagram(s)",
    description="""
Analyzes the provided n8n workflow JSON and generates Mermaid flowchart syntax.

- **workflow_data**: The complete JSON object of your n8n workflow.
- **params**: Optional parameters to control the diagram generation:
    - `direction`: Main layout direction (TD, LR, TB, RL, BT). Default: LR.
    - `subgraph_direction`: Layout direction inside subgraphs. Default: BT.
    - `show_credentials`: If true, display credential names on nodes. Default: false.
    - `show_key_parameters`: If true, display key parameters (like AI model) on nodes.
      Default: false.
    - `subgraph_display_mode`: How to handle clusters ('subgraph', 'simple_node',
      'separate_clusters'). Default: 'subgraph'.

Returns a dictionary where the key `main` holds the primary diagram.
If `subgraph_display_mode` is 'separate_clusters', additional keys will contain
diagrams for each cluster root.
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
async def generate_mermaid_endpoint(
    request_body: ApiMermaidRequest
) -> ApiMermaidResponse:
    """
    Handles requests to generate Mermaid diagrams.

    Args:
        request_body: The request body containing workflow data and parameters.

    Returns:
        An ApiMermaidResponse containing the generated diagram(s).

    Raises:
        HTTPException: If errors occur during processing.
    """
    logger.info("Received request for /v2/mermaid endpoint.")
    try:
        result = await run_api_orchestration_v2(
            request_body=request_body, command="generate_mermaid"
        )

        if not isinstance(result, dict):
            logger.error("Mermaid generation returned unexpected type: %s",
                      type(result).__name__)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error: Generator returned unexpected format.",
            )

        return ApiMermaidResponse(diagrams=result)

    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        logger.exception("Unexpected error in /v2/mermaid endpoint.")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An internal server error occurred: {e}",
        ) from e
