# src/n8nmermaid/api/schemas.py
"""Pydantic schemas for API request and response models."""

from typing import Any

from pydantic import BaseModel, Field

from n8nmermaid.models_v2 import MermaidGenerationParamsV2, ReportGenerationParamsV2


class ApiMermaidRequest(BaseModel):
    """Request body schema for the /mermaid endpoint."""
    workflow_data: dict[str, Any] = Field(
        ..., description="The raw n8n workflow JSON object.")
    params: MermaidGenerationParamsV2 = Field(
        default_factory=MermaidGenerationParamsV2,
        description="Mermaid generation parameters.")

class ApiReportRequest(BaseModel):
    """Request body schema for the /report endpoint."""
    workflow_data: dict[str, Any] = Field(
        ..., description="The raw n8n workflow JSON object.")
    params: ReportGenerationParamsV2 = Field(
        ..., description="Report generation parameters.")

class ApiMermaidResponse(BaseModel):
    """Response schema for the /mermaid endpoint."""
    diagrams: dict[str, str] = Field(
        description="Dictionary of generated Mermaid diagrams. "
        "Key 'main' holds the primary diagram.")

class ApiReportResponse(BaseModel):
    """Response schema for the /report endpoint."""
    report: str = Field(description="The generated report content as a string.")

class ApiErrorDetail(BaseModel):
    """Schema for error responses."""
    detail: str
