# filename: src/n8nmermaid/core/analyzer_v2/phase_1_initial_parse.py
"""Phase 1: Initial parsing of raw node data into AnalyzedNodeV2 objects."""

import logging
from typing import Any

from pydantic import ValidationError

from .models import (
    AnalyzedNodeV2,
    CredentialsV2,
    NodeCredentialDetailV2,
    WorkflowAnalysisV2,
)

logger = logging.getLogger(__name__)


def _parse_credentials(raw_credentials: Any) -> tuple[CredentialsV2, list[str]]:
    """
    Parses the raw credential data for a node.

    Args:
        raw_credentials: The 'credentials' dictionary from the raw node data.

    Returns:
        A tuple containing the parsed CredentialsV2 object and a list of warnings.
    """
    warnings: list[str] = []
    details: dict[str, NodeCredentialDetailV2] = {}
    has_creds = False

    if not isinstance(raw_credentials, dict):
        if raw_credentials is not None:
            warnings.append(
                "Credentials field is not a dictionary, skipping credential parsing."
            )
        return CredentialsV2(has_credentials=False), warnings

    if not raw_credentials:
        return CredentialsV2(has_credentials=False), warnings

    has_creds = True
    for cred_type, cred_data in raw_credentials.items():
        if isinstance(cred_data, dict):
            try:
                details[cred_type] = NodeCredentialDetailV2(
                    id=cred_data.get("id"), name=cred_data.get("name")
                )
            except ValidationError as e:
                warnings.append(
                    f"Validation error parsing credential type '{cred_type}': {e}"
                )
        else:
            warnings.append(
                f"Unexpected format for credential type '{cred_type}', expected dict."
            )

    return CredentialsV2(has_credentials=has_creds, details=details), warnings


def parse_initial_nodes(
    raw_workflow_data: dict[str, Any], analysis_result: WorkflowAnalysisV2
) -> tuple[dict[str, str], list[str]]:
    """
    Parses raw node list, creates initial AnalyzedNodeV2 objects, builds name map.

    Populates basic fields, raw_parameters, and credentials. Handles validation
    errors and duplicates. Updates analysis_result.nodes in place.

    Args:
        raw_workflow_data: The raw workflow dictionary.
        analysis_result: The WorkflowAnalysisV2 object to populate.

    Returns:
        A tuple containing:
        - Dictionary mapping unique node names to their corresponding node IDs.
        - List of warning messages generated during this phase.
    """
    nodes_dict: dict[str, AnalyzedNodeV2] = {}
    name_to_id: dict[str, str] = {}
    warnings: list[str] = []
    processed_ids: set[str] = set()
    duplicate_names: set[str] = set()

    raw_nodes_list = raw_workflow_data.get("nodes", [])
    initial_node_count = 0

    if not isinstance(raw_nodes_list, list):
        warnings.append(
            f"Workflow 'nodes' data is not a list "
            f"(found {type(raw_nodes_list).__name__}). Treating as empty."
        )
        raw_nodes_list = []
    else:
        initial_node_count = len(raw_nodes_list)

    invalid_or_duplicate_count = 0

    for i, node_data in enumerate(raw_nodes_list):
        node_name_default = f"Unnamed_Node_{i+1}"
        if not isinstance(node_data, dict):
            warnings.append(f"Skipping non-dictionary item in nodes list at index {i}.")
            invalid_or_duplicate_count += 1
            continue

        node_id = node_data.get("id")
        node_type = node_data.get("type")
        node_name = node_data.get("name", node_name_default)

        # Basic Validation
        if not node_id or not isinstance(node_id, str):
            warnings.append(
                f"Node '{node_name}' (index {i}) missing or invalid 'id'. Skipping."
            )
            invalid_or_duplicate_count += 1
            continue
        if not node_type or not isinstance(node_type, str):
            warnings.append(
                f"Node '{node_name}' (ID: {node_id}) missing or invalid 'type'. "
                "Skipping."
            )
            invalid_or_duplicate_count += 1
            continue
        if node_id in processed_ids:
            warnings.append(
                f"Duplicate node ID '{node_id}' found for node '{node_name}'. "
                "Skipping duplicate."
            )
            invalid_or_duplicate_count += 1
            continue

        processed_ids.add(node_id)

        # Handle Name Mapping and Duplicates
        if node_name and node_name != node_name_default:
            if node_name in name_to_id:
                if node_name not in duplicate_names:
                    original_id = name_to_id[node_name]
                    warnings.append(
                        f"Duplicate node name '{node_name}'. Connections will use "
                        f"first encountered ID: {original_id}."
                    )
                    duplicate_names.add(node_name)
            else:
                name_to_id[node_name] = node_id
        elif node_name == node_name_default:
            temp_name = node_name
            counter = 2
            while temp_name in name_to_id:
                temp_name = f"{node_name_default}_{counter}"
                counter += 1
            if temp_name != node_name:
                warnings.append(
                    f"Default node name '{node_name}' conflicted, renaming to "
                    f"'{temp_name}' for internal mapping."
                )
                node_name = temp_name
            name_to_id[node_name] = node_id

        # Create AnalyzedNodeV2 Object
        try:
            node_params = node_data.get("parameters", {})
            raw_creds = node_data.get("credentials")
            parsed_creds, cred_warnings = _parse_credentials(raw_creds)
            warnings.extend(
                f"Node '{node_name}' (ID: {node_id}): {w}" for w in cred_warnings
            )

            analyzed_node = AnalyzedNodeV2(
                id=node_id,
                name=node_name,
                type=node_type,
                type_version=node_data.get("typeVersion"),
                position=node_data.get("position"),
                is_disabled=node_data.get("disabled", False),
                notes=node_data.get("notes"),
                raw_parameters=node_params if isinstance(node_params, dict) else {},
                credentials=parsed_creds,
            )
            nodes_dict[node_id] = analyzed_node

        except ValidationError as e:
            warnings.append(
                f"Validation error creating AnalyzedNodeV2 for '{node_name}' "
                f"(ID: {node_id}): {e}. Skipping."
            )
            invalid_or_duplicate_count += 1
            if node_id in processed_ids:
                processed_ids.remove(node_id)
            if node_name in name_to_id and name_to_id[node_name] == node_id:
                del name_to_id[node_name]
            continue

    log_msg = (
        f"Phase 1: Processed {initial_node_count} raw node entries. "
        f"{len(nodes_dict)} valid nodes created."
    )
    if invalid_or_duplicate_count > 0:
        log_msg += f" ({invalid_or_duplicate_count} invalid/duplicates skipped)."
    logger.info(log_msg)
    if duplicate_names:
        logger.warning(
            "Phase 1: Found %d duplicate node name(s). Connections may be ambiguous.",
            len(duplicate_names),
        )

    # Update the main analysis result object
    analysis_result.nodes = nodes_dict
    analysis_result.workflow_name = raw_workflow_data.get("name")
    analysis_result.workflow_tags = raw_workflow_data.get("tags", [])
    analysis_result.workflow_id = raw_workflow_data.get("id")
    analysis_result.workflow_version_id = raw_workflow_data.get("versionId")

    return name_to_id, warnings
