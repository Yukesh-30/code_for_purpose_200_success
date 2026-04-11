import os
from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv
from models import db
from routes.auth_routes import auth_bp
from routes.business_routes import business_bp
from routes.upload_routes import upload_bp

load_dotenv()

app = Flask(__name__)
CORS(app)

print("DATABASE_URL:", os.getenv("DATABASE_URL"))


# Database Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    "pool_pre_ping": True,
    "pool_recycle": 3600,
}

db.init_app(app)

# Register Blueprints
app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(business_bp, url_prefix='/business')
app.register_blueprint(upload_bp, url_prefix='/upload')

@app.route('/')
def home():
    return {"message": "FlowSight AI Backend is Running!"}

if __name__ == '__main__':
    with app.app_context():
        # Create tables if they don't exist
        db.create_all()
    app.run(debug=True, port=5000)
