"""Agent factories for the Head Analyst and its three specialist sub-agents.

This mirrors the n8n workflow's roles exactly:
  - Head Analyst: orchestrates, then compiles the final cited report
  - Research Agent: finds authoritative sources (via the MCP research tool)
  - Analyst Agent: builds the competitor comparison table and insights
  - GTM Agent: drafts the go-to-market strategy section
"""

from __future__ import annotations

from typing import Iterable

from crewai import Agent
from crewai.tools import BaseTool
from crewai_tools import SerpApiGoogleSearchTool

from .config import get_llm


def build_research_agent(mcp_tools: Iterable[BaseTool]) -> Agent:
    return Agent(
        role="Research Agent",
        goal=(
            "Find authoritative, up-to-date sources on the assigned topic and "
            "capture the exact URL for every fact so it can be cited later."
        ),
        backstory=(
            "You are a meticulous research analyst. You never state a fact "
            "without a source URL attached to it."
        ),
        tools=list(mcp_tools),
        llm=get_llm(),
        allow_delegation=False,
        verbose=True,
    )


def build_analyst_agent() -> Agent:
    return Agent(
        role="Analyst Agent",
        goal=(
            "Turn raw research into a clear competitor comparison table plus "
            "sharp, decision-ready insights."
        ),
        backstory=(
            "You are a market analyst who thinks in comparisons: pricing, "
            "features, positioning, strengths, and weaknesses side by side."
        ),
        tools=[SerpApiGoogleSearchTool()],
        llm=get_llm(),
        allow_delegation=False,
        verbose=True,
    )


def build_gtm_agent() -> Agent:
    return Agent(
        role="GTM Agent",
        goal=(
            "Draft a concrete, actionable go-to-market strategy grounded in the "
            "research and competitive analysis."
        ),
        backstory=(
            "You are a go-to-market strategist who turns research and "
            "competitive analysis into a launch plan a founder could execute."
        ),
        tools=[SerpApiGoogleSearchTool()],
        llm=get_llm(),
        allow_delegation=False,
        verbose=True,
    )


def build_head_analyst() -> Agent:
    return Agent(
        role="Head Analyst",
        goal=(
            "Own the end-to-end market research and go-to-market report: "
            "curate the research, analysis, and GTM strategy into one "
            "well-structured, fully cited report."
        ),
        backstory=(
            "You are the lead analyst on the team. You never drop a source "
            "URL, you never drop the competitor table, and you write the "
            "final report so a busy executive can act on it immediately."
        ),
        llm=get_llm(),
        allow_delegation=False,
        verbose=True,
    )
