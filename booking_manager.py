import json
import os
from datetime import datetime

DATABASE_FILE = "./static/rooms.json"

def _load_room_database():
    """A private helper function to load the room database."""
    if not os.path.exists(DATABASE_FILE):
        return {"rooms": []}
    try:
        with open(DATABASE_FILE, 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return {"rooms": []}

def _save_room_database(db):
    """A private helper function to save the room database."""
    with open(DATABASE_FILE, 'w') as f:
        json.dump(db, f, indent=4)

def find_available_rooms(check_in_str, check_out_str, num_guests):
    """
    Finds rooms that are available for a given date range and can accommodate the guests.
    """
    db = _load_room_database()
    available_rooms = []
    
    try:
        desired_start = datetime.strptime(check_in_str, "%Y-%m-%d")
        desired_end = datetime.strptime(check_out_str, "%Y-%m-%d")
        num_guests = int(num_guests)
    except (ValueError, TypeError):
        return []

    for room in db["rooms"]:
        if room.get("capacity", 0) < num_guests:
            continue

        is_available = True
        for booking in room.get("bookings", []):
            booking_start = datetime.strptime(booking["start_date"], "%Y-%m-%d")
            booking_end = datetime.strptime(booking["end_date"], "%Y-%m-%d")

            # --- FIX: This is the robust and correct logic for checking date overlaps ---
            # A conflict exists if the desired start is before an existing booking ends,
            # AND the desired end is after that same booking starts.
            if desired_start < booking_end and desired_end > booking_start:
                is_available = False
                break
        
        if is_available:
            available_rooms.append(room)
            
    return available_rooms

def add_booking_to_room(booking_details):
    """
    Adds a new booking to the schedule of a specific room in rooms.json.
    """
    db = _load_room_database()
    room_number_to_update = booking_details.get("Alloted Room")
    
    for room in db["rooms"]:
        if room.get("room_number") == room_number_to_update:
            new_booking_entry = {
                "booking_id": booking_details.get("Booking ID"),
                "start_date": booking_details.get("Check In"),
                "end_date": booking_details.get("Check Out")
            }
            room["bookings"].append(new_booking_entry)
            print(f"✅  Updated schedule for Room {room_number_to_update} in rooms.json")
            break
    
    _save_room_database(db)