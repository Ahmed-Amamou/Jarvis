from src.jarvis.agents.gmail_agent import GmailAgent
from src.jarvis.agents.calendar_agent import CalendarAgent


def test_gmail_agent_has_tools():
    agent = GmailAgent()
    tools = agent.get_tools()
    assert len(tools) == 4
    tool_names = {t.name for t in tools}
    assert "list_unread_emails" in tool_names
    assert "read_email" in tool_names
    assert "search_emails" in tool_names
    assert "get_emails_needing_response" in tool_names


def test_gmail_agent_system_prompt():
    agent = GmailAgent()
    prompt = agent.get_system_prompt()
    assert "Gmail" in prompt
    assert len(prompt) > 50


def test_calendar_agent_has_tools():
    agent = CalendarAgent()
    tools = agent.get_tools()
    assert len(tools) == 4
    tool_names = {t.name for t in tools}
    assert "get_events_today" in tool_names
    assert "get_upcoming_events" in tool_names
    assert "get_events_this_week" in tool_names
    assert "check_calendar_conflicts" in tool_names


def test_calendar_agent_system_prompt():
    agent = CalendarAgent()
    prompt = agent.get_system_prompt()
    assert "Calendar" in prompt


def test_agent_ids():
    assert GmailAgent().agent_id == "gmail_agent"
    assert CalendarAgent().agent_id == "calendar_agent"
