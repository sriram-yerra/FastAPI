from collections.abc import AsyncGenerator
import uuid

from sqlalchemy import Column, String, Text, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, relationship
from datetime import datetime
from fastapi_users.db import SQLAlchemyUserDatabase, SQLAlchemyBaseUserTableUUID
from fastapi import Depends

DATABASE_URL = "sqlite+aiosqlite:///./test.db"

'''
These two lines are foundational to how SQLAlchemy + FastAPI Users work together.
'''
'''
- DeclarativeBase is SQLAlchemy’s base class for ORM models.
- Base = blueprint registry for all database tables
- Why we create our own Base?
    All models must share the same metadata
    Base.metadata is used to:
        - Base.metadata.create_all(engine)

    SQLAlchemy discovers all tables via this Base
'''
class Base(DeclarativeBase):
    pass

'''
It comes from fastapi-users. A preBuilt "SQLAlchemy" "ORM model", Which Contains some feilds like:
- id (UUID primary key)
- email
- hashed_password
- is_active
- is_superuser
- is_verified
'''
'''
But why Inheriting 2 Classes?
    1. SQLAlchemyBaseUserTableUUID : User fields & auth logic
    2. Base                        : Registers table with SQLAlchemy
'''
class User(SQLAlchemyBaseUserTableUUID, Base): # Multiple Inheritance..!
    '''
    This creates a one-to-many relationship:
        User → many Posts
        Post → one User
    '''
    posts = relationship("Post", back_populates="user")

'''
This Crates the schema for the Database table
'''
class Post(Base):
    __tablename__ = "posts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("user.id"), nullable=False)
    caption = Column(Text)
    url = Column(String, nullable=False)
    file_type = Column(String, nullable=False)
    file_name = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="posts")

'''
Engine = gateway between your app and the database
This is the core to async database usage in FastAPI.
An Engine is the Connection manager to the DataBase.
'''
'''
Why create_async_engine?

Because: FastAPI is "async"
For Instance:
Normal create_engine() is blocking
create_async_engine() is non-blocking
So, while the DB is responding:
your app can handle other requests
'''
engine = create_async_engine(DATABASE_URL)
async_session_maker = async_sessionmaker(engine, expire_on_commit=False)

'''
This function is used to create database tables asynchronously.
Using async prevents blocking FastAPI’s event loop.
'''
'''
Call function
    ↓
Open async DB connection
    ↓
Begin transaction
    ↓
Run synchronous table creation
    ↓
Commit transaction
    ↓
Close connection
'''
async def create_db_and_tables():
    # Opens a DB Connecion and "starts" a transaction, automatically "commits", "rolls back" and "Closes" the connection.
    async with engine.begin() as conn:
        # Run this synchronous function safely inside an async context.
        await conn.run_sync(Base.metadata.create_all)

'''
This function provides a database session per request in an async-safe way.
Give me a DB session for this request, and clean it up afterward.
The function yields an "AsyncSession", It does not return a final value.
'''
async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session

'''
This function is a FastAPI dependency used specifically with fastapi-users to: 
provide a "user database adapter" backed by "SQLAlchemy async sessions".
'''
'''
This is a dependency generator that:
    Receives an async SQLAlchemy session
    Wraps it inside SQLAlchemyUserDatabase
    Yields it to FastAPI Users
    Cleans up automatically after the request

Think of it as:
    “Give FastAPI-Users a DB interface to manage users for this request.”
'''
async def get_user_db(session: AsyncSession = Depends(get_async_session)):
    yield SQLAlchemyUserDatabase(session, User)