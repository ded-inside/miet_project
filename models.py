from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import datetime

from app import db

Base = declarative_base()

cross_table = db.Table('user_chat', db.metadata,
                       db.Column('user_id', db.Integer, db.ForeignKey("users.id")),
                       db.Column('chat_id', db.Integer, db.ForeignKey('chats.id'))
                       )


class Session(db.Model):
    __tablename__ = "sessions"

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    user = relationship("User", uselist=False, back_populates="session")


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)

    login = db.Column(db.String)
    password_hash = db.Column(db.String)

    session_id = db.Column(db.Integer, db.ForeignKey("session.id"))
    session = relationship("Session", uselist=False, back_populates="user")

    def __init__(self, username):
        self.username = username


class Admin(User):
    pass


class Member(User):
    pass


class Schedule(db.Model):
    pass


class ScheduleEntry(db.Model):
    pass


class Transaction(db.Model):
    pass


class Club(db.Model):
    pass


class Certificate(db.Model):
    pass


class Log(db.Model):
    pass

# class Chat(db.Model):
#     __tablename__ = "chats"
#
#     id = db.Column(db.Integer, primary_key=True)
#
#     name = db.Column(db.String)
#
#     users = relationship("User",
#                          secondary=cross_table,
#                          back_populates="chats")
#
#     created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
#
#     messages = relationship("Message", back_populates="chat")
#
#     def __init__(self, name):
#         self.name = name
#
#
# class Message(db.Model):
#     __tablename__ = "messages"
#
#     id = db.Column(db.Integer, primary_key=True)
#
#     chat = relationship("Chat", back_populates="messages")
#     chat_id = db.Column(db.Integer, db.ForeignKey('chats.id'))
#
#     author = relationship("User", back_populates="messages")
#     author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
#
#     text = db.Column(db.Text)
#
#     created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
#
#     def __init__(self, text):
#         self.text = text
