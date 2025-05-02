# src/n8nmermaid/core/generators/mermaid_v2/helpers.py
"""Utility functions for V2 Mermaid diagram generation."""

import logging
import re
from typing import Any, Literal

from n8nmermaid.core.analyzer_v2.models import (
    AnalyzedNodeV2,
    ConnectionDetail,
    NodeGroupType,
)
from n8nmermaid.models_v2.request_v2_models import MermaidGenerationParamsV2

from .constants import (
    N8N_CONNECTION_TYPE_MAIN,
    NODE_GROUP_TO_SHAPE,
    SHAPE_START,
    SHAPE_STOP,
    MermaidShapeName,
)

logger = logging.getLogger(__name__)


def sanitize_mermaid_label(label: Any) -> str:
    """
    Escapes characters problematic for Mermaid labels within quotes.

    Args:
        label: The label content to sanitize.

    Returns:
        The sanitized label string suitable for Mermaid.
    """
    if not isinstance(label, str):
        label = str(label)
    escaped = label.replace("\\", "\\\\").replace('"', "#quot;")
    return escaped


def sanitize_filename(name: str, default: str = "unnamed_cluster") -> str:
    """
    Converts a string into a simplified, filesystem-safe filename component.

    Args:
        name: The input string (e.g., a node name).
        default: The fallback string if sanitization results in an empty string.

    Returns:
        A sanitized string suitable for use in filenames.
    """
    if not name:
        return default
    s = re.sub(r"[\s\./\\]+", "_", name)
    s = re.sub(r"[^\w\-\_]+", "", s)
    s = s.strip("_-")
    if not s:
        return default
    return s[:64]


def get_mermaid_shape(
    node: AnalyzedNodeV2 | None, is_symbol: Literal["start", "end"] | None = None
) -> MermaidShapeName:
    """
    Gets the Mermaid shape name based on V2 node group type or symbol type.

    Args:
        node: The AnalyzedNodeV2 object, or None if getting a symbol shape.
        is_symbol: Specify 'start' or 'end' to get the dedicated symbol shape.

    Returns:
        The appropriate Mermaid shape name.
    """
    if is_symbol == "start":
        return SHAPE_START
    if is_symbol == "end":
        return SHAPE_STOP

    if node is None:
        logger.warning("get_mermaid_shape called with None node and no symbol type.")
        return "rect"

    group_type = node.classification.group_type
    shape_name = NODE_GROUP_TO_SHAPE.get(group_type, "rect")
    logger.debug(
        "Node %s: Group '%s' -> Shape '%s'",
        node.id,
        group_type.value,
        shape_name,
    )
    return shape_name


def format_node_label(node: AnalyzedNodeV2, params: MermaidGenerationParamsV2) -> str:
    """
    Constructs the display label for a V2 node, applying formatting options.

    Args:
        node: The AnalyzedNodeV2 object.
        params: Mermaid generation parameters (V2) controlling label content.

    Returns:
        The formatted and sanitized label string for the node definition.
    """
    base_label = node.name
    extra_info = []

    if params.show_credentials and node.credentials.has_credentials:
        cred_names = [
            details.name or f"ID:{details.id[:8]}..."
            for details in node.credentials.details.values()
            if details.name or details.id
        ]
        if cred_names:
            extra_info.append(f"Creds: {', '.join(cred_names)}")

    if params.show_key_parameters:
        model_val = (
            node.extracted_parameters.get("model")
            or node.extracted_parameters.get("modelId")
            or node.extracted_parameters.get("model_identifier")
        )
        if model_val:
            model_str = str(model_val)
            if len(model_str) > 30:
                model_str = model_str[:27] + "..."
            extra_info.append(f"Model: {model_str}")

    if extra_info:
        safe_base = sanitize_mermaid_label(base_label)
        safe_extras = [sanitize_mermaid_label(info) for info in extra_info]
        return f'{safe_base}<br/>{"<br/>".join(safe_extras)}'
    else:
        return sanitize_mermaid_label(base_label)


def format_node_definition(
    node_id: str, label: str, shape_name: MermaidShapeName
) -> str:
    """
    Constructs the Mermaid 10+ node definition syntax string.

    Args:
        node_id: The unique identifier for the node in the diagram.
        label: The pre-formatted and sanitized display label for the node.
        shape_name: The Mermaid shape name.

    Returns:
        The complete node definition string.
    """
    valid_shape = shape_name if isinstance(shape_name, str) else "rect"
    definition = f'{node_id}@{{shape: {valid_shape}, label: "{label}"}}'
    logger.debug("Formatted definition for %s: %s", node_id, definition)
    return definition


def get_connection_label_parts(
    source_node: AnalyzedNodeV2, connection: ConnectionDetail
) -> list[str]:
    """
    Determines the label parts for a connection edge based on V2 detail.

    Args:
        source_node: The node originating the connection.
        connection: The ConnectionDetail object for the specific link.

    Returns:
        A list of strings to be joined for the connection label. Empty if no
        specific label is needed.
    """
    label_parts = []
    conn_type = connection.connection_type
    source_port = connection.source_port_name
    source_group_type = source_node.classification.group_type

    if conn_type == N8N_CONNECTION_TYPE_MAIN:
        if (
            source_group_type == NodeGroupType.ROUTER
            and source_port.startswith("main_")
        ):
            try:
                port_index_str = source_port.split("_")[-1]
                port_index = int(port_index_str)
                label_parts.append(f"({port_index})")
            except (ValueError, IndexError, AttributeError):
                label_parts.append(f"({source_port})")

    elif conn_type != N8N_CONNECTION_TYPE_MAIN:
        ai_label = conn_type.replace("ai_", "")
        label_parts.append(f"({ai_label})")

    return [sanitize_mermaid_label(part) for part in label_parts]


def _get_display_ids_subgraph_mode(
    source_node: AnalyzedNodeV2, target_node: AnalyzedNodeV2
) -> tuple[str, str, str]:
    """
    Helper to determine display IDs for 'subgraph' mode.

    Args:
        source_node: The source node.
        target_node: The target node.

    Returns:
        A tuple of (display_source_id, display_target_id, log_context).
    """
    source_id = source_node.id
    target_id = target_node.id
    source_is_clustered = source_node.cluster.is_clustered
    target_is_clustered = target_node.cluster.is_clustered
    source_root_id = source_node.cluster.cluster_root_id
    target_root_id = target_node.cluster.cluster_root_id

    display_source_id = source_id
    display_target_id = target_id
    log_context = "standard"

    if (
        source_is_clustered
        and target_is_clustered
        and source_root_id != target_root_id
        and source_root_id
        and target_root_id
    ):
        display_source_id = f"{source_root_id}_graph"
        display_target_id = f"{target_root_id}_graph"
        log_context = "cross_cluster_subgraph"
    elif source_is_clustered and not target_is_clustered and source_root_id:
        display_source_id = f"{source_root_id}_graph"
        log_context = "exit_cluster_subgraph"
    elif not source_is_clustered and target_is_clustered and target_root_id:
        display_target_id = f"{target_root_id}_graph"
        log_context = "enter_cluster_subgraph"
    elif (
        source_is_clustered
        and target_is_clustered
        and source_root_id == target_root_id
    ):
        log_context = "internal_cluster_subgraph"

    return display_source_id, display_target_id, log_context


def _get_display_ids_simple_mode(
    source_node: AnalyzedNodeV2, target_node: AnalyzedNodeV2
) -> tuple[str, str, str]:
    """
    Helper to determine display IDs for 'simple_node'/'separate_clusters'.

    Args:
        source_node: The source node.
        target_node: The target node.

    Returns:
        A tuple of (display_source_id, display_target_id, log_context).
    """
    source_id = source_node.id
    target_id = target_node.id
    source_is_clustered = source_node.cluster.is_clustered
    target_is_clustered = target_node.cluster.is_clustered
    source_root_id = source_node.cluster.cluster_root_id
    target_root_id = target_node.cluster.cluster_root_id
    source_is_root = (
        source_node.classification.group_type == NodeGroupType.CLUSTER_ROOT
    )
    target_is_root = (
        target_node.classification.group_type == NodeGroupType.CLUSTER_ROOT
    )

    display_source_id = source_id
    display_target_id = target_id
    log_context = "standard"

    is_source_sub_node = source_is_clustered and not source_is_root
    is_target_sub_node = target_is_clustered and not target_is_root

    if is_source_sub_node and source_root_id:
        display_source_id = source_root_id
        log_context = "source_rerouted_from_sub"
    if is_target_sub_node and target_root_id:
        display_target_id = target_root_id
        log_context = (
            f"{log_context}_target_rerouted_from_sub"
            if log_context != "standard"
            else "target_rerouted_from_sub"
        )

    if display_source_id == source_node.id:
        is_final_source_cluster_rep = source_is_root
    elif display_source_id == source_root_id:
        is_final_source_cluster_rep = True
    else:
        is_final_source_cluster_rep = False

    if display_target_id == target_node.id:
        is_final_target_cluster_rep = target_is_root
    elif display_target_id == target_root_id:
        is_final_target_cluster_rep = True
    else:
        is_final_target_cluster_rep = False

    is_same_cluster_root = (
        is_final_source_cluster_rep
        and is_final_target_cluster_rep
        and display_source_id == display_target_id
    )

    if is_same_cluster_root:
        log_context = "internal_cluster_simple_selfloop"
    elif is_final_source_cluster_rep and is_final_target_cluster_rep:
        log_context = "cross_cluster_simple"
    elif is_final_source_cluster_rep and not is_final_target_cluster_rep:
        log_context = "exit_cluster_simple"
    elif not is_final_source_cluster_rep and is_final_target_cluster_rep:
        log_context = "enter_cluster_simple"

    return display_source_id, display_target_id, log_context


def get_display_ids_and_context(
    source_node: AnalyzedNodeV2,
    target_node: AnalyzedNodeV2,
    params: MermaidGenerationParamsV2,
) -> tuple[str, str, str]:
    """
    Determines the source/target IDs for linking in the main diagram (V2).

    Handles subgraph boundaries or simplified nodes based on display mode.

    Args:
        source_node: The source node (AnalyzedNodeV2).
        target_node: The target node (AnalyzedNodeV2).
        params: Mermaid generation parameters (V2).

    Returns:
        A tuple containing:
        - Effective source ID for Mermaid link.
        - Effective target ID for Mermaid link.
        - Logging context string.
    """
    mode = params.subgraph_display_mode

    if mode == "subgraph":
        display_source_id, display_target_id, log_context = (
            _get_display_ids_subgraph_mode(source_node, target_node)
        )
    elif mode in ["simple_node", "separate_clusters"]:
        display_source_id, display_target_id, log_context = (
            _get_display_ids_simple_mode(source_node, target_node)
        )
    else:
        logger.warning("Invalid subgraph_display_mode '%s'. Falling back.", mode)
        display_source_id = source_node.id
        display_target_id = target_node.id
        log_context = "standard_fallback"

    is_visual_self_loop = display_source_id == display_target_id
    original_ids_different = source_node.id != target_node.id
    is_subgraph_self_link = mode == "subgraph" and "_graph" in display_source_id

    if is_visual_self_loop and (original_ids_different or is_subgraph_self_link):
        logger.debug(
            "Visual self-loop detected for '%s' in mode '%s'. "
            "Original: %s -> %s. Will be skipped by caller.",
            display_source_id,
            mode,
            source_node.id,
            target_node.id,
        )

    return display_source_id, display_target_id, log_context
