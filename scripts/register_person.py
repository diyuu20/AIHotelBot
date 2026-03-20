import cv2
import face_recognition
import pickle
import sqlite3
import os
import uuid

ENCODINGS_FILE = "encodings.pickle"
DB_FILE = "face_db.sqlite"

def create_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS persons (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            mobile TEXT,
            email TEXT,
            point_of_contact TEXT,
            purpose TEXT
        )
    ''')
    conn.commit()
    conn.close()

def get_user_input():
    print("📝 Enter visitor details:")
    name = input("Name: ").strip()
    mobile = input("Mobile Number: ").strip()
    email = input("Email: ").strip()
    poc = input("Point of Contact: ").strip()
    purpose = input("Purpose of Visit: ").strip()
    return name, mobile, email, poc, purpose

def capture_face_image():
    print("📸 Capturing face. Look at the camera...")
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    face_encoding = None

    while True:
        ret, frame = cap.read()
        if not ret:
            print("❌ Failed to capture image.")
            break

        cv2.imshow("Capture - Press 'c' to capture, 'q' to quit", frame)
        key = cv2.waitKey(1)

        if key & 0xFF == ord('c'):
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            boxes = face_recognition.face_locations(rgb)
            encodings = face_recognition.face_encodings(rgb, boxes)

            if len(encodings) == 1:
                face_encoding = encodings[0]
                print("✅ Face captured successfully.")
            elif len(encodings) == 0:
                print("⚠️ No face found. Try again.")
            else:
                print("⚠️ Multiple faces found. Please ensure only one person is in frame.")
            break

        elif key & 0xFF == ord('q'):
            print("❌ Capture cancelled.")
            break

    cap.release()
    cv2.destroyAllWindows()
    return face_encoding

def save_to_database(person_id, name, mobile, email, poc, purpose):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO persons (id, name, mobile, email, point_of_contact, purpose)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (person_id, name, mobile, email, poc, purpose))
    conn.commit()
    conn.close()

def update_encodings(name, face_encoding):
    data = {"encodings": [], "names": []}
    if os.path.exists(ENCODINGS_FILE):
        with open(ENCODINGS_FILE, "rb") as f:
            data = pickle.load(f)

    data["encodings"].append(face_encoding)
    data["names"].append(name)

    with open(ENCODINGS_FILE, "wb") as f:
        pickle.dump(data, f)

def register_person():
    create_db()
    name, mobile, email, poc, purpose = get_user_input()
    face_encoding = capture_face_image()

    if face_encoding is None:
        print("❌ Registration failed. No valid face captured.")
        return

    person_id = str(uuid.uuid4())  # 🔑 Unique ID
    save_to_database(person_id, name, mobile, email, poc, purpose)
    update_encodings(name, face_encoding)

    print(f"✅ Registered successfully with ID: {person_id}")

if __name__ == "__main__":
    register_person()
