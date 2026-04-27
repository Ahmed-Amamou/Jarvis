import pytest
from langchain_core.messages import AIMessage, HumanMessage

from src.jarvis.orchestrator.state import JarvisState
from src.jarvis.orchestrator.nodes import create_nodes
from tests.conftest import MockProvider


@pytest.mark.asyncio
async def test_classifier_email_intent(mock_gateway):
    """Test that classifier correctly identifies email intents."""
    # Override the mock to return email_summary
    provider = list(mock_gateway.router.providers.values())[0]
    provider.response_text = "email_summary"

    nodes = create_nodes(mock_gateway)
    state: JarvisState = {
        "messages": [HumanMessage(content="Show me my unread emails")],
        "intent": None,
        "agent_output": None,
        "memory_context": [],
        "session_id": "test",
    }

    result = await nodes["classifier"](state)
    assert result["intent"] == "email_summary"


@pytest.mark.asyncio
async def test_classifier_calendar_intent(mock_gateway):
    provider = list(mock_gateway.router.providers.values())[0]
    provider.response_text = "calendar_today"

    nodes = create_nodes(mock_gateway)
    state: JarvisState = {
        "messages": [HumanMessage(content="What meetings do I have today?")],
        "intent": None,
        "agent_output": None,
        "memory_context": [],
        "session_id": "test",
    }

    result = await nodes["classifier"](state)
    assert result["intent"] == "calendar_today"


@pytest.mark.asyncio
async def test_classifier_general_fallback(mock_gateway):
    provider = list(mock_gateway.router.providers.values())[0]
    provider.response_text = "some_invalid_intent"

    nodes = create_nodes(mock_gateway)
    state: JarvisState = {
        "messages": [HumanMessage(content="What is the weather?")],
        "intent": None,
        "agent_output": None,
        "memory_context": [],
        "session_id": "test",
    }

    result = await nodes["classifier"](state)
    assert result["intent"] == "general"


@pytest.mark.asyncio
async def test_direct_llm_node(mock_gateway):
    nodes = create_nodes(mock_gateway)
    state: JarvisState = {
        "messages": [HumanMessage(content="Tell me a joke")],
        "intent": "general",
        "agent_output": None,
        "memory_context": [],
        "session_id": "test",
    }

    result = await nodes["direct_llm"](state)
    assert result["agent_output"] == "Mock response"


@pytest.mark.asyncio
async def test_synthesizer_general_passthrough(mock_gateway):
    nodes = create_nodes(mock_gateway)
    state: JarvisState = {
        "messages": [HumanMessage(content="hello")],
        "intent": "general",
        "agent_output": "Here is a joke!",
        "memory_context": [],
        "session_id": "test",
    }

    result = await nodes["synthesizer"](state)
    assert len(result["messages"]) == 1
    assert isinstance(result["messages"][0], AIMessage)
    assert result["messages"][0].content == "Here is a joke!"
