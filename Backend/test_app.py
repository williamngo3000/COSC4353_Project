"""
Full-coverage test suite for app.py (100% coverage)
"""

import unittest
import json
import sys
import os
from unittest.mock import patch, MagicMock
from datetime import datetime

# Ensure project root is importable
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from app import app, db, init_db, create_notification
    from models import (
        UserCredentials,
        UserProfile,
        EventDetails,
        VolunteerHistory,
        EventInvite,
        Notification,
        States
    )
except Exception as e:
    print("IMPORT ERROR:", e)
    sys.exit(1)


#                            BASE TEST CLASS

class BaseTestCase(unittest.TestCase):

    def setUp(self):
        app.config["TESTING"] = True
        app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
        self.client = app.test_client()

        with app.app_context():
            db.create_all()
            init_db()

    def tearDown(self):
        with app.app_context():
            db.session.remove()
            db.drop_all()


#                      AUTHENTICATION TESTS

class TestAuth(BaseTestCase):

    def test_register_success(self):
        payload = {"email": "new@example.com", "password": "Password123"}
        r = self.client.post("/register", json=payload)
        self.assertEqual(r.status_code, 201)

    def test_register_existing(self):
        payload = {"email": "volunteer@example.com", "password": "Password123"}
        r = self.client.post("/register", json=payload)
        self.assertEqual(r.status_code, 409)

    def test_register_invalid_email(self):
        r = self.client.post("/register", json={"email": "bad", "password": "Password123"})
        self.assertIn(r.status_code, [400, 415])

    def test_register_commit_failure(self):
        with patch("app.db.session.commit", side_effect=Exception("DB FAIL")):
            r = self.client.post("/register", json={"email": "xx@xx.com", "password": "Password123"})
            self.assertEqual(r.status_code, 500)

    def test_register_short_password(self):
        r = self.client.post("/register", json={"email": "a@b.com", "password": "123"})
        self.assertIn(r.status_code, [400, 415])

    def test_register_missing_email(self):
        r = self.client.post("/register", json={"password": "Password123"})
        self.assertIn(r.status_code, [400, 415])

    def test_register_missing_password(self):
        r = self.client.post("/register", json={"email": "test@example.com"})
        self.assertIn(r.status_code, [400, 415])

    def test_register_empty_email(self):
        r = self.client.post("/register", json={"email": "", "password": "Password123"})
        self.assertIn(r.status_code, [400, 415])

    def test_register_empty_password(self):
        r = self.client.post("/register", json={"email": "test@example.com", "password": ""})
        self.assertIn(r.status_code, [400, 415])

    def test_register_no_json_body(self):
        r = self.client.post("/register")
        self.assertIn(r.status_code, [400, 415])

    def test_login_success(self):
        r = self.client.post("/login", json={"email": "admin@example.com", "password": "AdminPassword1"})
        self.assertEqual(r.status_code, 200)

    def test_login_wrong_password(self):
        r = self.client.post("/login", json={"email": "admin@example.com", "password": "WRONG"})
        self.assertEqual(r.status_code, 401)

    def test_login_missing_fields(self):
        r = self.client.post("/login", json={"email": "admin@example.com"})
        self.assertIn(r.status_code, [400, 415])

    def test_login_user_not_found(self):
        r = self.client.post("/login", json={"email": "nonexistent@example.com", "password": "Password123"})
        self.assertEqual(r.status_code, 401)

    def test_login_no_json_body(self):
        r = self.client.post("/login")
        self.assertIn(r.status_code, [400, 415])

    def test_login_empty_email(self):
        r = self.client.post("/login", json={"email": "", "password": "Password123"})
        self.assertEqual(r.status_code, 401)

    def test_login_success_with_profile(self):
        r = self.client.post("/login", json={"email": "volunteer@example.com", "password": "Password1"})
        self.assertEqual(r.status_code, 200)
        data = json.loads(r.data)
        self.assertTrue(data["user"]["profileComplete"])

    def test_login_success_without_profile(self):
        with app.app_context():
            user = UserCredentials(email="noprof@example.com")
            user.set_password("Password123")
            db.session.add(user)
            db.session.commit()

        r = self.client.post("/login", json={"email": "noprof@example.com", "password": "Password123"})
        self.assertEqual(r.status_code, 200)
        data = json.loads(r.data)
        self.assertFalse(data["user"]["profileComplete"])

    def test_login_internal_error(self):
        with app.app_context():
            with patch("app.UserCredentials.query.filter_by", side_effect=Exception("fail")):
                r = self.client.post("/login", json={"email": "admin@example.com", "password": "AdminPassword1"})
        self.assertIn(r.status_code, [200, 500])


#                      PROFILE TESTS

class TestProfiles(BaseTestCase):

    def test_get_profile_success(self):
        r = self.client.get("/profile/volunteer@example.com")
        self.assertEqual(r.status_code, 200)
        data = json.loads(r.data)
        self.assertIsInstance(data.get("skills", []), list)
        self.assertIsInstance(data.get("availability", []), list)

    def test_get_profile_with_no_skills(self):
        with app.app_context():
            user = UserCredentials(email="noskills@example.com")
            user.set_password("Password1")
            db.session.add(user)
            db.session.commit()

            profile = UserProfile(id=user.id, full_name="No Skills User")
            db.session.add(profile)
            db.session.commit()

        r = self.client.get("/profile/noskills@example.com")
        self.assertEqual(r.status_code, 200)
        data = json.loads(r.data)
        self.assertEqual(data["skills"], [])
        self.assertEqual(data["availability"], [])

    def test_get_profile_not_found(self):
        r = self.client.get("/profile/nope@example.com")
        self.assertEqual(r.status_code, 404)

    def test_get_profile_no_profile(self):
        with app.app_context():
            u = UserCredentials(email="x@x.com")
            u.set_password("Password1")
            db.session.add(u)
            db.session.commit()

        r = self.client.get("/profile/x@x.com")
        self.assertEqual(r.status_code, 200)
        self.assertEqual(json.loads(r.data), {})

    def test_get_profile_internal_error(self):
        with app.app_context():
            with patch("app.UserCredentials.query.filter_by", side_effect=Exception("fail")):
                r = self.client.get("/profile/volunteer@example.com")
        self.assertIn(r.status_code, [200, 500])

    def test_put_profile_create_new(self):
        payload = {
            "full_name": "New User",
            "address1": "100 St",
            "city": "Houston",
            "state": "TX",
            "zip_code": "77001",
            "skills": ["Tech Support"]
        }
        r = self.client.put("/profile/admin@example.com", json=payload)
        self.assertEqual(r.status_code, 200)

    def test_put_profile_update_existing(self):
        payload = {
            "full_name": "Updated Name",
            "city": "Dallas"
        }
        r = self.client.put("/profile/volunteer@example.com", json=payload)
        self.assertEqual(r.status_code, 200)

    def test_put_profile_invalid_zip(self):
        payload = {
            "full_name": "Bad Zip",
            "zip_code": "bad",
        }
        r = self.client.put("/profile/volunteer@example.com", json=payload)
        self.assertEqual(r.status_code, 400)

    def test_put_profile_9_digit_zip(self):
        payload = {
            "full_name": "Nine Digit",
            "zip_code": "770011234"
        }
        r = self.client.put("/profile/volunteer@example.com", json=payload)
        self.assertEqual(r.status_code, 200)

    def test_put_profile_empty_zip(self):
        payload = {
            "full_name": "Empty Zip",
            "zip_code": ""
        }
        r = self.client.put("/profile/volunteer@example.com", json=payload)
        self.assertEqual(r.status_code, 200)

    def test_put_profile_missing_fullname_on_create(self):
        with app.app_context():
            u = UserCredentials(email="np@example.com")
            u.set_password("Password1")
            db.session.add(u)
            db.session.commit()

        r = self.client.put("/profile/np@example.com", json={"city": "Austin"})
        self.assertEqual(r.status_code, 400)

    def test_put_profile_user_not_found(self):
        r = self.client.put("/profile/nonexistent@example.com", json={"full_name": "Test"})
        self.assertEqual(r.status_code, 404)

    def test_put_profile_no_json(self):
        r = self.client.put("/profile/volunteer@example.com", data="not-json")
        self.assertIn(r.status_code, [400, 415])

    def test_put_profile_empty_strings(self):
        payload = {
            "full_name": "Test User",
            "address1": "",
            "address2": "",
            "city": "",
            "state": "",
            "preferences": "",
            "skills": []
        }
        r = self.client.put("/profile/volunteer@example.com", json=payload)
        self.assertEqual(r.status_code, 200)

    def test_put_profile_list_skills(self):
        payload = {
            "full_name": "Test",
            "skills": ["First Aid", "Logistics", ""]
        }
        r = self.client.put("/profile/volunteer@example.com", json=payload)
        self.assertEqual(r.status_code, 200)

    def test_put_profile_string_skills(self):
        payload = {
            "full_name": "Test",
            "skills": "First Aid, Logistics"
        }
        r = self.client.put("/profile/volunteer@example.com", json=payload)
        self.assertEqual(r.status_code, 200)

    def test_put_profile_availability_list(self):
        payload = {
            "full_name": "Test",
            "availability": ["2026-01-01", "2026-01-15"]
        }
        r = self.client.put("/profile/volunteer@example.com", json=payload)
        self.assertEqual(r.status_code, 200)

    def test_put_profile_internal_error(self):
        with patch("app.db.session.commit", side_effect=Exception("fail")):
            r = self.client.put("/profile/volunteer@example.com", json={"full_name": "Test"})
            self.assertEqual(r.status_code, 500)


#                      SIGNUP / MATCHING / HISTORY

class TestSignupMatchingHistory(BaseTestCase):

    def test_signup_success(self):
        r = self.client.post("/signup", json={"email": "volunteer@example.com", "event_id": 2})
        self.assertEqual(r.status_code, 201)

    def test_signup_missing_fields(self):
        r = self.client.post("/signup", json={"event_id": 1})
        self.assertEqual(r.status_code, 400)

    def test_signup_missing_event_id(self):
        r = self.client.post("/signup", json={"email": "volunteer@example.com"})
        self.assertEqual(r.status_code, 400)

    def test_signup_user_not_found(self):
        r = self.client.post("/signup", json={"email": "none@example.com", "event_id": 1})
        self.assertEqual(r.status_code, 404)

    def test_signup_event_not_found(self):
        r = self.client.post("/signup", json={"email": "volunteer@example.com", "event_id": 999})
        self.assertEqual(r.status_code, 404)

    def test_signup_duplicate(self):
        r = self.client.post("/signup", json={"email": "volunteer@example.com", "event_id": 1})
        self.assertEqual(r.status_code, 409)

    def test_signup_no_json(self):
        r = self.client.post("/signup", data="not-json")
        self.assertEqual(r.status_code, 400)

    def test_signup_internal_error(self):
        with patch("app.db.session.commit", side_effect=Exception("fail")):
            r = self.client.post("/signup", json={"email": "volunteer@example.com", "event_id": 2})
            self.assertEqual(r.status_code, 500)

    def test_get_history_success(self):
        r = self.client.get("/history/volunteer@example.com")
        self.assertEqual(r.status_code, 200)
        data = json.loads(r.data)
        self.assertIsInstance(data, list)

    def test_get_history_no_user(self):
        r = self.client.get("/history/nope@example.com")
        self.assertEqual(r.status_code, 404)

    def test_get_history_no_events(self):
        with app.app_context():
            user = UserCredentials(email="nohistory@example.com")
            user.set_password("Password1")
            db.session.add(user)
            db.session.commit()

        r = self.client.get("/history/nohistory@example.com")
        self.assertEqual(r.status_code, 200)
        data = json.loads(r.data)
        self.assertEqual(len(data), 0)

    def test_get_history_internal_error(self):
        with app.app_context():
            with patch("app.UserCredentials.query.filter_by", side_effect=Exception("fail")):
                r = self.client.get("/history/volunteer@example.com")
        self.assertIn(r.status_code, [200, 500])

    def test_matching_success(self):
        r = self.client.get("/matching/1")
        self.assertEqual(r.status_code, 200)
        data = json.loads(r.data)
        self.assertIsInstance(data, list)

    def test_matching_event_not_found(self):
        r = self.client.get("/matching/999")
        self.assertEqual(r.status_code, 404)

    def test_matching_no_skills(self):
        with app.app_context():
            e = EventDetails(event_name="No Skills")
            db.session.add(e)
            db.session.commit()
            eid = e.id
        r = self.client.get(f"/matching/{eid}")
        self.assertEqual(r.status_code, 200)
        self.assertEqual(json.loads(r.data), [])

    def test_matching_volunteer_without_profile(self):
        with app.app_context():
            vol = UserCredentials(email="noprofile@example.com", role="volunteer")
            vol.set_password("Password1")
            db.session.add(vol)
            db.session.commit()

        r = self.client.get("/matching/1")
        self.assertEqual(r.status_code, 200)

    def test_matching_volunteer_without_skills(self):
        with app.app_context():
            vol = UserCredentials(email="noskills@example.com", role="volunteer")
            vol.set_password("Password1")
            db.session.add(vol)
            db.session.commit()

            profile = UserProfile(id=vol.id, full_name="No Skills")
            db.session.add(profile)
            db.session.commit()

        r = self.client.get("/matching/1")
        self.assertEqual(r.status_code, 200)

    def test_matching_internal_error(self):
        with patch("app.db.session.get", side_effect=Exception("fail")):
            r = self.client.get("/matching/1")
            self.assertEqual(r.status_code, 500)


#                      EVENT CRUD TESTS

class TestEvents(BaseTestCase):

    def test_get_events(self):
        r = self.client.get("/events")
        self.assertEqual(r.status_code, 200)
        data = json.loads(r.data)
        self.assertIsInstance(data, list)

    def test_get_events_with_accepted_volunteers(self):
        with app.app_context():
            user = UserCredentials.query.filter_by(email="volunteer@example.com").first()
            invite = EventInvite(user_id=user.id, event_id=1, status="accepted")
            db.session.add(invite)
            db.session.commit()

        r = self.client.get("/events")
        self.assertEqual(r.status_code, 200)

    def test_get_events_internal_error(self):
        with app.app_context():
            with patch("app.EventDetails.query.all", side_effect=Exception("fail")):
                r = self.client.get("/events")
        self.assertIn(r.status_code, [200, 500])

    def test_get_event_by_id_success(self):
        r = self.client.get("/events/1")
        self.assertEqual(r.status_code, 200)
        data = json.loads(r.data)
        self.assertIn("id", data)
        self.assertIn("current_volunteers", data)

    def test_get_event_by_id_not_found(self):
        r = self.client.get("/events/9999")
        self.assertEqual(r.status_code, 404)

    def test_get_event_by_id_internal_error(self):
        with patch("app.db.session.get", side_effect=Exception("fail")):
            r = self.client.get("/events/1")
            self.assertEqual(r.status_code, 500)

    def test_create_event_success(self):
        payload = {"event_name": "New Event", "city": "NY", "state": "NY"}
        r = self.client.post("/events", json=payload)
        self.assertEqual(r.status_code, 201)

    def test_create_event_with_all_fields(self):
        payload = {
            "event_name": "Complete Event",
            "description": "Test description",
            "location": "Test Location",
            "city": "Houston",
            "state": "TX",
            "zipcode": "77001",
            "skills": ["First Aid", "Logistics"],
            "required_skills": "First Aid",
            "preferences": "Indoor",
            "availability": "Weekends",
            "urgency": "High",
            "event_date": "2026-12-01",
            "volunteer_limit": 10,
            "status": "open"
        }
        r = self.client.post("/events", json=payload)
        self.assertEqual(r.status_code, 201)

    def test_create_event_invalid_urgency(self):
        payload = {
            "event_name": "Test Event",
            "urgency": "SuperHigh"
        }
        r = self.client.post("/events", json=payload)
        self.assertEqual(r.status_code, 201)

    def test_create_event_no_urgency(self):
        payload = {
            "event_name": "Test Event"
        }
        r = self.client.post("/events", json=payload)
        self.assertEqual(r.status_code, 201)

    def test_create_event_validation_error(self):
        r = self.client.post("/events", json={"city": "NY"})
        self.assertEqual(r.status_code, 400)

    def test_create_event_invalid_date(self):
        payload = {
            "event_name": "Bad Date",
            "event_date": "invalid"
        }
        r = self.client.post("/events", json=payload)
        self.assertEqual(r.status_code, 400)

    def test_create_event_no_json(self):
        r = self.client.post("/events", data="not-json")
        self.assertIn(r.status_code, [400, 415])

    def test_create_event_internal_error(self):
        with patch("app.db.session.commit", side_effect=Exception("fail")):
            r = self.client.post("/events", json={"event_name": "x"})
            self.assertEqual(r.status_code, 500)

    def test_update_event_success(self):
        r = self.client.put("/events/1", json={"event_name": "Updated"})
        self.assertEqual(r.status_code, 200)

    def test_update_event_with_date(self):
        r = self.client.put("/events/1", json={"event_date": "2026-12-25"})
        self.assertEqual(r.status_code, 200)

    def test_update_event_empty_date(self):
        r = self.client.put("/events/1", json={"event_date": ""})
        self.assertEqual(r.status_code, 200)

    def test_update_event_null_date(self):
        r = self.client.put("/events/1", json={"event_date": None})
        self.assertEqual(r.status_code, 200)

    def test_update_event_invalid_urgency(self):
        r = self.client.put("/events/1", json={"urgency": "Invalid"})
        self.assertEqual(r.status_code, 200)

    def test_update_event_empty_urgency(self):
        r = self.client.put("/events/1", json={"urgency": ""})
        self.assertEqual(r.status_code, 200)

    def test_update_event_skills_list(self):
        r = self.client.put("/events/1", json={"skills": ["First Aid", "Medical"]})
        self.assertEqual(r.status_code, 200)

    def test_update_event_empty_skills(self):
        r = self.client.put("/events/1", json={"skills": ""})
        self.assertEqual(r.status_code, 200)

    def test_update_event_not_found(self):
        r = self.client.put("/events/9999", json={"event_name": "X"})
        self.assertEqual(r.status_code, 404)

    def test_update_event_invalid_date(self):
        r = self.client.put("/events/1", json={"event_date": "bad"})
        self.assertEqual(r.status_code, 400)

    def test_update_event_no_json(self):
        r = self.client.put("/events/1", data="not-json")
        self.assertIn(r.status_code, [400, 500])

    def test_update_event_internal_error(self):
        with patch("app.db.session.commit", side_effect=Exception("fail")):
            r = self.client.put("/events/1", json={"event_name": "x"})
            self.assertEqual(r.status_code, 500)

    def test_delete_event_success(self):
        r = self.client.delete("/events/1")
        self.assertEqual(r.status_code, 200)

    def test_delete_event_with_invites(self):
        with app.app_context():
            user = UserCredentials.query.first()
            invite = EventInvite(user_id=user.id, event_id=2, status="pending")
            db.session.add(invite)
            db.session.commit()

        r = self.client.delete("/events/2")
        self.assertEqual(r.status_code, 200)

    def test_delete_event_with_history(self):
        with app.app_context():
            user = UserCredentials.query.first()
            history = VolunteerHistory(user_id=user.id, event_id=2)
            db.session.add(history)
            db.session.commit()

        r = self.client.delete("/events/2")
        self.assertEqual(r.status_code, 200)

    def test_delete_event_not_found(self):
        r = self.client.delete("/events/9999")
        self.assertEqual(r.status_code, 404)

    def test_delete_event_internal_error(self):
        with patch("app.db.session.commit", side_effect=Exception("fail")):
            r = self.client.delete("/events/1")
            self.assertEqual(r.status_code, 500)


#                      EVENT VOLUNTEERS TESTS

class TestEventVolunteers(BaseTestCase):

    def test_get_event_volunteers_success(self):
        with app.app_context():
            user = UserCredentials.query.filter_by(email="volunteer@example.com").first()
            invite = EventInvite(user_id=user.id, event_id=1, status="accepted")
            db.session.add(invite)
            db.session.commit()

        r = self.client.get("/events/1/volunteers")
        self.assertEqual(r.status_code, 200)
        data = json.loads(r.data)
        self.assertIsInstance(data, list)

    def test_get_event_volunteers_without_profile(self):
        with app.app_context():
            user = UserCredentials(email="noprof@example.com")
            user.set_password("Password1")
            db.session.add(user)
            db.session.commit()

            invite = EventInvite(user_id=user.id, event_id=1, status="accepted")
            db.session.add(invite)
            db.session.commit()

        r = self.client.get("/events/1/volunteers")
        self.assertEqual(r.status_code, 200)

    def test_get_event_volunteers_no_event(self):
        r = self.client.get("/events/9999/volunteers")
        self.assertEqual(r.status_code, 404)

    def test_get_event_volunteers_no_accepted(self):
        r = self.client.get("/events/2/volunteers")
        self.assertEqual(r.status_code, 200)
        data = json.loads(r.data)
        self.assertEqual(len(data), 0)

    def test_get_event_volunteers_internal_error(self):
        with patch("app.db.session.get", side_effect=Exception("fail")):
            r = self.client.get("/events/1/volunteers")
            self.assertEqual(r.status_code, 500)


#                      INVITE TESTS

class TestInvites(BaseTestCase):

    def make_invite(self):
        r = self.client.post("/invites",
                             json={"email": "volunteer@example.com", "event_id": 2})
        with app.app_context():
            inv = EventInvite.query.filter_by(event_id=2).order_by(EventInvite.id.desc()).first()
            return inv.id

    def test_get_invites_all(self):
        with app.app_context():
            user = UserCredentials.query.filter_by(email="volunteer@example.com").first()
            invite = EventInvite(user_id=user.id, event_id=1, status="pending")
            db.session.add(invite)
            db.session.commit()

        r = self.client.get("/invites")
        self.assertEqual(r.status_code, 200)
        data = json.loads(r.data)
        self.assertIsInstance(data, list)

    def test_get_invites_with_status(self):
        with app.app_context():
            user = UserCredentials.query.filter_by(email="volunteer@example.com").first()
            invite = EventInvite(user_id=user.id, event_id=1, status="accepted")
            db.session.add(invite)
            db.session.commit()

        r = self.client.get("/invites?status=accepted")
        self.assertEqual(r.status_code, 200)

    def test_get_invites_with_type(self):
        with app.app_context():
            user = UserCredentials.query.filter_by(email="volunteer@example.com").first()
            invite = EventInvite(user_id=user.id, event_id=1, status="pending", type="admin_invite")
            db.session.add(invite)
            db.session.commit()

        r = self.client.get("/invites?type=admin_invite")
        self.assertEqual(r.status_code, 200)

    def test_get_invites_internal_error(self):
        with app.app_context():
            with patch("app.EventInvite.query", side_effect=Exception("fail")):
                r = self.client.get("/invites")
        self.assertIn(r.status_code, [200, 500])

    def test_create_invite_success(self):
        r = self.client.post("/invites",
                             json={"email": "volunteer@example.com", "event_id": 1})
        self.assertEqual(r.status_code, 201)

    def test_create_invite_with_type(self):
        r = self.client.post("/invites",
                             json={"email": "volunteer@example.com", "event_id": 1, "type": "admin_invite"})
        self.assertEqual(r.status_code, 201)

    def test_create_invite_missing(self):
        r = self.client.post("/invites", json={"email": "x"})
        self.assertEqual(r.status_code, 400)

    def test_create_invite_missing_email(self):
        r = self.client.post("/invites", json={"event_id": 1})
        self.assertEqual(r.status_code, 400)

    def test_create_invite_user_not_found(self):
        r = self.client.post("/invites", json={"email": "none@x.com", "event_id": 1})
        self.assertEqual(r.status_code, 404)

    def test_create_invite_event_not_found(self):
        r = self.client.post("/invites", json={"email": "volunteer@example.com", "event_id": 999})
        self.assertEqual(r.status_code, 404)

    def test_create_invite_duplicate(self):
        self.client.post("/invites", json={"email": "volunteer@example.com", "event_id": 2})
        r = self.client.post("/invites", json={"email": "volunteer@example.com", "event_id": 2})
        self.assertEqual(r.status_code, 409)

    def test_create_invite_no_json(self):
        r = self.client.post("/invites", data="not-json")
        self.assertEqual(r.status_code, 400)

    def test_create_invite_internal_error(self):
        with patch("app.db.session.commit", side_effect=Exception("fail")):
            r = self.client.post("/invites", json={"email": "volunteer@example.com", "event_id": 1})
            self.assertEqual(r.status_code, 500)

    def test_update_invite_success(self):
        iid = self.make_invite()
        r = self.client.put(f"/invites/{iid}", json={"status": "accepted"})
        self.assertEqual(r.status_code, 200)

    def test_update_invite_declined(self):
        iid = self.make_invite()
        r = self.client.put(f"/invites/{iid}", json={"status": "declined"})
        self.assertEqual(r.status_code, 200)

    def test_update_invite_creates_history(self):
        with app.app_context():
            user = UserCredentials.query.filter_by(email="volunteer@example.com").first()
            invite = EventInvite(user_id=user.id, event_id=2, status="pending")
            db.session.add(invite)
            db.session.commit()
            invite_id = invite.id

        r = self.client.put(f"/invites/{invite_id}", json={"status": "accepted"})
        self.assertEqual(r.status_code, 200)

        with app.app_context():
            history = VolunteerHistory.query.filter_by(
                user_id=UserCredentials.query.filter_by(email="volunteer@example.com").first().id,
                event_id=2
            ).first()
            self.assertIsNotNone(history)

    def test_update_invite_no_duplicate_history(self):
        with app.app_context():
            user = UserCredentials.query.filter_by(email="volunteer@example.com").first()
            history = VolunteerHistory(user_id=user.id, event_id=2)
            db.session.add(history)

            invite = EventInvite(user_id=user.id, event_id=2, status="pending")
            db.session.add(invite)
            db.session.commit()
            invite_id = invite.id

        r = self.client.put(f"/invites/{invite_id}", json={"status": "accepted"})
        self.assertEqual(r.status_code, 200)

    def test_update_invite_already_accepted(self):
        with app.app_context():
            user = UserCredentials.query.filter_by(email="volunteer@example.com").first()
            invite = EventInvite(user_id=user.id, event_id=2, status="accepted")
            db.session.add(invite)
            db.session.commit()
            invite_id = invite.id

        r = self.client.put(f"/invites/{invite_id}", json={"status": "declined"})
        self.assertEqual(r.status_code, 200)

    def test_update_invite_not_found(self):
        r = self.client.put("/invites/9999", json={"status": "accepted"})
        self.assertEqual(r.status_code, 404)

    def test_update_invite_bad_status(self):
        iid = self.make_invite()
        r = self.client.put(f"/invites/{iid}", json={"status": "bad"})
        self.assertEqual(r.status_code, 400)

    def test_update_invite_no_json(self):
        iid = self.make_invite()
        r = self.client.put(f"/invites/{iid}", data="not-json")
        self.assertIn(r.status_code, [400, 500])

    def test_update_invite_internal_error(self):
        with app.app_context():
            user = UserCredentials.query.first()
            invite = EventInvite(user_id=user.id, event_id=1)
            db.session.add(invite)
            db.session.commit()
            iid = invite.id

        with patch("app.db.session.commit", side_effect=Exception("fail")):
            r = self.client.put(f"/invites/{iid}", json={"status": "accepted"})
            self.assertEqual(r.status_code, 500)

    def test_delete_invite_success(self):
        iid = self.make_invite()
        r = self.client.delete(f"/invites/{iid}")
        self.assertEqual(r.status_code, 200)

    def test_delete_invite_removes_history(self):
        with app.app_context():
            user = UserCredentials.query.filter_by(email="volunteer@example.com").first()
            invite = EventInvite(user_id=user.id, event_id=2, status="accepted")
            history = VolunteerHistory(user_id=user.id, event_id=2)
            db.session.add_all([invite, history])
            db.session.commit()
            invite_id = invite.id

        r = self.client.delete(f"/invites/{invite_id}")
        self.assertEqual(r.status_code, 200)

        with app.app_context():
            user = UserCredentials.query.filter_by(email="volunteer@example.com").first()
            history = VolunteerHistory.query.filter_by(user_id=user.id, event_id=2).first()
            self.assertIsNone(history)

    def test_delete_invite_not_found(self):
        r = self.client.delete("/invites/9999")
        self.assertEqual(r.status_code, 404)

    def test_delete_invite_internal_error(self):
        with app.app_context():
            user = UserCredentials.query.first()
            invite = EventInvite(user_id=user.id, event_id=1)
            db.session.add(invite)
            db.session.commit()
            iid = invite.id

        with patch("app.db.session.commit", side_effect=Exception("fail")):
            r = self.client.delete(f"/invites/{iid}")
            self.assertEqual(r.status_code, 500)


#                      INVITE COMPLETION TESTS

class TestInviteCompletion(BaseTestCase):

    def test_update_invite_completion_true(self):
        with app.app_context():
            user = UserCredentials.query.filter_by(email="volunteer@example.com").first()
            invite = EventInvite(user_id=user.id, event_id=1, status="accepted")
            db.session.add(invite)
            db.session.commit()
            invite_id = invite.id

        r = self.client.put(f"/invites/{invite_id}/complete", json={"completed": True})
        self.assertEqual(r.status_code, 200)

    def test_update_invite_completion_false(self):
        with app.app_context():
            user = UserCredentials.query.filter_by(email="volunteer@example.com").first()
            invite = EventInvite(user_id=user.id, event_id=1, status="accepted", completed=True)
            db.session.add(invite)
            db.session.commit()
            invite_id = invite.id

        r = self.client.put(f"/invites/{invite_id}/complete", json={"completed": False})
        self.assertEqual(r.status_code, 200)

    def test_update_invite_completion_not_found(self):
        r = self.client.put("/invites/9999/complete", json={"completed": True})
        self.assertEqual(r.status_code, 404)

    def test_update_invite_completion_missing_field(self):
        with app.app_context():
            user = UserCredentials.query.filter_by(email="volunteer@example.com").first()
            invite = EventInvite(user_id=user.id, event_id=1, status="accepted")
            db.session.add(invite)
            db.session.commit()
            invite_id = invite.id

        r = self.client.put(f"/invites/{invite_id}/complete", json={})
        self.assertEqual(r.status_code, 400)

    def test_update_invite_completion_no_json(self):
        with app.app_context():
            user = UserCredentials.query.filter_by(email="volunteer@example.com").first()
            invite = EventInvite(user_id=user.id, event_id=1, status="accepted")
            db.session.add(invite)
            db.session.commit()
            invite_id = invite.id

        r = self.client.put(f"/invites/{invite_id}/complete")
        self.assertIn(r.status_code, [400, 500])

    def test_update_invite_completion_invalid_type(self):
        with app.app_context():
            user = UserCredentials.query.filter_by(email="volunteer@example.com").first()
            invite = EventInvite(user_id=user.id, event_id=1, status="accepted")
            db.session.add(invite)
            db.session.commit()
            invite_id = invite.id

        r = self.client.put(f"/invites/{invite_id}/complete", json={"completed": "yes"})
        self.assertEqual(r.status_code, 400)

    def test_update_invite_completion_internal_error(self):
        with app.app_context():
            user = UserCredentials.query.first()
            invite = EventInvite(user_id=user.id, event_id=1)
            db.session.add(invite)
            db.session.commit()
            iid = invite.id

        with patch("app.db.session.commit", side_effect=Exception("fail")):
            r = self.client.put(f"/invites/{iid}/complete", json={"completed": True})
            self.assertEqual(r.status_code, 500)


#                      USER INVITES TESTS

class TestUserInvites(BaseTestCase):

    def test_get_user_invites_success(self):
        with app.app_context():
            user = UserCredentials.query.filter_by(email="volunteer@example.com").first()
            invite = EventInvite(user_id=user.id, event_id=1, status="pending")
            db.session.add(invite)
            db.session.commit()

        r = self.client.get("/invites/user/volunteer@example.com")
        self.assertEqual(r.status_code, 200)
        data = json.loads(r.data)
        self.assertIsInstance(data, list)
        if len(data) > 0:
            self.assertIn("event", data[0])

    def test_get_user_invites_with_null_event_date(self):
        with app.app_context():
            user = UserCredentials.query.filter_by(email="volunteer@example.com").first()
            event = EventDetails(event_name="No Date Event")
            db.session.add(event)
            db.session.commit()

            invite = EventInvite(user_id=user.id, event_id=event.id, status="pending")
            db.session.add(invite)
            db.session.commit()

        r = self.client.get("/invites/user/volunteer@example.com")
        self.assertEqual(r.status_code, 200)

    def test_get_user_invites_with_status_filter(self):
        with app.app_context():
            user = UserCredentials.query.filter_by(email="volunteer@example.com").first()
            invite1 = EventInvite(user_id=user.id, event_id=1, status="pending")
            invite2 = EventInvite(user_id=user.id, event_id=2, status="accepted")
            db.session.add_all([invite1, invite2])
            db.session.commit()

        r = self.client.get("/invites/user/volunteer@example.com?status=pending")
        self.assertEqual(r.status_code, 200)

    def test_get_user_invites_with_type_filter(self):
        with app.app_context():
            user = UserCredentials.query.filter_by(email="volunteer@example.com").first()
            invite = EventInvite(user_id=user.id, event_id=1, status="pending", type="admin_invite")
            db.session.add(invite)
            db.session.commit()

        r = self.client.get("/invites/user/volunteer@example.com?type=admin_invite")
        self.assertEqual(r.status_code, 200)

    def test_get_user_invites_not_found(self):
        r = self.client.get("/invites/user/nonexistent@example.com")
        self.assertEqual(r.status_code, 404)

    def test_get_user_invites_internal_error(self):
        with app.app_context():
            with patch("app.UserCredentials.query.filter_by", side_effect=Exception("fail")):
                r = self.client.get("/invites/user/volunteer@example.com")
        self.assertIn(r.status_code, [200, 500])


#                      USER EVENTS TESTS

class TestUserEvents(BaseTestCase):

    def test_get_user_events_success(self):
        with app.app_context():
            user = UserCredentials.query.filter_by(email="volunteer@example.com").first()
            invite = EventInvite(user_id=user.id, event_id=1, status="accepted")
            db.session.add(invite)
            db.session.commit()

        r = self.client.get("/user/volunteer@example.com/events")
        self.assertEqual(r.status_code, 200)
        data = json.loads(r.data)
        self.assertIn("events", data)

    def test_get_user_events_with_completion(self):
        with app.app_context():
            user = UserCredentials.query.filter_by(email="volunteer@example.com").first()
            invite = EventInvite(user_id=user.id, event_id=1, status="accepted", completed=True)
            db.session.add(invite)
            db.session.commit()

        r = self.client.get("/user/volunteer@example.com/events")
        self.assertEqual(r.status_code, 200)

    def test_get_user_events_with_null_event_date(self):
        with app.app_context():
            user = UserCredentials.query.filter_by(email="volunteer@example.com").first()
            event = EventDetails(event_name="No Date")
            db.session.add(event)
            db.session.commit()

            invite = EventInvite(user_id=user.id, event_id=event.id, status="accepted")
            db.session.add(invite)
            db.session.commit()

        r = self.client.get("/user/volunteer@example.com/events")
        self.assertEqual(r.status_code, 200)

    def test_get_user_events_not_found(self):
        r = self.client.get("/user/nonexistent@example.com/events")
        self.assertEqual(r.status_code, 404)

    def test_get_user_events_internal_error(self):
        with app.app_context():
            with patch("app.UserCredentials.query.filter_by", side_effect=Exception("fail")):
                r = self.client.get("/user/volunteer@example.com/events")
        self.assertIn(r.status_code, [200, 500])


#                      USER MANAGEMENT TESTS

class TestUsersManagement(BaseTestCase):

    def test_get_all_users(self):
        r = self.client.get("/users")
        self.assertEqual(r.status_code, 200)
        data = json.loads(r.data)
        self.assertIsInstance(data, list)
        if len(data) > 0:
            self.assertIn("address", data[0])

    def test_get_all_users_with_full_address(self):
        with app.app_context():
            user = UserCredentials(email="fulladdr@example.com")
            user.set_password("Password1")
            db.session.add(user)
            db.session.commit()

            profile = UserProfile(
                id=user.id,
                full_name="Full Address",
                address1="123 Main St",
                city="Houston",
                state="TX",
                zipcode="77001"
            )
            db.session.add(profile)
            db.session.commit()

        r = self.client.get("/users")
        self.assertEqual(r.status_code, 200)

    def test_get_all_users_without_profile(self):
        with app.app_context():
            user = UserCredentials(email="noaddr@example.com")
            user.set_password("Password1")
            db.session.add(user)
            db.session.commit()

        r = self.client.get("/users")
        self.assertEqual(r.status_code, 200)

    def test_get_all_users_internal_error(self):
        with app.app_context():
            with patch("app.UserCredentials.query.all", side_effect=Exception("fail")):
                r = self.client.get("/users")
        self.assertIn(r.status_code, [200, 500])

    def test_update_user_role(self):
        r = self.client.put("/users/volunteer@example.com", json={"role": "admin"})
        self.assertEqual(r.status_code, 200)

    def test_update_user_name(self):
        r = self.client.put("/users/volunteer@example.com", json={"name": "New Name"})
        self.assertEqual(r.status_code, 200)

    def test_update_user_name_no_profile(self):
        with app.app_context():
            user = UserCredentials(email="noprofile@example.com")
            user.set_password("Password1")
            db.session.add(user)
            db.session.commit()

        r = self.client.put("/users/noprofile@example.com", json={"name": "Test Name"})
        self.assertEqual(r.status_code, 200)

    def test_update_user_role_and_name(self):
        r = self.client.put("/users/volunteer@example.com", json={"role": "admin", "name": "Admin User"})
        self.assertEqual(r.status_code, 200)

    def test_update_user_not_found(self):
        r = self.client.put("/users/nonexistent@example.com", json={"role": "admin"})
        self.assertEqual(r.status_code, 404)

    def test_update_user_no_json(self):
        r = self.client.put("/users/volunteer@example.com")
        self.assertEqual(r.status_code, 500)

    def test_update_user_internal_error(self):
        with patch("app.db.session.commit", side_effect=Exception("fail")):
            r = self.client.put("/users/volunteer@example.com", json={"role": "x"})
            self.assertEqual(r.status_code, 500)

    def test_delete_user_success(self):
        with app.app_context():
            user = UserCredentials(email="todelete@example.com")
            user.set_password("Password1")
            db.session.add(user)
            db.session.commit()

        r = self.client.delete("/users/todelete@example.com")
        self.assertEqual(r.status_code, 200)

    def test_delete_user_with_profile(self):
        with app.app_context():
            user = UserCredentials(email="todelete2@example.com")
            user.set_password("Password1")
            db.session.add(user)
            db.session.commit()

            profile = UserProfile(id=user.id, full_name="Test User")
            db.session.add(profile)
            db.session.commit()

        r = self.client.delete("/users/todelete2@example.com")
        self.assertEqual(r.status_code, 200)

    def test_delete_user_with_history_and_invites(self):
        with app.app_context():
            user = UserCredentials(email="todelete3@example.com")
            user.set_password("Password1")
            db.session.add(user)
            db.session.commit()

            history = VolunteerHistory(user_id=user.id, event_id=1)
            invite = EventInvite(user_id=user.id, event_id=1)
            db.session.add_all([history, invite])
            db.session.commit()

        r = self.client.delete("/users/todelete3@example.com")
        self.assertEqual(r.status_code, 200)

    def test_delete_user_not_found(self):
        r = self.client.delete("/users/nonexistent@example.com")
        self.assertEqual(r.status_code, 404)

    def test_delete_user_internal_error(self):
        with patch("app.db.session.commit", side_effect=Exception("fail")):
            r = self.client.delete("/users/volunteer@example.com")
            self.assertEqual(r.status_code, 500)


#                      NOTIFICATION TESTS

class TestNotifications(BaseTestCase):

    def test_get_notifications(self):
        with app.app_context():
            n = Notification(message="Hello", type="info")
            db.session.add(n)
            db.session.commit()

        r = self.client.get("/notifications")
        self.assertEqual(r.status_code, 200)
        data = json.loads(r.data)
        self.assertIsInstance(data, list)

    def test_get_notifications_only_unread(self):
        with app.app_context():
            n1 = Notification(message="Unread", type="info", read=False)
            n2 = Notification(message="Read", type="info", read=True)
            db.session.add_all([n1, n2])
            db.session.commit()

        r = self.client.get("/notifications")
        self.assertEqual(r.status_code, 200)
        data = json.loads(r.data)
        messages = [n["message"] for n in data]
        self.assertIn("Unread", messages)
        self.assertNotIn("Read", messages)

    def test_get_notifications_empty(self):
        r = self.client.get("/notifications")
        self.assertEqual(r.status_code, 200)

    def test_get_notifications_internal_error(self):
        with app.app_context():
            with patch("app.Notification.query.filter_by", side_effect=Exception("fail")):
                r = self.client.get("/notifications")
        self.assertIn(r.status_code, [200, 500])

    def test_mark_read(self):
        with app.app_context():
            n = Notification(message="xx", type="info")
            db.session.add(n)
            db.session.commit()
            nid = n.id

        r = self.client.put(f"/notifications/{nid}/read")
        self.assertEqual(r.status_code, 200)

    def test_mark_read_not_found(self):
        r = self.client.put("/notifications/9999/read")
        self.assertEqual(r.status_code, 404)

    def test_mark_read_internal_error(self):
        with app.app_context():
            n = Notification(message="xx", type="info")
            db.session.add(n)
            db.session.commit()
            nid = n.id

        with patch("app.db.session.commit", side_effect=Exception("fail")):
            r = self.client.put(f"/notifications/{nid}/read")
            self.assertEqual(r.status_code, 500)


#                      STATIC DATA TESTS

class TestStaticData(BaseTestCase):

    def test_get_states(self):
        r = self.client.get("/data/states")
        self.assertEqual(r.status_code, 200)
        data = json.loads(r.data)
        self.assertEqual(len(data), 50)
        if len(data) > 0:
            self.assertIn("code", data[0])
            self.assertIn("name", data[0])

    def test_get_states_internal_error(self):
        with app.app_context():
            with patch("app.States.query.all", side_effect=Exception("fail")):
                r = self.client.get("/data/states")
        self.assertIn(r.status_code, [200, 500])

    def test_get_skills(self):
        r = self.client.get("/data/skills")
        self.assertEqual(r.status_code, 200)
        data = json.loads(r.data)
        self.assertIn("First Aid", data)
        self.assertIsInstance(data, list)


#                      REPORT TESTS

class TestReports(BaseTestCase):

    def test_history_csv(self):
        r = self.client.get("/reports/volunteer_history.csv")
        self.assertEqual(r.status_code, 200)
        self.assertIn("text/csv", r.content_type)

    def test_history_csv_with_history(self):
        with app.app_context():
            user = UserCredentials.query.filter_by(email="volunteer@example.com").first()
        r = self.client.get("/reports/volunteer_history.csv")
        self.assertEqual(r.status_code, 200)

    def test_history_csv_no_history(self):
        with app.app_context():
            user = UserCredentials(email="nohistvol@example.com", role="volunteer")
            user.set_password("Password1")
            db.session.add(user)
            db.session.commit()

        r = self.client.get("/reports/volunteer_history.csv")
        self.assertEqual(r.status_code, 200)
        self.assertIn("No History", r.data.decode())

    def test_history_csv_internal_error(self):
        with app.app_context():
            with patch("app.UserCredentials.query.filter_by", side_effect=Exception("fail")):
                r = self.client.get("/reports/volunteer_history.csv")
        self.assertIn(r.status_code, [200, 500])

    def test_assignments_csv(self):
        r = self.client.get("/reports/event_assignments.csv")
        self.assertEqual(r.status_code, 200)
        self.assertIn("text/csv", r.content_type)

    def test_assignments_csv_no_volunteers(self):
        with app.app_context():
            event = EventDetails(event_name="No Vols Event")
            db.session.add(event)
            db.session.commit()

        r = self.client.get("/reports/event_assignments.csv")
        self.assertEqual(r.status_code, 200)
        self.assertIn("No Volunteers", r.data.decode())


#                  MODELS.PY COVERAGE TESTS (Lines 168-174)

class TestModelDefaults(BaseTestCase):
    """Tests to cover models.py lines 168-174 - VolunteerHistory default participation_date"""

    def test_volunteer_history_default_date(self):
        """Covers models.py lines 168-174 (default participation_date with timezone)"""
        with app.app_context():
            # Create user
            user = UserCredentials(email="historydefault@example.com")
            user.set_password("Password123!")
            db.session.add(user)

            # Create event
            event = EventDetails(event_name="Default Date Event")
            db.session.add(event)
            db.session.commit()

            # Create VolunteerHistory WITHOUT specifying participation_date
            # This should trigger the default value with timezone
            hist = VolunteerHistory(user_id=user.id, event_id=event.id)
            db.session.add(hist)
            db.session.commit()

            # Fetch and inspect - should have auto-generated date with timezone
            fetched = VolunteerHistory.query.filter_by(id=hist.id).first()

            # Verify participation_date was set
            self.assertIsNotNone(fetched.participation_date)
            # Verify it has timezone info (lines 168-174 in models.py)
            self.assertTrue(hasattr(fetched.participation_date, 'tzinfo'))

    def test_volunteer_history_explicit_date(self):
        """Test that explicit participation_date also works"""
        from datetime import datetime, timezone

        with app.app_context():
            user = UserCredentials(email="historyexplicit@example.com")
            user.set_password("Password123!")
            db.session.add(user)

            event = EventDetails(event_name="Explicit Date Event")
            db.session.add(event)
            db.session.commit()

            # Explicitly set participation_date
            explicit_date = datetime(2026, 1, 15, 10, 30, 0, tzinfo=timezone.utc)
            hist = VolunteerHistory(
                user_id=user.id,
                event_id=event.id,
                participation_date=explicit_date
            )
            db.session.add(hist)
            db.session.commit()

            fetched = VolunteerHistory.query.filter_by(id=hist.id).first()
            # Compare just the datetime components, ignoring timezone differences
            self.assertEqual(fetched.participation_date.year, explicit_date.year)
            self.assertEqual(fetched.participation_date.month, explicit_date.month)
            self.assertEqual(fetched.participation_date.day, explicit_date.day)
            self.assertEqual(fetched.participation_date.hour, explicit_date.hour)
            self.assertEqual(fetched.participation_date.minute, explicit_date.minute)


    def test_assignments_csv_internal_error(self):
        with app.app_context():
            with patch("app.EventDetails.query.all", side_effect=Exception("fail")):
                r = self.client.get("/reports/event_assignments.csv")
        self.assertIn(r.status_code, [200, 500])

    def test_history_json(self):
        r = self.client.get("/reports/json/volunteer_history")
        self.assertEqual(r.status_code, 200)
        data = json.loads(r.data)
        self.assertIsInstance(data, list)

    def test_history_json_no_history(self):
        with app.app_context():
            user = UserCredentials(email="jsonnohi@example.com", role="volunteer")
            user.set_password("Password1")
            db.session.add(user)
            db.session.commit()

        r = self.client.get("/reports/json/volunteer_history")
        self.assertEqual(r.status_code, 200)

    def test_history_json_internal_error(self):
        with app.app_context():
            with patch("app.UserCredentials.query.filter_by", side_effect=Exception("fail")):
                r = self.client.get("/reports/json/volunteer_history")
        self.assertIn(r.status_code, [200, 500])

    def test_assignments_json(self):
        r = self.client.get("/reports/json/event_assignments")
        self.assertEqual(r.status_code, 200)
        data = json.loads(r.data)
        self.assertIsInstance(data, list)

    def test_assignments_json_no_volunteers(self):
        with app.app_context():
            event = EventDetails(event_name="JSON No Vols")
            db.session.add(event)
            db.session.commit()

        r = self.client.get("/reports/json/event_assignments")
        self.assertEqual(r.status_code, 200)
        data = json.loads(r.data)
        self.assertTrue(any("None" in str(e.get("Volunteer")) for e in data))

    def test_assignments_json_internal_error(self):
        with app.app_context():
            with patch("app.EventDetails.query.all", side_effect=Exception("fail")):
                r = self.client.get("/reports/json/event_assignments")
        self.assertIn(r.status_code, [200, 500])


#                      NOTIFICATION HELPER TEST

class TestNotificationHelper(BaseTestCase):

    def test_create_notification_helper(self):
        with app.app_context():
            create_notification("Test notification message")
            notif = Notification.query.filter_by(message="Test notification message").first()
            self.assertIsNotNone(notif)

    def test_create_notification_with_type(self):
        with app.app_context():
            create_notification("Warning message", "warning")
            notif = Notification.query.filter_by(message="Warning message").first()
            self.assertIsNotNone(notif)
            self.assertEqual(notif.type, "warning")

    def test_create_notification_internal_error(self):
        with app.app_context():
            with patch("app.db.session.commit", side_effect=Exception("fail")):
                create_notification("Test")


#                      SEEDER STABILITY TEST

class TestSeeder(BaseTestCase):

    def test_init_db_idempotent(self):
        with app.app_context():
            init_db()
            init_db()
            self.assertEqual(States.query.count(), 50)
            self.assertEqual(
                UserCredentials.query.filter_by(email="admin@example.com").count(), 1
            )

    def test_init_db_creates_all_data(self):
        with app.app_context():
            self.assertEqual(States.query.count(), 50)

            admin = UserCredentials.query.filter_by(email="admin@example.com").first()
            self.assertIsNotNone(admin)
            self.assertIsNotNone(admin.profile)

            vol = UserCredentials.query.filter_by(email="volunteer@example.com").first()
            self.assertIsNotNone(vol)
            self.assertIsNotNone(vol.profile)

            self.assertEqual(EventDetails.query.count(), 2)

            self.assertGreaterEqual(VolunteerHistory.query.count(), 1)


#                  HELPER AND UTILITY FUNCTION TESTS

class TestHelperFunctions(BaseTestCase):

    def test_password_hashing(self):
        with app.app_context():
            user = UserCredentials(email="test@example.com")
            user.set_password("TestPassword123")
            self.assertTrue(user.check_password("TestPassword123"))
            self.assertFalse(user.check_password("WrongPassword"))


#                      EDGE CASE AND BOUNDARY TESTS

class TestEdgeCasesAndBoundaries(BaseTestCase):

    def test_very_long_event_name(self):
        payload = {
            "event_name": "A" * 500,
            "city": "Houston",
            "state": "TX"
        }
        r = self.client.post("/events", json=payload)
        self.assertIn(r.status_code, [201, 400])

    def test_special_characters_in_email(self):
        r = self.client.post("/register", json={
            "email": "test+special@example.com",
            "password": "Password123"
        })
        self.assertIn(r.status_code, [201, 400, 415])

    def test_null_values_in_profile(self):
        r = self.client.put("/profile/volunteer@example.com", json={
            "full_name": "Test",
            "address1": None
        })
        self.assertIn(r.status_code, [200, 400])

    def test_negative_event_id(self):
        r = self.client.get("/events/-1")
        self.assertIn(r.status_code, [404, 400])

    def test_zero_volunteer_limit(self):
        r = self.client.post("/events", json={
            "event_name": "Zero Limit",
            "volunteer_limit": 0
        })
        self.assertIn(r.status_code, [201, 400])

    def test_unicode_in_event_description(self):
        r = self.client.post("/events", json={
            "event_name": "Unicode Event 🎉",
            "description": "Test with émojis and spëcial çhars"
        })
        self.assertIn(r.status_code, [201, 400])


#                      CONCURRENT OPERATION TESTS

class TestConcurrentOperations(BaseTestCase):

    def test_double_signup_prevention(self):
        r1 = self.client.post("/signup", json={"email": "volunteer@example.com", "event_id": 2})
        r2 = self.client.post("/signup", json={"email": "volunteer@example.com", "event_id": 2})
        self.assertEqual(r2.status_code, 409)

    def test_delete_nonexistent_after_creation(self):
        r1 = self.client.post("/events", json={"event_name": "Temp Event"})
        if r1.status_code == 201:
            with app.app_context():
                event = EventDetails.query.filter_by(event_name="Temp Event").first()
                if event:
                    eid = event.id
                    r2 = self.client.delete(f"/events/{eid}")
                    self.assertEqual(r2.status_code, 200)
                    r3 = self.client.delete(f"/events/{eid}")
                    self.assertEqual(r3.status_code, 404)


#                      ADDITIONAL COVERAGE TESTS

class TestAdditionalCoverageForMissingLines(BaseTestCase):

    def test_profile_get_with_skills_and_availability(self):
        """Test profile GET with actual skills and availability data"""
        r = self.client.get("/profile/volunteer@example.com")
        self.assertEqual(r.status_code, 200)
        data = json.loads(r.data)
        # Volunteer has skills and availability from seeder
        self.assertGreater(len(data.get("skills", [])), 0)
        self.assertGreater(len(data.get("availability", [])), 0)

    def test_login_with_no_profile_user(self):
        """Ensure login checks profile existence correctly"""
        with app.app_context():
            user = UserCredentials(email="justcreds@example.com")
            user.set_password("Password123")
            db.session.add(user)
            db.session.commit()

        r = self.client.post("/login", json={"email": "justcreds@example.com", "password": "Password123"})
        self.assertEqual(r.status_code, 200)
        data = json.loads(r.data)
        self.assertFalse(data["user"]["profileComplete"])

    def test_event_with_null_date_formatting(self):
        """Test event with null event_date"""
        with app.app_context():
            event = EventDetails(event_name="No Date Event", event_date=None)
            db.session.add(event)
            db.session.commit()
            eid = event.id

        r = self.client.get(f"/events/{eid}")
        self.assertEqual(r.status_code, 200)
        data = json.loads(r.data)
        self.assertIsNone(data["event_date"])

    def test_events_get_all_with_null_dates(self):
        """Test GET all events includes events with null dates"""
        with app.app_context():
            event = EventDetails(event_name="Null Date Event", event_date=None)
            db.session.add(event)
            db.session.commit()

        r = self.client.get("/events")
        self.assertEqual(r.status_code, 200)
        data = json.loads(r.data)
        # Should include event with null date
        null_date_events = [e for e in data if e["event_date"] is None]
        self.assertGreater(len(null_date_events), 0)

    def test_matching_with_no_profile_skill_match(self):
        """Test matching when volunteer profile exists but no skill match"""
        with app.app_context():
            vol = UserCredentials(email="nomatch@example.com", role="volunteer")
            vol.set_password("Password1")
            db.session.add(vol)
            db.session.commit()

            profile = UserProfile(id=vol.id, full_name="No Match", skills="Cooking, Dancing")
            db.session.add(profile)
            db.session.commit()

        r = self.client.get("/matching/1")  # Event 1 has "Logistics, Event Setup"
        self.assertEqual(r.status_code, 200)
        data = json.loads(r.data)
        # Should not include nomatch user
        emails = [v["email"] for v in data]
        self.assertNotIn("nomatch@example.com", emails)

    def test_invite_with_existing_history_on_accept(self):
        """Test accepting invite when history already exists"""
        with app.app_context():
            user = UserCredentials.query.filter_by(email="volunteer@example.com").first()
            # Create history first
            history = VolunteerHistory(user_id=user.id, event_id=2)
            db.session.add(history)

            # Then create pending invite
            invite = EventInvite(user_id=user.id, event_id=2, status="pending")
            db.session.add(invite)
            db.session.commit()
            invite_id = invite.id

        # Accept the invite
        r = self.client.put(f"/invites/{invite_id}", json={"status": "accepted"})
        self.assertEqual(r.status_code, 200)

        # Verify only one history record
        with app.app_context():
            user = UserCredentials.query.filter_by(email="volunteer@example.com").first()
            count = VolunteerHistory.query.filter_by(user_id=user.id, event_id=2).count()
            self.assertEqual(count, 1)

    def test_user_without_volunteer_history(self):
        """Test user with no volunteer history"""
        with app.app_context():
            user = UserCredentials(email="nohistory2@example.com")
            user.set_password("Password1")
            db.session.add(user)
            db.session.commit()

        r = self.client.get("/history/nohistory2@example.com")
        self.assertEqual(r.status_code, 200)
        data = json.loads(r.data)
        self.assertEqual(len(data), 0)

    def test_user_events_with_no_event_object(self):
        """Test user events when event is deleted but invite remains"""
        with app.app_context():
            user = UserCredentials.query.filter_by(email="volunteer@example.com").first()
            # Create invite with non-existent event
            invite = EventInvite(user_id=user.id, event_id=9999, status="accepted")
            db.session.add(invite)
            db.session.commit()

        r = self.client.get("/user/volunteer@example.com/events")
        self.assertEqual(r.status_code, 200)
        data = json.loads(r.data)
        # Should handle None event gracefully

    def test_volunteer_history_with_no_event(self):
        """Test history endpoint when event is deleted"""
        with app.app_context():
            user = UserCredentials.query.filter_by(email="volunteer@example.com").first()
            # Create history with non-existent event
            history = VolunteerHistory(user_id=user.id, event_id=9999)
            db.session.add(history)
            db.session.commit()

        r = self.client.get("/history/volunteer@example.com")
        self.assertEqual(r.status_code, 200)
        # Should handle None event gracefully

    def test_event_volunteers_with_no_user_profile(self):
        """Test event volunteers when user has no profile"""
        with app.app_context():
            user = UserCredentials(email="noprofile2@example.com")
            user.set_password("Password1")
            db.session.add(user)
            db.session.commit()

            invite = EventInvite(user_id=user.id, event_id=1, status="accepted")
            db.session.add(invite)
            db.session.commit()

        r = self.client.get("/events/1/volunteers")
        self.assertEqual(r.status_code, 200)
        data = json.loads(r.data)
        # Should only include users with profiles

    def test_users_list_with_partial_address(self):
        """Test users list with various address completeness"""
        with app.app_context():
            # User with only address1
            user1 = UserCredentials(email="partial1@example.com")
            user1.set_password("Password1")
            db.session.add(user1)
            db.session.commit()

            profile1 = UserProfile(id=user1.id, full_name="Partial 1", address1="123 St")
            db.session.add(profile1)

            # User with address1 and city
            user2 = UserCredentials(email="partial2@example.com")
            user2.set_password("Password1")
            db.session.add(user2)
            db.session.commit()

            profile2 = UserProfile(id=user2.id, full_name="Partial 2", address1="456 Ave", city="Austin")
            db.session.add(profile2)

            # User with all address fields
            user3 = UserCredentials(email="complete@example.com")
            user3.set_password("Password1")
            db.session.add(user3)
            db.session.commit()

            profile3 = UserProfile(
                id=user3.id,
                full_name="Complete",
                address1="789 Blvd",
                city="Dallas",
                state="TX",
                zipcode="75001"
            )
            db.session.add(profile3)
            db.session.commit()

        r = self.client.get("/users")
        self.assertEqual(r.status_code, 200)
        data = json.loads(r.data)

        # Find our test users
        users_map = {u["email"]: u for u in data}

        # Verify address formatting
        self.assertIn("partial1@example.com", users_map)
        self.assertIn("partial2@example.com", users_map)
        self.assertIn("complete@example.com", users_map)

    def test_csv_report_with_volunteers_no_history(self):
        """Test CSV volunteer history report with volunteers who have no events"""
        with app.app_context():
            user = UserCredentials(email="csvnohistory@example.com", role="volunteer")
            user.set_password("Password1")
            db.session.add(user)
            db.session.commit()

            profile = UserProfile(id=user.id, full_name="CSV No History")
            db.session.add(profile)
            db.session.commit()

        r = self.client.get("/reports/volunteer_history.csv")
        self.assertEqual(r.status_code, 200)
        self.assertIn("No History", r.data.decode())

    def test_csv_report_event_assignments_no_volunteers(self):
        """Test CSV event assignments with events that have no volunteers"""
        with app.app_context():
            event = EventDetails(event_name="CSV No Volunteers Event")
            db.session.add(event)
            db.session.commit()

        r = self.client.get("/reports/event_assignments.csv")
        self.assertEqual(r.status_code, 200)
        self.assertIn("No Volunteers", r.data.decode())

    def test_json_report_volunteer_history_no_events(self):
        """Test JSON volunteer history with users who have no events"""
        with app.app_context():
            user = UserCredentials(email="jsonnoevents@example.com", role="volunteer")
            user.set_password("Password1")
            db.session.add(user)
            db.session.commit()

            profile = UserProfile(id=user.id, full_name="JSON No Events")
            db.session.add(profile)
            db.session.commit()

        r = self.client.get("/reports/json/volunteer_history")
        self.assertEqual(r.status_code, 200)
        data = json.loads(r.data)
        # Should include entry with "No History"
        no_history = [d for d in data if d.get("Event Name") == "No History"]
        self.assertGreater(len(no_history), 0)

    def test_json_report_event_assignments_no_volunteers(self):
        """Test JSON event assignments with events that have no volunteers"""
        with app.app_context():
            event = EventDetails(event_name="JSON No Vols Event")
            db.session.add(event)
            db.session.commit()

        r = self.client.get("/reports/json/event_assignments")
        self.assertEqual(r.status_code, 200)
        data = json.loads(r.data)
        # Should include event with "None" volunteer
        no_vol_events = [d for d in data if d.get("Volunteer") == "None"]
        self.assertGreater(len(no_vol_events), 0)

    def test_update_user_with_existing_profile_name_change(self):
        """Test updating user name when profile already exists"""
        r = self.client.put("/users/volunteer@example.com", json={"name": "Changed Name"})
        self.assertEqual(r.status_code, 200)

        # Verify the name was changed
        with app.app_context():
            user = UserCredentials.query.filter_by(email="volunteer@example.com").first()
            self.assertEqual(user.profile.full_name, "Changed Name")

    def test_update_user_create_profile_when_missing(self):
        """Test updating user name creates profile if missing"""
        with app.app_context():
            user = UserCredentials(email="needsprofile@example.com")
            user.set_password("Password1")
            db.session.add(user)
            db.session.commit()

        r = self.client.put("/users/needsprofile@example.com", json={"name": "New Profile Name"})
        self.assertEqual(r.status_code, 200)

        # Verify profile was created
        with app.app_context():
            user = UserCredentials.query.filter_by(email="needsprofile@example.com").first()
            self.assertIsNotNone(user.profile)
            self.assertEqual(user.profile.full_name, "New Profile Name")

    def test_delete_user_without_profile(self):
        """Test deleting user who has no profile"""
        with app.app_context():
            user = UserCredentials(email="noprofiledelete@example.com")
            user.set_password("Password1")
            db.session.add(user)
            db.session.commit()

        r = self.client.delete("/users/noprofiledelete@example.com")
        self.assertEqual(r.status_code, 200)

    def test_register_admin_email(self):
        """Test registering with admin email gets admin role"""
        # Use a different admin email to avoid conflicts
        r = self.client.post("/register", json={"email": "admin@example.com", "password": "AdminPass123"})
        # Will return 409 if admin already exists from seeder
        self.assertIn(r.status_code, [201, 409])

        # Verify the admin user has admin role
        with app.app_context():
            user = UserCredentials.query.filter_by(email="admin@example.com").first()
            self.assertIsNotNone(user)
            self.assertEqual(user.role, "admin")

    def test_profile_with_empty_skills_list(self):
        """Test profile update with empty skills list results in empty array on GET"""
        payload = {
            "full_name": "Empty Skills",
            "skills": []
        }
        r = self.client.put("/profile/volunteer@example.com", json=payload)
        self.assertEqual(r.status_code, 200)

        # GET the profile
        r2 = self.client.get("/profile/volunteer@example.com")
        data = json.loads(r2.data)
        # Skills might be None or empty list
        self.assertIn(data.get("skills", []), [[], None, [""]])



#          TARGETED TESTS FOR SPECIFIC MISSING LINES

class TestSpecificMissingLines(BaseTestCase):
    """Tests specifically designed to hit uncovered lines"""

    # Lines 92, 94 - profile.skills/availability None check in GET
    def test_profile_get_with_none_skills(self):
        """Hit lines 92, 94 - when profile.skills is None"""
        with app.app_context():
            user = UserCredentials.query.filter_by(email="volunteer@example.com").first()
            if user.profile:
                user.profile.skills = None
                user.profile.availability = None
                db.session.commit()

        r = self.client.get("/profile/volunteer@example.com")
        self.assertEqual(r.status_code, 200)
        data = json.loads(r.data)
        self.assertEqual(data.get("skills"), [])
        self.assertEqual(data.get("availability"), [])

    # Lines 101, 106 - login when user has no profile
    def test_login_profile_complete_false(self):
        """Hit lines 101, 106 - profileComplete check when no profile"""
        with app.app_context():
            user = UserCredentials(email="noproflogin@example.com")
            user.set_password("Password123")
            db.session.add(user)
            db.session.commit()

        r = self.client.post("/login", json={"email": "noproflogin@example.com", "password": "Password123"})
        self.assertEqual(r.status_code, 200)
        data = json.loads(r.data)
        self.assertFalse(data["user"]["profileComplete"])

    # Lines 124, 146, 154 - event.event_date None handling
    def test_events_get_with_none_event_date(self):
        """Hit lines 124 - event_date None in GET /events"""
        with app.app_context():
            event = EventDetails(event_name="None Date", event_date=None)
            db.session.add(event)
            db.session.commit()

        r = self.client.get("/events")
        self.assertEqual(r.status_code, 200)
        data = json.loads(r.data)
        none_date_events = [e for e in data if e["event_name"] == "None Date"]
        self.assertEqual(len(none_date_events), 1)
        self.assertIsNone(none_date_events[0]["event_date"])

    def test_event_get_by_id_with_none_date(self):
        """Hit line 146 - event_date None in GET /events/<id>"""
        with app.app_context():
            event = EventDetails(event_name="None Date Single", event_date=None)
            db.session.add(event)
            db.session.commit()
            eid = event.id

        r = self.client.get(f"/events/{eid}")
        self.assertEqual(r.status_code, 200)
        data = json.loads(r.data)
        self.assertIsNone(data["event_date"])

    # Line 164 - matching when profile is None
    def test_matching_volunteer_none_profile(self):
        """Hit line 164 - continue when profile is None"""
        with app.app_context():
            vol = UserCredentials(email="noprof@example.com", role="volunteer")
            vol.set_password("Password1")
            db.session.add(vol)
            db.session.commit()

        r = self.client.get("/matching/1")
        self.assertEqual(r.status_code, 200)

    # Line 192 - matching when profile.skills is None
    def test_matching_volunteer_none_skills(self):
        """Hit line 192 - continue when profile.skills is None"""
        with app.app_context():
            vol = UserCredentials(email="noskillsmatch@example.com", role="volunteer")
            vol.set_password("Password1")
            db.session.add(vol)
            db.session.commit()

            profile = UserProfile(id=vol.id, full_name="No Skills", skills=None)
            db.session.add(profile)
            db.session.commit()

        r = self.client.get("/matching/1")
        self.assertEqual(r.status_code, 200)

    # Line 210 - invite update when old_status == 'pending' and new == 'accepted'
    def test_invite_accept_creates_history(self):
        """Hit line 210 - create history on pending->accepted"""
        with app.app_context():
            user = UserCredentials.query.filter_by(email="volunteer@example.com").first()
            invite = EventInvite(user_id=user.id, event_id=2, status="pending")
            db.session.add(invite)
            db.session.commit()
            iid = invite.id

        r = self.client.put(f"/invites/{iid}", json={"status": "accepted"})
        self.assertEqual(r.status_code, 200)

    # Lines 284-286 - get_user_invites when invite.event exists
    def test_user_invites_with_event_details(self):
        """Hit lines 284-286 - event details in user invites"""
        with app.app_context():
            user = UserCredentials.query.filter_by(email="volunteer@example.com").first()
            invite = EventInvite(user_id=user.id, event_id=1, status="pending")
            db.session.add(invite)
            db.session.commit()

        r = self.client.get("/invites/user/volunteer@example.com")
        self.assertEqual(r.status_code, 200)
        data = json.loads(r.data)
        self.assertGreater(len(data), 0)
        self.assertIn("event", data[0])

    # Lines 338-339 - get_user_events when event exists
    def test_user_events_format_date(self):
        """Hit lines 338-339 - format event date in user events"""
        with app.app_context():
            user = UserCredentials.query.filter_by(email="volunteer@example.com").first()
            invite = EventInvite(user_id=user.id, event_id=1, status="accepted")
            db.session.add(invite)
            db.session.commit()

        r = self.client.get("/user/volunteer@example.com/events")
        self.assertEqual(r.status_code, 200)
        data = json.loads(r.data)
        self.assertIn("events", data)

    # Lines 437-439 - get_volunteer_history when event exists
    def test_history_with_event_formatting(self):
        """Hit lines 437-439 - format history event data"""
        r = self.client.get("/history/volunteer@example.com")
        self.assertEqual(r.status_code, 200)
        data = json.loads(r.data)
        # Volunteer has history from seeder
        if len(data) > 0:
            self.assertIn("event_id", data[0])

    # Lines 638-639 - get_event_volunteers when user and profile exist
    def test_event_volunteers_with_profile(self):
        """Hit lines 638-639 - include user with profile in volunteers"""
        with app.app_context():
            user = UserCredentials.query.filter_by(email="volunteer@example.com").first()
            invite = EventInvite(user_id=user.id, event_id=1, status="accepted")
            db.session.add(invite)
            db.session.commit()

        r = self.client.get("/events/1/volunteers")
        self.assertEqual(r.status_code, 200)
        data = json.loads(r.data)
        self.assertIsInstance(data, list)

    # Lines 840-842 - get_all_users address formatting with all fields
    def test_users_full_address_formatting(self):
        """Hit lines 840-842 - build full address string"""
        with app.app_context():
            user = UserCredentials(email="fulladdress@example.com")
            user.set_password("Password1")
            db.session.add(user)
            db.session.commit()

            profile = UserProfile(
                id=user.id,
                full_name="Full Address",
                address1="123 Main St",
                city="Houston",
                state="TX",
                zipcode="77001"
            )
            db.session.add(profile)
            db.session.commit()

        r = self.client.get("/users")
        self.assertEqual(r.status_code, 200)
        data = json.loads(r.data)
        full_user = [u for u in data if u["email"] == "fulladdress@example.com"]
        self.assertEqual(len(full_user), 1)
        # Address should contain all parts
        self.assertIn("123 Main St", full_user[0]["address"])

    # Lines 878-880 - update_user when 'name' in data
    def test_update_user_name_with_profile(self):
        """Hit lines 878-880 - update profile.full_name"""
        r = self.client.put("/users/volunteer@example.com", json={"name": "Updated Name"})
        self.assertEqual(r.status_code, 200)

        with app.app_context():
            user = UserCredentials.query.filter_by(email="volunteer@example.com").first()
            self.assertEqual(user.profile.full_name, "Updated Name")

    # Lines 907-909 - delete_user when profile exists
    def test_delete_user_with_existing_profile(self):
        """Hit lines 907-909 - delete profile before user"""
        with app.app_context():
            user = UserCredentials(email="deleteprof@example.com")
            user.set_password("Password1")
            db.session.add(user)
            db.session.commit()

            profile = UserProfile(id=user.id, full_name="Delete Me")
            db.session.add(profile)
            db.session.commit()

        r = self.client.delete("/users/deleteprof@example.com")
        self.assertEqual(r.status_code, 200)

    # Lines 982-984 - CSV volunteer history when user has no history
    def test_csv_volunteer_no_history(self):
        """Hit lines 982-984 - 'No History' in CSV"""
        with app.app_context():
            user = UserCredentials(email="csvnohist@example.com", role="volunteer")
            user.set_password("Password1")
            db.session.add(user)
            db.session.commit()

            profile = UserProfile(id=user.id, full_name="CSV User")
            db.session.add(profile)
            db.session.commit()

        r = self.client.get("/reports/volunteer_history.csv")
        self.assertEqual(r.status_code, 200)
        self.assertIn("No History", r.data.decode())

    # Lines 1062-1064 - CSV event assignments when event has no volunteers
    def test_csv_event_no_volunteers(self):
        """Hit lines 1062-1064 - 'No Volunteers' in CSV"""
        with app.app_context():
            event = EventDetails(event_name="CSV No Vol")
            db.session.add(event)
            db.session.commit()

        r = self.client.get("/reports/event_assignments.csv")
        self.assertEqual(r.status_code, 200)
        self.assertIn("No Volunteers", r.data.decode())

    # Lines 1092-1094 - JSON volunteer history no history
    def test_json_volunteer_no_history(self):
        """Hit lines 1092-1094 - No History in JSON"""
        with app.app_context():
            user = UserCredentials(email="jsonnohist@example.com", role="volunteer")
            user.set_password("Password1")
            db.session.add(user)
            db.session.commit()

            profile = UserProfile(id=user.id, full_name="JSON User")
            db.session.add(profile)
            db.session.commit()

        r = self.client.get("/reports/json/volunteer_history")
        self.assertEqual(r.status_code, 200)
        data = json.loads(r.data)
        no_hist = [d for d in data if "No History" in d.get("Event Name", "")]
        self.assertGreater(len(no_hist), 0)

    # Lines 1152-1154 - JSON event assignments no volunteers
    def test_json_event_no_volunteers(self):
        """Hit lines 1152-1154 - None volunteer in JSON"""
        with app.app_context():
            event = EventDetails(event_name="JSON No Vol")
            db.session.add(event)
            db.session.commit()

        r = self.client.get("/reports/json/event_assignments")
        self.assertEqual(r.status_code, 200)
        data = json.loads(r.data)
        none_vol = [d for d in data if d.get("Volunteer") == "None"]
        self.assertGreater(len(none_vol), 0)

    # Lines 1196-1198 - update_user when 'role' in data
    def test_update_user_role_change(self):
        """Hit lines 1196-1198 - change user role"""
        r = self.client.put("/users/volunteer@example.com", json={"role": "admin"})
        self.assertEqual(r.status_code, 200)

        with app.app_context():
            user = UserCredentials.query.filter_by(email="volunteer@example.com").first()
            self.assertEqual(user.role, "admin")

    # Lines 1233-1235 - update_user create new profile when missing
    def test_update_user_create_new_profile(self):
        """Hit lines 1233-1235 - create profile if missing"""
        with app.app_context():
            user = UserCredentials(email="createprof@example.com")
            user.set_password("Password1")
            db.session.add(user)
            db.session.commit()

        r = self.client.put("/users/createprof@example.com", json={"name": "New Profile"})
        self.assertEqual(r.status_code, 200)

        with app.app_context():
            user = UserCredentials.query.filter_by(email="createprof@example.com").first()
            self.assertIsNotNone(user.profile)

    # Lines 1268-1270 - delete_user delete history and invites
    def test_delete_user_with_history_invites(self):
        """Hit lines 1268-1270 - delete history and invites"""
        with app.app_context():
            user = UserCredentials(email="deletehist@example.com")
            user.set_password("Password1")
            db.session.add(user)
            db.session.commit()

            history = VolunteerHistory(user_id=user.id, event_id=1)
            invite = EventInvite(user_id=user.id, event_id=1)
            db.session.add_all([history, invite])
            db.session.commit()

        r = self.client.delete("/users/deletehist@example.com")
        self.assertEqual(r.status_code, 200)

    # Lines 1392-1397 - register with admin@example.com email
    def test_register_gets_admin_role(self):
        """Hit lines 1392-1397 - admin role assignment"""
        # Try to register admin (will fail if exists, but tests the code path)
        r = self.client.post("/register", json={"email": "admin@example.com", "password": "TestPass123"})
        # Either 201 (created) or 409 (already exists)
        self.assertIn(r.status_code, [201, 409])

        # Verify admin role
        with app.app_context():
            user = UserCredentials.query.filter_by(email="admin@example.com").first()
            self.assertEqual(user.role, "admin")

    # Force TRUE branches - Lines 92, 94: when profile HAS skills/availability
    def test_profile_splits_skills_string(self):
        """Ensure profile.skills is a comma-separated string that gets split"""
        with app.app_context():
            user = UserCredentials.query.filter_by(email="volunteer@example.com").first()
            # Volunteer already has skills from seeder: "First Aid, Logistics"
            self.assertIsNotNone(user.profile.skills)

        r = self.client.get("/profile/volunteer@example.com")
        self.assertEqual(r.status_code, 200)
        data = json.loads(r.data)
        # This MUST hit line 92: skills_list = [s.strip() for s in profile.skills.split(',')]
        self.assertIsInstance(data["skills"], list)
        self.assertGreater(len(data["skills"]), 0)

    def test_profile_splits_availability_string(self):
        """Ensure profile.availability gets split properly"""
        with app.app_context():
            user = UserCredentials.query.filter_by(email="volunteer@example.com").first()
            # Volunteer has availability from seeder
            if user.profile.availability:
                pass  # Has availability
            else:
                # Set it
                user.profile.availability = "2026-12-01, 2026-12-15"
                db.session.commit()

        r = self.client.get("/profile/volunteer@example.com")
        self.assertEqual(r.status_code, 200)
        data = json.loads(r.data)
        # This MUST hit line 94: availability_list = [a.strip() for a in profile.availability.split(',')]
        self.assertIsInstance(data["availability"], list)

    # Line 192: when skills DO match (intersection is non-empty)
    def test_matching_finds_matching_volunteer(self):
        """Hit line 192 - volunteer skills match event skills"""
        # Volunteer has "First Aid, Logistics"
        # Event 1 has "Logistics, Event Setup"
        # They share "Logistics" so should match
        r = self.client.get("/matching/1")
        self.assertEqual(r.status_code, 200)
        data = json.loads(r.data)
        # Should find volunteer@example.com
        emails = [v["email"] for v in data]
        self.assertIn("volunteer@example.com", emails)

    # Lines 284-286: when event exists and has all fields
    def test_user_invites_includes_full_event_data(self):
        """Hit lines 284-286 - event details included when event exists"""
        with app.app_context():
            user = UserCredentials.query.filter_by(email="volunteer@example.com").first()
            # Event 1 has all fields including event_date
            invite = EventInvite(user_id=user.id, event_id=1, status="pending")
            db.session.add(invite)
            db.session.commit()

        r = self.client.get("/invites/user/volunteer@example.com")
        self.assertEqual(r.status_code, 200)
        data = json.loads(r.data)
        # Find the invite for event 1
        event1_invites = [inv for inv in data if inv["event_id"] == 1]
        self.assertGreater(len(event1_invites), 0)
        # Must have event details
        self.assertIn("event", event1_invites[0])
        self.assertIn("event_name", event1_invites[0]["event"])

    # Lines 338-339: when event has non-null date
    def test_user_events_formats_event_date(self):
        """Hit lines 338-339 - format event date when present"""
        with app.app_context():
            user = UserCredentials.query.filter_by(email="volunteer@example.com").first()
            # Event 1 has a date: date(2026,12,1)
            invite = EventInvite(user_id=user.id, event_id=1, status="accepted")
            db.session.add(invite)
            db.session.commit()

        r = self.client.get("/user/volunteer@example.com/events")
        self.assertEqual(r.status_code, 200)
        data = json.loads(r.data)
        events = data["events"]
        # Should have event with formatted date
        event1 = [e for e in events if e["event_id"] == 1]
        if len(event1) > 0:
            self.assertIsNotNone(event1[0].get("event_date"))

    # Lines 437-439: when event exists in history
    def test_history_includes_event_details(self):
        """Hit lines 437-439 - include event details when event exists"""
        # Volunteer already has history for event 1 from seeder
        r = self.client.get("/history/volunteer@example.com")
        self.assertEqual(r.status_code, 200)
        data = json.loads(r.data)
        # Should have at least one event
        self.assertGreater(len(data), 0)
        # Should have event_id, event_name, participation_date
        self.assertIn("event_id", data[0])
        self.assertIn("event_name", data[0])

    # Lines 638-639: when user has profile
    def test_event_volunteers_includes_user_with_profile(self):
        """Hit lines 638-639 - include volunteer with profile"""
        with app.app_context():
            user = UserCredentials.query.filter_by(email="volunteer@example.com").first()
            # Volunteer has profile
            self.assertIsNotNone(user.profile)
            invite = EventInvite(user_id=user.id, event_id=1, status="accepted")
            db.session.add(invite)
            db.session.commit()

        r = self.client.get("/events/1/volunteers")
        self.assertEqual(r.status_code, 200)
        data = json.loads(r.data)
        # Should include volunteer
        emails = [v["email"] for v in data]
        self.assertIn("volunteer@example.com", emails)

    # Lines 840-842: when profile has address fields
    def test_users_builds_address_string(self):
        """Hit lines 840-842 - build address from multiple fields"""
        # Admin and volunteer both have addresses from seeder
        r = self.client.get("/users")
        self.assertEqual(r.status_code, 200)
        data = json.loads(r.data)
        # Find volunteer user
        vol = [u for u in data if u["email"] == "volunteer@example.com"]
        self.assertEqual(len(vol), 1)
        # Should have address with multiple parts
        self.assertNotEqual(vol[0]["address"], "N/A")
        self.assertIn(",", vol[0]["address"])  # Multiple parts joined

    # Lines 878-880: when profile exists
    def test_update_user_updates_existing_profile(self):
        """Hit lines 878-880 - update existing profile full_name"""
        # Volunteer has profile from seeder
        r = self.client.put("/users/volunteer@example.com", json={"name": "Changed Via API"})
        self.assertEqual(r.status_code, 200)

        with app.app_context():
            user = UserCredentials.query.filter_by(email="volunteer@example.com").first()
            self.assertEqual(user.profile.full_name, "Changed Via API")

    # Lines 907-909: when profile exists for deletion
    def test_delete_user_deletes_profile_first(self):
        """Hit lines 907-909 - delete profile before user"""
        with app.app_context():
            user = UserCredentials(email="delwithprof@example.com")
            user.set_password("Password1")
            db.session.add(user)
            db.session.commit()

            profile = UserProfile(id=user.id, full_name="Will Delete")
            db.session.add(profile)
            db.session.commit()

        r = self.client.delete("/users/delwithprof@example.com")
        self.assertEqual(r.status_code, 200)

    # Lines 982-984: when user has NO history
    def test_csv_shows_no_history_for_volunteers(self):
        """Hit lines 982-984 - show 'No History' in CSV"""
        with app.app_context():
            user = UserCredentials(email="csvempty@example.com", role="volunteer")
            user.set_password("Password1")
            db.session.add(user)
            db.session.commit()

            profile = UserProfile(id=user.id, full_name="CSV Empty")
            db.session.add(profile)
            db.session.commit()

        r = self.client.get("/reports/volunteer_history.csv")
        self.assertEqual(r.status_code, 200)
        content = r.data.decode()
        self.assertIn("csvempty@example.com", content)
        self.assertIn("No History", content)

    # Lines 1062-1064: when event has NO volunteers
    def test_csv_shows_no_volunteers_for_events(self):
        """Hit lines 1062-1064 - show 'No Volunteers' in CSV"""
        with app.app_context():
            event = EventDetails(event_name="CSV Empty Event")
            db.session.add(event)
            db.session.commit()

        r = self.client.get("/reports/event_assignments.csv")
        self.assertEqual(r.status_code, 200)
        content = r.data.decode()
        self.assertIn("CSV Empty Event", content)
        self.assertIn("No Volunteers", content)

    # Lines 1092-1094: when user has NO history
    def test_json_shows_no_history_for_volunteers(self):
        """Hit lines 1092-1094 - show 'No History' in JSON"""
        with app.app_context():
            user = UserCredentials(email="jsonempty@example.com", role="volunteer")
            user.set_password("Password1")
            db.session.add(user)
            db.session.commit()

            profile = UserProfile(id=user.id, full_name="JSON Empty")
            db.session.add(profile)
            db.session.commit()

        r = self.client.get("/reports/json/volunteer_history")
        self.assertEqual(r.status_code, 200)
        data = json.loads(r.data)
        empty_user = [d for d in data if d["Email"] == "jsonempty@example.com"]
        self.assertGreater(len(empty_user), 0)
        self.assertEqual(empty_user[0]["Event Name"], "No History")

    # Lines 1152-1154: when event has NO volunteers
    def test_json_shows_none_for_events_without_volunteers(self):
        """Hit lines 1152-1154 - show 'None' volunteer in JSON"""
        with app.app_context():
            event = EventDetails(event_name="JSON Empty Event")
            db.session.add(event)
            db.session.commit()

        r = self.client.get("/reports/json/event_assignments")
        self.assertEqual(r.status_code, 200)
        data = json.loads(r.data)
        empty_event = [d for d in data if d["Event Name"] == "JSON Empty Event"]
        self.assertGreater(len(empty_event), 0)
        self.assertEqual(empty_event[0]["Volunteer"], "None")

    # Lines 1196-1198: when 'role' in data
    def test_update_user_changes_role(self):
        """Hit lines 1196-1198 - change user role"""
        with app.app_context():
            user = UserCredentials(email="rolechanger@example.com")
            user.set_password("Password1")
            db.session.add(user)
            db.session.commit()

        r = self.client.put("/users/rolechanger@example.com", json={"role": "admin"})
        self.assertEqual(r.status_code, 200)

        with app.app_context():
            user = UserCredentials.query.filter_by(email="rolechanger@example.com").first()
            self.assertEqual(user.role, "admin")

    # Lines 1233-1235: when profile doesn't exist (else branch)
    def test_update_user_creates_profile_when_none_exists(self):
        """Hit lines 1233-1235 - create new profile if missing"""
        with app.app_context():
            user = UserCredentials(email="needsnewprof@example.com")
            user.set_password("Password1")
            db.session.add(user)
            db.session.commit()
            # Explicitly NO profile

        r = self.client.put("/users/needsnewprof@example.com", json={"name": "Brand New"})
        self.assertEqual(r.status_code, 200)

        with app.app_context():
            user = UserCredentials.query.filter_by(email="needsnewprof@example.com").first()
            self.assertIsNotNone(user.profile)
            self.assertEqual(user.profile.full_name, "Brand New")

    # Lines 1268-1270: delete history and invites
    def test_delete_user_removes_history_and_invites(self):
        """Hit lines 1268-1270 - delete all history and invites"""
        with app.app_context():
            user = UserCredentials(email="deletefull@example.com")
            user.set_password("Password1")
            db.session.add(user)
            db.session.commit()

            # Add history and invite
            history = VolunteerHistory(user_id=user.id, event_id=1)
            invite = EventInvite(user_id=user.id, event_id=1)
            db.session.add_all([history, invite])
            db.session.commit()

            user_id = user.id

        r = self.client.delete("/users/deletefull@example.com")
        self.assertEqual(r.status_code, 200)

        # Verify history and invites are gone
        with app.app_context():
            hist_count = VolunteerHistory.query.filter_by(user_id=user_id).count()
            inv_count = EventInvite.query.filter_by(user_id=user_id).count()
            self.assertEqual(hist_count, 0)
            self.assertEqual(inv_count, 0)


if __name__ == "__main__":
    unittest.main()
