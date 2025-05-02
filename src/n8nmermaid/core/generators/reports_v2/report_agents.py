# src/n8nmermaid/core/generators/reports_v2/report_agents.py
"""Generates structured data for the V2 AI Agents report."""

import logging

from n8nmermaid.core.analyzer_v2.models import (
    AnalyzedNodeV2,
    NodeGroupType,
    WorkflowAnalysisV2,
)

from .models import AgentDetail, AgentsReportData, ModelCredentialInfo

logger = logging.getLogger(__name__)


def _find_connected_llm_details(
    agent_node: AnalyzedNodeV2, analysis_nodes: dict[str, AnalyzedNodeV2]
) -> tuple[str | None, list[ModelCredentialInfo] | None]:
    """
    Finds connected LLM node and extracts model identifier and credentials.

    Searches incoming connections for 'ai_languageModel' type. Extracts model
    details and credentials from the first connected LLM node found.

    Args:
        agent_node: The agent node being analyzed.
        analysis_nodes: Dictionary of all nodes in the analysis.

    Returns:
        A tuple containing the model identifier (str or None) and a list of
        ModelCredentialInfo (or None).
    """
    model_name: str | None = None
    model_creds: list[ModelCredentialInfo] | None = None
    llm_node_id: str | None = None
    connected_llm_ids: list[str] = []

    for conn in agent_node.connectivity.incoming_connections:
        if conn.connection_type == "ai_languageModel":
            connected_llm_ids.append(conn.source_node_id)

    if not connected_llm_ids:
        logger.debug("Agent '%s' has no ai_languageModel input.", agent_node.name)
        return None, None

    llm_node_id = connected_llm_ids[0]
    llm_node = analysis_nodes.get(llm_node_id)

    if not llm_node:
        logger.warning(
            "Agent '%s' connected to unknown LLM node ID '%s'",
            agent_node.name,
            llm_node_id,
        )
        return None, None

    model_name = (
        llm_node.extracted_parameters.get("model")
        or llm_node.extracted_parameters.get("modelId")
        or llm_node.extracted_parameters.get("model_identifier")
    )

    if llm_node.credentials.has_credentials:
        model_creds = []
        for cred_type, details in llm_node.credentials.details.items():
            model_creds.append(
                ModelCredentialInfo(type=cred_type, name=details.name, id=details.id)
            )

    logger.debug(
        "Found model '%s' (Creds: %s) for agent '%s' from node '%s'",
        model_name,
        "Yes" if model_creds else "No",
        agent_node.name,
        llm_node.name,
    )
    if len(connected_llm_ids) > 1:
        logger.warning(
            "Agent '%s' has multiple LLMs connected. Reporting details "
            "from first found ('%s').",
            agent_node.name,
            llm_node_id,
        )

    return model_name, model_creds


def _find_connected_tools(
    agent_node: AnalyzedNodeV2, analysis_nodes: dict[str, AnalyzedNodeV2]
) -> list[str]:
    """
    Finds tools connected to the agent node via 'ai_tool' connections.

    Checks both incoming and outgoing connections of type 'ai_tool'.

    Args:
        agent_node: The agent node being analyzed.
        analysis_nodes: Dictionary of all nodes in the analysis.

    Returns:
        A sorted list of strings describing the connected tools (Name (Type)).
    """
    tools_list: list[str] = []
    connected_tool_ids: list[str] = []

    for conn in agent_node.connectivity.incoming_connections:
        if conn.connection_type == "ai_tool":
            connected_tool_ids.append(conn.source_node_id)
    for conn in agent_node.connectivity.outgoing_connections:
        if conn.connection_type == "ai_tool":
            connected_tool_ids.append(conn.target_node_id)

    unique_tool_ids = set(connected_tool_ids)

    for tool_id in unique_tool_ids:
        tool_node = analysis_nodes.get(tool_id)
        if tool_node:
            tools_list.append(f"{tool_node.name} ({tool_node.type})")
        else:
            tools_list.append(f"Unknown Tool (ID: {tool_id})")
            logger.warning(
                "Agent '%s' connected to unknown tool node ID '%s'",
                agent_node.name,
                tool_id,
            )
    return sorted(tools_list)


def _find_system_message(agent_node: AnalyzedNodeV2) -> str | None:
    """
    Finds the system message from the agent's extracted parameters.

    Checks common parameter keys used for system messages.

    Args:
        agent_node: The agent node being analyzed.

    Returns:
        The system message string, or None if not found.
    """
    possible_keys = ["options.systemMessage", "systemMessage", "system_message"]
    for key in possible_keys:
        if key in agent_node.extracted_parameters:
            return str(agent_node.extracted_parameters[key])
    return None


def generate_agents_data_v2(analysis: WorkflowAnalysisV2) -> AgentsReportData:
    """
    Generates the structured data for the Agents report from V2 analysis.

    Identifies agent nodes (Cluster Roots) and extracts details like connected
    LLM, model credentials, system message, and connected tools.

    Args:
        analysis: The completed WorkflowAnalysisV2 object.

    Returns:
        An AgentsReportData object listing the identified agents and their details.
    """
    agents_list: list[AgentDetail] = []
    if not analysis or not analysis.nodes:
        logger.warning("V2 Agents report: No nodes found in analysis.")
        return AgentsReportData(agents=agents_list)

    for node in analysis.nodes.values():
        if node.classification.group_type == NodeGroupType.CLUSTER_ROOT:
            agent_model, model_creds = _find_connected_llm_details(
                node, analysis.nodes
            )
            tools_list = _find_connected_tools(node, analysis.nodes)
            system_message = _find_system_message(node)

            agent_info = AgentDetail(
                node_id=node.id,
                node_name=node.name,
                model=agent_model,
                model_credentials=model_creds,
                system_message=system_message,
                tools_used=tools_list,
            )
            agents_list.append(agent_info)

    logger.info("Generated V2 agents data: Found %d agents.", len(agents_list))
    return AgentsReportData(agents=agents_list)
