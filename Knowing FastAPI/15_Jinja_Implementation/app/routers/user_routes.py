from fastapi import FastAPI, Depends, HTTPException, APIRouter, Request, Form
from sqlmodel import SQLModel, create_engine, Session, select, delete
from typing import Annotated, Optional
from app.database import get_session
from app.models import User
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse

router = APIRouter()

SessionDep = Annotated[Session, Depends(get_session)]

templates = Jinja2Templates(directory="app/templates")

# Showing the Register Page! SHOW REGISTER PAGE
@router.get("/", response_class=HTMLResponse)
def register_form(request: Request):
    return templates.TemplateResponse(
        "register.html", 
        {"request": request}
    )           

# HANDLE FORM SUBMISSION
@router.post("/register")
def register_user(
    session: SessionDep, 
    name: str = Form(...),
    email: str = Form(...),
    phone: str = Form(...)
):
    
    # Creating a new user
    user = User(name=name, email=email, phone=phone)

    existing_user = session.exec(
        select(User).where(User.email == user.email)
    ).first()

    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    session.add(user)
    session.commit()
    
    return RedirectResponse(url="/users", status_code=303)

# SHOW USERS LIST
@router.get("/users", response_class=HTMLResponse)
def users(
    session: SessionDep,
    request: Request
):
    users_list = session.exec(
        select(User)
        ).all()

    return templates.TemplateResponse(
        "users.html", 
        {"request": request, "users_list": users_list} # Sending Users list into template..!
    )   