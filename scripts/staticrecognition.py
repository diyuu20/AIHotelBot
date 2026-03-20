import cv2
import face_recognition
import pickle
import os
import time

ENCODINGS_FILE = "encodings.pickle"

def load_encodings():
    if not os.path.exists(ENCODINGS_FILE):
        print("❌ No encodings file found.")
        return None
    with open(ENCODINGS_FILE, "rb") as f:
        return pickle.load(f)

def recognize_person(frame, data):
    # Resize frame for faster processing
    small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
    rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

    face_locations = face_recognition.face_locations(rgb_small_frame)
    face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)


    for face_encoding in face_encodings:
        matches = face_recognition.compare_faces(data["encodings"], face_encoding)

        if True in matches:
            matched_idxs = [i for i, match in enumerate(matches) if match]
            counts = {}
            for i in matched_idxs:
                name_match = data["names"][i]
                counts[name_match] = counts.get(name_match, 0) + 1
            name = max(counts, key=counts.get)

        return name


def recognize_from_camera():
    data = load_encodings()
    if not data:
        return "No encodings loaded"

    video_capture = cv2.VideoCapture(0, cv2.CAP_DSHOW)

    if not video_capture.isOpened():
        print("❌ Failed to open webcam.")
        

    print("🎥 Showing live preview. Capturing photo in 5 seconds...")
    start_time = time.time()
    captured_frame = None

    while True:
        ret, frame = video_capture.read()
        if not ret:
            print("❌ Failed to read frame.")
            break

        cv2.imshow("📸 Live Preview - Hold Still", frame)

        # Capture frame at 5 seconds
        if time.time() - start_time >= 3 and captured_frame is None:
            captured_frame = frame.copy()

        # Break loop after 6 seconds (1s extra to show the captured frame briefly)
        if time.time() - start_time > 6:
            break

        # Allow manual break
        if cv2.waitKey(1) & 0xFF == ord('q'):
            print("❌ User exited early.")
            break

    video_capture.release()
    cv2.destroyAllWindows()


    name = recognize_person(captured_frame, data)
    # print(f"👤 Recognized person: {name}")
    return name

