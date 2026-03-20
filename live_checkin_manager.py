import json
import os
from datetime import datetime
import face_recognition
import numpy as np
from config import DISTANCE_THRESHOLD # Import the consistent threshold

LIVE_CHECKINS_FILE = "live_checkins.json"

def load_live_checkins():
    """Loads the live check-ins database from the JSON file."""
    if not os.path.exists(LIVE_CHECKINS_FILE):
        return {"active_checkins": []}
    try:
        with open(LIVE_CHECKINS_FILE, 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return {"active_checkins": []}


def save_live_checkins(db):
    """Saves the live check-ins database to the JSON file."""
    with open(LIVE_CHECKINS_FILE, 'w') as f:
        json.dump(db, f, indent=4)

def is_room_checked_in(room_number):
    """
    Checks if a room number is already present in the live check-ins dataset.
    """
    db = load_live_checkins()
    for checkin in db["active_checkins"]:
        if checkin.get("allocatedRoom") == room_number:
            return True
    return False

def add_live_checkin(booking_id, room_number, all_guests_data):
    """
    Adds a new record to the live check-ins dataset.
    """
    db = load_live_checkins()
    
    guest_details_with_encodings = []
    for guest in all_guests_data:
        guest_details_with_encodings.append({
            "name": guest.get("name"),
            "dob": guest.get("dob"),
            "gender": guest.get("gender"),
            "photo_path": guest.get("photo_path"),
            "face_encoding": guest.get("face_encoding", "Not Captured") 
        })

    new_checkin_record = {
        "bookingId": booking_id,
        "allocatedRoom": room_number,
        "checkinTime": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
        "guests": guest_details_with_encodings
    }
    
    db["active_checkins"].append(new_checkin_record)
    save_live_checkins(db)
    print(f"✅  Added live check-in for Room {room_number}, Booking {booking_id}")

def find_checkin_by_face(face_encoding_to_check):
    """
    Searches the live_checkins.json file for a matching face.
    Returns the entire check-in record if a match is found, otherwise None.
    """
    db = load_live_checkins()
    if not db["active_checkins"]:
        return None

    for checkin_record in db["active_checkins"]:
        known_encodings = []
        for guest in checkin_record.get("guests", []):
            encoding = guest.get("face_encoding")
            if encoding and isinstance(encoding, list):
                known_encodings.append(np.array(encoding))
        
        if not known_encodings:
            continue

        face_distances = face_recognition.face_distance(known_encodings, face_encoding_to_check)
        
        if np.any(face_distances <= DISTANCE_THRESHOLD):
            # A guest from this booking was matched. Return the whole booking record.
            return checkin_record
            
    return None

def remove_checkin_by_booking_id(booking_id):
    """
    Finds a check-in record by its booking ID and removes it from the dataset.
    """
    db = load_live_checkins()
    original_count = len(db["active_checkins"])
    
    # Create a new list excluding the check-in to be removed
    db["active_checkins"] = [
        checkin for checkin in db["active_checkins"] if checkin.get("bookingId") != booking_id
    ]

    if len(db["active_checkins"]) < original_count:
        save_live_checkins(db)
        print(f"✅  Successfully checked out and removed Booking ID: {booking_id}")
        return True
        
    print(f"⚠️  Could not find Booking ID {booking_id} to remove for checkout.")
    return False
