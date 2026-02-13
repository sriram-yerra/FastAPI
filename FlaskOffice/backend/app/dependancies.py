from flask import request, jsonify
from functools import wraps
from app.database import get_session
from app.auth import verify_token
from app.models.user_model import User
from sqlalchemy.orm import Session

def get_current_user(func):
    """Decorator to get current authenticated user"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return jsonify({"detail": "Authorization header missing"}), 401
        
        try:
            token = auth_header.split(' ')[1]  # Extract token from "Bearer <token>"
        except IndexError:
            return jsonify({"detail": "Invalid token format"}), 401
        
        payload = verify_token(token)
        if not payload:
            return jsonify({"detail": "Invalid token"}), 401
        
        email = payload.get("sub")
        if not email:
            return jsonify({"detail": "Invalid token payload"}), 401
        
        session = next(get_session())
        try:
            user = session.query(User).filter(User.email == email).first()
            if not user:
                return jsonify({"detail": "User not found"}), 404
            
            # Add user to kwargs so the route can access it
            kwargs['current_user'] = user
            kwargs['session'] = session
            
            result = func(*args, **kwargs)
            return result
        except Exception as e:
            session.rollback()
            raise
        finally:
            # Don't close session here - let the route handler close it
            pass
    return wrapper
