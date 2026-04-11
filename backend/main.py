import os
from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv
from models import db
from routes.auth_routes import auth_bp
from routes.business_routes import business_bp
from routes.upload_routes import upload_bp
from routes.chatbot_routes import chatbot_bp
from routes.chat_routes import chat_bp
from routes.dashboard_routes import dashboard_bp
from routes.forecasting_routes import forecasting_bp
from routes.risk_routes import risk_bp
from routes.recommendation_routes import recommendation_bp

load_dotenv(override=True)

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
app.register_blueprint(chatbot_bp, url_prefix='/chatbot')
app.register_blueprint(chat_bp, url_prefix='/chat')
app.register_blueprint(dashboard_bp, url_prefix='/dashboard')
app.register_blueprint(forecasting_bp, url_prefix='/forecasting')
app.register_blueprint(risk_bp, url_prefix='/risk')
app.register_blueprint(recommendation_bp, url_prefix='/recommendation')
@app.route('/')
def home():
    return {"message": "FlowSight AI Backend is Running!"}

if __name__ == '__main__':
    with app.app_context():
        # Create tables if they don't exist
        db.create_all()
    app.run(debug=True, port=5000)
