# floor_map_manager.py

import json
import os
from datetime import datetime

DATABASE_FILE = "static/rooms.json"

def _load_room_database():
    """A private helper function to load the room database."""
    if not os.path.exists(DATABASE_FILE):
        return {"rooms": []}
    try:
        with open(DATABASE_FILE, 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return {"rooms": []}

def get_floor_room_statuses(floor_number, check_in_str, check_out_str, num_guests):
    """
    Gets a detailed status for all rooms on a specific floor for a given date range.
    """
    db = _load_room_database()
    room_statuses = []
    
    try:
        desired_start = datetime.strptime(check_in_str, "%Y-%m-%d")
        desired_end = datetime.strptime(check_out_str, "%Y-%m-%d")
        num_guests = int(num_guests)
    except (ValueError, TypeError):
        return []

    floor_rooms = []
    for r in db["rooms"]:
        room_num_str = r.get("room_number", "")
        if room_num_str.startswith(str(floor_number)):
            if floor_number < 10 and len(room_num_str) == 3:
                floor_rooms.append(r)
            elif floor_number == 10 and len(room_num_str) == 4:
                floor_rooms.append(r)

    for room in floor_rooms:
        is_booked = False
        for booking in room.get("bookings", []):
            booking_start = datetime.strptime(booking["start_date"], "%Y-%m-%d")
            booking_end = datetime.strptime(booking["end_date"], "%Y-%m-%d")

            if desired_start < booking_end and desired_end > booking_start:
                is_booked = True
                break
        
        status = ""
        # --- FIX: This logic now correctly distinguishes between exact and sufficient capacity ---
        if is_booked:
            status = "Booked"
        elif room.get("capacity", 0) == num_guests:
            status = "Available" # Green: Available and exact capacity.
        elif room.get("capacity", 0) > num_guests:
            status = "WrongCapacity" # Gray: Available but larger capacity.
        else:
            status = "WrongCapacity" # Gray: Too small (will be unbookable in the HTML).


        room_statuses.append({
            "room_number": room.get("room_number"),
            "status": status,
            "capacity": room.get("capacity"),
            "category": room.get("category"),
            "price_per_night": room.get("price_per_night")
        })
            
    return room_statuses