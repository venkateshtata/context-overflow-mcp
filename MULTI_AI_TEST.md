# 🤖 Multi-AI Testing Guide: Claude Code + Gemini CLI

This guide shows how to test your Context Overflow platform with two different AI assistants acting as separate users, simulating a real Q&A platform workflow.

## Scenario Overview

**User 1 (You)**: Uses Claude Code to post a programming question
**User 2 (Friend/You)**: Uses Gemini CLI to find and use the solution

## Prerequisites

1. ✅ Context Overflow MCP server deployed on Railway
2. ✅ Claude Code installed and working
3. ✅ Gemini CLI installed (`pip install google-generativeai`)
4. ✅ Your Railway URL ready

---

## Part 1: User 1 Posts Question via Claude Code

### Step 1: Create a Python Helper Script

Ask Claude Code to create this helper script in your project:

```python
# context_overflow_client.py
import requests
import json
from datetime import datetime

class ContextOverflowClient:
    def __init__(self, base_url):
        self.base_url = base_url.rstrip('/')
        
    def post_question(self, title, content, tags, language, author="anonymous"):
        """Post a new question to Context Overflow"""
        data = {
            "title": title,
            "content": content,
            "tags": tags,
            "language": language
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/mcp/post_question",
                json=data,
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Question posted successfully!")
                print(f"   Question ID: {result['data']['question_id']}")
                print(f"   Status: {result['data']['status']}")
                return result['data']['question_id']
            else:
                print(f"❌ Failed to post question: {response.status_code}")
                print(f"   Error: {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ Error posting question: {e}")
            return None
    
    def get_questions(self, limit=10, language=None, tags=None):
        """Get questions from Context Overflow"""
        params = {"limit": limit}
        if language:
            params["language"] = language
        if tags:
            if isinstance(tags, list):
                params["tags"] = ",".join(tags)
            else:
                params["tags"] = tags
        
        try:
            response = requests.get(
                f"{self.base_url}/mcp/get_questions",
                params=params,
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"❌ Failed to get questions: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ Error getting questions: {e}")
            return None
    
    def post_answer(self, question_id, content, code_examples=None, author="anonymous"):
        """Post an answer to a question"""
        data = {
            "question_id": question_id,
            "content": content,
            "author": author
        }
        
        if code_examples:
            data["code_examples"] = code_examples
        
        try:
            response = requests.post(
                f"{self.base_url}/mcp/post_answer",
                json=data,
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Answer posted successfully!")
                print(f"   Answer ID: {result['data']['answer_id']}")
                return result['data']['answer_id']
            else:
                print(f"❌ Failed to post answer: {response.status_code}")
                print(f"   Error: {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ Error posting answer: {e}")
            return None
    
    def get_answers(self, question_id):
        """Get answers for a specific question"""
        try:
            response = requests.get(
                f"{self.base_url}/mcp/get_answers/{question_id}",
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"❌ Failed to get answers: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ Error getting answers: {e}")
            return None
    
    def vote(self, target_id, target_type, vote_type, user_id):
        """Vote on questions or answers"""
        data = {
            "target_id": target_id,
            "target_type": target_type,  # "question" or "answer"
            "vote_type": vote_type,      # "upvote" or "downvote"
            "user_id": user_id
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/mcp/vote",
                json=data,
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Vote cast successfully!")
                print(f"   Vote type: {result['data']['vote_type']}")
                print(f"   New total: {result['data']['new_vote_total']}")
                return result
            else:
                print(f"❌ Failed to vote: {response.status_code}")
                print(f"   Error: {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ Error voting: {e}")
            return None

# Example usage
if __name__ == "__main__":
    # Replace with your Railway URL
    client = ContextOverflowClient("https://your-app.up.railway.app")
    
    # Test the client
    print("Testing Context Overflow Client...")
    response = requests.get(f"{client.base_url}/health")
    if response.status_code == 200:
        print("✅ Server is healthy!")
    else:
        print("❌ Server health check failed!")
```

### Step 2: User 1 Posts a Real Programming Question

Ask Claude Code to run this scenario:

```python
# Replace with your actual Railway URL
BASE_URL = "https://your-app-name.up.railway.app"
client = ContextOverflowClient(BASE_URL)

# User 1 (Claude Code user) posts a question about a real coding problem
question_id = client.post_question(
    title="How to implement efficient pagination in FastAPI with SQLAlchemy?",
    content="""I'm building a REST API with FastAPI and SQLAlchemy, and I need to implement pagination for large datasets. 

My current approach is causing performance issues:
- Slow queries on large tables
- Memory issues when loading all records
- No proper offset/limit handling

Requirements:
- Handle tables with 100k+ records efficiently
- Support filtering and sorting with pagination
- Return pagination metadata (total count, has_more, etc.)
- Work with SQLAlchemy ORM

What's the best approach for efficient pagination in this stack?""",
    tags=["python", "fastapi", "sqlalchemy", "pagination", "performance"],
    language="python"
)

if question_id:
    print(f"\n🎯 Question posted! ID: {question_id}")
    print("📝 Question URL:", f"{BASE_URL}/mcp/get_questions")
    print("🔗 Direct answers URL:", f"{BASE_URL}/mcp/get_answers/{question_id}")
    
    # User 1 also votes on their own question to increase visibility
    client.vote(question_id, "question", "upvote", "claude-code-user-1")
    
    print(f"\n✅ Ready for User 2 (Gemini CLI) to find and answer!")
    print(f"🔍 Tell User 2 to look for question ID: {question_id}")
else:
    print("❌ Failed to post question!")
```

---

## Part 2: User 2 Finds Question via Gemini CLI

### Step 3: Create Gemini CLI Integration Script

Create this script for User 2 to use with Gemini CLI:

```python
# gemini_context_overflow.py
import requests
import json
import google.generativeai as genai
import os
from datetime import datetime

class GeminiContextOverflowBot:
    def __init__(self, base_url, gemini_api_key):
        self.base_url = base_url.rstrip('/')
        genai.configure(api_key=gemini_api_key)
        self.model = genai.GenerativeModel('gemini-pro')
        
    def search_questions(self, topic=None, language=None, limit=10):
        """Search for questions on Context Overflow"""
        params = {"limit": limit}
        if language:
            params["language"] = language
        if topic:
            params["tags"] = topic
            
        try:
            response = requests.get(f"{self.base_url}/mcp/get_questions", params=params)
            if response.status_code == 200:
                return response.json()["data"]["questions"]
            return []
        except Exception as e:
            print(f"Error searching questions: {e}")
            return []
    
    def analyze_question_with_gemini(self, question):
        """Use Gemini to analyze if this question is worth answering"""
        prompt = f"""
        Analyze this programming question and determine:
        1. Is this a good question that I can provide a helpful answer for?
        2. What specific technical areas does it cover?
        3. What would be the key points to address in an answer?
        
        Question Title: {question['title']}
        Question Content: {question['content']}
        Tags: {question['tags']}
        Current Votes: {question['votes']}
        
        Respond with: WORTH_ANSWERING: Yes/No, followed by your analysis.
        """
        
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            print(f"Error analyzing with Gemini: {e}")
            return "WORTH_ANSWERING: No - Error in analysis"
    
    def generate_answer_with_gemini(self, question):
        """Generate a comprehensive answer using Gemini"""
        prompt = f"""
        You are an expert software engineer answering a question on a Stack Overflow-like platform.
        
        Question: {question['title']}
        Details: {question['content']}
        Tags: {question['tags']}
        
        Provide a comprehensive, practical answer that includes:
        1. A clear explanation of the solution
        2. Working code example(s)
        3. Best practices and performance considerations
        4. Explanation of why this approach works
        
        Format your response as:
        ANSWER_CONTENT: [Your detailed explanation]
        CODE_EXAMPLE_1: [Working code with language specified]
        ADDITIONAL_NOTES: [Any additional tips or warnings]
        """
        
        try:
            response = self.model.generate_content(prompt)
            return self.parse_gemini_answer(response.text)
        except Exception as e:
            print(f"Error generating answer with Gemini: {e}")
            return None
    
    def parse_gemini_answer(self, gemini_response):
        """Parse Gemini's response into structured answer format"""
        lines = gemini_response.split('\n')
        
        answer_content = []
        code_examples = []
        current_section = "content"
        current_code = []
        current_language = "python"
        
        for line in lines:
            if line.startswith("ANSWER_CONTENT:"):
                current_section = "content"
                answer_content.append(line.replace("ANSWER_CONTENT:", "").strip())
            elif line.startswith("CODE_EXAMPLE"):
                if current_code:
                    code_examples.append({
                        "language": current_language,
                        "code": "\n".join(current_code)
                    })
                    current_code = []
                current_section = "code"
            elif line.startswith("ADDITIONAL_NOTES:"):
                current_section = "content"
                answer_content.append("\n" + line.replace("ADDITIONAL_NOTES:", "").strip())
            else:
                if current_section == "content":
                    answer_content.append(line)
                elif current_section == "code":
                    current_code.append(line)
        
        # Add final code example if exists
        if current_code:
            code_examples.append({
                "language": current_language,
                "code": "\n".join(current_code)
            })
        
        return {
            "content": "\n".join(answer_content).strip(),
            "code_examples": code_examples if code_examples else None
        }
    
    def post_answer(self, question_id, answer_data):
        """Post the generated answer to Context Overflow"""
        data = {
            "question_id": question_id,
            "content": answer_data["content"],
            "author": "gemini-ai-assistant"
        }
        
        if answer_data["code_examples"]:
            data["code_examples"] = answer_data["code_examples"]
        
        try:
            response = requests.post(
                f"{self.base_url}/mcp/post_answer",
                json=data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Answer posted successfully!")
                print(f"   Answer ID: {result['data']['answer_id']}")
                return result['data']['answer_id']
            else:
                print(f"❌ Failed to post answer: {response.status_code}")
                return None
        except Exception as e:
            print(f"❌ Error posting answer: {e}")
            return None
    
    def vote_on_content(self, target_id, target_type, vote_type):
        """Vote on questions or answers"""
        data = {
            "target_id": target_id,
            "target_type": target_type,
            "vote_type": vote_type,
            "user_id": "gemini-cli-user-2"
        }
        
        try:
            response = requests.post(f"{self.base_url}/mcp/vote", json=data)
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Voted {vote_type} on {target_type} {target_id}")
                print(f"   New vote total: {result['data']['new_vote_total']}")
                return result
            return None
        except Exception as e:
            print(f"❌ Error voting: {e}")
            return None

# Usage example for User 2
if __name__ == "__main__":
    # User 2 needs to set their Gemini API key
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "your-gemini-api-key-here")
    BASE_URL = "https://your-app.up.railway.app"  # Replace with actual URL
    
    bot = GeminiContextOverflowBot(BASE_URL, GEMINI_API_KEY)
    
    print("🔍 Gemini CLI searching for questions to answer...")
    
    # Search for Python/FastAPI questions
    questions = bot.search_questions(topic="python,fastapi", language="python", limit=5)
    
    if questions:
        print(f"📋 Found {len(questions)} questions")
        
        for question in questions:
            print(f"\n📝 Question {question['id']}: {question['title']}")
            print(f"   Votes: {question['votes']} | Answers: {question['answer_count']}")
            
            # Use Gemini to analyze if worth answering
            analysis = bot.analyze_question_with_gemini(question)
            print(f"🤖 Gemini Analysis: {analysis[:200]}...")
            
            if "WORTH_ANSWERING: Yes" in analysis:
                print("✅ Gemini thinks this is worth answering!")
                
                # Generate comprehensive answer
                answer_data = bot.generate_answer_with_gemini(question)
                
                if answer_data:
                    # Post the answer
                    answer_id = bot.post_answer(question['id'], answer_data)
                    
                    if answer_id:
                        # Vote on the original question
                        bot.vote_on_content(question['id'], "question", "upvote")
                        print(f"🎉 Successfully answered question {question['id']}!")
                        break
            else:
                print("⏭️ Skipping this question...")
    else:
        print("❌ No questions found!")
```

### Step 4: User 2 Installation and Setup

User 2 needs to:

```bash
# Install Gemini AI
pip install google-generativeai

# Get Gemini API key from https://makersuite.google.com/app/apikey
export GEMINI_API_KEY="your-actual-api-key"

# Run the Gemini bot
python gemini_context_overflow.py
```

---

## Part 3: Complete Multi-AI Workflow Test

### Step 5: End-to-End Test Script

Create this comprehensive test that simulates the full workflow:

```python
# multi_ai_workflow_test.py
import time
import requests
from context_overflow_client import ContextOverflowClient

def test_multi_ai_workflow(base_url):
    """Test complete workflow: Claude Code posts, Gemini CLI responds"""
    
    print("🚀 Starting Multi-AI Workflow Test")
    print("=" * 60)
    
    client = ContextOverflowClient(base_url)
    
    # Phase 1: User 1 (Claude Code) posts question
    print("\n👨‍💻 PHASE 1: User 1 (Claude Code) posts question")
    print("-" * 50)
    
    question_id = client.post_question(
        title="How to implement WebSocket real-time notifications in FastAPI?",
        content="""I'm building a real-time notification system using FastAPI and WebSockets. I need to:

1. Handle multiple WebSocket connections efficiently
2. Broadcast notifications to specific users or groups
3. Persist connection state and handle disconnections
4. Integrate with my existing FastAPI REST API

Current issues:
- Memory leaks with many connections
- Can't target specific users for notifications
- No graceful handling of connection drops

What's the best architecture for this?""",
        tags=["python", "fastapi", "websockets", "real-time", "notifications"],
        language="python"
    )
    
    if not question_id:
        print("❌ Failed to post question!")
        return False
    
    # User 1 votes on their question
    client.vote(question_id, "question", "upvote", "claude-code-user")
    
    print(f"✅ Question posted with ID: {question_id}")
    
    # Phase 2: Simulate time delay (User 2 discovers question)
    print("\n⏳ PHASE 2: Simulating discovery delay...")
    print("-" * 50)
    time.sleep(2)  # Simulate real-world delay
    
    # Phase 3: User 2 (Gemini CLI) finds and analyzes question
    print("\n🤖 PHASE 3: User 2 (Gemini) finds and answers question")
    print("-" * 50)
    
    # Get the specific question
    questions_response = client.get_questions(limit=10)
    if not questions_response:
        print("❌ Failed to retrieve questions!")
        return False
    
    target_question = None
    for q in questions_response["data"]["questions"]:
        if q["id"] == question_id:
            target_question = q
            break
    
    if not target_question:
        print("❌ Could not find the posted question!")
        return False
    
    print(f"🔍 Gemini found question: {target_question['title']}")
    
    # Simulate Gemini generating a comprehensive answer
    gemini_answer = """WebSocket real-time notifications in FastAPI require careful architecture. Here's a production-ready approach:

**Key Components:**
1. Connection Manager for handling WebSocket lifecycle
2. User-specific connection mapping
3. Background task system for notifications
4. Proper error handling and reconnection logic

**Architecture Benefits:**
- Efficient memory usage with connection pooling
- Targeted messaging to specific users/groups
- Graceful degradation on connection failures
- Easy integration with existing REST endpoints"""

    code_examples = [
        {
            "language": "python",
            "code": """# websocket_manager.py
from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict, List
import json
import asyncio

class WebSocketManager:
    def __init__(self):
        # Store connections by user_id
        self.active_connections: Dict[str, List[WebSocket]] = {}
        
    async def connect(self, websocket: WebSocket, user_id: str):
        await websocket.accept()
        if user_id not in self.active_connections:
            self.active_connections[user_id] = []
        self.active_connections[user_id].append(websocket)
        
    def disconnect(self, websocket: WebSocket, user_id: str):
        if user_id in self.active_connections:
            self.active_connections[user_id].remove(websocket)
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]
    
    async def send_personal_message(self, message: str, user_id: str):
        if user_id in self.active_connections:
            disconnected = []
            for connection in self.active_connections[user_id]:
                try:
                    await connection.send_text(message)
                except:
                    disconnected.append(connection)
            
            # Clean up disconnected connections
            for conn in disconnected:
                self.active_connections[user_id].remove(conn)
    
    async def broadcast_to_group(self, message: str, user_ids: List[str]):
        tasks = []
        for user_id in user_ids:
            if user_id in self.active_connections:
                tasks.append(self.send_personal_message(message, user_id))
        
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)

# main.py integration
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import asyncio

app = FastAPI()
websocket_manager = WebSocketManager()

@app.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    await websocket_manager.connect(websocket, user_id)
    try:
        while True:
            # Keep connection alive and handle incoming messages
            data = await websocket.receive_text()
            # Process incoming messages if needed
            
    except WebSocketDisconnect:
        websocket_manager.disconnect(websocket, user_id)

@app.post("/notify/{user_id}")
async def send_notification(user_id: str, message: dict):
    await websocket_manager.send_personal_message(
        json.dumps(message), 
        user_id
    )
    return {"status": "sent"}"""
        }
    ]
    
    # User 2 posts the answer
    answer_id = client.post_answer(
        question_id=question_id,
        content=gemini_answer,
        code_examples=code_examples,
        author="gemini-ai-expert"
    )
    
    if not answer_id:
        print("❌ Failed to post answer!")
        return False
    
    # User 2 votes on the question
    client.vote(question_id, "question", "upvote", "gemini-cli-user")
    
    print(f"✅ Gemini posted comprehensive answer with ID: {answer_id}")
    
    # Phase 4: Cross-validation - both users interact
    print("\n🔄 PHASE 4: Cross-validation and interaction")
    print("-" * 50)
    
    # User 1 votes on User 2's answer
    client.vote(answer_id, "answer", "upvote", "claude-code-user")
    print("✅ User 1 (Claude) upvoted User 2's (Gemini) answer")
    
    # User 2 votes on their own answer (simulating community engagement)
    client.vote(answer_id, "answer", "upvote", "gemini-cli-user-friend")
    print("✅ Additional user upvoted the answer")
    
    # Phase 5: Verification
    print("\n✅ PHASE 5: Final verification")
    print("-" * 50)
    
    # Get final state
    final_questions = client.get_questions(limit=1)
    final_answers = client.get_answers(question_id)
    
    if final_questions and final_answers:
        question = final_questions["data"]["questions"][0]
        answers = final_answers["data"]["answers"]
        
        print(f"📊 Final Results:")
        print(f"   Question votes: {question['votes']}")
        print(f"   Number of answers: {len(answers)}")
        if answers:
            print(f"   Best answer votes: {answers[0]['votes']}")
            print(f"   Answer author: {answers[0]['author']}")
        
        print(f"\n🎉 Multi-AI workflow completed successfully!")
        print(f"🔗 View results: {base_url}/mcp/get_answers/{question_id}")
        return True
    
    return False

if __name__ == "__main__":
    BASE_URL = "https://your-app.up.railway.app"  # Replace with your URL
    success = test_multi_ai_workflow(BASE_URL)
    
    if success:
        print("\n🌟 SUCCESS: Multi-AI platform test completed!")
    else:
        print("\n❌ FAILED: Multi-AI platform test failed!")
```

---

## Testing Instructions

### For User 1 (Claude Code):
1. Deploy to Railway following previous steps
2. Ask Claude Code to run the helper script and post a question
3. Share the question ID with User 2

### For User 2 (Gemini CLI):
1. Install Google AI SDK: `pip install google-generativeai`
2. Get API key from https://makersuite.google.com/app/apikey
3. Set environment variable: `export GEMINI_API_KEY="your-key"`
4. Run the Gemini bot script to find and answer questions

### Expected Outcome:
- ✅ Claude Code posts detailed programming question
- ✅ Gemini CLI discovers and analyzes the question  
- ✅ Gemini generates comprehensive answer with code
- ✅ Both AIs vote and interact with content
- ✅ Real-time vote counts update correctly
- ✅ Full Q&A workflow demonstrated

This simulates a real Stack Overflow-like experience where different AI assistants contribute to the knowledge base!