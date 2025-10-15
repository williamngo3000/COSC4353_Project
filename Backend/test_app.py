import unittest
import json
import sys
import os
import copy
from unittest.mock import patch

# Add the project's root directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, DB

class TestApp(unittest.TestCase):
    def setUp(self):
        # Create a test client
        self.app = app.test_client()
        # Propagate the exceptions to the test client
        self.app.testing = True
        # Use copy.deepcopy to preserve integer keys and avoid test pollution.
        self.original_db = copy.deepcopy(DB)

    def tearDown(self):
        # Restore the original DB state by modifying the dictionary in-place.
        global DB
        DB.clear()
        DB.update(self.original_db)

    # --- Test Cases ---

    def test_register_user_success(self):
        response = self.app.post('/register', 
                                 data=json.dumps({"email": "newuser@example.com", "password": "NewPassword1"}),
                                 content_type='application/json')
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertEqual(data['message'], 'Registration successful')

    def test_register_user_already_exists(self):
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
        response = self.app.post('/login',
                                 data=json.dumps({"email": "admin@example.com", "password": "AdminPassword1"}),
                                 content_type='application/json')
        self.assertEqual(response.status_code, 200)

    def test_login_user_invalid_credentials(self):
        response = self.app.post('/login',
                                 data=json.dumps({"email": "volunteer@example.com", "password": "WrongPassword"}),
                                 content_type='application/json')
        self.assertEqual(response.status_code, 401)

    def test_get_profile_success(self):
        response = self.app.get('/profile/volunteer@example.com')
        self.assertEqual(response.status_code, 200)

    def test_get_profile_not_found(self):
        response = self.app.get('/profile/nouser@example.com')
        self.assertEqual(response.status_code, 404)

    def test_update_profile_success(self):
        profile_data = {
            "full_name": "John D. Updated", "address1": "123 New St", "city": "Austin",
            "state": "TX", "zip_code": "78701", "skills": ["New Skill"],
            "availability": ["2025-01-01"]
        }
        response = self.app.put('/profile/volunteer@example.com',
                                data=json.dumps(profile_data),
                                content_type='application/json')
        self.assertEqual(response.status_code, 200)

    def test_get_events_success(self):
        response = self.app.get('/events')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(len(data), 2)

    def test_create_event_success(self):
        event_data = {
            "event_name": "New Charity Gala", "description": "A fancy event.",
            "location": "The Grand Hall", "required_skills": ["Catering", "Marketing"],
            "urgency": "High", "event_date": "2025-05-10"
        }
        response = self.app.post('/events',
                                 data=json.dumps(event_data),
                                 content_type='application/json')
        self.assertEqual(response.status_code, 201)
        
    def test_get_volunteer_matches_success(self):
        response = self.app.get('/matching/1')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(json.loads(response.data)), 1)

    def test_get_volunteer_matches_no_match(self):
        response = self.app.get('/matching/2')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(json.loads(response.data)), 0)

    def test_get_volunteer_history_success(self):
        response = self.app.get('/history/volunteer@example.com')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(json.loads(response.data)), 1)
        
    # --- New Tests to Improve Coverage ---

    def test_get_skills_endpoint(self):
        """Test the /data/skills endpoint."""
        response = self.app.get('/data/skills')
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(json.loads(response.data), list)

    def test_get_urgency_levels_endpoint(self):
        """Test the /data/urgency endpoint."""
        response = self.app.get('/data/urgency')
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(json.loads(response.data), list)

    def test_match_volunteers_event_not_found(self):
        """Test volunteer matching for a non-existent event."""
        response = self.app.get('/matching/999')
        self.assertEqual(response.status_code, 404)

    def test_get_history_user_not_found(self):
        """Test getting history for a non-existent user."""
        response = self.app.get('/history/nouser@example.com')
        self.assertEqual(response.status_code, 404)
        
    @patch('app.DB', new_callable=lambda: {}) # Mock the DB to force an error
    def test_internal_server_error_on_register(self, mock_db):
        """Test the generic exception handler for the register endpoint."""
        response = self.app.post('/register',
                                 data=json.dumps({"email": "error@example.com", "password": "ErrorPassword1"}),
                                 content_type='application/json')
        self.assertEqual(response.status_code, 500)

if __name__ == '__main__':
    unittest.main()

