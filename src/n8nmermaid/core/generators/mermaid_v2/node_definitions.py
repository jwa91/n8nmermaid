# src/n8nmermaid/core/generators/mermaid_v2/node_definitions.py
"""Functions for generating V2 Mermaid node and subgraph definitions."""

import logging

from .constants import N8N_CONNECTION_TYPE_MAIN
from n8nmermaid.core.analyzer_v2.models import (
    AnalyzedNodeV2,
    NodeGroupType,
    WorkflowAnalysisV2,
)
from n8nmermaid.models_v2.request_v2_models import MermaidGenerationParamsV2

from .constants import END_SYMBOL_SUFFIX, START_SYMBOL_SUFFIX
from .helpers import (
    format_node_definition,
    format_node_label,
    get_connection_label_parts,
    get_mermaid_shape,
    sanitize_mermaid_label,
)

logger = logging.getLogger(__name__)


def _define_one_subgraph(
    root_node: AnalyzedNodeV2,
    analysis: WorkflowAnalysisV2,
    params: MermaidGenerationParamsV2,
) -> tuple[list[str], set[str]]:
    """
    Generates definition lines for a single subgraph and its contents (V2).

    Includes internal node definitions and internal connections.

    Args:
        root_node: The root node (AnalyzedNodeV2) of the cluster.
        analysis: The overall V2 workflow analysis.
        params: Mermaid generation parameters.

    Returns:
        A tuple containing:
        - List of Mermaid definition lines for the subgraph.
        - Set of node IDs defined within this subgraph (root + sub-nodes).
    """
    subgraph_defs: list[str] = []
    subgraph_member_ids: set[str] = set()
    root_id = root_node.id

    subgraph_id = f"{root_id}_graph"
    subgraph_label = sanitize_mermaid_label(f"Agent: {root_node.name}")

    subgraph_defs.append(f'subgraph {subgraph_id} ["{subgraph_label}"]')
    subgraph_defs.append(f"    direction {params.subgraph_direction}")

    root_label = format_node_label(root_node, params)
    root_shape = get_mermaid_shape(root_node)
    subgraph_defs.append(
        f"    {format_node_definition(root_id, root_label, root_shape)}"
    )
    subgraph_member_ids.add(root_id)

    sub_nodes = sorted(
        [
            n
            for n in analysis.nodes.values()
            if n.cluster.cluster_root_id == root_id and n.id != root_id
        ],
        key=lambda n: (
            n.position[1] if n.position else 0,
            n.position[0] if n.position else 0,
            n.id,
        ),
    )

    logger.debug(
        "Defining %d sub-nodes for cluster %s", len(sub_nodes), root_id
    )
    for sub_node in sub_nodes:
        sub_label = format_node_label(sub_node, params)
        sub_shape = get_mermaid_shape(sub_node)
        subgraph_defs.append(
            f"    {format_node_definition(sub_node.id, sub_label, sub_shape)}"
        )
        subgraph_member_ids.add(sub_node.id)

    subgraph_connections: set[str] = set()
    all_member_nodes = {root_id} | subgraph_member_ids

    for member_id in all_member_nodes:
        source_node = analysis.nodes.get(member_id)
        if not source_node:
            continue

        for connection in source_node.connectivity.outgoing_connections:
            target_id = connection.target_node_id
            if target_id in all_member_nodes:
                arrow = (
                    "-->"
                    if connection.connection_type == N8N_CONNECTION_TYPE_MAIN
                    else "-.->"
                )
                label_parts = get_connection_label_parts(
                    source_node, connection
                )
                label_str = (
                    f'|"{" ".join(label_parts)}"|' if label_parts else ""
                )
                link = f"{member_id} {arrow}{label_str} {target_id}"
                subgraph_connections.add(link)

    if subgraph_connections:
        subgraph_defs.append("")
        subgraph_defs.append("    %% Internal Connections")
        subgraph_defs.extend(
            [f"    {conn}" for conn in sorted(subgraph_connections)]
        )

    subgraph_defs.append("end")
    subgraph_defs.append("")

    return subgraph_defs, all_member_nodes


def _handle_cluster_root_definition(
    node: AnalyzedNodeV2,
    analysis: WorkflowAnalysisV2,
    params: MermaidGenerationParamsV2,
    definitions: list[str],
    visible_diagram_element_ids: set[str],
    trigger_node_ids: list[str],
    end_node_ids: list[str],
    processed_nodes: set[str],
) -> None:
    """
    Handles definition logic for cluster root nodes based on display mode.

    Args:
        node: The cluster root node.
        analysis: The workflow analysis.
        params: Generation parameters.
        definitions: List to append definition strings to.
        visible_diagram_element_ids: Set of visible element IDs to update.
        trigger_node_ids: List of trigger IDs to update.
        end_node_ids: List of end node IDs to update.
        processed_nodes: Set of processed node IDs to update.
    """
    subgraph_mode = params.subgraph_display_mode
    node_id = node.id

    if subgraph_mode == "subgraph":
        subgraph_defs, subgraph_member_ids = _define_one_subgraph(
            node, analysis, params
        )
        definitions.extend(subgraph_defs)
        processed_nodes.update(subgraph_member_ids)
        visible_diagram_element_ids.add(f"{node_id}_graph")
        if (
            node.classification.group_type == NodeGroupType.TRIGGER
            and node_id not in trigger_node_ids
        ):
            trigger_node_ids.append(node_id)
        if node.classification.is_end_node and node_id not in end_node_ids:
            end_node_ids.append(node_id)
    elif subgraph_mode in ["simple_node", "separate_clusters"]:
        logger.debug(
            "Defining cluster root %s as simple node (mode: %s)",
            node_id,
            subgraph_mode,
        )
        node_label = format_node_label(node, params)
        shape = get_mermaid_shape(node)
        definitions.append(format_node_definition(node_id, node_label, shape))
        processed_nodes.add(node_id)
        visible_diagram_element_ids.add(node_id)

        if (
            node.classification.group_type == NodeGroupType.TRIGGER
            and node_id not in trigger_node_ids
        ):
            trigger_node_ids.append(node_id)
        if node.classification.is_end_node and node_id not in end_node_ids:
            end_node_ids.append(node_id)

        sub_nodes_count = 0
        for sub_node_id, sub_node_check in analysis.nodes.items():
            if (
                sub_node_check.cluster.cluster_root_id == node_id
                and sub_node_id != node_id
            ):
                processed_nodes.add(sub_node_id)
                sub_nodes_count += 1
        if sub_nodes_count > 0:
            logger.debug(
                "Hiding %d sub-nodes for simplified cluster %s",
                sub_nodes_count,
                node_id,
            )


def _handle_regular_node_definition(
    node: AnalyzedNodeV2,
    params: MermaidGenerationParamsV2,
    definitions: list[str],
    visible_diagram_element_ids: set[str],
    trigger_node_ids: list[str],
    end_node_ids: list[str],
    processed_nodes: set[str],
) -> None:
    """
    Handles definition logic for non-clustered, non-sticky nodes.

    Args:
        node: The node to define.
        params: Generation parameters.
        definitions: List to append definition strings to.
        visible_diagram_element_ids: Set of visible element IDs to update.
        trigger_node_ids: List of trigger IDs to update.
        end_node_ids: List of end node IDs to update.
        processed_nodes: Set of processed node IDs to update.
    """
    node_id = node.id
    logger.debug("Defining non-clustered node %s", node_id)
    node_label = format_node_label(node, params)
    shape = get_mermaid_shape(node)
    definitions.append(format_node_definition(node_id, node_label, shape))
    processed_nodes.add(node_id)
    visible_diagram_element_ids.add(node_id)

    if (
        node.classification.group_type == NodeGroupType.TRIGGER
        and node_id not in trigger_node_ids
    ):
        trigger_node_ids.append(node_id)
    if node.classification.is_end_node and node_id not in end_node_ids:
        end_node_ids.append(node_id)


def define_nodes_and_subgraphs(
    analysis: WorkflowAnalysisV2, params: MermaidGenerationParamsV2
) -> tuple[list[str], list[str], list[str], set[str]]:
    """
    Generates node and subgraph definitions for the main diagram (V2).

    Args:
        analysis: The V2 workflow analysis results.
        params: Mermaid generation parameters.

    Returns:
        A tuple containing:
        - List of definition lines (nodes and subgraphs incl. internal links).
        - List of trigger node IDs visible/represented in the main diagram.
        - List of end node IDs visible/represented in the main diagram.
        - Set of all top-level node/subgraph IDs visible in the main diagram.
    """
    definitions: list[str] = []
    trigger_node_ids: list[str] = []
    end_node_ids: list[str] = []
    visible_diagram_element_ids: set[str] = set()
    processed_nodes: set[str] = set()
    subgraph_mode = params.subgraph_display_mode

    sorted_node_ids = sorted(
        analysis.nodes.keys(),
        key=lambda nid: (
            analysis.nodes[nid].position[1]
            if analysis.nodes[nid].position
            and len(analysis.nodes[nid].position) > 1
            else 0,
            analysis.nodes[nid].position[0]
            if analysis.nodes[nid].position
            and len(analysis.nodes[nid].position) > 0
            else 0,
            nid,
        ),
    )

    for node_id in sorted_node_ids:
        if node_id in processed_nodes:
            continue

        node = analysis.nodes[node_id]
        group_type = node.classification.group_type

        if group_type == NodeGroupType.STICKY:
            logger.debug("Skipping definition for StickyNote node %s", node_id)
            processed_nodes.add(node_id)
            continue

        is_cluster_root = group_type == NodeGroupType.CLUSTER_ROOT
        is_sub_node = node.cluster.is_clustered and not is_cluster_root

        if is_cluster_root:
            _handle_cluster_root_definition(
                node,
                analysis,
                params,
                definitions,
                visible_diagram_element_ids,
                trigger_node_ids,
                end_node_ids,
                processed_nodes,
            )
        elif is_sub_node and subgraph_mode in [
            "simple_node",
            "separate_clusters",
        ]:
            if node_id not in processed_nodes:
                logger.warning(
                    "Sub-node %s was not marked processed by its root in "
                    "mode %s. Skipping anyway.",
                    node_id,
                    subgraph_mode,
                )
                processed_nodes.add(node_id)
            continue
        elif not node.cluster.is_clustered:
            _handle_regular_node_definition(
                node,
                params,
                definitions,
                visible_diagram_element_ids,
                trigger_node_ids,
                end_node_ids,
                processed_nodes,
            )

    logger.debug(
        "define_nodes_and_subgraphs finished. Visible elements count: %d. "
        "Processed node count: %d",
        len(visible_diagram_element_ids),
        len(processed_nodes),
    )
    return (
        definitions,
        trigger_node_ids,
        end_node_ids,
        visible_diagram_element_ids,
    )


def define_start_end_symbols(
    trigger_ids: list[str], end_ids: list[str]
) -> list[str]:
    """
    Generates definitions for dedicated Start and End symbols (V2).

    Args:
        trigger_ids: List of IDs for trigger nodes needing a Start symbol.
        end_ids: List of IDs for end nodes needing an End symbol.

    Returns:
        A list of Mermaid definition lines for the Start/End symbols.
    """
    definitions = []
    symbol_count = 0
    if trigger_ids or end_ids:
        definitions.append("")
        definitions.append("%% Start/End Symbols")
        for trigger_id in trigger_ids:
            symbol_id = f"{trigger_id}{START_SYMBOL_SUFFIX}"
            shape = get_mermaid_shape(None, is_symbol="start")
            def_str = format_node_definition(symbol_id, "Start", shape)
            definitions.append(def_str)
            symbol_count += 1
        for end_id in end_ids:
            symbol_id = f"{end_id}{END_SYMBOL_SUFFIX}"
            shape = get_mermaid_shape(None, is_symbol="end")
            def_str = format_node_definition(symbol_id, "End", shape)
            definitions.append(def_str)
            symbol_count += 1
        logger.debug("Defined %d Start/End symbols.", symbol_count)
    return definitions
