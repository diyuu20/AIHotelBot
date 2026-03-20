# checkout_module.py

import json
import os
import face_recognition
import numpy as np
from config import DISTANCE_THRESHOLD # We still use the consistent threshold from config

LIVE_CHECKINS_FILE = "live_checkins.json"

def _load_live_checkins():
    """A private helper function to load the live check-ins database."""
    if not os.path.exists(LIVE_CHECKINS_FILE):
        return {"active_checkins": []}
    try:
        with open(LIVE_CHECKINS_FILE, 'r') as f:
            # Handle case where file might be empty
            content = f.read()
            if not content:
                return {"active_checkins": []}
            return json.loads(content)
    except (json.JSONDecodeError, FileNotFoundError):
        return {"active_checkins": []}

def _save_live_checkins(db):
    """A private helper function to save the live check-ins database."""
    with open(LIVE_CHECKINS_FILE, 'w') as f:
        json.dump(db, f, indent=4)

def find_checkin_by_face(face_encoding_to_check):
    """
    Searches the live_checkins.json file for a matching face.
    This is a self-contained recognition function for the checkout process.
    Returns the entire check-in record if a match is found, otherwise None.
    """
    db = _load_live_checkins()
    if not db["active_checkins"]:
        return None

    # Iterate through each booking currently checked in
    for checkin_record in db["active_checkins"]:
        known_encodings = []
        # Check against all guests in that booking
        for guest in checkin_record.get("guests", []):
            encoding = guest.get("face_encoding")
            # Ensure the encoding is a valid list of numbers
            if encoding and isinstance(encoding, list) and len(encoding) == 128:
                known_encodings.append(np.array(encoding))
        
        if not known_encodings:
            continue # Skip this booking if it has no valid encodings

        # Compare the new face to all faces in the current booking
        face_distances = face_recognition.face_distance(known_encodings, face_encoding_to_check)
        
        # If any face in the booking is a close enough match, we've found the record
        if np.any(face_distances <= DISTANCE_THRESHOLD):
            print(f"✅ Checkout match found for Booking ID: {checkin_record.get('bookingId')}")
            return checkin_record
            
    print("❌ No matching check-in found for the provided face.")
    return None

def remove_checkin_by_booking_id(booking_id):
    """
    Finds a check-in record by its booking ID and removes it from the dataset.
    """
    db = _load_live_checkins()
    original_count = len(db["active_checkins"])
    
    # Create a new list that excludes the check-in to be removed
    db["active_checkins"] = [
        checkin for checkin in db["active_checkins"] if checkin.get("bookingId") != booking_id
    ]

    # If the new list is shorter, it means we found and removed the record
    if len(db["active_checkins"]) < original_count:
        _save_live_checkins(db)
        print(f"✅ Successfully checked out and removed Booking ID: {booking_id}")
        return True
        
    print(f"⚠️  Could not find Booking ID {booking_id} to remove for checkout.")
    return False