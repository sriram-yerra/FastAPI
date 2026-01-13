'''
What is this file overall used for?
This file is the authentication & user-management configuration layer of your FastAPI app.

In one sentence:
This file defines how users are created, authenticated, issued JWT tokens, and injected into protected routes.
'''

import uuid
from typing import Optional
from fastapi import Depends, Request
from fastapi_users import BaseUserManager, FastAPIUsers, UUIDIDMixin, models
from fastapi_users.authentication import (
    AuthenticationBackend,
    BearerTransport,
    JWTStrategy
)
from fastapi_users.db import SQLAlchemyUserDatabase
from app.db import User, get_user_db

SECRET = "sakjdhkjad872323"

'''
This class is part of fastapi-users 
It is responsible for user lifecycle logic (registration, password reset, verification, etc.).
'''
'''
Think of it as: Controller for user behavior, not storage
    - It does NOT store users (DB does that)
    - It DOES decide what happens when:
        - a user registers
        - resets password
        - requests email verification
'''
class UserManager(UUIDIDMixin, BaseUserManager[User, uuid.UUID]):
    reset_password_token_secret = SECRET
    verification_token_secret = SECRET
    '''
    Lifecycle hooks (VERY IMPORTANT)
        - These methods are hooks.
        - They are called automatically by fastapi-users at specific moments.
    '''
    '''
    It is called when a user successfully registers..!
    '''
    async def on_after_register(self, user: User, request: Optional[Request] = None):
        print(f"User {user.id} has registered.")

    '''
    It is called when user Rwquests password Reser..!
    '''
    async def on_after_forgot_password(self, user: User, token: str, request: Optional[Request] = None):
        print(f"User {user.id} has forgot their password. Reset token: {token}")

    '''
    It is called When user requests email verification
    '''
    async def on_after_request_verify(self, user: User, token: str, request: Optional[Request] = None):
        print(f"Verification requested for user {user.id}. Verification token: {token}")

'''
These pieces together wire authentication into your FastAPI app using fastapi-users + JWT.
Think of them as the plumbing that connects users, tokens, and request protection.
'''
'''
What this does?
Creates a UserManager instance. Injects a database adapter (user_db). Provides it per request

Why this exists?
fastapi-users separates:
    Storage → SQLAlchemyUserDatabase
    Logic → UserManager
This function connects them.

Mental model:
“Give me a UserManager that knows how to talk to the database.”
'''
async def get_user_manager(user_db: SQLAlchemyUserDatabase = Depends(get_user_db)):
    yield UserManager(user_db)

'''
Define how tokens are created & verified.
It defines: How JWT tokens are "signed", How long they are "valid", How they are "verified".
Why a function, not a variable?
    - FastAPI Users expects a callable, so it can:
    - Re-create strategy when needed
    - Stay dependency-injection friendly
'''
def get_jwt_strategy():
    strategy = JWTStrategy(secret=SECRET, lifetime_seconds=3600)
    return strategy

'''
How the token is sent (Transport).
What this means?
    Tokens are sent via: "Authorization: Bearer <token>"
'''
bearer_transport = BearerTransport(
    # TokenUrl tells "Swagger UI" where to log in
    tokenUrl="auth/jwt/login"
)

'''
What this represents?
    - An authentication method.

It answers:
    - How do tokens travel? → BearerTransport
    - How are tokens validated? → JWTStrategy
'''
auth_backend = AuthenticationBackend(
    name="jwt",
    transport=bearer_transport,
    get_strategy=get_jwt_strategy,
)

'''
Main authentication engine.
What this creates? A central authentication controller that:
    - Registers routes
    - Handles login / logout
    - Validates tokens
    - Fetches users
'''
fastapi_users = FastAPIUsers[User, uuid.UUID](get_user_manager, [auth_backend])

'''
Protect routes.
What this returns? A FastAPI dependency that:
    - Extracts JWT from request
    - Validates it
    - Fetches user from DB
    - Ensures user is active
'''
current_active_user = fastapi_users.current_user(active=True)

'''
User logs in
 ↓
POST /auth/jwt/login
 ↓
JWT created (JWTStrategy)
 ↓
Token returned
 ↓
Client sends Authorization: Bearer <token>
 ↓
current_active_user dependency runs
 ↓
User fetched & validated
 ↓
Route executes
'''