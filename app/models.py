from sqlalchemy import Column, String, ForeignKey, DateTime, Enum, Boolean, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.database import Base


# Enum for identifying the sender of a message (AI or user)
class SenderEnum(str, enum.Enum):
    ai = "ai"  # Message sent by AI
    user = "user"  # Message sent by the user


# Conversation model representing a conversation between the user and the AI
class Conversation(Base):
    __tablename__ = "conversations"  # Table name in the database

    # Columns
    id = Column(String, primary_key=True, index=True)  # Unique identifier for the conversation
    user_id = Column(String, index=True)  # ID of the user associated with the conversation
    created_at = Column(DateTime(timezone=True), server_default=func.now())  # Timestamp for when the conversation was created

    # Relationship to the Message model (One-to-Many: One conversation has many messages)
    # The `cascade="all, delete-orphan"` means that when a conversation is deleted, all its messages are also deleted.
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")


# Message model representing individual messages in a conversation
class Message(Base):
    __tablename__ = "messages"  # Table name in the database

    # Columns
    id = Column(String, primary_key=True, index=True)  # Unique identifier for the message
    conversation_id = Column(String, ForeignKey("conversations.id"))  # Foreign key to associate the message with a conversation
    sender = Column(Enum(SenderEnum))  # Identifies whether the message was sent by AI or the user
    content = Column(String)  # The actual content of the message (text)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)  # Timestamp for when the message was created
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)  # Timestamp for when the message was last updated

    # Relationship back to the Conversation model (Many-to-One: Many messages belong to one conversation)
    conversation = relationship("Conversation", back_populates="messages")
