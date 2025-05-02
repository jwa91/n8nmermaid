# filename: src/n8nmermaid/core/analyzer_v2/phase_6_parameter_categorization.py
"""Phase 6: Categorize extracted parameters based on keywords."""

import logging

from .constants import PARAM_CATEGORIES
from .models import AnalyzedNodeV2

logger = logging.getLogger(__name__)


def categorize_parameters(nodes_dict: dict[str, AnalyzedNodeV2]) -> list[str]:
    """
    Categorizes extracted parameters based on keywords defined in constants.

    Updates the `parameter_categories` field of each AnalyzedNodeV2.

    Args:
        nodes_dict: Dictionary mapping node IDs to AnalyzedNodeV2 objects.

    Returns:
        A list of warning messages (currently none generated here).
    """
    warnings: list[str] = []
    nodes_processed = 0
    categories_found_count = 0

    # Use _node_id as node_id is not used in the loop (B007 fix)
    for _node_id, node in nodes_dict.items():
        categories: dict[str, list[str]] = {}
        # Use `in dict` instead of `in dict.keys()` (SIM118 fix)
        for param_key in node.extracted_parameters:
            key_lower = param_key.lower()
            for category, keywords in PARAM_CATEGORIES.items():
                # Check if any keyword is a substring of the parameter key part
                key_parts = key_lower.split(".")
                found_in_category = False
                for keyword in keywords:
                    # Check if keyword matches exactly any part or is a substring
                    if any(part == keyword or keyword in part for part in key_parts):
                        categories.setdefault(category, []).append(param_key)
                        found_in_category = True
                        break  # Assign to first matching category found
                # If assigned to a category, stop checking other categories
                if found_in_category:
                    break

        if categories:
            node.parameter_categories = categories
            categories_found_count += sum(len(v) for v in categories.values())
        nodes_processed += 1

    logger.info(
        "Phase 6: Parameter categorization complete. Processed %d nodes, "
        "found categories for %d parameter keys across nodes.",
        nodes_processed,
        categories_found_count,
    )
    return warnings
