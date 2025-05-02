# filename: src/n8nmermaid/core/analyzer_v2/__init__.py
"""
Workflow analysis module (V2). Processes raw n8n JSON into structured analysis results.
"""

import logging
from typing import Any

from .models import WorkflowAnalysisV2
from .phase_1_initial_parse import parse_initial_nodes
from .phase_2_connection_mapping import map_connections
from .phase_3_cluster_analysis import analyze_clusters
from .phase_4_node_classification import classify_nodes
from .phase_5_parameter_extraction import extract_parameters
from .phase_6_parameter_categorization import categorize_parameters

logger = logging.getLogger(__name__)


class WorkflowAnalyzerV2:
    """
    Orchestrates the V2 analysis of n8n workflow data.

    Takes raw workflow JSON (as dict) and runs analysis phases sequentially
    to produce a WorkflowAnalysisV2 object.
    """

    def __init__(self, workflow_data: dict[str, Any]):
        """
        Initializes the V2 analyzer.

        Args:
            workflow_data: The raw n8n workflow structure as a dictionary.
        """
        if not isinstance(workflow_data, dict):
            raise TypeError("WorkflowAnalyzerV2 requires workflow_data as a dict.")
        self.raw_workflow_data = workflow_data
        self.analysis_result = WorkflowAnalysisV2()

    def analyze(self) -> WorkflowAnalysisV2:
        """
        Performs the full V2 workflow analysis sequence.

        Runs phases for initial parsing, connection mapping, cluster analysis,
        node classification, parameter extraction, and parameter categorization.

        Returns:
            The completed WorkflowAnalysisV2 object.
        """
        logger.info("Starting V2 workflow analysis...")
        all_warnings: list[str] = []

        logger.info("Running Phase 1: Initial Node Parsing...")
        name_to_id, phase1_warnings = parse_initial_nodes(
            self.raw_workflow_data, self.analysis_result
        )
        all_warnings.extend(phase1_warnings)

        if not self.analysis_result.nodes:
            logger.error("Phase 1 resulted in no valid nodes. Aborting analysis.")
            self.analysis_result.analysis_warnings = all_warnings
            return self.analysis_result

        nodes_dict = self.analysis_result.nodes
        raw_connections = self.raw_workflow_data.get("connections", {})

        logger.info("Running Phase 2: Detailed Connection Mapping...")
        phase2_warnings = map_connections(nodes_dict, name_to_id, raw_connections)
        all_warnings.extend(phase2_warnings)

        logger.info("Running Phase 3: Cluster Analysis...")
        phase3_warnings = analyze_clusters(nodes_dict)
        all_warnings.extend(phase3_warnings)

        logger.info("Running Phase 4: Node Classification...")
        phase4_warnings = classify_nodes(nodes_dict)
        all_warnings.extend(phase4_warnings)

        logger.info("Running Phase 5: Generic Parameter Extraction...")
        phase5_warnings = extract_parameters(nodes_dict)
        all_warnings.extend(phase5_warnings)

        logger.info("Running Phase 6: Parameter Categorization...")
        phase6_warnings = categorize_parameters(nodes_dict)
        all_warnings.extend(phase6_warnings)

        self.analysis_result.analysis_warnings = all_warnings
        logger.info(
            "V2 Workflow analysis complete. Found %d warnings.", len(all_warnings)
        )
        if all_warnings:
            logger.warning("Analysis completed with warnings:")
            for warning in all_warnings:
                logger.warning("  - %s", warning)

        return self.analysis_result


def analyze_workflow_v2(workflow_data: dict[str, Any]) -> WorkflowAnalysisV2:
    """
    Functional entry point for V2 workflow analysis.

    Instantiates and runs the WorkflowAnalyzerV2.

    Args:
        workflow_data: The raw n8n workflow structure as a dictionary.

    Returns:
        The completed WorkflowAnalysisV2 object.

    Raises:
        TypeError: If workflow_data is not a dictionary.
        Exception: For any unexpected errors during analysis.
    """
    try:
        analyzer = WorkflowAnalyzerV2(workflow_data=workflow_data)
        return analyzer.analyze()
    except Exception as e:
        logger.exception("Critical error during V2 workflow analysis.")
        raise e
