from fastapi import FastAPI, Depends, HTTPException, Form, File, UploadFile, APIRouter
from sqlmodel import SQLModel, create_engine, Session, select
from typing import Annotated, Optional
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestFormStrict
from app.models.user_model import User
from app.dependancies import get_current_user, SessionDep
from app.schemas.user_schema import CreateUser, UpdateUser, loginUser, UserRead, Token
from app.auth import hash_password, verified_password, create_acess_token

router = APIRouter()

@router.post("/register", response_model=User)
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

@router.get("/users")
def get_users(session: SessionDep):
    users = session.exec(select(User)).all()
    if not users:
        raise HTTPException( status_code=401, detail="No users found..!")
    return users

@router.post("/login", response_model=Token)
def login(
    session: SessionDep,
    # login_user: loginUser,
    form_data: Annotated[OAuth2PasswordRequestFormStrict, Depends()]
):
    # Fetching unique user by using emial address..!
    user = session.exec(
        select(User).where(User.email == form_data.username)
        ).first()
    
    if not user:
        raise HTTPException(status_code=400, detail="Bro..! Email doesnt Exists..! please register first..!")
    
    pwd = verified_password(form_data.password, user.hashed_password)

    if not pwd:
        raise HTTPException(status_code=400, detail="Bro..! Password isn't correct..!")

    token = create_acess_token(data={"sub": user.email})
    return {"access_token": token, "token_type": "bearer"}

@router.get("/profile")
def profile(current_user: Annotated[User, Depends(get_current_user)]):
    return  {"name": current_user, "email": current_user.email}
