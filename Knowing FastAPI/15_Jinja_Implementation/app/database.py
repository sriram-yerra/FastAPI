from fastapi import *
from sqlmodel import *

DATABASE_URL = "sqlite:///./users.db"
# DATABASE_URL= "postgresql://fastapi_user:1234@localhost:5432/fastapi_db"
engine = create_engine(DATABASE_URL, echo=True)

def create_tables_database():
    return SQLModel.metadata.create_all(engine)

# This function creates a database session and safely closes it after use.
def get_session():
    with Session(engine) as session:
        yield session # Provides the session to FastAPI