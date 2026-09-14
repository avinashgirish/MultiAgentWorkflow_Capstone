"""Builds and runs the Head Analyst crew end to end.

Flow (sequential, each task's output feeds the next via `context=`):
    Research Agent -> Analyst Agent -> GTM Agent -> Head Analyst (compiles report)

Then, deterministically in Python (not agent tool calls):
    report -> optionally published to Google Docs -> optionally emailed via Gmail
"""

from __future__ import annotations

import logging

from crewai import Crew, Process
from crewai_tools import MCPServerAdapter

from .agents import (
    build_analyst_agent,
    build_gtm_agent,
    build_head_analyst,
    build_research_agent,
)
from .config import MCP_SERVER_URL
from .google_workspace import create_or_update_doc, send_email
from .tasks import build_tasks

logger = logging.getLogger(__name__)


def run_workflow(
    topic: str,
    publish_to_google_doc: bool = True,
    notify_email: str | None = None,
) -> dict:
    """Run the full multi-agent workflow for `topic` and return its results.

    Returns a dict with:
        report:  the final markdown report (str)
        doc_url: the Google Doc URL, or None if not published / publishing failed
    """
    server_params = {"url": MCP_SERVER_URL}

    with MCPServerAdapter(server_params) as mcp_tools:
        research_agent = build_research_agent(mcp_tools)
        analyst_agent = build_analyst_agent()
        gtm_agent = build_gtm_agent()
        head_analyst = build_head_analyst()

        tasks = build_tasks(head_analyst, research_agent, analyst_agent, gtm_agent)

        crew = Crew(
            agents=[research_agent, analyst_agent, gtm_agent, head_analyst],
            tasks=tasks,
            process=Process.sequential,
            verbose=True,
        )

        crew_output = crew.kickoff(inputs={"topic": topic})

    report_markdown = str(crew_output)
    result: dict = {"report": report_markdown, "doc_url": None}

    if publish_to_google_doc:
        try:
            result["doc_url"] = create_or_update_doc(
                title=f"Market Research & GTM: {topic}",
                content_markdown=report_markdown,
            )
        except Exception:
            logger.exception("Failed to publish report to Google Docs")

    if notify_email:
        try:
            subject = f"Market Research & GTM report: {topic}"
            body = (
                f"{result['doc_url']}\n\n{report_markdown}"
                if result["doc_url"]
                else report_markdown
            )
            send_email(to=notify_email, subject=subject, body=body)
        except Exception:
            logger.exception("Failed to send email via Gmail")

    return result
