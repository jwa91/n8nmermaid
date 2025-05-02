# src/n8nmermaid/core/generators/reports_v2/report_credentials.py
"""Generates structured data for the V2 credentials usage report."""

import logging

from n8nmermaid.core.analyzer_v2.models import WorkflowAnalysisV2

from .models import CredentialsReportData, CredentialUsageInfo

logger = logging.getLogger(__name__)


def generate_credentials_data_v2(
    analysis: WorkflowAnalysisV2,
) -> CredentialsReportData:
    """
    Generates the structured data for the Credentials report from V2 analysis.

    Scans all nodes in the analysis for credential usage, aggregates the
    information, and returns a structured list of unique credentials found.

    Args:
        analysis: The completed WorkflowAnalysisV2 object.

    Returns:
        A CredentialsReportData object listing the used credentials and the
        nodes using them.
    """
    creds_map: dict[tuple[str, str | None, str | None], CredentialUsageInfo] = {}

    if not analysis or not analysis.nodes:
        logger.warning("V2 Credentials report: No nodes found in analysis.")
        return CredentialsReportData()

    for node in analysis.nodes.values():
        if node.credentials.has_credentials:
            for cred_type, details in node.credentials.details.items():
                key = (cred_type, details.name, details.id)
                if key not in creds_map:
                    creds_map[key] = CredentialUsageInfo(
                        credential_type=cred_type,
                        credential_name=details.name,
                        credential_id=details.id,
                        used_by_nodes=[],
                    )
                creds_map[key].used_by_nodes.append(f"{node.name} ({node.id})")

    cred_list = list(creds_map.values())
    logger.info(
        "Generated V2 credentials data: Found %d unique credentials.", len(cred_list)
    )
    return CredentialsReportData(credentials_found=cred_list)
