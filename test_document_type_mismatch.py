"""
Test script to demonstrate document type mismatch handling
"""

from document_classifier import validate_document_type

def test_document_type_mismatch():
    """Test the document type mismatch scenarios."""
    
    print("🔍 Testing Document Type Mismatch Scenarios")
    print("=" * 60)
    
    # Test cases with mismatched document types
    test_cases = [
        {
            "image": "uploads/doc_ABHISHEK_226c7275-08d1-4e5c-90f9-1af4c7d11ed6.jpg",  # This is an Aadhaar
            "selected_type": "passport",  # User selected passport but image is Aadhaar
            "description": "User selects Passport but uploads Aadhaar"
        },
        {
            "image": "uploads/doc_Aqeel_Memon_passport.jpg",  # This is a Passport
            "selected_type": "aadhaar",  # User selected Aadhaar but image is Passport
            "description": "User selects Aadhaar but uploads Passport"
        },
        {
            "image": "uploads/doc_Dixit_shah_adhaar_front.jpg",  # This is an Aadhaar
            "selected_type": "driving_licence",  # User selected Driving Licence but image is Aadhaar
            "description": "User selects Driving Licence but uploads Aadhaar"
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📋 Test Case {i}: {test_case['description']}")
        print(f"   Image: {test_case['image']}")
        print(f"   User Selected: {test_case['selected_type']}")
        
        result = validate_document_type(test_case['image'], test_case['selected_type'])
        
        print(f"   Result: {'✅ VALID' if result.get('valid') else '❌ INVALID'}")
        print(f"   Predicted Class: {result.get('predicted_class', 'Unknown')}")
        print(f"   Confidence: {result.get('confidence', 0):.2%}")
        print(f"   Message: {result.get('message', 'No message')}")
    
    print("\n" + "=" * 60)
    print("📝 Document Type Validation Logic:")
    print("1. First check: Does predicted class match selected document type?")
    print("   - If NO → Show 'Document type mismatch' error")
    print("   - If YES → Continue to confidence check")
    print()
    print("2. Second check: Is confidence ≥ 90%?")
    print("   - If NO → Show 'Low confidence' error")
    print("   - If YES → Document accepted")
    print()
    print("💡 This ensures users can only proceed with the correct document type!")

if __name__ == "__main__":
    test_document_type_mismatch()
