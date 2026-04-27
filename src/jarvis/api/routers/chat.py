import uuid

from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
from langchain_core.messages import AIMessage, HumanMessage

from src.jarvis.api.deps import get_llm_gateway
from src.jarvis.api.schemas import ChatRequest, ChatResponse
from src.jarvis.llm.gateway import LLMGateway
from src.jarvis.orchestrator.graph import build_graph

router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest, gateway: LLMGateway = Depends(get_llm_gateway)):
    graph = build_graph(gateway)

    initial_state = {
        "messages": [HumanMessage(content=req.message)],
        "intent": None,
        "agent_output": None,
        "memory_context": [],
        "session_id": req.session_id,
    }

    result = await graph.ainvoke(initial_state)

    response_text = ""
    for msg in reversed(result["messages"]):
        if isinstance(msg, AIMessage):
            response_text = msg.content
            break

    return ChatResponse(
        response=response_text,
        session_id=req.session_id,
        model="default",
    )


@router.websocket("/chat/ws")
async def chat_ws(ws: WebSocket, gateway: LLMGateway = Depends(get_llm_gateway)):
    await ws.accept()
    graph = build_graph(gateway)

    try:
        while True:
            data = await ws.receive_json()
            message = data.get("content", "")
            session_id = data.get("session_id", str(uuid.uuid4()))

            await ws.send_json({"type": "chat.processing", "session_id": session_id})

            initial_state = {
                "messages": [HumanMessage(content=message)],
                "intent": None,
                "agent_output": None,
                "memory_context": [],
                "session_id": session_id,
            }

            result = await graph.ainvoke(initial_state)

            response_text = ""
            for msg in reversed(result["messages"]):
                if isinstance(msg, AIMessage):
                    response_text = msg.content
                    break

            await ws.send_json({
                "type": "chat.complete",
                "content": response_text,
                "intent": result.get("intent", "general"),
                "session_id": session_id,
            })
    except WebSocketDisconnect:
        pass
