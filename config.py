# config.py

# --- File Paths ---
# This is the primary database for the simple check-in recognition.
ENCODINGS_FILE = "encodings.pickle"
# This is the directory where new user photos are saved for the simple check-in.
DATASET_PATH = "dataset"
# This is the new, separate database for fully verified guests with document details.
GUEST_DB_FILE = "guest_database.json"



DISTANCE_THRESHOLD = 0.5

PROCESSING_IMAGE_WIDTH = 600

# --- Document Classification Configuration ---
# Path to the YOLO model for document classification
# Set this to the path of your trained YOLO model file
YOLO_MODEL_PATH = "model/Id_Classifier.pt"  # Replace with actual model path, e.g., "models/document_classifier.pt"

# Confidence threshold for document type validation
DOCUMENT_VALIDATION_CONFIDENCE_THRESHOLD = 0.9  # 90% confidence required

# Threshold below which document is considered unrecognized
UNRECOGNIZED_DOCUMENT_THRESHOLD = 0.5  # 30% - below this is considered unrecognized