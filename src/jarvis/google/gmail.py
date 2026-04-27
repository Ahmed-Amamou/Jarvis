import base64
import logging
from dataclasses import dataclass

from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials

logger = logging.getLogger(__name__)


@dataclass
class EmailSummary:
    id: str
    thread_id: str
    sender: str
    subject: str
    snippet: str
    date: str
    is_unread: bool


@dataclass
class EmailDetail:
    id: str
    sender: str
    to: str
    subject: str
    date: str
    body: str


class GmailClient:
    def __init__(self, credentials: Credentials):
        self.service = build("gmail", "v1", credentials=credentials)

    def list_unread(self, max_results: int = 20) -> list[EmailSummary]:
        results = (
            self.service.users()
            .messages()
            .list(userId="me", q="is:unread", maxResults=max_results)
            .execute()
        )
        messages = results.get("messages", [])
        return [self._to_summary(msg["id"], is_unread=True) for msg in messages]

    def search_emails(self, query: str, max_results: int = 10) -> list[EmailSummary]:
        results = (
            self.service.users()
            .messages()
            .list(userId="me", q=query, maxResults=max_results)
            .execute()
        )
        messages = results.get("messages", [])
        return [self._to_summary(msg["id"]) for msg in messages]

    def read_email(self, msg_id: str) -> EmailDetail:
        msg = (
            self.service.users()
            .messages()
            .get(userId="me", id=msg_id, format="full")
            .execute()
        )
        headers = {h["name"]: h["value"] for h in msg["payload"]["headers"]}
        body = self._extract_body(msg["payload"])

        return EmailDetail(
            id=msg_id,
            sender=headers.get("From", ""),
            to=headers.get("To", ""),
            subject=headers.get("Subject", ""),
            date=headers.get("Date", ""),
            body=body,
        )

    def get_threads_needing_response(self, max_results: int = 10) -> list[EmailSummary]:
        """Find emails where user is in TO/CC but hasn't replied."""
        results = (
            self.service.users()
            .messages()
            .list(
                userId="me",
                q="is:unread to:me -from:me",
                maxResults=max_results,
            )
            .execute()
        )
        messages = results.get("messages", [])
        return [self._to_summary(msg["id"], is_unread=True) for msg in messages]

    def _to_summary(self, msg_id: str, is_unread: bool = False) -> EmailSummary:
        msg = (
            self.service.users()
            .messages()
            .get(userId="me", id=msg_id, format="metadata", metadataHeaders=["From", "Subject", "Date"])
            .execute()
        )
        headers = {h["name"]: h["value"] for h in msg["payload"]["headers"]}
        labels = msg.get("labelIds", [])

        return EmailSummary(
            id=msg_id,
            thread_id=msg.get("threadId", ""),
            sender=headers.get("From", ""),
            subject=headers.get("Subject", ""),
            snippet=msg.get("snippet", ""),
            date=headers.get("Date", ""),
            is_unread=is_unread or "UNREAD" in labels,
        )

    def _extract_body(self, payload: dict) -> str:
        """Extract plain text body from email payload."""
        if payload.get("mimeType") == "text/plain" and payload.get("body", {}).get("data"):
            return base64.urlsafe_b64decode(payload["body"]["data"]).decode("utf-8", errors="replace")

        for part in payload.get("parts", []):
            result = self._extract_body(part)
            if result:
                return result

        # Fallback: try HTML
        if payload.get("mimeType") == "text/html" and payload.get("body", {}).get("data"):
            html = base64.urlsafe_b64decode(payload["body"]["data"]).decode("utf-8", errors="replace")
            # Strip HTML tags naively for now
            import re
            return re.sub(r"<[^>]+>", "", html).strip()

        return ""
