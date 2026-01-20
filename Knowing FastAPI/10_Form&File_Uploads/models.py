from sqlmodel import SQLModel, Field
from typing import Optional
from pydantic import BaseModel, EmailStr

# DataBase Table
class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    phone: int
    email: EmailStr
    file_path: str

'''
class CreateUser(SQLModel) Means:
“I am defining a structured data model that supports validation and type safety, and can optionally map to a database table.”
'''
# Request Schema
# can also use BaseModel here
class CreateUser(SQLModel):
    name: str
    phone: int
    email: EmailStr

class UpdateUser(SQLModel):
    name: Optional[str] = None
    phone: Optional[int] = None
    email: Optional[EmailStr] = None