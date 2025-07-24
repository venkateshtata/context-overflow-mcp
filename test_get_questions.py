#!/usr/bin/env python3
"""
Test script for the get_questions MCP tool
"""

import json
import requests
import time

BASE_URL = "http://localhost:8000"

def create_test_data():
    """Create some test questions to work with"""
    test_questions = [
        {
            "title": "How to use async/await in Python asyncio?",
            "content": "I'm learning about asynchronous programming in Python and need examples of async/await usage with asyncio library.",
            "tags": ["python", "async", "asyncio", "await"],
            "language": "python"
        },
        {
            "title": "JavaScript promises vs async/await comparison",
            "content": "What are the practical differences between using promises and async/await in JavaScript? When should I use each approach?",
            "tags": ["javascript", "async", "promises", "es6"],
            "language": "javascript"
        },
        {
            "title": "Python list comprehension best practices",
            "content": "I want to learn about list comprehensions in Python. What are some best practices and common pitfalls to avoid?",
            "tags": ["python", "list-comprehension", "best-practices"],
            "language": "python"
        },
        {
            "title": "React hooks useState and useEffect tutorial",
            "content": "I'm new to React hooks and need a comprehensive guide on useState and useEffect with practical examples.",
            "tags": ["react", "hooks", "javascript", "frontend"],
            "language": "javascript"
        },
        {
            "title": "SQL JOIN operations explained with examples",
            "content": "Can someone explain different types of SQL JOINs (INNER, LEFT, RIGHT, FULL) with clear examples?",
            "tags": ["sql", "joins", "database", "query"],
            "language": "sql"
        }
    ]
    
    print("Creating test data...")
    created_ids = []
    
    for question in test_questions:
        try:
            response = requests.post(
                f"{BASE_URL}/mcp/post_question",
                json=question,
                headers={"Content-Type": "application/json"}
            )
            if response.status_code == 200:
                data = response.json()
                created_ids.append(data["data"]["question_id"])
                print(f"✅ Created question ID: {data['data']['question_id']}")
            else:
                print(f"❌ Failed to create question: {response.status_code}")
        except Exception as e:
            print(f"❌ Error creating question: {e}")
    
    print(f"Created {len(created_ids)} test questions\n")
    return created_ids

def test_get_questions():
    """Test the get_questions endpoint with various scenarios"""
    
    print("Testing GET /mcp/get_questions endpoint...\n")
    
    test_cases = [
        {
            "name": "Get all questions (default)",
            "params": {},
            "expected_status": 200
        },
        {
            "name": "Get questions with limit",
            "params": {"limit": 3},
            "expected_status": 200
        },
        {
            "name": "Get questions with offset",
            "params": {"limit": 2, "offset": 2},
            "expected_status": 200
        },
        {
            "name": "Filter by language - Python",
            "params": {"language": "python"},
            "expected_status": 200
        },
        {
            "name": "Filter by language - JavaScript",
            "params": {"language": "javascript"},
            "expected_status": 200
        },
        {
            "name": "Filter by single tag",
            "params": {"tags": "async"},
            "expected_status": 200
        },
        {
            "name": "Filter by multiple tags",
            "params": {"tags": "python,async"},
            "expected_status": 200
        },
        {
            "name": "Filter by language and tags",
            "params": {"language": "javascript", "tags": "async,promises"},
            "expected_status": 200
        },
        {
            "name": "Large limit",
            "params": {"limit": 50},
            "expected_status": 200
        },
        {
            "name": "Invalid limit (too large)",
            "params": {"limit": 150},
            "expected_status": 422
        },
        {
            "name": "Invalid offset (negative)",
            "params": {"offset": -1},
            "expected_status": 422
        },
        {
            "name": "Non-existent language filter",
            "params": {"language": "nonexistent"},
            "expected_status": 200  # Should return empty results
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"Test {i}: {test_case['name']}")
        print("=" * 50)
        
        try:
            response = requests.get(
                f"{BASE_URL}/mcp/get_questions",
                params=test_case["params"]
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
                
                if response.status_code == 200 and "data" in response_json:
                    data = response_json["data"]
                    print(f"Questions returned: {len(data.get('questions', []))}")
                    print(f"Total questions: {data.get('total', 0)}")
                    print(f"Has more: {data.get('has_more', False)}")
                    
                    # Show first question details if available
                    if data.get("questions"):
                        first_q = data["questions"][0]
                        print(f"First question: ID={first_q.get('id')}, Title='{first_q.get('title', '')[:50]}...'")
                        print(f"Tags: {first_q.get('tags', [])}")
                        print(f"Votes: {first_q.get('votes', 0)}, Answers: {first_q.get('answer_count', 0)}")
                
                print("Full Response:")
                print(json.dumps(response_json, indent=2, default=str)[:500] + "..." if len(str(response_json)) > 500 else json.dumps(response_json, indent=2, default=str))
                    
            except Exception as e:
                print(f"Response parsing error: {e}")
                print("Response (raw):", response.text[:300])
                
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
    print("Context Overflow MCP Server - get_questions Tool Test")
    print("=" * 60)
    
    # Check server health first
    if check_server_health():
        print("\n")
        
        # Create test data
        create_test_data()
        
        # Run tests
        test_get_questions()
    else:
        print("\nPlease start the server with: python main.py")
        print("Then run this test again.")