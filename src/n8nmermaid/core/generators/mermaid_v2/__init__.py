# src/n8nmermaid/core/generators/mermaid_v2/__init__.py
"""
V2 Mermaid diagram generation module.
"""

from n8nmermaid.core.analyzer_v2.models import WorkflowAnalysisV2
from n8nmermaid.models_v2.request_v2_models import MermaidGenerationParamsV2

from .generator import MermaidGeneratorV2


def generate_mermaid_v2(
    analysis: WorkflowAnalysisV2, params: MermaidGenerationParamsV2
) -> dict[str, str]:
    """
    Generates Mermaid diagrams from V2 workflow analysis results.

    Args:
        analysis: The WorkflowAnalysisV2 object containing analyzed data.
        params: The MermaidGenerationParamsV2 specifying diagram options.

    Returns:
        A dictionary where keys are diagram identifiers ("main", cluster names)
        and values are Mermaid diagram strings.
    """
    generator = MermaidGeneratorV2(analysis=analysis, params=params)
    return generator.generate()


__all__ = [
    "MermaidGeneratorV2",
    "generate_mermaid_v2",
]
