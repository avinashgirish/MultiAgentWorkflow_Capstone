"""Environment configuration and LLM factory.

Reads all secrets/config from environment variables (see .env.example).
Supports Gemini, OpenAI, or Azure OpenAI as the model backend, matching
the choice the n8n Chat Model node also offers.
"""

from __future__ import annotations

import os

from dotenv import load_dotenv

load_dotenv()

LLM_PROVIDER = os.getenv("LLM_PROVIDER", "gemini").lower()
LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0.3"))

MCP_SERVER_URL = os.getenv("MCP_SERVER_URL", "http://localhost:8000/sse")

GOOGLE_CREDENTIALS_PATH = os.getenv("GOOGLE_CREDENTIALS_PATH", "credentials.json")
GOOGLE_TOKEN_PATH = os.getenv("GOOGLE_TOKEN_PATH", "token.json")


def get_llm():
    """Build the crewai.LLM used by every agent, based on LLM_PROVIDER."""
    from crewai import LLM

    if LLM_PROVIDER == "gemini":
        return LLM(
            model=os.getenv("GEMINI_MODEL", "gemini/gemini-2.0-flash"),
            api_key=os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY"),
            temperature=LLM_TEMPERATURE,
        )

    if LLM_PROVIDER == "openai":
        return LLM(
            model=os.getenv("OPENAI_MODEL", "gpt-4o"),
            api_key=os.getenv("OPENAI_API_KEY"),
            temperature=LLM_TEMPERATURE,
        )

    if LLM_PROVIDER == "azure":
        deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT")
        return LLM(
            model=f"azure/{deployment}",
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            api_base=os.getenv("AZURE_OPENAI_ENDPOINT"),
            api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2024-08-01-preview"),
            temperature=LLM_TEMPERATURE,
        )

    raise ValueError(
        f"Unsupported LLM_PROVIDER={LLM_PROVIDER!r}. Use 'gemini', 'openai', or 'azure'."
    )
