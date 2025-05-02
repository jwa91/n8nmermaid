# src/n8nmermaid/core/orchestrator_v2.py
"""
Central orchestrator V2 for n8nmermaid analysis and generation tasks.

Connects V2 analysis and V2 generation based on user requests specified
in V2 models.
"""

import logging

from n8nmermaid.core.analyzer_v2 import WorkflowAnalysisV2, WorkflowAnalyzerV2
from n8nmermaid.core.generators.mermaid_v2 import MermaidGeneratorV2
from n8nmermaid.core.generators.reports_v2 import (
    ReportGeneratorError,
    ReportGeneratorV2,
)
from n8nmermaid.models_v2.request_v2_models import (
    AnalysisRequestV2,
    ReportGenerationParamsV2,
    RequestCommand,
)

logger = logging.getLogger(__name__)


class OrchestratorErrorV2(Exception):
    """Custom exception for failures within the V2 orchestration process."""
    pass


class OrchestratorV2:
    """
    Coordinates the V2 workflow analysis and output generation process.

    Acts as the central component connecting the V2 analyzer and V2 generators
    based on the details provided in the AnalysisRequestV2. Expects workflow
    data within the request.
    """

    def __init__(self, request: AnalysisRequestV2):
        """
        Initializes the OrchestratorV2.

        Args:
            request: The AnalysisRequestV2 containing workflow data (as dict)
                    and command parameters. Uses V2 parameter models.

        Raises:
            TypeError: If request is not an AnalysisRequestV2 object.
        """
        if not isinstance(request, AnalysisRequestV2):
            raise TypeError("OrchestratorV2 requires an AnalysisRequestV2 object.")

        self.request = request
        logger.debug(
            "OrchestratorV2 initialized with command: %s", self.request.command
        )

    def process_request(self) -> str | dict[str, str]:
        """
        Executes the V2 analysis and generation steps defined in the request.

        Returns:
            For 'generate_mermaid', a dictionary where keys are diagram
            identifiers ("main", cluster root names) and values are Mermaid
            diagram strings.
            For 'generate_report', a string containing the report content or
            serialized V2 analysis data.

        Raises:
            OrchestratorErrorV2: If a critical step fails. # <-- Docstring bijgewerkt
        """
        logger.info("Processing V2 request command: %s", self.request.command)

        analysis_result: WorkflowAnalysisV2
        try:
            logger.debug("Instantiating WorkflowAnalyzerV2...")
            analyzer = WorkflowAnalyzerV2(workflow_data=self.request.workflow_data)
            logger.debug("Running V2 workflow analysis...")
            analysis_result = analyzer.analyze()

            if analysis_result.analysis_warnings:
                logger.warning(
                    "V2 Analysis completed with %d warnings:",
                    len(analysis_result.analysis_warnings),
                )
                for warning in analysis_result.analysis_warnings:
                    logger.warning("  - %s", warning)

        except Exception as e:
            logger.exception("Critical error during V2 workflow analysis phase.")
            raise OrchestratorErrorV2(f"V2 Workflow analysis failed: {e}") from e

        if not analysis_result or not analysis_result.nodes:
            logger.error("V2 Analysis yielded no processable nodes. Cannot proceed.")
            raise OrchestratorErrorV2(
                "V2 Workflow analysis yielded no processable nodes."
            )

        command: RequestCommand = self.request.command
        output: str | dict[str, str]

        try:
            logger.debug("Selecting V2 generator for command '%s'...", command)
            match command:
                case "generate_mermaid":
                    logger.debug("Instantiating MermaidGeneratorV2...")
                    generator = MermaidGeneratorV2(
                        analysis=analysis_result, params=self.request.mermaid_params
                    )
                    logger.debug("Generating V2 Mermaid output...")
                    output = generator.generate()

                case "generate_report":
                    report_params: ReportGenerationParamsV2 | None = (
                        self.request.report_params
                    )
                    if not report_params:
                        logger.error(
                            "Command 'generate_report' requires 'report_params'."
                        )
                        raise OrchestratorErrorV2(
                            "Missing report parameters for 'generate_report'."
                        )

                    requested_types = report_params.report_types
                    output_format = report_params.output_format

                    logger.info(
                        "Processing report types: %s with format: %s",
                        ", ".join(requested_types),
                        output_format,
                    )

                    if "analysis_json" in requested_types:
                        if len(requested_types) > 1:
                            logger.error(
                                "Report type 'analysis_json' cannot be combined."
                            )
                            raise OrchestratorErrorV2(
                                "Report type 'analysis_json' cannot be combined."
                            )
                        logger.debug(
                            "Serializing WorkflowAnalysisV2 object to JSON..."
                        )
                        output = analysis_result.model_dump_json(indent=2)
                    else:
                        try:
                            logger.debug("Instantiating ReportGeneratorV2...")
                            report_generator = ReportGeneratorV2(
                                analysis=analysis_result, params=report_params
                            )
                            logger.debug(
                                "Generating combined V2 report string..."
                            )
                            output = report_generator.generate()
                        except ReportGeneratorError as rge:
                            logger.error("ReportGeneratorV2 failed: %s", rge)
                            raise OrchestratorErrorV2(str(rge)) from rge
                        except Exception as e:
                            logger.exception(
                                "Unexpected error during V2 report generation."
                            )
                            raise OrchestratorErrorV2(
                                "Unexpected error generating V2 combined report."
                            ) from e

                case _:
                    logger.error("Unsupported command received: %s", command)
                    raise OrchestratorErrorV2(f"Unsupported command: {command}")

        except Exception as e:
            if isinstance(e, OrchestratorErrorV2):
                raise e
            else:
                logger.exception(
                    "Critical error during V2 output generation for command '%s'.",
                    command,
                )
                raise OrchestratorErrorV2(
                    f"Output generation failed for command '{command}': {e}"
                ) from e

        logger.info("V2 Request processing finished successfully.")
        return output


def process_v2(request: AnalysisRequestV2) -> str | dict[str, str]:
    """
    Functional interface to run the V2 orchestration process.

    Delegates processing to the OrchestratorV2 class.

    Args:
        request: The AnalysisRequestV2 object containing V2 workflow data
                 and parameters.

    Returns:
        The generated output (Mermaid diagram dict, report string, etc.).

    Raises:
        OrchestratorErrorV2: If the orchestration process fails. # <-- Docstring bijgewerkt
        TypeError: If input types are incorrect.
    """
    try:
        orchestrator = OrchestratorV2(request=request)
        return orchestrator.process_request()
    except (TypeError, OrchestratorErrorV2) as e:
        logger.error(
            "Failed to process V2 request via functional interface: %s", e
        )
        raise