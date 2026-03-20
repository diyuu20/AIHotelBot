"""
Test script to demonstrate unrecognized document handling
"""

from document_classifier import validate_document_type
from config import UNRECOGNIZED_DOCUMENT_THRESHOLD

def test_unrecognized_document():
    """Test the unrecognized document scenario with very low confidence."""
    
    print("🔍 Testing Unrecognized Document Scenario")
    print("=" * 50)
    
    # Simulate a very low confidence result (like 15%)
    # This would happen when the model can't properly identify the document
    print(f"Unrecognized Document Threshold: {UNRECOGNIZED_DOCUMENT_THRESHOLD:.0%}")
    print()
    
    # Test with a real image that might have low confidence
    test_image = "uploads/doc_Aqeel_Memon_passport.jpg"  # This had 60% confidence in our test
    
    print("📋 Testing with existing image (should show low confidence, not unrecognized):")
    result = validate_document_type(test_image, "passport")
    
    print(f"   Result: {'✅ VALID' if result.get('valid') else '❌ INVALID'}")
    print(f"   Predicted Class: {result.get('predicted_class', 'Unknown')}")
    print(f"   Confidence: {result.get('confidence', 0):.2%}")
    print(f"   Message: {result.get('message', 'No message')}")
    
    print("\n" + "=" * 50)
    print("📝 Unrecognized Document Logic:")
    print(f"- Confidence ≥ 90%: Document accepted")
    print(f"- 50% ≤ Confidence < 90%: Low confidence error")
    print(f"- Confidence < 50%: Unrecognized document error")
    print()
    print("💡 To trigger 'unrecognized document' error:")
    print("   - Upload a blurry, unclear, or non-document image")
    print("   - The model will return very low confidence (< 50%)")
    print("   - System will show 'Unrecognized document' error and reload page")

if __name__ == "__main__":
    test_unrecognized_document()
