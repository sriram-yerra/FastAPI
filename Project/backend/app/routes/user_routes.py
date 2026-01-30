from fastapi import FastAPI, Depends, HTTPException, Form, File, UploadFile, APIRouter
from sqlmodel import SQLModel, create_engine, Session, select, delete
from typing import Annotated, Optional
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestFormStrict
from app.models.user_model import User, EmailOTP
from app.dependancies import get_current_user, SessionDep
from app.schemas.user_schema import CreateUser, OTPVerify, UpdateUser, loginUser, UserRead, Token
from app.auth import hash_password, verified_password, create_acess_token
import random, smtplib
from fastapi.responses import JSONResponse, FileResponse
from email.message import EmailMessage
from datetime import datetime, timedelta, timezone
from app.emailverfication import send_otp_email, generate_otp


router = APIRouter()

@router.post("/otp-registration")
def request_otp(user_data: CreateUser, session: SessionDep):

    if not user_data.email.endswith("@itspe.co.in"):
        raise HTTPException(400, "Company email required")

    existing_user = session.exec(
        select(User).where(User.email == user_data.email)
    ).first()

    if existing_user:
        raise HTTPException(400, "Email already registered")

    session.exec(delete(EmailOTP).where(EmailOTP.email == user_data.email))
    session.commit()

    otp = generate_otp()
    expiry_time = datetime.utcnow() + timedelta(minutes=2)

    temp_record = EmailOTP(
        email=user_data.email,
        name=user_data.name,
        hashed_password=hash_password(user_data.password),
        otp=otp,
        expires_at=expiry_time
    )

    session.add(temp_record)
    session.commit()

    send_otp_email(user_data.email, otp)

    return {"message": "OTP sent"}

@router.post("/verify-otp-register", response_model=User)
def verify_otp_register(data: OTPVerify, session: SessionDep):

    record = session.exec(
        select(EmailOTP).where(EmailOTP.email == data.email)
    ).first()

    if not record:
        raise HTTPException(400, "OTP not requested")

    if datetime.utcnow() > record.expires_at:
        raise HTTPException(400, "OTP expired")

    if record.otp != data.otp:
        raise HTTPException(400, "Invalid OTP")

    new_user = User(
        name=record.name,
        email=record.email,
        hashed_password=record.hashed_password
    )

    session.add(new_user)

    session.delete(record)

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

    return {
        "access_token": token, 
        "token_type": "bearer"
    }

@router.get("/profile")
def profile(current_user: Annotated[User, Depends(get_current_user)]):
    return  {"name": current_user, "email": current_user.email}
