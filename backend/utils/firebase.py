import firebase_admin
from firebase_admin import credentials
import os

def init_firebase():
    if not firebase_admin._apps:
        cred_path = os.path.join(
            os.path.dirname(__file__),
            "..",
            "config",
            "serviceAccountKey.json"
        )

        cred = credentials.Certificate(cred_path)
        firebase_admin.initialize_app(cred)
