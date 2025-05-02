# src/n8nmermaid/core/generators/reports_v2/models.py
"""
Pydantic models defining the structured data for various reports (V2).

These models represent the intermediate data extracted before formatting.
"""

from typing import Any

from pydantic import BaseModel, Field


class NodeCountByType(BaseModel):
    """Represents the count of nodes for a specific type."""

    node_type: str
    count: int


class CredentialUsageInfo(BaseModel):
    """Details about a specific credential found in the workflow."""

    credential_type: str
    credential_name: str | None = None
    credential_id: str | None = None
    used_by_nodes: list[str] = Field(default_factory=list)


class ModelCredentialInfo(BaseModel):
    """Simplified credential info for the model used by an agent."""

    type: str
    name: str | None = None
    id: str | None = None


class AgentDetail(BaseModel):
    """Structured information about a single identified Agent node (V2)."""

    node_id: str
    node_name: str
    model: str | None = None
    model_credentials: list[ModelCredentialInfo] | None = None
    system_message: str | None = None
    tools_used: list[str] = Field(default_factory=list)


class StatsReportData(BaseModel):
    """Structured data for the workflow statistics report (V2)."""

    total_nodes: int
    nodes_by_type: list[NodeCountByType] = Field(default_factory=list)
    nodes_by_role: dict[str, int] = Field(default_factory=dict)
    nodes_with_credentials: int = 0
    disabled_nodes: int = 0
    cluster_roots: int = 0
    total_warnings: int = 0


class CredentialsReportData(BaseModel):
    """Structured data for the credentials usage report (V2)."""

    credentials_found: list[CredentialUsageInfo] = Field(default_factory=list)


class AgentsReportData(BaseModel):
    """Structured data for the AI Agents report (V2)."""

    agents: list[AgentDetail] = Field(default_factory=list)


class NodeParameterDetail(BaseModel):
    """Details of a specific node instance for parameter reporting (V2)."""

    node_id: str
    node_name: str
    raw_parameters: dict[str, Any] = Field(default_factory=dict)


class NodeTypeParameters(BaseModel):
    """Groups parameter details for all nodes of a specific type (V2)."""

    node_type: str
    node_details: list[NodeParameterDetail] = Field(default_factory=list)


class NodeParametersReportData(BaseModel):
    """Top-level structured data for the node parameters report (V2)."""

    node_types: list[NodeTypeParameters] = Field(default_factory=list)
