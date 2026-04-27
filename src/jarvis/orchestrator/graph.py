from langgraph.graph import END, StateGraph

from src.jarvis.llm.gateway import LLMGateway
from .nodes import create_nodes
from .state import JarvisState


def route_by_intent(state: JarvisState) -> str:
    intent = state.get("intent", "general")
    if intent in ("email_summary", "email_search", "email_response"):
        return "gmail_node"
    elif intent in ("calendar_today", "calendar_week", "calendar_upcoming", "calendar_conflicts"):
        return "calendar_node"
    else:
        return "direct_llm"


def build_graph(gateway: LLMGateway) -> StateGraph:
    nodes = create_nodes(gateway)

    graph = StateGraph(JarvisState)

    graph.add_node("classifier", nodes["classifier"])
    graph.add_node("gmail_node", nodes["gmail_node"])
    graph.add_node("calendar_node", nodes["calendar_node"])
    graph.add_node("direct_llm", nodes["direct_llm"])
    graph.add_node("synthesizer", nodes["synthesizer"])

    graph.set_entry_point("classifier")

    graph.add_conditional_edges(
        "classifier",
        route_by_intent,
        {
            "gmail_node": "gmail_node",
            "calendar_node": "calendar_node",
            "direct_llm": "direct_llm",
        },
    )

    graph.add_edge("gmail_node", "synthesizer")
    graph.add_edge("calendar_node", "synthesizer")
    graph.add_edge("direct_llm", "synthesizer")
    graph.add_edge("synthesizer", END)

    return graph.compile()
