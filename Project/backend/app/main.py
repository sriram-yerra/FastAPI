from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.database import create_tables_database
from app.routes.user_routes import router as user_router
from app.routes import user_routes

# This is an Event Handler..!
@asynccontextmanager
async def lifespan(app: FastAPI):
    create_tables_database()
    yield # app runs here
 
# Initialising FastAPI with lifespan constructor..!
app = FastAPI(lifespan=lifespan)

# app.include_router(user_routes.router)
app.include_router(user_router)
