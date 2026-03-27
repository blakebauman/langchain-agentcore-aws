"""Web search tool stub.

Replace this implementation with a real search provider (Tavily, SerpAPI, etc.)
when ready. This stub exists so the tool interface is established and agents
can be tested without external API dependencies.
"""

from langchain_core.tools import tool


@tool
def web_search(query: str) -> str:
    """Search the web for information.

    Args:
        query: The search query string.
    """
    # TODO: Replace with real search provider integration
    # Example with Tavily:
    #   from langchain_community.tools.tavily_search import TavilySearchResults
    #   search = TavilySearchResults(max_results=3)
    #   return search.invoke(query)
    return (
        f"[Web search stub] No results for: '{query}'. "
        "Replace this stub with a real search provider in src/agentic_ai/tools/web_search.py"
    )
