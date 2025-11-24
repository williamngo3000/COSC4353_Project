from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import datetime
import os
from datetime import timezone

# Initialize SQLAlchemy
db = SQLAlchemy()

# ------------------------------------------------
# USER CREDENTIALS MODEL
# ------------------------------------------------
class UserCredentials(db.Model):
    __tablename__ = 'user_credentials'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), nullable=False, unique=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default='volunteer')

    # Relationship to UserProfile (1-to-1)
    profile = db.relationship('UserProfile', back_populates='user', uselist=False)

    # Relationship to VolunteerHistory (1-to-many)
    volunteer_history = db.relationship('VolunteerHistory', back_populates='user')
    
    # Relationship to EventInvites (1-to-many)
    invites = db.relationship('EventInvite', back_populates='user')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


# ------------------------------------------------
# USER PROFILE MODEL
# ------------------------------------------------
class UserProfile(db.Model):
    __tablename__ = 'user_profile'

    id = db.Column(db.Integer, db.ForeignKey('user_credentials.id'), primary_key=True)
    full_name = db.Column(db.String(120), nullable=False)
    address1 = db.Column(db.String(255)) # Changed from 'address'
    address2 = db.Column(db.String(255)) # Added
    city = db.Column(db.String(100))
    state = db.Column(db.String(2))
    zipcode = db.Column(db.String(10))
    skills = db.Column(db.String(255))
    preferences = db.Column(db.String(255))
    availability = db.Column(db.String(255))

    # Back reference to UserCredentials
    user = db.relationship('UserCredentials', back_populates='profile')


# ------------------------------------------------
# EVENT DETAILS MODEL
# ------------------------------------------------
class EventDetails(db.Model):
    __tablename__ = 'event_details'

    id = db.Column(db.Integer, primary_key=True)
    event_name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)

    # --- NEW: Added location field ---
    location = db.Column(db.String(255), nullable=True)

    city = db.Column(db.String(100))
    state = db.Column(db.String(50))
    zipcode = db.Column(db.String(20))
    skills = db.Column(db.String(255))
    required_skills = db.Column(db.String(255), nullable=True)  # For frontend compatibility
    preferences = db.Column(db.String(255))
    availability = db.Column(db.String(255))
    urgency = db.Column(db.String(50), nullable=True, default='Medium')  # Low, Medium, High, Critical

    # --- NEW: Added event_date, required by frontend ---
    event_date = db.Column(db.Date, nullable=True)

    # --- NEW: Volunteer management fields ---
    volunteer_limit = db.Column(db.Integer, nullable=True)  # NULL = unlimited
    current_volunteers = db.Column(db.Integer, nullable=True, default=0)
    status = db.Column(db.String(50), nullable=True, default='open')  # open, closed

    # Relationship to volunteer history
    volunteers = db.relationship('VolunteerHistory', back_populates='event')

    # Relationship to invites
    invites = db.relationship('EventInvite', back_populates='event')


# ------------------------------------------------
# VOLUNTEER HISTORY MODEL
# ------------------------------------------------
class VolunteerHistory(db.Model):
    __tablename__ = 'volunteer_history'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user_credentials.id'))
    event_id = db.Column(db.Integer, db.ForeignKey('event_details.id'))
    
    # --- FIX: Use timezone-aware datetime ---
    participation_date = db.Column(db.DateTime, default=lambda: datetime.datetime.now(timezone.utc))

    # Relationships
    user = db.relationship('UserCredentials', back_populates='volunteer_history')
    event = db.relationship('EventDetails', back_populates='volunteers')


# ------------------------------------------------
# STATES MODEL
# ------------------------------------------------
class States(db.Model):
    __tablename__ = 'states'

    code = db.Column(db.String(10), primary_key=True)
    name = db.Column(db.String(100))


# ------------------------------------------------
# NEW: EVENT INVITE MODEL
# ------------------------------------------------
class EventInvite(db.Model):
    __tablename__ = 'event_invite'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user_credentials.id'), nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey('event_details.id'), nullable=False)

    # 'pending', 'accepted', 'declined'
    status = db.Column(db.String(50), nullable=False, default='pending')

    # 'user_request' (volunteer clicked signup), 'admin_invite' (admin invited user)
    type = db.Column(db.String(50), nullable=False, default='user_request')

    # Track if volunteer completed the event
    completed = db.Column(db.Boolean, default=False, nullable=False)

    created_at = db.Column(db.DateTime, default=lambda: datetime.datetime.now(timezone.utc))

    # Relationships
    user = db.relationship('UserCredentials', back_populates='invites')
    event = db.relationship('EventDetails', back_populates='invites')

# ------------------------------------------------
# NEW: NOTIFICATION MODEL
# ------------------------------------------------
class Notification(db.Model):
    __tablename__ = 'notification'
    
    id = db.Column(db.Integer, primary_key=True)
    message = db.Column(db.String(255), nullable=False)
    
    # 'info', 'success', 'warning', 'error'
    type = db.Column(db.String(50), nullable=False, default='info')
    
    created_at = db.Column(db.DateTime, default=lambda: datetime.datetime.now(timezone.utc))
    read = db.Column(db.Boolean, default=False, nullable=False)


# ------------------------------------------------
# DATABASE INITIALIZATION (for direct execution)
# ------------------------------------------------
if __name__ == "__main__":
    try:
        from app import app
        with app.app_context():
            db.create_all()
            print("Database initialized at:", os.path.abspath("volunteer.db"))
    except ImportError:
        print("Run this file from the main 'app.py' context to initialize the database.")
