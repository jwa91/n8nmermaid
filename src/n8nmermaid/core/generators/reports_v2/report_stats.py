# src/n8nmermaid/core/generators/reports_v2/report_stats.py
"""Generates structured data for the V2 workflow statistics report."""

import logging
from collections import Counter

from n8nmermaid.core.analyzer_v2.models import NodeGroupType, WorkflowAnalysisV2

from .models import NodeCountByType, StatsReportData

logger = logging.getLogger(__name__)


def generate_stats_data_v2(analysis: WorkflowAnalysisV2) -> StatsReportData:
    """
    Generates the structured data for the Statistics report from V2 analysis.

    Counts elements like total nodes, nodes by type/group, credential
    usage, disabled status, cluster presence, and analysis warnings.

    Args:
        analysis: The completed WorkflowAnalysisV2 object.

    Returns:
        A StatsReportData object containing the calculated statistics.
    """
    if not analysis or not analysis.nodes:
        logger.warning("V2 Stats report: No nodes found in analysis.")
        return StatsReportData(total_nodes=0)

    nodes = list(analysis.nodes.values())
    node_types = Counter(node.type for node in nodes)
    node_groups = Counter(node.classification.group_type.value for node in nodes)

    nodes_with_creds = sum(1 for node in nodes if node.credentials.has_credentials)
    disabled_nodes = sum(1 for node in nodes if node.is_disabled)
    cluster_roots = sum(
        1
        for node in nodes
        if node.classification.group_type == NodeGroupType.CLUSTER_ROOT
    )

    nodes_by_type_list = [
        NodeCountByType(node_type=nt, count=c) for nt, c in node_types.items()
    ]

    stats_data = StatsReportData(
        total_nodes=len(nodes),
        nodes_by_type=nodes_by_type_list,
        nodes_by_role=dict(node_groups),
        nodes_with_credentials=nodes_with_creds,
        disabled_nodes=disabled_nodes,
        cluster_roots=cluster_roots,
        total_warnings=len(analysis.analysis_warnings),
    )
    logger.info("Generated V2 stats data: %d nodes processed.", len(nodes))
    return stats_data
