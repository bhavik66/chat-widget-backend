import socketio
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app import models, schemas
from uuid import uuid4
from app.utils.chatbot_logic import generate_ai_response
import asyncio
from fastapi.encoders import jsonable_encoder

# Initialize Socket.IO server with ASGI integration
sio = socketio.AsyncServer(async_mode='asgi', cors_allowed_origins='*')
sio_app = socketio.ASGIApp(sio)


# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@sio.event
async def connect(sid, environ):
    print(f"Client connected: {sid}")


@sio.event
async def disconnect(sid):
    print(f"Client disconnected: {sid}")


@sio.event
async def join_conversation(sid, data):
    """
    Handle a client joining a conversation room.
    Expected data format:
    {
        "conversationId": "unique_conversation_id"
    }
    """
    conversation_id = data.get('conversationId')
    if conversation_id:
        await sio.enter_room(sid, conversation_id)
        print(f"Client {sid} joined conversation {conversation_id}")
    else:
        await sio.emit('error', {'message': 'conversationId is required'}, to=sid)


@sio.event
async def leave_conversation(sid, data):
    """
    Handle a client leaving a conversation room.
    Expected data format:
    {
        "conversationId": "unique_conversation_id"
    }
    """
    conversation_id = data.get('conversationId')
    if conversation_id:
        await sio.leave_room(sid, conversation_id)
        print(f"Client {sid} left conversation {conversation_id}")
    else:
        await sio.emit('error', {'message': 'conversationId is required'}, to=sid)


@sio.event
async def typing(sid, data):
    """
    Handle typing events.
    Expected data format:
    {
        "conversationId": "unique_conversation_id",
        "isTyping": true/false
    }
    """
    conversation_id = data.get('conversationId')
    is_typing = data.get('isTyping')
    if conversation_id is not None and is_typing is not None:
        # Broadcast typing status to other clients in the room
        await sio.emit(
            'typing',
            {'userId': sid, 'isTyping': is_typing},
            room=conversation_id,
            skip_sid=sid  # Optionally skip the sender
        )
        print(f"Client {sid} typing in conversation {conversation_id}: {is_typing}")
    else:
        await sio.emit('error', {'message': 'conversationId and isTyping are required'}, to=sid)


@sio.event
async def send_message(sid, data):
    """
    Handle incoming messages from clients.
    Expected data format:
    {
        "conversationId": "unique_conversation_id",
        "content": "message content"
    }
    """
    conversation_id = data.get('conversationId')
    content = data.get('content')

    if not conversation_id or not content:
        await sio.emit('error', {'message': 'conversationId and content are required'}, to=sid)
        return

    # Create a new DB session
    db: Session = SessionLocal()
    try:
        # Create and save user message
        user_message = models.Message(
            id=str(uuid4()),
            conversation_id=conversation_id,
            sender=schemas.SenderEnum.user,
            content=content
        )
        db.add(user_message)
        db.commit()
        db.refresh(user_message)

        # Broadcast user message to the room
        await sio.emit(
            'new_message',
            jsonable_encoder(schemas.Message.from_orm(user_message)),
            room=conversation_id
        )
        print(f"Broadcasted message from {sid} in conversation {conversation_id}")

        # Notify others that AI is typing
        await sio.emit(
            'typing',
            {'userId': 'ai', 'isTyping': True},
            room=conversation_id,
            skip_sid=None  # Notify all including AI if needed
        )

        # Generate AI response (simulate delay for typing effect)
        ai_response = await asyncio.to_thread(generate_ai_response, content)
        await asyncio.sleep(1)  # Simulate typing delay

        # Create and save AI message
        ai_message = models.Message(
            id=str(uuid4()),
            conversation_id=conversation_id,
            sender=schemas.SenderEnum.ai,
            content=ai_response.get("content")
        )
        db.add(ai_message)
        db.commit()
        db.refresh(ai_message)

        # Notify others that AI has stopped typing
        await sio.emit(
            'typing',
            {'userId': 'ai', 'isTyping': False},
            room=conversation_id
        )

        # Broadcast AI message to the room
        await sio.emit(
            'new_message',
            {
                **jsonable_encoder(schemas.Message.from_orm(ai_message)),
                "actions": ai_response.get('actions')
            },
            room=conversation_id
        )
        print(f"Broadcasted AI message in conversation {conversation_id}")

    except Exception as e:
        print(f"Error handling message from {sid}: {e}")
        await sio.emit('error', {'message': 'Internal server error'}, to=sid)
    finally:
        db.close()
