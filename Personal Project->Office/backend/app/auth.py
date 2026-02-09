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

from jose import jwt, JWTError
from datetime import datetime, timedelta, timezone
from passlib.context import CryptContext
from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.database import create_tables_database


SECRET_KEY = "mysecretkey"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


# This is an Event Handler..!
@asynccontextmanager
async def lifespan(app: FastAPI):
    create_tables_database()
    yield # app runs here
 
# Initialising FastAPI with lifespan constructor..!
app = FastAPI(lifespan=lifespan)

pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

# Authentication, comparing the hashed pwd to the db password..!
def verified_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)

def create_acess_token(data: dict, expires_delta: timedelta | None=None):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=30))
    to_encode.update({"exp": expire})

    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=ALGORITHM)
        return payload  
    # except Exception as e:
    except JWTError:
        return None
    
