"""Bedrock Knowledge Base retrieval tool.

Requires a deployed knowledge base — use after `make infra-apply`.
"""

import boto3
from langchain_core.tools import tool

from agentic_ai.config import settings


@tool
def query_knowledge_base(query: str) -> str:
    """Search the knowledge base for relevant information.

    Args:
        query: Natural language question to search for.
    """
    if not settings.knowledge_base_id:
        return "Error: KNOWLEDGE_BASE_ID is not configured. Deploy infrastructure first."

    client = boto3.client("bedrock-agent-runtime", region_name=settings.aws_region)
    response = client.retrieve(
        knowledgeBaseId=settings.knowledge_base_id,
        retrievalQuery={"text": query},
        retrievalConfiguration={"vectorSearchConfiguration": {"numberOfResults": 5}},
    )

    results = response.get("retrievalResults", [])
    if not results:
        return f"No knowledge base results found for: '{query}'"

    formatted = []
    for i, result in enumerate(results, 1):
        text = result.get("content", {}).get("text", "")
        score = result.get("score", 0)
        formatted.append(f"[{i}] (score: {score:.3f}) {text}")

    return "\n\n".join(formatted)
