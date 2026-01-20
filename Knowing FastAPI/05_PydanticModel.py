'''
A Pydantic Model is a Python class that inherits from BaseModel and is used to define the structure of data using type annotations.

It automatically provides:
    Data validation based on types
    Automatic type conversion
    Clear error reporting
    Serialization and deserialization between Python objects and JSON

Why it is used in FastAPI?
    Ensures incoming request data is valid
    Converts data to correct Python types
    Prevents invalid or malformed data from reaching business logic
    Automatically documents request and response schemas
'''
'''
Why Use Pydantic Models?

1. Automatic Validation:
    Ensures incoming data matches the correct data types such as strings, integers, and emails.
2. Automatic Error Responses in FastAPI:
    FastAPI automatically returns clear and structured errors when invalid data is sent.
3. Swagger / OpenAPI Integration:
    FastAPI reads Pydantic models and displays them automatically in /docs and /redoc.
4. Cleaner Code:
    Removes the need to manually check and validate request inputs.
5. Serialization and Deserialization: ***
    Converts Python objects to JSON and JSON back to Python automatically.
6. Nested Models Support:**
    Allows defining complex data structures by nesting one model inside another.
7. Consistency Across APIs:
    Ensures request and response data always follow a defined structure.
'''

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

user_details = {}
user_id = 1

class User(BaseModel):
    name: str
    phone: int
    email: str

@app.post("/create")
async def create_user(user: User):
    global user_id
    user_details[user_id] = user
    user_id += 1

    response = {
        "Message" : "User created successfully",
        "User Id" : user_id,
        "user details" : user
    }
    return response
    # return "New User added: ", user

@app.post("/fetch")
@app.get("/fetch")
async def get_users():
    response = {
        "message" : "List of all Users created successfully",
        "user" : user_details
    }

    return response
    # return "Currently added users: ", user_details