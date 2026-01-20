from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field, EmailStr

app = FastAPI()

user_details = {}
user_id = 1

class User(BaseModel):
    name: str = Field(..., min_length=3, max_length=20)
    phone: int = Field(..., ge=999999999, le=10000000000)
    email: EmailStr

@app.post("/create")
async def create_user(user: User):
    global user_id
    user_details[user_id] = user
    user_id += 1
    return "New User added: ", user

@app.get("/fetch")
async def get_users():
    if not user_details:
        raise HTTPException(status_code=404, detail="No user found..!")
    return "Currently added users: ", user_details

@app.get("/user/{user_id}")
async def get_SingleUser(user_id: int):
    if user_id not in user_details:
        raise HTTPException(status_code=404, detail="User not found..!")
    return user_details[user_id]

@app.put("/user/{user_id}")
async def update_user(user_id: int, user: User):
    if user_id not in user_details:
        raise HTTPException(status_code=404, detail="User not found..!")
    user_details[user_id] = user
    return {"message" : "User updated", "User" : user}

@app.delete("/user/{user_id}")
async def delete_user(user_id: int):
    if user_id not in user_details:
        raise HTTPException(status_code=404, detail="User not found..!")
    # del user_details[user_id]
    deleted_user = user_details.pop(user_id)

    return user_details