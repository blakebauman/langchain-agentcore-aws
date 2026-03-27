---
name: aws-bedrock
description: Look up AWS Bedrock model invocation, Knowledge Bases, Agents, Guardrails, and LangChain integration
user-invocable: true
allowed-tools: WebSearch, WebFetch(domain:docs.aws.amazon.com), WebFetch(domain:aws.amazon.com), WebFetch(domain:python.langchain.com), WebFetch(domain:langchain-ai.github.io), WebFetch(domain:pypi.org), WebFetch(domain:github.com), Read, Grep, Glob
---

# AWS Bedrock Guidance

Look up AWS Bedrock documentation for model invocation, Knowledge Bases, Agents, Guardrails, and LangChain integration patterns.

## Arguments

Topic or question: $ARGUMENTS

## Behavior

1. Search Bedrock documentation using WebSearch and fetch from docs.aws.amazon.com
2. Read project code to understand current Bedrock usage:
   - `src/agentic_ai/agents/langgraph_agent.py` for model invocation patterns
   - `src/agentic_ai/tools/knowledge_base.py` for Knowledge Base integration
   - `src/agentic_ai/config.py` for model ID and region settings
3. IMPORTANT: This project uses `ChatBedrockConverse` from `langchain_aws`, NOT the legacy `ChatBedrock`. Always recommend the Converse API pattern.
4. For model questions, include the full model ID format (e.g., `us.anthropic.claude-sonnet-4-20250514-v1:0`) and note region availability
5. For Knowledge Base questions, cover both the Terraform setup (`infra/`) and the retrieval tool (`tools/knowledge_base.py`)
6. For LangChain integration, fetch docs from python.langchain.com and reference `langchain-aws` (not `langchain-community`)
7. Cite specific documentation URLs for every recommendation
