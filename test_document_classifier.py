"""
Test script for the Document Classification Module
This script demonstrates how to use the document classifier for testing purposes.
"""

import os
from document_classifier import validate_document_type, document_classifier

def test_document_classification():
    """Test the document classification functionality."""
    
    print("🔍 Document Classification Test")
    print("=" * 50)
    
    # Test with a sample image (you can replace this with actual document images)
    test_images = [
        "uploads/doc_ABHISHEK_226c7275-08d1-4e5c-90f9-1af4c7d11ed6.jpg",
        "uploads/doc_Aqeel_Memon_passport.jpg",
        "uploads/doc_Dixit_shah_adhaar_front.jpg"
    ]
    
    test_cases = [
        {"image": test_images[0], "expected_type": "aadhaar", "description": "Aadhaar Card Test"},
        {"image": test_images[1], "expected_type": "passport", "description": "Passport Test"},
        {"image": test_images[2], "expected_type": "aadhaar", "description": "Aadhaar Front Test"}
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📋 Test Case {i}: {test_case['description']}")
        print(f"   Image: {test_case['image']}")
        print(f"   Expected Type: {test_case['expected_type']}")
        
        if os.path.exists(test_case['image']):
            # Test document validation
            result = validate_document_type(
                test_case['image'], 
                test_case['expected_type']
            )
            
            print(f"   Result: {'✅ VALID' if result.get('valid') else '❌ INVALID'}")
            print(f"   Predicted Class: {result.get('predicted_class', 'Unknown')}")
            print(f"   Confidence: {result.get('confidence', 0):.2%}")
            print(f"   Message: {result.get('message', 'No message')}")
            
            if 'error' in result:
                print(f"   Error: {result['error']}")
        else:
            print(f"   ⚠️  Image file not found: {test_case['image']}")
    
    print("\n" + "=" * 50)
    print("📝 Notes:")
    print("- This test uses placeholder classification if no YOLO model is provided")
    print("- To use your trained YOLO model, update YOLO_MODEL_PATH in config.py")
    print("- The classifier supports: aadhaar, passport, driving_licence")
    print("- Valid classes: aadhar_front, aadhar_back, passport, driving_license_front, driving_license_back")

def test_classifier_info():
    """Display information about the document classifier."""
    
    print("\n🔧 Document Classifier Information")
    print("=" * 50)
    print(f"Model Path: {document_classifier.model_path or 'Not specified'}")
    print(f"Model Loaded: {'Yes' if document_classifier.model else 'No (using placeholder)'}")
    print(f"Valid Classes: {', '.join(document_classifier.valid_classes)}")
    print(f"Document Type Mapping:")
    for doc_type, classes in document_classifier.doc_type_mapping.items():
        print(f"  {doc_type}: {', '.join(classes)}")

if __name__ == "__main__":
    test_classifier_info()
    test_document_classification()



