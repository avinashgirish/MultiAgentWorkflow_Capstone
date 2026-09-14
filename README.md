# MultiAgentWorkflow_Capstone

Building a Multi-Agent AI Workflow with n8n and CrewAI (Google & LLM Integration).

## Overview

This project implements a multi-agent workflow system that automates market
research and go-to-market (GTM) planning, in **two equivalent ways**:

1. **[`n8n/`](n8n/)** — a no-code n8n workflow with Google integration.
2. **[`crewai_project/`](crewai_project/)** — a CrewAI project with a CLI and
   a Streamlit interface.

Both versions use a **Head Analyst Agent** to orchestrate three specialized
sub-agents:

- **Research Agent** — finds authoritative sources
- **Analyst Agent** — creates competitor tables & insights
- **GTM Agent** — drafts strategy sections

The output is a structured Google Doc containing the research, analysis, and
GTM strategy, optionally emailed to the user via Gmail.

## Architecture

```
Chat / CLI / Streamlit input
            │
            ▼
      Head Analyst  ──────────────┬──────────────┬───────────────┐
            │                     │               │               │
            ▼                     ▼               ▼               ▼
     Research Agent         Analyst Agent     GTM Agent      Google Docs
    (MCP tool / Tavily)      (SerpAPI)        (SerpAPI)      (create/update)
            │                     │               │
            └─────────────────────┴───────────────┘
                            │
                            ▼
                  Structured report + Google Doc
                            │
                            ▼
                   Gmail (optional email)
```

## Where to start

| I want to... | Go to |
|---|---|
| Build the workflow visually in n8n | [`n8n/README.md`](n8n/README.md) |
| Run the workflow as Python code (CLI/Streamlit) | [`crewai_project/README.md`](crewai_project/README.md) |

Both implementations share the same Google Cloud OAuth setup (Gmail + Google
Docs APIs) — see [`n8n/README.md` Step 1](n8n/README.md#step-1-google-cloud-console-setup).
