import unittest

from src.models import *


class DatabaseTest(unittest.TestCase):

    def test_new_session(self):
        db = MockDatabase()
        # Test if session gets added
        db.new_session()
        self.assertEqual(1, len(db.get_sessions()))
        db.new_session()
        self.assertEqual(2, len(db.get_sessions()))

    def test_add_resistor(self):
        db = MockDatabase()
        db.new_session()
        self.assertEqual(1, len(db.get_sessions()))

        db.add_resistor(200, 1)
        # Test if resistor gets added correctly
        resistors = db.get_resistors()
        self.assertEqual(1, len(resistors))
        self.assertEqual(resistors[0]["resistance"], 200)
        self.assertEqual(resistors[0]["wattage"], 1)

        # Test updating of total value
        session_data = db.get_current_session()
        self.assertEqual(session_data["total"], 1)

        db.add_resistor(200, 1)
        session_data = db.get_current_session()
        self.assertEqual(session_data["total"], 2)
