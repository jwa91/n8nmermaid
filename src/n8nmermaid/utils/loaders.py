# src/n8nmermaid/utils/loaders.py
"""
Functions for loading n8n workflow JSON. # Updated Docstring
Handles file reading, JSON parsing, and basic validation.
"""

import json
import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)



def load_workflow_from_file(filepath: Path) -> dict[str, Any] | None:
    """
    Loads and parses the n8n workflow JSON file from the given path.

    Handles file not found, JSON decoding errors, and checks if the top-level
    element is a dictionary. Removes UTF-8 BOM if present.

    Args:
        filepath: The path to the workflow JSON file.

    Returns:
        A dictionary representing the workflow, or None if loading or parsing fails.
    """
    logger.debug("Attempting to load workflow from: %s", filepath)
    if not filepath.is_file():
        logger.error("Workflow file not found at: %s", filepath)
        return None

    try:
        # Ensure correct encoding and handle potential BOM
        with open(filepath, encoding='utf-8-sig') as f:
            # Read the entire content first (though for large files consider streaming)
            content = f.read()
            # Now parse the content using json.loads
            workflow = json.loads(content)

            if not isinstance(workflow, dict):
                logger.error(
                    "Error: Expected JSON object at the top level in %s, got %s.",
                    filepath, type(workflow).__name__
                )
                return None

            logger.info(
                "Successfully loaded workflow '%s' from %s",
                workflow.get('name', 'Unnamed'), filepath
            )
            return workflow
    except json.JSONDecodeError as e:
        logger.error("Error: Invalid JSON in %s. Details: %s", filepath, e)
        return None
    except FileNotFoundError: # Should be caught by is_file, but good practice
         logger.error("Workflow file not found at: %s", filepath)
         return None
    except Exception as e: # Catch other potential errors like permission issues
        logger.exception("Unexpected error loading workflow %s: %s", filepath, e)
        return None
