'''
Understanding model_validate()
    1. Pydantic v2 class method:
        model_validate() is a class method introduced in Pydantic v2 (it replaces parse_obj() from v1).
    2. Validates "incoming data":
        It checks data types, required fields, constraints, and formats based on the model definition.
    3. Converts data into a model instance:
        If validation passes, it returns a properly constructed model object.
    4. Handles type conversion:
        Automatically converts compatible types (for example, strings to integers where allowed).
    5. Used by SQLModel directly:
        SQLModel builds on Pydantic, so model_validate() works seamlessly for creating ORM-compatible objects.
    6. Ensures data safety before DB operations:
        Helps prevent invalid or malformed data from reaching the database.

    In short, model_validate() takes raw input data, validates it, and safely turns it into a model object.
'''
'''
Understanding response_model:
    1. Used in FastAPI route decorators to define the shape of the response
    2. Controls what data is sent back to the client
    3. Filters output fields (only fields defined in the model are returned)
    4. Helps remove sensitive fields like passwords or internal IDs
    5. Validates the response data before sending it
    6. Ensures consistent and predictable API responses
    7. Improves OpenAPI / Swagger documentation automatically
    8. Acts as a contract between backend and client
'''
from fastapi import FastAPI, Depends, HTTPException
from sqlmodel import SQLModel, create_engine, Session, select
from contextlib import asynccontextmanager, contextmanager
from typing import Annotated
from DataBase_Connection_7.models import User, CreateUser

DATABASE_URL = "sqlite:///./users.db"
engine = create_engine(DATABASE_URL, echo=True)

# This is an Event Handler..!
@asynccontextmanager
async def lifespan(app: FastAPI):
    SQLModel.metadata.create_all(engine)
    yield # app runs here
 
# Initialising FastAPI with lifespan constructor..!
app = FastAPI(lifespan=lifespan)

# This function creates a database session and safely closes it after use.
async def get_session():
    with Session(engine) as session:
        yield session # Provides the session to FastAPI

# Annotated combines the "Type Hint" and "Dependency Injection"..!
SessionDep = Annotated[Session, Depends(get_session)]

@app.post("/create_user", response_model=User)
def create_user(user: CreateUser, session: SessionDep):
    new_user = User.model_validate(user)
    # new_user = User(**user.model_dump())
    session.add(new_user)
    session.commit()
    session.refresh(new_user)
    return new_user

@app.get("/users/{user_id}", response_model=User)
def get_users(user_id: int, session: SessionDep):
    # user = session.exec(
    #     select(User).where(User.id == user_id)
    #     ).first()
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Useer Not Found Error..!")
    return user

@app.get("/users", response_model=list[User])
def get_users(session: SessionDep):
    users = session.exec(
        select(User)
        ).all()
    if not users:
        raise HTTPException(status_code=404, detail="Useer Not Found Error..!")
    return users
