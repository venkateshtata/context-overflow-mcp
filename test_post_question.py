#!/usr/bin/env python3
"""
Test script for the post_question MCP tool
"""

import json
import requests
import time

BASE_URL = "http://localhost:8000"

def test_post_question():
    """Test the post_question endpoint with various scenarios"""
    
    print("Testing POST /mcp/post_question endpoint...\n")
    
    # Test data scenarios
    test_cases = [
        {
            "name": "Valid question",
            "data": {
                "title": "How to implement async/await in Python?",
                "content": "I'm struggling with understanding how async/await works in Python. Can someone explain the concept and provide some practical examples?",
                "tags": ["python", "async", "await", "asyncio"],
                "language": "python"
            },
            "expected_status": 200
        },
        {
            "name": "Another valid question", 
            "data": {
                "title": "What's the difference between let and const in JavaScript?",
                "content": "I keep seeing both let and const in JavaScript code. What's the practical difference between them and when should I use each one?",
                "tags": ["javascript", "variables", "es6"],
                "language": "javascript"
            },
            "expected_status": 200
        },
        {
            "name": "Title too short",
            "data": {
                "title": "Short",
                "content": "This is a valid content that meets the minimum length requirement for testing purposes.",
                "tags": ["test"],
                "language": "python"
            },
            "expected_status": 422
        },
        {
            "name": "Content too short",
            "data": {
                "title": "This is a valid title that meets length requirements",
                "content": "Short content",
                "tags": ["test"],
                "language": "python"
            },
            "expected_status": 422
        },
        {
            "name": "No tags provided",
            "data": {
                "title": "This is a valid title that meets length requirements",
                "content": "This is valid content that meets the minimum length requirement for testing purposes.",
                "tags": [],
                "language": "python"
            },
            "expected_status": 422
        },
        {
            "name": "Missing required field",
            "data": {
                "title": "This is a valid title that meets length requirements",
                "content": "This is valid content that meets the minimum length requirement for testing purposes.",
                "tags": ["test"]
                # Missing language field
            },
            "expected_status": 422
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"Test {i}: {test_case['name']}")
        print("=" * 50)
        
        try:
            response = requests.post(
                f"{BASE_URL}/mcp/post_question",
                json=test_case["data"],
                headers={"Content-Type": "application/json"}
            )
            
            print(f"Status Code: {response.status_code}")
            print(f"Expected: {test_case['expected_status']}")
            
            if response.status_code == test_case["expected_status"]:
                print("✅ Status code matches expected")
            else:
                print("❌ Status code mismatch")
            
            # Pretty print response
            try:
                response_json = response.json()
                print("Response:")
                print(json.dumps(response_json, indent=2))
            except:
                print("Response (raw):", response.text)
                
        except requests.exceptions.ConnectionError:
            print("❌ Connection error - is the server running?")
        except Exception as e:
            print(f"❌ Error: {e}")
        
        print("\n" + "-" * 70 + "\n")

def check_server_health():
    """Check if server is running and healthy"""
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            health_data = response.json()
            print(f"Server status: {health_data.get('message', 'Unknown')}")
            print(f"Database status: {health_data.get('database', 'Unknown')}")
            return True
        else:
            print(f"Server health check failed: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server. Please start the server first.")
        return False

if __name__ == "__main__":
    print("Context Overflow MCP Server - post_question Tool Test")
    print("=" * 60)
    
    # Check server health first
    if check_server_health():
        print("\n")
        test_post_question()
    else:
        print("\nPlease start the server with: python main.py")
        print("Then run this test again.")