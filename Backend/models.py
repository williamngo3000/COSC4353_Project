from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import datetime
from datetime import timezone
import os

db = SQLAlchemy()

# USER CREDENTIALS MODEL
class UserCredentials(db.Model):
    __tablename__ = 'user_credentials'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), nullable=False, unique=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default='volunteer')

    # Correct 1→1 mapping using ONLY back_populates
    profile = db.relationship(
        "UserProfile",
        uselist=False,
        back_populates="user",
        cascade="all, delete-orphan"
    )

    # Volunteer history (1→many)
    volunteer_history = db.relationship(
        "VolunteerHistory",
        back_populates="user",
        cascade="all, delete-orphan"
    )

    # Event invites (1→many)
    invites = db.relationship(
        "EventInvite",
        back_populates="user",
        cascade="all, delete-orphan"
    )

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)



# USER PROFILE MODEL
class UserProfile(db.Model):
    __tablename__ = 'user_profile'

    # FK must match parent table + back_populates
    id = db.Column(db.Integer, db.ForeignKey('user_credentials.id'), primary_key=True)

    full_name = db.Column(db.String(120), nullable=False)
    address1 = db.Column(db.String(255))
    address2 = db.Column(db.String(255))
    city = db.Column(db.String(100))
    state = db.Column(db.String(2))
    zipcode = db.Column(db.String(10))
    phone_number = db.Column(db.String(20), nullable=True)
    skills = db.Column(db.String(255))
    preferences = db.Column(db.String(255))
    availability = db.Column(db.String(255))

    # CORRECT — single relationship matching parent
    user = db.relationship("UserCredentials", back_populates="profile")


# EVENT DETAILS MODEL
class EventDetails(db.Model):
    __tablename__ = 'event_details'

    id = db.Column(db.Integer, primary_key=True)
    event_name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    location = db.Column(db.String(255))
    city = db.Column(db.String(100))
    state = db.Column(db.String(50))
    zipcode = db.Column(db.String(20))
    skills = db.Column(db.String(255))
    required_skills = db.Column(db.String(255))
    preferences = db.Column(db.String(255))
    availability = db.Column(db.String(255))
    urgency = db.Column(db.String(50), default="Medium")
    event_date = db.Column(db.Date)
    volunteer_limit = db.Column(db.Integer)
    current_volunteers = db.Column(db.Integer, default=0)
    status = db.Column(db.String(50), default="open")

    # History & Invites
    volunteers = db.relationship("VolunteerHistory", back_populates="event", cascade="all, delete-orphan")
    invites = db.relationship("EventInvite", back_populates="event", cascade="all, delete-orphan")



# VOLUNTEER HISTORY MODEL
class VolunteerHistory(db.Model):
    __tablename__ = 'volunteer_history'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user_credentials.id'))
    event_id = db.Column(db.Integer, db.ForeignKey('event_details.id'))
    participation_date = db.Column(
        db.DateTime,
        default=lambda: datetime.datetime.now(timezone.utc)
    )

    user = db.relationship("UserCredentials", back_populates="volunteer_history")
    event = db.relationship("EventDetails", back_populates="volunteers")


# STATES MODEL
class States(db.Model):
    __tablename__ = 'states'

    code = db.Column(db.String(10), primary_key=True)
    name = db.Column(db.String(100))


# EVENT INVITE MODEL
class EventInvite(db.Model):
    __tablename__ = 'event_invite'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user_credentials.id'), nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey('event_details.id'), nullable=False)
    status = db.Column(db.String(50), nullable=False, default="pending")
    type = db.Column(db.String(50), nullable=False, default="user_request")
    completed = db.Column(db.Boolean, nullable=False, default=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.datetime.now(timezone.utc))

    user = db.relationship("UserCredentials", back_populates="invites")
    event = db.relationship("EventDetails", back_populates="invites")


# NOTIFICATIONS MODEL
class Notification(db.Model):
    __tablename__ = 'notification'

    id = db.Column(db.Integer, primary_key=True)
    message = db.Column(db.String(255), nullable=False)
    type = db.Column(db.String(50), default="info")
    created_at = db.Column(db.DateTime, default=lambda: datetime.datetime.now(timezone.utc))
    read = db.Column(db.Boolean, default=False, nullable=False)

