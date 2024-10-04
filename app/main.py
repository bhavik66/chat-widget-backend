# app/main.py

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import messages, health, websocket
from app.database import engine, Base

# Create all tables in the database. In production, use migrations instead.
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="FastAPI Chatbot",
    description="A chatbot API with REST and WebSocket support, including conversations and pagination.",
    version="1.1.0",
)

# Set up CORS (adjust origins as needed)
origins = [
    "http://localhost",
    "http://localhost:5173",
    # Add other origins if needed
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(messages.router)
app.include_router(health.router)

app.mount('/', app=websocket.sio_app)

if __name__ == '__main__':
    uvicorn.run('app.main:app', reload=True)
