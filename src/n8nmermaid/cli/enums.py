# src/n8nmermaid/cli/enums.py
"""Defines Enumerations used for Typer CLI choices."""

from enum import StrEnum


class CliMermaidDirection(StrEnum):
    """CLI choices for Mermaid diagram direction."""

    TD = "TD"
    LR = "LR"
    TB = "TB"
    RL = "RL"
    BT = "BT"


class CliSubgraphDisplayMode(StrEnum):
    """CLI choices for how to display subgraphs/clusters."""

    SUBGRAPH = "subgraph"
    SIMPLE_NODE = "simple_node"
    SEPARATE_CLUSTERS = "separate_clusters"


class CliReportType(StrEnum):
    """CLI choices for report types."""

    STATS = "stats"
    CREDENTIALS = "credentials"
    AGENTS = "agents"
    ANALYSIS_JSON = "analysis_json"
    NODE_PARAMETERS = "node_parameters"


class CliReportFormat(StrEnum):
    """CLI choices for report output formats."""

    TEXT = "text"
    MARKDOWN = "markdown"
    JSON = "json"
