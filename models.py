from flask_login import UserMixin
from datetime import datetime
from . import db


class User(UserMixin, db.Model):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    name = db.Column(db.String(1000), nullable=False)
    lastname = db.Column(db.String(1000), nullable=False)
    position = db.Column(db.String(100))    # optional

    posts = db.relationship('Post', back_populates='author')

    def __repr__(self) -> str:
        return f"{self.id} {self.username} {self.password} {self.name}"


class Post(db.Model):
    __tablename__ = 'post'

    id = db.Column(db.Integer, primary_key=True)
    author_username = db.Column(db.String(100), nullable=False)
    editor_username = db.Column(db.String(100), nullable=False)
    created = db.Column(db.DateTime, nullable=False, default=datetime.now)
    edited = db.Column(db.DateTime, nullable=False, default=datetime.now)
    title = db.Column(db.String(80), nullable=False)
    body = db.Column(db.Text)

    author_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    author = db.relationship('User', back_populates='posts')
