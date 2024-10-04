# app/routers/messages.py

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import uuid4

from app import schemas, models
from app.database import SessionLocal
from app.utils.chatbot_logic import generate_ai_response

router = APIRouter(
    prefix="/conversations",
    tags=["conversations"],
)


# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/", response_model=schemas.Conversation)
def create_conversation(conversation: schemas.ConversationCreate, db: Session = Depends(get_db)):
    db_conversation = models.Conversation(
        id=str(uuid4()),
        user_id=conversation.user_id
    )
    db.add(db_conversation)
    db.commit()
    db.refresh(db_conversation)
    return db_conversation


@router.get("/{conversation_id}", response_model=schemas.Conversation)
def get_conversations(conversation_id: str, db: Session = Depends(get_db)):
    conversations = db.query(models.Conversation).filter(models.Conversation.id == conversation_id).first()
    return conversations


@router.get("/{conversation_id}/messages", response_model=schemas.MessagePagination)
def get_messages(
        conversation_id: str,
        page: int = Query(1, ge=1),
        size: int = Query(10, ge=1, le=100),
        db: Session = Depends(get_db)
):
    skip = (page - 1) * size
    total = db.query(models.Message).filter(models.Message.conversation_id == conversation_id).count()
    messages = (
        db.query(models.Message)
        .filter(models.Message.conversation_id == conversation_id)
        .order_by(models.Message.created_at.desc())
        .offset(skip)
        .limit(size)
        .all()
    )
    return schemas.MessagePagination(
        messages=messages,
        total=total,
        page=page,
        size=size
    )


@router.post("/{conversation_id}/messages", response_model=schemas.Message)
def send_message(
        conversation_id: str,
        message: schemas.MessageCreate,
        db: Session = Depends(get_db)
):
    # Verify conversation exists
    conversation = db.query(models.Conversation).filter(models.Conversation.id == conversation_id).first()
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    # Create user message
    db_message = models.Message(
        id=str(uuid4()),
        conversation_id=conversation_id,
        sender=message.sender,
        content=message.content,
    )
    db.add(db_message)
    db.commit()
    db.refresh(db_message)

    # If user sent a message, generate AI response
    # if message.sender == schemas.SenderEnum.user:
    #     ai_response = generate_ai_response(message.content)
    #     ai_content = ai_response.get("content")
    #     ai_message = models.Message(
    #         id=str(uuid4()),
    #         conversation_id=conversation_id,
    #         sender=schemas.SenderEnum.ai,
    #         content=ai_content,
    #     )
    #     db.add(ai_message)
    #     db.commit()
    #     db.refresh(ai_message)
    #     return ai_message  # Optionally, return both messages or handle differently

    return db_message


@router.put("/{conversation_id}/messages/{message_id}", response_model=schemas.Message)
def edit_message(
    conversation_id: str,
    message_id: str,
    message_update: schemas.MessageUpdate,
    db: Session = Depends(get_db)
):
    message = db.query(models.Message).filter(
        models.Message.id == message_id,
        models.Message.conversation_id == conversation_id,
        models.Message.sender == schemas.SenderEnum.user
    ).first()
    if not message:
        raise HTTPException(status_code=404, detail="Message not found or cannot be edited")

    if message_update.content is not None:
        message.content = message_update.content

    db.commit()
    db.refresh(message)
    return message


@router.delete("/{conversation_id}/messages/{message_id}", status_code=204)
def delete_message(
    conversation_id: str,
    message_id: str,
    db: Session = Depends(get_db)
):
    message = db.query(models.Message).filter(
        models.Message.id == message_id,
        models.Message.conversation_id == conversation_id,
        models.Message.sender == schemas.SenderEnum.user
    ).first()
    if not message:
        raise HTTPException(status_code=404, detail="Message not found or cannot be deleted")

    db.delete(message)
    db.commit()
    return
