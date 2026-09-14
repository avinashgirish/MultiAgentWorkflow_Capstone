# Market Research & GTM Crew (CrewAI)

A CrewAI implementation of the same multi-agent workflow as the [n8n version](../n8n/README.md):
a **Head Analyst** agent orchestrates three specialist sub-agents to produce a
structured, cited market research + go-to-market (GTM) report, optionally
publishing it to Google Docs and emailing it via Gmail.

| Role | Responsibility | Tools |
|---|---|---|
| **Head Analyst** | Compiles the final cited report | — |
| **Research Agent** | Finds authoritative sources | MCP `web_research` tool (Tavily), served by `server.py` |
| **Analyst Agent** | Competitor comparison table & insights | SerpAPI Google Search |
| **GTM Agent** | Drafts the GTM strategy section | SerpAPI Google Search |

Publishing to Google Docs / Gmail is handled deterministically in Python
(`crew_app/crew.py`) after the crew finishes, so a completed report is never
lost to a missed tool call.

## Project layout

```
crewai_project/
├── pyproject.toml       # uv-managed dependencies
├── .env.example         # copy to .env and fill in your keys
├── server.py            # FastMCP research backend (Tavily search tool)
├── test_crewai.py       # CLI + Streamlit entrypoint
└── crew_app/
    ├── config.py         # env config + LLM factory (Gemini/OpenAI/Azure)
    ├── agents.py         # Head Analyst + 3 sub-agents
    ├── tasks.py          # research -> analysis -> GTM -> report pipeline
    ├── crew.py           # builds & runs the crew, then publishes the result
    └── google_workspace.py  # Google Docs create/update + Gmail send
```

## Setup

1. **Install dependencies** (already pinned in `pyproject.toml`/`uv.lock`):

   ```bash
   cd crewai_project
   uv sync
   ```

2. **Configure secrets** — copy `.env.example` to `.env` and fill in:
   - `LLM_PROVIDER` (`gemini`, `openai`, or `azure`) + the matching API key
   - `SERPAPI_API_KEY` — for the Analyst/GTM search tool ([serpapi.com](https://serpapi.com/manage-api-key))
   - `TAVILY_API_KEY` — for the Research Agent's MCP search tool ([tavily.com](https://app.tavily.com))

3. **Google OAuth credentials** (for Google Docs + Gmail publishing) — reuse
   the same OAuth 2.0 client described in the [n8n setup, Step 1](../n8n/README.md#step-1-google-cloud-console-setup):
   - In Google Cloud Console, create an **OAuth client ID** of type **Desktop app**.
   - Enable the **Google Docs API** and **Gmail API**.
   - Download the client secret JSON and save it as `credentials.json` in this
     folder (path configurable via `GOOGLE_CREDENTIALS_PATH`).
   - The first run opens a browser for consent and caches the result in
     `token.json` (`GOOGLE_TOKEN_PATH`) for subsequent runs.
   - If your OAuth consent screen is still in **Testing** mode, add your
     Google account as a **Test User** under *OAuth Consent Screen*.

## Running it

Run these in **two separate terminals** — the backend server has to be up
before the crew connects to it.

**Terminal 1 — start the MCP research backend and keep it running:**

```bash
uv run server.py
```

**Terminal 2 — run the crew:**

CLI:

```bash
uv run python test_crewai.py "simplilearn vs edureka"
```

Streamlit UI:

```bash
uv run streamlit run test_crewai.py
```

Then open the local URL Streamlit prints (e.g. `http://localhost:8501`),
enter a topic (e.g. `simplilearn vs edureka`), choose whether to publish to
Google Docs / email the result, and click **Run analysis**.

## How it maps to the n8n workflow

| n8n | CrewAI |
|---|---|
| Chat Trigger | CLI arg / Streamlit form input |
| Head Analyst (AI Agent) | `build_head_analyst()` — compiles the final report |
| Research Agent + MCP Tool node | `build_research_agent()` + `server.py` (FastMCP/Tavily) via `MCPServerAdapter` |
| Analyst Agent + SerpAPI node | `build_analyst_agent()` + `SerpApiGoogleSearchTool` |
| GTM Agent + SerpAPI node | `build_gtm_agent()` + `SerpApiGoogleSearchTool` |
| Gemini Chat Model node(s) | `crew_app/config.py::get_llm()` (Gemini/OpenAI/Azure) |
| Google Docs Create/Update nodes | `crew_app/google_workspace.py::create_or_update_doc()` |
| Gmail Send Email node | `crew_app/google_workspace.py::send_email()` |
| MCP Server workflow (Step 2.9) | `server.py` |
