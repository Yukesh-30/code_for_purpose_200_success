import os
from flask import Flask
from models import db
from dotenv import load_dotenv
import sqlalchemy as sa

load_dotenv(override=True)

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

with app.app_context():
    res = db.session.execute(sa.text("SELECT pg_get_constraintdef(oid) FROM pg_constraint WHERE conname = 'business_users_role_check';")).fetchone()
    print('CONSTRAINT:', res)
