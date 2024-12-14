import firebase_admin
from firebase_admin import credentials
from pathlib import Path

CREDENTIALS_PATH = Path(__file__).parents[4] / "creds/credentials.json"


class FirebaseClient:
    def __init__(self):

        self.credentials = credentials.Certificate(CREDENTIALS_PATH)
        self.app = firebase_admin.initialize_app(self.credentials)
