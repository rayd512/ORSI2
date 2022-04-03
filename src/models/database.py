
import os
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore


class Database:
    def __init__(self) -> None:
        self._init_firebase_admin()
        self.db = firestore.client()

    def _init_firebase_admin(self) -> None:
        """
        Initialize firebase admin
        """
        firebase_json_path = os.environ.get('FIREBASE_ADMIN_PATH')

        if not firebase_json_path:
            raise Exception('FIREBASE_ADMIN_PATH not set!')

        cred = credentials.Certificate(
            os.environ.get('FIREBASE_ADMIN_PATH'))

        firebase_admin.initialize_app(cred)

    def new_session(self) -> None:
        """
        Instantiates a new scanning session
        """
        new_session_data = {
            u'time': firestore.SERVER_TIMESTAMP,
            u'total': 0
        }
        new_doc = self.db.collection(u'sessions').document()
        new_doc.set(new_session_data)
        self.current_session = new_doc.id

    def add_resistor(self, resistance: int, wattage: str) -> None:
        """
        Adds a new resistor to the current scanning session.
        Resistance to be provided in ohms
        Wattage to be provided in watts
        Raises error if no session has been started
        """
        new_scan_data = {
            u'createdAt': firestore.SERVER_TIMESTAMP,
            u'resistance': resistance,
            u'wattage': wattage
        }

        if self.current_session is None:
            raise Exception('No Current Session')

        self.db.collection(u'sessions').document(
            self.current_session).collection(u'scans').add(new_scan_data)

        session_ref = self.db.collection(
            u'sessions').document(self.current_session)

        session_data = session_ref.get()

        if not session_data.exists:
            raise Exception('Could not find current session')

        new_session_data = session_data.to_dict()
        new_session_data["total"] += 1

        self.db.collection(u'sessions').document(
            self.current_session).set(new_session_data)


if __name__ == "__main__":
    db = Database()
    db.new_session()
    print(db.current_session)
    db.add_resistor(200, 1)
