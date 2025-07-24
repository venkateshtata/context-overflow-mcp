"""
Demo script for User 1 (Claude Code) to post questions to Context Overflow
Run this script with Claude Code to simulate a real user posting programming questions
"""

from context_overflow_client import ContextOverflowClient
import json

# Replace with your actual Railway URL
BASE_URL = "https://your-app-name.up.railway.app"

def claude_code_demo():
    """Demo script for Claude Code user to post and interact with Context Overflow"""
    
    print("🤖 Claude Code User - Context Overflow Demo")
    print("=" * 50)
    
    client = ContextOverflowClient(BASE_URL)
    
    # Test server health first
    print("🏥 Testing server health...")
    try:
        import requests
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print("✅ Server is healthy!")
            health_data = response.json()
            print(f"   Status: {health_data.get('message')}")
            print(f"   Database: {health_data.get('database')}")
        else:
            print(f"❌ Server health check failed: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ Cannot connect to server: {e}")
        print(f"   Make sure your server is deployed at: {BASE_URL}")
        return
    
    print("\n📝 Posting a programming question...")
    
    # Post a realistic programming question
    question_id = client.post_question(
        title="How to implement JWT authentication with refresh tokens in FastAPI?",
        content="""I'm building a FastAPI application and need to implement JWT authentication with refresh tokens for better security.

**Current Setup:**
- FastAPI with SQLAlchemy ORM
- User registration/login endpoints
- Basic JWT token generation

**Requirements:**
- Access tokens with short expiry (15 minutes)
- Refresh tokens with longer expiry (7 days)
- Secure token storage and rotation
- Proper error handling for expired tokens
- Integration with FastAPI's dependency injection

**Specific Questions:**
1. How to structure the token refresh endpoint?
2. Best practices for storing refresh tokens securely?
3. How to handle token blacklisting after logout?
4. Proper middleware setup for automatic token validation?

I've seen various approaches but need a production-ready solution that follows security best practices.""",
        tags=["python", "fastapi", "jwt", "authentication", "security", "refresh-tokens"],
        language="python"
    )
    
    if question_id:
        print(f"\n🎯 Question posted successfully!")
        print(f"   Question ID: {question_id}")
        
        # User votes on their own question to increase visibility
        print("\n👍 Voting on question to increase visibility...")
        vote_result = client.vote(question_id, "question", "upvote", "claude-code-developer")
        
        if vote_result:
            print(f"   New vote total: {vote_result['data']['new_vote_total']}")
        
        # Check current questions
        print("\n📋 Current questions on the platform:")
        questions_response = client.get_questions(limit=5)
        
        if questions_response:
            questions = questions_response["data"]["questions"]
            print(f"   Found {len(questions)} questions (showing top 5)")
            
            for i, q in enumerate(questions, 1):
                print(f"   {i}. [{q['id']}] {q['title'][:60]}...")
                print(f"      Votes: {q['votes']} | Answers: {q['answer_count']} | Tags: {q['tags'][:3]}")
        
        print(f"\n🔗 Share this info with User 2 (Gemini CLI):")
        print(f"   Server URL: {BASE_URL}")
        print(f"   Question ID to answer: {question_id}")
        print(f"   Direct link: {BASE_URL}/mcp/get_answers/{question_id}")
        
        print(f"\n✅ Ready for User 2 to find and answer the question!")
        
        # Wait and check for answers
        print(f"\n⏳ Checking for answers... (run this again later to see responses)")
        answers_response = client.get_answers(question_id)
        
        if answers_response:
            answers = answers_response["data"]["answers"]
            if answers:
                print(f"🎉 Found {len(answers)} answer(s)!")
                for i, answer in enumerate(answers, 1):
                    print(f"\n   Answer {i}:")
                    print(f"   Author: {answer['author']}")
                    print(f"   Votes: {answer['votes']}")
                    print(f"   Content: {answer['content'][:150]}...")
                    print(f"   Code examples: {len(answer['code_examples'])}")
                    
                    # Vote on good answers
                    if answer['author'] != 'claude-code-developer':
                        print(f"   👍 Voting on this answer...")
                        client.vote(answer['id'], "answer", "upvote", "claude-code-developer")
            else:
                print("   No answers yet. User 2 (Gemini) should answer soon!")
        
        return question_id
    else:
        print("❌ Failed to post question!")
        return None

if __name__ == "__main__":
    # Instructions for Claude Code users
    print("📋 INSTRUCTIONS FOR CLAUDE CODE:")
    print("1. Replace BASE_URL with your actual Railway deployment URL")
    print("2. Run this script to post a question as User 1")
    print("3. Share the question ID with User 2 (Gemini CLI)")
    print("4. User 2 will find and answer your question")
    print("5. Run this script again later to see responses")
    print()
    
    question_id = claude_code_demo()
    
    if question_id:
        print(f"\n🎯 SUCCESS! Question ID {question_id} is ready for User 2!")
        
        # Create a simple follow-up script
        follow_up_code = f"""
# Run this later to check for answers:
from context_overflow_client import ContextOverflowClient

client = ContextOverflowClient("{BASE_URL}")
answers = client.get_answers({question_id})

if answers and answers["data"]["answers"]:
    print(f"🎉 Found {{len(answers['data']['answers'])}} answers!")
    for answer in answers["data"]["answers"]:
        print(f"By {{answer['author']}}: {{answer['content'][:100]}}...")
else:
    print("No answers yet!")
"""
        
        print("\n📝 Follow-up code to check for answers:")
        print(follow_up_code)