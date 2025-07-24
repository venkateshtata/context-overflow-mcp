#!/usr/bin/env python3
"""
Test script for deployed Context Overflow MCP Server
"""

import requests
import json
import sys

def test_deployed_api(base_url):
    """Test the deployed MCP server API"""
    
    print(f"🚀 Testing Context Overflow MCP Server at: {base_url}")
    print("=" * 60)
    
    # Test 1: Health check
    print("\n1. Testing health endpoint...")
    try:
        response = requests.get(f"{base_url}/health", timeout=30)
        if response.status_code == 200:
            print("✅ Health check passed")
            print(f"   Response: {response.json()}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False
    
    # Test 2: Post a question
    print("\n2. Testing post question...")
    question_data = {
        "title": "How to deploy FastAPI applications to the cloud?",
        "content": "I need help understanding the best practices for deploying FastAPI applications to cloud platforms like Railway, Render, or Fly.io. What are the key considerations?",
        "tags": ["python", "fastapi", "deployment", "cloud"],
        "language": "python"
    }
    
    try:
        response = requests.post(
            f"{base_url}/mcp/post_question",
            json=question_data,
            timeout=30
        )
        if response.status_code == 200:
            question_id = response.json()["data"]["question_id"]
            print(f"✅ Question posted successfully (ID: {question_id})")
        else:
            print(f"❌ Post question failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Post question error: {e}")
        return False
    
    # Test 3: Get questions
    print("\n3. Testing get questions...")
    try:
        response = requests.get(f"{base_url}/mcp/get_questions?limit=5", timeout=30)
        if response.status_code == 200:
            questions = response.json()["data"]["questions"]
            print(f"✅ Retrieved {len(questions)} questions")
            if questions:
                print(f"   Latest question: {questions[0]['title'][:50]}...")
        else:
            print(f"❌ Get questions failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Get questions error: {e}")
        return False
    
    # Test 4: Post an answer
    print("\n4. Testing post answer...")
    answer_data = {
        "question_id": question_id,
        "content": "For deploying FastAPI applications, I recommend using Railway or Render for simplicity. Both offer free tiers and automatic deployments from GitHub.",
        "code_examples": [
            {
                "language": "python",
                "code": "# main.py\nimport os\nfrom fastapi import FastAPI\nimport uvicorn\n\napp = FastAPI()\n\n@app.get('/')\ndef root():\n    return {'message': 'Hello World'}\n\nif __name__ == '__main__':\n    port = int(os.getenv('PORT', 8000))\n    uvicorn.run('main:app', host='0.0.0.0', port=port)"
            }
        ],
        "author": "deployment-expert"
    }
    
    try:
        response = requests.post(
            f"{base_url}/mcp/post_answer",
            json=answer_data,
            timeout=30
        )
        if response.status_code == 200:
            answer_id = response.json()["data"]["answer_id"]
            print(f"✅ Answer posted successfully (ID: {answer_id})")
        else:
            print(f"❌ Post answer failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Post answer error: {e}")
        return False
    
    # Test 5: Vote on question
    print("\n5. Testing voting...")
    vote_data = {
        "target_id": question_id,
        "target_type": "question",
        "vote_type": "upvote",
        "user_id": "claude-code-tester"
    }
    
    try:
        response = requests.post(
            f"{base_url}/mcp/vote",
            json=vote_data,
            timeout=30
        )
        if response.status_code == 200:
            vote_total = response.json()["data"]["new_vote_total"]
            print(f"✅ Vote cast successfully (new total: {vote_total})")
        else:
            print(f"❌ Voting failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Voting error: {e}")
        return False
    
    # Test 6: Get answers
    print("\n6. Testing get answers...")
    try:
        response = requests.get(f"{base_url}/mcp/get_answers/{question_id}", timeout=30)
        if response.status_code == 200:
            answers = response.json()["data"]["answers"]
            print(f"✅ Retrieved {len(answers)} answers for question {question_id}")
            if answers:
                print(f"   Answer by: {answers[0]['author']}")
        else:
            print(f"❌ Get answers failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Get answers error: {e}")
        return False
    
    print("\n🎉 All tests passed! Your Context Overflow MCP Server is working perfectly!")
    print(f"\n📝 Your API is ready to use with Claude Code at: {base_url}")
    print("\n🔗 Available endpoints:")
    print(f"   • Health: {base_url}/health")
    print(f"   • Post Question: {base_url}/mcp/post_question")
    print(f"   • Get Questions: {base_url}/mcp/get_questions")
    print(f"   • Post Answer: {base_url}/mcp/post_answer")
    print(f"   • Get Answers: {base_url}/mcp/get_answers/:id")
    print(f"   • Vote: {base_url}/mcp/vote")
    
    return True

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python test_deployed.py <your-deployed-url>")
        print("Example: python test_deployed.py https://your-app.up.railway.app")
        sys.exit(1)
    
    base_url = sys.argv[1].rstrip('/')
    success = test_deployed_api(base_url)
    
    if not success:
        print("\n❌ Some tests failed. Please check your deployment.")
        sys.exit(1)