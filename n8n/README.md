# Multi-Agent Analysis System (n8n)

An n8n implementation of the multi-agent market research + GTM workflow. A
**Head Analyst** AI Agent orchestrates three specialist sub-agents (each
exposed to it as a *tool*), then writes the final report to a Google Doc and
emails the link via Gmail.

Two importable workflow files are included as a starting scaffold:

| File | Purpose |
|---|---|
| `multi_agent_analysis_workflow.json` | The main workflow: Chat Trigger → Head Analyst (+ tools) → Send Email |
| `mcp_server_workflow.json` | A standalone MCP server workflow (Step 2.9) that exposes SerpAPI as an MCP tool |

> **Import note:** after importing (`n8n → Workflows → Import from File`),
> every node's credentials show as missing — that's expected, since
> credentials aren't portable between n8n instances. Open each node and pick
> (or create) your own credential, per Step 1 below. Node versions may also
> show an "update available" notice depending on your n8n version; that's
> safe to accept.

## Architecture

```
Chat Trigger
     │
     ▼
Head Analyst (AI Agent) ── ai_languageModel ── Gemini Chat Model
     │  ▲ ai_tool                                ▲ ai_tool           ▲ ai_tool
     │  ├── Research Agent (AI Agent) ── ai_tool ── Research MCP Tool
     │  ├── Analyst Agent (AI Agent)  ── ai_tool ── SerpAPI (Analyst)
     │  ├── GTM Agent (AI Agent)      ── ai_tool ── SerpAPI (GTM)
     │  ├── Google Doc create
     │  └── Google Doc update
     │
     ▼  main (final answer = just the Doc link)
Send Email (Gmail)
```

Each sub-agent (Research/Analyst/GTM) is itself an AI Agent node, connected
into the Head Analyst's **tool** input (`ai_tool`) rather than the main data
flow — this is what the "magic button" in Step 2.4 sets up: it swaps the
sub-agent's prompt field to `$fromAI(...)`, so the Head Analyst decides what
to pass it. Google Doc create/update are added as tools the same way,
matching the Head Analyst's Tool Settings in Step 2.3 and the "write it to a
Google Doc using doc tools" instruction in its system prompt. Because the
system prompt tells the Head Analyst to output *only* the Doc link with no
extra words, that clean output can be piped straight into the Gmail node's
message body.

## Prerequisites

- n8n instance (self-hosted or cloud)
- Google Cloud Console account
- SerpAPI key ([serpapi.com](https://serpapi.com/manage-api-key))
- Gemini API key
- MCP tool access

## Step 1: Google Cloud Console setup

### 1.1 Create OAuth 2.0 credentials

1. Navigate to [Google Cloud Console](https://console.cloud.google.com/).
2. Create a new project or select an existing one.
3. Go to **APIs & Services → Credentials**.
4. Click **+ CREATE CREDENTIALS → OAuth client ID**.
5. Configure the OAuth consent screen if prompted:
   - Choose **External** or **Internal** based on your needs.
   - Fill in the required application information.
6. For **Application type**, pick based on your n8n setup:
   - **Web application** — if n8n is hosted on a server.
   - **Desktop app** — if running locally.
7. Add authorized redirect URIs (for web application):
   - `https://your-n8n-instance.com/rest/oauth2-credential/callback`
   - For local development: `http://localhost:5678/rest/oauth2-credential/callback`
8. Save your **Client ID** and **Client Secret**.

### 1.2 Enable APIs and configure sign-in

1. In Google Cloud Console, go to **APIs & Services → Library**.
2. Search for and enable:
   - **Gmail API** — for sending emails.
   - **Google Docs API** — for document creation and updates.
   - **Google Drive API** *(optional)* — for file management.
3. Confirm each API shows an **"API Enabled"** status.

### Google Cloud → OAuth sign-in (after credentials)

- After adding the Client ID/Secret into n8n (on the Google Docs or Gmail
  node), n8n will prompt you to log in with Google.
- If your app is still in **Testing** mode on the OAuth consent screen, you
  must add your Google account as a **Test User** under *OAuth Consent
  Screen*, or the sign-in will be rejected.

## Step 2: n8n workflow construction

### 2.1 Create a new workflow

1. Open your n8n instance.
2. Click **New Workflow**.
3. Name it, e.g. `Multi-Agent Analysis System`.

### 2.2 Add a Chat Trigger node

1. Click **+** to add a new node.
2. Search for **Chat Trigger** and add it.
3. Configure:
   - Set response mode as needed.
   - Enable any required options for your use case.

### 2.3 Configure the Head Analyst (AI Agent node)

1. Add an **AI Agent** node — this is your Head Analyst.
2. Connect the Chat Trigger's output to it.
3. Basic settings:
   - **Name:** `Head Analyst`
   - **Model:** select Gemini
4. **Tool Settings** — attach these five tools (built in the following
   sub-steps):
   - Research Agent tool
   - Analyst Agent tool
   - GTM Agent tool
   - Google Doc create
   - Google Doc update
5. **System instructions** (copy and paste):

   ```text
   You are a report creator, in your team, you have several agents for your help and tools as well

   rules must follow:
   1. Include URL and links for the Research Agent and cite them in the right place if not already

   task:
   1. Understand the topic of research
   2. Use the Research Agent tool to get the research and supporting links on that.
   3. Pass the content to the analysis agent to analyze
   4. Make a GTM using the strategy agent tool
   5. Curate everything, including URLs from web search and links to support the facts, into a report format and write it to a Google Doc using doc tools
   6. output link to the doc, no extra words, just the link
   ```

6. **Prompt configuration:**
   - Connect to: `{{ $json.chatInput }}` (from Chat Trigger)
   - Enable batch processing if needed; set temperature and other model
     parameters as desired.

### 2.4 Create the sub-agents as tools

**Research Agent setup**

1. Add another **AI Agent** node.
2. Configure it as a tool:
   - **Name:** `Research Agent`
   - Click the magic button near the prompt bar — this makes the prompt come
     from the Head Analyst (`$fromAI(...)`). Do the same for the system
     prompt field.
3. Add an **MCP Tool** node:
   - Connect it to the Research Agent.
   - Configure the MCP URL (point it at your MCP server workflow's
     production URL — see Step 2.9).

**Analyst Agent setup**

1. Add an **AI Agent** node.
2. Configure it as a tool:
   - **Name:** `Analyst Agent`
   - Click the magic button near the prompt bar, and do the same for the
     system prompt.
3. Add a **SerpAPI** node:
   - Connect it to the Analyst Agent.
   - Configure it with your SerpAPI key and search parameters.

**GTM Agent setup**

1. Add an **AI Agent** node.
2. Configure it as a tool:
   - **Name:** `GTM Agent`
   - Click the magic button near the prompt bar, and do the same for the
     system prompt.
3. Add another **SerpAPI** node:
   - Connect it to the GTM Agent.
   - Configure it for market/competitive searches.

This creates the dotted-line (tool) connections in the workflow.

### 2.5 Configure the chat model for all agents

For each AI Agent node:

1. Add a **Gemini Chat Model** node (you can choose your preferred chat
   model: Google Gemini, OpenAI, or Azure OpenAI).
2. Connect it to the respective AI Agent.
3. Configure:
   - **API Key:** your Gemini API key.
   - **Model:** an appropriate model (e.g., `gemini-1.5-pro`).

### 2.6 Add Google Docs tools

1. Add a **Google Docs** node — **Google Doc create**:
   - Operation: **Create Document**.
   - Connect it as a tool to the Head Analyst.
   - Configure authentication using the OAuth credentials from Step 1.
2. Add another **Google Docs** node — **Google Doc update**:
   - Operation: **Update Document**.
   - Connect it as a tool to the Head Analyst.
   - Configure authentication using the OAuth credentials from Step 1.
   - In the document ID field, use the expression builder to reference the
     Document ID the model passes in (this is filled automatically via
     `$fromAI(...)` once the Head Analyst has already called
     **Google Doc create** in the same run).

### 2.7 Configure Gmail integration

1. Add a **Gmail** node — **Send Email**.
2. Connect it to the **Head Analyst**'s main output (its final answer, which
   per the system prompt is just the Doc link).
3. Configure:
   - **Authentication:** OAuth credentials from Step 1.
   - **Operation:** Send Email.
   - **To:** `{{ $json.recipientEmail }}`
   - **Subject:** a dynamic subject based on the analysis.
   - **Body:** include the document link (and summary if desired).

### 2.8 Set up the MCP server in n8n

1. **Create a new workspace** — in your n8n instance, click **New Workflow**
   to start a fresh workspace dedicated to MCP server integration.
2. **Add an MCP Server Trigger node** — search for **MCP Server Trigger** in
   the node list and drag it into your workflow. This node is the entry
   point for requests to the MCP server.
3. **Connect SerpAPI as a tool** — add a **SerpAPI** node, link it directly
   to the MCP Server Trigger node, and configure it with your SerpAPI key
   and search parameters. When the MCP server is triggered, SerpAPI runs
   automatically as the connected tool.
4. **Activate the workspace** — toggle **Active** in the top-right corner of
   the n8n editor to make the workflow live and able to listen for MCP
   server requests.
5. **Execute the flow** — click **Execute Workflow** to test the setup. The
   MCP server trigger fires, SerpAPI runs, and results are passed back into
   the flow.

## Step 3: Workflow parameters and data flow

**Chat Trigger → Head Analyst:** passes the user message as `chatInput`.

**Head Analyst → Sub-Agents:** delegates specific queries based on content;
each sub-agent receives a targeted prompt via `$fromAI(...)`.

**Sub-Agents → External Tools:**
- Research Agent → MCP Tool
- Analyst / GTM Agents → SerpAPI

**Results aggregation:** sub-agents return findings to the Head Analyst,
which synthesizes a comprehensive report.

**Output generation:**
1. Create the Google Doc with the findings.
2. Update the document with the fully formatted content.
3. Send the document link via Gmail.

## Testing

1. Activate the workflow.
2. Open the Chat Trigger's chat panel (or its public URL).
3. Send a message such as `simplilearn vs edureka`.
4. Confirm: the Research/Analyst/GTM tools are invoked, a Google Doc is
   created and populated, and (if configured) an email with the doc link is
   sent.

See [`../crewai_project/README.md`](../crewai_project/README.md) for the
equivalent workflow implemented as a CrewAI project with a CLI and Streamlit
interface.
