from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import datetime

from app import db

Base = declarative_base()


class Session(db.Model):
    __tablename__ = "sessions"

    id = db.Column(db.Integer, primary_key=True)

    user = relationship("Member", uselist=False, back_populates="session")

    token = db.Column(db.String)

    expires_at = db.Column(db.DateTime, default=datetime.datetime.now()+datetime.timedelta(hours=1))


class Member(db.Model):
    __tablename__ = "members"

    id = db.Column(db.Integer, primary_key=True)

    login = db.Column(db.String, nullable=False)
    password_hash = db.Column(db.String, nullable=False)

    session_id = db.Column(db.Integer, db.ForeignKey("sessions.id"), nullable=True)
    session = relationship("Session", back_populates="user")

    certificates = relationship("Certificate", back_populates="owner")

    schedule_id = db.Column(db.Integer, db.ForeignKey("schedules.id"))
    schedule = relationship("Schedule", back_populates="owner")

    entries = relationship("ScheduleEntry", back_populates="owner")

    about = db.Column(db.String,default="")

    def __init__(self, login, password_hash):
        self.login = login
        self.password_hash = password_hash


class ScheduleEntry(db.Model):
    __tablename__ = "schedule_entries"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    owner_id = db.Column(db.Integer, db.ForeignKey("members.id"))
    owner = relationship("Member", back_populates="entries")

    date = db.Column(db.DateTime, nullable=False)

    buyer_id = db.Column(db.Integer, db.ForeignKey("members.id"))

    name = db.Column(db.String)


class Transaction(db.Model):
    __tablename__ = "transactions"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    from_id = db.Column(db.Integer, db.ForeignKey("members.id"))

    to_id = db.Column(db.Integer, db.ForeignKey("members.id"))

#
# class Club(db.Model):
#     pass


class Certificate(db.Model):
    __tablename__ = "certificates"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    owner_id = db.Column(db.Integer, db.ForeignKey("members.id"))
    owner = relationship("Member", back_populates="certificates")


class Log(db.Model):
    __tablename__ = "logs"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
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