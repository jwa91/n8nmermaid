# src/n8nmermaid/models_v2/__init__.py
"""Initializes the V2 models package, exporting key data structures."""

from n8nmermaid.core.analyzer_v2.constants import N8nConnectionLiteral
from n8nmermaid.core.analyzer_v2.models import (
    AnalyzedNodeV2,
    ClusterInfoV2,
    ClusterRole,
    ConnectionDetail,
    CredentialsV2,
    NodeClassificationV2,
    NodeConnectivityV2,
    NodeCredentialDetailV2,
    NodeGroupType,
    WorkflowAnalysisV2,
)
from n8nmermaid.core.generators.reports_v2.models import (
    AgentDetail,
    AgentsReportData,
    CredentialsReportData,
    CredentialUsageInfo,
    ModelCredentialInfo,
    NodeCountByType,
    NodeParameterDetail,
    NodeParametersReportData,
    NodeTypeParameters,
    StatsReportData,
)

from .request_v2_models import (
    AnalysisRequestV2,
    MermaidDirection,
    MermaidGenerationParamsV2,
    ReportFormat,
    ReportGenerationParamsV2,
    ReportType,
    RequestCommand,
    SubgraphDisplayMode,
)

# Define __all__ for explicit public interface
__all__ = [
    # V2 Request Models & Types
    "AnalysisRequestV2",
    "MermaidGenerationParamsV2",
    "ReportGenerationParamsV2",
    "RequestCommand",
    "ReportType",
    "ReportFormat",
    "SubgraphDisplayMode",
    "MermaidDirection",
    # V2 Analysis Result Models & Types
    "AnalyzedNodeV2",
    "WorkflowAnalysisV2",
    "NodeConnectivityV2",
    "ConnectionDetail",
    "NodeClassificationV2",
    "NodeGroupType",
    "CredentialsV2",
    "NodeCredentialDetailV2",
    "ClusterInfoV2",
    "ClusterRole",
    "N8nConnectionLiteral",
    "StatsReportData",
    "CredentialsReportData",
    "AgentsReportData",
    "NodeParametersReportData",
    "NodeCountByType",
    "CredentialUsageInfo",
    "AgentDetail",
    "ModelCredentialInfo",
    "NodeParameterDetail",
    "NodeTypeParameters",
]
