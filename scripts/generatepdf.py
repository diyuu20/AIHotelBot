import random
from datetime import datetime, timedelta
from fpdf import FPDF
import os

OUTPUT_DIR = r"F:\Documents\Downloads\Devshree\AIHOTELBOT\AIHOTELBOT\static"
os.makedirs(OUTPUT_DIR, exist_ok=True)


# --- Configuration ---
NUM_BOOKINGS = 10
NUM_ROOMS = 100 # 10 floors * 10 rooms/floor
CURRENCY = "INR"

SAMPLE_NAMES = [
    "Aarav Sharma", "Vivaan Singh", "Aditya Kumar", "Vihaan Gupta", "Arjun Patel",
    "Sai Reddy", "Reyansh Joshi", "Krishna Verma", "Ishaan Mehra", "Saanvi Devi",
    "Aanya Iyer", "Myra Choudhary", "Aadya Menon", "Ananya Khatri", "Pari Agarwal"
]

# --- NEW: Data for the new columns ---
ROOM_TYPES = ['Standard', 'Deluxe', 'Suite', 'Executive Suite']
ROOM_FACING = ['City View', 'Sea View', 'Garden View', 'Pool View']
MEAL_PLANS = ['Breakfast Only', 'Half Board (B+D)', 'Full Board (All Meals)', 'Room Only']
SPECIAL_REQUESTS = ['Late Check-out', 'Extra Bed', 'Honeymoon Decor', 'Quiet Room', 'None']


def generate_all_room_numbers():
    """Generates a list of all 100 3/4-digit room numbers."""
    all_rooms = []
    for floor in range(1, 11):
        for room in range(1, 11):
            all_rooms.append(int(f"{floor}{room:02d}"))
    return all_rooms

def generate_active_bookings(num_bookings, all_rooms):
    """Generates a list of random active booking data."""
    bookings = []
    
    # Add specific booking for Aqeel Memon
    aqeel_booking = {
        "booking_id": "21960",
        "booking_under_name": "Aqeel Memon",
        "booking_date": (datetime.now() - timedelta(days=random.randint(5, 30))).strftime("%Y-%m-%d"),
        "check_in": "2025-09-11",
        "check_out": "2025-09-15",
        "account_number": str(random.randint(6000000000, 9999999999)),
        "num_people": "2",
        "alloted_room": str(random.choice(all_rooms)),
        "type_of_room": random.choice(ROOM_TYPES),
        "room_facing": random.choice(ROOM_FACING),
        "type_of_plan": random.choice(MEAL_PLANS),
        "special_request": random.choice(SPECIAL_REQUESTS)
    }
    abhishek_shah = {
        "booking_id": "22901",
        "booking_under_name": "Abhishek Khambata",
        "booking_date": (datetime.now() - timedelta(days=random.randint(5, 30))).strftime("%Y-%m-%d"),
        "check_in": "2025-09-11",
        "check_out": "2025-09-15",
        "account_number": str(random.randint(6000000000, 9999999999)),
        "num_people": "1",
        "alloted_room": str(random.choice(all_rooms)),
        "type_of_room": random.choice(ROOM_TYPES),
        "room_facing": random.choice(ROOM_FACING),
        "type_of_plan": random.choice(MEAL_PLANS),
        "special_request": random.choice(SPECIAL_REQUESTS)
    }

    devshree_booking = {
    "booking_id": "DEV002",
    "booking_under_name": "Devshree Patel",
    "booking_date": datetime.now().strftime("%Y-%m-%d"),
    "check_in": "2026-03-20",
    "check_out": "2026-03-22",
    "account_number": "9876543210",
    "num_people": "2",
    "alloted_room": str(random.choice(all_rooms)),
    "type_of_room": random.choice(ROOM_TYPES),
    "room_facing": random.choice(ROOM_FACING),
    "type_of_plan": random.choice(MEAL_PLANS),
    "special_request": "None"
    }

    


    all_rooms.remove(int(abhishek_shah["alloted_room"]))
    bookings.append(abhishek_shah)
    all_rooms.remove(int(aqeel_booking["alloted_room"]))
    bookings.append(aqeel_booking)
    all_rooms.remove(int(devshree_booking["alloted_room"]))
    bookings.append(devshree_booking)
    
    # Generate the rest of the random bookings
    remaining = num_bookings - len(bookings)
    alloted_rooms_random = random.sample(all_rooms, remaining)

    # alloted_rooms_random = random.sample(all_rooms, num_bookings - 1)
    
    # for i in range(num_bookings - 1):
    for i in range(remaining):
        bookings.append({
            "booking_id": f"BK{random.randint(10000, 99999)}",
            "booking_under_name": random.choice(SAMPLE_NAMES),
            "booking_date": (datetime.now() - timedelta(days=random.randint(5, 30))).strftime("%Y-%m-%d"),
            "check_in": (datetime.now() - timedelta(days=random.randint(0, 4))).strftime("%Y-%m-%d"),
            "check_out": (datetime.now() + timedelta(days=random.randint(1, 10))).strftime("%Y-%m-%d"),
            "account_number": str(random.randint(6000000000, 9999999999)),
            "num_people": str(random.randint(2, 7)),
            "alloted_room": str(alloted_rooms_random[i]),
            "type_of_room": random.choice(ROOM_TYPES),
            "room_facing": random.choice(ROOM_FACING),
            "type_of_plan": random.choice(MEAL_PLANS),
            "special_request": random.choice(SPECIAL_REQUESTS)
        })
    return bookings

def generate_room_list(num_rooms, active_bookings):
    """Generates a list of all rooms, marking booked ones."""
    rooms = []
    
    booked_rooms_map = {
        booking['alloted_room']: booking['booking_id'] for booking in active_bookings
    }
    
    all_room_numbers = []
    for floor in range(1, 11):
        for room in range(1, 11):
            all_room_numbers.append(int(f"{floor}{room:02d}"))

    for room_num in all_room_numbers:
        rooms.append({
            "room_no": str(room_num),
            "number_of_beds": str(random.randint(2, 7)),
            "price": f"{random.randint(25, 150) * 100} {CURRENCY}",
            "booking_id": booked_rooms_map.get(str(room_num), "Available")
        })
    return rooms

class PDF(FPDF):
    """Custom PDF class to handle headers and footers."""
    def header(self):
        self.set_font('Arial', 'B', 12)
        title_w = self.get_string_width(self.title) + 6
        self.set_x((self.w - title_w) / 2)
        self.cell(title_w, 10, self.title, border=1, ln=1, align='C')
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', align='C')

def create_pdf_from_data(title, headers, data, filename):
    """Creates a PDF with a table from a list of dictionaries."""
    pdf = PDF()
    pdf.set_title(title)
    pdf.add_page(orientation='L')
    pdf.set_font('Arial', '', 10)
    
    col_widths = {}
    for header in headers:
        max_width = pdf.get_string_width(header)
        for row in data:
            key = header.lower().replace(" ", "_").replace(".", "")
            cell_width = pdf.get_string_width(str(row.get(key, '')))
            if cell_width > max_width:
                max_width = cell_width
        col_widths[header] = max_width + 6

    pdf.set_fill_color(200, 220, 255)
    pdf.set_font('Arial', 'B', 10)
    for header in headers:
        pdf.cell(col_widths[header], 10, header, border=1, align='C', fill=True)
    pdf.ln()
    
    pdf.set_font('Arial', '', 9)
    fill = False
    for row in data:
        pdf.set_fill_color(240, 240, 240)
        for header in headers:
            key = header.lower().replace(" ", "_").replace(".", "")
            pdf.cell(col_widths[header], 10, str(row.get(key, '')), border=1, align='C', fill=fill)
        pdf.ln()
        fill = not fill

    pdf.output(filename)
    print(f"✅ Successfully generated '{filename}'")


if __name__ == "__main__":
    print("🚀 Starting PDF generation...")

    all_rooms = generate_all_room_numbers()
    active_bookings_data = generate_active_bookings(NUM_BOOKINGS, all_rooms.copy())
    rooms_data = generate_room_list(NUM_ROOMS, active_bookings_data)
    
    # --- CHANGE: Updated the headers list ---
    bookings_headers = [
        "Booking ID", "Booking Under Name", "Check In", "Check Out", 
        "Num People", "Alloted Room", "Type of Room", "Room Facing", 
        "Type of Plan", "Special Request", "Account Number"
    ]
    rooms_headers = ["Room No.", "Number of Beds", "Price", "Booking ID"]
    
    # create_pdf_from_data("Active Hotel Bookings", bookings_headers, active_bookings_data, "active_bookings.pdf")
    # create_pdf_from_data("Hotel Room Availability", rooms_headers, rooms_data, "rooms_available.pdf")
    
    print("🎉 All PDFs generated successfully.")

    create_pdf_from_data(
    "Active Hotel Bookings",
    bookings_headers,
    active_bookings_data,
    os.path.join(OUTPUT_DIR, "active_bookings.pdf")
    )
    
    create_pdf_from_data(
    "Hotel Room Availability",
    rooms_headers,
    rooms_data,
    os.path.join(OUTPUT_DIR, "rooms_available.pdf")
    )
