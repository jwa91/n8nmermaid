# src/n8nmermaid/core/generators/mermaid_v2/generator.py
"""Contains the MermaidGeneratorV2 class for creating V2 Mermaid diagrams."""

import logging

from n8nmermaid.core.analyzer_v2.models import (
    AnalyzedNodeV2,
    NodeGroupType,
    WorkflowAnalysisV2,
)
from n8nmermaid.models_v2.request_v2_models import MermaidGenerationParamsV2

from .connection_definitions import (
    generate_node_connections,
    generate_start_end_connections,
)
from .constants import N8N_CONNECTION_TYPE_MAIN
from .helpers import (
    format_node_definition,
    format_node_label,
    get_connection_label_parts,
    get_mermaid_shape,
    sanitize_filename,
)
from .node_definitions import define_nodes_and_subgraphs, define_start_end_symbols

logger = logging.getLogger(__name__)


class MermaidGeneratorV2:
    """
    Generates Mermaid flowchart syntax from a WorkflowAnalysisV2 object.

    Produces a dictionary containing the main diagram and potentially separate
    diagrams for individual clusters, based on generation parameters.
    """

    def __init__(
        self,
        analysis: WorkflowAnalysisV2,
        params: MermaidGenerationParamsV2,
    ):
        """
        Initializes the V2 generator.

        Args:
            analysis: The WorkflowAnalysisV2 object.
            params: The MermaidGenerationParamsV2 specifying diagram options.
        """
        self.analysis = analysis
        self.params = params
        self.handled_node_ids_main: set[str] = set()
        logger.debug(
            "MermaidGeneratorV2 initialized. Main dir: %s, Subgraph dir: %s, "
            "Subgraph mode: %s",
            self.params.direction,
            self.params.subgraph_direction,
            self.params.subgraph_display_mode,
        )

    def generate(self) -> dict[str, str]:
        """
        Assembles the final Mermaid flowchart output dictionary (V2).

        Returns:
            A dictionary where keys are diagram identifiers ("main", sanitized
            cluster root names) and values are the corresponding Mermaid diagram
            strings.
        """
        logger.info(
            "Generating V2 Mermaid output(s) for mode: %s",
            self.params.subgraph_display_mode,
        )
        result: dict[str, str] = {}

        if not self.analysis or not self.analysis.nodes:
            logger.warning("V2 Workflow analysis contains no processable nodes.")
            result["main"] = (
                f"flowchart {self.params.direction}\n"
                f"    %% No processable nodes found\n"
            )
            return result

        logger.debug("Generating V2 main diagram content...")
        main_diagram_string = self._generate_main_diagram()
        result["main"] = main_diagram_string
        logger.info("V2 Main diagram generation complete.")

        if self.params.subgraph_display_mode == "separate_clusters":
            logger.debug("Generating separate diagrams for V2 clusters...")
            cluster_roots = [
                node
                for node in self.analysis.nodes.values()
                if node.classification.group_type == NodeGroupType.CLUSTER_ROOT
            ]
            if cluster_roots:
                logger.info(
                    "Found %d V2 cluster roots to generate diagrams for.",
                    len(cluster_roots),
                )
                used_keys: dict[str, int] = {}
                for root_node in cluster_roots:
                    base_key = sanitize_filename(root_node.name)
                    final_key = base_key
                    count = used_keys.get(base_key, 0)
                    if count > 0:
                        final_key = f"{base_key}_{count}"
                    used_keys[base_key] = count + 1

                    cluster_diagram = self._generate_single_cluster_diagram(
                        root_node
                    )
                    if cluster_diagram:
                        result[final_key] = cluster_diagram
                        logger.debug(
                            "Generated separate diagram for V2 cluster %s (key: %s)",
                            root_node.id,
                            final_key,
                        )
                    else:
                        logger.warning(
                            "Failed to generate separate diagram for V2 cluster %s",
                            root_node.id,
                        )
            else:
                logger.info(
                    "No V2 cluster roots found, no separate diagrams needed."
                )

        logger.info(
            "V2 Mermaid generation complete. Returning %d diagram(s).",
            len(result),
        )
        return result

    def _generate_main_diagram(self) -> str:
        """
        Generates the primary Mermaid diagram string based on V2 analysis.

        Returns:
            A string containing the Mermaid syntax for the main diagram.
        """
        logger.debug("Assembling V2 main Mermaid string...")
        (
            node_defs,
            trigger_ids,
            end_node_ids,
            self.handled_node_ids_main,
        ) = define_nodes_and_subgraphs(self.analysis, self.params)
        logger.info(
            "V2 Main diagram: Generated %d node/subgraph lines. "
            "Handled elements: %d",
            len(node_defs),
            len(self.handled_node_ids_main),
        )

        symbol_defs = define_start_end_symbols(trigger_ids, end_node_ids)

        connection_defs = generate_node_connections(
            self.analysis, self.params, self.handled_node_ids_main
        )
        start_end_conns = generate_start_end_connections(
            self.analysis, self.params, trigger_ids, end_node_ids
        )

        output_lines = [f"flowchart {self.params.direction}"]
        all_node_defs = node_defs + symbol_defs
        if all_node_defs:
            output_lines.append("")
            output_lines.append("%% Nodes, Subgraphs & Symbols (Main V2)")
            output_lines.extend(
                [
                    f"    {line}" if line != "end" and line else line
                    for line in all_node_defs
                ]
            )

        all_connections = sorted(set(connection_defs + start_end_conns))
        if all_connections:
            output_lines.append("")
            output_lines.append("%% Connections (Main V2)")
            output_lines.extend(
                [f"    {conn.strip()}" for conn in all_connections]
            )
        else:
            output_lines.append("")
            output_lines.append("    %% No connections generated (Main V2)")

        return "\n".join(output_lines).strip() + "\n"

    def _generate_single_cluster_diagram(
        self, root_node: AnalyzedNodeV2
    ) -> str | None:
        """
        Generates a self-contained Mermaid diagram for a single V2 cluster.

        Args:
            root_node: The AnalyzedNodeV2 object representing the cluster root.

        Returns:
            A string containing the Mermaid syntax for the cluster, or None.
        """
        logger.debug(
            "Generating diagram for V2 cluster root: %s", root_node.id
        )
        cluster_node_ids = {
            n.id
            for n in self.analysis.nodes.values()
            if n.cluster.cluster_root_id == root_node.id
        }

        if not cluster_node_ids:
            logger.warning(
                "V2 Cluster root %s has no associated nodes.", root_node.id
            )
            return None

        node_defs: list[str] = []
        for node_id in sorted(cluster_node_ids):
            node = self.analysis.nodes[node_id]
            node_label = format_node_label(node, self.params)
            shape = get_mermaid_shape(node)
            node_defs.append(
                format_node_definition(node_id, node_label, shape)
            )

        connection_defs: set[str] = set()
        for source_id in cluster_node_ids:
            source_node = self.analysis.nodes[source_id]

            for connection in source_node.connectivity.outgoing_connections:
                target_id = connection.target_node_id
                if target_id in cluster_node_ids:
                    arrow = (
                        "-->"
                        if connection.connection_type
                        == N8N_CONNECTION_TYPE_MAIN
                        else "-.->"
                    )
                    label_parts = get_connection_label_parts(
                        source_node, connection
                    )
                    label_str = (
                        f'|"{" ".join(label_parts)}"|' if label_parts else ""
                    )
                    link = f"{source_id} {arrow}{label_str} {target_id}"
                    if link not in connection_defs:
                        connection_defs.add(link)
                        logger.debug(
                            "Cluster %s: Added internal link (%s): %s",
                            root_node.id,
                            connection.connection_type,
                            link,
                        )

        output_lines = [f"flowchart {self.params.subgraph_direction}"]

        if node_defs:
            output_lines.append("")
            output_lines.append(
                f"%% Nodes (Cluster V2: {root_node.name} / {root_node.id})"
            )
            output_lines.extend([f"    {line}" for line in node_defs])

        if connection_defs:
            output_lines.append("")
            output_lines.append(
                f"%% Connections (Cluster V2: {root_node.name} / {root_node.id})"
            )
            output_lines.extend(
                [f"    {conn.strip()}" for conn in sorted(connection_defs)]
            )
        else:
            output_lines.append("")
            output_lines.append(
                f"    %% No internal connections found "
                f"(Cluster V2: {root_node.name} / {root_node.id})"
            )

        return "\n".join(output_lines).strip() + "\n"
