import requests
import time

BASE_URL = "http://localhost:5000/api"


def test_workflow():
    print("=== Starting Complete Workflow Test ===\n")

    # Test 1: Known question
    print("1. Testing known question...")
    response = requests.post(
        f"{BASE_URL}/simulate-call",
        json={"question": "What are your hours?", "customer_phone": "555-1111"},
    )
    result = response.json()
    print(f"   Result: {'ESCALATED' if result['escalated'] else 'ANSWERED'}")

    # Test 2: Unknown question
    print("2. Testing unknown question...")
    response = requests.post(
        f"{BASE_URL}/simulate-call",
        json={"question": "Do you offer beard trimming?", "customer_phone": "555-2222"},
    )
    result = response.json()
    print(f"   Result: {'ESCALATED' if result['escalated'] else 'ANSWERED'}")
    print(f"   Request ID: {result['request_id']}")

    # Test 3: Another unknown
    print("3. Testing another unknown question...")
    response = requests.post(
        f"{BASE_URL}/simulate-call",
        json={"question": "What products do you sell?", "customer_phone": "555-3333"},
    )
    result = response.json()
    print(f"   Result: {'ESCALATED' if result['escalated'] else 'ANSWERED'}")

    print("\n=== Check http://localhost:5000/requests for pending requests ===")
    print("=== Submit answers via the web interface ===")


if __name__ == "__main__":
    test_workflow()
