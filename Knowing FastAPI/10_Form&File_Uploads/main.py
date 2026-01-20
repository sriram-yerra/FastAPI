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
from models import User, CreateUser, UpdateUser, EmailStr
import uuid
import os, shutil # shutil will upload the file in chunks to avoid server/system crash..!

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

UPLOAD_DIRS = "uploads"
os.makedirs(UPLOAD_DIRS, exist_ok=True)

@app.post("/createuser")
def UserCreate(
    session: SessionDep,
    name: str = Form(...),
    phone: int = Form(...),
    email: EmailStr = Form(...),
    file: UploadFile = File(...)
):
    user_data = {"name" : name, "phone" : phone, "email" : email}
    validated = CreateUser.model_validate(user_data)

    unique_name = f"{uuid.uuid4()}_{file.filename}"
    file_path = os.path.join(UPLOAD_DIRS, unique_name)
    with open(file_path, 'wb') as f:
        shutil.copyfileobj(file.file, f)

    # validate the input user details, unpacks to json and dump into User db structure..!
    user = User(**validated.model_dump(), file_path=f"{UPLOAD_DIRS}/{file.filename}") # "**" is to convert back to dict format from class format

    session.add(user)
    session.commit()
    session.refresh(user)

    return user

@app.get("/users", response_model=list[User])
def get_users(session: SessionDep):
    users = session.exec(
        select(User)
        ).all()
    if not users:
        raise HTTPException(status_code=404, detail="Useer Not Found Error..!")
    return users    

# PUT replaces the whole object..!
@app.put("/user/{user_id}", response_model=User)
async def update_user(
    user_id: int,
    session: SessionDep,
    name: str = Form(...),
    phone: int = Form(...),
    email: EmailStr = Form(...),
    file: UploadFile = File(...),
):
    db_user = session.get(User, user_id)

    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    db_user.name = name
    db_user.phone = phone
    db_user.email = email
    
    if file:
        unique_name = f"{uuid.uuid4()}_{file.filename}"
        file_path = os.path.join(UPLOAD_DIRS, unique_name)

        with open(file_path, "wb") as f:
            shutil.copyfileobj(file.file, f)

        db_user.file_path = file.filename

    session.commit()
    session.refresh(db_user)
    return db_user

# PATCH updates the required fields by the user..!
@app.patch("/user/{user_id}", response_model=User)
def update_user_partial(
    user_id: int,
    session: SessionDep,
    name: Optional[str] = Form(None),
    phone: Optional[int] = Form(None),
    email: Optional[EmailStr] = Form(None),
    file: Optional[UploadFile] = File(None),
):
    db_user = session.get(User, user_id)

    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    # Update only provided fields
    if name is not None:
        db_user.name = name
    if phone is not None:
        db_user.phone = phone
    if email is not None:
        db_user.email = email

    # Update file only if provided
    if file is not None:
        # Delete the old file and then update the new file
        if db_user.file_path:
            old_path = os.path.join(UPLOAD_DIRS, db_user.file_path)
            if os.path.exists(old_path):
                os.remove(old_path)

        unique_name = f"{uuid.uuid4()}_{file.filename}"
        file_path = os.path.join(UPLOAD_DIRS, unique_name)
        with open(file_path, "wb") as f:
            shutil.copyfileobj(file.file, f)

        db_user.file_path = file.filename

    session.commit()
    session.refresh(db_user)

    return db_user

# @app.delete("/user/{user_id}", response_model=list[User])
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

    current_users = session.exec(select(User)).all()

    return current_users

