"""
Context Overflow Python Client
Helper class for interacting with the Context Overflow MCP API
"""

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
        print(f"Response: {response.json()}")
    else:
        print("❌ Server health check failed!")