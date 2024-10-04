# app/schemas.py

from typing import List, Optional, Dict
from pydantic import BaseModel
from enum import Enum
from datetime import datetime


class SenderEnum(str, Enum):
    ai = "ai"
    user = "user"


class MessageBase(BaseModel):
    sender: SenderEnum
    content: str


class MessageCreate(MessageBase):
    pass


class MessageUpdate(BaseModel):
    content: Optional[str] = None


class Message(MessageBase):
    id: str
    conversation_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class ConversationBase(BaseModel):
    user_id: str


class ConversationCreate(ConversationBase):
    pass


class Conversation(ConversationBase):
    id: str
    created_at: datetime
    messages: List[Message] = []

    class Config:
        orm_mode = True


class MessagePagination(BaseModel):
    messages: List[Message]
    total: int
    page: int
    size: int
