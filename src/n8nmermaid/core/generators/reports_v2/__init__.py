# src/n8nmermaid/core/generators/reports_v2/__init__.py
"""
V2 Report generation module for n8nmermaid.

This package contains modules for generating structured data reports
based on V2 workflow analysis results and formatting that data.
"""

from .generator import ReportGeneratorError, ReportGeneratorV2
from .models import (
    AgentDetail,
    AgentsReportData,
    CredentialsReportData,
    CredentialUsageInfo,
    NodeCountByType,
    NodeParameterDetail,
    NodeParametersReportData,
    NodeTypeParameters,
    StatsReportData,
)

__all__ = [
    "ReportGeneratorV2",
    "ReportGeneratorError",
    "StatsReportData",
    "CredentialsReportData",
    "AgentsReportData",
    "NodeParametersReportData",
    "NodeCountByType",
    "CredentialUsageInfo",
    "AgentDetail",
    "NodeParameterDetail",
    "NodeTypeParameters",
]
