from sqlmodel import SQLModel, Field
from typing import Optional
from pydantic import BaseModel, EmailStr    

# Importtance Of Field
'''
Field defines the identity of each row.
Field defines rules and performance behavior for the column.
Field is used to add database-specific rules (primary key, uniqueness, indexing, defaults) that Python types alone cannot express.
'''

# DataBase Table
class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    email: EmailStr = Field(unique=True, index=True)
    hashed_password: str

class CreateUser(SQLModel):
    name: str
    email: EmailStr
    # password: str
    password: str = Field(min_length=6, max_length=72)

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
