from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import datetime
import os

# Initialize SQLAlchemy (app binds it in app2.py)
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
    address = db.Column(db.String(255))
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
    city = db.Column(db.String(100))
    state = db.Column(db.String(50))
    zipcode = db.Column(db.String(20))
    skills = db.Column(db.String(255))
    preferences = db.Column(db.String(255))
    availability = db.Column(db.String(255))

    # Relationship to volunteer history
    volunteers = db.relationship('VolunteerHistory', back_populates='event')


# ------------------------------------------------
# VOLUNTEER HISTORY MODEL
# ------------------------------------------------
class VolunteerHistory(db.Model):
    __tablename__ = 'volunteer_history'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user_credentials.id'))
    event_id = db.Column(db.Integer, db.ForeignKey('event_details.id'))
    participation_date = db.Column(db.DateTime, default=datetime.datetime.utcnow)

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
# DATABASE INITIALIZATION (for direct execution)
# ------------------------------------------------
if __name__ == "__main__":
    from app2 import app
    with app.app_context():
        db.create_all()
        print("✅ Database initialized at:", os.path.abspath("volunteer.db"))

