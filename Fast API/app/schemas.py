from pydantic import BaseModel
from fastapi_users import schemas
import uuid

'''
"Schemas ≠ Database models"
These are Pydantic schema classes.
They define how data "enters and leaves your API" — not how it’s stored in the database.
'''
'''
Client (JSON)
   ↓
Pydantic Schemas  ←––– THIS FILE
   ↓
FastAPI Routes
   ↓
SQLAlchemy Models (DB)
'''

'''
What this is for?
    - Used when creating a post
    - Validates incoming JSON
    - Ensures required fields exist
'''
# PostCreate — input schema (request body)
class PostCreate(BaseModel):
    title: str
    content: str

'''
What this is for?
    - Controls what data you send back
    - Hides internal fields
    - Keeps API responses clean
'''
# PostResponse — output schema (response body)
class PostResponse(BaseModel):
    title: str
    content: str

'''
What this is for --> Used when returning user data.
Example endpoints:
    /users/me
    /users/{id}
'''
'''
Fields included (by default)
From BaseUser: id, email, is_active, is_verified, is_superuser
'''
# UserRead — user response schema (fastapi-users)
class UserRead(schemas.BaseUser[uuid.UUID]):
    pass

'''
What this is for --> Used when registering a user.
Endpoint: POST /auth/register
Fields expected: email, password
'''
# UserCreate — user registration schema
class UserCreate(schemas.BaseUserCreate):
    pass

'''
What this is for --> Used when updating user info
Endpoint: PATCH /users/{id}
Fields allowed: Optional email, Optional password, Optional flags
'''
# UserUpdate — user update schema
class UserUpdate(schemas.BaseUserUpdate):
    pass