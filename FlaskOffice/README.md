# FlaskOffice - Flask Conversion of FastAPI Office Project

This is a Flask conversion of the FastAPI Office project. The project structure and functionality remain the same, but the implementation uses Flask instead of FastAPI.

## Project Structure

```
FlaskOffice/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py              # Flask app initialization
│   │   ├── auth.py               # JWT authentication utilities
│   │   ├── database.py           # Database configuration (SQLAlchemy)
│   │   ├── dependancies.py       # Authentication decorator
│   │   ├── emailverfication.py   # OTP email sending
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── user_model.py     # User and EmailOTP models
│   │   │   └── product_model.py  # Detections model
│   │   ├── routes/
│   │   │   ├── __init__.py
│   │   │   ├── user_routes.py    # User authentication routes
│   │   │   └── product_routes.py # Product/detection routes
│   │   └── schemas/
│   │       ├── __init__.py
│   │       ├── user_schema.py    # Pydantic schemas for validation
│   │       └── product_schema.py
│   └── requirements.txt
├── storage/
│   ├── images/
│   └── videos/
├── weights/
├── config.ini
└── .gitignore
```

## Key Differences from FastAPI

1. **Framework**: Uses Flask instead of FastAPI
2. **Database**: Uses Flask-SQLAlchemy instead of SQLModel
3. **Routing**: Uses Blueprints instead of APIRouter
4. **Dependency Injection**: Uses decorators instead of Depends()
5. **Request Handling**: Uses Flask's request object instead of FastAPI's dependency injection
6. **Response**: Uses jsonify() and Flask response objects

## Installation

1. Install dependencies:
```bash
pip install -r backend/requirements.txt
```

2. Set up environment variables (create .env file):
```
EMAIL_SENDER=your_email@gmail.com
EMAIL_PASSWORD=your_app_password
```

3. Ensure PostgreSQL database is running and configured in `backend/app/database.py`

4. Run the application:
```bash
cd backend
python -m app.main
```

Or:
```bash
export FLASK_APP=app.main
flask run
```

## API Endpoints

### User Routes
- `POST /otp-registration` - Request OTP for registration
- `POST /verify-otp-register` - Verify OTP and complete registration
- `POST /login` - User login (returns JWT token)
- `GET /users` - Get all users (requires authentication)
- `GET /profile` - Get current user profile (requires authentication)

### Product Routes
- `POST /detect-image` - Upload image for YOLO detection (requires authentication)
- `GET /detections` - Get detection records
- `GET /download` - Download detection result image (requires authentication)
- `GET /detections-history` - Get detection history (requires authentication)
- `DELETE /detections/all` - Delete all detections (requires authentication)
- `DELETE /detections/id/<file_id>` - Delete specific detection (requires authentication)

## Authentication

All protected routes require a Bearer token in the Authorization header:
```
Authorization: Bearer <your_jwt_token>
```

## Notes

- The application uses JWT tokens for authentication
- OTP verification is required for user registration
- Image detection uses YOLO model from the weights folder
- Detection results are stored in the storage/images directory
