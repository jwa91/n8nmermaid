# src/n8nmermaid/core/generators/reports_v2/formatters.py
"""
Functions to format structured report data into output strings (V2).

Provides functions to convert V2 report data models into human-readable
text formats.
"""

import json
import logging
from typing import Any

from pydantic import BaseModel

from .models import (
    AgentsReportData,
    CredentialsReportData,
    CredentialUsageInfo,
    NodeParametersReportData,
    StatsReportData,
)

logger = logging.getLogger(__name__)


def _format_stats_report_text(data: StatsReportData) -> str:
    """Formats StatsReportData into a plain text string."""
    lines = ["## Workflow Statistics Report (V2)"]
    lines.append(f"- Total Nodes: {data.total_nodes}")
    lines.append(f"- Disabled Nodes: {data.disabled_nodes}")
    lines.append(f"- Nodes with Credentials: {data.nodes_with_credentials}")
    lines.append(f"- Identified Cluster Roots: {data.cluster_roots}")
    lines.append("\n### Nodes by Type:")
    if data.nodes_by_type:
        sorted_types = sorted(
            data.nodes_by_type, key=lambda x: (-x.count, x.node_type)
        )
        for item in sorted_types:
            lines.append(f"  - {item.node_type}: {item.count}")
    else:
        lines.append("  (No node types found)")
    lines.append("\n### Nodes by Group Type:")
    if data.nodes_by_role:
        for group_type_value, count in sorted(data.nodes_by_role.items()):
            lines.append(f"  - {group_type_value}: {count}")
    else:
        lines.append("  (No node groups found)")
    lines.append(f"\n- Analysis Warnings: {data.total_warnings}")
    return "\n".join(lines)


def _credential_sort_key(
    cred: CredentialUsageInfo,
) -> tuple[str, str]:
    """Provides a sort key for credentials based on type and name/ID."""
    return (cred.credential_type, cred.credential_name or cred.credential_id or "")


def _format_credentials_report_text(data: CredentialsReportData) -> str:
    """Formats CredentialsReportData into a plain text string."""
    lines = ["## Credentials Usage Report (V2)"]
    if not data.credentials_found:
        lines.append("- No credentials found in use.")
        return "\n".join(lines)

    for cred in sorted(data.credentials_found, key=_credential_sort_key):
        name_part = f" (Name: {cred.credential_name})" if cred.credential_name else ""
        id_part = f" (ID: {cred.credential_id})" if cred.credential_id else ""
        lines.append(f"\n### Credential: {cred.credential_type}{name_part}{id_part}")
        lines.append("  Used by nodes:")
        if cred.used_by_nodes:
            for node_ref in sorted(cred.used_by_nodes):
                lines.append(f"    - {node_ref}")
        else:
            lines.append("    (None specified)")
    return "\n".join(lines)


def _format_agents_report_text(data: AgentsReportData) -> str:
    """Formats AgentsReportData into a plain text string."""
    lines = ["## AI Agents Report (V2)"]
    if not data.agents:
        lines.append("- No Cluster Root nodes identified in the workflow.")
        return "\n".join(lines)

    for agent in sorted(data.agents, key=lambda x: x.node_name):
        lines.append(f"\n### Agent: {agent.node_name} ({agent.node_id})")
        lines.append(f"  - Model: {agent.model or 'Not specified/Found'}")

        if agent.model_credentials:
            lines.append("  - Model Credentials:")
            for cred in agent.model_credentials:
                name_part = f" (Name: {cred.name})" if cred.name else ""
                id_part = f" (ID: {cred.id})" if cred.id else ""
                lines.append(f"    - {cred.type}{name_part}{id_part}")
        else:
            lines.append("  - Model Credentials: None Found")

        if agent.system_message:
            formatted_msg = agent.system_message.replace("\n", "\n       ")
            lines.append(f'  - System Message:\n       "{formatted_msg}"')
        else:
            lines.append("  - System Message: None Found")

        if agent.tools_used:
            lines.append("  - Connected Tools:")
            for tool_info in agent.tools_used:
                lines.append(f"    - {tool_info}")
        else:
            lines.append("  - Connected Tools: None Found")

    return "\n".join(lines)


def _format_node_parameters_report_text(data: NodeParametersReportData) -> str:
    """Formats NodeParametersReportData into a plain text string."""
    lines = ["## Node Parameters Report (V2)"]
    if not data.node_types:
        lines.append("- No nodes with parameters found.")
        return "\n".join(lines)

    for type_group in sorted(data.node_types, key=lambda x: x.node_type):
        lines.append(f"\n### Node Type: {type_group.node_type}")
        if not type_group.node_details:
            lines.append("  (No nodes of this type found with parameters)")
            continue

        for node_detail in sorted(type_group.node_details, key=lambda x: x.node_name):
            lines.append(
                f"\n  --- Node: {node_detail.node_name} (ID: {node_detail.node_id}) ---"
            )
            if node_detail.raw_parameters:
                try:
                    params_str = json.dumps(
                        node_detail.raw_parameters, indent=2, sort_keys=True
                    )
                    indented_params = "\n".join(
                        f"    {line}" for line in params_str.splitlines()
                    )
                    lines.append(indented_params)
                except TypeError as e:
                    logger.error(
                        "Could not serialize parameters for node %s: %s",
                        node_detail.node_id,
                        e,
                    )
                    lines.append("    (Error serializing parameters)")
            else:
                lines.append("    (No parameters defined)")

    return "\n".join(lines)


def format_report(
    report_type: str, data: BaseModel | Any, format_style: str = "text"
) -> str:
    """
    Dispatches to the appropriate V2 formatting function based on type and style.

    Args:
        report_type: The key identifying the type of report (e.g., "stats").
        data: The structured Pydantic model or dict containing the report data.
        format_style: The desired output format (e.g., "text").

    Returns:
        The formatted report as a string.
    """
    formatter_map = {
        ("stats", "text"): _format_stats_report_text,
        ("credentials", "text"): _format_credentials_report_text,
        ("agents", "text"): _format_agents_report_text,
        ("node_parameters", "text"): _format_node_parameters_report_text,
    }

    formatter = formatter_map.get((report_type, format_style))

    if formatter:
        try:
            return formatter(data)  # type: ignore
        except Exception as e:
            logger.exception(
                "Error formatting report '%s' with style '%s'",
                report_type,
                format_style,
            )
            return f"Error formatting report '{report_type}': {e}"
    else:
        logger.warning(
            "No V2 formatter found for report type '%s' and format '%s'. Falling back.",
            report_type,
            format_style,
        )
        if isinstance(data, BaseModel):
            try:
                return data.model_dump_json(indent=2)
            except Exception as json_err:
                logger.error(
                    "Failed to dump Pydantic model to JSON for fallback: %s", json_err
                )
                return str(data)
        else:
            try:
                return json.dumps(data, indent=2)
            except TypeError:
                return str(data)
