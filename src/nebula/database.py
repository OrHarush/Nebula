from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from nebula.config import DB_PATH

# 1. DB_PATH comes from config.py, so it is the same no matter where the server is started from

# 2. Automatically create the 'data/' folder if it doesn't exist yet so SQLite doesn't crash trying to save there
DB_PATH.parent.mkdir(parents=True, exist_ok=True)

# 3. Create the standard SQLite connection URL string that SQLAlchemy requires (e.g., sqlite:///data/database.db)
SQLALCHEMY_DATABASE_URL = f"sqlite:///{DB_PATH}"

# 4. Initialize the SQLAlchemy engine.
# 'connect_args={"check_same_thread": False}' is a special SQLite setting:
# It tells SQLite to allow multiple threads (like FastAPI's background workers and web requests) to talk to the database safely.
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# 5. Create a factory for database sessions. Every time an API request comes in, it will use this to open a temporary session.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 6. Create the base class for your database models. Your tables will inherit from this 'Base'.
class Base(DeclarativeBase):
    pass

def get_db():
    """FastAPI dependency that provides a fresh database session per request and closes it when done."""
    db = SessionLocal()
    try:
        yield db  # Hand the database session to the API endpoint
    finally:
        db.close()  # Always close the connection when the request finishes, even if an error occurs