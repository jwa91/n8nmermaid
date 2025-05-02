# filename: src/n8nmermaid/core/analyzer_v2/phase_4_node_classification.py
"""Phase 4: Classify nodes based on type, connectivity, and cluster info."""

import logging

from .constants import STICKY_NODE_TYPE
from .models import AnalyzedNodeV2, ClusterRole, NodeGroupType

logger = logging.getLogger(__name__)


def _is_potential_router(node: AnalyzedNodeV2) -> bool:
    """Check if a node acts as a router based on outgoing main ports."""
    main_output_ports_used = set()
    for conn in node.connectivity.outgoing_connections:
        if conn.connection_type == "main" and conn.source_port_name.startswith(
            "main_"
        ):
            main_output_ports_used.add(conn.source_port_name)
    # If more than one distinct main output port (e.g., main_0, main_1) is used
    return len(main_output_ports_used) > 1


def classify_nodes(nodes_dict: dict[str, AnalyzedNodeV2]) -> list[str]:
    """
    Classifies each node's group type and determines if it's an end node.

    Updates the `classification` field of each AnalyzedNodeV2. Needs to run
    AFTER cluster analysis (Phase 3).

    Args:
        nodes_dict: Dictionary mapping node IDs to AnalyzedNodeV2 objects.

    Returns:
        A list of warning messages generated during classification.
    """
    warnings: list[str] = []
    classification_counts: dict[NodeGroupType, int] = {}

    if not nodes_dict:
        logger.warning("Phase 4: No nodes found to classify.")
        return warnings

    for node_id, node in nodes_dict.items():
        # 1. Determine if it's an end node (no outgoing main connections)
        has_outgoing_main = any(
            conn.connection_type == "main"
            for conn in node.connectivity.outgoing_connections
        )
        node.classification.is_end_node = not has_outgoing_main

        # 2. Determine Group Type based on priority
        group_type = NodeGroupType.UNKNOWN  # Default

        if node.type == STICKY_NODE_TYPE:
            group_type = NodeGroupType.STICKY
        elif node.cluster.is_clustered:
            # Assign type based on cluster role determined in Phase 3
            if node.cluster.cluster_role == ClusterRole.ROOT:
                group_type = NodeGroupType.CLUSTER_ROOT
            elif node.cluster.cluster_role == ClusterRole.SUB_ROOT:
                group_type = NodeGroupType.CLUSTER_SUB_ROOT
            elif node.cluster.cluster_role == ClusterRole.SUB:
                group_type = NodeGroupType.CLUSTER_SUB
            else:
                warnings.append(
                    f"Node {node_id} is clustered but has no role assigned."
                )
                group_type = NodeGroupType.UNKNOWN
        else:
            # Node is not Sticky and not part of a cluster
            has_incoming_main = any(
                conn.connection_type == "main"
                for conn in node.connectivity.incoming_connections
            )
            if not has_incoming_main:
                group_type = NodeGroupType.TRIGGER
            elif _is_potential_router(node):
                group_type = NodeGroupType.ROUTER
            else:
                # Standard node in the main flow
                group_type = NodeGroupType.ACTION

        node.classification.group_type = group_type
        classification_counts[group_type] = (
            classification_counts.get(group_type, 0) + 1
        )
        logger.debug(
            "Classified node %s (%s) as Group: %s, IsEndNode: %s",
            node_id,
            node.name,
            group_type.value,
            node.classification.is_end_node,
        )

    logger.info(
        "Phase 4: Node classification complete. Counts: %s", dict(classification_counts)
    )
    unknown_nodes = classification_counts.get(NodeGroupType.UNKNOWN, 0)
    if unknown_nodes > 0:
        unknown_ids = [
            nid
            for nid, n in nodes_dict.items()
            if n.classification.group_type == NodeGroupType.UNKNOWN
        ]
        warning_msg = (
            f"Found {unknown_nodes} nodes with Unknown classification: {unknown_ids}"
        )
        warnings.append(warning_msg)
        logger.warning(warning_msg)

    return warnings
