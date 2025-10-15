from flask import Flask, jsonify, request
from flask_cors import CORS
from pydantic import BaseModel, field_validator, ValidationError
from typing import List, Optional
import re
import json

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
            "urgency": "High", "event_date": "2024-12-01"
        },
        2: {
            "event_name": "Park Cleanup Day", "description": "Help us clean and beautify Memorial Park.",
            "location": "Memorial Park", "required_skills": ["Event Setup"],
            "urgency": "Medium", "event_date": "2024-11-20"
        }
    },
    "skills": ["First Aid", "Logistics", "Event Setup", "Public Speaking", "Registration", "Tech Support", "Catering", "Marketing", "Fundraising", "Photography", "Social Media", "Team Leadership", "Translation"],
    "urgency_levels": ["Low", "Medium", "High", "Critical"]
}

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
        return jsonify({"message": "Registration successful", "user": {"email": user_data.email, "role": "volunteer"}}), 201
    except ValidationError as e:
        # Fixed the TypeError by loading the JSON string from the validation error
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
        event_list = [{"id": id, **event} for id, event in DB["events"].items()]
        return jsonify(event_list), 200
        
    if request.method == 'POST':
        try:
            event_data = EventCreation(**request.json)
            new_id = max(DB["events"].keys()) + 1 if DB["events"] else 1
            DB["events"][new_id] = event_data.model_dump()
            return jsonify({"message": "Event created successfully", "event": {"id": new_id, **event_data.model_dump()}}), 201
        except ValidationError as e:
            return jsonify({"message": "Validation error", "errors": json.loads(e.json())}), 400
        except Exception as e:
            return jsonify({"message": "An internal error occurred", "error": str(e)}), 500

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

# --- Main Execution ---
if __name__ == '__main__':
    app.run(debug=True, port=5001)

