#!/usr/bin/env python3
"""
Test script for the get_answers MCP tool
"""

import json
import requests
import time

BASE_URL = "http://localhost:8000"

def create_test_data():
    """Create test questions and answers with varying vote counts"""
    print("Creating test questions and answers...")
    
    # Create a test question
    question_data = {
        "title": "How to handle async/await in Python with multiple operations?",
        "content": "I need to understand how to properly chain multiple async operations in Python and handle errors gracefully.",
        "tags": ["python", "async", "await", "asyncio", "error-handling"],
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
            return None
    except Exception as e:
        print(f"❌ Error creating question: {e}")
        return None
    
    # Create multiple answers with different characteristics
    test_answers = [
        {
            "question_id": question_id,
            "content": "The best approach is to use asyncio.gather() for concurrent operations. This allows you to run multiple async functions simultaneously and wait for all of them to complete.",
            "code_examples": [
                {
                    "language": "python",
                    "code": "import asyncio\n\nasync def fetch_data(url):\n    # Simulate async operation\n    await asyncio.sleep(1)\n    return f\"Data from {url}\"\n\nasync def main():\n    urls = ['url1', 'url2', 'url3']\n    results = await asyncio.gather(*[fetch_data(url) for url in urls])\n    return results\n\n# Run the async function\nresults = asyncio.run(main())\nprint(results)"
                }
            ],
            "author": "async-expert",
            "expected_votes": 15  # We'll simulate this later
        },
        {
            "question_id": question_id,
            "content": "You can also use asyncio.create_task() to create tasks and then await them individually. This gives you more control over error handling.",
            "code_examples": [
                {
                    "language": "python",
                    "code": "import asyncio\n\nasync def process_item(item):\n    try:\n        await asyncio.sleep(0.5)\n        return f\"Processed {item}\"\n    except Exception as e:\n        return f\"Error processing {item}: {e}\"\n\nasync def main():\n    items = ['item1', 'item2', 'item3']\n    tasks = [asyncio.create_task(process_item(item)) for item in items]\n    \n    results = []\n    for task in tasks:\n        try:\n            result = await task\n            results.append(result)\n        except Exception as e:\n            results.append(f\"Task failed: {e}\")\n    \n    return results"
                }
            ],
            "author": "python-guru",
            "expected_votes": 8
        },
        {
            "question_id": question_id,
            "content": "For error handling in async operations, you should use try/except blocks around your await statements. You can also use asyncio.as_completed() for more advanced scenarios.",
            "code_examples": [
                {
                    "language": "python",
                    "code": "import asyncio\n\nasync def safe_async_operation(data):\n    try:\n        # Your async operation here\n        await asyncio.sleep(0.1)\n        if data == 'error':\n            raise ValueError('Simulated error')\n        return f'Success: {data}'\n    except ValueError as e:\n        return f'Handled error: {e}'\n    except Exception as e:\n        return f'Unexpected error: {e}'"
                },
                {
                    "language": "python", 
                    "code": "# Using asyncio.as_completed for handling results as they arrive\nasync def process_with_completion():\n    tasks = [safe_async_operation(f'data{i}') for i in range(5)]\n    \n    for task in asyncio.as_completed(tasks):\n        result = await task\n        print(f'Completed: {result}')"
                }
            ],
            "author": "error-handler-pro",
            "expected_votes": 12
        },
        {
            "question_id": question_id,
            "content": "A simple approach is to just use basic async/await syntax. Make sure to always await your async functions.",
            "code_examples": [],
            "author": "beginner-dev",
            "expected_votes": 3
        },
        {
            "question_id": question_id,
            "content": "Here's a comprehensive example that combines multiple async patterns with proper error handling and logging.",
            "code_examples": [
                {
                    "language": "python",
                    "code": "import asyncio\nimport logging\nfrom typing import List, Any\n\nlogging.basicConfig(level=logging.INFO)\nlogger = logging.getLogger(__name__)\n\nclass AsyncProcessor:\n    def __init__(self, max_concurrent: int = 3):\n        self.max_concurrent = max_concurrent\n        self.semaphore = asyncio.Semaphore(max_concurrent)\n    \n    async def process_item(self, item: Any) -> dict:\n        async with self.semaphore:\n            try:\n                logger.info(f'Processing {item}')\n                await asyncio.sleep(0.5)  # Simulate work\n                return {'item': item, 'status': 'success', 'result': f'processed_{item}'}\n            except Exception as e:\n                logger.error(f'Error processing {item}: {e}')\n                return {'item': item, 'status': 'error', 'error': str(e)}\n    \n    async def process_batch(self, items: List[Any]) -> List[dict]:\n        tasks = [self.process_item(item) for item in items]\n        return await asyncio.gather(*tasks, return_exceptions=True)\n\n# Usage\nasync def main():\n    processor = AsyncProcessor(max_concurrent=2)\n    items = [f'item_{i}' for i in range(10)]\n    results = await processor.process_batch(items)\n    \n    for result in results:\n        if isinstance(result, Exception):\n            logger.error(f'Task exception: {result}')\n        else:\n            logger.info(f'Result: {result}')\n\nif __name__ == '__main__':\n    asyncio.run(main())"
                }
            ],
            "author": "senior-architect",
            "expected_votes": 20
        }
    ]
    
    created_answers = []
    for i, answer_data in enumerate(test_answers):
        try:
            response = requests.post(
                f"{BASE_URL}/mcp/post_answer",
                json=answer_data,
                headers={"Content-Type": "application/json"}
            )
            if response.status_code == 200:
                answer_id = response.json()["data"]["answer_id"]
                created_answers.append({
                    "answer_id": answer_id,
                    "expected_votes": answer_data["expected_votes"],
                    "author": answer_data["author"]
                })
                print(f"✅ Created answer ID: {answer_id} by {answer_data['author']}")
            else:
                print(f"❌ Failed to create answer {i+1}: {response.status_code}")
        except Exception as e:
            print(f"❌ Error creating answer {i+1}: {e}")
    
    print(f"Created {len(created_answers)} answers for question {question_id}\\n")
    return question_id, created_answers

def test_get_answers(question_id):
    """Test the get_answers endpoint with various scenarios"""
    
    print("Testing GET /mcp/get_answers/{question_id} endpoint...\\n")
    
    test_cases = [
        {
            "name": "Get answers for valid question",
            "question_id": question_id,
            "expected_status": 200
        },
        {
            "name": "Get answers for non-existent question",
            "question_id": 99999,
            "expected_status": 404
        },
        {
            "name": "Get answers for invalid question ID (negative)",
            "question_id": -1,
            "expected_status": 404
        },
        {
            "name": "Get answers for question ID zero",
            "question_id": 0,
            "expected_status": 404
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"Test {i}: {test_case['name']}")
        print("=" * 50)
        
        try:
            response = requests.get(f"{BASE_URL}/mcp/get_answers/{test_case['question_id']}")
            
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
                    print(f"Question ID: {data.get('question_id')}")
                    print(f"Number of answers: {len(data.get('answers', []))}")
                    
                    # Show answer details
                    for j, answer in enumerate(data.get('answers', []), 1):
                        print(f"  Answer {j}:")
                        print(f"    ID: {answer.get('id')}")
                        print(f"    Author: {answer.get('author')}")
                        print(f"    Votes: {answer.get('votes')}")
                        print(f"    Content: {answer.get('content', '')[:100]}...")
                        print(f"    Code examples: {len(answer.get('code_examples', []))}")
                        
                        # Show first code example if available
                        if answer.get('code_examples'):
                            first_example = answer['code_examples'][0]
                            print(f"      First example ({first_example.get('language')}): {first_example.get('code', '')[:50]}...")
                        print()
                
                # Show truncated response for non-200 responses
                if response.status_code != 200:
                    print("Response:")
                    print(json.dumps(response_json, indent=2, default=str))
                    
            except Exception as e:
                print(f"Response parsing error: {e}")
                print("Response (raw):", response.text[:300])
                
        except requests.exceptions.ConnectionError:
            print("❌ Connection error - is the server running?")
        except Exception as e:
            print(f"❌ Error: {e}")
        
        print("\\n" + "-" * 70 + "\\n")

def test_sorting_and_structure(question_id):
    """Test that answers are properly sorted by votes and have correct structure"""
    print("Testing answer sorting and structure...")
    print("=" * 50)
    
    try:
        response = requests.get(f"{BASE_URL}/mcp/get_answers/{question_id}")
        
        if response.status_code == 200:
            data = response.json()["data"]
            answers = data["answers"]
            
            # Test sorting (should be by votes descending)
            if len(answers) > 1:
                is_sorted = all(
                    answers[i]["votes"] >= answers[i+1]["votes"] 
                    for i in range(len(answers)-1)
                )
                
                if is_sorted:
                    print("✅ Answers are properly sorted by votes (highest first)")
                else:
                    print("❌ Answers are not properly sorted by votes")
                    vote_sequence = [a["votes"] for a in answers]
                    print(f"Vote sequence: {vote_sequence}")
            
            # Test structure of each answer
            required_fields = ["id", "content", "code_examples", "author", "votes", "created_at"]
            all_valid = True
            
            for i, answer in enumerate(answers):
                for field in required_fields:
                    if field not in answer:
                        print(f"❌ Answer {i+1} missing required field '{field}'")
                        all_valid = False
                
                # Test code_examples structure
                if "code_examples" in answer:
                    for j, code_example in enumerate(answer["code_examples"]):
                        if not isinstance(code_example, dict):
                            print(f"❌ Answer {i+1}, code example {j+1} is not a dict")
                            all_valid = False
                        elif "language" not in code_example or "code" not in code_example:
                            print(f"❌ Answer {i+1}, code example {j+1} missing language or code")
                            all_valid = False
            
            if all_valid:
                print("✅ All answers have correct structure")
            
            # Show summary
            print(f"\\nSummary:")
            print(f"Total answers: {len(answers)}")
            for i, answer in enumerate(answers, 1):
                print(f"  {i}. {answer['author']} - {answer['votes']} votes - {len(answer['code_examples'])} code examples")
        
        else:
            print(f"❌ Failed to get answers: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error testing sorting: {e}")
    
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
    print("Context Overflow MCP Server - get_answers Tool Test")
    print("=" * 60)
    
    # Check server health first
    if check_server_health():
        print("\\n")
        
        # Create test data
        result = create_test_data()
        if result:
            question_id, created_answers = result
            
            # Run tests
            test_get_answers(question_id)
            
            # Test sorting and structure
            test_sorting_and_structure(question_id)
        else:
            print("Failed to create test data - skipping tests")
    else:
        print("\\nPlease start the server with: python main.py")
        print("Then run this test again.")