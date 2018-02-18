import uuid
import datetime

from flask_sqlalchemy import SQLAlchemy

__all__ = ["db", "User", "Post", "Comment"]

db = SQLAlchemy()


# setup data model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    created = db.Column(db.DateTime, nullable=False, default=datetime.datetime.utcnow)

    def __repr__(self):
        return '<User username="%r">' % self.username


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(64), nullable=False)
    body = db.Column(db.Text(), nullable=False, default="")
    created = db.Column(db.DateTime, nullable=False, default=datetime.datetime.utcnow)
    author_user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    author_user = db.relationship('User', backref=db.backref('posts', lazy=True))


class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(64), nullable=False)
    created = db.Column(db.DateTime, nullable=False, default=datetime.datetime.utcnow)
    author_name = db.Column(db.String(80), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    post = db.relationship('Post', backref=db.backref('comments', lazy=True))

