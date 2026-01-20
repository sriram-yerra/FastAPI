'''
Compatible Databases:
FastAPI supports multiple databases through ORMs like SQLAlchemy and SQLModel, allowing easy interaction with relational databases.

Popular Supported Databases:
    SQLite
    PostgreSQL
    MySQL / MariaDB
    Microsoft SQL Server
    Oracle and others

Why this matters:
    You can switch databases without changing your API logic
    ORMs handle SQL queries using Python objects
    Works well with async and sync database drivers

About SQLModel:
    Combines Pydantic and SQLAlchemy
    Uses one model for database tables and API schemas
    Simplifies table definitions, request handling, and responses
'''
'''
Depends(get_session):
Tells FastAPI:
    “Call get_session() before running the endpoint”
    “Inject its yielded value into the endpoint”
    “Clean it up after request ends”
'''
'''
yield:
    Provides the session to FastAPI
    After the request is completed:
    code after yield (if any) would run
    session is cleaned up automatically
'''