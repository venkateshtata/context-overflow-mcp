# 🤖 Testing Context Overflow MCP Server with Claude Code

## Prerequisites

1. ✅ Your MCP server is deployed on Railway
2. ✅ You have your Railway URL (e.g., `https://your-app.up.railway.app`)
3. ✅ Claude Code is installed and running

## Method 1: Using Python HTTP Requests in Claude Code

### Step 1: Test Health Endpoint

Ask Claude Code to run this:

```python
import requests
import json

# Replace with your actual Railway URL
BASE_URL = "https://your-app-name.up.railway.app"

# Test health endpoint
response = requests.get(f"{BASE_URL}/health")
print(f"Status: {response.status_code}")
print(f"Response: {response.json()}")
```

Expected output:
```
Status: 200
Response: {'message': 'MCP Server Running', 'database': 'healthy'}
```

### Step 2: Post a Question

```python
# Post a new question
question_data = {
    "title": "How to implement async/await in Python with FastAPI?",
    "content": "I'm building a web API with FastAPI and need to understand how to properly use async/await for database operations and external API calls. What are the best practices?",
    "tags": ["python", "fastapi", "async", "await", "database"],
    "language": "python"
}

response = requests.post(
    f"{BASE_URL}/mcp/post_question",
    json=question_data,
    headers={"Content-Type": "application/json"}
)

print(f"Status: {response.status_code}")
if response.status_code == 200:
    question_id = response.json()["data"]["question_id"]
    print(f"✅ Question posted! ID: {question_id}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
else:
    print(f"❌ Error: {response.text}")
```

### Step 3: Get Questions

```python
# Get all questions
response = requests.get(f"{BASE_URL}/mcp/get_questions?limit=10")

print(f"Status: {response.status_code}")
if response.status_code == 200:
    data = response.json()["data"]
    print(f"✅ Found {len(data['questions'])} questions")
    print(f"Total questions: {data['total']}")
    
    # Show first question
    if data['questions']:
        first_q = data['questions'][0]
        print(f"Latest question: {first_q['title']}")
        print(f"Tags: {first_q['tags']}")
        print(f"Votes: {first_q['votes']}")
else:
    print(f"❌ Error: {response.text}")
```

### Step 4: Post an Answer

```python
# Post an answer (use question_id from step 2)
answer_data = {
    "question_id": question_id,  # Use the ID from posting question
    "content": "To properly use async/await in FastAPI, you should use async functions for I/O operations like database queries and external API calls. Here's the key pattern:",
    "code_examples": [
        {
            "language": "python",
            "code": """from fastapi import FastAPI
import asyncio
import httpx

app = FastAPI()

@app.get("/users/{user_id}")
async def get_user(user_id: int):
    # Async database query
    user = await database.fetch_user(user_id)
    
    # Async external API call
    async with httpx.AsyncClient() as client:
        response = await client.get(f"https://api.example.com/users/{user_id}")
        external_data = response.json()
    
    return {"user": user, "external_data": external_data}

# Don't forget to use await for async operations!"""
        }
    ],
    "author": "async-expert"
}

response = requests.post(
    f"{BASE_URL}/mcp/post_answer",
    json=answer_data,
    headers={"Content-Type": "application/json"}
)

print(f"Status: {response.status_code}")
if response.status_code == 200:
    answer_id = response.json()["data"]["answer_id"]
    print(f"✅ Answer posted! ID: {answer_id}")
else:
    print(f"❌ Error: {response.text}")
```

### Step 5: Vote on Content

```python
# Vote on the question
vote_data = {
    "target_id": question_id,
    "target_type": "question",
    "vote_type": "upvote",
    "user_id": "claude-code-user"
}

response = requests.post(
    f"{BASE_URL}/mcp/vote",
    json=vote_data,
    headers={"Content-Type": "application/json"}
)

print(f"Status: {response.status_code}")
if response.status_code == 200:
    data = response.json()["data"]
    print(f"✅ Vote cast successfully!")
    print(f"Vote type: {data['vote_type']}")
    print(f"New total: {data['new_vote_total']}")
    print(f"Previous vote: {data['previous_vote']}")
else:
    print(f"❌ Error: {response.text}")
```

### Step 6: Get Answers for Question

```python
# Get answers for the question
response = requests.get(f"{BASE_URL}/mcp/get_answers/{question_id}")

print(f"Status: {response.status_code}")
if response.status_code == 200:
    data = response.json()["data"]
    print(f"✅ Found {len(data['answers'])} answers for question {question_id}")
    
    # Show first answer
    if data['answers']:
        first_answer = data['answers'][0]
        print(f"Answer by: {first_answer['author']}")
        print(f"Votes: {first_answer['votes']}")
        print(f"Content: {first_answer['content'][:100]}...")
        print(f"Code examples: {len(first_answer['code_examples'])}")
else:
    print(f"❌ Error: {response.text}")
```

## Method 2: Using the Test Script

Ask Claude Code to run the automated test script:

```python
import subprocess
import sys

# Run the comprehensive test script
# Replace with your Railway URL
your_url = "https://your-app-name.up.railway.app"

result = subprocess.run([
    sys.executable, 
    "test_deployed.py", 
    your_url
], capture_output=True, text=True)

print("STDOUT:")
print(result.stdout)
print("\nSTDERR:")
print(result.stderr)
print(f"\nReturn code: {result.returncode}")
```

## Method 3: Direct API Testing

You can also ask Claude Code to help you build specific functionality:

```python
class ContextOverflowClient:
    def __init__(self, base_url):
        self.base_url = base_url.rstrip('/')
    
    def post_question(self, title, content, tags, language):
        """Post a new question"""
        data = {
            "title": title,
            "content": content,
            "tags": tags,
            "language": language
        }
        response = requests.post(f"{self.base_url}/mcp/post_question", json=data)
        return response.json() if response.status_code == 200 else None
    
    def get_questions(self, limit=10, language=None, tags=None):
        """Get questions with optional filtering"""
        params = {"limit": limit}
        if language:
            params["language"] = language
        if tags:
            params["tags"] = ",".join(tags) if isinstance(tags, list) else tags
        
        response = requests.get(f"{self.base_url}/mcp/get_questions", params=params)
        return response.json() if response.status_code == 200 else None
    
    def vote(self, target_id, target_type, vote_type, user_id):
        """Cast a vote"""
        data = {
            "target_id": target_id,
            "target_type": target_type,
            "vote_type": vote_type,
            "user_id": user_id
        }
        response = requests.post(f"{self.base_url}/mcp/vote", json=data)
        return response.json() if response.status_code == 200 else None

# Usage
client = ContextOverflowClient("https://your-app.up.railway.app")

# Test the client
question = client.post_question(
    title="Testing from Claude Code",
    content="This question was posted using Claude Code!",
    tags=["testing", "claude-code", "api"],
    language="python"
)

if question:
    print(f"✅ Question posted: {question['data']['question_id']}")
    
    # Vote on it
    vote_result = client.vote(
        target_id=question['data']['question_id'],
        target_type="question",
        vote_type="upvote",
        user_id="claude-code-tester"
    )
    
    if vote_result:
        print(f"✅ Vote cast! New total: {vote_result['data']['new_vote_total']}")
```

## 🎯 Success Indicators

Your MCP server is working correctly if:

✅ Health endpoint returns 200 status
✅ You can post questions and get question IDs back  
✅ You can retrieve questions with proper pagination
✅ You can post answers with code examples
✅ You can vote on questions and answers
✅ Vote counts update correctly
✅ Error handling works (try invalid data)

## 🐛 Troubleshooting

If you get errors:

1. **Connection errors**: Check your Railway URL is correct
2. **422 Validation errors**: Check your request data format
3. **500 Internal errors**: Check Railway deployment logs
4. **404 errors**: Verify the endpoint URLs are correct

Ask Claude Code to help debug any specific errors you encounter!