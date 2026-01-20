# Dependency Injection:
'''
Providing a way to inject resuable logic..!
What is Dependency Injection?
    Dependency Injection (DI) is a design pattern where required components are provided from outside, instead of being created inside a function or class.
    Dependencies can be services, database sessions, configuration objects, or utility functions.
    This makes code cleaner, reusable, testable, and easier to maintain.
'''
'''
Initially it checks the logic of depends method and then it goes with the "path operation method".
Dependency Injection in FastAPI:
    FastAPI has built-in support for Dependency Injection using Depends().
FastAPI automatically:
    Calls the dependency
    Passes its return value to your function
    Manages cleanup if needed
'''

# Dependencies Flow in FastAPI (simple explanation):
'''
1. Request hits the endpoint:
    A client sends an HTTP request to a specific API route.

2. FastAPI executes dependencies first:
    Any dependency declared using Depends() (like authentication, database session) runs before the endpoint logic.

3. Dependency checks and validation:
    The dependency may validate data, check login status, or prepare resources.

4. Dependency returns a value:
    If no error occurs, the dependency returns a value (for example, a user object or database session).

5. Value is injected into the endpoint:
    FastAPI automatically passes the returned value as a parameter to the endpoint function.

6. Business logic executes:
    The actual code inside the endpoint runs using the injected dependency values.
'''

# Real-world examples of reusable dependencies:
'''
1. Database session injection:
    A single database connection logic is reused across many routes, so you don’t manually open and close connections every time.

2. Authentication / Authorization:
    The same login and permission checks are reused to protect multiple endpoints (only logged-in users, admins, etc.).

3. Pagination parameters:
    Common query parameters like page and limit are defined once and reused across many APIs.

4. Custom logger or timer:
    Shared logic to log request time or performance metrics across routes without repeating code.

5. Reusable form or file validation:
    Common validation logic for forms or file uploads is written once and reused in multiple endpoints.
'''

# EXAMPLE FOR EMPLOYEE ATTENDANCE..!

from fastapi import FastAPI, Depends, HTTPException

app = FastAPI()

# Fake database
users_db = {
    "ram": {"password": "1234", "role": "employee"},
    "sai": {"password": "abcd", "role": "manager"},
    "admin": {"password": "admin", "role": "admin"},
}

attendance = []

# Authentication
def authenticate(username: str, password: str):
    user = users_db.get(username)
    if not user or user["password"] != password:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return {"username": username, "role": user["role"]}

# Authorization
def employee_only(user=Depends(authenticate)):
    if user["role"] != "employee":
        raise HTTPException(status_code=403, detail="Only employees allowed")
    return user

def manager_only(user=Depends(authenticate)):
    if user["role"] not in ["manager", "admin"]:
        raise HTTPException(status_code=403, detail="Only managers allowed")
    return user

# Employee marks attendance
@app.post("/mark-attendance")
def mark_attendance(user=Depends(employee_only)):
    attendance.append(user["username"])
    return {"message": f"Attendance marked for {user['username']}"}

# Manager views attendance
@app.get("/view-attendance")
def view_attendance(user=Depends(manager_only)):
    return {"attendance": attendance}

'''
Why Dependency Injection is useful?
    Avoids hard-coding logic inside endpoints
    Makes code modular and reusable
    Simplifies testing (you can replace dependencies easily)
    Centralizes shared logic (DB sessions, auth, configs)

One-line takeaway:
    Dependency Injection means FastAPI gives your function what it needs, instead of your function creating everything itself.
'''
# LAYMANN ANALOGY:
'''
Very short analogy:
    Authentication = Showing ID at the gate
    Authorization = Door access inside the office
'''
# AUTHENTICATION:
'''
Authentication (Who are you?):
    Authentication means proving your identity.

Real-world example (Office entry):
    You come to the office gate
    You show your ID card / fingerprint / face scan
    Security checks: “Is this really Ram?”

If yes → you are authenticated
If no → entry denied

In attendance terms:
    You log in with email + password
    System verifies your credentials
    Only after that, you can mark attendance

Authentication answers: "Are you really the employee you claim to be?”
'''
# AUTHORIZATION:
'''
Authorization (What are you allowed to do?):
    Authorization means checking permissions.
    Real-world example (Inside office)

After you enter the building:
    Employee → can mark attendance
    Manager → can view team attendance
    HR → can edit or approve attendance
    Security asks: “You are Ram, but are you allowed to enter THIS room?”

In attendance terms:
    Employee → can mark own attendance
    Manager → can view team attendance
    Admin → can edit any attendance

Authorization answers: “Now that you are verified, what actions can you perform?”
'''
