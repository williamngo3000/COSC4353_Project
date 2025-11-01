import unittest
import json
import sys
import os
import copy
from unittest.mock import patch
from datetime import datetime, timedelta

# Add the project's root directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, DB, add_notification, add_activity, get_event_volunteer_count, check_and_close_event, check_all_events_status

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

    # Test Cases 

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
        
    #  New Tests to Improve Coverage 

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

    # --- Business Logic Function Tests ---

    def test_add_notification(self):
        """Test adding notifications to the database"""
        initial_count = len(DB["notifications"])
        notification = add_notification("Test notification", "info")

        self.assertIsNotNone(notification)
        self.assertEqual(notification["message"], "Test notification")
        self.assertEqual(notification["type"], "info")
        self.assertFalse(notification["read"])
        self.assertEqual(len(DB["notifications"]), initial_count + 1)

    def test_notification_limit(self):
        """Test that notifications are limited to 50"""
        # Clear notifications
        DB["notifications"].clear()

        # Add 60 notifications
        for i in range(60):
            add_notification(f"Notification {i}", "info")

        # Should only have 50
        self.assertEqual(len(DB["notifications"]), 50)
        # The first notification should be the most recent
        self.assertEqual(DB["notifications"][0]["message"], "Notification 59")

    def test_add_activity(self):
        """Test adding activity to the activity log"""
        initial_count = len(DB["activity_log"])
        activity = add_activity("test_activity", user="test@example.com", details="Test details")

        self.assertIsNotNone(activity)
        self.assertEqual(activity["type"], "test_activity")
        self.assertEqual(activity["user"], "test@example.com")
        self.assertEqual(activity["details"], "Test details")
        self.assertEqual(len(DB["activity_log"]), initial_count + 1)

    def test_activity_limit(self):
        """Test that activity log is limited to 50"""
        # Clear activity log
        DB["activity_log"].clear()

        # Add 60 activities
        for i in range(60):
            add_activity("test_activity", count=i)

        # Should only have 50
        self.assertEqual(len(DB["activity_log"]), 50)

    def test_get_event_volunteer_count_zero(self):
        """Test getting volunteer count when no volunteers"""
        count = get_event_volunteer_count(999)
        self.assertEqual(count, 0)

    def test_get_event_volunteer_count_with_volunteers(self):
        """Test getting volunteer count with accepted invites"""
        # Add test invites
        DB["invites"].append({
            "id": 1,
            "event_id": 1,
            "user_email": "test1@example.com",
            "status": "accepted",
            "type": "admin_invite",
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
        DB["invites"].append({
            "id": 2,
            "event_id": 1,
            "user_email": "test2@example.com",
            "status": "pending",
            "type": "user_request",
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
        DB["invites"].append({
            "id": 3,
            "event_id": 1,
            "user_email": "test3@example.com",
            "status": "accepted",
            "type": "user_request",
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })

        # Should only count accepted invites
        count = get_event_volunteer_count(1)
        self.assertEqual(count, 2)

    def test_check_and_close_event_date_passed(self):
        """Test event closure when date has passed"""
        past_date = (datetime.now() - timedelta(days=5)).strftime("%Y-%m-%d")
        DB["events"][999] = {
            "event_name": "Past Event",
            "event_date": past_date,
            "status": "open",
            "volunteer_limit": None
        }

        result = check_and_close_event(999)
        self.assertTrue(result)
        self.assertEqual(DB["events"][999]["status"], "closed")

    def test_check_and_close_event_volunteer_limit_reached(self):
        """Test event closure when volunteer limit is reached"""
        future_date = (datetime.now() + timedelta(days=5)).strftime("%Y-%m-%d")
        DB["events"][998] = {
            "event_name": "Limited Event",
            "event_date": future_date,
            "status": "open",
            "volunteer_limit": 2
        }

        # Add 2 accepted volunteers
        DB["invites"].append({
            "id": 10,
            "event_id": 998,
            "user_email": "vol1@example.com",
            "status": "accepted",
            "type": "admin_invite",
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
        DB["invites"].append({
            "id": 11,
            "event_id": 998,
            "user_email": "vol2@example.com",
            "status": "accepted",
            "type": "admin_invite",
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })

        result = check_and_close_event(998)
        self.assertTrue(result)
        self.assertEqual(DB["events"][998]["status"], "closed")

    def test_check_and_close_event_already_closed(self):
        """Test that already closed events stay closed"""
        DB["events"][997] = {
            "event_name": "Closed Event",
            "event_date": "2024-12-01",
            "status": "closed",
            "volunteer_limit": None
        }

        result = check_and_close_event(997)
        self.assertFalse(result)
        self.assertEqual(DB["events"][997]["status"], "closed")

    def test_check_and_close_event_not_found(self):
        """Test handling of non-existent event"""
        result = check_and_close_event(99999)
        self.assertFalse(result)

    def test_check_all_events_status(self):
        """Test checking all events status"""
        past_date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        DB["events"][996] = {
            "event_name": "Should Close",
            "event_date": past_date,
            "status": "open",
            "volunteer_limit": None
        }

        check_all_events_status()
        self.assertEqual(DB["events"][996]["status"], "closed")

    # Invite/Request Management Tests 

    def test_create_user_request(self):
        """Test creating a user request to join an event"""
        # Create a future event
        future_date = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
        DB["events"][990] = {
            "event_name": "Future Event",
            "description": "Test event",
            "location": "Test Location",
            "required_skills": ["Test"],
            "urgency": "Medium",
            "event_date": future_date,
            "volunteer_limit": None,
            "status": "open"
        }

        request_data = {
            "event_id": 990,
            "user_email": "newvolunteer@example.com",
            "type": "user_request"
        }
        response = self.app.post('/invites',
                                data=json.dumps(request_data),
                                content_type='application/json')
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertEqual(data["invite"]["status"], "pending")

    def test_create_admin_invite(self):
        """Test admin inviting a volunteer to an event"""
        # Create a future event
        future_date = (datetime.now() + timedelta(days=45)).strftime("%Y-%m-%d")
        DB["events"][991] = {
            "event_name": "Future Event 2",
            "description": "Test event",
            "location": "Test Location",
            "required_skills": ["Test"],
            "urgency": "High",
            "event_date": future_date,
            "volunteer_limit": None,
            "status": "open"
        }

        invite_data = {
            "event_id": 991,
            "user_email": "volunteer@example.com",
            "type": "admin_invite"
        }
        response = self.app.post('/invites',
                                data=json.dumps(invite_data),
                                content_type='application/json')
        self.assertEqual(response.status_code, 201)

    def test_create_invite_event_not_found(self):
        """Test creating invite for non-existent event"""
        invite_data = {
            "event_id": 99999,
            "user_email": "volunteer@example.com",
            "type": "admin_invite"
        }
        response = self.app.post('/invites',
                                data=json.dumps(invite_data),
                                content_type='application/json')
        self.assertEqual(response.status_code, 404)

    def test_create_invite_closed_event(self):
        """Test creating invite for a closed event"""
        # Create a closed event
        past_date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        DB["events"][995] = {
            "event_name": "Closed Event",
            "event_date": past_date,
            "status": "open",
            "volunteer_limit": None
        }

        invite_data = {
            "event_id": 995,
            "user_email": "volunteer@example.com",
            "type": "user_request"
        }
        response = self.app.post('/invites',
                                data=json.dumps(invite_data),
                                content_type='application/json')
        self.assertEqual(response.status_code, 403)

    def test_duplicate_pending_invite(self):
        """Test that duplicate pending invites are prevented"""
        # Create a future event
        future_date = (datetime.now() + timedelta(days=60)).strftime("%Y-%m-%d")
        DB["events"][992] = {
            "event_name": "Duplicate Test Event",
            "description": "Test event",
            "location": "Test Location",
            "required_skills": ["Test"],
            "urgency": "Low",
            "event_date": future_date,
            "volunteer_limit": None,
            "status": "open"
        }

        invite_data = {
            "event_id": 992,
            "user_email": "duplicate@example.com",
            "type": "user_request"
        }

        # Create first invite
        response1 = self.app.post('/invites',
                                 data=json.dumps(invite_data),
                                 content_type='application/json')
        self.assertEqual(response1.status_code, 201)

        # Try to create duplicate
        response2 = self.app.post('/invites',
                                 data=json.dumps(invite_data),
                                 content_type='application/json')
        self.assertEqual(response2.status_code, 409)

    def test_get_invites(self):
        """Test getting all invites"""
        response = self.app.get('/invites')
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(json.loads(response.data), list)

    def test_get_invites_filtered_by_status(self):
        """Test filtering invites by status"""
        # Add test invites
        DB["invites"].append({
            "id": 100,
            "event_id": 1,
            "user_email": "test@example.com",
            "status": "pending",
            "type": "user_request",
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })

        response = self.app.get('/invites?status=pending')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        for invite in data:
            self.assertEqual(invite["status"], "pending")

    def test_update_invite_status(self):
        """Test updating an invite status"""
        # Create an invite first
        DB["invites"].append({
            "id": 200,
            "event_id": 1,
            "user_email": "update@example.com",
            "status": "pending",
            "type": "user_request",
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })

        response = self.app.put('/invites/200',
                               data=json.dumps({"status": "accepted"}),
                               content_type='application/json')
        self.assertEqual(response.status_code, 200)

        # Verify status was updated
        invite = next((inv for inv in DB["invites"] if inv["id"] == 200), None)
        self.assertEqual(invite["status"], "accepted")

    def test_update_invite_not_found(self):
        """Test updating non-existent invite"""
        response = self.app.put('/invites/99999',
                               data=json.dumps({"status": "accepted"}),
                               content_type='application/json')
        self.assertEqual(response.status_code, 404)

    def test_delete_invite(self):
        """Test deleting an invite"""
        # Create an invite first
        DB["invites"].append({
            "id": 300,
            "event_id": 1,
            "user_email": "delete@example.com",
            "status": "pending",
            "type": "user_request",
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })

        response = self.app.delete('/invites/300')
        self.assertEqual(response.status_code, 200)

        # Verify invite was deleted
        invite = next((inv for inv in DB["invites"] if inv["id"] == 300), None)
        self.assertIsNone(invite)

    def test_mark_invite_complete(self):
        """Test marking an invite as completed"""
        # Create user and accepted invite
        DB["users"]["complete@example.com"] = {
            "password": "Password1",
            "role": "volunteer",
            "profile": {},
            "history": []
        }

        DB["invites"].append({
            "id": 400,
            "event_id": 1,
            "user_email": "complete@example.com",
            "status": "accepted",
            "type": "user_request",
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })

        response = self.app.put('/invites/400/complete',
                               data=json.dumps({"completed": True}),
                               content_type='application/json')
        self.assertEqual(response.status_code, 200)

        # Verify event was added to history
        self.assertIn(1, DB["users"]["complete@example.com"]["history"])

    def test_unmark_invite_complete(self):
        """Test unmarking an invite as completed"""
        # Create user with history
        DB["users"]["uncomplete@example.com"] = {
            "password": "Password1",
            "role": "volunteer",
            "profile": {},
            "history": [1]
        }

        DB["invites"].append({
            "id": 500,
            "event_id": 1,
            "user_email": "uncomplete@example.com",
            "status": "accepted",
            "type": "user_request",
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "completed": True
        })

        response = self.app.put('/invites/500/complete',
                               data=json.dumps({"completed": False}),
                               content_type='application/json')
        self.assertEqual(response.status_code, 200)

        # Verify event was removed from history
        self.assertNotIn(1, DB["users"]["uncomplete@example.com"]["history"])

    def test_get_user_invites(self):
        """Test getting invites for a specific user"""
        response = self.app.get('/invites/user/volunteer@example.com')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIsInstance(data, list)

    # --- Event Management Tests ---

    def test_update_event(self):
        """Test updating an event"""
        updated_data = {
            "event_name": "Updated Food Drive",
            "description": "Updated description",
            "location": "New Location",
            "required_skills": ["Updated Skill"],
            "urgency": "Critical",
            "event_date": "2025-01-01"
        }
        response = self.app.put('/events/1',
                               data=json.dumps(updated_data),
                               content_type='application/json')
        self.assertEqual(response.status_code, 200)

        # Verify update
        self.assertEqual(DB["events"][1]["event_name"], "Updated Food Drive")

    def test_update_event_not_found(self):
        """Test updating non-existent event"""
        event_data = {
            "event_name": "Test",
            "description": "Test",
            "location": "Test",
            "required_skills": ["Test"],
            "urgency": "Low",
            "event_date": "2025-01-01"
        }
        response = self.app.put('/events/99999',
                               data=json.dumps(event_data),
                               content_type='application/json')
        self.assertEqual(response.status_code, 404)

    def test_delete_event(self):
        """Test deleting an event"""
        # Create a test event
        DB["events"][994] = {
            "event_name": "Delete Me",
            "description": "Test",
            "location": "Test",
            "required_skills": ["Test"],
            "urgency": "Low",
            "event_date": "2025-01-01",
            "status": "open"
        }

        response = self.app.delete('/events/994')
        self.assertEqual(response.status_code, 200)
        self.assertNotIn(994, DB["events"])

    def test_delete_event_not_found(self):
        """Test deleting non-existent event"""
        response = self.app.delete('/events/99999')
        self.assertEqual(response.status_code, 404)

    def test_get_specific_event(self):
        """Test getting a specific event by ID"""
        response = self.app.get('/events/1')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data["event_name"], "Community Food Drive")

    def test_get_specific_event_not_found(self):
        """Test getting non-existent event"""
        response = self.app.get('/events/99999')
        self.assertEqual(response.status_code, 404)

    def test_event_with_volunteer_limit(self):
        """Test creating event with volunteer limit"""
        event_data = {
            "event_name": "Limited Event",
            "description": "Only 5 volunteers",
            "location": "Test Location",
            "required_skills": ["Test"],
            "urgency": "Medium",
            "event_date": "2025-06-01",
            "volunteer_limit": 5
        }
        response = self.app.post('/events',
                                data=json.dumps(event_data),
                                content_type='application/json')
        self.assertEqual(response.status_code, 201)

    def test_event_with_invalid_volunteer_limit(self):
        """Test creating event with invalid volunteer limit"""
        event_data = {
            "event_name": "Invalid Limit",
            "description": "Test",
            "location": "Test",
            "required_skills": ["Test"],
            "urgency": "Low",
            "event_date": "2025-01-01",
            "volunteer_limit": 0
        }
        response = self.app.post('/events',
                                data=json.dumps(event_data),
                                content_type='application/json')
        self.assertEqual(response.status_code, 400)

    # --- User Management Tests ---

    def test_get_all_users(self):
        """Test getting all users"""
        response = self.app.get('/users')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIsInstance(data, list)
        self.assertGreater(len(data), 0)

    def test_update_user_role(self):
        """Test updating a user's role"""
        response = self.app.put('/users/volunteer@example.com',
                               data=json.dumps({"role": "admin"}),
                               content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(DB["users"]["volunteer@example.com"]["role"], "admin")

    def test_update_user_name(self):
        """Test updating a user's name"""
        response = self.app.put('/users/volunteer@example.com',
                               data=json.dumps({"name": "Updated Name"}),
                               content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(DB["users"]["volunteer@example.com"]["profile"]["full_name"], "Updated Name")

    def test_update_user_not_found(self):
        """Test updating non-existent user"""
        response = self.app.put('/users/nouser@example.com',
                               data=json.dumps({"role": "admin"}),
                               content_type='application/json')
        self.assertEqual(response.status_code, 404)

    def test_delete_user(self):
        """Test deleting a user"""
        # Create test user
        DB["users"]["deleteme@example.com"] = {
            "password": "Password1",
            "role": "volunteer",
            "profile": {},
            "history": []
        }

        response = self.app.delete('/users/deleteme@example.com')
        self.assertEqual(response.status_code, 200)
        self.assertNotIn("deleteme@example.com", DB["users"])

    def test_delete_user_not_found(self):
        """Test deleting non-existent user"""
        response = self.app.delete('/users/nouser@example.com')
        self.assertEqual(response.status_code, 404)

    def test_get_user_events(self):
        """Test getting events a user has signed up for"""
        response = self.app.get('/user/volunteer@example.com/events')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn("events", data)

    def test_get_user_events_not_found(self):
        """Test getting events for non-existent user"""
        response = self.app.get('/user/nouser@example.com/events')
        self.assertEqual(response.status_code, 404)

    # --- Notification Tests ---

    def test_get_notifications(self):
        """Test getting all notifications"""
        response = self.app.get('/notifications')
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(json.loads(response.data), list)

    def test_mark_notification_read(self):
        """Test marking a notification as read"""
        # Add a notification
        notification = add_notification("Test notification", "info")

        response = self.app.put(f'/notifications/{notification["id"]}/read')
        self.assertEqual(response.status_code, 200)

        # Verify it was marked as read
        updated_notif = next((n for n in DB["notifications"] if n["id"] == notification["id"]), None)
        self.assertTrue(updated_notif["read"])

    def test_mark_notification_read_not_found(self):
        """Test marking non-existent notification as read"""
        response = self.app.put('/notifications/99999/read')
        self.assertEqual(response.status_code, 404)

    # --- Activity Log Tests ---

    def test_get_activity(self):
        """Test getting activity log"""
        response = self.app.get('/activity')
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(json.loads(response.data), list)

    # --- Validation Tests ---

    def test_register_invalid_email(self):
        """Test registration with invalid email"""
        response = self.app.post('/register',
                                data=json.dumps({"email": "invalid-email", "password": "Password1"}),
                                content_type='application/json')
        self.assertEqual(response.status_code, 400)

    def test_register_password_too_short(self):
        """Test registration with password too short"""
        response = self.app.post('/register',
                                data=json.dumps({"email": "test@test.com", "password": "Pass1"}),
                                content_type='application/json')
        self.assertEqual(response.status_code, 400)

    def test_register_password_no_digit(self):
        """Test registration with password missing digit"""
        response = self.app.post('/register',
                                data=json.dumps({"email": "test@test.com", "password": "PasswordOnly"}),
                                content_type='application/json')
        self.assertEqual(response.status_code, 400)

    def test_register_password_no_uppercase(self):
        """Test registration with password missing uppercase"""
        response = self.app.post('/register',
                                data=json.dumps({"email": "test@test.com", "password": "password1"}),
                                content_type='application/json')
        self.assertEqual(response.status_code, 400)

    def test_update_profile_invalid_zip(self):
        """Test profile update with invalid zip code"""
        profile_data = {
            "full_name": "Test User",
            "address1": "123 Test St",
            "city": "Test City",
            "state": "TX",
            "zip_code": "ABC",
            "skills": ["Test"],
            "availability": ["2025-01-01"]
        }
        response = self.app.put('/profile/volunteer@example.com',
                               data=json.dumps(profile_data),
                               content_type='application/json')
        self.assertEqual(response.status_code, 400)

    def test_update_profile_name_too_long(self):
        """Test profile update with name too long"""
        profile_data = {
            "full_name": "A" * 51,
            "address1": "123 Test St",
            "city": "Test City",
            "state": "TX",
            "zip_code": "12345",
            "skills": ["Test"],
            "availability": ["2025-01-01"]
        }
        response = self.app.put('/profile/volunteer@example.com',
                               data=json.dumps(profile_data),
                               content_type='application/json')
        self.assertEqual(response.status_code, 400)

    def test_update_profile_empty_skills(self):
        """Test profile update with empty skills list"""
        profile_data = {
            "full_name": "Test User",
            "address1": "123 Test St",
            "city": "Test City",
            "state": "TX",
            "zip_code": "12345",
            "skills": [],
            "availability": ["2025-01-01"]
        }
        response = self.app.put('/profile/volunteer@example.com',
                               data=json.dumps(profile_data),
                               content_type='application/json')
        self.assertEqual(response.status_code, 400)

    def test_create_event_empty_name(self):
        """Test creating event with empty name"""
        event_data = {
            "event_name": "",
            "description": "Test",
            "location": "Test",
            "required_skills": ["Test"],
            "urgency": "Low",
            "event_date": "2025-01-01"
        }
        response = self.app.post('/events',
                                data=json.dumps(event_data),
                                content_type='application/json')
        self.assertEqual(response.status_code, 400)

    def test_create_event_name_too_long(self):
        """Test creating event with name too long"""
        event_data = {
            "event_name": "A" * 101,
            "description": "Test",
            "location": "Test",
            "required_skills": ["Test"],
            "urgency": "Low",
            "event_date": "2025-01-01"
        }
        response = self.app.post('/events',
                                data=json.dumps(event_data),
                                content_type='application/json')
        self.assertEqual(response.status_code, 400)

    def test_create_event_empty_skills(self):
        """Test creating event with empty required skills"""
        event_data = {
            "event_name": "Test Event",
            "description": "Test",
            "location": "Test",
            "required_skills": [],
            "urgency": "Low",
            "event_date": "2025-01-01"
        }
        response = self.app.post('/events',
                                data=json.dumps(event_data),
                                content_type='application/json')
        self.assertEqual(response.status_code, 400)

if __name__ == '__main__':
    unittest.main()

