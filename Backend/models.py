from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import UniqueConstraint
from sqlalchemy.types import JSON
from werkzeug.security import generate_password_hash, check_password_hash
import datetime
from datetime import datetime
db = SQLAlchemy()


# User Credentials Model

class UserCredentials(db.Model):
    __tablename__ = 'user_credentials'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), nullable=False, unique=True, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default='volunteer')

    profile = db.relationship("UserProfile", back_populates = "user", uselist = False, cascade= "all, delete-orphan")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)



# Event Details Model

class EventDetails(db.Model):
    __tablename__ = 'event_details'
    id = db.Column(db.Integer, primary_key=True)
    event_name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=False)
    location = db.Column(db.Text, nullable=False)
    required_skills = db.Column(JSON, nullable=False, default=list)
    urgency = db.Column(db.String(20), nullable=False)
    event_date = db.Column(db.Date, nullable=False)
    volunteer_limit = db.Column(db.Integer, nullable=True)
    status = db.Column(db.String(10), nullable=False, default="open")



# User Profile Model

class UserProfile(db.Model):
    __tablename__ = 'user_profile'
    id = db.Column(db.Integer, db.ForeignKey('user_credentials.id'), primary_key=True)
    full_name = db.Column(db.String(120), nullable=False)
    address1 = db.Column(db.String(255), nullable=False)
    address2 = db.Column(db.String(255))
    city = db.Column(db.String(100), nullable=False)
    state = db.Column(db.String(2), nullable=False)
    zip_code = db.Column(db.String(10), nullable=False)
    phone = db.Column(db.String(25))
    skills = db.Column(JSON, nullable=False, default=list)
    preferences = db.Column(db.String(255))
    availability = db.Column(JSON, nullable=False, default=list)

    user = db.relationship("UserCredentials", back_populates="profile")



# Volunteer History Model

class VolunteerHistory(db.Model):
    __tablename__ = 'volunteer_history'
    id = db.Column(db.Integer, primary_key=True)
    user_email = db.Column(db.String(255), nullable=False, index=True)
    event_id = db.Column(db.Integer, db.ForeignKey('event_details.id'), nullable=False, index=True)
    participation_date = db.Column(db.DateTime, default=datetime.utcnow(), nullable=False)

    __table_args__ = (UniqueConstraint('user_email', 'event_id', name='uq_history_email_event'),)

# Invites

class Invite(db.Model):
    __tablename__ = 'invites'
    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('event_details.id'), nullable=False, index=True)
    user_email = db.Column(db.String(255), nullable=False, index=True)
    status = db.Column(db.String(10), nullable=False, default='pending')
    type = db.Column(db.String(20), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow(), nullable=False)
    completed = db.Column(db.Boolean, default=False, nullable=False)

    __table_args__ = (UniqueConstraint('event_id', 'user_email', name='uq_invite_event_email'),)


# Notifications
class Notification(db.Model):
    __tablename__ = 'notifications'
    id = db.Column(db.Integer, primary_key=True)
    message = db.Column(db.Text, nullable=False)
    type = db.Column(db.String(20), nullable=False, default='info')
    time = db.Column(db.DateTime, default=datetime.utcnow(), nullable=False)


# Activity Log
class ActivityLog(db.Model):
    __tablename__ = 'activity_log'
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(50), nullable=False)
    time = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    meta = db.Column(JSON)


# States Model

class States(db.Model):
    __tablename__ = 'states'
    code = db.Column(db.String(10), primary_key=True)
    name = db.Column(db.String(100), nullable=False)

