from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), default="free")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    role = db.Column(db.String(10))  # user / bot
    content = db.Column(db.Text)
    emotion = db.Column(db.String(50))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class Mood(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    value = db.Column(db.Integer)
    date = db.Column(db.DateTime, default=datetime.utcnow)

class UserProfile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    anxiety_level = db.Column(db.String(50))
    common_topics = db.Column(db.Text)
    goals = db.Column(db.Text)

class CBTEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    situation = db.Column(db.Text)
    thought = db.Column(db.Text)
    emotion = db.Column(db.Text)
    rational_response = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
