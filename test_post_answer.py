#!/usr/bin/env python3
"""
Test script for the post_answer MCP tool
"""

import json
import requests
import time

BASE_URL = "http://localhost:8000"

def create_test_questions():
    """Create test questions to answer"""
    test_questions = [
        {
            "title": "How to implement async/await in Python?",
            "content": "I'm struggling with understanding how async/await works in Python. Can someone explain the concept and provide some practical examples?",
            "tags": ["python", "async", "await", "asyncio"],
            "language": "python"
        },
        {
            "title": "What's the difference between var and let in JavaScript?",
            "content": "I keep seeing both var and let in JavaScript code. What's the practical difference between them and when should I use each one?",
            "tags": ["javascript", "variables", "es6"],
            "language": "javascript"
        }
    ]
    
    print("Creating test questions...")
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

def test_post_answer(question_ids):
    """Test the post_answer endpoint with various scenarios"""
    
    print("Testing POST /mcp/post_answer endpoint...\n")
    
    if not question_ids:
        print("❌ No question IDs available for testing")
        return
    
    test_cases = [
        {
            "name": "Valid answer without code examples",
            "data": {
                "question_id": question_ids[0],
                "content": "You can use async/await in Python by defining async functions with the 'async def' keyword and using 'await' to call other async functions. This allows for non-blocking code execution.",
                "code_examples": [],
                "author": "gpt-4"
            },
            "expected_status": 200
        },
        {
            "name": "Valid answer with single code example",
            "data": {
                "question_id": question_ids[0],
                "content": "Here's a practical example of async/await in Python. The key is to use 'async def' for function definitions and 'await' for calling async operations.",
                "code_examples": [
                    {
                        "language": "python",
                        "code": "import asyncio\n\nasync def fetch_data():\n    await asyncio.sleep(1)  # Simulate async operation\n    return \"Data fetched\"\n\nasync def main():\n    result = await fetch_data()\n    print(result)\n\n# Run the async function\nasyncio.run(main())"
                    }
                ],
                "author": "expert-python"
            },
            "expected_status": 200
        },
        {
            "name": "Valid answer with multiple code examples",
            "data": {
                "question_id": question_ids[1] if len(question_ids) > 1 else question_ids[0],
                "content": "The main differences between var and let are scope and hoisting behavior. Let me show you examples of both.",
                "code_examples": [
                    {
                        "language": "javascript",
                        "code": "// var example - function scope\nfunction varExample() {\n    if (true) {\n        var x = 1;\n    }\n    console.log(x); // 1 - accessible outside block\n}"
                    },
                    {
                        "language": "javascript", 
                        "code": "// let example - block scope\nfunction letExample() {\n    if (true) {\n        let y = 1;\n    }\n    console.log(y); // ReferenceError - not accessible outside block\n}"
                    }
                ],
                "author": "js-expert"
            },
            "expected_status": 200
        },
        {
            "name": "Answer with too short content",
            "data": {
                "question_id": question_ids[0],
                "content": "Short answer",
                "code_examples": [],
                "author": "user1"
            },
            "expected_status": 422
        },
        {
            "name": "Answer with invalid question ID",
            "data": {
                "question_id": 99999,
                "content": "This is a valid answer with sufficient length to pass content validation requirements.",
                "code_examples": [],
                "author": "user1"
            },
            "expected_status": 404
        },
        {
            "name": "Answer with empty author",
            "data": {
                "question_id": question_ids[0],
                "content": "This is a valid answer with sufficient length to pass content validation requirements.",
                "code_examples": [],
                "author": ""
            },
            "expected_status": 422
        },
        {
            "name": "Answer with invalid code example (empty code)",
            "data": {
                "question_id": question_ids[0],
                "content": "This answer has an invalid code example that should cause validation to fail.",
                "code_examples": [
                    {
                        "language": "python",
                        "code": ""
                    }
                ],
                "author": "user1"
            },
            "expected_status": 422
        },
        {
            "name": "Answer with invalid code example (empty language)",
            "data": {
                "question_id": question_ids[0],
                "content": "This answer has an invalid code example that should cause validation to fail.",
                "code_examples": [
                    {
                        "language": "",
                        "code": "print('hello')"
                    }
                ],
                "author": "user1"
            },
            "expected_status": 422
        },
        {
            "name": "Answer with missing required field (question_id)",
            "data": {
                "content": "This answer is missing the required question_id field.",
                "code_examples": [],
                "author": "user1"
            },
            "expected_status": 422
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"Test {i}: {test_case['name']}")
        print("=" * 50)
        
        try:
            response = requests.post(
                f"{BASE_URL}/mcp/post_answer",
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
                
                if response.status_code == 200 and "data" in response_json:
                    data = response_json["data"]
                    print(f"Answer ID: {data.get('answer_id')}")
                    print(f"Question ID: {data.get('question_id')}")
                    print(f"Status: {data.get('status')}")
                
                print("Response:")
                print(json.dumps(response_json, indent=2, default=str))
                    
            except Exception as e:
                print(f"Response parsing error: {e}")
                print("Response (raw):", response.text[:300])
                
        except requests.exceptions.ConnectionError:
            print("❌ Connection error - is the server running?")
        except Exception as e:
            print(f"❌ Error: {e}")
        
        print("\n" + "-" * 70 + "\n")

def test_answer_retrieval(question_ids):
    """Test retrieving questions with answers to verify answer_count"""
    if not question_ids:
        return
    
    print("Testing answer retrieval...")
    print("=" * 50)
    
    try:
        response = requests.get(f"{BASE_URL}/mcp/get_questions?limit=5")
        
        if response.status_code == 200:
            data = response.json()
            if data.get("data", {}).get("questions"):
                for question in data["data"]["questions"]:
                    print(f"Question {question['id']}: {question['title'][:50]}...")
                    print(f"  Answer count: {question['answer_count']}")
                    print(f"  Votes: {question['votes']}")
        else:
            print(f"Failed to retrieve questions: {response.status_code}")
            
    except Exception as e:
        print(f"Error retrieving questions: {e}")
    
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
    print("Context Overflow MCP Server - post_answer Tool Test")
    print("=" * 60)
    
    # Check server health first
    if check_server_health():
        print("\n")
        
        # Create test questions
        question_ids = create_test_questions()
        
        if question_ids:
            # Run answer tests
            test_post_answer(question_ids)
            
            # Test answer retrieval
            test_answer_retrieval(question_ids)
        else:
            print("No questions created - skipping answer tests")
    else:
        print("\nPlease start the server with: python main.py")
        print("Then run this test again.")