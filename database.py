import os
from google.cloud import firestore
from dotenv import load_dotenv

load_dotenv()

def get_db():
    """Initializes and returns a Firestore client."""
    try:
        if not os.getenv("GOOGLE_APPLICATION_CREDENTIALS"):
            raise ValueError("GOOGLE_APPLICATION_CREDENTIALS environment variable not set.")
        
        db = firestore.Client()
        return db
    except Exception as e:
        print(f"Error connecting to Firestore: {e}")
        return None
