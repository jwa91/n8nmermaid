# filename: src/n8nmermaid/core/analyzer_v2/phase_3_cluster_analysis.py
"""Phase 3: Identify clusters based on non-main connections."""

import logging
from collections import deque

from .models import AnalyzedNodeV2, ClusterInfoV2, ClusterRole

logger = logging.getLogger(__name__)


def _has_main_connections(node: AnalyzedNodeV2) -> bool:
    """Check if a node has any incoming or outgoing main connections."""
    for conn in node.connectivity.incoming_connections:
        if conn.connection_type == "main":
            return True
    for conn in node.connectivity.outgoing_connections:
        if conn.connection_type == "main":
            return True
    return False


def _has_non_main_connections(node: AnalyzedNodeV2) -> bool:
    """Check if a node has any incoming or outgoing non-main connections."""
    for conn in node.connectivity.incoming_connections:
        if conn.connection_type != "main":
            return True
    for conn in node.connectivity.outgoing_connections:
        if conn.connection_type != "main":
            return True
    return False


def _get_non_main_neighbors(
    node_id: str, nodes_dict: dict[str, AnalyzedNodeV2]
) -> set[str]:
    """Get IDs of neighbors connected via non-main links."""
    neighbors = set()
    node = nodes_dict.get(node_id)
    if not node:
        return neighbors

    for conn in node.connectivity.outgoing_connections:
        if conn.connection_type != "main":
            neighbors.add(conn.target_node_id)
    for conn in node.connectivity.incoming_connections:
        if conn.connection_type != "main":
            neighbors.add(conn.source_node_id)
    return neighbors


def analyze_clusters(nodes_dict: dict[str, AnalyzedNodeV2]) -> list[str]:
    """
    Identifies clusters based on non-'main' connections and assigns roles.

    Updates the `cluster` attribute of nodes involved in clusters.

    Args:
        nodes_dict: Dictionary mapping node IDs to AnalyzedNodeV2 objects.

    Returns:
        A list of warning messages generated during cluster analysis.
    """
    warnings: list[str] = []
    potential_roots = set()
    nodes_in_clusters: set[str] = set()

    # 1. Identify potential cluster roots
    for node_id, node in nodes_dict.items():
        if _has_main_connections(node) and _has_non_main_connections(node):
            potential_roots.add(node_id)
            logger.debug(
                "Identified potential cluster root: %s (%s)", node_id, node.name
            )

    cluster_count = 0

    # 2. Perform BFS from each root to identify cluster members
    for root_id in potential_roots:
        if root_id in nodes_in_clusters:
            continue

        root_node = nodes_dict[root_id]
        root_node.cluster = ClusterInfoV2(
            is_clustered=True, cluster_root_id=root_id, cluster_role=ClusterRole.ROOT
        )
        nodes_in_clusters.add(root_id)
        cluster_count += 1
        logger.info(
            "Starting cluster analysis for root: %s (%s)", root_id, root_node.name
        )

        queue: deque[str] = deque([root_id])
        visited_in_this_cluster: set[str] = {root_id}

        while queue:
            current_id = queue.popleft()
            # current_node variable removed as it was unused (F841 fix)

            neighbors = _get_non_main_neighbors(current_id, nodes_dict)

            for neighbor_id in neighbors:
                if (
                    neighbor_id not in nodes_dict
                    or neighbor_id in visited_in_this_cluster
                ):
                    continue

                neighbor_node = nodes_dict[neighbor_id]

                # Only add nodes that have non-main connections or are potential roots
                if (
                    not _has_non_main_connections(neighbor_node)
                    and neighbor_id not in potential_roots
                ):
                    continue

                if (
                    neighbor_id in nodes_in_clusters
                    and neighbor_node.cluster.cluster_root_id != root_id
                ):
                    warnings.append(
                        f"Node {neighbor_id} connected to multiple cluster roots "
                        f"({root_id} and {neighbor_node.cluster.cluster_root_id}). "
                        "Analysis might be ambiguous."
                    )
                    logger.warning(
                        "Node %s seems connected to multiple " "cluster roots.",
                        neighbor_id,
                    )
                    continue

                visited_in_this_cluster.add(neighbor_id)
                nodes_in_clusters.add(neighbor_id)

                # Determine role (SubRoot or Sub) - simplified logic
                has_unvisited_non_main_neighbors = False
                neighbor_neighbors = _get_non_main_neighbors(neighbor_id, nodes_dict)
                for nn_id in neighbor_neighbors:
                    neighbor_neighbor_node = nodes_dict.get(
                        nn_id, AnalyzedNodeV2(id="", name="", type="")
                    )
                    if (
                        nn_id not in visited_in_this_cluster
                        and _has_non_main_connections(neighbor_neighbor_node)
                    ):
                        has_unvisited_non_main_neighbors = True
                        break

                role = (
                    ClusterRole.SUB_ROOT
                    if has_unvisited_non_main_neighbors
                    else ClusterRole.SUB
                )

                neighbor_node.cluster = ClusterInfoV2(
                    is_clustered=True, cluster_root_id=root_id, cluster_role=role
                )
                logger.debug(
                    "Assigned node %s (%s) to cluster %s with role %s",
                    neighbor_id,
                    neighbor_node.name,
                    root_id,
                    role,
                )
                queue.append(neighbor_id)

    logger.info(
        "Phase 3: Cluster analysis complete. Identified %d cluster(s).", cluster_count
    )
    return warnings
