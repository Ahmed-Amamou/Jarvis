from langchain_core.tools import BaseTool

from .base import BaseAgent
from .tools.gmail_tools import (
    get_emails_needing_response,
    list_unread_emails,
    read_email,
    search_emails,
)

SYSTEM_PROMPT = """You are the Gmail Agent for JARVIS. Your job is to help the user with their email.

You have access to tools for reading, searching, and analyzing Gmail messages.
When summarizing emails, be concise but include key information: sender, subject, and the gist.
When asked about emails needing response, prioritize by importance and urgency.

Always be helpful and proactive — if you notice something urgent, mention it."""


class GmailAgent(BaseAgent):
    @property
    def agent_id(self) -> str:
        return "gmail_agent"

    def get_tools(self) -> list[BaseTool]:
        return [
            list_unread_emails,
            read_email,
            search_emails,
            get_emails_needing_response,
        ]

    def get_system_prompt(self) -> str:
        return SYSTEM_PROMPT
