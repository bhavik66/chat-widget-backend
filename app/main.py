import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import messages, health, websocket
from app.database import engine, Base

# Automatically creates all tables in the database upon starting the application.
# In production, it's better to use migration tools like Alembic to manage database schema changes.
Base.metadata.create_all(bind=engine)

# Initialize FastAPI application
app = FastAPI(
    title="FastAPI Chatbot",  # The title of the API documentation
    description="A chatbot API with REST and WebSocket support, including conversations and pagination.",  # A short description of the API's functionality
    version="1.1.0",  # The version of the API
)

# Set up Cross-Origin Resource Sharing (CORS) settings to control access from other domains.
# This is necessary to allow frontend applications (or other clients) to communicate with the API.
# Modify the `origins` list to restrict which domains can access the API.
origins = [
    "http://localhost",  # Allow localhost for development
    "http://localhost:5173",  # Allow frontend apps running on a different port (e.g., Vite or other dev tools)
    # Add other origins as needed, such as your production frontend URL
]

# Add CORS middleware to the FastAPI app to handle cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],  # Allow requests from any origin. In production, you may want to restrict this.
    allow_credentials=True,  # Allow sending cookies or credentials with requests
    allow_methods=["*"],  # Allow all HTTP methods (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],  # Allow all HTTP headers
)

# Include the routes for handling messages and health checks
app.include_router(messages.router)  # Include the message-related routes
app.include_router(health.router)    # Include the health check routes

# Mount the WebSocket functionality on the root path.
# WebSockets provide real-time communication support for chat features.
# `sio_app` is assumed to be a Socket.IO server instance defined in the `websocket` module.
app.mount('/', app=websocket.sio_app)

# Entry point for running the application if executed directly
# if __name__ == '__main__':
#     # Use Uvicorn, an ASGI server, to run the FastAPI app. The `reload=True` option enables auto-reloading
#     # when changes are made to the code (useful during development).
#     uvicorn.run('app.main:app', reload=True)
