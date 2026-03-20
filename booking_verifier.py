import pdfplumber
import os
from datetime import datetime

PDF_PATH = os.path.join('static', 'active_bookings.pdf')

def find_booking_in_pdf(booking_id):
    """
    Searches for a booking ID in the active_bookings.pdf file and returns all details.
    """
    if not os.path.exists(PDF_PATH):
        return {"error": "Booking data file not found."}

    try:
        with pdfplumber.open(PDF_PATH) as pdf:
            page = pdf.pages[0]
            table = page.extract_table()
            if not table:
                return {"error": "Could not find a table in the booking PDF."}

            headers = [h.strip() for h in table[0]]
            # Find all column indices
            id_col = headers.index("Booking ID")
            name_col = headers.index("Booking Under Name")
            people_col = headers.index("Num People")
            room_col = headers.index("Alloted Room")
            checkin_col = headers.index("Check In")
            checkout_col = headers.index("Check Out")
            # --- NEW: Get indices for new columns ---
            type_of_room_col = headers.index("Type of Room")
            room_facing_col = headers.index("Room Facing")
            type_of_plan_col = headers.index("Type of Plan")
            special_request_col = headers.index("Special Request")

            for row in table[1:]:
                if row[id_col] and row[id_col].strip() == booking_id:
                    # return {
                    #     "booking_id": row[id_col].strip(),
                    #     "name": row[name_col].strip(),
                    #     "people": row[people_col].strip(),
                    #     "room": row[room_col].strip(),
                    #     "check_in_date": row[checkin_col].strip(),
                    #     "check_out_date": row[checkout_col].strip(),
                    #     # --- NEW: Add new data to the returned dictionary ---
                    #     "type_of_room": row[type_of_room_col].strip(),
                    #     "room_facing": row[room_facing_col].strip(),
                    #     "type_of_plan": row[type_of_plan_col].strip(),
                    #     "special_request": row[special_request_col].strip(),
                    # }
                    return {
                        "booking_id": row[id_col].strip(),
                        "booking_under_name": row[name_col].strip(),
                        "num_people": row[people_col].strip(),
                        "alloted_room": row[room_col].strip(),
                        "check_in": row[checkin_col].strip(),
                        "check_out": row[checkout_col].strip(),

                        "type_of_room": row[type_of_room_col].strip(),
                        "room_facing": row[room_facing_col].strip(),
                        "type_of_plan": row[type_of_plan_col].strip(),
                        "special_request": row[special_request_col].strip(),
                    }
            return None # Return None if loop finishes and no booking is found
    except (ValueError, IndexError):
        return {"error": "PDF has missing or incorrect column headers."}
    except Exception as e:
        return {"error": f"An error occurred while reading the PDF: {e}"}


def verify_checkin_time(booking_details):
    """
    Checks the booking's check-in date and time against the current time.
    """
    response = {"status": "error", "message": "", "details": booking_details}
    try:
        checkin_date_str = booking_details.get("check_in_date")
        checkin_date = datetime.strptime(checkin_date_str, "%Y-%m-%d").date()
        
        now = datetime.now()
        today = now.date()
        
        # --- CHANGE: Updated the message to include all new details ---
        base_message = (
            f"Booking Found for {booking_details.get('name')}. "
            f"Room: {booking_details.get('room')} ({booking_details.get('type_of_room', '')} - {booking_details.get('room_facing', '')}). "
            f"Guests: {booking_details.get('people')}. "
            f"Plan: {booking_details.get('type_of_plan', '')}. "
            f"Special Request: {booking_details.get('special_request', 'None')}. "
            f"Check-in: {booking_details.get('check_in_date')}, Check-out: {booking_details.get('check_out_date')}."
        )

        if checkin_date > today:
            response["status"] = "future_booking"
            response["message"] = base_message + " Your check-in is not today. Please come back on your check-in date."
        elif checkin_date < today:
            response["status"] = "date_passed"
            response["message"] = base_message + " Your check-in date has passed. Please see the front desk for assistance."
        else:
            response["status"] = "proceed"
            response["message"] = base_message + " Please proceed to guest verification."
        
        return response

    except (ValueError, TypeError):
        response["message"] = "Could not parse the check-in date from the booking data."
        return response

def get_checkout_date(booking_id):
    """
    Reads the active_bookings.pdf and returns the checkout date for a given booking ID.
    """
    if not os.path.exists(PDF_PATH):
        return None
    try:
        with pdfplumber.open(PDF_PATH) as pdf:
            page = pdf.pages[0]
            table = page.extract_table()
            if not table: return None
            headers = [h.strip() for h in table[0]]
            id_col = headers.index("Booking ID")
            checkout_col = headers.index("Check Out")
            for row in table[1:]:
                if row[id_col] and row[id_col].strip() == booking_id:
                    return row[checkout_col].strip()
        return None
    except Exception as e:
        print(f"Error reading checkout date from PDF: {e}")
        return None