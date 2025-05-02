# filename: src/n8nmermaid/core/analyzer_v2/phase_2_connection_mapping.py
"""Phase 2: Mapping connections between nodes."""

import logging
from typing import Any, cast

from .constants import N8nConnectionLiteral
from .models import AnalyzedNodeV2, ConnectionDetail

logger = logging.getLogger(__name__)


def _log_missing_connection_node(
    node_kind: str,
    node_name: str,
    warnings: list[str],
    source_name_context: str | None = None,
    target_name_context: str | None = None,
) -> None:
    """Logs info about nodes referenced in connections but not found/valid."""
    context = ""
    if source_name_context and target_name_context:
        context = (
            f"Connection from '{source_name_context}' to "
            f"'{target_name_context}': "
        )
    elif source_name_context:
        context = f"Connection from '{source_name_context}': "

    msg = (
        f"{context}Skipping connection involving {node_kind} node '{node_name}': "
        "Node not found/valid (check name, duplicates, or earlier errors)."
    )
    warnings.append(msg)
    logger.warning(msg)


def map_connections(
    nodes_dict: dict[str, AnalyzedNodeV2],
    name_to_id: dict[str, str],
    raw_connections: dict[str, Any],
) -> list[str]:
    """
    Analyzes raw connection data and populates node connectivity details.

    Updates the `connectivity.incoming_connections` and
    `connectivity.outgoing_connections` lists for each node in nodes_dict.

    Args:
        nodes_dict: Dictionary mapping node IDs to AnalyzedNodeV2 objects.
        name_to_id: Dictionary mapping node names to their corresponding node IDs.
        raw_connections: The 'connections' dictionary from the raw workflow JSON.

    Returns:
        A list of warning messages generated during connection processing.
    """
    warnings: list[str] = []
    connection_parse_errors = 0
    total_connections_processed = 0

    if not isinstance(raw_connections, dict):
        warnings.append(
            f"Workflow 'connections' data is not a dict "
            f"(found {type(raw_connections).__name__}). Skipping connection analysis."
        )
        return warnings

    for source_name, output_types in raw_connections.items():
        source_id = name_to_id.get(source_name)

        if not source_id or source_id not in nodes_dict:
            _log_missing_connection_node("source", source_name, warnings)
            connection_parse_errors += 1
            continue

        source_node = nodes_dict[source_id]

        if not isinstance(output_types, dict):
            warnings.append(
                f"Connections data for source node '{source_name}' (ID: {source_id}) "
                "is not a dict. Skipping."
            )
            connection_parse_errors += 1
            continue

        for conn_type_str, output_ports in output_types.items():
            try:
                # Validate and cast connection type
                conn_type = cast(N8nConnectionLiteral, conn_type_str)
            except Exception:
                warnings.append(
                    f"Unknown connection type '{conn_type_str}' from node "
                    f"'{source_name}'. Skipping."
                )
                connection_parse_errors += 1
                continue

            if not isinstance(output_ports, list):
                warnings.append(
                    f"Connection type '{conn_type}' from '{source_name}' "
                    f"expected list, got {type(output_ports).__name__}. Skipping."
                )
                connection_parse_errors += 1
                continue

            # Process each output port for the current connection type
            for port_index, targets in enumerate(output_ports):
                if not isinstance(targets, list):
                    logger.debug(
                        "Output port %d for type '%s' from '%s' "
                        "is not a list of targets.",
                        port_index,
                        conn_type,
                        source_name,
                    )
                    continue

                # Process each target connection from this specific port
                for connection in targets:
                    if not isinstance(connection, dict):
                        warnings.append(
                            f"Connection target from '{source_name}' "
                            f"(port {port_index}, type {conn_type}) "
                            "is not a dictionary. Skipping."
                        )
                        connection_parse_errors += 1
                        continue

                    target_node_name = connection.get("node")
                    target_port_type = connection.get(
                        "type"
                    )  # Input port name/type on target
                    # target_port_index = connection.get("index", 0) # Not used here

                    if not target_node_name:
                        warnings.append(
                            f"Connection from '{source_name}' (port {port_index}, "
                            f"type {conn_type}) missing target node name. Skipping."
                        )
                        connection_parse_errors += 1
                        continue

                    target_id = name_to_id.get(str(target_node_name))

                    if not target_id or target_id not in nodes_dict:
                        _log_missing_connection_node(
                            "target",
                            str(target_node_name),
                            warnings,
                            source_name_context=source_name,
                        )
                        connection_parse_errors += 1
                        continue

                    target_node = nodes_dict[target_id]

                    # Construct port names
                    source_port_name = f"{conn_type}_{port_index}"
                    # Target port name often just the type
                    target_port_name = (
                        str(target_port_type) if target_port_type else conn_type
                    )

                    detail = ConnectionDetail(
                        source_node_id=source_id,
                        source_port_name=source_port_name,
                        target_node_id=target_id,
                        target_port_name=target_port_name,
                        connection_type=conn_type,
                    )

                    source_node.connectivity.outgoing_connections.append(detail)
                    target_node.connectivity.incoming_connections.append(detail)
                    total_connections_processed += 1

                    logger.debug(
                        "Mapped connection: %s (%s) -> %s (%s) via type %s",
                        source_id,
                        source_port_name,
                        target_id,
                        target_port_name,
                        conn_type,
                    )

    logger.info(
        "Phase 2: Connection mapping complete. Processed %d connections.",
        total_connections_processed,
    )
    if connection_parse_errors > 0:
        warnings.append(
            f"{connection_parse_errors} connection issues found during mapping "
            "(see logs/previous warnings)."
        )
        logger.warning(
            "Phase 2: %d connection issues found (check logs).",
            connection_parse_errors,
        )

    return warnings
