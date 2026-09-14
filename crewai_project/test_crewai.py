"""Streamlit UI and CLI entrypoint for the Market Research & GTM Crew.

CLI:
    uv run python test_crewai.py "simplilearn vs edureka"

Streamlit:
    uv run streamlit run test_crewai.py

The MCP research server (server.py) must already be running in another
terminal before either of these is used.
"""

from __future__ import annotations

import sys

from crew_app.crew import run_workflow


def run_cli(topic: str) -> None:
    result = run_workflow(topic)
    print(result["report"])
    if result.get("doc_url"):
        print(f"\nGoogle Doc: {result['doc_url']}")


def run_streamlit() -> None:
    import streamlit as st

    st.set_page_config(page_title="Multi-Agent Market Research & GTM", page_icon="📊")
    st.title("📊 Multi-Agent Market Research & GTM Planner")
    st.caption("Head Analyst → Research Agent → Analyst Agent → GTM Agent")

    with st.form("query_form"):
        topic = st.text_input(
            "Research topic", placeholder="e.g., simplilearn vs edureka"
        )
        publish = st.checkbox("Publish result to Google Docs", value=True)
        email = st.text_input("Email the report to (optional)")
        submitted = st.form_submit_button("Run analysis")

    if submitted and topic:
        with st.spinner(
            "Agents are researching, analyzing, and drafting your GTM strategy..."
        ):
            try:
                result = run_workflow(
                    topic,
                    publish_to_google_doc=publish,
                    notify_email=email or None,
                )
            except Exception as exc:  # surface the failure in the UI
                st.error(f"Workflow failed: {exc}")
                return

        st.success("Done!")
        if result.get("doc_url"):
            st.markdown(f"**Google Doc:** [{result['doc_url']}]({result['doc_url']})")
        st.markdown(result["report"])


def _running_under_streamlit() -> bool:
    try:
        from streamlit.runtime.scriptrunner import get_script_run_ctx

        return get_script_run_ctx() is not None
    except Exception:
        return False


if __name__ == "__main__":
    if _running_under_streamlit():
        run_streamlit()
    elif len(sys.argv) > 1:
        run_cli(" ".join(sys.argv[1:]))
    else:
        print('Usage: uv run python test_crewai.py "<research topic>"')
        print("   or: uv run streamlit run test_crewai.py")
