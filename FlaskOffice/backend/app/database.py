from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session

# Use only SQLite database
# This will create/use a users.db file in the backend directory
DATABASE_URL = "sqlite:///./users.db"

db = SQLAlchemy()

engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = scoped_session(sessionmaker(bind=engine, autocommit=False, autoflush=False))


def create_tables_database(app):
    """Create all database tables"""
    with app.app_context():
        db.create_all()
    return True


def get_session():
    """Get database session"""
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
