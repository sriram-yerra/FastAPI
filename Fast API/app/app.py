from fastapi import FastAPI, HTTPException, File, UploadFile, Form, Depends
from app.schemas import PostCreate, PostResponse, UserRead, UserCreate, UserUpdate
from app.db import Post, create_db_and_tables, get_async_session, User
from sqlalchemy.ext.asyncio import AsyncSession
from contextlib import asynccontextmanager
from sqlalchemy import select
from app.images import imagekit
# from imagekitio.models.UploadFileRequestOptions import UploadFileRequestOptions
import shutil
import os
import uuid
import tempfile
from app.users import auth_backend, current_active_user, fastapi_users

# text_posts = {
#     1: {"title": "Monkey and Dance", "Content": "Dancing Monkey"},
#     2: {"title": "Donkey and Cook", "Content": "Cooking Donkey"},
# 

# @app.get("/hello-world")
# def hello_world():
#     return {"Message": "Hello World"} # Output as JSON

# @app.get("/posts")
# def get_all_posts(limit: int = None) -> PostResponse:
#     if limit:
#         return list(text_posts.values())[:limit]
#     if limit == None:
#         return {"Error": "Set a limit"}

# @app.get("/posts/{id}")
# def get_post_id(id: int) -> PostResponse:
#     if id not in text_posts:
#         raise HTTPException(status_code=404, detail="No Id is present of that kind,,! We are Sorry..!")
#     return text_posts[id]

# @app.post("/posts")
# def create_post(post: PostCreate) -> PostResponse: 
#     # PostResponse Schema Guarentees we need the data in that format only..!
#     new_post = {"title": post.title, "content": post.content}
#     text_posts[max(text_posts.keys()) + 1] = new_post
#     return new_post

'''
This lifespan function defines application-level startup and shutdown behavior in FastAPI.
It tells FastAPI what to run when the app starts and what to clean up when it shuts down.
“Run some code once when the app starts, and optionally run cleanup code when the app stops.”
'''
@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_db_and_tables()
    yield # Startup is complete, app is ready, then app begins serving requests..!

app = FastAPI(lifespan=lifespan)

'''
These lines are what actually expose authentication & user-management APIs in your FastAPI app.
These "include_router" lines turn auth into real HTTP endpoints.

Big-picture flow:
Auth config (users.py) -> Routers registered here -> FastAPI exposes endpoints -> Clients can register, login, reset, verify -> Protected routes use current_active_user
'''
'''
Email+password -> Password verified -> JWT created -> Token returned
Endpoints added: --> With prefix /auth/jwt:
    Method	  Endpoint	         Purpose
    POST	  /auth/jwt/login	 Login & get JWT
    POST	  /auth/jwt/logout   Logout (client-side)
'''
# Login & Logout (JWT)
app.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix="/auth/jwt",
    tags=["auth"]
)

'''
Endpoints added:
    Method	Endpoint	    Purpose
    POST	/auth/register	Create new user
Schemas used:
    UserCreate → request body
    UserRead → response
'''
# User registration
app.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/auth",
    tags=["auth"]
)

'''
Endpoints added:
    Method	Endpoint	            Purpose
    POST	/auth/forgot-password	Request reset
    POST	/auth/reset-password	Reset password

Lifecycle hook used: "on_after_forgot_password(...)"
'''
# Forgot password
app.include_router(
    fastapi_users.get_reset_password_router(),
    prefix="/auth",
    tags=["auth"]
)

'''
Endpoints added:
    Method	Endpoint	Purpose
    POST	/auth/request-verify-token	Request verification
    POST	/auth/verify	Verify user
'''
# Email verification
app.include_router(
    fastapi_users.get_verify_router(UserRead),
    prefix="/auth",
    tags=["auth"]
)

'''
Endpoints added:
    Method	Endpoint	 Purpose
    GET	    /users/me	 Current user profile
    GET	    /users/{id}	 Get user by ID
    PATCH	/users/{id}	 Update user
    DELETE	/users/{id}	 Delete user
'''
# User management (Admin / Self)
app.include_router(
    fastapi_users.get_users_router(UserRead, UserUpdate),
    prefix="/users",
    tags=["users"]
)

@app.post("/upload")
async def upload_file(
        file: UploadFile = File(...),
        caption: str = Form(""),
        user: User = Depends(current_active_user),
        session: AsyncSession = Depends(get_async_session) 
        # We can use the current active referemce of the database directly in this function throught this "session".
):
    temp_file_path = None

    try:
        # Creating the temporary file..!
        # Save uploaded file to temp
        suffix = os.path.splitext(file.filename)[1]
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
            temp_file_path = temp_file.name
            shutil.copyfileobj(file.file, temp_file)

        # Uploading the temporary file..!
        upload_result = imagekit.upload_file(
            file=open(temp_file_path, "rb"),
            file_name=file.filename,
            upload_result = imagekit.upload(
                file=open(temp_file_path, "rb"),
                file_name=file.filename,
                options={
                    "private_key": os.getenv("IMAGEKIT_PRIVATE_KEY"),
                    "public_key": os.getenv("IMAGEKIT_PUBLIC_KEY"),
                    "url_endpoint": os.getenv("IMAGEKIT_URL"),
                    "use_unique_file_name": True,
                    "folder": "/posts",
                    "tags": ["backend-upload"],
                },
            )
        )

        # Check the response code, proceed if 200..! then only Post
        if upload_result.response_metadata.http_status_code == 200:
            post = Post(
                user_id = user.id,
                caption = caption,
                url = upload_result.url,
                file_type = "video" if file.content_type.startswith("video/") else "image",
                file_name = upload_result.name
            )
            session.add(post) # Telling db that it is ready to be added..!
            await session.commit() # But it will go into the db only when it is committed..!
            await session.refresh(post) # Refreshing the object
            return post

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    finally:
        if temp_file_path and os.path.exists(temp_file_path):
            os.unlink(temp_file_path)
        file.file.close()

# Retriving from the DataBase..!
@app.get("/feed")
async def get_feed(
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_active_user)
):
    result = await session.execute(select(Post).order_by(Post.created_at.desc()))
    posts = [row[0] for row in result.all()]

    result = await session.execute(select(User))
    users = [row[0] for row in result.all()]
    user_dict = {u.id: u.email for u in users}

    posts_data = []
    for post in posts:
        posts_data.append(
            {
                "id": str(post.id),
                "user_id": str(post.user_id),
                "caption": post.caption,
                "url": post.url,
                "file_type": post.file_type,
                "file_name": post.file_name,
                "created_at": post.created_at.isoformat(),
                "is_owner": post.user_id == user.id,
                "email": user_dict.get(post.user_id, "Unknown")
            }
        )

    return {"posts": posts_data}

@app.delete("/posts/{post_id}")
async def delete_post(post_id: str, session: AsyncSession = Depends(get_async_session), user: User = Depends(current_active_user),):
    try:
        post_uuid = uuid.UUID(post_id)

        result = await session.execute(select(Post).where(Post.id == post_uuid))
        post = result.scalars().first()

        if not post:
            raise HTTPException(status_code=404, detail="Post not found")
        
        if post.user_id != user.id:
            raise HTTPException(status_code=403, detail="You don't have permission to delete this post")

        await session.delete(post)
        await session.commit()

        return {"success": True, "message": "Post deleted successfully"}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))