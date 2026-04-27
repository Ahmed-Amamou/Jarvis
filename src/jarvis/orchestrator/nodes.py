import json
import logging

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

from src.jarvis.agents.calendar_agent import CalendarAgent
from src.jarvis.agents.gmail_agent import GmailAgent
from src.jarvis.llm.gateway import LLMGateway
from src.jarvis.llm.providers.base import LLMResponse
from .state import JarvisState

logger = logging.getLogger(__name__)

gmail_agent = GmailAgent()
calendar_agent = CalendarAgent()


def create_nodes(gateway: LLMGateway):
    """Create all graph nodes bound to the given LLM gateway."""

    async def classifier(state: JarvisState) -> dict:
        """Classify user intent to route to the right agent."""
        last_message = ""
        for msg in reversed(state["messages"]):
            if isinstance(msg, HumanMessage):
                last_message = msg.content
                break

        classification_prompt = [
            {
                "role": "system",
                "content": (
                    "You are an intent classifier. Classify the user message into exactly one of these intents:\n"
                    '- "email_summary": user wants to see/summarize emails, inbox overview\n'
                    '- "email_search": user wants to search for specific emails\n'
                    '- "email_response": user wants to know which emails need a response\n'
                    '- "calendar_today": user asks about today\'s meetings/schedule\n'
                    '- "calendar_week": user asks about this week\'s schedule\n'
                    '- "calendar_upcoming": user asks about upcoming/next meetings\n'
                    '- "calendar_conflicts": user asks about scheduling conflicts\n'
                    '- "general": general question, not about email or calendar\n\n'
                    "Respond with ONLY the intent string, nothing else."
                ),
            },
            {"role": "user", "content": last_message},
        ]

        result = await gateway.complete(messages=classification_prompt, model="default", temperature=0.0)
        assert isinstance(result, LLMResponse)
        intent = result.content.strip().strip('"').lower()

        # Normalize
        valid_intents = {
            "email_summary", "email_search", "email_response",
            "calendar_today", "calendar_week", "calendar_upcoming", "calendar_conflicts",
            "general",
        }
        if intent not in valid_intents:
            intent = "general"

        logger.info(f"Classified intent: {intent}")
        return {"intent": intent}

    async def gmail_node(state: JarvisState) -> dict:
        """Run Gmail agent tools based on intent."""
        intent = state.get("intent", "email_summary")
        last_message = ""
        for msg in reversed(state["messages"]):
            if isinstance(msg, HumanMessage):
                last_message = msg.content
                break

        # Select the right tool based on intent
        if intent == "email_response":
            from src.jarvis.agents.tools.gmail_tools import get_emails_needing_response
            tool_result = get_emails_needing_response.invoke({"max_results": 10})
        elif intent == "email_search":
            from src.jarvis.agents.tools.gmail_tools import search_emails
            tool_result = search_emails.invoke({"query": last_message, "max_results": 5})
        else:
            from src.jarvis.agents.tools.gmail_tools import list_unread_emails
            tool_result = list_unread_emails.invoke({"max_results": 10})

        return {"agent_output": tool_result}

    async def calendar_node(state: JarvisState) -> dict:
        """Run Calendar agent tools based on intent."""
        intent = state.get("intent", "calendar_today")

        if intent == "calendar_week":
            from src.jarvis.agents.tools.calendar_tools import get_events_this_week
            tool_result = get_events_this_week.invoke({})
        elif intent == "calendar_upcoming":
            from src.jarvis.agents.tools.calendar_tools import get_upcoming_events
            tool_result = get_upcoming_events.invoke({"minutes": 60})
        else:
            from src.jarvis.agents.tools.calendar_tools import get_events_today
            tool_result = get_events_today.invoke({})

        return {"agent_output": tool_result}

    async def direct_llm(state: JarvisState) -> dict:
        """Handle general questions directly with the LLM."""
        messages = [{"role": "system", "content": "You are JARVIS, a helpful AI assistant."}]
        for msg in state["messages"]:
            if isinstance(msg, HumanMessage):
                messages.append({"role": "user", "content": msg.content})
            elif isinstance(msg, AIMessage):
                messages.append({"role": "assistant", "content": msg.content})

        result = await gateway.complete(messages=messages, model="default")
        assert isinstance(result, LLMResponse)
        return {"agent_output": result.content}

    async def synthesizer(state: JarvisState) -> dict:
        """Synthesize agent output into a natural language response."""
        agent_output = state.get("agent_output", "")
        intent = state.get("intent", "general")

        if intent == "general":
            return {"messages": [AIMessage(content=agent_output)]}

        last_message = ""
        for msg in reversed(state["messages"]):
            if isinstance(msg, HumanMessage):
                last_message = msg.content
                break

        synthesis_prompt = [
            {
                "role": "system",
                "content": (
                    "You are JARVIS, a helpful AI assistant. The user asked a question and "
                    "a specialized agent gathered the following data. Summarize it in a clear, "
                    "friendly, and concise way. Include actionable items if relevant."
                ),
            },
            {"role": "user", "content": last_message},
            {
                "role": "assistant",
                "content": f"Here is the raw data from the agent:\n\n{agent_output}",
            },
            {
                "role": "user",
                "content": "Please present this information in a clear, well-formatted summary.",
            },
        ]

        result = await gateway.complete(messages=synthesis_prompt, model="default")
        assert isinstance(result, LLMResponse)
        return {"messages": [AIMessage(content=result.content)]}

    return {
        "classifier": classifier,
        "gmail_node": gmail_node,
        "calendar_node": calendar_node,
        "direct_llm": direct_llm,
        "synthesizer": synthesizer,
    }
