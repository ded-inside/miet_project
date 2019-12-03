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

    # certificates = relationship("Certificate", back_populates="owner")

    # entries = relationship("ScheduleEntry", back_populates="owner")

    about = db.Column(db.String, default="")

    def __init__(self, login, password_hash):
        self.login = login
        self.password_hash = password_hash


class ScheduleEntry(db.Model):
    __tablename__ = "schedule_entries"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    owner_id = db.Column(db.Integer, db.ForeignKey("members.id"))
    # owner = relationship("Member", back_populates="entries")

    date = db.Column(db.DateTime, nullable=False)
    duration = db.Column(db.DateTime)

    buyer_id = db.Column(db.Integer, db.ForeignKey("members.id"), nullable=True)

    price = db.Column(db.Integer)

    name = db.Column(db.String)


class Transaction(db.Model):
    __tablename__ = "transactions"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    cert_id = db.column(db.Integer, db.ForeignKey("certificates.id"))

    from_id = db.Column(db.Integer, db.ForeignKey("members.id"))

    to_id = db.Column(db.Integer, db.ForeignKey("members.id"))

    date_time = db.Column(db.DateTime)


class Certificate(db.Model):
    __tablename__ = "certificates"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    owner_id = db.Column(db.Integer, db.ForeignKey("members.id"))
    # owner = relationship("Member", back_populates="certificates")


class Log(db.Model):
    __tablename__ = "logs"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
