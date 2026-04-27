from pydantic import BaseModel


class ChatRequest(BaseModel):
    message: str
    session_id: str = "default"
    model: str = "default"
    stream: bool = False


class ChatResponse(BaseModel):
    response: str
    session_id: str
    model: str


class HealthResponse(BaseModel):
    status: str
    ollama: bool
    version: str = "0.1.0"
