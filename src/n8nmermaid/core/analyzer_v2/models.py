# filename: src/n8nmermaid/core/analyzer_v2/models.py
"""Pydantic models defining the structured results of workflow analysis (V2)."""

import logging
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field

from .constants import N8nConnectionLiteral

logger = logging.getLogger(__name__)


# --- Enums ---


class NodeGroupType(str, Enum):
    """Categorization of nodes based on function and connectivity."""

    TRIGGER = "Trigger"
    ACTION = "Action"
    ROUTER = "Router"  # e.g., IF, Switch
    STICKY = "Sticky"
    CLUSTER_ROOT = "ClusterRoot"  # Bridge between main and non-main connections
    CLUSTER_SUB_ROOT = (
        "ClusterSubRoot"  # Intermediate node within non-main cluster graph
    )
    CLUSTER_SUB = "ClusterSub"  # Leaf or simple node within non-main cluster graph
    UNKNOWN = "Unknown"


class ClusterRole(str, Enum):
    """Role of a node within a non-main connection cluster."""

    ROOT = "Root"
    SUB_ROOT = "SubRoot"
    SUB = "Sub"


# --- Detail Models ---


class ConnectionDetail(BaseModel):
    """Detailed information about a single connection between two nodes."""

    source_node_id: str
    source_port_name: str  # e.g., "main_0", "ai_tool_0"
    target_node_id: str
    target_port_name: str  # e.g., "main", "ai_tool" (may need inference)
    connection_type: N8nConnectionLiteral  # 'main', 'ai_tool', etc.


class NodeConnectivityV2(BaseModel):
    """Structured node connection information using detailed lists."""

    incoming_connections: list[ConnectionDetail] = Field(default_factory=list)
    outgoing_connections: list[ConnectionDetail] = Field(default_factory=list)


class NodeClassificationV2(BaseModel):
    """Node classification focusing on group type and end status."""

    group_type: NodeGroupType = NodeGroupType.UNKNOWN
    is_end_node: bool = False  # True if node has no outgoing 'main' connections


class ClusterInfoV2(BaseModel):
    """Cluster membership information (based on non-'main' connections)."""

    is_clustered: bool = False
    cluster_root_id: str | None = None  # ID of the root node of this cluster
    cluster_role: ClusterRole | None = None  # Role within its cluster


class NodeCredentialDetailV2(BaseModel):
    """Details of a specific credential configuration used by a node."""

    id: str | None = None
    name: str | None = None


class CredentialsV2(BaseModel):
    """Credential usage summary for a node."""

    has_credentials: bool = False
    details: dict[str, NodeCredentialDetailV2] = Field(default_factory=dict)


# --- Main Node Model ---


class AnalyzedNodeV2(BaseModel):
    """Comprehensive analyzed information for a single n8n node (V2)."""

    # Core Info from Raw Node
    id: str
    name: str
    type: str
    type_version: float | None = None
    position: list[float] | None = None
    is_disabled: bool = False
    notes: str | None = None

    # Raw and Extracted Parameters
    raw_parameters: dict[str, Any] = Field(default_factory=dict)
    extracted_parameters: dict[str, Any] = Field(
        default_factory=dict
    )  # Flattened params

    # Processed Information
    connectivity: NodeConnectivityV2 = Field(default_factory=NodeConnectivityV2)
    classification: NodeClassificationV2 = Field(default_factory=NodeClassificationV2)
    cluster: ClusterInfoV2 = Field(default_factory=ClusterInfoV2)
    credentials: CredentialsV2 = Field(default_factory=CredentialsV2)
    parameter_categories: dict[str, list[str]] = Field(
        default_factory=dict
    )  # Added Phase 6 output

    class Config:
        """Pydantic configuration."""

        arbitrary_types_allowed = True
        use_enum_values = True  # Store enum values as strings in output


# --- Top-Level Workflow Analysis Model ---


class WorkflowAnalysisV2(BaseModel):
    """The complete, structured result of analyzing an n8n workflow (V2)."""

    # Workflow Metadata
    workflow_name: str | None = None
    workflow_tags: list[dict[str, Any]] = Field(default_factory=list)
    workflow_id: str | None = None
    workflow_version_id: str | None = None

    # Analyzed Nodes
    nodes: dict[str, AnalyzedNodeV2] = Field(default_factory=dict)

    # Analysis Metadata
    analysis_warnings: list[str] = Field(default_factory=list)

    class Config:
        """Pydantic configuration."""

        use_enum_values = True  # Store enum values as strings in output
