import os
from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv
from models import db
from routes.auth_routes import auth_bp

load_dotenv()

app = Flask(__name__)
CORS(app)

# Database Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# Register Blueprints
app.register_blueprint(auth_bp, url_prefix='/auth')

@app.route('/')
def home():
    return {"message": "FlowSight AI Backend is Running!"}

if __name__ == '__main__':
    with app.app_context():
        # Create tables if they don't exist
        db.create_all()
    app.run(debug=True, port=5000)
