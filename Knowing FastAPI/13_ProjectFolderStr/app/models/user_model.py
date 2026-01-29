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
    name: str = Field(nullable=False)
    email: EmailStr = Field(unique=True, index=True, nullable=False)
    hashed_password: str = Field(nullable=False)
