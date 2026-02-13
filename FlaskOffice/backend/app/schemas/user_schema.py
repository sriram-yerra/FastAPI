from pydantic import BaseModel, EmailStr, Field
from typing import Optional

class CreateUser(BaseModel):
    name: str
    email: EmailStr
    password: str = Field(min_length=1, max_length=72)

class UpdateUser(BaseModel):
    name: Optional[str] = None
    phone: Optional[int] = None
    email: Optional[EmailStr] = None

class loginUser(BaseModel):
    email: str
    password: str   

class UserRead(BaseModel):
    id: int
    name: str
    email: EmailStr

class Token(BaseModel):
    access_token: str
    token_type: str

class OTPVerify(BaseModel):
    email: EmailStr
    otp: str
