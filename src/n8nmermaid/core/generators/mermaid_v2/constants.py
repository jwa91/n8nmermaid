# src/n8nmermaid/core/generators/mermaid_v2/constants.py
"""Constants and mappings for the V2 Mermaid generator."""


from n8nmermaid.core.analyzer_v2.constants import N8nConnectionLiteral
from n8nmermaid.core.analyzer_v2.models import NodeGroupType

MermaidShapeName = str

NODE_GROUP_TO_SHAPE: dict[NodeGroupType, MermaidShapeName] = {
    NodeGroupType.TRIGGER: "stadium",
    NodeGroupType.ACTION: "rect",
    NodeGroupType.ROUTER: "diamond",
    NodeGroupType.CLUSTER_ROOT: "subroutine",
    NodeGroupType.CLUSTER_SUB_ROOT: "hexagon",
    NodeGroupType.CLUSTER_SUB: "trapezoid",
    NodeGroupType.STICKY: "rect",
    NodeGroupType.UNKNOWN: "rect",
}

SHAPE_START: MermaidShapeName = "circle"
SHAPE_STOP: MermaidShapeName = "doublecircle"

START_SYMBOL_SUFFIX = "_startsymbol"
END_SYMBOL_SUFFIX = "_endsymbol"

N8N_CONNECTION_TYPE_MAIN: N8nConnectionLiteral = "main"
