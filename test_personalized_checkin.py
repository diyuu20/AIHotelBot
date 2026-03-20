"""
Test script to demonstrate personalized check-in completion messages
"""

def test_personalized_messages():
    """Test the personalized check-in completion messages."""
    
    print("🏨 Testing Personalized Check-in Completion Messages")
    print("=" * 60)
    
    # Test cases for different guest scenarios
    test_cases = [
        {
            "guest_names": ["John Doe"],
            "description": "Single guest check-in"
        },
        {
            "guest_names": ["John Doe", "Jane Smith"],
            "description": "Two guests check-in"
        },
        {
            "guest_names": ["John Doe", "Jane Smith", "Bob Johnson"],
            "description": "Three guests check-in"
        },
        {
            "guest_names": ["John Doe", "Jane Smith", "Bob Johnson", "Alice Brown"],
            "description": "Four guests check-in"
        },
        {
            "guest_names": [],
            "description": "No guest names (fallback)"
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📋 Test Case {i}: {test_case['description']}")
        print(f"   Guest Names: {test_case['guest_names']}")
        
        # Simulate the message generation logic
        guest_names = test_case['guest_names']
        
        if guest_names:
            if len(guest_names) == 1:
                message = f"Check-in Complete! We welcome you to our hotel, {guest_names[0]}. Please enjoy your stay."
            else:
                # Multiple guests
                names_str = ", ".join(guest_names[:-1]) + f" and {guest_names[-1]}"
                message = f"Check-in Complete! We welcome you to our hotel, {names_str}. Please enjoy your stay."
        else:
            message = "Check-in Complete! We welcome you to our hotel. Please enjoy your stay."
        
        print(f"   Message: {message}")
    
    print("\n" + "=" * 60)
    print("📝 Message Generation Logic:")
    print("1. Single guest: 'We welcome you to our hotel, [Name]. Please enjoy your stay.'")
    print("2. Multiple guests: 'We welcome you to our hotel, [Name1], [Name2] and [Name3]. Please enjoy your stay.'")
    print("3. No names: 'We welcome you to our hotel. Please enjoy your stay.'")
    print()
    print("💡 This provides a personalized welcome experience for each guest!")

if __name__ == "__main__":
    test_personalized_messages()
