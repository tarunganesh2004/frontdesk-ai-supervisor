import requests
import json

BASE_URL = "http://localhost:5000/api"

# Test questions
test_calls = [
    {"question": "What are your hours?", "customer_phone": "555-1111"},
    {"question": "Do you do beard trims?", "customer_phone": "555-2222"},
    {
        "question": "What is your return policy for products?",
        "customer_phone": "555-3333",
    },
    {"question": "How much is a haircut?", "customer_phone": "555-4444"},
    {"question": "Do you have gift certificates?", "customer_phone": "555-5555"},
]

print("=== Testing Salon AI Supervisor System ===\n")

for i, call in enumerate(test_calls, 1):
    print(f"Test {i}: Customer asks: '{call['question']}'")

    response = requests.post(f"{BASE_URL}/simulate-call", json=call)
    result = response.json()

    if result["escalated"]:
        print("   → ESCALATED to supervisor (AI didn't know answer)")
        print(f"   → Request ID: {result['request_id']}")
    else:
        print(f"   → AI answered: {result['answer'][:50]}...")

    print()

print("Check http://localhost:5000/requests to see pending requests!")
