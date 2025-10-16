## TESTING.md

# Testing the Salon AI Supervisor System

This document explains how to test the complete workflow of the Salon AI Supervisor system.

## Prerequisites

- The application is running (see README.md for setup)
- You have access to the Supervisor UI at http://localhost:5000
- You can make HTTP requests to the API (using curl, Postman, or the provided test script)

## Testing the Complete Workflow

### Step 1: Start the Server

If not already running, start the server:

```bash
python run.py
```
You should see output indicating the database is initialized and the server is running.

### Step 2: Simulate Customer Calls

Open a new terminal and simulate customer calls using the API, Using curl


#### Test 1- Known Question (AI Answers Immediately)

API Call:
```bash
curl -X POST http://localhost:5000/api/simulate-call \
  -H "Content-Type: application/json" \
  -d '{"question": "What are your hours?", "customer_phone": "555-1234"}'
```
Expected Response:
```json
{
  "success": true,
  "escalated": false,
  "answer": "We're open Monday to Friday from 9 AM to 7 PM...",
  "request_id": "req-123"
}
```

#### Test 2 - Unknown Question (Escalates to Supervisor)
API Call:
```bash
curl -X POST http://localhost:5000/api/simulate-call \
  -H "Content-Type: application/json" \
  -d '{"question": "Do you offer hair coloring for men?", "customer_phone": "555-5678"}'
```
Expected Response:
```json
{
  "success": true,
  "escalated": true,
  "message": "Escalated to supervisor",
  "request_id": "req-456"
}
```
Check Server Console:
- SUPERVISOR NOTIFICATION: Help needed for request req-456
- QUESTION: Do you offer hair coloring for men?

#### Test 3 - Another Unknown Question
API Call:
```bash
curl -X POST http://localhost:5000/api/simulate-call \
  -H "Content-Type: application/json" \
  -d '{"question": "What is your cancellation policy?", "customer_phone": "555-9012"}'
```

### Step 3: View Pending Requests in Supervisor UI

1. Open http://localhost:5000 in your browser
2. Click on "Pending Requests"
3. You should see both escalated questions

