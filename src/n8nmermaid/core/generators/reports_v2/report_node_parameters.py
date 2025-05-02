# src/n8nmermaid/core/generators/reports_v2/report_node_parameters.py
"""Generates structured data for the V2 Node Parameters report."""

import logging
from collections import defaultdict

from n8nmermaid.core.analyzer_v2.models import WorkflowAnalysisV2

from .models import (
    NodeParameterDetail,
    NodeParametersReportData,
    NodeTypeParameters,
)

logger = logging.getLogger(__name__)


def generate_node_parameters_data_v2(
    analysis: WorkflowAnalysisV2,
) -> NodeParametersReportData:
    """
    Generates the structured data for the Node Parameters report from V2 analysis.

    Groups nodes by type and lists the raw parameters for each node instance.

    Args:
        analysis: The completed WorkflowAnalysisV2 object.

    Returns:
        A NodeParametersReportData object with parameter details grouped by node type.
    """
    nodes_by_type: dict[str, list[NodeParameterDetail]] = defaultdict(list)

    if not analysis or not analysis.nodes:
        logger.warning("V2 Node parameter report: No nodes found in analysis.")
        return NodeParametersReportData()

    for _node_id, node in sorted(analysis.nodes.items()):
        detail = NodeParameterDetail(
            node_id=node.id,
            node_name=node.name,
            raw_parameters=node.raw_parameters,
        )
        nodes_by_type[node.type].append(detail)

    report_data_list = [
        NodeTypeParameters(node_type=nt, node_details=details)
        for nt, details in sorted(nodes_by_type.items())
    ]

    logger.info(
        "Generated V2 node parameter data for %d node types.",
        len(report_data_list),
    )
    return NodeParametersReportData(node_types=report_data_list)
