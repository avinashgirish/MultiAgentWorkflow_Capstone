"""Google Docs + Gmail integration, mirroring the n8n Google Docs/Gmail nodes.

Uses the same OAuth 2.0 client (Client ID/Secret from Google Cloud Console,
see the top-level README) as the n8n workflow, but drives it directly with
google-api-python-client instead of n8n's built-in nodes.

Publishing is done deterministically in Python (crew_app/crew.py) rather than
as an LLM-invoked tool call, so a report is never lost to a flaky tool call --
the agents focus on producing the content, this module focuses on delivering
it.
"""

from __future__ import annotations

import base64
from email.message import EmailMessage

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

from .config import GOOGLE_CREDENTIALS_PATH, GOOGLE_TOKEN_PATH

SCOPES = [
    "https://www.googleapis.com/auth/documents",
    "https://www.googleapis.com/auth/gmail.send",
]

# Tracks the Google Doc created during the current process, so a second
# publish call in the same run updates it instead of creating a new doc --
# same idea as the n8n "Create Document" -> "Update Document" pair.
_active_doc_id: str | None = None


def _get_credentials() -> Credentials:
    creds: Credentials | None = None
    if GOOGLE_TOKEN_PATH and _path_exists(GOOGLE_TOKEN_PATH):
        creds = Credentials.from_authorized_user_file(GOOGLE_TOKEN_PATH, SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                GOOGLE_CREDENTIALS_PATH, SCOPES
            )
            creds = flow.run_local_server(port=0)
        with open(GOOGLE_TOKEN_PATH, "w") as token_file:
            token_file.write(creds.to_json())

    return creds


def _path_exists(path: str) -> bool:
    import os

    return os.path.exists(path)


def _docs_service():
    return build("docs", "v1", credentials=_get_credentials())


def _gmail_service():
    return build("gmail", "v1", credentials=_get_credentials())


def create_or_update_doc(title: str, content_markdown: str) -> str:
    """Create a new Google Doc, or update the one already created this run.

    Returns the doc's shareable URL.
    """
    global _active_doc_id
    service = _docs_service()

    if _active_doc_id is None:
        doc = service.documents().create(body={"title": title}).execute()
        _active_doc_id = doc["documentId"]
    else:
        doc = service.documents().get(documentId=_active_doc_id).execute()
        end_index = doc["body"]["content"][-1]["endIndex"]
        if end_index > 2:
            service.documents().batchUpdate(
                documentId=_active_doc_id,
                body={
                    "requests": [
                        {
                            "deleteContentRange": {
                                "range": {"startIndex": 1, "endIndex": end_index - 1}
                            }
                        }
                    ]
                },
            ).execute()

    service.documents().batchUpdate(
        documentId=_active_doc_id,
        body={
            "requests": [
                {"insertText": {"location": {"index": 1}, "text": content_markdown}}
            ]
        },
    ).execute()

    return f"https://docs.google.com/document/d/{_active_doc_id}/edit"


def send_email(to: str, subject: str, body: str) -> None:
    """Send the report via Gmail, same as the n8n Gmail "Send Email" node."""
    service = _gmail_service()

    message = EmailMessage()
    message.set_content(body)
    message["To"] = to
    message["Subject"] = subject

    encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
    service.users().messages().send(
        userId="me", body={"raw": encoded_message}
    ).execute()
