from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from uuid import uuid4

from app import schemas, models
from app.database import SessionLocal

# Create a new router for the conversations API
router = APIRouter(
    prefix="/conversations",  # The prefix for all conversation-related routes
    tags=["conversations"],  # Group these routes under the 'conversations' tag in the docs
)


# Dependency to get the database session
def get_db():
    """Provides a new session for each request and closes it when done."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/", response_model=schemas.Conversation)
def create_conversation(conversation: schemas.ConversationCreate, db: Session = Depends(get_db)):
    """
    Create a new conversation. This generates a new UUID for the conversation and associates it with a user.

    Parameters:
    - conversation: ConversationCreate schema (which includes the user_id).
    - db: Database session.

    Returns:
    - The newly created conversation.
    """
    # Create a new conversation record with a generated UUID
    db_conversation = models.Conversation(
        id=str(uuid4()),  # Generate a unique identifier for the conversation
        user_id=conversation.user_id  # Assign the provided user_id
    )
    db.add(db_conversation)  # Add the new conversation to the session
    db.commit()  # Commit the transaction to the database
    db.refresh(db_conversation)  # Refresh the session to get the updated conversation object
    return db_conversation  # Return the created conversation


@router.get("/{conversation_id}", response_model=schemas.Conversation)
def get_conversations(conversation_id: str, db: Session = Depends(get_db)):
    """
    Retrieve a conversation by its ID.

    Parameters:
    - conversation_id: The ID of the conversation to retrieve.
    - db: Database session.

    Returns:
    - The conversation if found, otherwise raises a 404 error.
    """
    # Query the conversation by its ID
    conversation = db.query(models.Conversation).filter(models.Conversation.id == conversation_id).first()
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return conversation  # Return the retrieved conversation


@router.get("/{conversation_id}/messages", response_model=schemas.MessagePagination)
def get_messages(
    conversation_id: str,
    page: int = Query(1, ge=1),  # Pagination starts at page 1, minimum value 1
    size: int = Query(10, ge=1, le=100),  # Page size between 1 and 100, default is 10
    db: Session = Depends(get_db)
):
    """
    Get paginated messages from a conversation.

    Parameters:
    - conversation_id: The ID of the conversation.
    - page: The current page number (default: 1).
    - size: The number of messages per page (default: 10, max: 100).
    - db: Database session.

    Returns:
    - A paginated list of messages.
    """
    # Calculate the offset for the pagination
    skip = (page - 1) * size
    # Count total messages in the conversation
    total = db.query(models.Message).filter(models.Message.conversation_id == conversation_id).count()
    # Query the messages for the given conversation, sorted by creation date in descending order
    messages = (
        db.query(models.Message)
        .filter(models.Message.conversation_id == conversation_id)
        .order_by(models.Message.created_at.desc())  # Newest messages first
        .offset(skip)  # Skip messages based on the current page
        .limit(size)  # Limit the number of messages retrieved
        .all()
    )
    # Return the paginated response with the total count and messages
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
    """
    Send a new message in a conversation.

    Parameters:
    - conversation_id: The ID of the conversation.
    - message: The message content and sender details.
    - db: Database session.

    Returns:
    - The newly created message.
    """
    # Check if the conversation exists
    conversation = db.query(models.Conversation).filter(models.Conversation.id == conversation_id).first()
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    # Create the new message with a generated UUID and link it to the conversation
    db_message = models.Message(
        id=str(uuid4()),  # Generate a unique identifier for the message
        conversation_id=conversation_id,  # Link the message to the conversation
        sender=message.sender,  # Set the sender of the message
        content=message.content  # Set the message content
    )
    db.add(db_message)  # Add the message to the session
    db.commit()  # Commit the transaction
    db.refresh(db_message)  # Refresh to get the updated message object
    return db_message  # Return the created message


@router.put("/{conversation_id}/messages/{message_id}", response_model=schemas.Message)
def edit_message(
    conversation_id: str,
    message_id: str,
    message_update: schemas.MessageUpdate,
    db: Session = Depends(get_db)
):
    """
    Edit a user-sent message.

    Parameters:
    - conversation_id: The ID of the conversation.
    - message_id: The ID of the message to be edited.
    - message_update: The new content of the message.
    - db: Database session.

    Returns:
    - The updated message if successful, or raises a 404 error if the message cannot be found or edited.
    """
    # Query the message, ensuring it belongs to the user and the conversation
    message = db.query(models.Message).filter(
        models.Message.id == message_id,
        models.Message.conversation_id == conversation_id,
        models.Message.sender == schemas.SenderEnum.user  # Ensure the message is user-sent
    ).first()
    if not message:
        raise HTTPException(status_code=404, detail="Message not found or cannot be edited")

    # Update the message content if provided
    if message_update.content is not None:
        message.content = message_update.content

    db.commit()  # Commit the changes to the database
    db.refresh(message)  # Refresh to get the updated message object
    return message  # Return the updated message


@router.delete("/{conversation_id}/messages/{message_id}", status_code=204)
def delete_message(
    conversation_id: str,
    message_id: str,
    db: Session = Depends(get_db)
):
    """
    Delete a user-sent message.

    Parameters:
    - conversation_id: The ID of the conversation.
    - message_id: The ID of the message to be deleted.
    - db: Database session.

    Returns:
    - Status 204 No Content if successful, or raises a 404 error if the message cannot be found or deleted.
    """
    # Query the message, ensuring it belongs to the user and the conversation
    message = db.query(models.Message).filter(
        models.Message.id == message_id,
        models.Message.conversation_id == conversation_id,
        models.Message.sender == schemas.SenderEnum.user  # Ensure the message is user-sent
    ).first()
    if not message:
        raise HTTPException(status_code=404, detail="Message not found or cannot be deleted")

    db.delete(message)  # Delete the message from the database
    db.commit()  # Commit the transaction
    return  # Return with no content (204)
