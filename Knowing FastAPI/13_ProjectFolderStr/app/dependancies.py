from fastapi import FastAPI, Depends, HTTPException, Form, File, UploadFile
from sqlmodel import SQLModel, create_engine, Session, select
from typing import Annotated, Optional
from app.schemas.user_schema import CreateUser, UpdateUser, loginUser, UserRead, Token
from pydantic import EmailStr
import uuid
import os, shutil # shutil will upload the file in chunks to avoid server/system crash..!
from passlib.context import CryptContext
from jose import jwt, JWTError
from datetime import datetime, timedelta, timezone
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestFormStrict
from app.database import get_session
from app.auth import verified_password, verify_token
from app.models.user_model import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

SessionDep = Annotated[Session, Depends(get_session)]

def get_current_user(token: Annotated[str, Depends(oauth2_scheme)], session: SessionDep):
    # payload = verified_password(token, )
    payload = verify_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="invlaid token..!")
    
    email = payload.get("sub")
    if not email:
        raise HTTPException(status_code=401, detail="Invalid token payload")
    
    user = session.exec(
        select(User).where(User.email == email)
    ).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found..!")
    
    return user