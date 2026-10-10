from datetime import datetime

from pydantic import BaseModel

from app.schemas.common import ORMModel


class ChatRequest(BaseModel):
    message: str
    conversation_id: int | None = None


class ChatResponse(BaseModel):
    message: str
    conversation_id: int
    message_id: int
    used_memory: str = "letta"  # letta | gemini


class ConversationOut(ORMModel):
    id: int
    title: str
    updated_at: datetime | None


class MessageOut(ORMModel):
    id: int
    role: str
    content: str
    created_at: datetime | None