# src/n8nmermaid/core/generators/reports_v2/generator.py
"""
Defines the main ReportGeneratorV2 class for V2 analysis results.

This module orchestrates the process of generating different types of reports
from the data produced by the V2 workflow analyzer.
"""

import logging
from collections.abc import Callable

from pydantic import BaseModel

from n8nmermaid.core.analyzer_v2.models import WorkflowAnalysisV2
from n8nmermaid.models_v2.request_v2_models import (
    ReportGenerationParamsV2,
    ReportType,
)

from .formatters import format_report
from .report_agents import generate_agents_data_v2
from .report_credentials import generate_credentials_data_v2
from .report_node_parameters import generate_node_parameters_data_v2
from .report_stats import generate_stats_data_v2

logger = logging.getLogger(__name__)


class ReportGeneratorError(Exception):
    """Custom exception for V2 report generation failures."""

    pass


ReportDataGeneratorV2 = Callable[[WorkflowAnalysisV2], BaseModel]


_REPORT_GENERATORS_V2: dict[ReportType, ReportDataGeneratorV2] = {
    "stats": generate_stats_data_v2,
    "credentials": generate_credentials_data_v2,
    "agents": generate_agents_data_v2,
    "node_parameters": generate_node_parameters_data_v2,
}


class ReportGeneratorV2:
    """
    Orchestrates the generation of specific reports based on V2 analysis results.
    """

    def __init__(
        self,
        analysis: WorkflowAnalysisV2,
        params: ReportGenerationParamsV2,
    ):
        """
        Initializes the ReportGeneratorV2.

        Args:
            analysis: The completed WorkflowAnalysisV2 object.
            params: The ReportGenerationParamsV2 specifying report type(s) and format.
        """
        self.analysis = analysis
        self.params = params
        logger.debug(
            "ReportGeneratorV2 initialized for report types: %s",
            self.params.report_types,
        )

    def generate(self) -> str:
        """
        Generates the requested combined report string from V2 analysis.

        Iterates through the requested report types, calls the appropriate
        data generator and formatter, and combines the results.

        Returns:
            A string containing the formatted, combined report(s).

        Raises:
            ReportGeneratorError: If errors occur during generation/formatting.
        """
        output_format = self.params.output_format
        all_report_strings: list[str] = []
        requested_types = self.params.report_types

        report_separator = "\n\n---\n\n"

        logger.info(
            "Generating V2 combined report for types: %s with format: %s",
            ", ".join(requested_types),
            output_format,
        )

        for report_type in requested_types:
            if report_type == "analysis_json":
                logger.debug("Skipping 'analysis_json' report type in generator.")
                continue

            logger.debug("Processing report type '%s'...", report_type)
            generator_func = _REPORT_GENERATORS_V2.get(report_type)

            if generator_func is None:
                logger.error(
                    "No V2 generator function registered for report type: %s",
                    report_type,
                )
                raise ReportGeneratorError(
                    f"Unsupported or unregistered V2 report type: {report_type}"
                )

            try:
                logger.debug("Calling V2 data generator for '%s'...", report_type)
                report_data: BaseModel = generator_func(self.analysis)

                logger.debug("Formatting V2 report data for '%s'...", report_type)
                formatted_report_part = format_report(
                    report_type, report_data, output_format
                )
                all_report_strings.append(formatted_report_part)

            except Exception as e:
                logger.exception(
                    "Error during V2 generation pipeline for type '%s'", report_type
                )
                raise ReportGeneratorError(
                    f"Failed to generate V2 report part '{report_type}': {e}"
                ) from e

        if not all_report_strings:
            logger.warning(
                "No V2 report parts were generated for requested types."
            )
            return "No report content generated."

        return report_separator.join(all_report_strings)
