# identity_verifier.py

import face_recognition
import json
import os
import numpy as np
import uuid
from config import GUEST_DB_FILE, DISTANCE_THRESHOLD

def _load_guest_database():
    """A private helper function to load the guest identity database."""
    if not os.path.exists(GUEST_DB_FILE):
        return {"guests": []}
    try:
        with open(GUEST_DB_FILE, 'r') as f:
            content = f.read()
            if not content:
                return {"guests": []}
            return json.loads(content)
    except (json.JSONDecodeError, FileNotFoundError):
        return {"guests": []}

def _save_guest_database(db):
    """A private helper function to save the guest identity database."""
    with open(GUEST_DB_FILE, 'w') as f:
        json.dump(db, f, indent=4)

def find_guest_by_face(face_encoding_to_check):
    """
    Searches the guest database for a matching face and returns the guest's data.
    """
    db = _load_guest_database()
    if not db["guests"]:
        return None

    # Filter out any guests that have an invalid or null face encoding
    valid_guests = [
        guest for guest in db['guests'] 
        if 'face_encoding' in guest and isinstance(guest['face_encoding'], list) and len(guest['face_encoding']) == 128
    ]

    if not valid_guests:
        return None

    known_encodings = [np.array(guest['face_encoding']) for guest in valid_guests]

    # Compare the new face to all existing valid faces
    face_distances = face_recognition.face_distance(known_encodings, face_encoding_to_check)
    
    if len(face_distances) > 0:
        best_match_index = np.argmin(face_distances)
        if face_distances[best_match_index] <= DISTANCE_THRESHOLD:
            # Return the data of the guest that corresponds to the best match
            return valid_guests[best_match_index]
            
    return None

def add_guest_to_database(face_encoding, user_data, ocr_data, doc_image_path, doc_type):
    """
    Adds a new, fully verified guest to the identity database.
    """
    db = _load_guest_database()

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
    _save_guest_database(db)
    print(f"✅ Added new verified guest to database: {user_data['name']}")
    return new_guest_record