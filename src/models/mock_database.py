from typing import List
from .database import Database
from mockfirestore import MockFirestore


class MockDatabase(Database):
    def __init__(self) -> None:
        self.db = MockFirestore()

    def get_sessions(self) -> List[dict]:
        return [doc.to_dict()
                for doc in self.db.collection('sessions').stream()]

    def get_resistors(self) -> List[dict]:
        return [doc.to_dict() for doc in self.db.collection('sessions').document(
            self.current_session).collection('scans').stream()]

    def get_current_session(self) -> dict:
        return self.db.collection('sessions').document(
            self.current_session).get().to_dict()
