# src/n8nmermaid/core/generators/mermaid_v2/connection_definitions.py
"""Functions for generating V2 Mermaid connection definitions."""

import logging

from .constants import N8N_CONNECTION_TYPE_MAIN
from n8nmermaid.core.analyzer_v2.models import (
    AnalyzedNodeV2,
    ConnectionDetail,
    WorkflowAnalysisV2,
)
from n8nmermaid.models_v2.request_v2_models import MermaidGenerationParamsV2

from .constants import END_SYMBOL_SUFFIX, START_SYMBOL_SUFFIX
from .helpers import get_connection_label_parts, get_display_ids_and_context

logger = logging.getLogger(__name__)


def _process_single_connection(
    source_node: AnalyzedNodeV2,
    connection: ConnectionDetail,
    analysis_nodes: dict[str, AnalyzedNodeV2],
    params: MermaidGenerationParamsV2,
    visible_diagram_element_ids: set[str],
) -> str | None:
    """
    Processes a single connection detail.

    Args:
        source_node: The node where the connection originates.
        connection: The connection detail object.
        analysis_nodes: A dictionary mapping node IDs to AnalyzedNodeV2 objects.
        params: Mermaid generation parameters.
        visible_diagram_element_ids: Set of IDs visible in the current diagram context.

    Returns:
        A Mermaid diagram link string, or None if the connection should be skipped.
    """
    target_id = connection.target_node_id
    target_node = analysis_nodes.get(target_id)

    if not target_node:
        logger.warning(
            "Connection source %s links to unknown target %s (%s). Skipping.",
            source_node.id,
            target_id,
            connection.connection_type,
        )
        return None

    disp_src, disp_tgt, log_ctx = get_display_ids_and_context(
        source_node, target_node, params
    )

    if disp_src == disp_tgt:
        logger.debug(
            "Skipping connection %s -> %s as source/target resolve to "
            "same display ID: %s (Context: %s, Mode: %s)",
            source_node.id,
            target_id,
            disp_src,
            log_ctx,
            params.subgraph_display_mode,
        )
        return None

    is_subgraph_link = params.subgraph_display_mode == "subgraph" and (
        "_graph" in disp_src or "_graph" in disp_tgt
    )

    if not is_subgraph_link and not (
        disp_src in visible_diagram_element_ids
        and disp_tgt in visible_diagram_element_ids
    ):
        logger.debug(
            "Skipping link %s -> %s because display elements "
            "'%s' or '%s' are not in the visible set for mode %s",
            source_node.id,
            target_id,
            disp_src,
            disp_tgt,
            params.subgraph_display_mode,
        )
        return None

    arrow = (
        "-->"
        if connection.connection_type == N8N_CONNECTION_TYPE_MAIN
        else "-.->"
    )
    label_parts = get_connection_label_parts(source_node, connection)
    label_str = f'|"{" ".join(label_parts)}"|' if label_parts else ""

    mermaid_link = f"{disp_src} {arrow}{label_str} {disp_tgt}"

    logger.debug(
        "Formatted %s link (%s, Mode: %s): %s",
        connection.connection_type,
        log_ctx,
        params.subgraph_display_mode,
        mermaid_link,
    )
    return mermaid_link


def generate_node_connections(
    analysis: WorkflowAnalysisV2,
    params: MermaidGenerationParamsV2,
    visible_diagram_element_ids: set[str],
) -> list[str]:
    """
    Generates Mermaid connection lines for the main diagram (V2).

    Args:
        analysis: The V2 workflow analysis results.
        params: Mermaid generation parameters (V2).
        visible_diagram_element_ids: Set of node/subgraph IDs visible.

    Returns:
        A list of strings, each representing a Mermaid connection definition.
    """
    definitions: set[str] = set()
    connection_errors = 0

    for _, source_node in sorted(analysis.nodes.items()):
        for connection in source_node.connectivity.outgoing_connections:
            mermaid_link = _process_single_connection(
                source_node,
                connection,
                analysis.nodes,
                params,
                visible_diagram_element_ids,
            )
            if mermaid_link:
                definitions.add(mermaid_link)
            elif (
                mermaid_link is None
                and analysis.nodes.get(connection.target_node_id) is None
            ):
                connection_errors += 1

    unique_definitions_list = sorted(definitions)
    logger.debug(
        "Generated %d unique node/subgraph connection lines for main diagram.",
        len(unique_definitions_list),
    )
    if connection_errors > 0:
        logger.warning(
            "Skipped %d connections due to missing target nodes (see logs).",
            connection_errors,
        )
    return unique_definitions_list


def generate_start_end_connections(
    analysis: WorkflowAnalysisV2,
    params: MermaidGenerationParamsV2,
    trigger_ids: list[str],
    end_node_ids: list[str],
) -> list[str]:
    """
    Generates connections involving the dedicated Start/End symbols (V2).

    Args:
        analysis: The V2 workflow analysis results.
        params: Mermaid generation parameters (V2).
        trigger_ids: List of IDs for nodes classified as triggers.
        end_node_ids: List of IDs for nodes classified as end nodes.

    Returns:
        A list of strings, each representing a Start/End connection definition.
    """
    start_end_connections: set[str] = set()
    arrow = "-->"

    from n8nmermaid.core.analyzer_v2.models import AnalyzedNodeV2

    for trigger_id in trigger_ids:
        trigger_node = analysis.nodes.get(trigger_id)
        if not trigger_node:
            continue

        start_symbol_id = f"{trigger_id}{START_SYMBOL_SUFFIX}"
        dummy_start_symbol_node = AnalyzedNodeV2(
            id=start_symbol_id,
            name="StartSymbol",
            type="symbol",
            raw_parameters={},
            extracted_parameters={},
            parameter_categories={},
        )

        disp_src, disp_tgt, log_ctx = get_display_ids_and_context(
            dummy_start_symbol_node, trigger_node, params
        )

        link = f"{start_symbol_id} {arrow} {disp_tgt}"
        start_end_connections.add(link)
        logger.debug("Added start link (%s): %s", log_ctx, link)

    for end_id in end_node_ids:
        end_node = analysis.nodes.get(end_id)
        if not end_node:
            continue

        end_symbol_id = f"{end_id}{END_SYMBOL_SUFFIX}"
        dummy_end_symbol_node = AnalyzedNodeV2(
            id=end_symbol_id,
            name="EndSymbol",
            type="symbol",
            raw_parameters={},
            extracted_parameters={},
            parameter_categories={},
        )

        disp_src, disp_tgt, log_ctx = get_display_ids_and_context(
            end_node, dummy_end_symbol_node, params
        )

        link = f"{disp_src} {arrow} {end_symbol_id}"
        if disp_src != end_symbol_id:
            start_end_connections.add(link)
            logger.debug("Added end link (%s): %s", log_ctx, link)
        else:
            logger.debug(
                "Skipped end link for %s as display source (%s) matches symbol "
                "ID (%s) in mode %s",
                end_id,
                disp_src,
                end_symbol_id,
                params.subgraph_display_mode,
            )

    return sorted(start_end_connections)
