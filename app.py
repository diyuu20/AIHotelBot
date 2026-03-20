from flask import Flask, render_template, Response, request, redirect, url_for, session, flash
from face_recognition_module import recognize_person, load_encodings
from face_registration_module import register_guest, add_new_user
from booking_verifier import find_booking_in_pdf, verify_checkin_time
from ocr_processor import process_document
from guest_verification_module import add_guest_to_database
from live_checkin_manager import is_room_checked_in, add_live_checkin, find_checkin_by_face, remove_checkin_by_booking_id
import cv2
import time
import os
from datetime import datetime
import json
import base64
import numpy as np
import uuid
import face_recognition
from booking_verifier import find_booking_in_pdf, verify_checkin_time, get_checkout_date # <-- Add get_checkout_date
from booking_manager import find_available_rooms
from pdf_booking_manager import add_booking_to_pdf
import random # Also add this for generating booking IDs
from identity_verifier import find_guest_by_face
from booking_manager import find_available_rooms, add_booking_to_room
import os
import urllib.parse
from floor_map_manager import get_floor_room_statuses
from document_classifier import validate_document_type
from config import UNRECOGNIZED_DOCUMENT_THRESHOLD

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 32 * 1024 * 1024 
app.secret_key = 'your_super_secret_key'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['TEMP_CHECKIN_FOLDER'] = 'temp_checkins' # Folder for temporary check-in files

# --- JSON Report Generation Function ---
def generate_checkin_report_json(booking_id, verification_data, all_guests_data, room_number):
    checkin_time = datetime.now()
    time_str = checkin_time.strftime("%d-%m-%y-%H-%M")
    filename = f"{booking_id}_{time_str}.json"
    output_dir = os.path.join('static', 'checkins')
    os.makedirs(output_dir, exist_ok=True)
    filepath = os.path.join(output_dir, filename)
    report_data = {
        "bookingId": booking_id,
        "allocatedRoom": room_number,
        "checkinTime": checkin_time.strftime("%d/%m/%Y %H:%M:%S"),
        "totalGuests": len(all_guests_data),
        "allGuests": all_guests_data,
        "verifiedGuests": verification_data
    }
    with open(filepath, 'w') as f:
        json.dump(report_data, f, indent=4)
    print(f"Generated check-in report: {filepath}")
    return filepath

# --- Main Application Routes ---

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/checkin')
def checkin():
    return render_template('recognizing.html')

@app.route('/checkout_face_scan')
def checkout_face_scan():
    return render_template('checkout_scan.html')

# --- NEW: Routes for the "Book a Room" Feature ---

# In app.py

@app.route('/book_a_room', methods=['GET', 'POST'])
def book_a_room():
    """
    Handles the initial search and displays a list of floors with availability counts.
    """
    if request.method == 'POST':
        search_details = {
            "check_in": request.form.get('check_in'),
            "check_out": request.form.get('check_out'),
            "guests": int(request.form.get('guests', 1))
        }
        
        # --- NEW: Calculate availability for each floor ---
        floor_availability = []
        for floor_num in range(1, 11):
            # Get the status of all rooms on this floor
            room_statuses = get_floor_room_statuses(
                floor_num, 
                search_details["check_in"], 
                search_details["check_out"],
                search_details["guests"]
            )
            # Count how many rooms are marked as "Available"
            available_count = sum(1 for room in room_statuses if room['status'] == 'Available')
            floor_availability.append({'floor_number': floor_num, 'available_rooms': available_count})

        return render_template(
            'book_a_room.html', 
            search_complete=True, 
            search_details=search_details,
            floor_availability=floor_availability # Pass the new data to the template
        )

    # For a GET request, just show the initial search form
    return render_template('book_a_room.html', search_complete=False, search_details=None)

@app.route('/floor_map/<int:floor_number>')
def floor_map(floor_number):
    check_in = request.args.get('check_in')
    check_out = request.args.get('check_out')
    guests = request.args.get('guests')

    rooms = [
        {"room_no": f"{floor_number}01", "type": "Deluxe", "status": "available"},
        {"room_no": f"{floor_number}02", "type": "Suite", "status": "available"},
        {"room_no": f"{floor_number}03", "type": "Standard", "status": "booked"},
    ]

    return render_template(
        "floor_map.html",
        floor_number=floor_number,
        rooms=rooms,
        check_in=check_in,
        check_out=check_out,
        guests=guests
    )

# @app.route('/floor_map/<int:floor_number>')
# def floor_map(floor_number):
#     """
#     Displays the interactive map for a specific floor.
#     """
#     # Get the search criteria from the URL parameters
#     search_details = {
#         "check_in": request.args.get('check_in'),
#         "check_out": request.args.get('check_out'),
#         "guests": int(request.args.get('guests', 1))
#     }

#     # Get the status of all rooms on this floor for the selected dates
#     room_statuses = get_floor_room_statuses(floor_number, search_details["check_in"], search_details["check_out"], search_details["guests"])
    
#     return render_template(
#         'floor_map.html', 
#         floor_number=floor_number, 
#         room_statuses=room_statuses,
#         search_details=search_details
#     )

# @app.route('/run_checkout_recognition', methods=['POST'])
# def run_checkout_recognition():
#     data = request.get_json()
#     image_data = data.get('image')
#     if not image_data:
#         return redirect(url_for('index'))
#     try:
#         img_data = base64.b64decode(image_data.split(',')[1])
#         nparr = np.frombuffer(img_data, np.uint8)
#         frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
#         rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
#     except Exception as e:
#         print(f"Error decoding base64 image for checkout: {e}")
#         return redirect(url_for('index'))
#     face_locations = face_recognition.face_locations(rgb_frame)
#     face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)
#     if not face_encodings:
#         message = "Could not detect a face. Please try scanning again."
#         return render_template('redirect_page.html', message=message, redirect_url=url_for('index'))
#     checkin_record = find_checkin_by_face(face_encodings[0])
#     if checkin_record:
#         return render_template('confirm_checkout.html', checkin_details=checkin_record)
#     else:
#         message = "You were not found in the live check-in list. Please see the front desk for assistance."
#         return render_template('redirect_page.html', message=message, redirect_url=url_for('index'))

@app.route('/run_checkout_recognition', methods=['POST'])
def run_checkout_recognition():
    """Receives a captured face and checks against the live_checkins dataset."""
    data = request.get_json()
    image_data = data.get('image')
    if not image_data:
        return redirect(url_for('index'))

    try:
        img_data = base64.b64decode(image_data.split(',')[1])
        nparr = np.frombuffer(img_data, np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    except Exception as e:
        print(f"Error decoding base64 image for checkout: {e}")
        return redirect(url_for('index'))

    face_locations = face_recognition.face_locations(rgb_frame)
    face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

    if not face_encodings:
        message = "Could not detect a face. Please try scanning again."
        return render_template('redirect_page.html', message=message, redirect_url=url_for('index'))

    checkin_record = find_checkin_by_face(face_encodings[0])

    if checkin_record:
        booking_id = checkin_record.get("bookingId")
        checkout_date_str = get_checkout_date(booking_id)
        is_early_checkout = False
        
        if checkout_date_str:
            try:
                checkout_date = datetime.strptime(checkout_date_str, "%Y-%m-%d").date()
                today = datetime.now().date()
                if today < checkout_date:
                    is_early_checkout = True
            except ValueError:
                print(f"Warning: Could not parse checkout date '{checkout_date_str}'")

        return render_template('confirm_checkout.html', checkin_details=checkin_record, is_early_checkout=is_early_checkout)
    else:
        message = "You were not found in the live check-in list. Please see the front desk for assistance."
        return render_template('redirect_page.html', message=message, redirect_url=url_for('index'))

@app.route('/confirm_checkout/<booking_id>', methods=['POST'])
def confirm_checkout(booking_id):
    success = remove_checkin_by_booking_id(booking_id)
    if success:
        message = "Checkout Successful! We hope you enjoyed your stay."
    else:
        message = "There was an error processing your checkout. Please see the front desk."
    return render_template('redirect_page.html', message=message, redirect_url=url_for('index'))

@app.route('/run_recognition', methods=['POST'])
def run_recognition():
    data = request.get_json()
    if not data or not data.get('image'):
        return redirect(url_for('index'))
    image_data = data.get('image')
    try:
        img_data = base64.b64decode(image_data.split(',')[1])
        nparr = np.frombuffer(img_data, np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if frame is None: raise ValueError("Decoded image is None")
    except Exception as e:
        print(f"Error decoding base64 image: {e}")
        return redirect(url_for('index'))
    encodings_data = load_encodings()
    if encodings_data:
        name = recognize_person(frame, encodings_data)
    else:
        name = "No encodings loaded"
    # ✅ CASE 1: FACE DETECTED + RECOGNIZED
    if name and name not in ["Unknown", "No encodings loaded", "No face captured."]:
        question = f"Welcome back, {name}. Do you have a booking with us?"
        return render_template('ask_booking.html', question=question)

    # ❌ CASE 2: NO FACE DETECTED → SHOW OPTIONS
    elif name == "No face captured.":
        return render_template('checkin_options.html')

    # ❌ CASE 3: FACE NOT RECOGNIZED
    else:
        return render_template('checkin_options.html')

@app.route('/checkin_options')
def checkin_options():
    return render_template('checkin_options.html')

@app.route('/ask_register')
def ask_register_page():
    question = "Would you like to register?"
    return render_template('ask_register.html', question=question)

@app.route('/manual_booking')
def manual_booking():
    return render_template('manual_booking.html')

@app.route('/submit_booking_id', methods=['POST'])
def submit_booking_id():
    booking_id = request.form.get('booking_id')

    if not booking_id:
        flash("Please enter a booking ID", "error")
        return redirect(url_for('manual_booking'))

    # 🔥 Redirect to SAME QR FLOW
    return redirect(url_for('verify_booking', booking_id=booking_id))

@app.route('/scan_qr_page')
def scan_qr_page():
    return render_template('scan_qr.html')

@app.route('/verify_booking/<booking_id>')
def verify_booking(booking_id):
    booking_details = find_booking_in_pdf(booking_id)
    if not booking_details or "error" in booking_details:
        message = booking_details.get("error", "Booking ID not found.")
        return render_template('checkin.html', greeting=message)
    room_number = booking_details.get('room')
    if is_room_checked_in(room_number):
        message = f"Check-in failed. Room {room_number} is already occupied."
        return render_template('redirect_page.html', message=message, redirect_url=url_for('index'))
    
    temp_checkin_path = os.path.join(app.config['TEMP_CHECKIN_FOLDER'], f"{booking_id}.json")
    os.makedirs(app.config['TEMP_CHECKIN_FOLDER'], exist_ok=True)
    with open(temp_checkin_path, 'w') as f:
        json.dump({
            "booking_id": booking_id,
            "room_number": room_number,
            "guest_data": [],
            "verified_guests_data": []
        }, f, indent=4)
        
        
    # Always show booking details page (your 2nd image UI)
    return render_template('booking_details.html', booking=booking_details)



@app.route('/guest_details_form/<booking_id>')
def guest_details_form(booking_id):
    booking_details = find_booking_in_pdf(booking_id)
    if not booking_details or "error" in booking_details:
        return redirect(url_for('index'))
    try:
        num_people = int(booking_details.get("num_people", 0))
    except (ValueError, TypeError):
        num_people = 0
    return render_template('guest_form.html', num_people=num_people, booking_id=booking_id)

@app.route('/submit_guest_details/<booking_id>', methods=['POST'])
def submit_guest_details(booking_id):
    temp_checkin_path = os.path.join(app.config['TEMP_CHECKIN_FOLDER'], f"{booking_id}.json")
    if not os.path.exists(temp_checkin_path):
        return redirect(url_for('index'))

    num_people = int(request.form.get('num_people', 0))
    guest_data = []
    existing_guests = []
    failed_guests = []
    for i in range(1, num_people + 1):
        name = request.form.get(f'name_{i}')
        dob = request.form.get(f'dob_{i}')
        gender = request.form.get(f'gender_{i}')
        photo_data = request.form.get(f'photo_{i}')
        if name and photo_data:
            status, result_data = register_guest(name, photo_data)
            if status == "face_exists":
                existing_guests.append(name)
                face_encoding, photo_path = result_data
                guest_data.append({'name': name, 'dob': dob, 'gender': gender, 'photo_path': photo_path, 'face_encoding': face_encoding.tolist()})
            elif status == "success":
                photo_path, face_encoding = result_data
                guest_data.append({'name': name, 'dob': dob, 'gender': gender, 'photo_path': photo_path, 'face_encoding': face_encoding.tolist()})
            else:
                failed_guests.append(name)
    if failed_guests:
        flash(f"Error: Could not process photo for: {', '.join(failed_guests)}. Please try again.", 'error')
        return redirect(url_for('guest_details_form', booking_id=booking_id))
    if existing_guests:
        flash(f"Note: The following guests are already registered: {', '.join(existing_guests)}.", 'info')
    
    with open(temp_checkin_path, 'r') as f:
        data = json.load(f)
    data['guest_data'] = guest_data
    with open(temp_checkin_path, 'w') as f:
        json.dump(data, f, indent=4)

    return redirect(url_for('select_main_guests', booking_id=booking_id))

@app.route('/select_main_guests/<booking_id>')
def select_main_guests(booking_id):
    temp_checkin_path = os.path.join(app.config['TEMP_CHECKIN_FOLDER'], f"{booking_id}.json")
    if not os.path.exists(temp_checkin_path):
        return redirect(url_for('index'))
    
    with open(temp_checkin_path, 'r') as f:
        data = json.load(f)
    
    all_guests = data.get('guest_data', [])
    verified_guests = data.get('verified_guests_data', [])
    
    if all_guests and len(verified_guests) >= len(all_guests):
        return redirect(url_for('finalize_checkin', booking_id=booking_id))

    verified_guest_names = [g.get('name') for g in verified_guests]
    return render_template('select_main_guests.html', all_guests=all_guests, verified_guest_names=verified_guest_names, booking_id=booking_id)

@app.route('/start_guest_verification/<booking_id>/<guest_name>')
def start_guest_verification(booking_id, guest_name):
    return render_template('verify_guest_face.html', booking_id=booking_id, guest_name=guest_name)

@app.route('/check_guest_face/<booking_id>', methods=['POST'])
def check_guest_face(booking_id):
    temp_checkin_path = os.path.join(app.config['TEMP_CHECKIN_FOLDER'], f"{booking_id}.json")
    if not os.path.exists(temp_checkin_path):
        return redirect(url_for('index'))

    data = request.get_json()
    image_data = data.get('image')
    guest_name = data.get('guest_name')
    if not image_data or not guest_name:
        return redirect(url_for('index'))
    try:
        img_data = base64.b64decode(image_data.split(',')[1])
        nparr = np.frombuffer(img_data, np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    except Exception as e:
        print(f"Error decoding base64 image: {e}")
        return redirect(url_for('index'))
    face_locations = face_recognition.face_locations(rgb_frame)
    face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)
    if not face_encodings:
        flash("Could not detect a face. Please try capturing the photo again.", "error")
        return redirect(url_for('start_guest_verification', booking_id=booking_id, guest_name=guest_name))
    
    found_guest_data = find_guest_by_face(face_encodings[0])
    
    if found_guest_data:
        with open(temp_checkin_path, 'r') as f:
            data = json.load(f)
        if not any(g.get('guest_id') == found_guest_data.get('guest_id') for g in data['verified_guests_data']):
            data['verified_guests_data'].append(found_guest_data)
        with open(temp_checkin_path, 'w') as f:
            json.dump(data, f, indent=4)
        flash(f"Verified {guest_name} from database.", "info")
        return redirect(url_for('select_main_guests', booking_id=booking_id))
    else:
        with open(temp_checkin_path, 'r') as f:
            data = json.load(f)
        data['new_face_encoding'] = face_encodings[0].tolist()
        with open(temp_checkin_path, 'w') as f:
            json.dump(data, f, indent=4)
        return redirect(url_for('document_verification', booking_id=booking_id, guest_name=guest_name))

@app.route('/document_verification/<booking_id>/<guest_name>', methods=['GET', 'POST'])
def document_verification(booking_id, guest_name):
    temp_checkin_path = os.path.join(app.config['TEMP_CHECKIN_FOLDER'], f"{booking_id}.json")
    if not os.path.exists(temp_checkin_path):
        return redirect(url_for('index'))
    
    with open(temp_checkin_path, 'r') as f:
        data = json.load(f)
    
    all_guests = data.get('guest_data', [])
    guest_to_verify = next((g for g in all_guests if g['name'] == guest_name), None)
    if not guest_to_verify:
        flash("Error: Could not find guest data to verify.", "error")
        return redirect(url_for('select_main_guests', booking_id=booking_id))

    if request.method == 'POST':
        doc_type = request.form.get(f'doctype_{guest_name}')
        doc_photo_b64 = request.form.get(f'doc_photo_data_{guest_name}')
        
        if not doc_type:
            flash("Please select a document type.", "error")
            return render_template('document_upload.html', selected_guests=[guest_to_verify], booking_id=booking_id, guest_name=guest_name)
        
        if not doc_photo_b64:
            flash("Please capture a photo of your document.", "error")
            return render_template('document_upload.html', selected_guests=[guest_to_verify], booking_id=booking_id, guest_name=guest_name)
        
        filepath = None
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        try:
            img_data = base64.b64decode(doc_photo_b64.split(',')[1])
            filename = f"doc_{guest_name.replace(' ', '_')}_{uuid.uuid4()}.jpg"
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            with open(filepath, 'wb') as f:
                f.write(img_data)
        except Exception as e:
            print(f"Error decoding/saving base64 doc image for {guest_name}: {e}")
            flash("Error processing document photo. Please try again.", "error")
            return render_template('document_upload.html', selected_guests=[guest_to_verify], booking_id=booking_id, guest_name=guest_name)
        
        if filepath:
            # Validate document type using YOLO classification
            try:
                validation_result = validate_document_type(filepath, doc_type)
                
                if not validation_result.get('valid', False):
                    # Document type validation failed
                    error_message = validation_result.get('message', 'Document type validation failed')
                    
                    # Check if it's an unrecognized document (very low confidence)
                    predicted_class = validation_result.get('predicted_class', '')
                    confidence = validation_result.get('confidence', 0)
                    
                    if confidence < UNRECOGNIZED_DOCUMENT_THRESHOLD:  # Unrecognized document
                        flash(f"Unrecognized document: {error_message}", "error")
                    else:
                        flash(f"Document validation failed: {error_message}", "error")
                    
                    return render_template('document_upload.html', selected_guests=[guest_to_verify], booking_id=booking_id, guest_name=guest_name)
            except Exception as e:
                flash(f"Error during document validation: {str(e)}", "error")
                return render_template('document_upload.html', selected_guests=[guest_to_verify], booking_id=booking_id, guest_name=guest_name)
            
            # Document type validation passed, proceed with OCR
            try:
                ocr_data = process_document(filepath, doc_type)
                
                new_face_encoding = np.array(data.get('new_face_encoding'))
                new_guest_record = add_guest_to_database(new_face_encoding, guest_to_verify, ocr_data, filepath, doc_type)
                
                data['verified_guests_data'].append(new_guest_record)
                with open(temp_checkin_path, 'w') as f:
                    json.dump(data, f, indent=4)
                
                success_message = f"Successfully verified and saved identity for {guest_name}. Document validated as {validation_result.get('predicted_class', 'unknown')}."
                flash(success_message, "success")
                return redirect(url_for('select_main_guests', booking_id=booking_id))
            except Exception as e:
                flash(f"Error during document processing: {str(e)}", "error")
                return render_template('document_upload.html', selected_guests=[guest_to_verify], booking_id=booking_id, guest_name=guest_name)
    return render_template('document_upload.html', selected_guests=[guest_to_verify], booking_id=booking_id, guest_name=guest_name)

# @app.route('/finalize_checkin/<booking_id>')
# def finalize_checkin(booking_id):
#     temp_checkin_path = os.path.join(app.config['TEMP_CHECKIN_FOLDER'], f"{booking_id}.json")
#     if not os.path.exists(temp_checkin_path):
#         return redirect(url_for('index'))
    
#     with open(temp_checkin_path, 'r') as f:
#         data = json.load(f)

#     verified_guests = data.get('verified_guests_data', [])
#     all_guests = data.get('guest_data', [])
#     room_number = data.get('room_number', 'N/A')
    
#     generate_checkin_report_json(booking_id, verified_guests, all_guests, room_number)
#     add_live_checkin(booking_id, room_number, all_guests)
    
#     os.remove(temp_checkin_path)
#     return redirect(url_for('complete_checkin'))
@app.route('/finalize_checkin/<booking_id>')
def finalize_checkin(booking_id):
    """Final step to generate reports and add to live check-ins."""
    import pprint
    temp_checkin_path = os.path.join(app.config['TEMP_CHECKIN_FOLDER'], f"{booking_id}.json")
    if not os.path.exists(temp_checkin_path):
        print(f"Temp file not found: {temp_checkin_path}")
        return redirect(url_for('index'))

    with open(temp_checkin_path, 'r') as f:
        data = json.load(f)

   # pprint.pprint({"TEMP DATA": data})

    verified_guests = data.get('verified_guests_data', [])
    all_guests = data.get('guest_data', [])
    room_number = data.get('room_number', 'N/A')

    report_filepath = generate_checkin_report_json(booking_id, verified_guests, all_guests, room_number)

    with open(report_filepath, 'r') as f:
        data = json.load(f)

    # Manually build the report_data structure for the template
    report_data = {
        "booking_id": booking_id,
        "allocated_room": data.get('room_number', 'N/A'),
        "checkin_time": datetime.now().strftime("%d-%m-%y %H:%M"),
        "all_guests": data.get('guest_data', []),
        "verified_guests": data.get('verified_guests_data', [])
    }



    return render_template('final_confirmation.html', booking_id=booking_id, report_data=report_data)

@app.route('/confirm_and_complete_checkin/<booking_id>', methods=['POST'])
def confirm_and_complete_checkin(booking_id):
    temp_checkin_path = os.path.join(app.config['TEMP_CHECKIN_FOLDER'], f"{booking_id}.json")
    if not os.path.exists(temp_checkin_path):
        return redirect(url_for('index'))
    
    with open(temp_checkin_path, 'r') as f:
        data = json.load(f)

    all_guests = data.get('guest_data', [])
    room_number = data.get('room_number', 'N/A')
    
    # Add the booking to the live check-in list
    add_live_checkin(booking_id, room_number, all_guests)
    
    # Clean up the temporary file
    os.remove(temp_checkin_path)
    
    # Pass guest names as URL parameters
    if all_guests:
        guest_names = [guest.get('name', 'Guest') for guest in all_guests]
        # URL encode the names and pass them as parameters
        names_param = urllib.parse.quote(','.join(guest_names))
        return redirect(url_for('complete_checkin', names=names_param))
    else:
        return redirect(url_for('complete_checkin'))




@app.route('/complete_checkin')
def complete_checkin():
    # Get guest names from URL parameters
    names_param = request.args.get('names', '')
    guest_names = []
    
    if names_param:
        names_str = urllib.parse.unquote(names_param)
        guest_names = [name.strip() for name in names_str.split(',') if name.strip()]
    
    if guest_names:
        if len(guest_names) == 1:
            message = f"Check-in Complete! We welcome you to our hotel, {guest_names[0]}. Please enjoy your stay."
        else:
            # Multiple guests
            names_str = ", ".join(guest_names[:-1]) + f" and {guest_names[-1]}"
            message = f"Check-in Complete! We welcome you to our hotel, {names_str}. Please enjoy your stay."
    else:
        message = "Check-in Complete! We welcome you to our hotel. Please enjoy your stay."
    
    redirect_url = url_for('index')
    session.clear()
    return render_template('redirect_page.html', message=message, redirect_url=redirect_url)

@app.route('/no_booking')
def no_booking():
    message = "Please proceed to the front desk for booking."
    redirect_url = url_for('index')
    return render_template('redirect_page.html', message=message, redirect_url=redirect_url)

@app.route('/face_exists_error')
def face_exists_error():
    message = "Registration failed. One of the faces you submitted already exists in our system."
    redirect_url = url_for('index')
    return render_template('redirect_page.html', message=message, redirect_url=redirect_url)

@app.route('/checkout')
def checkout():
    return redirect(url_for('checkout_face_scan'))

# --- Old Registration Flow ---
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        global registration_info
        registration_info = {
            "name": request.form.get('name'),
            "dob": request.form.get('dob'),
            "gender": request.form.get('gender')
        }
        return redirect(url_for('capture_for_registration'))
    return render_template('register_form.html')

@app.route('/capture_for_registration')
def capture_for_registration():
    return render_template('capture.html')

@app.route('/run_new_registration', methods=['POST'])
def run_new_registration():
    global registration_info
    data = request.get_json()
    image_data = data.get('image')
    if not image_data or not registration_info:
        return redirect(url_for('index'))
    try:
        img_data = base64.b64decode(image_data.split(',')[1])
        nparr = np.frombuffer(img_data, np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    except Exception as e:
        print(f"Error decoding base64 image during new registration: {e}")
        return redirect(url_for('index'))
    message = add_new_user(frame, registration_info)
    if message == "face_exists":
        return redirect(url_for('face_exists_error'))

    return render_template(
        'redirect_page.html',
        message=message,
        redirect_url=url_for('index')
    )

@app.route('/booking_confirmation', methods=['POST'])
def booking_confirmation():
    """
    Displays the final confirmation page before booking.
    """
    room_details = {
        "room_number": request.form.get('room_number'),
        "category": request.form.get('category'),
        "capacity": request.form.get('capacity'),
        "price_per_night": request.form.get('price_per_night'),
        "currency": request.form.get('currency')
    }
    search_details = {
        "check_in": request.form.get('check_in'),
        "check_out": request.form.get('check_out'),
        "guests": request.form.get('guests')
    }
    return render_template('booking_confirmation.html', room=room_details, search=search_details)

@app.route('/process_booking', methods=['POST'])
def process_booking():
    """
    Processes the final booking, generates a booking ID, and updates the PDF.
    """
    # Generate a new, unique booking ID
    booking_id = f"BK{random.randint(10000, 99999)}"
    
    # Gather all data from the form
    new_booking = {
        "Booking ID": booking_id,
        "Booking Under Name": request.form.get('booking_name'),
        "Booking Date": datetime.now().strftime("%Y-%m-%d"),
        "Check In": request.form.get('check_in'),
        "Check Out": request.form.get('check_out'),
        "Account Number": request.form.get('mobile_number'),
        "Num People": request.form.get('guests'),
        "Alloted Room": request.form.get('room_number')
    }
    
    # Use the new module to add the booking to the PDF
    add_booking_to_pdf(new_booking)
    add_booking_to_room(new_booking)
    
    return render_template('booking_successful.html', booking_details=new_booking)


@app.route('/view_room/<room_number>')
def view_room(room_number):
    """
    Finds and displays images for a specific room.
    """
    image_paths = []
    try:
        # Construct the physical path to the directory
        image_folder_path = os.path.join(app.static_folder, 'rooms', room_number)
        
        if os.path.isdir(image_folder_path):
            # List all files and filter for common image extensions
            all_files = os.listdir(image_folder_path)
            image_files = [f for f in all_files if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
            
            # Create web-accessible paths for the template
            for img_file in image_files:
                web_path = os.path.join('rooms', room_number, img_file).replace('\\', '/')
                image_paths.append(web_path)

    except Exception as e:
        print(f"Error finding room images for {room_number}: {e}")

    return render_template('view_room.html', room_number=room_number, image_paths=image_paths)


# if __name__ == '__main__':
#     # Create necessary folders on startup
#     os.makedirs('uploads', exist_ok=True)
#     os.makedirs('temp_checkins', exist_ok=True)
#     app.run(host='0.0.0.0', port=5000, debug=True)


if __name__ == '__main__':
    import os
    
    # Create required folders
    os.makedirs('uploads', exist_ok=True)
    os.makedirs('temp_checkins', exist_ok=True)
    os.makedirs('static/checkins', exist_ok=True)

    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)

    