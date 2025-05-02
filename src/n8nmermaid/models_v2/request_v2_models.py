# src/n8nmermaid/models_v2/request_v2_models.py
"""Pydantic models defining the V2 structure of analysis requests."""

from typing import Any, Literal

from pydantic import BaseModel, Field, field_validator

MermaidDirection = Literal["TD", "LR", "TB", "RL", "BT"]
RequestCommand = Literal["generate_mermaid", "generate_report"]
ReportType = Literal[
    "stats",
    "credentials",
    "agents",
    "analysis_json",
    "node_parameters",
]
ReportFormat = Literal["text", "markdown", "json"]
SubgraphDisplayMode = Literal["subgraph", "simple_node", "separate_clusters"]

DEFAULT_DIRECTION_V2: MermaidDirection = "LR"
DEFAULT_SUBGRAPH_DIRECTION_V2: MermaidDirection = "BT"


class MermaidGenerationParamsV2(BaseModel):
    """Parameters specific to generating V2 Mermaid diagrams."""

    direction: MermaidDirection = DEFAULT_DIRECTION_V2
    subgraph_direction: MermaidDirection = DEFAULT_SUBGRAPH_DIRECTION_V2
    show_credentials: bool = False
    show_key_parameters: bool = False
    subgraph_display_mode: SubgraphDisplayMode = "subgraph"

    class Config:
        """Pydantic configuration"""
        extra = "forbid"


class ReportGenerationParamsV2(BaseModel):
    """Parameters specific to generating V2 textual reports."""

    report_types: list[ReportType]
    output_format: ReportFormat = "text"

    @field_validator("report_types")
    @classmethod
    def check_report_types_not_empty(cls, v: list[ReportType]) -> list[ReportType]:
        """Ensure at least one report type is provided."""
        if not v:
            raise ValueError("At least one report type must be specified.")
        if "analysis_json" in v and len(v) > 1:
            raise ValueError(
                "Report type 'analysis_json' cannot be combined with other types."
            )
        return v

    class Config:
        """Pydantic configuration"""
        extra = "forbid"


class AnalysisRequestV2(BaseModel):
    """
    Represents a V2 request to analyze and process an n8n workflow.
    """

    workflow_data: dict[str, Any]
    command: RequestCommand = "generate_mermaid"
    mermaid_params: MermaidGenerationParamsV2 = Field(
        default_factory=MermaidGenerationParamsV2
    )
    report_params: ReportGenerationParamsV2 | None = None

    class Config:
        """Pydantic configuration"""
        arbitrary_types_allowed = True
        validate_assignment = True
        extra = "ignore"
