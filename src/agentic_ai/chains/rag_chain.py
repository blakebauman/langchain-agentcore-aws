"""Simple RAG chain for knowledge base question answering.

This demonstrates a non-agent pattern — a straightforward retrieval-augmented
generation chain. Use this when you don't need tool calling or multi-step
reasoning, just Q&A over a knowledge base.

Usage:
    from agentic_ai.chains.rag_chain import create_rag_chain

    chain = create_rag_chain()
    answer = chain.invoke("What is our refund policy?")
"""

import boto3
from langchain_aws import ChatBedrockConverse
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableLambda

from agentic_ai.config import settings


def _retrieve_from_kb(query: str) -> str:
    """Retrieve relevant documents from Bedrock Knowledge Base."""
    if not settings.knowledge_base_id:
        return "No knowledge base configured."

    client = boto3.client("bedrock-agent-runtime", region_name=settings.aws_region)
    response = client.retrieve(
        knowledgeBaseId=settings.knowledge_base_id,
        retrievalQuery={"text": query},
        retrievalConfiguration={"vectorSearchConfiguration": {"numberOfResults": 5}},
    )

    results = response.get("retrievalResults", [])
    return "\n\n".join(r.get("content", {}).get("text", "") for r in results)


def create_rag_chain(
    model_id: str | None = None,
) -> RunnableLambda:
    """Create a RAG chain that retrieves from the knowledge base and answers.

    Args:
        model_id: Bedrock model ID. Defaults to settings.bedrock_model_id.
    """
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "Answer the user's question based on the following context. "
                "If the context doesn't contain relevant information, say so.\n\n"
                "Context:\n{context}",
            ),
            ("human", "{question}"),
        ]
    )

    llm = ChatBedrockConverse(
        model=model_id or settings.bedrock_model_id,
        region_name=settings.aws_region,
        temperature=0,
    )

    chain = (
        {
            "context": RunnableLambda(_retrieve_from_kb),
            "question": RunnableLambda(lambda x: x),
        }
        | prompt
        | llm
        | StrOutputParser()
    )

    return chain
