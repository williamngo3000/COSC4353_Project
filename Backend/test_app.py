import unittest
import json
import sys
import os
from datetime import datetime
from unittest.mock import patch

# Add the project's root directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import the app, db, and all the models from your actual project files
try:
    from app import app, db, init_db
    from models import UserCredentials, UserProfile, EventDetails, VolunteerHistory, States
except ImportError as e:
    print(f"Error importing app or models: {e}")
    print("Please make sure test_app.py is in the same directory as app.py and models.py")
    sys.exit(1)

class TestVolunteerApp(unittest.TestCase):
    def setUp(self):
        """Set up a temporary, in-memory database for each test."""
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:' # Use in-memory db
        self.app = app.test_client()

        # Set up the database and populate it with seed data
        with app.app_context():
            db.create_all()
            init_db() # Run your seeder function from app.py

    def tearDown(self):
        """Clean up the database after each test."""
        with app.app_context():
            db.session.remove()
            db.drop_all()

    # --- Test Cases for UserCredentials ---

    def test_register_user_success(self):
        """Test successful user registration."""
        response = self.app.post('/register', 
                                 data=json.dumps({"email": "newuser@example.com", "password": "NewPassword1"}),
                                 content_type='application/json')
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertEqual(data['message'], 'Registration successful')
        
        # Verify in DB
        with app.app_context():
            user = UserCredentials.query.filter_by(email="newuser@example.com").first()
            self.assertIsNotNone(user)
            self.assertEqual(user.role, "volunteer")

    def test_register_user_already_exists(self):
        """Test registration with an email that already exists."""
        # This user was created by init_db()
        response = self.app.post('/register',
                                 data=json.dumps({"email": "volunteer@example.com", "password": "Password1"}),
                                 content_type='application/json')
        self.assertEqual(response.status_code, 409)
        self.assertIn("already exists", str(response.data))

    def test_register_user_invalid_password(self):
        """Test registration with a password that's too short."""
        response = self.app.post('/register',
                                 data=json.dumps({"email": "test@test.com", "password": "short"}),
                                 content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertIn("Password must be at least 8 characters", str(response.data))

    def test_register_user_invalid_email_400(self):
        """Test registration with a bad email to trigger a 400 Validation Error."""
        response = self.app.post('/register',
                                 data=json.dumps({"email": "bad-email", "password": "NewPassword1"}),
                                 content_type='application/json')
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertEqual(data['message'], 'Validation error')
        self.assertIn('Email is not valid', str(data['errors'])) 

    def test_register_user_general_exception_500(self):
        """Test the general exception handler for 500 error."""
        # Use patch to simulate a database commit failure
        with patch('app.db.session.commit') as mock_commit:
            mock_commit.side_effect = Exception("Simulated DB Error")
            
            response = self.app.post('/register', 
                                     data=json.dumps({"email": "exception@example.com", "password": "NewPassword1"}),
                                     content_type='application/json')
            
            self.assertEqual(response.status_code, 500)
            data = json.loads(response.data)
            self.assertEqual(data['message'], 'An internal error occurred')
            self.assertIn("Simulated DB Error", data['error'])

    def test_login_user_success(self):
        """Test successful login for admin."""
        # This user was created by init_db()
        response = self.app.post('/login',
                                 data=json.dumps({"email": "admin@example.com", "password": "AdminPassword1"}),
                                 content_type='application/json')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['user']['profileComplete']) # Admin profile is complete
        self.assertEqual(data['user']['role'], 'admin')

    def test_login_user_invalid_credentials(self):
        """Test login with an incorrect password."""
        response = self.app.post('/login',
                                 data=json.dumps({"email": "volunteer@example.com", "password": "WrongPassword"}),
                                 content_type='application/json')
        self.assertEqual(response.status_code, 401)
        self.assertIn("Invalid email or password", str(response.data))

    def test_login_user_validation_error(self):
        """Test login with missing/invalid data."""
        response = self.app.post('/login',
                                 data=json.dumps({"email": "volunteer@example.com"}), # Missing password
                                 content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertIn("Validation error", str(response.data))

    # --- Test Cases for UserProfile ---

    def test_get_profile_success(self):
        """Test fetching an existing user profile."""
        response = self.app.get('/profile/volunteer@example.com')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['full_name'], 'John Doe')
        self.assertEqual(data['address1'], '123 Main St')
        self.assertIn('First Aid', data['skills'])

    def test_get_profile_with_null_skills_and_availability(self):
        """Test GET profile for a user with None for skills/availability."""
        # 1. Create a user and profile with null skills/availability
        with app.app_context():
            user = UserCredentials(email="nulluser@example.com")
            user.set_password("Password123")
            db.session.add(user)
            db.session.commit()
            
            profile = UserProfile(
                id=user.id,
                full_name="Null User",
                address1="123 Null St",
                city="Nullville",
                state="TX",
                zipcode="00000",
                skills=None,
                availability=None
            )
            db.session.add(profile)
            db.session.commit()
            
        # 2. Request their profile
        response = self.app.get('/profile/nulluser@example.com')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['full_name'], 'Null User')
        self.assertEqual(data['skills'], []) # Should be an empty list
        self.assertEqual(data['availability'], []) # Should be an empty list

    def test_get_profile_not_found(self):
        """Test fetching a profile for a user that doesn't exist."""
        response = self.app.get('/profile/nouser@example.com')
        self.assertEqual(response.status_code, 404)
        self.assertIn("User not found", str(response.data))

    def test_get_profile_no_profile_exists(self):
        """Test fetching a profile for a user who exists but has no profile."""
        # 1. Create a user with no profile
        with app.app_context():
            new_user = UserCredentials(email="noprofile@example.com")
            new_user.set_password("Password123")
            db.session.add(new_user)
            db.session.commit()
        
        # 2. Request their profile
        response = self.app.get('/profile/noprofile@example.com')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data, {}) # Should return an empty object

    def test_update_profile_success(self):
        """Test successfully updating a user profile."""
        profile_data = {
            "full_name": "John D. Updated",
            "address1": "123 New St",
            "address2": "Apt 1",
            "city": "Austin",
            "state": "TX",
            "zip_code": "78701",
            "skills": ["Marketing", "Photography"],
            "availability": ["2026-01-01", "2026-02-02"],
            "preferences": "Weekends"
        }
        response = self.app.put('/profile/volunteer@example.com',
                                data=json.dumps(profile_data),
                                content_type='application/json')
        self.assertEqual(response.status_code, 200)
        
        # Verify in DB
        with app.app_context():
            user = UserCredentials.query.filter_by(email="volunteer@example.com").first()
            self.assertEqual(user.profile.full_name, "John D. Updated")
            self.assertEqual(user.profile.city, "Austin")
            self.assertEqual(user.profile.address2, "Apt 1")
            self.assertIn("Marketing", user.profile.skills)
            self.assertNotIn("First Aid", user.profile.skills) # Old skill should be gone

    def test_update_profile_with_null_zip(self):
        """Test updating a profile with a null/empty zip code."""
        profile_data = {
            "full_name": "John D. Updated",
            "address1": "123 New St",
            "city": "Austin",
            "state": "TX",
            "zip_code": None, # Test the None case
            "skills": ["Marketing"]
        }
        response = self.app.put('/profile/volunteer@example.com',
                                data=json.dumps(profile_data),
                                content_type='application/json')
        self.assertEqual(response.status_code, 200) # Should be successful

        # Verify in DB
        with app.app_context():
            user = UserCredentials.query.filter_by(email="volunteer@example.com").first()
            self.assertIsNone(user.profile.zipcode) # Zipcode should be None

        # Test the empty string case
        profile_data["zip_code"] = ""
        response = self.app.put('/profile/volunteer@example.com',
                                data=json.dumps(profile_data),
                                content_type='application/json')
        self.assertEqual(response.status_code, 200)
        with app.app_context():
            user = UserCredentials.query.filter_by(email="volunteer@example.com").first()
            self.assertEqual(user.profile.zipcode, "") # Zipcode should be ""

    def test_update_profile_creates_new_profile(self):
        """Test that PUT creates a profile if one doesn't exist."""
        # 1. Create a user with no profile
        with app.app_context():
            new_user = UserCredentials(email="newprofile@example.com")
            new_user.set_password("Password123")
            db.session.add(new_user)
            db.session.commit()
        
        # 2. Send PUT data to create their profile
        profile_data = {
            "full_name": "New User",
            "address1": "456 First St",
            "city": "Dallas",
            "state": "TX",
            "zip_code": "75201",
            "skills": ["Tech Support"],
        }
        response = self.app.put('/profile/newprofile@example.com',
                                data=json.dumps(profile_data),
                                content_type='application/json')
        self.assertEqual(response.status_code, 200)

        # 3. Verify in DB
        with app.app_context():
            user = UserCredentials.query.filter_by(email="newprofile@example.com").first()
            self.assertIsNotNone(user.profile)
            self.assertEqual(user.profile.full_name, "New User")
            self.assertEqual(user.profile.city, "Dallas")

    def test_update_profile_invalid_zipcode_400(self):
        """Test profile update with a bad zip code for a 400 error."""
        profile_data = {
            "full_name": "John D. Updated",
            "address1": "123 New St",
            "city": "Austin",
            "state": "TX",
            "zip_code": "bad-zip", # <-- Invalid zip
            "skills": ["Marketing"],
            "availability": ["2026-01-01"]
        }
        response = self.app.put('/profile/volunteer@example.com',
                                data=json.dumps(profile_data),
                                content_type='application/json')
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('zip_code', str(data['errors']))

    # --- Test Cases for EventDetails ---

    def test_get_events_success(self):
        """Test fetching all events."""
        response = self.app.get('/events')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(len(data), 2) # From init_db()
        self.assertEqual(data[0]['event_name'], "Community Food Drive")

    def test_get_events_no_events(self):
        """Test fetching events when none exist."""
        # Clear the tables
        with app.app_context():
            db.session.query(VolunteerHistory).delete()
            db.session.query(EventDetails).delete()
            db.session.commit()
        
        response = self.app.get('/events')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data, []) # Should return an empty list

    def test_create_event_success(self):
        """Test successfully creating a new event."""
        event_data = {
            "event_name": "New Charity Gala",
            "city": "New York",
            "state": "NY",
            "zipcode": "10001",
            "skills": "Catering, Marketing",
            "preferences": "Evening",
            "availability": "2026-10-10"
        }
        response = self.app.post('/events',
                                 data=json.dumps(event_data),
                                 content_type='application/json')
        self.assertEqual(response.status_code, 201)
        
        # Verify in DB
        with app.app_context():
            event = EventDetails.query.filter_by(event_name="New Charity Gala").first()
            self.assertIsNotNone(event)
            self.assertEqual(event.city, "New York")
            self.assertEqual(event.skills, "Catering, Marketing")

    def test_create_event_validation_error(self):
        """Test creating an event with missing data."""
        event_data = { "city": "New York" } # Missing event_name
        response = self.app.post('/events',
                                 data=json.dumps(event_data),
                                 content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertIn("Validation error", str(response.data))

    # --- Test Cases for VolunteerHistory & Matching ---

    def test_signup_for_event_success(self):
        """Test successfully signing up for an event."""
        response = self.app.post('/signup',
                                 data=json.dumps({"email": "volunteer@example.com", "event_id": 2}),
                                 content_type='application/json')
        self.assertEqual(response.status_code, 201)
        self.assertIn("Successfully signed up", str(response.data))

        # Verify in DB
        with app.app_context():
            user = UserCredentials.query.filter_by(email="volunteer@example.com").first()
            history = VolunteerHistory.query.filter_by(user_id=user.id, event_id=2).first()
            self.assertIsNotNone(history)

    def test_signup_for_event_already_signed_up(self):
        """Test signing up for an event the user is already registered for."""
        # volunteer@example.com is signed up for event 1 by init_db()
        response = self.app.post('/signup',
                                 data=json.dumps({"email": "volunteer@example.com", "event_id": 1}),
                                 content_type='application/json')
        self.assertEqual(response.status_code, 409)
        self.assertIn("Already signed up", str(response.data))

    def test_signup_for_event_user_not_found(self):
        """Test signing up with a non-existent user."""
        response = self.app.post('/signup',
                                 data=json.dumps({"email": "nouser@example.com", "event_id": 1}),
                                 content_type='application/json')
        self.assertEqual(response.status_code, 404)
        self.assertIn("User not found", str(response.data))

    def test_signup_for_event_event_not_found(self):
        """Test signing up for a non-existent event."""
        response = self.app.post('/signup',
                                 data=json.dumps({"email": "volunteer@example.com", "event_id": 999}),
                                 content_type='application/json')
        self.assertEqual(response.status_code, 404)
        self.assertIn("Event not found", str(response.data))

    def test_signup_for_event_missing_data(self):
        """Test signing up with missing data."""
        response = self.app.post('/signup',
                                 data=json.dumps({"event_id": 1}), # Missing email
                                 content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertIn("Email and Event ID are required", str(response.data))

    def test_get_volunteer_history_success(self):
        """Test fetching a user's volunteer history."""
        # init_db adds Event 1 to the volunteer's history
        response = self.app.get('/history/volunteer@example.com')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['event_name'], 'Community Food Drive')

    def test_get_volunteer_history_no_history(self):
        """Test fetching history for a user with no history."""
        # admin@example.com was created but has no history
        response = self.app.get('/history/admin@example.com')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data, []) # Should return an empty list

    def test_get_volunteer_history_user_not_found_404(self):
        """Test history for a non-existent user."""
        response = self.app.get('/history/nouser@example.com')
        self.assertEqual(response.status_code, 404)

    def test_get_volunteer_matches_success(self):
        """Test the matching algorithm for a skill match."""
        # Event 1 ("Community Food Drive") needs "Logistics, Event Setup"
        # "volunteer@example.com" has "First Aid, Logistics"
        # This should be a match on "Logistics".
        response = self.app.get('/matching/1')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['email'], 'volunteer@example.com')

    def test_get_volunteer_matches_no_match(self):
        """Test the matching algorithm for no skill match."""
        # Event 2 ("Park Cleanup Day") needs "Event Setup, General Labor"
        # "volunteer@example.com" has "First Aid, Logistics"
        # This should be no match.
        response = self.app.get('/matching/2')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(json.loads(response.data)), 0)

    def test_get_volunteer_matches_with_skill_less_volunteer(self):
        """Test that a volunteer with no skills is skipped."""
        # 1. Create a user and profile with no skills
        with app.app_context():
            user = UserCredentials(email="noskill@example.com", role="volunteer")
            user.set_password("Password123")
            db.session.add(user)
            db.session.commit()
            
            profile = UserProfile(
                id=user.id,
                full_name="No Skill User",
                address1="123 NoSkill St",
                city="Anywhere",
                state="TX",
                zipcode="00000",
                skills=None # Explicitly None
            )
            db.session.add(profile)
            db.session.commit()
            
        # 2. Request matches for Event 1, which "volunteer@example.com" matches.
        # This new "noskill@example.com" user should be skipped over.
        response = self.app.get('/matching/1')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(len(data), 1) # Should only be the one match
        self.assertEqual(data[0]['email'], 'volunteer@example.com') # Should not be 'noskill@example.com'


    def test_get_volunteer_matches_event_not_found_404(self):
        """Test matching for a non-existent event."""
        response = self.app.get('/matching/999')
        self.assertEqual(response.status_code, 404)

    def test_get_volunteer_matches_event_has_no_skills(self):
        """Test matching for an event that has no skills listed."""
        # 1. Create a new event with no skills
        with app.app_context():
            no_skill_event = EventDetails(event_name="No Skills Needed Event")
            db.session.add(no_skill_event)
            db.session.commit()
            event_id = no_skill_event.id
        
        # 2. Request matches for it
        response = self.app.get(f'/matching/{event_id}')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data, []) # Should return an empty list

    # --- Test Cases for Static Data Endpoints ---

    def test_get_skills_endpoint(self):
        """Test the /data/skills endpoint."""
        response = self.app.get('/data/skills')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIsInstance(data, list)
        self.assertIn("Tech Support", data)
        self.assertIn("First Aid", data)

    def test_get_states_endpoint(self):
        """Test the /data/states endpoint."""
        response = self.app.get('/data/states')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 50) # init_db() seeds 50 states
        self.assertEqual(data[0]['code'], 'AL')
        self.assertEqual(data[0]['name'], 'Alabama')

if __name__ == '__main__':
    unittest.main()

