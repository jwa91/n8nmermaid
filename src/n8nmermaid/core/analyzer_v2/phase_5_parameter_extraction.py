# filename: src/n8nmermaid/core/analyzer_v2/phase_5_parameter_extraction.py
"""Phase 5: Generic flattening of raw node parameters."""

import logging
from typing import Any

from .models import AnalyzedNodeV2

logger = logging.getLogger(__name__)


def _flatten_dict(
    data: Any, parent_key: str = "", sep: str = "."
) -> dict[str, Any]:
    """
    Recursively flattens a nested dictionary or list structure.

    Args:
        data: The dictionary or list to flatten.
        parent_key: The base key string to prepend to flattened keys.
        sep: The separator character between keys.

    Returns:
        A flattened dictionary.
    """
    items: dict[str, Any] = {}
    if isinstance(data, dict):
        for k, v in data.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            items.update(_flatten_dict(v, new_key, sep=sep))
    elif isinstance(data, list):
        # Create indexed keys for list items
        for i, v in enumerate(data):
            new_key = f"{parent_key}{sep}{i}" if parent_key else str(i)
            items.update(_flatten_dict(v, new_key, sep=sep))
    else:
        # Base case: value is simple type
        if parent_key:
            items[parent_key] = data
        # If initial data is simple type, returns empty (shouldn't happen with params)

    return items


def extract_parameters(nodes_dict: dict[str, AnalyzedNodeV2]) -> list[str]:
    """
    Flattens the raw_parameters for each node into extracted_parameters.

    Args:
        nodes_dict: Dictionary mapping node IDs to AnalyzedNodeV2 objects.

    Returns:
        A list of warning messages (currently none generated here).
    """
    warnings: list[str] = []
    nodes_processed = 0
    total_params_extracted = 0

    for node_id, node in nodes_dict.items():
        try:
            if isinstance(node.raw_parameters, dict):
                flattened = _flatten_dict(node.raw_parameters)
                node.extracted_parameters = flattened
                total_params_extracted += len(flattened)
            else:
                warnings.append(
                    f"Node {node_id} ('{node.name}') has non-dict raw_parameters "
                    f"type: {type(node.raw_parameters)}. Skipping extraction."
                )
                logger.warning(
                    "Node %s ('%s') has non-dict raw_parameters type: %s.",
                    node_id,
                    node.name,
                    type(node.raw_parameters),
                )
            nodes_processed += 1
        except Exception as e:
            warnings.append(
                f"Error flattening parameters for node {node_id} ('{node.name}'): {e}"
            )
            logger.exception("Error during parameter flattening for node %s", node_id)

    logger.info(
        "Phase 5: Parameter extraction complete. Processed %d nodes, "
        "extracted %d parameters.",
        nodes_processed,
        total_params_extracted,
    )
    return warnings
