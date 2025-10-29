from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from pydantic import BaseModel, field_validator, ValidationError
from typing import List, Optional
import re
import json
import os

app = Flask(__name__)
CORS(app)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///volunteer.db"  # creates Backend/volunteer.db
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)



# --- Pydantic Models for Data Validation ---

class UserRegistration(BaseModel):
    email: str
    password: str

    @field_validator('email')
    @classmethod
    def email_must_be_valid(cls, value):
        # A simple regex for email validation
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
    email: str
    password: str

class ProfileUpdate(BaseModel):
    full_name: str
    address1: str
    address2: Optional[str] = None
    city: str
    state: str
    zip_code: str
    skills: List[str]
    preferences: Optional[str] = None
    availability: List[str]

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

    @field_validator('skills', 'availability')
    @classmethod
    def lists_not_empty(cls, value):
        if not value:
            raise ValueError('This field cannot be empty')
        return value

class EventCreation(BaseModel):
    event_name: str
    description: str
    location: str
    required_skills: List[str]
    urgency: str
    event_date: str
    volunteer_limit: Optional[int] = None  # None means unlimited

    @field_validator('volunteer_limit')
    @classmethod
    def validate_volunteer_limit(cls, value):
        if value is not None and value < 1:
            raise ValueError('Volunteer limit must be at least 1')
        return value

    @field_validator('event_name')
    @classmethod
    def event_name_length(cls, value):
        if not (1 <= len(value) <= 100):
            raise ValueError('Event name must be between 1 and 100 characters')
        return value

    @field_validator('required_skills')
    @classmethod
    def required_skills_not_empty(cls, value):
        if not value:
            raise ValueError('Required skills cannot be empty')
        return value

# --- Flask App Initialization ---
app = Flask(__name__)
CORS(app)

# --- In-Memory Database Simulation ---
DB = {
    "users": {
        "volunteer@example.com": {
            "password": "Password1", "role": "volunteer",
            "profile": {
                "full_name": "John Doe", "address1": "123 Main St", "address2": "Apt 4B",
                "city": "Houston", "state": "TX", "zip_code": "77002",
                "phone": "(555) 123-4567",
                "skills": ["First Aid", "Logistics"], "preferences": "I prefer morning events.",
                "availability": ["2024-12-01", "2024-12-15"]
            },
            "history": [1]
        },
        "admin@example.com": {
            "password": "AdminPassword1", "role": "admin",
            "profile": {
                "full_name": "Jane Smith", "address1": "456 Admin Ave", "city": "Houston",
                "state": "TX", "zip_code": "77002",
                "phone": "(555) 987-6543",
                "skills": ["Team Leadership", "Public Speaking"], "preferences": "",
                "availability": ["2024-11-01", "2024-12-01"]
            },
            "history": []
        }
    },
    "events": {
        1: {
            "event_name": "Community Food Drive", "description": "Annual food drive to support local families.",
            "location": "Downtown Community Center", "required_skills": ["Logistics", "Event Setup"],
            "urgency": "High", "event_date": "2024-12-01", "volunteer_limit": 10, "status": "open"
        },
        2: {
            "event_name": "Park Cleanup Day", "description": "Help us clean and beautify Memorial Park.",
            "location": "Memorial Park", "required_skills": ["Event Setup"],
            "urgency": "Medium", "event_date": "2024-11-20", "volunteer_limit": None, "status": "open"
        }
    },
    "skills": ["First Aid", "Logistics", "Event Setup", "Public Speaking", "Registration", "Tech Support", "Catering", "Marketing", "Fundraising", "Photography", "Social Media", "Team Leadership", "Translation"],
    "urgency_levels": ["Low", "Medium", "High", "Critical"],
    "notifications": [],
    "activity_log": [],
    "invites": [],
    "invite_counter": 1
}

# --- Helper Functions ---
from datetime import datetime

def add_notification(message, type="info"):
    """Add a notification to the notifications list"""
    notification = {
        "id": len(DB["notifications"]) + 1,
        "message": message,
        "type": type,
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "read": False
    }
    # Add to beginning
    DB["notifications"].insert(0, notification)
    # Keep only last 50 notifications
    if len(DB["notifications"]) > 50:
        DB["notifications"] = DB["notifications"][:50]
    return notification

def add_activity(type, **kwargs):
    """Add an activity to the activity log"""
    activity = {
        "type": type,
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        **kwargs
    }
    # Add to beginning
    DB["activity_log"].insert(0, activity)
    # Keep only last 50 activities
    if len(DB["activity_log"]) > 50:
        DB["activity_log"] = DB["activity_log"][:50]
    return activity

def get_event_volunteer_count(event_id):
    """Get the current number of accepted volunteers for an event"""
    return len([inv for inv in DB["invites"]
                if inv['event_id'] == event_id and inv['status'] == 'accepted'])

def check_and_close_event(event_id):
    """Check if event should be closed (full or date passed) and close it"""
    event = DB["events"].get(event_id)
    if not event or event.get("status") == "closed":
        return False

    # Check if event date has passed
    event_date = datetime.strptime(event["event_date"], "%Y-%m-%d").date()
    today = datetime.now().date()

    if event_date < today:
        event["status"] = "closed"
        return True

    # Check if volunteer limit reached
    volunteer_limit = event.get("volunteer_limit")
    if volunteer_limit is not None:
        current_count = get_event_volunteer_count(event_id)
        if current_count >= volunteer_limit:
            event["status"] = "closed"
            return True

    return False

def check_all_events_status():
    """Check and auto-close all events that should be closed"""
    for event_id in DB["events"]:
        check_and_close_event(event_id)

# --- API Endpoints ---

@app.route('/register', methods=['POST'])
def register_user():
    try:
        user_data = UserRegistration(**request.json)
        if user_data.email in DB["users"]:
            return jsonify({"message": "User with this email already exists"}), 409

        DB["users"][user_data.email] = {
            "password": user_data.password, "role": "volunteer",
            "profile": {}, "history": []
        }

        # Add notification and activity log
        add_notification(f"New user registered: {user_data.email}", "info")
        add_activity("registration", user=user_data.email)

        return jsonify({"message": "Registration successful", "user": {"email": user_data.email, "role": "volunteer"}}), 201
    except ValidationError as e:
        return jsonify({"message": "Validation error", "errors": json.loads(e.json())}), 400
    except Exception as e:
        return jsonify({"message": "An internal error occurred", "error": str(e)}), 500

@app.route('/login', methods=['POST'])
def login_user():
    try:
        login_data = UserLogin(**request.json)
        user = DB["users"].get(login_data.email)

        if not user or user["password"] != login_data.password:
            return jsonify({"message": "Invalid email or password"}), 401

        return jsonify({
            "message": "Login successful",
            "user": {
                "email": login_data.email, "role": user["role"],
                "profileComplete": bool(user.get("profile"))
            }
        }), 200
    except ValidationError as e:
        return jsonify({"message": "Validation error", "errors": json.loads(e.json())}), 400
    except Exception as e:
        return jsonify({"message": "An internal error occurred", "error": str(e)}), 500

@app.route('/profile/<string:email>', methods=['GET', 'PUT'])
def user_profile(email):
    user = DB["users"].get(email)
    if not user:
        return jsonify({"message": "User not found"}), 404

    if request.method == 'GET':
        return jsonify(user.get("profile", {})), 200

    if request.method == 'PUT':
        try:
            profile_data = ProfileUpdate(**request.json)
            DB["users"][email]["profile"] = profile_data.model_dump()
            return jsonify({"message": "Profile updated successfully", "profile": profile_data.model_dump()}), 200
        except ValidationError as e:
            return jsonify({"message": "Validation error", "errors": json.loads(e.json())}), 400
        except Exception as e:
            return jsonify({"message": "An internal error occurred", "error": str(e)}), 500

@app.route('/events', methods=['GET', 'POST'])
def manage_events():
    if request.method == 'GET':
        # Check and update event statuses before returning
        check_all_events_status()

        # Add volunteer count to each event
        event_list = []
        for id, event in DB["events"].items():
            event_data = {"id": id, **event}
            event_data["current_volunteers"] = get_event_volunteer_count(id)
            event_list.append(event_data)

        return jsonify(event_list), 200

    if request.method == 'POST':
        try:
            event_data = EventCreation(**request.json)
            new_id = max(DB["events"].keys()) + 1 if DB["events"] else 1
            event_dict = event_data.model_dump()
            event_dict["status"] = "open"  # All new events start as open
            DB["events"][new_id] = event_dict

            # Add notification and activity log
            add_notification(f"New event created: {event_data.event_name}", "success")
            add_activity("event_created", event=event_data.event_name)

            return jsonify({"message": "Event created successfully", "event": {"id": new_id, **event_dict}}), 201
        except ValidationError as e:
            return jsonify({"message": "Validation error", "errors": json.loads(e.json())}), 400
        except Exception as e:
            return jsonify({"message": "An internal error occurred", "error": str(e)}), 500

@app.route('/events/<int:event_id>', methods=['GET', 'PUT', 'DELETE'])
def modify_event(event_id):
    """Get, update, or delete a specific event by ID"""
    if event_id not in DB["events"]:
        return jsonify({"message": "Event not found"}), 404

    if request.method == 'GET':
        event = DB["events"][event_id]
        return jsonify({"id": event_id, **event}), 200

    if request.method == 'PUT':
        try:
            event_data = EventCreation(**request.json)
            DB["events"][event_id] = event_data.model_dump()
            return jsonify({"message": "Event updated successfully", "event": {"id": event_id, **event_data.model_dump()}}), 200
        except ValidationError as e:
            return jsonify({"message": "Validation error", "errors": json.loads(e.json())}), 400
        except Exception as e:
            return jsonify({"message": "An internal error occurred", "error": str(e)}), 500

    if request.method == 'DELETE':
        del DB["events"][event_id]
        return jsonify({"message": "Event deleted successfully"}), 200

@app.route('/data/skills', methods=['GET'])
def get_skills():
    return jsonify(DB["skills"]), 200

@app.route('/data/urgency', methods=['GET'])
def get_urgency_levels():
    return jsonify(DB["urgency_levels"]), 200

@app.route('/matching/<int:event_id>', methods=['GET'])
def get_volunteer_matches(event_id):
    event = DB["events"].get(event_id)
    if not event:
        return jsonify({"message": "Event not found"}), 404

    matches = []
    for email, user_data in DB["users"].items():
        if user_data["role"] == "volunteer" and user_data.get("profile"):
            profile = user_data["profile"]
            has_skill = any(skill in profile.get("skills", []) for skill in event["required_skills"])
            is_available = event["event_date"] in profile.get("availability", [])

            if has_skill and is_available:
                matches.append({
                    "email": email, "full_name": profile["full_name"],
                    "skills": profile["skills"]
                })

    return jsonify(matches), 200

@app.route('/history/<string:email>', methods=['GET'])
def get_volunteer_history(email):
    user = DB["users"].get(email)
    if not user:
        return jsonify({"message": "User not found"}), 404

    history_ids = user.get("history", [])
    history_events = [{"id": id, **DB["events"][id]} for id in history_ids if id in DB["events"]]

    return jsonify(history_events), 200

@app.route('/user/<string:email>/events', methods=['GET'])
def get_user_events(email):
    """Get all events a user has signed up for (for notifications page)"""
    user = DB["users"].get(email)
    if not user:
        return jsonify({"message": "User not found"}), 404

    # Get events from accepted invites, not from history
    # History is for completed events only
    user_invites = [inv for inv in DB["invites"] if inv['user_email'] == email and inv['status'] == 'accepted']

    # Create list of events with full details
    events = []
    for invite in user_invites:
        event_id = invite['event_id']
        if event_id in DB["events"]:
            event = DB["events"][event_id]
            events.append({
                "id": event_id,
                "event_name": event["event_name"],
                "description": event["description"],
                "location": event["location"],
                "event_date": event["event_date"],
                "required_skills": event.get("required_skills", []),
                "urgency": event.get("urgency", ""),
                "completed": invite.get("completed", False)
            })

    return jsonify({"events": events}), 200

@app.route('/users', methods=['GET'])
def get_all_users():
    """Get all users (for admin statistics and user management)"""
    users_list = []
    user_id = 1
    for email, user_data in DB["users"].items():
        profile = user_data.get("profile", {})
        users_list.append({
            "id": user_id,
            "email": email,
            "role": user_data.get("role", "volunteer"),
            "name": profile.get("full_name", "N/A"),
            "phone": profile.get("phone", "N/A"),
            "profileComplete": profile is not None and len(profile) > 0
        })
        user_id += 1

    return jsonify(users_list), 200

@app.route('/notifications', methods=['GET'])
def get_notifications():
    """Get all notifications for admin"""
    return jsonify(DB["notifications"]), 200

@app.route('/notifications/<int:notification_id>/read', methods=['PUT'])
def mark_notification_read(notification_id):
    """Mark a notification as read"""
    for notification in DB["notifications"]:
        if notification["id"] == notification_id:
            notification["read"] = True
            return jsonify({"message": "Notification marked as read"}), 200
    return jsonify({"message": "Notification not found"}), 404

@app.route('/activity', methods=['GET'])
def get_activity():
    """Get recent activity log"""
    return jsonify(DB["activity_log"]), 200

@app.route('/users/<string:email>', methods=['PUT', 'DELETE'])
def modify_user(email):
    """Update or delete a specific user by email"""
    if email not in DB["users"]:
        return jsonify({"message": "User not found"}), 404

    if request.method == 'PUT':
        try:
            data = request.json
            user = DB["users"][email]

            # Update role if provided
            if 'role' in data:
                user['role'] = data['role']

            # Update profile fields if provided
            if 'name' in data and user.get('profile'):
                user['profile']['full_name'] = data['name']

            return jsonify({"message": "User updated successfully", "user": {"email": email, **user}}), 200
        except Exception as e:
            return jsonify({"message": "An internal error occurred", "error": str(e)}), 500

    if request.method == 'DELETE':
        del DB["users"][email]
        return jsonify({"message": "User deleted successfully"}), 200

# --- Invite/Request Endpoints ---

@app.route('/invites', methods=['GET', 'POST'])
def manage_invites():
    """Get all invites or create a new invite/request"""
    if request.method == 'GET':
        # Filter by status and type if provided
        status = request.args.get('status')
        invite_type = request.args.get('type')

        filtered_invites = DB["invites"]
        if status:
            filtered_invites = [inv for inv in filtered_invites if inv['status'] == status]
        if invite_type:
            filtered_invites = [inv for inv in filtered_invites if inv['type'] == invite_type]

        return jsonify(filtered_invites), 200

    if request.method == 'POST':
        try:
            data = request.json
            event_id = data['event_id']

            # Check if event exists and is open
            event = DB["events"].get(event_id)
            if not event:
                return jsonify({"message": "Event not found"}), 404

            # Check and update event status
            check_and_close_event(event_id)

            # Check if event is closed
            if event.get("status") == "closed":
                return jsonify({"message": "This event is now closed and no longer accepting volunteers"}), 403

            # Check for existing pending or accepted invite/request for this user and event
            existing_invite = next(
                (inv for inv in DB["invites"]
                 if inv['user_email'] == data['user_email']
                 and inv['event_id'] == event_id
                 and inv['status'] in ['pending', 'accepted']),
                None
            )

            if existing_invite:
                if existing_invite['status'] == 'pending':
                    return jsonify({"message": "You already have a pending request for this event"}), 409
                elif existing_invite['status'] == 'accepted':
                    return jsonify({"message": "You are already signed up for this event"}), 409

            invite_id = DB["invite_counter"]
            DB["invite_counter"] += 1

            invite = {
                "id": invite_id,
                "event_id": event_id,
                "user_email": data['user_email'],
                "status": "pending",
                "type": data['type'],  # 'admin_invite' or 'user_request'
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }

            DB["invites"].append(invite)

            # Add notification based on type
            if data['type'] == 'admin_invite':
                event = DB["events"].get(data['event_id'])
                event_name = event['event_name'] if event else f"Event #{data['event_id']}"
                add_notification(f"You've been invited to: {event_name}", "info")
            elif data['type'] == 'user_request':
                event = DB["events"].get(data['event_id'])
                event_name = event['event_name'] if event else f"Event #{data['event_id']}"
                add_notification(f"{data['user_email']} requested to join: {event_name}", "info")

            return jsonify({"message": "Invite/request created successfully", "invite": invite}), 201
        except Exception as e:
            return jsonify({"message": "An internal error occurred", "error": str(e)}), 500

@app.route('/invites/<int:invite_id>', methods=['PUT', 'DELETE'])
def modify_invite(invite_id):
    """Update or delete an invite"""
    invite = next((inv for inv in DB["invites"] if inv["id"] == invite_id), None)

    if not invite:
        return jsonify({"message": "Invite not found"}), 404

    if request.method == 'PUT':
        try:
            data = request.json
            old_status = invite['status']
            new_status = data.get('status', invite['status'])
            invite['status'] = new_status

            # If invite is being accepted, check if event should be closed
            if old_status != 'accepted' and new_status == 'accepted':
                check_and_close_event(invite['event_id'])

            # Note: History is now only for completed events, not accepted invites
            # Events are added to history when marked as completed via the /complete endpoint

            return jsonify({"message": "Invite updated successfully", "invite": invite}), 200
        except Exception as e:
            return jsonify({"message": "An internal error occurred", "error": str(e)}), 500

    if request.method == 'DELETE':
        DB["invites"].remove(invite)
        return jsonify({"message": "Invite deleted successfully"}), 200

@app.route('/invites/<int:invite_id>/complete', methods=['PUT'])
def mark_invite_complete(invite_id):
    """Mark a volunteer's event participation as completed"""
    invite = next((inv for inv in DB["invites"] if inv["id"] == invite_id), None)

    if not invite:
        return jsonify({"message": "Invite not found"}), 404

    try:
        data = request.json
        completed = data.get('completed', False)

        invite['completed'] = completed

        # If marking as completed, add to user's history
        if completed and invite['status'] == 'accepted':
            user_email = invite['user_email']
            event_id = invite['event_id']
            if user_email in DB["users"]:
                if event_id not in DB["users"][user_email]["history"]:
                    DB["users"][user_email]["history"].append(event_id)
        # If unmarking as completed, remove from history
        elif not completed and invite['status'] == 'accepted':
            user_email = invite['user_email']
            event_id = invite['event_id']
            if user_email in DB["users"]:
                if event_id in DB["users"][user_email]["history"]:
                    DB["users"][user_email]["history"].remove(event_id)

        return jsonify({"message": "Completion status updated successfully", "invite": invite}), 200
    except Exception as e:
        return jsonify({"message": "An internal error occurred", "error": str(e)}), 500

@app.route('/invites/user/<string:email>', methods=['GET'])
def get_user_invites(email):
    """Get all invites for a specific user with optional filtering"""
    user_invites = [inv for inv in DB["invites"] if inv['user_email'] == email]

    # Filter by status and type if provided
    status = request.args.get('status')
    invite_type = request.args.get('type')

    if status:
        user_invites = [inv for inv in user_invites if inv['status'] == status]
    if invite_type:
        user_invites = [inv for inv in user_invites if inv['type'] == invite_type]

    # Enrich with event details
    enriched_invites = []
    for invite in user_invites:
        event = DB["events"].get(invite['event_id'])
        if event:
            enriched_invites.append({
                **invite,
                "event": event
            })
        else:
            enriched_invites.append(invite)

    return jsonify(enriched_invites), 200

# --- Main Execution ---
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        print("Database initialized at:", os.path.abspath("voluunteer.db"))
    app.run(debug=True, port=5002)

