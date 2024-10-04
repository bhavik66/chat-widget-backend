from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Database URL: SQLite database stored in the `./db/` directory under the file `chatbot.db`
# For other databases (PostgreSQL, MySQL, etc.), you would replace the URL accordingly.
DATABASE_URL = "sqlite:///./db/chatbot.db"

# Create a database engine
# `check_same_thread=False` is specific to SQLite and allows the use of the same connection across different threads.
# This is required when using SQLite in multi-threaded applications (like FastAPI) to avoid errors.
engine = create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}
)

# Create a configured "SessionLocal" class, a factory for session objects
# Session objects are used to interact with the database during a request and automatically close after the request is done.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create a base class for models to inherit from, using SQLAlchemy's `declarative_base`
# This is needed to define models that map to database tables.
Base = declarative_base()
