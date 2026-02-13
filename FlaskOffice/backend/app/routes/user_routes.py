from flask import Blueprint, request, jsonify
from app.database import get_session
from flasgger import swag_from

from app.models.user_model import User, EmailOTP
from app.dependancies import get_current_user
from app.schemas.user_schema import CreateUser, OTPVerify, UpdateUser, loginUser, UserRead, Token
from app.auth import hash_password, verified_password, create_acess_token
from app.emailverfication import send_otp_email, generate_otp
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session

router = Blueprint('user_routes', __name__)

@router.route("/otp-registration", methods=["POST"])
@swag_from({
    "tags": ["User Auth"],
    "parameters": [
        {
            "name": "body",
            "in": "body",
            "required": True,
            "schema": {
                "properties": {
                    "name": {"type": "string"},
                    "email": {"type": "string"},
                    "password": {"type": "string"}
                }
            }
        }
    ],
    "responses": {
        200: {"description": "OTP sent"},
        400: {"description": "Invalid email or already exists"}
    }
})
def request_otp():
    data = request.get_json()
    user_data = CreateUser(**data)
    
    # if not user_data.email.endswith("@itspe.co.in"):
    #     return jsonify({"detail": "Company email required"}), 400

    if not user_data.email.endswith("@gmail.com"):
        return jsonify({"detail": "G-mail required"}), 400

    session = next(get_session())
    try:
        existing_user = session.query(User).filter(User.email == user_data.email).first()

        if existing_user:
            return jsonify({"detail": "Email already registered"}), 400

        session.query(EmailOTP).filter(EmailOTP.email == user_data.email).delete()
        session.commit()

        otp = generate_otp()
        expiry_time = datetime.utcnow() + timedelta(minutes=2)

        temp_record = EmailOTP(
            email=user_data.email,
            name=user_data.name,
            hashed_password=hash_password(user_data.password),
            otp=otp,
            expires_at=expiry_time
        )

        session.add(temp_record)
        session.commit()

        send_otp_email(user_data.email, otp)

        return jsonify({"message": "OTP sent"}), 200
    finally:
        session.close()

@router.route("/verify-otp-register", methods=["POST"])
@swag_from({
    "tags": ["User Auth"],
    "parameters": [
        {
            "name": "body",
            "in": "body",
            "required": True,
            "schema": {
                "properties": {
                    "email": {"type": "string"},
                    "otp": {"type": "string"}
                }
            }
        }
    ],
    "responses": {
        200: {"description": "User created successfully"},
        400: {"description": "Invalid OTP or expired"}
    }
})
def verify_otp_register():
    data = request.get_json()
    otp_data = OTPVerify(**data)
    
    session = next(get_session())
    try:
        record = session.query(EmailOTP).filter(EmailOTP.email == otp_data.email).first()

        if not record:
            return jsonify({"detail": "OTP not requested"}), 400

        if datetime.utcnow() > record.expires_at:
            return jsonify({"detail": "OTP expired"}), 400

        if record.otp != otp_data.otp:
            return jsonify({"detail": "Invalid OTP"}), 400

        new_user = User(
            name=record.name,
            email=record.email,
            hashed_password=record.hashed_password
        )

        session.add(new_user)
        session.delete(record)
        session.commit()
        session.refresh(new_user)

        return jsonify({
            "id": new_user.id,
            "name": new_user.name,
            "email": new_user.email
        }), 200
    finally:
        session.close()

@router.route("/login", methods=["POST"])
@swag_from({
    "tags": ["User Auth"],
    "parameters": [
        {
            "name": "body",
            "in": "body",
            "required": True,
            "schema": {
                "properties": {
                    "email": {"type": "string"},
                    "password": {"type": "string"}
                }
            }
        }
    ],
    "responses": {
        200: {"description": "JWT token"},
        400: {"description": "Invalid credentials"}
    }
})
def login():
    data = request.get_json()
    form_data = loginUser(**data)
    
    session = next(get_session())
    try:
        # Fetching unique user by using email address..!
        user = session.query(User).filter(User.email == form_data.email).first()
        
        if not user:
            return jsonify({"detail": "Bro..! Email doesnt Exists..! please register first..!"}), 400
        
        pwd = verified_password(form_data.password, user.hashed_password)

        if not pwd:
            return jsonify({"detail": "Bro..! Password isn't correct..!"}), 400

        token = create_acess_token(data={"sub": user.email})

        return jsonify({
            "access_token": token, 
            "token_type": "bearer"
        }), 200
    finally:
        session.close()

@router.route("/users", methods=["GET"])
@swag_from({
    "tags": ["User"],
    "security": [{"Bearer": []}],
    "responses": {
        200: {"description": "List of users"},
        401: {"description": "Unauthorized"}
    }
})
@get_current_user
def get_users(current_user=None, session=None):
    try:
        users = session.query(User).all()
        if not users:
            return jsonify({"detail": "No users found..!"}), 401
        
        return jsonify([{
            "id": u.id,
            "name": u.name,
            "email": u.email
        } for u in users]), 200
    finally:
        session.close()

@router.route("/profile", methods=["GET"])
@swag_from({
    "tags": ["User"],
    "security": [{"Bearer": []}],
    "responses": {
        200: {"description": "User profile"},
        401: {"description": "Unauthorized"}
    }
})
@get_current_user
def profile(current_user=None, session=None):
    try:
        return jsonify({"name": current_user.name, "email": current_user.email}), 200
    finally:
        if session:
            session.close()
