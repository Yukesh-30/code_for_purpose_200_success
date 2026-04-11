import os
from flask import Flask
from models import db, User, BusinessUser, BusinessProfile
from dotenv import load_dotenv

load_dotenv(override=True)

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

with app.app_context():
    # Make sure business 1 exists
    b1 = BusinessProfile.query.get(1)
    if not b1:
        print("Business 1 not found. Please create it first.")
    else:
        users = User.query.all()
        for u in users:
            existing = BusinessUser.query.filter_by(user_id=u.id, business_id=1).first()
            if not existing:
                print(f"Mapping user {u.email} to Business 1")
                bu = BusinessUser(user_id=u.id, business_id=1, role='owner', is_primary=True)
                db.session.add(bu)
        db.session.commit()
        print("Done mapping existing users.")
