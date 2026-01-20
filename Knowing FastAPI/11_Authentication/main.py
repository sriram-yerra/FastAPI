'''
Request JSON
        ↓
CreateUser (validated)
        ↓ model_dump()
converts to dictonery
        ↓ ** unpacking
User (DB model)
'''

from fastapi import FastAPI, Depends, HTTPException, Form, File, UploadFile
from sqlmodel import SQLModel, create_engine, Session, select
from contextlib import asynccontextmanager, contextmanager
from typing import Annotated, Optional
from models import User, CreateUser, UpdateUser, loginUser, UserRead
from pydantic import EmailStr
import uuid
import os, shutil # shutil will upload the file in chunks to avoid server/system crash..!
from passlib.context import CryptContext

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
def get_session():
    with Session(engine) as session:
        yield session # Provides the session to FastAPI

# Annotated combines the "Type Hint" and "Dependency Injection"..!
SessionDep = Annotated[Session, Depends(get_session)]

pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

# Converting plain password to Hash..!
# async def hash_password(password: str) -> str:
#     return await pwd_context.hash(password)

# # Authentication, comparing the hashed pwd to the db password..!
# async def verified_password(plain: str, hashed: str) -> bool:
#     return await pwd_context.verify(plain, hashed)

def hash_password(password: str) -> str:
    if len(password.encode("utf-8")) > 72:
        raise HTTPException(
            status_code=400,
            detail="Password must be at most 72 characters"
        )
    return pwd_context.hash(password)

# Authentication, comparing the hashed pwd to the db password..!
def verified_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)

@app.post("/register", response_model=User)
# @app.post("/register", response_model=UserRead)
def register(
    session: SessionDep,
    user_data: CreateUser,
):
    # Getting unique user by using emial address..!
    user = session.exec(
        select(User).where(User.email == user_data.email)
        ).first()
    
    if user:
        raise HTTPException(status_code=400, detail="Bro..! Email already Exists..!")
    
    # new_user = User.model_validate(user_data) # this wont work for password included thing..!

    hash_pwd =   hash_password(user_data.password)
    # creating db model manually..!
    new_user = User(
        email=user_data.email, 
        name=user_data.name, 
        hashed_password=hash_pwd
    )

    session.add(new_user)
    session.commit()
    session.refresh(new_user)

    return new_user

@app.get("/users")
def get_users(session: SessionDep):
    users = session.exec(select(User)).all()
    return users

@app.post("/login")
def login(
    session: SessionDep,
    login_user: loginUser,
):
    # Fetching unique user by using emial address..!
    user = session.exec(
        select(User).where(User.email == login_user.email)
        ).first()
    
    if not user:
        raise HTTPException(status_code=400, detail="Bro..! Email doesnt Exists..! please register first..!")
    
    pwd = verified_password(login_user.password, user.hashed_password)

    if not pwd:
        raise HTTPException(status_code=400, detail="Bro..! Password isn't correct..!")

    return user
