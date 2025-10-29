import unittest
import json
import sys
import os
from datetime import datetime, timezone # Added timezone
from unittest.mock import patch # Make sure this is imported

# Add the project's root directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import all the models we need for the tests
from app import app, db, init_db, User, Profile, Event, Skill, Availability, Notification

class TestCombinedApp(unittest.TestCase):
    def setUp(self):
        """Set up a temporary, in-memory database for each test."""
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:' # Use in-memory db
        self.app = app.test_client()

        # Set up the database and populate it with seed data
        with app.app_context():
            db.create_all()
            init_db() # Run our seeder function

    def tearDown(self):
        """Clean up the database after each test."""
        with app.app_context():
            db.session.remove()
            db.drop_all()

    # --- Original Test Cases ---

    def test_register_user_success(self):
        response = self.app.post('/register', 
                                 data=json.dumps({"email": "newuser@example.com", "password": "NewPassword1"}),
                                 content_type='application/json')
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertEqual(data['message'], 'Registration successful')
        
        # Verify in DB
        with app.app_context():
            user = User.query.filter_by(email="newuser@example.com").first()
            self.assertIsNotNone(user)

    def test_register_user_already_exists(self):
        # This user was created by init_db()
        response = self.app.post('/register',
                                 data=json.dumps({"email": "volunteer@example.com", "password": "Password1"}),
                                 content_type='application/json')
        self.assertEqual(response.status_code, 409)

    def test_register_user_invalid_password(self):
        response = self.app.post('/register',
                                 data=json.dumps({"email": "test@test.com", "password": "short"}),
                                 content_type='application/json')
        self.assertEqual(response.status_code, 400)

    def test_login_user_success(self):
        # This user was created by init_db()
        response = self.app.post('/login',
                                 data=json.dumps({"email": "admin@example.com", "password": "AdminPassword1"}),
                                 content_type='application/json')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['user']['profileComplete']) # Admin profile is complete

    def test_login_user_invalid_credentials(self):
        response = self.app.post('/login',
                                 data=json.dumps({"email": "volunteer@example.com", "password": "WrongPassword"}),
                                 content_type='application/json')
        self.assertEqual(response.status_code, 401)

    def test_get_profile_success(self):
        response = self.app.get('/profile/volunteer@example.com')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['full_name'], 'John Doe')
        self.assertIn('First Aid', data['skills'])

    def test_get_profile_not_found(self):
        response = self.app.get('/profile/nouser@example.com')
        self.assertEqual(response.status_code, 404)

    def test_update_profile_success(self):
        profile_data = {
            "full_name": "John D. Updated", "address1": "123 New St", "city": "Austin",
            "state": "TX", "zip_code": "78701", "skills": ["Marketing", "Photography"],
            "availability": ["2026-01-01", "2026-02-02"], "phone": "111-222-3333"
        }
        response = self.app.put('/profile/volunteer@example.com',
                                data=json.dumps(profile_data),
                                content_type='application/json')
        self.assertEqual(response.status_code, 200)
        
        # Verify in DB
        with app.app_context():
            user = User.query.filter_by(email="volunteer@example.com").first()
            self.assertEqual(user.profile.full_name, "John D. Updated")
            self.assertEqual(user.profile.city, "Austin")
            skill_names = [s.name for s in user.skills]
            self.assertIn("Marketing", skill_names)
            self.assertNotIn("First Aid", skill_names) # Old skill should be gone

    def test_get_events_success(self):
        response = self.app.get('/events')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(len(data), 2) # From init_db()

    def test_create_event_success(self):
        event_data = {
            "event_name": "New Charity Gala", "description": "A fancy event.",
            "location": "The Grand Hall", "required_skills": ["Catering", "Marketing"],
            "urgency": "High", "event_date": "2026-05-10"
        }
        response = self.app.post('/events',
                                 data=json.dumps(event_data),
                                 content_type='application/json')
        self.assertEqual(response.status_code, 201)
        
        # Verify in DB
        with app.app_context():
            event = Event.query.filter_by(event_name="New Charity Gala").first()
            self.assertIsNotNone(event)
            self.assertEqual(event.location, "The Grand Hall")

    def test_get_volunteer_matches_success(self):
        # This test uses future dates from init_db now
        with app.app_context():
            # FIX: Use db.session.get()
            evt1 = db.session.get(Event, 1) 
            # Ensure event date matches volunteer availability from init_db
            evt1.event_date = datetime.strptime("2026-12-01", "%Y-%m-%d").date()
            db.session.commit()

        response = self.app.get('/matching/1')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['email'], 'volunteer@example.com')

    def test_get_volunteer_matches_no_match(self):
        # Event 2 ("Park Cleanup Day") date is 2026-11-20
        # "volunteer@example.com" is not available on that day
        response = self.app.get('/matching/2')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(json.loads(response.data)), 0)

    def test_get_volunteer_history_success(self):
        # init_db adds Event 1 to the volunteer's history
        response = self.app.get('/history/volunteer@example.com')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['event_name'], 'Community Food Drive')

    def test_get_skills_endpoint(self):
        response = self.app.get('/data/skills')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIsInstance(data, list)
        self.assertIn("Tech Support", data)

    def test_get_urgency_levels_endpoint(self):
        response = self.app.get('/data/urgency')
        self.assertEqual(response.status_code, 200)
        self.assertIn("Medium", json.loads(response.data))

    # --- NEW TESTS TO IMPROVE COVERAGE ---

    def test_get_statistics_success(self):
        """Test the /statistics endpoint."""
        # Dates are now future dates from init_db
        response = self.app.get('/statistics')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['total_users'], 2) 
        self.assertEqual(data['total_events'], 2)
        self.assertEqual(data['open_events'], 2) # Should be open

    def test_get_notifications_success(self):
        """Test the GET /notifications endpoint."""
        # Add a notification first
        with app.app_context():
            db.session.add(Notification(message="Test notification"))
            db.session.commit()
            
        response = self.app.get('/notifications')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['message'], 'Test notification')

    def test_mark_notification_read_success(self):
        """Test the PUT /notifications/<id>/read endpoint."""
        with app.app_context():
            n = Notification(message="Test")
            db.session.add(n)
            db.session.commit()
            notif_id = n.id

        response = self.app.put(f'/notifications/{notif_id}/read')
        self.assertEqual(response.status_code, 200)
        
        # Verify in DB
        with app.app_context():
            # FIX: Use db.session.get()
            n_updated = db.session.get(Notification, notif_id) 
            self.assertTrue(n_updated.read)

    def test_mark_notification_read_not_found(self):
        """Test marking a non-existent notification as read."""
        response = self.app.put('/notifications/999/read')
        self.assertEqual(response.status_code, 404)

    def test_register_user_invalid_email_400(self):
        """Test registration with a bad email to trigger a 400 Validation Error."""
        response = self.app.post('/register',
                                 data=json.dumps({"email": "bad-email", "password": "NewPassword1"}),
                                 content_type='application/json')
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertEqual(data['message'], 'Validation error')
        self.assertIn('Email is not valid', str(data['errors'])) 

    def test_update_profile_invalid_zipcode_400(self):
        """Test profile update with a bad zip code for a 400 error."""
        profile_data = {
            "full_name": "John D. Updated", "address1": "123 New St", "city": "Austin",
            "state": "TX", "zip_code": "bad", # <-- Invalid zip
            "skills": ["Marketing"], "availability": ["2026-01-01"]
        }
        response = self.app.put('/profile/volunteer@example.com',
                                data=json.dumps(profile_data),
                                content_type='application/json')
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('zip_code', str(data['errors']))

    def test_create_event_invalid_date_400(self):
        """Test event creation with a bad date format for a 400 error."""
        event_data = {
            "event_name": "New Charity Gala", "description": "A fancy event.",
            "location": "The Grand Hall", "required_skills": ["Catering"],
            "urgency": "High", "event_date": "05/10/2026" # <-- Invalid format
        }
        response = self.app.post('/events',
                                 data=json.dumps(event_data),
                                 content_type='application/json')
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('event_date', str(data['errors']))

    def test_get_volunteer_matches_event_not_found_404(self):
        """Test matching for a non-existent event."""
        response = self.app.get('/matching/999')
        self.assertEqual(response.status_code, 404)

    def test_get_volunteer_history_user_not_found_404(self):
        """Test history for a non-existent user."""
        response = self.app.get('/history/nouser@example.com')
        self.assertEqual(response.status_code, 404)

if __name__ == '__main__':
    unittest.main()