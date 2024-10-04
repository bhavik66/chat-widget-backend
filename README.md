
# FastAPI Chatbot API

This project is a FastAPI-based chatbot API that supports both REST and WebSocket communication. The API allows users to create conversations, send messages, and retrieve conversations or messages with pagination support. It is designed to handle chat-based interactions and can be extended with AI or other processing mechanisms.

## Features
- **REST API** for conversations and messages
- **WebSocket support** for real-time communication
- **Message Pagination** for efficient data retrieval
- **SQLite** as the default database (can be easily swapped with other databases)
- **Cross-Origin Resource Sharing (CORS)** for handling requests from external domains

## Project Structure
```
app/
│
├── main.py           # Entry point for the FastAPI application
├── database.py       # Database configuration and session management
├── models.py         # SQLAlchemy models for Conversation and Message
├── schemas.py        # Pydantic schemas for request validation and response formatting
├── routers/
│   ├── messages.py   # Routes for handling conversations and messages
│   ├── health.py     # Health check routes
│   ├── websocket.py  # WebSocket routes for real-time chat
├── utils/
│   ├── chatbot_logic.py   # Chat bot logic for AI reply
└── db/
    └── chatbot.db    # SQLite database file (auto-created)
```

## Requirements

- Python 3.7+
- FastAPI
- SQLAlchemy
- SQLite (default)
- Uvicorn (for running the ASGI app)

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/your-repo/fastapi-chatbot.git
   cd fastapi-chatbot
   ```

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Run the application:

   ```bash
   uvicorn app.main:app --reload
   ```

   This command starts the application with automatic reloading enabled. The API will be available at `http://localhost:8000`.

## Endpoints

### Conversations

- **Create a Conversation**:  
  `POST /conversations/`  
  Body:  
  ```json
  {
    "user_id": "string"
  }
  ```

- **Get a Conversation**:  
  `GET /conversations/{conversation_id}`

- **Get Paginated Messages**:  
  `GET /conversations/{conversation_id}/messages?page=1&size=10`

- **Send a Message**:  
  `POST /conversations/{conversation_id}/messages`  
  Body:  
  ```json
  {
    "sender": "user or ai",
    "content": "Hello, this is a message."
  }
  ```

- **Edit a Message**:  
  `PUT /conversations/{conversation_id}/messages/{message_id}`  
  Body:  
  ```json
  {
    "content": "Updated content"
  }
  ```

- **Delete a Message**:  
  `DELETE /conversations/{conversation_id}/messages/{message_id}`

### Health Check

- **Health Check**:  
  `GET /health/`

### WebSocket

- **WebSocket Connection**:  
  Mounts on the root path `/`. Connect via a WebSocket client (e.g., in the browser or Postman) to handle real-time messaging.

## Database Configuration

By default, the application uses SQLite. The database file is located in the `./db/chatbot.db` directory. If you need to switch to another database (like PostgreSQL or MySQL), update the `DATABASE_URL` in `app/database.py`:

```python
DATABASE_URL = "postgresql://user:password@localhost/dbname"
```

Ensure the necessary database drivers are installed, for example:

```bash
pip install psycopg2  # for PostgreSQL
pip install pymysql   # for MySQL
```

## Detailed Explanation of Code

### 1. **`main.py`**
   This is the entry point of the application. It defines the FastAPI app, sets up CORS middleware, and mounts the WebSocket functionality. It also includes the routers for handling REST API routes for conversations, messages, and health checks.

### 2. **`database.py`**
   Handles the database connection setup using SQLAlchemy. It defines the `engine`, `SessionLocal` for database sessions, and `Base` for model inheritance.

### 3. **`models.py`**
   Contains SQLAlchemy models for `Conversation` and `Message`:
   - **Conversation**: Represents a chat session between the user and AI.
   - **Message**: Stores individual messages in a conversation, including details like the sender, content, and timestamps.

### 4. **`schemas.py`**
   Defines Pydantic schemas for data validation and serialization. It includes:
   - **Conversation and Message schemas** for validating input and formatting output.
   - **Pagination support** for retrieving messages in a paginated format.

### 5. **`routers/messages.py`**
   Implements the logic for CRUD operations on conversations and messages. This includes:
   - Creating and retrieving conversations
   - Sending, editing, and deleting messages
   - Pagination support for message retrieval

### 6. **`routers/websocket.py`**
   Implements WebSocket routes for real-time communication between users and the chatbot. This file manages:
   - Establishing WebSocket connections to enable two-way communication.
   - Handling incoming messages from users in real time.
   - Broadcasting or sending responses back to the users.
   - It integrates WebSocket functionalities seamlessly with the FastAPI application, allowing for a live, continuous flow of chat interactions.

### 7. **`utils/chatbot_logic.py`**
   This file contains the core logic that powers the chatbot's responses and interactions. It typically includes:
   - **AI Response Generation**: Logic for generating or fetching chatbot responses based on user input. This could involve calling external APIs or services to generate responses (e.g., NLP models).
   - **Message Processing**: Handles the logic for interpreting and processing incoming messages from users, such as understanding the context and maintaining conversation flow.
   - **Business Logic**: Implements any specific rules or logic tied to how the chatbot should behave, including custom responses, triggers, or actions based on the conversation state.
   - **Integration**: This file likely serves as the bridge between the real-time WebSocket interactions and the message-handling API, providing an AI-driven experience.

## CORS Configuration

The app allows cross-origin requests by default. To modify this, edit the `origins` list in `main.py`. For example, restrict access to specific domains:

```python
origins = [
    "http://localhost",  # Allow localhost during development
    "https://your-production-domain.com"  # Allow production domain
]
```

## Running in Production

For production deployment, you may want to use a production-grade ASGI server like `gunicorn`:

```bash
pip install gunicorn
gunicorn -k uvicorn.workers.UvicornWorker app.main:app
```

Also, for production, you should replace SQLite with a more scalable database like PostgreSQL or MySQL, and implement proper database migrations using a tool like Alembic.