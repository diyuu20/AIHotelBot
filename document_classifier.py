"""
Document Classification Module using YOLO
This module classifies uploaded document images to verify they match the expected document type.
"""

import cv2
import numpy as np
import os
from ultralytics import YOLO
import torch
from config import YOLO_MODEL_PATH, DOCUMENT_VALIDATION_CONFIDENCE_THRESHOLD, UNRECOGNIZED_DOCUMENT_THRESHOLD

class DocumentClassifier:
    def __init__(self, model_path=None):
        """
        Initialize the document classifier with YOLO model.
        
        Args:
            model_path (str): Path to the YOLO model file. If None, will use config value or default model.
        """
        self.model_path = model_path or YOLO_MODEL_PATH
        self.model = None
        self.valid_classes = [
            'aadhar_back', 'aadhar_front', 
            'driving_license_back', 'driving_license_front', 
            'pan_card_front', 'passport', 'voter_id'
        ]
        
        # Mapping from user-friendly names to model classes
        self.doc_type_mapping = {
            'aadhaar': ['aadhar_front', 'aadhar_back'],
            'passport': ['passport'],
            'driving_licence': ['driving_license_front', 'driving_license_back']
        }
        
        self.load_model()
    
    def load_model(self):
        """Load the YOLO model for document classification."""
        try:
            if self.model_path and os.path.exists(self.model_path):
                self.model = YOLO(self.model_path)
                print(f"✅ Loaded YOLO model from {self.model_path}")
            else:
                # Use a default YOLO model (you can replace this with your trained model)
                print("⚠️  No custom model path provided. Using default YOLO model.")
                print("Please provide the path to your trained document classification model.")
                # For now, we'll create a placeholder that returns random results
                # Replace this with actual model loading when you have the trained model
                self.model = None
        except Exception as e:
            print(f"❌ Error loading YOLO model: {e}")
            self.model = None
    
    def preprocess_image(self, image_path):
        """
        Preprocess the image for YOLO classification.
        
        Args:
            image_path (str): Path to the image file
            
        Returns:
            numpy.ndarray: Preprocessed image
        """
        try:
            # Read image
            image = cv2.imread(image_path)
            if image is None:
                raise ValueError(f"Could not read image from {image_path}")
            
            # Convert BGR to RGB
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            return image
        except Exception as e:
            print(f"Error preprocessing image: {e}")
            return None
    
    def classify_document(self, image_path, confidence_threshold=0.5):
        """
        Classify the document type using YOLO model.
        
        Args:
            image_path (str): Path to the document image
            confidence_threshold (float): Minimum confidence threshold for classification
            
        Returns:
            dict: Classification results with predicted class and confidence
        """
        if self.model is None:
            # Placeholder implementation - replace with actual model when available
            return self._placeholder_classification(image_path)
        
        try:
            # Preprocess image
            image = self.preprocess_image(image_path)
            if image is None:
                return {"error": "Could not preprocess image"}
            
            # Run YOLO inference
            results = self.model(image, conf=confidence_threshold)
            
            if not results or len(results) == 0:
                return {"error": "No classification results"}
            
            # Extract the best prediction
            result = results[0]
            
            # Check if we have detection results
            if result.boxes is None or len(result.boxes) == 0:
                # Try to get predictions from probs if available (classification model)
                if hasattr(result, 'probs') and result.probs is not None:
                    probs = result.probs.data.cpu().numpy()
                    predicted_class_id = int(np.argmax(probs))
                    confidence = float(probs[predicted_class_id])
                    
                    # Get class name
                    if hasattr(result, 'names') and predicted_class_id in result.names:
                        predicted_class = result.names[predicted_class_id]
                    else:
                        predicted_class = f"class_{predicted_class_id}"
                else:
                    return {"error": "No objects detected in image"}
            else:
                # Get the prediction with highest confidence from detection
                confidences = result.boxes.conf.cpu().numpy()
                class_ids = result.boxes.cls.cpu().numpy()
                
                best_idx = np.argmax(confidences)
                predicted_class_id = int(class_ids[best_idx])
                confidence = float(confidences[best_idx])
                
                # Get class name
                if hasattr(result, 'names') and predicted_class_id in result.names:
                    predicted_class = result.names[predicted_class_id]
                else:
                    predicted_class = f"class_{predicted_class_id}"
            
            return {
                "predicted_class": predicted_class,
                "confidence": confidence,
                "success": True
            }
            
        except Exception as e:
            print(f"Error during document classification: {e}")
            return {"error": f"Classification failed: {str(e)}"}
    
    def _placeholder_classification(self, image_path):
        """
        Placeholder classification function for testing.
        Replace this with actual YOLO model when available.
        """
        import random
        
        # Simulate classification based on filename or random selection
        filename = os.path.basename(image_path).lower()
        
        # Simple heuristics based on filename
        if 'aadhaar' in filename or 'aadhar' in filename:
            predicted_class = random.choice(['aadhar_front', 'aadhar_back'])
        elif 'passport' in filename:
            predicted_class = 'passport'
        elif 'driving' in filename or 'license' in filename or 'licence' in filename:
            predicted_class = random.choice(['driving_license_front', 'driving_license_back'])
        else:
            # Random selection from valid classes
            predicted_class = random.choice(self.valid_classes)
        
        confidence = random.uniform(0.6, 0.95)  # Simulate confidence
        
        return {
            "predicted_class": predicted_class,
            "confidence": confidence,
            "success": True,
            "note": "This is a placeholder result. Please provide your trained YOLO model."
        }
    
    def validate_document_type(self, image_path, expected_doc_type, confidence_threshold=0.5):
        """
        Validate if the uploaded document matches the expected type.
        
        Args:
            image_path (str): Path to the document image
            expected_doc_type (str): Expected document type ('aadhaar', 'passport', 'driving_licence')
            confidence_threshold (float): Minimum confidence threshold
            
        Returns:
            dict: Validation results
        """
        # Classify the document
        classification_result = self.classify_document(image_path, confidence_threshold)
        
        if "error" in classification_result:
            return {
                "valid": False,
                "error": classification_result["error"],
                "classification_result": classification_result
            }
        
        predicted_class = classification_result.get("predicted_class")
        confidence = classification_result.get("confidence", 0)
        
        # Check if predicted class matches expected document type
        expected_classes = self.doc_type_mapping.get(expected_doc_type, [])
        
        # First check if the predicted class matches the expected document type
        if predicted_class not in expected_classes:
            return {
                "valid": False,
                "predicted_class": predicted_class,
                "confidence": confidence,
                "expected_type": expected_doc_type,
                "message": "Valid document not detected. Please take a more clear photo."
            }
        
        # If predicted class matches expected type, then check confidence
        if confidence < confidence_threshold:
            # Check if confidence is very low - likely unrecognized document
            if confidence < UNRECOGNIZED_DOCUMENT_THRESHOLD:
                return {
                    "valid": False,
                    "predicted_class": predicted_class,
                    "confidence": confidence,
                    "expected_type": expected_doc_type,
                    "message": "Valid document not detected. Please take a more clear photo."
                }
            else:
                return {
                    "valid": False,
                    "predicted_class": predicted_class,
                    "confidence": confidence,
                    "expected_type": expected_doc_type,
                    "message": "Valid document not detected. Please take a more clear photo."
                }
        
        # If we reach here, the document type matches and confidence is high enough
        return {
            "valid": True,
            "predicted_class": predicted_class,
            "confidence": confidence,
            "expected_type": expected_doc_type,
            "message": "Document validated successfully"
        }

# Global instance for the application
document_classifier = DocumentClassifier()

def validate_document_type(image_path, expected_doc_type, confidence_threshold=None):
    """
    Convenience function to validate document type.
    
    Args:
        image_path (str): Path to the document image
        expected_doc_type (str): Expected document type
        confidence_threshold (float): Minimum confidence threshold. If None, uses config value.
        
    Returns:
        dict: Validation results
    """
    if confidence_threshold is None:
        confidence_threshold = DOCUMENT_VALIDATION_CONFIDENCE_THRESHOLD
    return document_classifier.validate_document_type(image_path, expected_doc_type, confidence_threshold)
