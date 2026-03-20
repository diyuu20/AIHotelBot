import cv2
import face_recognition
import pickle
import os
import base64
import numpy as np
import uuid
import shutil
from config import DATASET_PATH, ENCODINGS_FILE, DISTANCE_THRESHOLD, PROCESSING_IMAGE_WIDTH

def resize_image(frame):
    """
    Resizes an image to a standard width for efficient processing, maintaining aspect ratio.
    """
    h, w, _ = frame.shape
    if w > PROCESSING_IMAGE_WIDTH:
        ratio = PROCESSING_IMAGE_WIDTH / float(w)
        new_h = int(h * ratio)
        return cv2.resize(frame, (PROCESSING_IMAGE_WIDTH, new_h))
    return frame

# def find_existing_face_encoding(new_encoding_to_check):
#     """
#     Checks if a face exists. If so, returns the existing encoding. Otherwise, returns None.
#     """
#     try:
#         with open(ENCODINGS_FILE, "rb") as f:
#             data = pickle.load(f)
#     except FileNotFoundError:
#         return None
    
#     if not data.get("encodings"):
#         return None

#     face_distances = face_recognition.face_distance(data["encodings"], new_encoding_to_check)
    
#     if np.any(face_distances <= DISTANCE_THRESHOLD):
#         best_match_index = np.argmin(face_distances)
#         return data["encodings"][best_match_index] # Return the existing encoding
    
#     return None

def find_existing_face_encoding(new_encoding_to_check):
    """
    Checks if a face exists. If so, returns the existing encoding. Otherwise, returns None.
    """
    if not os.path.exists(ENCODINGS_FILE):
        return None

    try:
        with open(ENCODINGS_FILE, "rb") as f:
            data = pickle.load(f)
    except Exception as e:
        print("❌ Corrupted encodings file detected. Deleting it.")
        print("Reason:", e)
        try:
            os.remove(ENCODINGS_FILE)
        except:
            pass
        return None

    if not data.get("encodings"):
        return None

    face_distances = face_recognition.face_distance(
        data["encodings"], new_encoding_to_check
    )

    if np.any(face_distances <= DISTANCE_THRESHOLD):
        best_match_index = np.argmin(face_distances)
        return data["encodings"][best_match_index]

    return None


def _safe_save_encodings(data):
    """
    Safely saves the encodings data to a temporary file before renaming it.
    """
    temp_file = ENCODINGS_FILE + ".tmp"
    try:
        with open(temp_file, "wb") as f:
            f.write(pickle.dumps(data))
        shutil.move(temp_file, ENCODINGS_FILE)
    except Exception as e:
        print(f"❌  Failed to save encodings file safely: {e}")
        if os.path.exists(temp_file):
            os.remove(temp_file)

def add_new_user(frame, user_info):
    """
    Handles the 'old' registration flow for an unrecognized user.
    """
    user_name = user_info.get("name")
    if not user_name:
        return "Error: User name is required for registration."

    resized_frame = resize_image(frame)
    rgb_image = cv2.cvtColor(resized_frame, cv2.COLOR_BGR2RGB)
    boxes = face_recognition.face_locations(rgb_image, model="hog")
    if not boxes:
        return "Registration Error: No face could be detected."
        
    new_encodings = face_recognition.face_encodings(rgb_image, boxes)
    if not new_encodings:
        return "Registration Error: Could not create a face encoding."

    existing_encoding = find_existing_face_encoding(new_encodings[0])
    if existing_encoding is not None:
        print(f"❌ Registration failed for {user_name}. Face already exists.")
        return "face_exists"
    
    dir_name = "".join(c for c in user_name if c.isalnum() or c in (' ', '_')).rstrip()
    user_dir = os.path.join(DATASET_PATH, dir_name)
    os.makedirs(user_dir, exist_ok=True)
    
    unique_id = str(uuid.uuid4())[:8]
    img_path = os.path.join(user_dir, f"{dir_name}_{unique_id}.jpg")
    cv2.imwrite(img_path, frame)

    try:
        with open(ENCODINGS_FILE, "rb") as f:
            data = pickle.load(f)
    except FileNotFoundError:
        data = {"encodings": [], "names": []}
        
    data["encodings"].append(new_encodings[0])
    data["names"].append(user_name)
    _safe_save_encodings(data)
    
    print(f"✅ Successfully registered new user: {user_name}")
    return f"Registration successful for {user_name}! You can now proceed to check in."


def register_guest(user_name, base64_image_data):
    """
    Saves a guest's photo and adds their encoding.
    Returns a tuple: (status, result_data)
    """
    if not user_name or not base64_image_data:
        return ("error", None)

    try:
        img_data = base64.b64decode(base64_image_data.split(',')[1])
        nparr = np.frombuffer(img_data, np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if frame is None: raise ValueError("Failed to decode image")
    except Exception as e:
        print(f"Error decoding base64 image: {e}")
        return ("error", None)

    resized_frame = resize_image(frame)
    rgb_image = cv2.cvtColor(resized_frame, cv2.COLOR_BGR2RGB)
    boxes = face_recognition.face_locations(rgb_image, model="hog")
    if not boxes:
        return ("error", None)
        
    new_encodings = face_recognition.face_encodings(rgb_image, boxes)
    if not new_encodings:
        return ("error", None)

    existing_encoding = find_existing_face_encoding(new_encodings[0])
    if existing_encoding is not None:
        print(f"Found existing face for {user_name}.")
        # For pre-existing guests, we don't save a new photo, so path is 'pre_existing'
        return ("face_exists", (existing_encoding, 'pre_existing'))

    dir_name = "".join(c for c in user_name if c.isalnum() or c in (' ', '_')).rstrip()
    user_dir = os.path.join('uploads', 'guest_photos') 
    os.makedirs(user_dir, exist_ok=True)
    
    unique_id = str(uuid.uuid4())[:8]
    img_path = os.path.join(user_dir, f"{dir_name}_{unique_id}.jpg")
    cv2.imwrite(img_path, frame)

    try:
        with open(ENCODINGS_FILE, "rb") as f:
            data = pickle.load(f)
    except FileNotFoundError:
        data = {"encodings": [], "names": []}
        
    data["encodings"].append(new_encodings[0])
    data["names"].append(user_name)
    _safe_save_encodings(data)
    
    print(f"✅ Successfully registered guest: {user_name}")
    return ("success", (img_path, new_encodings[0]))
