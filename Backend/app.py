import os
import re
import json
from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from pydantic import BaseModel, field_validator, ValidationError
from typing import List, Optional
from datetime import datetime, timezone # <-- Added timezone import

"""
Backend Flask application for the Volunteer Management System.
This app uses SQLAlchemy as the ORM to interact with a SQLite database.
"""

#App & DB Setup
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
CORS(app, origins=["http://localhost:5173", "http://127.0.0.1:5173"]) # Allow React frontend
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(BASE_DIR, 'volunteer_combined.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

#  SQLAlchemy Models (The new "DB") 

# Many-to-Many Association Tables
user_skills = db.Table('user_skills',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('skill_id', db.Integer, db.ForeignKey('skill.id'), primary_key=True)
)

event_skills = db.Table('event_skills',
    db.Column('event_id', db.Integer, db.ForeignKey('event.id'), primary_key=True),
    db.Column('skill_id', db.Integer, db.ForeignKey('skill.id'), primary_key=True)
)

user_event_history = db.Table('user_event_history',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('event_id', db.Integer, db.ForeignKey('event.id'), primary_key=True)
)

class User(db.Model):
    """
    Represents a user in the system (either 'volunteer' or 'admin').
    Holds login credentials and basic role information.
    """
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(80), nullable=False, default='volunteer')

    # --- Relationships ---
    profile = db.relationship('Profile', back_populates='user', uselist=False, cascade="all, delete-orphan")
    skills = db.relationship('Skill', secondary=user_skills, back_populates='users')
    availability = db.relationship('Availability', back_populates='user', cascade="all, delete-orphan")
    invites = db.relationship('Invite', back_populates='user', cascade="all, delete-orphan")
    completed_events = db.relationship('Event', secondary=user_event_history, back_populates='completed_by_users')

    def __repr__(self):
        return f'<User {self.email}>'

class Profile(db.Model):
    """
    Stores detailed personal and contact information for a User.
    This is linked one-to-one with a User.
    """
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    address1 = db.Column(db.String(200), nullable=False)
    address2 = db.Column(db.String(200))
    city = db.Column(db.String(100), nullable=False)
    state = db.Column(db.String(2), nullable=False)
    zip_code = db.Column(db.String(10), nullable=False)
    phone = db.Column(db.String(20))
    preferences = db.Column(db.Text)
    
    # Foreign Key
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), unique=True, nullable=False)
    # Relationship 
    user = db.relationship('User', back_populates='profile')

class Skill(db.Model):
    """
    Represents a single, unique skill that a user can possess
    or an event can require (e.g., "First Aid", "Logistics").
    """
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    
    #Relationships
    users = db.relationship('User', secondary=user_skills, back_populates='skills')
    events = db.relationship('Event', secondary=event_skills, back_populates='required_skills')

class Availability(db.Model):
    """
    Represents a single date when a user is available to volunteer.
    A user can have many availability entries.
    """
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False) # Store as date object
    
    #Foreign Key
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    # Relationship
    user = db.relationship('User', back_populates='availability')

class Event(db.Model):
    """
    Represents a volunteering event that requires volunteers.
    Contains event details, location, date, and status.
    """
    id = db.Column(db.Integer, primary_key=True)
    event_name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    location = db.Column(db.String(200), nullable=False)
    urgency = db.Column(db.String(50), nullable=False)
    event_date = db.Column(db.Date, nullable=False) # Store as date object
    volunteer_limit = db.Column(db.Integer) # Nullable
    status = db.Column(db.String(50), default='open') # open, closed

    # Relationships
    required_skills = db.relationship('Skill', secondary=event_skills, back_populates='events')
    invites = db.relationship('Invite', back_populates='event', cascade="all, delete-orphan")
    completed_by_users = db.relationship('User', secondary=user_event_history, back_populates='completed_events')

class Invite(db.Model):
    """
    Tracks the status of an invitation or request for a user to join an event.
    This links a User to an Event.
    """
    id = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.String(50), default='pending') # pending, accepted, declined
    type = db.Column(db.String(50)) # admin_invite, user_request
    completed = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc)) 
    
    # --- Foreign Keys ---
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'), nullable=False)
    
    # --- Relationships ---
    user = db.relationship('User', back_populates='invites')
    event = db.relationship('Event', back_populates='invites')

class Notification(db.Model):
    """
    A simple notification message for the system (e.g., "New user registered").
    Used to populate the admin dashboard notification feed.
    """
    id = db.Column(db.Integer, primary_key=True)
    message = db.Column(db.String(500), nullable=False)
    type = db.Column(db.String(50), default='info') # info, success, warning, error
    time = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    read = db.Column(db.Boolean, default=False)

class ActivityLog(db.Model):
    """
    Logs significant actions taken within the application for auditing.
    (e.g., "registration", "event_created").
    """
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(100), nullable=False)
    time = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    details = db.Column(db.String(500)) # Store details as JSON string or simple text


#Pydantic Models for Data Validation

class UserRegistration(BaseModel):
    """Validates the data required for a new user to register."""
    email: str
    password: str

    @field_validator('email')
    @classmethod
    def email_must_be_valid(cls, value):
        if not re.match(r"[^@]+@[^@]+\.[^@]+", value):
            raise ValueError('Email is not valid')
        return value

    @field_validator('password')
    @classmethod
    def password_complexity(cls, value):
        if len(value) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not any(char.isdigit() for char in value):
            raise ValueError('Password must contain at least one number')
        if not any(char.isupper() for char in value):
            raise ValueError('Password must contain at least one uppercase letter')
        return value

class UserLogin(BaseModel):
    """Validates the data required for a user to log in."""
    email: str
    password: str

class ProfileUpdate(BaseModel):
    """Validates the data for creating or updating a user's profile."""
    full_name: str
    address1: str
    address2: Optional[str] = None
    city: str
    state: str
    zip_code: str
    skills: List[str] # List of skill names
    preferences: Optional[str] = None
    availability: List[str] # List of date strings "YYYY-MM-DD"
    phone: Optional[str] = None

    @field_validator('full_name')
    @classmethod
    def full_name_length(cls, value):
        if not (1 <= len(value) <= 50):
            raise ValueError('Full name must be between 1 and 50 characters')
        return value

    @field_validator('zip_code')
    @classmethod
    def zip_code_format(cls, value):
        if not (5 <= len(value) <= 9 and value.isdigit()): 
            raise ValueError('Zip code must be a 5 to 9 digit number')
        return value

class EventCreation(BaseModel):
    """Validates the data required for an admin to create a new event."""
    event_name: str
    description: str
    location: str
    required_skills: List[str] # List of skill names
    urgency: str
    event_date: str # Date string "YYYY-MM-DD"
    volunteer_limit: Optional[int] = None

    @field_validator('volunteer_limit')
    @classmethod
    def validate_volunteer_limit(cls, value):
        if value is not None and value < 1:
            raise ValueError('Volunteer limit must be at least 1')
        return value
    
    @field_validator('event_date')
    @classmethod
    def validate_date_format(cls, value):
        try:
            datetime.strptime(value, "%Y-%m-%d") 
            return value
        except ValueError:
            raise ValueError('Event date must be in YYYY-MM-DD format')


# --- Helper Functions (Rewritten for SQLAlchemy) ---

def add_notification(message, type="info"):
    """
    Add a notification to the DB, keeping only the last 50.

    Args:
        message (str): The content of the notification.
        type (str, optional): The type of notification (e.g., "info", "success", "error"). 
                             Defaults to "info".

    Returns:
        Notification: The newly created Notification object.
    """
    new_notif = Notification(message=message, type=type)
    db.session.add(new_notif)
    
    # Keep only the last 50
    count = Notification.query.count()
    if count > 50:
        oldest = Notification.query.order_by(Notification.time.asc()).limit(count - 50).all()
        for n in oldest:
            db.session.delete(n)
    db.session.commit()
    return new_notif

def add_activity(type, **kwargs):
    """
    Add an activity to the DB, keeping only the last 50.

    Args:
        type (str): The type of activity (e.g., "registration", "event_created").
        **kwargs: Additional details to be stored as a JSON string.

    Returns:
        ActivityLog: The newly created ActivityLog object.
    """
    details_str = json.dumps(kwargs) if kwargs else None
    new_activity = ActivityLog(type=type, details=details_str)
    db.session.add(new_activity)
    
    # Keep only the last 50
    count = ActivityLog.query.count()
    if count > 50:
        oldest = ActivityLog.query.order_by(ActivityLog.time.asc()).limit(count - 50).all()
        for a in oldest:
            db.session.delete(a)
    db.session.commit()
    return new_activity

def get_event_volunteer_count(event_id):
    """
    Get the current number of accepted volunteers for a specific event.

    Args:
        event_id (int): The ID of the event to check.

    Returns:
        int: The count of users with an 'accepted' invite for the event.
    """
    return Invite.query.filter_by(event_id=event_id, status='accepted').count()

def check_and_close_event(event_id):
    """
    Check if an event should be closed (either past date or volunteer limit reached).
    If so, updates the event's status to 'closed' in the database.

    Args:
        event_id (int): The ID of the event to check.

    Returns:
        bool: True if the event was closed, False otherwise.
    """
    event = db.session.get(Event, event_id) 
    if not event or event.status == "closed":
        return False

    # Check if event date has passed
    today = datetime.now(timezone.utc).date() #Use timezone-aware comparison
    if event.event_date < today:
        event.status = "closed"
        db.session.commit()
        return True

    # Check if volunteer limit reached
    if event.volunteer_limit is not None:
        current_count = get_event_volunteer_count(event_id)
        if current_count >= event.volunteer_limit:
            event.status = "closed"
            db.session.commit()
            return True
    return False

def check_all_events_status():
    #Check and auto-close all open events that should be closed.
    open_events = Event.query.filter_by(status='open').all()
    for event in open_events:
        check_and_close_event(event.id)

# --- API Endpoints ---

@app.route('/register', methods=['POST'])
def register_user():
    """
    Register a new user (volunteer or admin).
    The role is automatically set to 'admin' if the email is 'admin@example.com',
    otherwise it defaults to 'volunteer'.
    
    Method: POST
    Payload:
        {
            "email": "user@example.com",
            "password": "StrongPassword1"
        }
    Success Response (201):
        {
            "message": "Registration successful",
            "user": {"email": "user@example.com", "role": "volunteer"}
        }
    Error Responses:
        400: Validation error (e.g., weak password, invalid email).
        409: User with this email already exists.
        500: Internal server error.
    """
    try:
        user_data = UserRegistration(**request.json)
        
        if User.query.filter_by(email=user_data.email).first():
            return jsonify({"message": "User with this email already exists"}), 409

        new_user = User(
            email=user_data.email,
            password_hash=generate_password_hash(user_data.password),
            role="admin" if user_data.email == "admin@example.com" else "volunteer"
        )
        db.session.add(new_user)
        db.session.commit()

        add_notification(f"New user registered: {user_data.email}", "info")
        add_activity("registration", user=user_data.email)

        return jsonify({
            "message": "Registration successful", 
            "user": {"email": new_user.email, "role": new_user.role}
        }), 201
        
    except ValidationError as e:
        return jsonify({"message": "Validation error", "errors": json.loads(e.json())}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "An internal error occurred", "error": str(e)}), 500

@app.route('/login', methods=['POST'])
def login_user():
    """
    Authenticate a user and return their details.
    
    Method: POST
    Payload:
        {
            "email": "user@example.com",
            "password": "StrongPassword1"
        }
    Success Response (200):
        {
            "message": "Login successful",
            "user": {
                "email": "user@example.com",
                "role": "volunteer",
                "profileComplete": true
            }
        }
    Error Responses:
        400: Validation error.
        401: Invalid email or password.
        500: Internal server error.
    """
    try:
        login_data = UserLogin(**request.json)
        user = User.query.filter_by(email=login_data.email).first()

        if not user or not check_password_hash(user.password_hash, login_data.password):
            return jsonify({"message": "Invalid email or password"}), 401
        
        profile_complete = user.profile is not None

        return jsonify({
            "message": "Login successful",
            "user": {
                "email": user.email, 
                "role": user.role,
                "profileComplete": profile_complete
            }
        }), 200
    except ValidationError as e:
        return jsonify({"message": "Validation error", "errors": json.loads(e.json())}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "An internal error occurred", "error": str(e)}), 500

@app.route('/profile/<string:email>', methods=['GET', 'PUT'])
def user_profile(email):
    """
    Handle user profile operations (GET and PUT).
    
    ---
    Method: GET
    Params:
        email (str): The email of the user to fetch.
    Success Response (200):
        {
            "full_name": "John Doe",
            "address1": "123 Main St",
            "address2": "Apt 4B",
            "city": "Houston",
            "state": "TX",
            "zip_code": "77002",
            "phone": "(555) 123-4567",
            "preferences": "...",
            "skills": ["First Aid", "Logistics"],
            "availability": ["2026-12-01", "2026-12-15"]
        }
        (Returns {} if profile is not yet created)
    Error Responses:
        404: User not found.
    
    ---
    Method: PUT
    Params:
        email (str): The email of the user to update.
    Payload:
        (Body must match the ProfileUpdate Pydantic model)
    Success Response (200):
        {"message": "Profile updated successfully"}
    Error Responses:
        400: Validation error.
        404: User not found.
        500: Internal server error.
    """
    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({"message": "User not found"}), 404

    if request.method == 'GET':
        if not user.profile:
            return jsonify({}), 200 #Return empty profile if not set
        
        profile_data = {
            "full_name": user.profile.full_name,
            "address1": user.profile.address1,
            "address2": user.profile.address2,
            "city": user.profile.city,
            "state": user.profile.state,
            "zip_code": user.profile.zip_code,
            "phone": user.profile.phone,
            "preferences": user.profile.preferences,
            "skills": [skill.name for skill in user.skills],
            "availability": [avail.date.strftime("%Y-%m-%d") for avail in user.availability]
        }
        return jsonify(profile_data), 200

    if request.method == 'PUT':
        try:
            profile_data = ProfileUpdate(**request.json)
            
            if not user.profile:
                user.profile = Profile(user_id=user.id)
            
            user.profile.full_name = profile_data.full_name
            user.profile.address1 = profile_data.address1
            user.profile.address2 = profile_data.address2
            user.profile.city = profile_data.city
            user.profile.state = profile_data.state
            user.profile.zip_code = profile_data.zip_code
            user.profile.phone = profile_data.phone
            user.profile.preferences = profile_data.preferences

            # Update skills
            user.skills.clear()
            for skill_name in profile_data.skills:
                skill = Skill.query.filter_by(name=skill_name).first()
                if skill:
                    user.skills.append(skill)
            
            # Update availability
            Availability.query.filter_by(user_id=user.id).delete()
            for date_str in profile_data.availability:
                avail_date = datetime.strptime(date_str, "%Y-%m-%d").date()
                user.availability.append(Availability(date=avail_date))

            db.session.commit()
            return jsonify({"message": "Profile updated successfully"}), 200
            
        except ValidationError as e:
            return jsonify({"message": "Validation error", "errors": json.loads(e.json())}), 400
        except Exception as e:
            db.session.rollback()
            return jsonify({"message": "An internal error occurred", "error": str(e)}), 500

@app.route('/events', methods=['GET', 'POST'])
def manage_events():
    """
    Handle event operations (GET all events and POST new event).
    
    ---
    Method: GET
    Success Response (200):
        [
            {
                "id": 1,
                "event_name": "Community Food Drive",
                "description": "...",
                "location": "...",
                "required_skills": ["Logistics", "Event Setup"],
                "urgency": "High",
                "event_date": "2026-12-01",
                "volunteer_limit": 10,
                "status": "open",
                "current_volunteers": 0
            }
        ]
    
    ---
    Method: POST
    Payload:
        (Body must match the EventCreation Pydantic model)
        {
            "event_name": "New Event",
            "description": "A new event.",
            "location": "Someplace",
            "required_skills": ["Tech Support"],
            "urgency": "Medium",
            "event_date": "2026-10-31",
            "volunteer_limit": 5
        }
    Success Response (201):
        {"message": "Event created successfully", "event_id": 2}
    Error Responses:
        400: Validation error.
        500: Internal server error.
    """
    if request.method == 'GET':
        check_all_events_status()
        events = Event.query.all()
        event_list = []
        for event in events:
            event_data = {
                "id": event.id,
                "event_name": event.event_name,
                "description": event.description,
                "location": event.location,
                "required_skills": [skill.name for skill in event.required_skills],
                "urgency": event.urgency,
                "event_date": event.event_date.strftime("%Y-%m-%d"),
                "volunteer_limit": event.volunteer_limit,
                "status": event.status,
                "current_volunteers": get_event_volunteer_count(event.id)
            }
            event_list.append(event_data)
        return jsonify(event_list), 200

    if request.method == 'POST':
        try:
            event_data = EventCreation(**request.json)
            
            new_event = Event(
                event_name=event_data.event_name,
                description=event_data.description,
                location=event_data.location,
                urgency=event_data.urgency,
                event_date=datetime.strptime(event_data.event_date, "%Y-%m-%d").date(),
                volunteer_limit=event_data.volunteer_limit,
                status="open"
            )
            
            db.session.add(new_event)
            db.session.flush() 

            for skill_name in event_data.required_skills:
                skill = Skill.query.filter_by(name=skill_name).first()
                if skill:
                    new_event.required_skills.append(skill)
            
            db.session.commit()

            add_notification(f"New event created: {new_event.event_name}", "success")
            add_activity("event_created", event=new_event.event_name)

            return jsonify({"message": "Event created successfully", "event_id": new_event.id}), 201
            
        except ValidationError as e:
            return jsonify({"message": "Validation error", "errors": json.loads(e.json())}), 400
        except Exception as e:
            db.session.rollback()
            return jsonify({"message": "An internal error occurred", "error": str(e)}), 500

@app.route('/data/skills', methods=['GET'])
def get_skills():
    """
    Get a list of all available skills from the database, sorted alphabetically.
    
    Method: GET
    Success Response (200):
        ["Catering", "Event Setup", "First Aid", "Logistics", ...]
    """
    skills = Skill.query.order_by(Skill.name).all()
    return jsonify([skill.name for skill in skills]), 200

@app.route('/data/urgency', methods=['GET'])
def get_urgency_levels():
    """
    Get the static list of allowed event urgency levels.
    
    Method: GET
    Success Response (200):
        ["Low", "Medium", "High", "Critical"]
    """
    return jsonify(["Low", "Medium", "High", "Critical"]), 200

@app.route('/matching/<int:event_id>', methods=['GET'])
def get_volunteer_matches(event_id):
    """
    Find matching volunteers for a specific event.
    
    Matches are based on:
    1. User role is 'volunteer'.
    2. User has a completed profile.
    3. User has at least one skill required by the event.
    4. User is available on the event date.
    
    Method: GET
    Params:
        event_id (int): The ID of the event to match against.
    Success Response (200):
        [
            {
                "email": "volunteer@example.com",
                "full_name": "John Doe",
                "skills": ["First Aid", "Logistics"]
            }
        ]
    Error Responses:
        404: Event not found.
    """
    event = db.session.get(Event, event_id) 
    if not event:
        return jsonify({"message": "Event not found"}), 404

    # Find users who have at least one of the required skills
    required_skill_ids = [skill.id for skill in event.required_skills]
    users_with_skill = db.session.query(User).join(user_skills).filter(
        user_skills.c.skill_id.in_(required_skill_ids)
    ).distinct()

    # Find users who are available on the event date
    users_with_availability = users_with_skill.join(Availability).filter(
        Availability.date == event.event_date
    )
    
    # Filter for role 'volunteer' and must have a profile
    matched_users = users_with_availability.join(Profile).filter(
        User.role == 'volunteer'
    ).all()

    matches = []
    for user in matched_users:
        matches.append({
            "email": user.email, 
            "full_name": user.profile.full_name,
            "skills": [skill.name for skill in user.skills]
        })

    return jsonify(matches), 200

@app.route('/history/<string:email>', methods=['GET'])
def get_volunteer_history(email):
    """
    Get the event history for a specific volunteer.
    Returns a list of events the user has marked as completed.
    
    Method: GET
    Params:
        email (str): The email of the user to fetch history for.
    Success Response (200):
        [
            {
                "id": 1,
                "event_name": "Community Food Drive",
                "description": "Annual food drive.",
                "location": "Downtown Community Center",
                "event_date": "2026-12-01"
            }
        ]
    Error Responses:
        404: User not found.
    """
    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({"message": "User not found"}), 404

    history_events = []
    for event in user.completed_events:
        history_events.append({
            "id": event.id,
            "event_name": event.event_name,
            "description": event.description,
            "location": event.location,
            "event_date": event.event_date.strftime("%Y-%m-%d")
        })
    return jsonify(history_events), 200


@app.route('/notifications', methods=['GET'])
def get_notifications():
    """
    Get all notifications, sorted most recent first.
    
    Method: GET
    Success Response (200):
        [
            {
                "id": 1,
                "message": "New user registered: ...",
                "type": "info",
                "time": "2025-10-29 16:00:00",
                "read": false
            }
        ]
    Error Responses:
        500: Internal server error.
    """
    try:
        notifications = Notification.query.order_by(Notification.time.desc()).all()
        
        notif_list = []
        for n in notifications:
            notif_list.append({
                "id": n.id,
                "message": n.message,
                "type": n.type,
                "time": n.time.strftime("%Y-%m-%d %H:%M:%S"),
                "read": n.read
            })
        
        return jsonify(notif_list), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "An internal error occurred", "error": str(e)}), 500

@app.route('/notifications/<int:notification_id>/read', methods=['PUT'])
def mark_notification_read(notification_id):
    """
    Mark a specific notification as read.
    
    Method: PUT
    Params:
        notification_id (int): The ID of the notification to mark.
    Success Response (200):
        {"message": "Notification marked as read", "id": 1}
    Error Responses:
        404: Notification not found.
        500: Internal server error.
    """
    try:
        notification = db.session.get(Notification, notification_id) 
        if not notification:
            return jsonify({"message": "Notification not found"}), 404
        
        notification.read = True
        db.session.commit()
        
        return jsonify({"message": "Notification marked as read", "id": notification_id}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "An internal error occurred", "error": str(e)}), 500

@app.route('/statistics', methods=['GET'])
def get_statistics():
    """
    Get high-level dashboard statistics for the admin panel.
    
    Method: GET
    Success Response (200):
        {
            "total_users": 2,
            "total_events": 2,
            "total_skills": 13,
            "open_events": 2
        }
    Error Responses:
        500: Internal server error.
    """
    try:
        user_count = User.query.count()
        event_count = Event.query.count()
        skill_count = Skill.query.count()
        
        open_events = Event.query.filter_by(status='open').count()
        
        stats = {
            "total_users": user_count,
            "total_events": event_count,
            "total_skills": skill_count,
            "open_events": open_events
        }
        
        return jsonify(stats), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "An internal error occurred", "error": str(e)}), 500


# Database Initializer

def init_db():
    """
    Create all database tables (if they don't exist) and populate
    static/seed data like default skills and admin/volunteer users.
    """
    db.create_all()

    # Populate Skills
    if Skill.query.count() == 0:
        print("Populating skills...")
        SKILLS_LIST = [
            "First Aid", "Logistics", "Event Setup", "Public Speaking", 
            "Registration", "Tech Support", "Catering", "Marketing", 
            "Fundraising", "Photography", "Social Media", "Team Leadership", "Translation"
        ]
        for skill_name in SKILLS_LIST:
            db.session.add(Skill(name=skill_name))
        db.session.commit()

    # Populate default Admin user
    if not User.query.filter_by(email="admin@example.com").first():
        print("Creating admin user...")
        admin = User(
            email="admin@example.com",
            password_hash=generate_password_hash("AdminPassword1"),
            role="admin"
        )
        admin.profile = Profile(
            full_name="Jane Smith", address1="456 Admin Ave", city="Houston",
            state="TX", zip_code="77002", phone="(555) 987-6543"
        )
        db.session.add(admin)
        db.session.commit()

    #Populate default Volunteer user
    if not User.query.filter_by(email="volunteer@example.com").first():
        print("Creating volunteer user...")
        vol = User(
            email="volunteer@example.com",
            password_hash=generate_password_hash("Password1"),
            role="volunteer"
        )
        vol.profile = Profile(
            full_name="John Doe", address1="123 Main St", address2="Apt 4B",
            city="Houston", state="TX", zip_code="77002", phone="(555) 123-4567"
        )
        db.session.add(vol)
        db.session.flush()

        #Add skills
        skill1 = Skill.query.filter_by(name="First Aid").first()
        skill2 = Skill.query.filter_by(name="Logistics").first()
        if skill1: vol.skills.append(skill1)
        if skill2: vol.skills.append(skill2)
        
        #Add availability
        vol.availability.append(Availability(date=datetime.strptime("2026-12-01", "%Y-%m-%d").date()))
        vol.availability.append(Availability(date=datetime.strptime("2026-12-15", "%Y-%m-%d").date()))
        
        db.session.commit()

    #Populate default Events
    if Event.query.count() == 0:
        print("Populating events...")
        event1 = Event(
            event_name="Community Food Drive", description="Annual food drive.",
            location="Downtown Community Center", urgency="High", 
            event_date=datetime.strptime("2026-12-01", "%Y-%m-%d").date(), 
            volunteer_limit=10, status="open"
        )
        db.session.add(event1)
        db.session.flush()
        
        skill_log = Skill.query.filter_by(name="Logistics").first()
        skill_set = Skill.query.filter_by(name="Event Setup").first()
        if skill_log: event1.required_skills.append(skill_log)
        if skill_set: event1.required_skills.append(skill_set)
        
        event2 = Event(
            event_name="Park Cleanup Day", description="Help clean Memorial Park.",
            location="Memorial Park", urgency="Medium",
            event_date=datetime.strptime("2026-11-20", "%Y-%m-%d").date(),
            status="open"
        )
        db.session.add(event2)
        db.session.flush()

        if skill_set: event2.required_skills.append(skill_set)
        
        db.session.commit()
        
        # Add history for volunteer
        vol = User.query.filter_by(email="volunteer@example.com").first()
        event1 = Event.query.filter_by(event_name="Community Food Drive").first()
        if vol and event1:
            vol.completed_events.append(event1)
            db.session.commit()


#Main Execution 
if __name__ == '__main__':
    with app.app_context():
        init_db()  #Create and populate DB
        print(f"Database initialized at: {os.path.join(BASE_DIR, 'volunteer_combined.db')}")
    app.run(debug=True, port=5001)