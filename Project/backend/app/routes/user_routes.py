from fastapi import FastAPI, Depends, HTTPException, Form, File, UploadFile, APIRouter
from sqlmodel import SQLModel, create_engine, Session, select
from typing import Annotated, Optional
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestFormStrict
from app.models.user_model import User, EmailOTP
from app.dependancies import get_current_user, SessionDep
from app.schemas.user_schema import CreateUser, OTPVerify, UpdateUser, loginUser, UserRead, Token
from app.auth import hash_password, verified_password, create_acess_token
import random
import smtplib
from email.message import EmailMessage
from datetime import datetime, timedelta, timezone
from app.emailverfication import generate_otp, send_otp_email


router = APIRouter()

@router.post("/request-otp")
def request_otp(user_data: CreateUser, session: SessionDep):
    if not user_data.email.endswith("@itspe.co.in"):
        raise HTTPException(status_code=400, detail="Company email only")

    otp = generate_otp()
    expiry = datetime.now(timezone.utc) + timedelta(minutes=2)

    otp_entry = EmailOTP(email=user_data.email, otp=otp, expires_at=expiry)
    session.add(otp_entry)
    session.commit()

    send_otp_email(user_data.email, otp)

    return {"message": "OTP sent to email"}

@router.post("/verify-otp")
def verify_otp(data: OTPVerify, session: SessionDep):
    record = session.exec(
        select(EmailOTP).where(EmailOTP.email == data.email)
    ).first()

    if not record:
        raise HTTPException(400, "OTP not requested")

    if datetime.utcnow() > record.expires_at:
        raise HTTPException(400, "OTP expired")

    if record.otp != data.otp:
        raise HTTPException(400, "Invalid OTP")

    hashed_pwd = hash_password(data.password)
    new_user = User(name=data.name, email=data.email, hashed_password=hashed_pwd)
    session.add(new_user)
    session.delete(record)
    session.commit()

    return {"message": "Registration successful"}

@router.post("/register", response_model=User)
# @app.post("/register", response_model=UserRead)
def register(
    session: SessionDep,
    user_data: CreateUser,
):
    if not user_data.email.endswith("@itspe.co.in"):
        raise HTTPException(status_code=400, detail="Use company email only")

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
