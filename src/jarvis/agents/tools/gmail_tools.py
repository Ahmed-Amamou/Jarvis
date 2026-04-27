from langchain_core.tools import tool

from config.settings import settings
from src.jarvis.google.auth import GoogleAuth
from src.jarvis.google.gmail import GmailClient


def _get_gmail_client() -> GmailClient:
    auth = GoogleAuth(
        client_id=settings.google_client_id,
        client_secret=settings.google_client_secret,
        tokens_dir=settings.tokens_dir,
    )
    creds = auth.get_credentials()
    if not creds:
        raise RuntimeError("Google account not authenticated. Run 'jarvis auth login' first.")
    return GmailClient(creds)


@tool
def list_unread_emails(max_results: int = 10) -> str:
    """List unread emails from Gmail. Returns sender, subject, snippet for each."""
    client = _get_gmail_client()
    emails = client.list_unread(max_results=max_results)
    if not emails:
        return "No unread emails."

    lines = []
    for e in emails:
        lines.append(f"- From: {e.sender} | Subject: {e.subject} | {e.snippet[:80]}...")
    return "\n".join(lines)


@tool
def read_email(email_id: str) -> str:
    """Read the full content of an email by its ID."""
    client = _get_gmail_client()
    detail = client.read_email(email_id)
    return (
        f"From: {detail.sender}\n"
        f"To: {detail.to}\n"
        f"Subject: {detail.subject}\n"
        f"Date: {detail.date}\n\n"
        f"{detail.body[:3000]}"
    )


@tool
def search_emails(query: str, max_results: int = 5) -> str:
    """Search Gmail using Gmail search syntax (e.g., 'from:john subject:meeting')."""
    client = _get_gmail_client()
    emails = client.search_emails(query, max_results=max_results)
    if not emails:
        return f"No emails found for query: {query}"

    lines = []
    for e in emails:
        lines.append(f"- [{e.id}] From: {e.sender} | Subject: {e.subject} | {e.snippet[:60]}...")
    return "\n".join(lines)


@tool
def get_emails_needing_response(max_results: int = 5) -> str:
    """Find emails that are addressed to you and still unread (may need a response)."""
    client = _get_gmail_client()
    emails = client.get_threads_needing_response(max_results=max_results)
    if not emails:
        return "No emails needing your response."

    lines = []
    for e in emails:
        lines.append(f"- [{e.id}] From: {e.sender} | Subject: {e.subject}")
    return "\n".join(lines)
