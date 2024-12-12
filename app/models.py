import datetime
from .ext import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash


class Users(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(15), unique=True, nullable=False)
    email = db.Column(db.String(30), unique=True, nullable=False)
    password = db.Column(db.String(20), nullable=False)
    age = db.Column(db.Integer, nullable=False)

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def __repr__(self):
        return f'User {self.username}'



class Secrets(db.Model):
    __tablename__ = 'secrets'
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(300), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, unique=True, default=datetime.datetime.now)

    def __repr__(self):
        return f'Secret {self.id}: {self.content}'
