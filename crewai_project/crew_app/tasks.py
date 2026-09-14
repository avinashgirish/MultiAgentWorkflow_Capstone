"""Task definitions for the sequential research -> analysis -> GTM -> report pipeline."""

from __future__ import annotations

from crewai import Agent, Task


def build_tasks(
    head_analyst: Agent,
    research_agent: Agent,
    analyst_agent: Agent,
    gtm_agent: Agent,
) -> list[Task]:
    research_task = Task(
        description=(
            "Research the topic: '{topic}'.\n"
            "Use the web_research tool to find authoritative, recent sources "
            "(official sites, news, industry reports, reviews). For every "
            "claim, record the exact source URL so it can be cited later."
        ),
        expected_output=(
            "A bullet list of 6-10 key findings about '{topic}'. Each bullet "
            "must end with its source URL in parentheses."
        ),
        agent=research_agent,
    )

    analysis_task = Task(
        description=(
            "Using the Research Agent's findings on '{topic}', identify the "
            "competing products or companies involved and build a comparison. "
            "Use the Google Search tool to fill any gaps (pricing, features, "
            "market positioning, strengths, weaknesses)."
        ),
        expected_output=(
            "A markdown comparison table of the competitors (columns: "
            "Company, Key Offering, Pricing, Strengths, Weaknesses) followed "
            "by 3-5 bullet insights, each citing a source URL."
        ),
        agent=analyst_agent,
        context=[research_task],
    )

    gtm_task = Task(
        description=(
            "Using the research and competitive analysis for '{topic}', draft "
            "a go-to-market strategy. Use the Google Search tool if you need "
            "more market-sizing or channel data."
        ),
        expected_output=(
            "A GTM strategy section in markdown covering: Target Segment, "
            "Positioning & Messaging, Pricing Strategy, Channels, and a "
            "90-day Launch Plan, citing supporting source URLs."
        ),
        agent=gtm_agent,
        context=[research_task, analysis_task],
    )

    report_task = Task(
        description=(
            "Combine the research findings, competitive analysis, and GTM "
            "strategy for '{topic}' into a single, well-structured report. "
            "Keep every source URL so the report is fully cited. Do not drop "
            "the competitor table."
        ),
        expected_output=(
            "A complete markdown report with sections: Title, Executive "
            "Summary, Research Findings (with links), Competitive Analysis "
            "(with table), Go-To-Market Strategy, and a final 'Sources' list "
            "of every URL used."
        ),
        agent=head_analyst,
        context=[research_task, analysis_task, gtm_task],
    )

    return [research_task, analysis_task, gtm_task, report_task]
