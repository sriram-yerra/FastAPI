from sqlmodel import SQLModel
from pydantic import BaseModel, EmailStr 
from sqlmodel import SQLModel, Field
from typing import Annotated, Optional


class CreateUser(SQLModel):
    name: str
    email: EmailStr
    password: str = Field(min_length=1, max_length=72)

class UpdateUser(SQLModel):
    name: Optional[str] = None
    phone: Optional[int] = None
    email: Optional[EmailStr] = None

class loginUser(SQLModel):
    email: str
    password: str   

class UserRead(SQLModel):
    id: int
    name: str
    email: EmailStr

class Token(SQLModel):
    access_token: str
    token_type: str

class OTPVerify(SQLModel):
    email: EmailStr
    otp: str