# guest_verification_module.py

import json
import os
import numpy as np
import uuid
from config import GUEST_DB_FILE

def load_guest_database():
    """Loads the guest identity database from the JSON file."""
    if not os.path.exists(GUEST_DB_FILE):
        return {"guests": []}
    try:
        with open(GUEST_DB_FILE, 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return {"guests": []}

def save_guest_database(db):
    """Saves the guest identity database to the JSON file."""
    with open(GUEST_DB_FILE, 'w') as f:
        json.dump(db, f, indent=4)

def add_guest_to_database(face_encoding, user_data, ocr_data, doc_image_path, doc_type):
    """
    Adds a new, fully verified guest to the identity database.
    """
    db = load_guest_database()

    encoding_for_json = None
    if isinstance(face_encoding, np.ndarray) and face_encoding.size > 0:
        encoding_for_json = face_encoding.tolist()
    else:
        print(f"⚠️  WARNING: An invalid face encoding was passed for guest '{user_data.get('name')}'. Saving as null.")

    new_guest_record = {
        "guest_id": str(uuid.uuid4()),
        "name": user_data['name'],
        "dob": user_data['dob'],
        "gender": user_data['gender'],
        "face_encoding": encoding_for_json,
        "document_type": doc_type,
        "document_photo_path": doc_image_path,
        "document_details": {
            "name_on_doc": ocr_data.get('name', 'N/A'),
            "dob_on_doc": ocr_data.get('dob', 'N/A'),
            "doc_number": ocr_data.get('document_number', 'N/A')
        }
    }

    db['guests'].append(new_guest_record)
    save_guest_database(db)
    print(f"✅ Added new verified guest to database: {user_data['name']}")
    return new_guest_record