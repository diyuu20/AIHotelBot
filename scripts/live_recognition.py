import cv2
import face_recognition
import pickle
import os

ENCODINGS_FILE = "encodings.pickle"

def load_encodings():
    if not os.path.exists(ENCODINGS_FILE):
        print("❌ No encodings file found.")
        return None
    with open(ENCODINGS_FILE, "rb") as f:
        return pickle.load(f)

def main():
    data = load_encodings()
    if not data:
        return

    # Start webcam with DirectShow backend for Windows stability
    video_capture = cv2.VideoCapture(0, cv2.CAP_DSHOW)

    print("🎥 Starting webcam. Press 'q' to quit.")

    while True:
        ret, frame = video_capture.read()
        if not ret:
            print("❌ Failed to read from webcam.")
            break

        # Resize frame to 1/4 size for faster processing
        small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
        rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

        face_locations = face_recognition.face_locations(rgb_small_frame)
        face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

        for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
            matches = face_recognition.compare_faces(data["encodings"], face_encoding)
            name = "Unknown"

            if True in matches:
                matched_idxs = [i for i, match in enumerate(matches) if match]
                counts = {}
                for i in matched_idxs:
                    name_match = data["names"][i]
                    counts[name_match] = counts.get(name_match, 0) + 1
                name = max(counts, key=counts.get)

            # Scale back up face locations
            top *= 4
            right *= 4
            bottom *= 4
            left *= 4

            # Draw rectangle and label
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
            cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 255, 0), cv2.FILLED)
            cv2.putText(frame, name, (left + 6, bottom - 6),
                        cv2.FONT_HERSHEY_DUPLEX, 0.75, (0, 0, 0), 1)

        cv2.imshow("🔍 Live Face Recognition - Press 'q' to quit", frame)

        # Quit on 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    video_capture.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
