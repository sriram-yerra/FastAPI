'''
Compatible Databases:
FastAPI supports multiple databases through ORMs like SQLAlchemy and SQLModel, allowing easy interaction with relational databases.

Popular Supported Databases:
    SQLite
    PostgreSQL
    MySQL / MariaDB
    Microsoft SQL Server
    Oracle and others

Why this matters:
    You can switch databases without changing your API logic
    ORMs handle SQL queries using Python objects
    Works well with async and sync database drivers

About SQLModel:
    Combines Pydantic and SQLAlchemy
    Uses one model for database tables and API schemas
    Simplifies table definitions, request handling, and responses
'''
'''
Depends(get_session):
Tells FastAPI:
    “Call get_session() before running the endpoint”
    “Inject its yielded value into the endpoint”
    “Clean it up after request ends”
'''
'''
SessionDep = Annotated[Session, Depends(get_session)]
Annotated combines:
    1. Type hint (Session)
    2. Dependency injection (Depends(get_session))
This allows cleaner endpoint signatures.
'''
'''
yield:
    Provides the session to FastAPI
    After the request is completed:
    code after yield (if any) would run
    session is cleaned up automatically
'''
'''
response_model=list[User]: Tells FastAPI what the response should look like
SessionDep: Injects a database session
'''
'''
users = session.exec(select(User)).all()
Step-by-step:
    select(User) builds an SQL query
    session.exec(...) runs the query
    .all() fetches all rows as a list of User objects
'''

from fastapi import FastAPI, Depends, HTTPException
from sqlmodel import SQLModel, create_engine, Session, select
from contextlib import asynccontextmanager, contextmanager
from typing import Annotated
from models import User, CreateUser

DATABASE_URL = "sqlite:///./users.db"
engine = create_engine(DATABASE_URL, echo=True)

# This is an Event Handler..!
@asynccontextmanager
async def lifespan(app: FastAPI):
    SQLModel.metadata.create_all(engine)
    yield # app runs here
 
# Initialising FastAPI with lifespan constructor..!
app = FastAPI(lifespan=lifespan)

# This function creates a database session and safely closes it after use.
async def get_session():
    with Session(engine) as session:
        yield session # Provides the session to FastAPI

# Annotated combines the "Type Hint" and "Dependency Injection"..!
SessionDep = Annotated[Session, Depends(get_session)]

@app.post("/create_user", response_model=User)
def create_user(user: CreateUser, session: SessionDep):
    new_user = User.model_validate(user)
    # new_user = User(**user.model_dump())
    session.add(new_user)
    session.commit()
    session.refresh(new_user)
    return new_user

'''
response_model=list[User] --> for fetching multiple users --> uses "all()"
response_model=User       --> for fetching single user    --> uses "first()"
'''
@app.get("/users", response_model=list[User])
def get_users(session: SessionDep):
    users = session.exec(
        select(User)
        ).all()
    if not users:
        raise HTTPException(status_code=404, detail="Useer Not Found Error..!")
    return users

@app.get("/users/{user_id}", response_model=User)
def get_users(user_id: int, session: SessionDep):
    # user = session.exec(
    #     select(User).where(User.id == user_id)
    #     ).first()
    user = session.get(User, user_id)

    if not user:
        raise HTTPException(status_code=404, detail="Useer Not Found Error..!")
    return user

@app.put("/user/{user_id}", response_model=User)
async def update_user(user_id: int, user_data: CreateUser, session: SessionDep):
    # user_update = User.model_validate(user) # Wrong because the new data should be validate, but not the existing one..!
    # session.add(users) # add() is for new objects, not for the existing object attached to the session..!

    # Fetch the existing user:
    # db_user = session.exec(
    #     select(User).where(User.id == user_id)
    #     ).first()
    db_user = session.get(User, user_id)

    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Updating the user
    db_user.name = user_data.name
    db_user.phone = user_data.phone
    db_user.email = user_data.email

    session.commit()
    session.refresh(db_user)

    # return {"Message": "Updated user", "User" : db_user} 
    # Error due to mismatch of User Object structure (Expects only the User Structure)
    return db_user

@app.delete("/user/{user_id}", response_model=list[User])
async def delete_user(user_id: int, session: SessionDep):
    # db_user = session.exec(
    #     select(User).where(User.id == user_id)
    #     ).first()
    db_user = session.get(User, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    # Deleting the user
    session.delete(db_user)
    session.commit()

    # The user is already deleted, so u cannot refresh the deleted ones..!
    # session.refresh(db_user) 

    current_users = session.exec(select(User)).all()

    return current_users

'''
What actually is session: SessionDep?
In simple words: "session is your connection + workspace for talking to the database."
Think of it as: “A temporary working area where you read, change, add, or delete database records safely.”

laymann Real-world analogy: Imagine a notebook:
    You open the notebook → session
    You write changes → session.add(), session.delete()
    You finalize changes → session.commit()
    You close the notebook → session ends automatically
'''
'''
What actually is session.delete(user)
session.delete(user) -> User is marked for deletion (not yet removed) -> session.commit() -> Row is deleted from database
'''
'''
Whole flow:
Request comes in
 ↓
Session is created
 ↓
User fetched
 ↓
session.delete(user)
 ↓
session.commit()
 ↓
User row removed from DB
 ↓
Session closed
'''