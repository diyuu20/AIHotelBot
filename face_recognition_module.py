import cv2
import face_recognition
import pickle
import os
import numpy as np
from config import ENCODINGS_FILE, DISTANCE_THRESHOLD, PROCESSING_IMAGE_WIDTH

def load_encodings():
    """
    Safely loads known face encodings from the pickle file.
    Returns None if the file doesn't exist or is empty.
    """
    try:
        with open(ENCODINGS_FILE, "rb") as f:
            data = pickle.load(f)
            # Ensure the file is not empty and has the correct structure
            if "encodings" in data and data["encodings"]:
                return data
            else:
                print("⚠️  Encodings file is empty or malformed.")
                return None
    except FileNotFoundError:
        print(f"❌  Error: Encodings file not found at '{ENCODINGS_FILE}'")
        return None
    except Exception as e:
        print(f"❌  An error occurred while loading encodings: {e}")
        return None

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

def recognize_person(frame, data):
    """
    Recognizes a person in a frame using face distance for higher accuracy and efficiency.
    """
    if not data or "encodings" not in data:
        return "No encodings loaded"

    # 1. Efficiency: Resize the image for faster processing
    resized_frame = resize_image(frame)
    
    # 2. Convert to RGB, which is required by the library
    rgb_frame = cv2.cvtColor(resized_frame, cv2.COLOR_BGR2RGB)
    
    # 3. Find all faces and their encodings in the current frame
    face_locations = face_recognition.face_locations(rgb_frame)
    if not face_locations:
        return "No face captured."
        
    face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

    name = "Unknown"

    # 4. Loop through each face found in the frame
    for face_encoding in face_encodings:
        # Compare this face to all known faces using a distance metric
        face_distances = face_recognition.face_distance(data["encodings"], face_encoding)
        
        # Find the best match (the one with the smallest distance)
        best_match_index = np.argmin(face_distances)
        
        # 5. Robustness: Check if the best match is within our defined threshold
        if face_distances[best_match_index] <= DISTANCE_THRESHOLD:
            name = data["names"][best_match_index]
            print(f"✅  Recognition successful: Found {name} with distance {face_distances[best_match_index]:.2f}")
            break # Stop after finding one confident match

    return name
