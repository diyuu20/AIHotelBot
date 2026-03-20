import json
import os
import random
from datetime import datetime, timedelta

# --- Configuration ---
NUM_ROOMS = 100
CURRENCY = "INR"
MAX_BOOKINGS_PER_ROOM = 4
DATABASE_FILE = "../static/rooms.json"

def generate_room_schedule():
    """Generates a random future booking schedule for a single room."""
    schedule = []
    num_bookings = random.randint(0, MAX_BOOKINGS_PER_ROOM)
    
    current_date = datetime.now() + timedelta(days=random.randint(1, 10))

    for _ in range(num_bookings):
        booking_duration = timedelta(days=random.randint(3, 7))
        check_out_date = current_date + booking_duration
        
        schedule.append({
            "booking_id": f"BK{random.randint(10000, 99999)}",
            "start_date": current_date.strftime("%Y-%m-%d"),
            "end_date": check_out_date.strftime("%Y-%m-%d")
        })
        
        current_date = check_out_date + timedelta(days=random.randint(1, 15))
        
    return schedule

def get_room_category(price):
    """Assigns a category based on the price per night."""
    if price < 5000:
        return "Silver"
    elif price < 10000:
        return "Gold"
    elif price < 15000:
        return "Platinum"
    else:
        return "Diamond"

def generate_room_database(num_rooms):
    """Generates a list of all rooms with their details and schedule."""
    database = {"rooms": []}
    
    all_room_numbers = []
    for floor in range(1, 11):
        for room in range(1, 11):
            all_room_numbers.append(int(f"{floor}{room:02d}"))
            
    for room_num in all_room_numbers:
        price = random.randint(25, 150) * 100
        category = get_room_category(price) # Get category from price

        database["rooms"].append({
            "room_number": str(room_num),
            "category": category, # --- CHANGE: Added the new category field ---
            "capacity": random.randint(2, 7),
            "price_per_night": price,
            "currency": CURRENCY,
            "bookings": generate_room_schedule()
        })
    return database

if __name__ == "__main__":
    print("🚀 Generating new room database...")
    room_database = generate_room_database(NUM_ROOMS)
    with open(DATABASE_FILE, 'w') as f:
        json.dump(room_database, f, indent=4)
    print(f"✅ Successfully generated '{DATABASE_FILE}' with room categories.")