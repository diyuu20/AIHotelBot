"""
Test script to verify URL parameter handling for guest names
"""

import urllib.parse

def test_url_parameter_handling():
    """Test the URL parameter encoding and decoding for guest names."""
    
    print("🔗 Testing URL Parameter Handling for Guest Names")
    print("=" * 60)
    
    # Test cases for different guest scenarios
    test_cases = [
        {
            "guest_names": ["John Doe"],
            "description": "Single guest"
        },
        {
            "guest_names": ["John Doe", "Jane Smith"],
            "description": "Two guests"
        },
        {
            "guest_names": ["John Doe", "Jane Smith", "Bob Johnson"],
            "description": "Three guests"
        },
        {
            "guest_names": ["John Doe", "Jane Smith", "Bob Johnson", "Alice Brown"],
            "description": "Four guests"
        },
        {
            "guest_names": ["John O'Connor", "Mary-Jane Smith"],
            "description": "Names with special characters"
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📋 Test Case {i}: {test_case['description']}")
        print(f"   Original Names: {test_case['guest_names']}")
        
        # Simulate the encoding process (from confirm_and_complete_checkin)
        guest_names = test_case['guest_names']
        names_param = urllib.parse.quote(','.join(guest_names))
        print(f"   URL Encoded: {names_param}")
        
        # Simulate the decoding process (from complete_checkin)
        names_str = urllib.parse.unquote(names_param)
        decoded_names = [name.strip() for name in names_str.split(',') if name.strip()]
        print(f"   Decoded Names: {decoded_names}")
        
        # Verify they match
        if guest_names == decoded_names:
            print("   ✅ Encoding/Decoding successful")
        else:
            print("   ❌ Encoding/Decoding failed")
        
        # Generate the final message
        if decoded_names:
            if len(decoded_names) == 1:
                message = f"Check-in Complete! We welcome you to our hotel, {decoded_names[0]}. Please enjoy your stay."
            else:
                names_str = ", ".join(decoded_names[:-1]) + f" and {decoded_names[-1]}"
                message = f"Check-in Complete! We welcome you to our hotel, {names_str}. Please enjoy your stay."
        else:
            message = "Check-in Complete! We welcome you to our hotel. Please enjoy your stay."
        
        print(f"   Final Message: {message}")
    
    print("\n" + "=" * 60)
    print("📝 URL Parameter Flow:")
    print("1. Guest names are collected during check-in")
    print("2. Names are URL-encoded and passed as parameters")
    print("3. Names are URL-decoded in the completion page")
    print("4. Personalized message is generated")
    print()
    print("💡 This approach ensures guest names are preserved through the redirect!")

if __name__ == "__main__":
    test_url_parameter_handling()
