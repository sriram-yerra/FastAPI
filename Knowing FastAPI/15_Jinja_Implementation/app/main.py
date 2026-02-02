from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.database import create_tables_database
from app.routers.user_routes import router as user_router
from contextlib import asynccontextmanager
from fastapi.staticfiles import StaticFiles

# This is an Event Handler..!
@asynccontextmanager
async def lifespan(app: FastAPI):
    create_tables_database()
    yield # app runs here
 
# Initialising FastAPI with lifespan constructor..!
app = FastAPI(lifespan=lifespan)

app.mount("/static", StaticFiles(directory="app/static"), name="static")

app.include_router(user_router)

