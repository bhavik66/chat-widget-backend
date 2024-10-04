from typing import List, Optional
from pydantic import BaseModel
from enum import Enum
from datetime import datetime


# Enum for identifying the sender of a message (either AI or user)
class SenderEnum(str, Enum):
    ai = "ai"  # AI-sent message
    user = "user"  # User-sent message


# Base schema for messages, shared across various message-related schemas
class MessageBase(BaseModel):
    sender: SenderEnum  # Identifies who sent the message (AI or user)
    content: str  # The content of the message (text)


# Schema for creating a new message
class MessageCreate(MessageBase):
    pass  # Inherits all fields from MessageBase, no additional fields needed


# Schema for updating an existing message
class MessageUpdate(BaseModel):
    content: Optional[str] = None  # Allows optional updating of the message content


# Schema representing a full message, including database-specific fields like `id`, `conversation_id`, and timestamps
class Message(MessageBase):
    id: str  # Unique identifier of the message
    conversation_id: str  # The ID of the conversation to which this message belongs
    created_at: datetime  # Timestamp for when the message was created
    updated_at: datetime  # Timestamp for when the message was last updated

    # Config class to allow Pydantic to work with ORM objects (SQLAlchemy models)
    class Config:
        orm_mode = True


# Base schema for conversations, shared across various conversation-related schemas
class ConversationBase(BaseModel):
    user_id: str  # The ID of the user involved in the conversation


# Schema for creating a new conversation
class ConversationCreate(ConversationBase):
    pass  # Inherits all fields from ConversationBase, no additional fields needed


# Schema representing a full conversation, including the `id`, `created_at`, and associated messages
class Conversation(ConversationBase):
    id: str  # Unique identifier of the conversation
    created_at: datetime  # Timestamp for when the conversation was created
    messages: List[Message] = []  # List of messages associated with this conversation (defaults to an empty list)

    # Config class to allow Pydantic to work with ORM objects (SQLAlchemy models)
    class Config:
        orm_mode = True


# Schema for paginating messages in a conversation
class MessagePagination(BaseModel):
    messages: List[Message]  # List of messages for the current page
    total: int  # Total number of messages in the conversation
    page: int  # The current page number
    size: int  # Number of messages per page
