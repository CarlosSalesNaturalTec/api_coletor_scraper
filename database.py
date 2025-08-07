import os
from google.cloud import firestore
from dotenv import load_dotenv

load_dotenv()

_db = None

def get_db():
    """
    Initializes and returns a Firestore client, ensuring a single instance.
    """
    global _db
    if _db is None:
        try:
            if not os.getenv("GOOGLE_APPLICATION_CREDENTIALS"):
                raise ValueError("GOOGLE_APPLICATION_CREDENTIALS environment variable not set.")
            
            _db = firestore.Client()
        except Exception as e:
            print(f"Error connecting to Firestore: {e}")
            # In case of an error, _db remains None
            return None
    return _db