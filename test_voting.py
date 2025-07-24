#!/usr/bin/env python3
"""
Test script for the voting MCP tool
"""

import json
import requests
import time

BASE_URL = "http://localhost:8000"

def create_test_data():
    """Create test questions and answers for voting"""
    print("Creating test questions and answers for voting tests...")
    
    # Create test question
    question_data = {
        "title": "How to implement efficient sorting algorithms in Python?",
        "content": "I need to understand different sorting algorithms and their time complexities. Which ones are best for different scenarios?",
        "tags": ["python", "algorithms", "sorting", "performance"],
        "language": "python"
    }
    
    question_id = None
    try:
        response = requests.post(
            f"{BASE_URL}/mcp/post_question",
            json=question_data,
            headers={"Content-Type": "application/json"}
        )
        if response.status_code == 200:
            question_id = response.json()["data"]["question_id"]
            print(f"✅ Created question ID: {question_id}")
        else:
            print(f"❌ Failed to create question: {response.status_code}")
            return None, None
    except Exception as e:
        print(f"❌ Error creating question: {e}")
        return None, None
    
    # Create test answers
    answer_data = {
        "question_id": question_id,
        "content": "For general purpose sorting, Python's built-in sorted() function uses Timsort, which is very efficient for real-world data with O(n log n) worst case and O(n) best case complexity.",
        "code_examples": [
            {
                "language": "python",
                "code": "# Using built-in sorted() function\ndata = [64, 34, 25, 12, 22, 11, 90]\nsorted_data = sorted(data)\nprint(sorted_data)  # [11, 12, 22, 25, 34, 64, 90]\n\n# In-place sorting with sort()\ndata.sort()\nprint(data)  # [11, 12, 22, 25, 34, 64, 90]"
            }
        ],
        "author": "algorithm-expert"
    }
    
    answer_id = None
    try:
        response = requests.post(
            f"{BASE_URL}/mcp/post_answer",
            json=answer_data,
            headers={"Content-Type": "application/json"}
        )
        if response.status_code == 200:
            answer_id = response.json()["data"]["answer_id"]
            print(f"✅ Created answer ID: {answer_id}")
        else:
            print(f"❌ Failed to create answer: {response.status_code}")
    except Exception as e:
        print(f"❌ Error creating answer: {e}")
    
    print(f"Test data created: Question {question_id}, Answer {answer_id}\\n")
    return question_id, answer_id

def test_voting_scenarios(question_id, answer_id):
    """Test various voting scenarios"""
    
    print("Testing POST /mcp/vote endpoint with various scenarios...\\n")
    
    test_cases = [
        # Basic voting tests
        {
            "name": "Upvote a question (first vote)",
            "data": {
                "target_id": question_id,
                "target_type": "question",
                "vote_type": "upvote",
                "user_id": "test_user_1"
            },
            "expected_status": 200,
            "expected_vote_type": "upvote",
            "expected_previous": None
        },
        {
            "name": "Downvote an answer (first vote)",
            "data": {
                "target_id": answer_id,
                "target_type": "answer",
                "vote_type": "downvote",
                "user_id": "test_user_2"
            },
            "expected_status": 200,
            "expected_vote_type": "downvote",
            "expected_previous": None
        },
        
        # Duplicate vote prevention (toggle behavior)
        {
            "name": "Same user upvotes question again (should remove vote)",
            "data": {
                "target_id": question_id,
                "target_type": "question",
                "vote_type": "upvote",
                "user_id": "test_user_1"
            },
            "expected_status": 200,
            "expected_vote_type": None,  # Vote removed
            "expected_previous": "upvote"
        },
        
        # Vote change scenarios
        {
            "name": "User votes question again (should create new upvote)",
            "data": {
                "target_id": question_id,
                "target_type": "question",
                "vote_type": "upvote",
                "user_id": "test_user_1"
            },
            "expected_status": 200,
            "expected_vote_type": "upvote",
            "expected_previous": None
        },
        {
            "name": "Same user changes upvote to downvote",
            "data": {
                "target_id": question_id,
                "target_type": "question",
                "vote_type": "downvote",
                "user_id": "test_user_1"
            },
            "expected_status": 200,
            "expected_vote_type": "downvote",
            "expected_previous": "upvote"
        },
        
        # Multiple users voting
        {
            "name": "Different user upvotes same question",
            "data": {
                "target_id": question_id,
                "target_type": "question",
                "vote_type": "upvote",
                "user_id": "test_user_3"
            },
            "expected_status": 200,
            "expected_vote_type": "upvote",
            "expected_previous": None
        },
        {
            "name": "Another user upvotes the answer",
            "data": {
                "target_id": answer_id,
                "target_type": "answer",
                "vote_type": "upvote",
                "user_id": "test_user_4"
            },
            "expected_status": 200,
            "expected_vote_type": "upvote",
            "expected_previous": None
        },
        
        # Error cases
        {
            "name": "Vote on non-existent question",
            "data": {
                "target_id": 99999,
                "target_type": "question",
                "vote_type": "upvote",
                "user_id": "test_user_5"
            },
            "expected_status": 404
        },
        {
            "name": "Vote on non-existent answer",
            "data": {
                "target_id": 99999,
                "target_type": "answer",
                "vote_type": "upvote",
                "user_id": "test_user_5"
            },
            "expected_status": 404
        },
        {
            "name": "Invalid target_type",
            "data": {
                "target_id": question_id,
                "target_type": "invalid",
                "vote_type": "upvote",
                "user_id": "test_user_5"
            },
            "expected_status": 422
        },
        {
            "name": "Invalid vote_type",
            "data": {
                "target_id": question_id,
                "target_type": "question",
                "vote_type": "invalid",
                "user_id": "test_user_5"
            },
            "expected_status": 422
        },
        {
            "name": "Empty user_id",
            "data": {
                "target_id": question_id,
                "target_type": "question",
                "vote_type": "upvote",
                "user_id": ""
            },
            "expected_status": 422
        },
        {
            "name": "Negative target_id",
            "data": {
                "target_id": -1,
                "target_type": "question",
                "vote_type": "upvote",
                "user_id": "test_user_5"
            },
            "expected_status": 422
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"Test {i}: {test_case['name']}")
        print("=" * 50)
        
        try:
            response = requests.post(
                f"{BASE_URL}/mcp/vote",
                json=test_case["data"],
                headers={"Content-Type": "application/json"}
            )
            
            print(f"Status Code: {response.status_code}")
            print(f"Expected: {test_case['expected_status']}")
            
            if response.status_code == test_case["expected_status"]:
                print("✅ Status code matches expected")
            else:
                print("❌ Status code mismatch")
            
            # Parse and validate response
            try:
                response_json = response.json()
                
                if response.status_code == 200:
                    # Validate successful vote response
                    data = response_json.get("data", {})
                    
                    print(f"Vote type: {data.get('vote_type')}")
                    print(f"Expected vote type: {test_case.get('expected_vote_type')}")
                    print(f"Previous vote: {data.get('previous_vote')}")
                    print(f"Expected previous: {test_case.get('expected_previous')}")
                    print(f"New vote total: {data.get('new_vote_total')}")
                    
                    # Check vote_type matches expected
                    if 'expected_vote_type' in test_case:
                        if data.get('vote_type') == test_case['expected_vote_type']:
                            print("✅ Vote type matches expected")
                        else:
                            print("❌ Vote type mismatch")
                    
                    # Check previous vote matches expected
                    if 'expected_previous' in test_case:
                        if data.get('previous_vote') == test_case['expected_previous']:
                            print("✅ Previous vote matches expected")
                        else:
                            print("❌ Previous vote mismatch")
                
                # Show response (truncated for readability)
                print("Response:")
                response_str = json.dumps(response_json, indent=2, default=str)
                if len(response_str) > 500:
                    print(response_str[:500] + "...")
                else:
                    print(response_str)
                    
            except Exception as e:
                print(f"Response parsing error: {e}")
                print("Response (raw):", response.text[:300])
                
        except requests.exceptions.ConnectionError:
            print("❌ Connection error - is the server running?")
        except Exception as e:
            print(f"❌ Error: {e}")
        
        print("\\n" + "-" * 70 + "\\n")

def test_vote_count_updates(question_id, answer_id):
    """Test that vote counts are properly updated in the questions/answers"""
    print("Testing vote count updates in questions and answers...")
    print("=" * 50)
    
    try:
        # Check question vote count
        response = requests.get(f"{BASE_URL}/mcp/get_questions?limit=10")
        if response.status_code == 200:
            questions = response.json()["data"]["questions"]
            test_question = next((q for q in questions if q["id"] == question_id), None)
            
            if test_question:
                print(f"Question {question_id} current vote count: {test_question['votes']}")
            else:
                print(f"❌ Question {question_id} not found in results")
        
        # Check answer vote count
        response = requests.get(f"{BASE_URL}/mcp/get_answers/{question_id}")
        if response.status_code == 200:
            answers = response.json()["data"]["answers"]
            test_answer = next((a for a in answers if a["id"] == answer_id), None)
            
            if test_answer:
                print(f"Answer {answer_id} current vote count: {test_answer['votes']}")
            else:
                print(f"❌ Answer {answer_id} not found in results")
        
        print("✅ Vote counts retrieved successfully")
        
    except Exception as e:
        print(f"❌ Error checking vote counts: {e}")
    
    print("\\n" + "-" * 70 + "\\n")

def test_voting_by_multiple_users(question_id):
    """Test voting by multiple users to verify totals"""
    print("Testing voting by multiple users...")
    print("=" * 50)
    
    users_and_votes = [
        ("alice", "upvote"),
        ("bob", "upvote"),
        ("charlie", "downvote"),
        ("diana", "upvote"),
        ("eve", "downvote")
    ]
    
    print("Multiple users voting on the same question:")
    for user, vote_type in users_and_votes:
        try:
            response = requests.post(
                f"{BASE_URL}/mcp/vote",
                json={
                    "target_id": question_id,
                    "target_type": "question",
                    "vote_type": vote_type,
                    "user_id": user
                },
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()["data"]
                print(f"  {user} -> {vote_type}: Total = {data['new_vote_total']}")
            else:
                print(f"  {user} -> {vote_type}: ERROR {response.status_code}")
                
        except Exception as e:
            print(f"  {user} -> {vote_type}: ERROR {e}")
    
    # Final vote count check
    try:
        response = requests.get(f"{BASE_URL}/mcp/get_questions?limit=10")
        if response.status_code == 200:
            questions = response.json()["data"]["questions"]
            test_question = next((q for q in questions if q["id"] == question_id), None)
            
            if test_question:
                print(f"\\nFinal question vote count: {test_question['votes']}")
                expected = 3 - 2  # 3 upvotes - 2 downvotes = 1 (plus any previous votes)
                print(f"Expected net from this test: +1 (3 upvotes - 2 downvotes)")
    except Exception as e:
        print(f"Error getting final count: {e}")
    
    print("\\n" + "-" * 70 + "\\n")

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
    print("Context Overflow MCP Server - Voting Tool Test")
    print("=" * 60)
    
    # Check server health first
    if check_server_health():
        print("\\n")
        
        # Create test data
        question_id, answer_id = create_test_data()
        
        if question_id and answer_id:
            # Run comprehensive voting tests
            test_voting_scenarios(question_id, answer_id)
            
            # Test vote count updates
            test_vote_count_updates(question_id, answer_id)
            
            # Test multiple users voting
            test_voting_by_multiple_users(question_id)
        else:
            print("Failed to create test data - skipping voting tests")
    else:
        print("\\nPlease start the server with: python main.py")
        print("Then run this test again.")