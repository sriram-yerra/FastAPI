'''
What is a JWT Authentication
    1. JWT stands for JSON Web Token.
    2. A JWT is a token that looks like a hash, but it serves a different purpose.
    3. Unlike password hashes, a JWT is generated using three components:
        a secret key
        an algorithm (e.g., HS256)
        payload data such as user email and expiration time
    4. JWTs are primarily used for authentication.
    5. The token is sent in the request header as a Bearer Token, like:
        Authorization: Bearer <token_here>
    6. The token acts as proof that the user is logged in.
    7. Each token has an expiration time; once expired, the user must log in again.
    8. Because the token carries all the session information, no server-side session storage is needed.
'''
'''
Setup – Installing Dependencies
    Open your terminal and install the following libraries:
    pip install python-jose[cryptography]
    python-jose is used for creating and decoding JWT tokens.
'''
'''
What is inside the JWT?
The token secretly contains:
{
  "sub": "ram@company.com",
  "exp": "2026-01-18 19:00"
}
'''

from fastapi import FastAPI, Depends, HTTPException, Form, File, UploadFile
from sqlmodel import SQLModel, create_engine, Session, select
from contextlib import asynccontextmanager, contextmanager
from typing import Annotated, Optional
from models import User, CreateUser, UpdateUser, loginUser, UserRead, Token
from pydantic import EmailStr
import uuid
import os, shutil # shutil will upload the file in chunks to avoid server/system crash..!
from passlib.context import CryptContext
from jose import jwt, JWTError
from datetime import datetime, timedelta, timezone
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestFormStrict

DATABASE_URL = "sqlite:///./users.db"
SECRET_KEY = "mysecretkey"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

engine = create_engine(DATABASE_URL, echo=True)

# This is an Event Handler..!
@asynccontextmanager
async def lifespan(app: FastAPI):
    SQLModel.metadata.create_all(engine)
    yield # app runs here
 
# Initialising FastAPI with lifespan constructor..!
app = FastAPI(lifespan=lifespan)

# This function creates a database session and safely closes it after use.
def get_session():
    with Session(engine) as session:
        yield session # Provides the session to FastAPI

# Annotated combines the "Type Hint" and "Dependency Injection"..!
SessionDep = Annotated[Session, Depends(get_session)]

pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

# Authentication, comparing the hashed pwd to the db password..!
def verified_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)

def create_acess_token(data: dict, expires_delta: timedelta | None=None):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})

    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=ALGORITHM)
        return payload  
    
    # except Exception as e:
    except JWTError:
        return None
    
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

@app.post("/register", response_model=User)
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

@app.get("/users")
def get_users(session: SessionDep):
    users = session.exec(select(User)).all()
    if not users:
        raise HTTPException( status_code=401, detail="No users found..!")
    return users

@app.post("/login", response_model=Token)
def login(
    session: SessionDep,
    # login_user: loginUser,
    # Depends() -> FastAPI interprets it as: “Use the type annotation itself as the dependency”
    form_data: Annotated[OAuth2PasswordRequestFormStrict, Depends()]
):
    # Fetching unique user by using emial address..!
    user = session.exec(
        select(User).where(User.email == form_data.email)
        ).first()
    
    if not user:
        raise HTTPException(status_code=400, detail="Bro..! Email doesnt Exists..! please register first..!")
    
    pwd = verified_password(form_data.password, user.hashed_password)

    if not pwd:
        raise HTTPException(status_code=400, detail="Bro..! Password isn't correct..!")

    token = create_acess_token(data={"sub": user.email})
    return {"access_token": token, "token_type": "bearer"}

@app.get("/profile")
def profile(current_user: Annotated[User, Depends(get_current_user)]):
    return  {"name": current_user.name, "email": current_user.email}
