from flask import Flask
from flasgger import Swagger
from app.database import db, create_tables_database
from app.routes.user_routes import router as user_router
from app.routes.product_routes import router as product_router
# Import models so SQLAlchemy can create tables
from app.models import user_model, product_model

# Initialize Flask app
app = Flask(__name__)

# Swagger config
app.config['SWAGGER'] = {
    'title': 'FlaskOffice API',
    'uiversion': 3
}

swagger = Swagger(app)

# Database configuration
DATABASE_URL = "postgresql://fastapi_user:1234@localhost:5432/fastapi_db"
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database
db.init_app(app)

# Create tables on startup
with app.app_context():
    create_tables_database(app)

# Register blueprints
app.register_blueprint(user_router)
app.register_blueprint(product_router)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8000)