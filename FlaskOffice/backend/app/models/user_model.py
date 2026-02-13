from app.database import db
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import declarative_base
from datetime import datetime
from pydantic import EmailStr
from typing import Optional

'''
Field defines the identity of each row.
Field defines rules and performance behavior for the column.
Field is used to add database-specific rules (primary key, uniqueness, indexing, defaults) that Python types alone cannot express.
'''

# Database Table
class User(db.Model):
    __tablename__ = "user"
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String, nullable=False)
    email = db.Column(db.String, unique=True, index=True, nullable=False)
    hashed_password = db.Column(db.String, nullable=False)

class EmailOTP(db.Model):
    __tablename__ = "emailotp"
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String, index=True)
    name = db.Column(db.String)
    hashed_password = db.Column(db.String)
    otp = db.Column(db.String)
    expires_at = db.Column(db.DateTime)
