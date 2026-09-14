"""FastMCP research backend used by the Research Agent (via MCPServerAdapter).

This is the CrewAI-side equivalent of the n8n "MCP Server" workflow (Step
2.9 in the README): a standalone MCP server exposing a web-search tool that
the Research Agent connects to over HTTP/SSE.

Run this in its own terminal and keep it running:
    uv run server.py

Then, in a second terminal, run the Streamlit app / CLI (test_crewai.py).
"""

from __future__ import annotations

import os

from dotenv import load_dotenv
from fastmcp import FastMCP
from tavily import TavilyClient

load_dotenv()

mcp = FastMCP("Research MCP Server")

_client: TavilyClient | None = None


def _get_client() -> TavilyClient:
    global _client
    if _client is None:
        api_key = os.environ["TAVILY_API_KEY"]
        _client = TavilyClient(api_key=api_key)
    return _client


@mcp.tool()
def web_research(query: str, max_results: int = 5) -> list[dict]:
    """Search the web for authoritative, up-to-date sources on `query`.

    Returns a list of {title, url, snippet} results, each with the exact
    source URL so the Research Agent can cite it.
    """
    response = _get_client().search(
        query=query,
        max_results=max_results,
        search_depth="advanced",
    )
    return [
        {
            "title": item.get("title"),
            "url": item.get("url"),
            "snippet": item.get("content"),
        }
        for item in response.get("results", [])
    ]


if __name__ == "__main__":
    host = os.getenv("MCP_SERVER_HOST", "0.0.0.0")
    port = int(os.getenv("MCP_SERVER_PORT", "8000"))
    mcp.run(transport="sse", host=host, port=port)
