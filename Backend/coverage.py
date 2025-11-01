import unittest
from app2 import DB, add_notification

class TestNotifications(unittest.TestCase):

    def setup(self):
        DB["notifications"].clear() #reset data before each test

    def test_add_notifications(self):
        """Test that a notification is added correct"""

        result = add_notification("Test message", "info")

        self.assertEqual(result["message"], "Test message")
        self.assertEqual(result["type"], "info")
        self.assertFalse(result["read"])
        self.assertEqual(len(DB["notifications"]))


