import os
import re
import json
import csv
import io
from flask import Flask, jsonify, request, make_response
from flask_cors import CORS
from werkzeug.security import check_password_hash
from pydantic import BaseModel, field_validator, ValidationError, Field
from typing import List, Optional
from datetime import datetime, date, timezone
import sys # Import sys for logging

# Import all models and the db object from your models.py
# Update: includes EventInvite and Notification module because apparently these didn't exist back then - Will
from models import (
    db, 
    UserCredentials, 
    UserProfile, 
    EventDetails, 
    VolunteerHistory, 
    States,
    EventInvite,
    Notification
)

# App & DB Setup
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__)
# Make sure your React app is running on 5173
CORS(app, origins=["http://localhost:5173", "http://127.0.0.1:5173"])
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(BASE_DIR, 'volunteer.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Link the db object from models.py to our app
db.init_app(app)


# --- Helper Function to create notifications ---
def create_notification(message, msg_type='info'):
    """Helper to create a new notification."""
    try:
        # We must be inside an app context to do database operations
        with app.app_context():
            new_notif = Notification(message=message, type=msg_type)
            db.session.add(new_notif)
            db.session.commit()
    except Exception as e:
        print(f"Error creating notification: {e}", file=sys.stderr)
        db.session.rollback()

# --- Pydantic Models for Data Validation ---

class UserRegistration(BaseModel):
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
        return value

class UserLogin(BaseModel):
    email: str
    password: str

class ProfileUpdate(BaseModel):
    model_config = {"arbitrary_types_allowed": True}
    
    # All fields optional for partial updates
    full_name: Optional[str] = None 
    address1: Optional[str] = None
    address2: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = Field(default=None, validation_alias='zip_code')
    skills: Optional[str] = None
    preferences: Optional[str] = None
    availability: Optional[str] = None

    # Convert lists to comma-separated strings - handles both list input and string input
    '''
        This later changed for some aspects bc it broke code; I modified the aspects, keeping this root one because it seemed like less work and more efficient
        - Will
    '''
    @field_validator('skills', 'availability', mode='before')
    @classmethod
    def convert_list_to_string(cls, value):
        if value is None or value == "":
            return None
        if isinstance(value, list):
            filtered = [str(v).strip() for v in value if v and str(v).strip()]
            return ', '.join(filtered) if filtered else None
        if isinstance(value, str):
            cleaned = value.strip()
            return cleaned if cleaned else None
        return str(value)
    
    # Validate zip code format
    @field_validator('zip_code', mode='before')
    @classmethod
    def validate_zipcode(cls, value):
        if value is None or value == "":
            return None
        value_str = str(value).strip()
        if value_str == "":
            return None
        if not (value_str.isdigit() and (len(value_str) == 5 or len(value_str) == 9)):
            raise ValueError('Zip code must be 5 or 9 digits')
        return value_str
    
    # Clean up string fields
    @field_validator('full_name', 'address1', 'address2', 'city', 'state', 'preferences', mode='before')
    @classmethod
    def clean_strings(cls, value):
        if value is None or value == "":
            return None
        if isinstance(value, str):
            cleaned = value.strip()
            return cleaned if cleaned else None
        return value
class EventCreation(BaseModel):
    '''
        Modified some categories from List to String because it was throwing errors - Will
    '''
    event_name: str
    description: Optional[str] = None
    location: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zipcode: Optional[str] = None
    skills: Optional[str] = None
    required_skills: Optional[str] = None
    preferences: Optional[str] = None
    availability: Optional[str] = None
    urgency: Optional[str] = None
    event_date: Optional[str] = None
    volunteer_limit: Optional[int] = None
    status: Optional[str] = 'open'

    # Convert lists to comma-separated strings
    @field_validator('skills', 'availability', 'required_skills', mode='before')
    @classmethod
    def convert_list_to_string(cls, value):
        if value is None:
            return None
        if isinstance(value, list):
            return ', '.join(str(v) for v in value if v)
        return value

    @field_validator('event_date', mode='before')
    @classmethod
    def validate_date(cls, value):
        if value is None:
            return None
        try:
            # Check if it's a valid YYYY-MM-DD string
            datetime.strptime(value, '%Y-%m-%d')
            return value
        except ValueError:
            raise ValueError('Event date must be in YYYY-MM-DD format')

    @field_validator('urgency', mode='before')
    @classmethod
    def validate_urgency(cls, value):
        if value is None:
            return 'Medium'
        if value not in ['Low', 'Medium', 'High', 'Critical']:
            return 'Medium'
        return value


class EventUpdate(BaseModel):
    """
        Updated Model for updating events - all fields are optional for partial updates in case Admin wants to change only one aspect
    """
    event_name: Optional[str] = None
    description: Optional[str] = None
    location: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zipcode: Optional[str] = None
    skills: Optional[str] = None
    required_skills: Optional[str] = None
    preferences: Optional[str] = None
    availability: Optional[str] = None
    urgency: Optional[str] = None
    event_date: Optional[str] = None
    volunteer_limit: Optional[int] = None
    status: Optional[str] = None

    # Convert lists to comma-separated strings
    @field_validator('skills', 'availability', 'required_skills', mode='before')
    @classmethod
    def convert_list_to_string(cls, value):
        # Handle None and empty strings
        if value is None or value == '':
            return None
        if isinstance(value, list):
            return ', '.join(str(v) for v in value if v)
        return value

    @field_validator('event_date', mode='before')
    @classmethod
    def validate_date(cls, value):
        # Handle None and empty strings
        if value is None or value == '':
            return None
        try:
            datetime.strptime(value, '%Y-%m-%d')
            return value
        except ValueError:
            raise ValueError('Event date must be in YYYY-MM-DD format')

    @field_validator('urgency', mode='before')
    @classmethod
    def validate_urgency(cls, value):
        # Handle None and empty strings
        if value is None or value == '':
            return None
        if value not in ['Low', 'Medium', 'High', 'Critical']:
            return 'Medium'
        return value


class InviteUpdate(BaseModel):
    status: str

    @field_validator('status')
    @classmethod
    def validate_status(cls, value):
        if value not in ('accepted', 'declined'):
            raise ValueError("Status must be 'accepted' or 'declined'")
        return value
# --- API Endpoints ---

@app.route('/register', methods=['POST'])
def register_user():
    """Register a new user (admin or volunteer)."""
    try:
        user_data = UserRegistration(**request.json)
    except ValidationError as e:
        return jsonify({"message": "Validation error", "errors": json.loads(e.json())}), 400

    if UserCredentials.query.filter_by(email=user_data.email).first():
        return jsonify({"message": "User with this email already exists"}), 409

    try:
        new_user = UserCredentials(
            email=user_data.email,
            role="admin" if user_data.email == "admin@example.com" else "volunteer"
        )
        new_user.set_password(user_data.password)
        db.session.add(new_user)
        db.session.commit()
        
        # Create a notification for the admin
        create_notification(f"New user registered: {new_user.email}", 'info')
        
        return jsonify({"message": "Registration successful", "user": {"email": new_user.email, "role": new_user.role}}), 201
    
    except Exception as e:
        db.session.rollback()
        print(f"--- 500 ERROR IN /register ---: {e}", file=sys.stderr)
        return jsonify({"message": "An internal error occurred", "error": str(e)}), 500


@app.route('/login', methods=['POST'])
def login_user():
    """Log in a user."""
    try:
        login_data = UserLogin(**request.json)
    except ValidationError as e:
        return jsonify({"message": "Validation error", "errors": json.loads(e.json())}), 400

    try:
        user = UserCredentials.query.filter_by(email=login_data.email).first()

        if not user or not user.check_password(login_data.password):
            return jsonify({"message": "Invalid email or password"}), 401

        # Check if a profile exists
        profile_complete = db.session.get(UserProfile, user.id) is not None

        return jsonify({
            "message": "Login successful",
            "user": {
                "email": user.email,
                "role": user.role,
                "profileComplete": profile_complete
            }
        }), 200
    
    except Exception as e:
        print(f"--- 500 ERROR IN /login ---: {e}", file=sys.stderr)
        return jsonify({"message": "An internal error occurred", "error": str(e)}), 500


@app.route('/profile/<string:email>', methods=['GET', 'PUT'])
def user_profile(email):
    """Get or Update a user's profile."""
    user_creds = UserCredentials.query.filter_by(email=email).first()
    if not user_creds:
        return jsonify({"message": "User not found"}), 404

    if request.method == 'GET':
        profile = db.session.get(UserProfile, user_creds.id)
        if not profile:
            return jsonify({}), 200
        
        # Convert comma-separated strings back to lists
        skills_list = [s.strip() for s in profile.skills.split(',')] if profile.skills else []
        availability_list = [a.strip() for a in profile.availability.split(',')] if profile.availability else []

        return jsonify({
            "full_name": profile.full_name,
            "address1": profile.address1,
            "address2": profile.address2,
            "city": profile.city,
            "state": profile.state,
            "zip_code": profile.zipcode,
            "skills": skills_list,
            "preferences": profile.preferences,
            "availability": availability_list
        }), 200

    if request.method == 'PUT':
        try:
            profile_data = ProfileUpdate(**request.json)
            update_data = profile_data.model_dump(exclude_unset=True)

        except ValidationError as e:
            return jsonify({"message": "Validation error", "errors": json.loads(e.json())}), 400

        try:
            profile = db.session.get(UserProfile, user_creds.id)
            
            if not profile:
                # Creating new profile - full_name required
                if 'full_name' not in update_data:
                    return jsonify({"message": "Validation error", "errors": {"full_name": "Full name is required to create a profile."}}), 400
                
                profile = UserProfile(id=user_creds.id)
                db.session.add(profile)

            # Apply all updates
            for key, value in update_data.items():
                if key == 'zip_code':
                    setattr(profile, 'zipcode', value)
                else:
                    setattr(profile, key, value)

            db.session.commit()
            return jsonify({"message": "Profile updated successfully"}), 200
        
        except Exception as e:
            db.session.rollback()
            print(f"--- 500 ERROR IN PUT /profile ---: {e}", file=sys.stderr)
            return jsonify({"message": "An internal error occurred", "error": str(e)}), 500

@app.route('/events', methods=['GET', 'POST'])
def manage_events():
    """Get all events or create a new event."""
    if request.method == 'GET':
        try:
            events = EventDetails.query.all()
            event_list = []
            for event in events:
                # Count current volunteers (accepted invites)
                current_vol_count = EventInvite.query.filter_by(event_id=event.id, status='accepted').count()

                event_list.append({
                    "id": event.id,
                    "event_name": event.event_name,
                    "description": event.description,
                    "location": event.location,
                    "city": event.city,
                    "state": event.state,
                    "zipcode": event.zipcode,
                    "skills": event.skills,
                    "required_skills": event.required_skills,
                    "preferences": event.preferences,
                    "availability": event.availability,
                    "urgency": event.urgency,
                    "event_date": event.event_date.strftime('%Y-%m-%d') if event.event_date else None,
                    "volunteer_limit": event.volunteer_limit,
                    "current_volunteers": current_vol_count,
                    "status": event.status
                })
            return jsonify(event_list), 200
        except Exception as e:
            print(f"--- 500 ERROR IN GET /events ---: {e}", file=sys.stderr)
            return jsonify({"message": "An internal error occurred", "error": str(e)}), 500

    if request.method == 'POST':
        try:
            print(f"--- POST /events REQUEST DATA ---: {request.json}", file=sys.stderr)
            event_data = EventCreation(**request.json)
        except ValidationError as e:
            print(f"--- VALIDATION ERROR IN POST /events ---: {e.json()}", file=sys.stderr)
            return jsonify({"message": "Validation error", "errors": json.loads(e.json())}), 400

        try:
            new_event = EventDetails(
                event_name=event_data.event_name,
                description=event_data.description,
                location=event_data.location,
                city=event_data.city,
                state=event_data.state,
                zipcode=event_data.zipcode,
                skills=event_data.skills,
                required_skills=event_data.required_skills,
                preferences=event_data.preferences,
                availability=event_data.availability,
                urgency=event_data.urgency or 'Medium',
                event_date=datetime.strptime(event_data.event_date, '%Y-%m-%d').date() if event_data.event_date else None,
                volunteer_limit=event_data.volunteer_limit,
                current_volunteers=0,
                status=event_data.status or 'open'
            )
            db.session.add(new_event)
            db.session.commit()
            return jsonify({"message": "Event created successfully", "event_id": new_event.id}), 201

        except Exception as e:
            db.session.rollback()
            print(f"--- 500 ERROR IN POST /events ---: {e}", file=sys.stderr)
            return jsonify({"message": "An internal error occurred", "error": str(e)}), 500


@app.route('/events/<int:event_id>', methods=['GET', 'PUT', 'DELETE'])
def manage_event_by_id(event_id):
    """Get, update, or delete a single event by its ID."""

    if request.method == 'GET':
        try:
            event = db.session.get(EventDetails, event_id)
            if not event:
                return jsonify({"message": "Event not found"}), 404

            # Count current volunteers (accepted invites)
            current_vol_count = EventInvite.query.filter_by(event_id=event.id, status='accepted').count()

            return jsonify({
                "id": event.id,
                "event_name": event.event_name,
                "description": event.description,
                "location": event.location,
                "city": event.city,
                "state": event.state,
                "zipcode": event.zipcode,
                "skills": event.skills,
                "required_skills": event.required_skills,
                "preferences": event.preferences,
                "availability": event.availability,
                "urgency": event.urgency,
                "event_date": event.event_date.strftime('%Y-%m-%d') if event.event_date else None,
                "volunteer_limit": event.volunteer_limit,
                "current_volunteers": current_vol_count,
                "status": event.status
            }), 200
        except Exception as e:
            print(f"--- 500 ERROR IN GET /events/{event_id} ---: {e}", file=sys.stderr)
            return jsonify({"message": "An internal error occurred", "error": str(e)}), 500

    if request.method == 'PUT':
        try:
            event = db.session.get(EventDetails, event_id)
            if not event:
                return jsonify({"message": "Event not found"}), 404

            # Validate input with Pydantic (all fields optional for updates)
            try:
                print(f"--- PUT /events/{event_id} REQUEST DATA ---: {request.json}", file=sys.stderr)
                # OLD: event_data = EventCreation(**request.json)
                # NEW: Use EventUpdate model which has all fields optional
                event_data = EventUpdate(**request.json)
            except ValidationError as e:
                print(f"--- VALIDATION ERROR IN PUT /events/{event_id} ---: {e.json()}", file=sys.stderr)
                return jsonify({"message": "Validation error", "errors": json.loads(e.json())}), 400

            # OLD: Update event fields one by one
            # event.event_name = event_data.event_name
            # event.description = event_data.description
            # event.location = event_data.location
            # event.city = event_data.city
            # event.state = event_data.state
            # event.zipcode = event_data.zipcode
            # event.skills = event_data.skills
            # event.required_skills = event_data.required_skills
            # event.preferences = event_data.preferences
            # event.availability = event_data.availability
            # event.urgency = event_data.urgency or 'Medium'
            # event.event_date = datetime.strptime(event_data.event_date, '%Y-%m-%d').date() if event_data.event_date else None
            # event.volunteer_limit = event_data.volunteer_limit
            # if event_data.status:
            #     event.status = event_data.status

            # NEW: Update only provided fields
            update_dict = event_data.model_dump(exclude_unset=True)
            for key, value in update_dict.items():
                if key == 'event_date' and value is not None:
                    setattr(event, key, datetime.strptime(value, '%Y-%m-%d').date())
                else:
                    setattr(event, key, value)

            db.session.commit()
            return jsonify({"message": "Event updated successfully"}), 200

        except Exception as e:
            db.session.rollback()
            print(f"--- 500 ERROR IN PUT /events/{event_id} ---: {e}", file=sys.stderr)
            return jsonify({"message": "An internal error occurred", "error": str(e)}), 500

    if request.method == 'DELETE':
        try:
            event = db.session.get(EventDetails, event_id)
            if not event:
                return jsonify({"message": "Event not found"}), 404

            # Delete all associated invites first
            EventInvite.query.filter_by(event_id=event_id).delete()

            # Delete all volunteer history records
            VolunteerHistory.query.filter_by(event_id=event_id).delete()

            # Delete the event
            db.session.delete(event)
            db.session.commit()

            return jsonify({"message": "Event deleted successfully"}), 200

        except Exception as e:
            db.session.rollback()
            print(f"--- 500 ERROR IN DELETE /events/{event_id} ---: {e}", file=sys.stderr)
            return jsonify({"message": "An internal error occurred", "error": str(e)}), 500


# --- NEW: Get all volunteers for a specific event ---
@app.route('/events/<int:event_id>/volunteers', methods=['GET'])
def get_event_volunteers(event_id):
    """Get all approved volunteers for a specific event."""
    try:
        event = db.session.get(EventDetails, event_id)
        if not event:
            return jsonify({"message": "Event not found"}), 404

        # Find all 'accepted' invites for this event
        accepted_invites = EventInvite.query.filter_by(event_id=event_id, status='accepted').all()
        
        volunteer_list = []
        for invite in accepted_invites:
            user = invite.user # Get the user from the relationship
            if user and user.profile:
                volunteer_list.append({
                    "user_id": user.id,
                    "email": user.email,
                    "full_name": user.profile.full_name,
                    "skills": user.profile.skills
                })
            
        return jsonify(volunteer_list), 200
    except Exception as e:
        print(f"--- 500 ERROR IN GET /events/{event_id}/volunteers ---: {e}", file=sys.stderr)
        return jsonify({"message": "An internal error occurred", "error": str(e)}), 500


@app.route('/invites', methods=['GET', 'POST'])
def manage_invites():
    """GET: Fetch all invites (for admin). POST: Create a new invite (signup)."""
    
    if request.method == 'GET':
        try:
            status = request.args.get('status')
            invite_type = request.args.get('type')

            query = EventInvite.query
            if status:
                query = query.filter_by(status=status)
            if invite_type:
                query = query.filter_by(type=invite_type)
            
            invites = query.order_by(EventInvite.created_at.desc()).all()
            
            result = []
            for invite in invites:
                result.append({
                    "id": invite.id,
                    "user_id": invite.user_id,
                    "event_id": invite.event_id,
                    "status": invite.status,
                    "type": invite.type,
                    "completed": invite.completed,
                    "user_email": invite.user.email,
                    "event_name": invite.event.event_name
                })
            return jsonify(result), 200
        except Exception as e:
            print(f"--- 500 ERROR IN GET /invites ---: {e}", file=sys.stderr)
            return jsonify({"message": "An internal error occurred", "error": str(e)}), 500

    if request.method == 'POST':
        try:
            data = request.json
            if not data:
                return jsonify({"message": "Validation error: No data provided"}), 400
            
            # Get user identifier and event_id from request
            email = data.get('email')
            user_id = data.get('user_id')
            event_id = data.get('event_id')
            invite_type = data.get('type', 'user_request')  # Default to 'user_request' if not provided

            # Validation
            if not email and not user_id:
                return jsonify({"message": "Validation error: 'email' or 'user_id' is required"}), 400
            if not event_id:
                return jsonify({"message": "Validation error: 'event_id' is required"}), 400

            # Find the user (try by email first, then by user_id)
            if email:
                user_creds = UserCredentials.query.filter_by(email=email).first()
            else:
                user_creds = db.session.get(UserCredentials, user_id)
            
            if not user_creds:
                return jsonify({"message": "User not found"}), 404
            
            # Use the found user's email for the notification
            email = user_creds.email

            # Find the event
            event = db.session.get(EventDetails, event_id)
            if not event:
                return jsonify({"message": "Event not found"}), 404

            # Check if already signed up (in history)
            existing_history = VolunteerHistory.query.filter_by(user_id=user_creds.id, event_id=event_id).first()
            if existing_history:
                return jsonify({"message": "Already signed up for this event"}), 409

            # Check if an invite of the same type is already pending
            existing_invite = EventInvite.query.filter_by(user_id=user_creds.id, event_id=event_id, status='pending', type=invite_type).first()
            if existing_invite:
                return jsonify({"message": "An invite of this type is already pending for this user and event"}), 409

            # Create a new invite
            new_invite = EventInvite(
                user_id=user_creds.id,
                event_id=event_id,
                status='pending',
                type=invite_type
            )
            db.session.add(new_invite)

            # Create a notification
            if invite_type == 'admin_invite':
                create_notification(f"Admin invited {email} to {event.event_name}", 'info')
            else:
                create_notification(f"Volunteer {email} requested to join {event.event_name}", 'info')
            
            db.session.commit()
            return jsonify({"message": "Request sent, awaiting admin approval"}), 201

        except Exception as e:
            db.session.rollback()
            print(f"--- 500 ERROR IN POST /invites ---: {e}", file=sys.stderr)
            return jsonify({"message": "An internal error occurred", "error": str(e)}), 500


@app.route('/invites/<int:invite_id>', methods=['PUT', 'DELETE'])
def manage_invite(invite_id):
    """Update or delete an invite."""

    if request.method == 'PUT':
        try:
            invite = db.session.get(EventInvite, invite_id)
            if not invite:
                return jsonify({"message": "Invite not found"}), 404

            # Validate input
            try:
                invite_data = InviteUpdate(**request.json)
            except ValidationError as e:
                return jsonify({"message": "Validation error", "errors": json.loads(e.json())}), 400

            # Update status
            old_status = invite.status
            invite.status = invite_data.status

            # If changing from pending to accepted, add to volunteer history
            if old_status == 'pending' and invite_data.status == 'accepted':
                # Check if already in history
                existing_history = VolunteerHistory.query.filter_by(
                    user_id=invite.user_id,
                    event_id=invite.event_id
                ).first()

                if not existing_history:
                    # Add to volunteer history
                    new_history = VolunteerHistory(
                        user_id=invite.user_id,
                        event_id=invite.event_id
                    )
                    db.session.add(new_history)

            db.session.commit()
            return jsonify({"message": "Invite updated successfully"}), 200

        except Exception as e:
            db.session.rollback()
            print(f"--- 500 ERROR IN PUT /invites/{invite_id} ---: {e}", file=sys.stderr)
            return jsonify({"message": "An internal error occurred", "error": str(e)}), 500

    if request.method == 'DELETE':
        try:
            invite = db.session.get(EventInvite, invite_id)
            if not invite:
                return jsonify({"message": "Invite not found"}), 404

            # Remove from volunteer history if exists
            VolunteerHistory.query.filter_by(
                user_id=invite.user_id,
                event_id=invite.event_id
            ).delete()

            # Delete the invite
            db.session.delete(invite)
            db.session.commit()

            return jsonify({"message": "Invite deleted successfully"}), 200

        except Exception as e:
            db.session.rollback()
            print(f"--- 500 ERROR IN DELETE /invites/{invite_id} ---: {e}", file=sys.stderr)
            return jsonify({"message": "An internal error occurred", "error": str(e)}), 500


@app.route('/invites/<int:invite_id>/complete', methods=['PUT'])
def update_invite_completion(invite_id):
    """Mark an invite as completed or not completed."""
    try:
        invite = db.session.get(EventInvite, invite_id)
        if not invite:
            return jsonify({"message": "Invite not found"}), 404

        # Get completed status from request body
        data = request.json
        if data is None or 'completed' not in data:
            return jsonify({"message": "Validation error: 'completed' field is required"}), 400

        completed = data.get('completed')
        if not isinstance(completed, bool):
            return jsonify({"message": "Validation error: 'completed' must be a boolean"}), 400

        # Update completion status
        invite.completed = completed
        db.session.commit()

        return jsonify({"message": "Completion status updated successfully"}), 200

    except Exception as e:
        db.session.rollback()
        print(f"--- 500 ERROR IN PUT /invites/{invite_id}/complete ---: {e}", file=sys.stderr)
        return jsonify({"message": "An internal error occurred", "error": str(e)}), 500


@app.route('/invites/user/<string:email>', methods=['GET'])
def get_user_invites(email):
    """Get all invites for a specific user by email."""
    try:
        # Find the user by email
        user_creds = UserCredentials.query.filter_by(email=email).first()
        if not user_creds:
            return jsonify({"message": "User not found"}), 404

        # Get query parameters for filtering
        status = request.args.get('status')
        invite_type = request.args.get('type')

        # Build query starting with user_id filter
        query = EventInvite.query.filter_by(user_id=user_creds.id)

        # Apply optional filters
        if status:
            query = query.filter_by(status=status)
        if invite_type:
            query = query.filter_by(type=invite_type)

        # Get filtered invites
        invites = query.all()

        result = []
        for invite in invites:
            invite_data = {
                "id": invite.id,
                "user_id": invite.user_id,
                "event_id": invite.event_id,
                "status": invite.status,
                "type": invite.type,
                "completed": invite.completed,
                "created_at": invite.created_at.isoformat(),
                "user_email": invite.user.email,
                "event_name": invite.event.event_name
            }

            # Include full event details if available
            if invite.event:
                invite_data["event"] = {
                    "id": invite.event.id,
                    "event_name": invite.event.event_name,
                    "description": invite.event.description,
                    "location": invite.event.location,
                    "event_date": invite.event.event_date.isoformat() if invite.event.event_date else None,
                    "required_skills": invite.event.required_skills,
                    "urgency": invite.event.urgency
                }

            result.append(invite_data)

        return jsonify(result), 200

    except Exception as e:
        print(f"--- 500 ERROR IN GET /invites/user/{email} ---: {e}", file=sys.stderr)
        return jsonify({"message": "An internal error occurred", "error": str(e)}), 500


@app.route('/user/<string:email>/events', methods=['GET'])
def get_user_events(email):
    """Get all accepted events for a user with completion status."""
    try:
        user_creds = UserCredentials.query.filter_by(email=email).first()
        if not user_creds:
            return jsonify({"message": "User not found"}), 404

        accepted_invites = EventInvite.query.filter_by(
            user_id=user_creds.id,
            status='accepted'
        ).all()

        event_list = []
        for invite in accepted_invites:
            event = invite.event
            if event:
                event_list.append({
                    "event_id": event.id,
                    "event_name": event.event_name,
                    "description": event.description,
                    "location": event.location,
                    "event_date": event.event_date.strftime('%Y-%m-%d') if event.event_date else None,
                    "required_skills": event.required_skills,
                    "completed": invite.completed
                })

        return jsonify({"events": event_list}), 200
    except Exception as e:
        print(f"--- 500 ERROR IN GET /user/{email}/events ---: {e}", file=sys.stderr)
        return jsonify({"message": "An internal error occurred", "error": str(e)}), 500


@app.route('/history/<string:email>', methods=['GET'])
def get_volunteer_history(email):
    """Get a specific volunteer's event history."""
    try:
        user_creds = UserCredentials.query.filter_by(email=email).first()
        if not user_creds:
            return jsonify({"message": "User not found"}), 404

        history_records = VolunteerHistory.query.filter_by(user_id=user_creds.id).all()

        event_list = []
        for record in history_records:
            event = record.event
            if event:
                event_list.append({
                    "event_id": event.id,
                    "event_name": event.event_name,
                    "participation_date": record.participation_date.isoformat()
                })

        return jsonify(event_list), 200
    except Exception as e:
        print(f"--- 500 ERROR IN GET /history/{email} ---: {e}", file=sys.stderr)
        return jsonify({"message": "An internal error occurred", "error": str(e)}), 500


@app.route('/matching/<int:event_id>', methods=['GET'])
def get_volunteer_matches(event_id):
    """Find volunteers who are a good match for an event."""
    try:
        event = db.session.get(EventDetails, event_id)
        if not event:
            return jsonify({"message": "Event not found"}), 404
            
        if not event.skills:
             return jsonify([]), 200 # No skills to match

        event_skills_set = set(skill.strip().lower() for skill in event.skills.split(','))
        
        # Get all volunteers
        volunteers = UserCredentials.query.filter_by(role='volunteer').all()
        
        matches = []
        for user_creds in volunteers:
            profile = user_creds.profile
            if not profile or not profile.skills:
                continue
                
            profile_skills_set = set(skill.strip().lower() for skill in profile.skills.split(','))
            
            # Check for any overlapping skills
            if event_skills_set.intersection(profile_skills_set):
                matches.append({
                    "email": user_creds.email,
                    "full_name": profile.full_name,
                    "skills": profile.skills 
                })
                
        return jsonify(matches), 200
    except Exception as e:
        print(f"--- 500 ERROR IN GET /matching/{event_id} ---: {e}", file=sys.stderr)
        return jsonify({"message": "An internal error occurred", "error": str(e)}), 500

# --- NEW: Get all users (for admin) ---
@app.route('/users', methods=['GET'])
def get_all_users():
    """Get a list of all users for the admin panel."""
    try:
        users = UserCredentials.query.all()
        user_list = []
        for user in users:
            profile = user.profile
            # Construct full address from address1, city, state, zipcode
            address_parts = []
            if profile:
                if profile.address1:
                    address_parts.append(profile.address1)
                if profile.city:
                    address_parts.append(profile.city)
                if profile.state:
                    address_parts.append(profile.state)
                if profile.zipcode:
                    address_parts.append(profile.zipcode)

            full_address = ", ".join(address_parts) if address_parts else "N/A"

            user_list.append({
                "id": user.id,
                "email": user.email,
                "role": user.role,
                "name": profile.full_name if profile else "N/A",  # Changed from "full_name" to "name"
                "address": full_address  # Added address field
            })
        return jsonify(user_list), 200
    except Exception as e:
        print(f"--- 500 ERROR IN GET /users ---: {e}", file=sys.stderr)
        return jsonify({"message": "An internal error occurred", "error": str(e)}), 500


@app.route('/users/<string:email>', methods=['PUT', 'DELETE'])
def manage_user(email):
    """Update or delete a user."""

    if request.method == 'PUT':
        try:
            user = UserCredentials.query.filter_by(email=email).first()
            if not user:
                return jsonify({"message": "User not found"}), 404

            data = request.json

            # Update role if provided
            if 'role' in data:
                user.role = data['role']

            # Update name if provided
            if 'name' in data:
                if user.profile:
                    user.profile.full_name = data['name']
                else:
                    # Create profile if it doesn't exist
                    new_profile = UserProfile(
                        id=user.id,
                        full_name=data['name']
                    )
                    db.session.add(new_profile)

            db.session.commit()
            return jsonify({"message": "User updated successfully"}), 200

        except Exception as e:
            db.session.rollback()
            print(f"--- 500 ERROR IN PUT /users/{email} ---: {e}", file=sys.stderr)
            return jsonify({"message": "An internal error occurred", "error": str(e)}), 500

    if request.method == 'DELETE':
        try:
            user = UserCredentials.query.filter_by(email=email).first()
            if not user:
                return jsonify({"message": "User not found"}), 404

            # Delete related records first
            if user.profile:
                db.session.delete(user.profile)

            # Delete volunteer history
            VolunteerHistory.query.filter_by(user_id=user.id).delete()

            # Delete invites
            EventInvite.query.filter_by(user_id=user.id).delete()

            # Delete the user
            db.session.delete(user)
            db.session.commit()

            return jsonify({"message": "User deleted successfully"}), 200

        except Exception as e:
            db.session.rollback()
            print(f"--- 500 ERROR IN DELETE /users/{email} ---: {e}", file=sys.stderr)
            return jsonify({"message": "An internal error occurred", "error": str(e)}), 500

# --- NEW: Notification Endpoints --- need to fix somehow!!!
@app.route('/notifications', methods=['GET'])
def get_notifications():
    """Get all unread notifications."""
    try:
        notifications = Notification.query.filter_by(read=False).order_by(Notification.created_at.desc()).all()
        notif_list = []
        for notif in notifications:
            notif_list.append({
                "id": notif.id,
                "message": notif.message,
                "type": notif.type,
                "created_at": notif.created_at.isoformat(),
                "read": notif.read
            })
        return jsonify(notif_list), 200
    except Exception as e:
        print(f"--- 500 ERROR IN GET /notifications ---: {e}", file=sys.stderr)
        return jsonify({"message": "An internal error occurred", "error": str(e)}), 500


@app.route('/notifications/<int:notif_id>/read', methods=['PUT'])
def mark_notification_read(notif_id):
    """Mark a notification as read."""
    try:
        notif = db.session.get(Notification, notif_id)
        if not notif:
            return jsonify({"message": "Notification not found"}), 404

        notif.read = True
        db.session.commit()
        return jsonify({"message": "Notification marked as read"}), 200
    except Exception as e:
        db.session.rollback()
        print(f"--- 500 ERROR IN PUT /notifications/{notif_id}/read ---: {e}", file=sys.stderr)
        return jsonify({"message": "An internal error occurred", "error": str(e)}), 500


# --- Activity Endpoint ---
@app.route('/activity', methods=['GET'])
def get_activity():
    """Get recent activity for admin dashboard."""
    try:
        activity_list = []

        # Get recent user registrations (last 50)
        recent_users = UserCredentials.query.order_by(UserCredentials.id.desc()).limit(50).all()
        for user in recent_users:
            # Approximate creation time - using ID as proxy for time since we don't have created_at
            activity_list.append({
                "type": "registration",
                "user": user.email,
                "event": None,
                "time": datetime.now(timezone.utc).isoformat()  # Placeholder time
            })

        # Get recent event signups (accepted invites)
        recent_signups = EventInvite.query.filter_by(status='accepted').order_by(EventInvite.created_at.desc()).limit(50).all()
        for invite in recent_signups:
            event = invite.event
            user = invite.user
            activity_list.append({
                "type": "event_signup",
                "user": user.email if user else "Unknown",
                "event": event.event_name if event else "Unknown Event",
                "time": invite.created_at.isoformat()
            })

        # Get recent event creations (last 50 events)
        recent_events = EventDetails.query.order_by(EventDetails.id.desc()).limit(50).all()
        for event in recent_events:
            # Approximate creation time - using ID as proxy
            activity_list.append({
                "type": "event_created",
                "user": "admin",  # Placeholder since we don't track who created events
                "event": event.event_name,
                "time": datetime.now(timezone.utc).isoformat()  # Placeholder time
            })

        # Sort by time descending and limit to most recent 20
        activity_list.sort(key=lambda x: x['time'], reverse=True)
        activity_list = activity_list[:20]

        return jsonify(activity_list), 200
    except Exception as e:
        print(f"--- 500 ERROR IN GET /activity ---: {e}", file=sys.stderr)
        return jsonify({"message": "An internal error occurred", "error": str(e)}), 500


# --- Static Data Endpoints ---

@app.route('/data/states', methods=['GET'])
def get_states():
    """Get all US states for dropdowns."""
    try:
        states = States.query.all()
        state_list = [{"code": s.code, "name": s.name} for s in states]
        return jsonify(state_list), 200
    except Exception as e:
        print(f"--- 500 ERROR IN GET /data/states ---: {e}", file=sys.stderr)
        return jsonify({"message": "An internal error occurred", "error": str(e)}), 500

SKILLS_LIST = [
    "First Aid", "Logistics", "Event Setup", "Public Speaking",
    "Registration", "Tech Support", "Catering", "Marketing",
    "Fundraising", "Photography", "Social Media", "Team Leadership", "Translation"
]
@app.route('/data/skills', methods=['GET'])
def get_skills():
    """Get a static list of available skills."""
    return jsonify(SKILLS_LIST), 200


# --- Reporting Endpoints (CSV) ---

@app.route('/reports/volunteer_history.csv', methods=['GET'])
def report_volunteer_history_csv():
    """Generate a CSV report of all volunteers and their history."""
    try:
        # Use an in-memory string buffer
        si = io.StringIO()
        cw = csv.writer(si)
        
        # Write Header
        headers = [
            "Volunteer Email", "Role", "Full Name", "City", "State", 
            "Skills", "Event Name", "Event Date", "Participation Date"
        ]
        cw.writerow(headers)
        
        # Get all volunteers
        volunteers = UserCredentials.query.filter_by(role='volunteer').all()
        
        for user in volunteers:
            profile = user.profile
            base_info = [
                user.email, user.role,
                profile.full_name if profile else "N/A",
                profile.city if profile else "N/A",
                profile.state if profile else "N/A",
                profile.skills if profile else "N/A"
            ]
            
            history = user.volunteer_history
            if not history:
                cw.writerow(base_info + ["N/A (No history)", "N/A", "N/A"])
            else:
                for record in history:
                    event = record.event
                    row = base_info + [
                        event.event_name if event else "Unknown Event",
                        event.event_date.strftime('%Y-%m-%d') if event and event.event_date else "N/A",
                        record.participation_date.isoformat()
                    ]
                    cw.writerow(row)
                    
        # Prepare response
        output = make_response(si.getvalue())
        today_str = datetime.now().strftime('%Y-%m-%d')
        output.headers["Content-Disposition"] = f"attachment; filename=volunteer_history_report_{today_str}.csv"
        output.headers["Content-type"] = "text/csv"
        return output
    except Exception as e:
        print(f"--- 500 ERROR IN CSV REPORT (Volunteers) ---: {e}", file=sys.stderr)
        return jsonify({"message": "An internal error occurred", "error": str(e)}), 500


@app.route('/reports/event_assignments.csv', methods=['GET'])
def report_event_assignments_csv():
    """Generate a CSV report of all events and their assigned volunteers."""
    try:
        si = io.StringIO()
        cw = csv.writer(si)
        
        # Write Header
        headers = [
            "Event ID", "Event Name", "Event Date", "Event Location",
            "Assigned Volunteer Email", "Volunteer Full Name", "Volunteer Skills"
        ]
        cw.writerow(headers)
        
        events = EventDetails.query.all()
        
        for event in events:
            base_info = [
                event.id,
                event.event_name,
                event.event_date.strftime('%Y-%m-%d') if event.event_date else "N/A",
                event.location if event.location else "N/A"
            ]
            
            # Get approved volunteers
            history = event.volunteers
            if not history:
                cw.writerow(base_info + ["N/A (No volunteer assigned)", "N/A", "N/A"])
            else:
                for record in history:
                    user = record.user
                    profile = user.profile
                    row = base_info + [
                        user.email,
                        profile.full_name if profile else "N/A",
                        profile.skills if profile else "N/A"
                    ]
                    cw.writerow(row)

        # Prepare response
        output = make_response(si.getvalue())
        today_str = datetime.now().strftime('%Y-%m-%d')
        output.headers["Content-Disposition"] = f"attachment; filename=event_assignments_report_{today_str}.csv"
        output.headers["Content-type"] = "text/csv"
        return output
    except Exception as e:
        print(f"--- 500 ERROR IN CSV REPORT (Events) ---: {e}", file=sys.stderr)
        return jsonify({"message": "An internal error occurred", "error": str(e)}), 500


# --- Reporting Endpoints (JSON for Preview) ---

@app.route('/reports/json/volunteer_history', methods=['GET'])
def report_volunteer_history_json():
    """Generate a JSON report of all volunteers and their history."""
    try:
        volunteers = UserCredentials.query.filter_by(role='volunteer').all()
        report_data = []
        
        for user in volunteers:
            profile = user.profile
            history = user.volunteer_history
            
            if not history:
                report_data.append({
                    "Email": user.email,
                    "Full Name": profile.full_name if profile else "N/A",
                    "Skills": profile.skills if profile else "N/A",
                    "Event Name": "N/A (No history)",
                    "Event Date": "N/A"
                })
            else:
                for record in history:
                    event = record.event
                    report_data.append({
                        "Email": user.email,
                        "Full Name": profile.full_name if profile else "N/A",
                        "Skills": profile.skills if profile else "N/A",
                        "Event Name": event.event_name if event else "Unknown Event",
                        "Event Date": event.event_date.strftime('%Y-%m-%d') if event and event.event_date else "N/A"
                    })
                    
        return jsonify(report_data), 200
    except Exception as e:
        print(f"--- 500 ERROR IN JSON REPORT (Volunteers) ---: {e}", file=sys.stderr)
        return jsonify({"message": "An internal error occurred", "error": str(e)}), 500

@app.route('/reports/json/event_assignments', methods=['GET'])
def report_event_assignments_json():
    """Generate a JSON report of all events and their assigned volunteers."""
    try:
        events = EventDetails.query.all()
        report_data = []
        
        for event in events:
            history = event.volunteers
            
            if not history:
                report_data.append({
                    "Event Name": event.event_name,
                    "Event Date": event.event_date.strftime('%Y-%m-%d') if event.event_date else "N/A",
                    "Location": event.location if event.location else "N/A",
                    "Volunteer": "N/A (No volunteer assigned)",
                    "Volunteer Skills": "N/A"
                })
            else:
                for record in history:
                    user = record.user
                    profile = user.profile
                    report_data.append({
                        "Event Name": event.event_name,
                        "Event Date": event.event_date.strftime('%Y-%m-%d') if event.event_date else "N/A",
                        "Location": event.location if event.location else "N/A",
                        "Volunteer": user.email,
                        "Volunteer Skills": profile.skills if profile else "N/A"
                    })
                    
        return jsonify(report_data), 200
    except Exception as e:
        print(f"--- 500 ERROR IN JSON REPORT (Events) ---: {e}", file=sys.stderr)
        return jsonify({"message": "An internal error occurred", "error": str(e)}), 500


# --- Database Initializer (Seeder) ---

def init_db():
    """Create all tables and populate static/seed data."""
    print("Checking database...")
    db.create_all()

    # Populate States
    if States.query.count() == 0:
        print("Populating states...")
        states_data = [
            States(code='AL', name='Alabama'), States(code='AK', name='Alaska'),
            States(code='AZ', name='Arizona'), States(code='AR', name='Arkansas'),
            States(code='CA', name='California'), States(code='CO', name='Colorado'),
            States(code='CT', name='Connecticut'), States(code='DE', name='Delaware'),
            States(code='FL', name='Florida'), States(code='GA', name='Georgia'),
            States(code='HI', name='Hawaii'), States(code='ID', name='Idaho'),
            States(code='IL', name='Illinois'), States(code='IN', name='Indiana'),
            States(code='IA', name='Iowa'), States(code='KS', name='Kansas'),
            States(code='KY', name='Kentucky'), States(code='LA', name='Louisiana'),
            States(code='ME', name='Maine'), States(code='MD', name='Maryland'),
            States(code='MA', name='Massachusetts'), States(code='MI', name='Michigan'),
            States(code='MN', name='Minnesota'), States(code='MS', name='Mississippi'),
            States(code='MO', name='Missouri'), States(code='MT', name='Montana'),
            States(code='NE', name='Nebraska'), States(code='NV', name='Nevada'),
            States(code='NH', name='New Hampshire'), States(code='NJ', name='New Jersey'),
            States(code='NM', name='New Mexico'), States(code='NY', name='New York'),
            States(code='NC', name='North Carolina'), States(code='ND', name='North Dakota'),
            States(code='OH', name='Ohio'), States(code='OK', name='Oklahoma'),
            States(code='OR', name='Oregon'), 
            States(code='PA', name='Pennsylvania'), 
            States(code='RI', name='Rhode Island'), States(code='SC', name='South Carolina'),
            States(code='SD', name='South Dakota'), States(code='TN', name='Tennessee'),
            States(code='TX', name='Texas'), States(code='UT', name='Utah'),
            States(code='VT', name='Vermont'), States(code='VA', name='Virginia'),
            States(code='WA', name='Washington'), States(code='WV', name='West Virginia'),
            States(code='WI', name='Wisconsin'), States(code='WY', name='Wyoming')
        ]
        db.session.bulk_save_objects(states_data)
        db.session.commit()
    
    # Populate default Admin user
    if not UserCredentials.query.filter_by(email="admin@example.com").first():
        print("Creating admin user...")
        admin = UserCredentials(email="admin@example.com", role="admin")
        admin.set_password("AdminPassword1")
        db.session.add(admin)
        db.session.commit() # Commit admin first to get an ID

        # Create profile, linking the ID
        admin_profile = UserProfile(
            id=admin.id,
            full_name="Admin User",
            address1="123 Admin Way",
            address2=None,
            city="Houston",
            state="TX",
            zipcode="77001",
            skills="Team Leadership, Management"
        )
        db.session.add(admin_profile)
        db.session.commit()

    # Populate default Volunteer user
    if not UserCredentials.query.filter_by(email="volunteer@example.com").first():
        print("Creating volunteer user...")
        vol = UserCredentials(email="volunteer@example.com", role="volunteer")
        vol.set_password("Password1")
        db.session.add(vol)
        db.session.commit() # Commit volunteer to get ID
        
        #Add profile for the volunteer
        vol_profile = UserProfile(
            id=vol.id,
            full_name="John Doe",
            address1="123 Main St", 
            address2=None, 
            city="Houston",
            state="TX",
            zipcode="77002",
            skills="First Aid, Logistics",
            availability="2026-12-01, 2026-12-15"
        )
        db.session.add(vol_profile)
        db.session.commit()

    # Populate default Events
    if EventDetails.query.count() == 0:
        print("Populating events...")
        event1 = EventDetails(
            event_name="Community Food Drive",
            location="Downtown Community Center",
            city="Houston",
            state="TX",
            zipcode="77002",
            skills="Logistics, Event Setup",
            event_date=date(2026, 12, 1)
        )
        event2 = EventDetails(
            event_name="Park Cleanup Day",
            location="Memorial Park",
            city="Houston",
            state="TX",
            zipcode="77056",
            skills="Event Setup, General Labor",
            event_date=date(2026, 11, 20)
        )
        db.session.add_all([event1, event2])
        db.session.commit()
    
    print("Database check complete.")


# --- Main Execution ---
if __name__ == '__main__':
    with app.app_context():
        init_db() # Create tables and seed data
    
    print(f"Database initialized at: {os.path.join(BASE_DIR, 'volunteer.db')}")
    # Run the app on port 5001
    app.run(debug=True, port=5001)
