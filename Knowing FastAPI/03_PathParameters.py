'''
Path Parameters in FastAPI..!

Path parameters are variables that are part of the URL path.
They allow you to capture values directly from the URL and use them inside your function.
'''

'''
How it works?
    {user_id} is a path parameter
    If you visit /users/10, FastAPI passes 10 to user_id
'''

from fastapi import FastAPI

app = FastAPI()

users = {
    1:{
        "name": "ram",
        "orders": {
            10: {"item": "goods", "amount": 1000},
            11: {"item": "aarti", "amount": 200}
        }
        },
    2:{
        "name": "sri",
        "orders": {
            12: {"item": "spy", "amount": 1000},
            13: {"item": "ram", "amount": 3000}
        }
        },
}

@app.get("/users/{user_id}")
def get_user(user_id: int):
    user_id = users[user_id]
    return {"user_id": user_id}

@app.get("/users/{user_id}/orders/{order_id}")
def get_user(user_id: int, order_id: int):
    user = users[user_id]
    order = user["orders"][order_id]
    return order