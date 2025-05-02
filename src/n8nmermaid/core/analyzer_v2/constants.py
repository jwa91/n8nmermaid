# filename: src/n8nmermaid/core/analyzer_v2/constants.py
"""Constants used specifically within the V2 analyzer."""

from typing import Literal

N8nConnectionLiteral = Literal[
    "ai_agent",
    "ai_chain",
    "ai_document",
    "ai_embedding",
    "ai_languageModel",
    "ai_memory",
    "ai_outputParser",
    "ai_retriever",
    "ai_textSplitter",
    "ai_tool",
    "ai_vectorStore",
    "main",
]

# Node type for Sticky Notes
STICKY_NODE_TYPE = "n8n-nodes-base.stickyNote"

# Parameter Categories for Phase 6
PARAM_CATEGORIES: dict[str, list[str]] = {
    "database": ["query", "sql", "table", "database", "postgres", "mysql", "db"],
    "ai": [
        "model",
        "prompt",
        "temperature",
        "llm",
        "agent",
        "embedding",
        "vector",
        "chat",
        "openai",
        "langchain",
        "toolDescription",  # Often AI-related
        "systemMessage",
    ],
    "file": ["path", "filename", "directory", "file", "folder", "read", "write"],
    "http": ["url", "request", "http", "api", "endpoint", "header", "body"],
    "scheduling": ["schedule", "cron", "interval", "datetime", "date", "time"],
    "data_manipulation": ["set", "map", "filter", "aggregate", "extract", "merge"],
    "control_flow": ["if", "switch", "router", "loop", "wait"],
    "credentials": ["credential", "auth", "token", "key", "secret"],
}
