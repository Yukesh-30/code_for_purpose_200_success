from __future__ import annotations

import os

from dotenv import load_dotenv
from flask import Flask
from flask_cors import CORS

from models import db

load_dotenv()


def create_app() -> Flask:
    app = Flask(__name__)

    # ── Database ──────────────────────────────────────────────────────────────
    db_url = (
        os.getenv("DATABASE_URL", "")
        .replace("&channel_binding=require", "")
        .replace("?channel_binding=require&", "?")
    )
    app.config["SQLALCHEMY_DATABASE_URI"] = db_url
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
        "pool_pre_ping": True,
        "pool_recycle": 300,
        "connect_args": {"sslmode": "require"},
    }
    db.init_app(app)

    # ── CORS — allow all localhost ports (dev) ────────────────────────────────
    CORS(app, origins=r"http://localhost:.*", supports_credentials=True)

    # ── Blueprints ────────────────────────────────────────────────────────────
    from routes.auth_routes     import auth_bp
    from routes.business_routes import business_bp
    from routes.upload_routes   import upload_bp
    from routes.talk_to_data_routes import talk_bp
    from routes.dashboard_routes    import dashboard_bp

    app.register_blueprint(auth_bp,      url_prefix='/auth')
    app.register_blueprint(business_bp,  url_prefix='/business')
    app.register_blueprint(upload_bp,    url_prefix='/upload')
    app.register_blueprint(talk_bp)           # /chat  /forecast  /anomaly
    app.register_blueprint(dashboard_bp)      # /stats  /bank/*  /alerts

    # ── Health ────────────────────────────────────────────────────────────────
    @app.route('/health')
    def health():
        return {'status': 'ok', 'service': 'FlowSight AI', 'version': '2.1.0'}, 200

    @app.route('/')
    def home():
        return {'message': 'FlowSight AI Backend is Running!'}, 200

    return app


app = create_app()

if __name__ == '__main__':
    app.run(debug=True, port=5000)
