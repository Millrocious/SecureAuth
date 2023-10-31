# models.py
from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql.functions import now

from app import login_manager, db, bcrypt


@login_manager.user_loader
def user_loader(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(40), unique=True, nullable=False)
    phone_number = db.Column(db.String(40), unique=False, nullable=False)
    email = db.Column(db.String(60), unique=True, nullable=False)
    password_hashed = db.Column(db.String(200), unique=False, nullable=False)

    @property
    def password(self):
        raise AttributeError('Is not readable')

    @password.setter
    def password(self, password):
        self.password_hashed = bcrypt.generate_password_hash(password).decode('utf-8')

    def __init__(self, username, phone_number, email, password):
        self.username = username
        self.phone_number = phone_number
        self.email = email
        self.password = password

    def verify_password(self, password):
        enc_password = password.encode('utf-8')
        return bcrypt.check_password_hash(self.password_hashed, enc_password)

    def __repr__(self):
        return self.email
