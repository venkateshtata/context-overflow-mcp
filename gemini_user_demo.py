"""
Demo script for User 2 (Gemini CLI) to find and answer questions on Context Overflow
This simulates a Gemini AI user discovering and responding to Claude Code user's questions
"""

import requests
import json
import os
from context_overflow_client import ContextOverflowClient

# Replace with your actual Railway URL
BASE_URL = "https://your-app-name.up.railway.app"

class GeminiSimulator:
    """Simulates Gemini AI behavior for answering programming questions"""
    
    def __init__(self, base_url):
        self.client = ContextOverflowClient(base_url)
        self.base_url = base_url
    
    def analyze_question(self, question):
        """Simulate Gemini analyzing if a question is worth answering"""
        print(f"🔍 Analyzing question: {question['title']}")
        print(f"   Tags: {question['tags']}")
        print(f"   Current votes: {question['votes']}")
        print(f"   Current answers: {question['answer_count']}")
        
        # Simple heuristics for whether to answer
        worth_answering = (
            question['answer_count'] < 3 and  # Not too many answers already
            question['votes'] >= 0 and        # Question has positive reception
            len(question['content']) > 100    # Substantial question
        )
        
        if worth_answering:
            print("✅ This question looks worth answering!")
            return True
        else:
            print("⏭️ Skipping this question")
            return False
    
    def generate_jwt_answer(self, question):
        """Generate a comprehensive answer for JWT authentication questions"""
        
        if "jwt" in question['title'].lower() or "authentication" in question['title'].lower():
            return {
                "content": """Here's a production-ready implementation of JWT authentication with refresh tokens in FastAPI:

**Architecture Overview:**
The solution uses a dual-token approach:
- **Access Token**: Short-lived (15 minutes) for API access
- **Refresh Token**: Long-lived (7 days) for getting new access tokens

**Key Security Features:**
1. Automatic token rotation on refresh
2. Secure HTTP-only cookies for refresh tokens
3. Token blacklisting for logout
4. Rate limiting on auth endpoints
5. Proper CORS and CSRF protection

**Implementation Benefits:**
- Follows OWASP security guidelines
- Integrates seamlessly with FastAPI dependencies
- Supports both cookie and header-based auth
- Includes comprehensive error handling
- Production-ready with proper logging""",
                
                "code_examples": [
                    {
                        "language": "python",
                        "code": """# auth.py - JWT Token Management
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import jwt
from fastapi import HTTPException, status
from passlib.context import CryptContext
import secrets

class JWTManager:
    def __init__(self, secret_key: str, algorithm: str = "HS256"):
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        self.blacklisted_tokens = set()  # In production, use Redis
    
    def create_access_token(self, data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=15)
        
        to_encode.update({
            "exp": expire,
            "type": "access",
            "jti": secrets.token_urlsafe(32)  # Unique token ID
        })
        
        return jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
    
    def create_refresh_token(self, data: Dict[str, Any]) -> str:
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=7)
        
        to_encode.update({
            "exp": expire,
            "type": "refresh",
            "jti": secrets.token_urlsafe(32)
        })
        
        return jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
    
    def verify_token(self, token: str, token_type: str = "access") -> Dict[str, Any]:
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            
            # Check if token is blacklisted
            if payload.get("jti") in self.blacklisted_tokens:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token has been revoked"
                )
            
            # Verify token type
            if payload.get("type") != token_type:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail=f"Invalid token type. Expected {token_type}"
                )
            
            return payload
            
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired"
            )
        except jwt.JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate token"
            )
    
    def blacklist_token(self, token: str):
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            self.blacklisted_tokens.add(payload.get("jti"))
        except jwt.JWTError:
            pass  # Invalid token, ignore"""
                    },
                    {
                        "language": "python", 
                        "code": """# main.py - FastAPI Integration
from fastapi import FastAPI, Depends, HTTPException, status, Response, Cookie
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from datetime import timedelta
import os

app = FastAPI()
security = HTTPBearer()

# Initialize JWT manager
JWT_SECRET = os.getenv("JWT_SECRET", "your-super-secret-key-change-in-production")
jwt_manager = JWTManager(JWT_SECRET)

# Dependency to get current user from access token
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    token = credentials.credentials
    payload = jwt_manager.verify_token(token, "access")
    
    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )
    
    user = get_user_by_id(db, user_id=user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    return user

@app.post("/auth/login")
async def login(user_credentials: UserLogin, response: Response, db: Session = Depends(get_db)):
    # Verify user credentials
    user = authenticate_user(db, user_credentials.username, user_credentials.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )
    
    # Create tokens
    access_token = jwt_manager.create_access_token(
        data={"sub": str(user.id), "username": user.username}
    )
    refresh_token = jwt_manager.create_refresh_token(
        data={"sub": str(user.id)}
    )
    
    # Set refresh token as HTTP-only cookie
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=True,  # HTTPS only in production
        samesite="strict",
        max_age=7 * 24 * 60 * 60  # 7 days
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": 900  # 15 minutes
    }

@app.post("/auth/refresh")
async def refresh_token(
    response: Response,
    refresh_token: Optional[str] = Cookie(None),
    db: Session = Depends(get_db)
):
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token not found"
        )
    
    # Verify refresh token
    payload = jwt_manager.verify_token(refresh_token, "refresh")
    user_id = payload.get("sub")
    
    user = get_user_by_id(db, user_id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    # Blacklist old refresh token
    jwt_manager.blacklist_token(refresh_token)
    
    # Create new tokens
    new_access_token = jwt_manager.create_access_token(
        data={"sub": str(user.id), "username": user.username}
    )
    new_refresh_token = jwt_manager.create_refresh_token(
        data={"sub": str(user.id)}
    )
    
    # Set new refresh token cookie
    response.set_cookie(
        key="refresh_token",
        value=new_refresh_token,
        httponly=True,
        secure=True,
        samesite="strict",
        max_age=7 * 24 * 60 * 60
    )
    
    return {
        "access_token": new_access_token,
        "token_type": "bearer",
        "expires_in": 900
    }

@app.post("/auth/logout")
async def logout(
    response: Response,
    current_user: User = Depends(get_current_user),
    refresh_token: Optional[str] = Cookie(None)
):
    # Blacklist refresh token if present
    if refresh_token:
        jwt_manager.blacklist_token(refresh_token)
    
    # Clear refresh token cookie
    response.delete_cookie(key="refresh_token")
    
    return {"message": "Successfully logged out"}

@app.get("/protected")
async def protected_route(current_user: User = Depends(get_current_user)):
    return {
        "message": f"Hello {current_user.username}",
        "user_id": current_user.id
    }"""
                    }
                ]
            }
        
        return self.generate_generic_answer(question)
    
    def generate_generic_answer(self, question):
        """Generate a generic helpful answer for programming questions"""
        return {
            "content": f"""Great question about {question['title']}! 

Based on your requirements, here's a comprehensive approach to solve this problem:

**Key Considerations:**
1. **Architecture**: Design with scalability and maintainability in mind
2. **Security**: Follow best practices for the technology stack
3. **Performance**: Consider efficiency and resource usage
4. **Error Handling**: Implement robust error management
5. **Testing**: Ensure comprehensive test coverage

**Recommended Approach:**
The solution should balance simplicity with robustness. Start with a minimal viable implementation and iterate based on specific requirements.

**Implementation Strategy:**
- Begin with core functionality
- Add proper error handling and validation
- Implement comprehensive logging
- Add monitoring and metrics
- Document the solution thoroughly

**Best Practices:**
- Follow the principle of least privilege
- Use established patterns and libraries
- Implement proper separation of concerns
- Consider future maintenance and scaling needs

This approach provides a solid foundation that can be extended based on your specific use case.""",
            
            "code_examples": [
                {
                    "language": "python",
                    "code": f"""# Example implementation for: {question['title']}
# This is a starting template - customize based on your specific needs

class Solution:
    def __init__(self):
        self.setup_components()
    
    def setup_components(self):
        \"\"\"Initialize required components\"\"\"
        pass
    
    def main_functionality(self, *args, **kwargs):
        \"\"\"Core implementation logic\"\"\"
        try:
            # Implementation goes here
            result = self.process_request(*args, **kwargs)
            return self.format_response(result)
        
        except Exception as e:
            self.handle_error(e)
            raise
    
    def process_request(self, *args, **kwargs):
        \"\"\"Process the main request\"\"\"
        # Add your specific logic here
        return {{"status": "success", "data": "processed"}}
    
    def format_response(self, result):
        \"\"\"Format the response for consistency\"\"\"
        return {{
            "success": True,
            "data": result,
            "timestamp": "2024-01-01T00:00:00Z"
        }}
    
    def handle_error(self, error):
        \"\"\"Handle errors gracefully\"\"\"
        print(f"Error occurred: {{error}}")
        # Add logging, monitoring, etc.

# Usage example
solution = Solution()
result = solution.main_functionality()
print(result)"""
                }
            ]
        }
    
    def search_and_answer(self):
        """Main method to search for questions and provide answers"""
        print("🤖 Gemini CLI User - Searching for questions to answer")
        print("=" * 60)
        
        # Search for questions
        print("🔍 Searching for recent programming questions...")
        questions_response = self.client.get_questions(limit=10)
        
        if not questions_response:
            print("❌ Could not retrieve questions!")
            return
        
        questions = questions_response["data"]["questions"]
        print(f"📋 Found {len(questions)} questions")
        
        # Analyze and answer questions
        answered_count = 0
        for question in questions:
            print(f"\n📝 Question {question['id']}: {question['title']}")
            
            if self.analyze_question(question):
                # Generate answer based on question content
                if "jwt" in question['title'].lower() or "auth" in question['title'].lower():
                    answer_data = self.generate_jwt_answer(question)
                else:
                    answer_data = self.generate_generic_answer(question)
                
                # Post the answer
                print("🤖 Generating comprehensive answer...")
                answer_id = self.client.post_answer(
                    question_id=question['id'],
                    content=answer_data["content"],
                    code_examples=answer_data["code_examples"],
                    author="gemini-ai-expert"
                )
                
                if answer_id:
                    # Vote on the original question
                    self.client.vote(question['id'], "question", "upvote", "gemini-cli-user")
                    
                    print(f"✅ Successfully answered question {question['id']}!")
                    answered_count += 1
                    
                    # Only answer one question in demo
                    break
        
        if answered_count == 0:
            print("ℹ️ No suitable questions found to answer at this time.")
        else:
            print(f"\n🎉 Successfully answered {answered_count} question(s)!")
            print("🔄 The Claude Code user can now see the response!")

def gemini_demo():
    """Main demo function for Gemini CLI user"""
    
    print("📋 GEMINI CLI USER INSTRUCTIONS:")
    print("1. This simulates Gemini AI finding and answering questions")
    print("2. It will search for questions posted by Claude Code users")
    print("3. Generate comprehensive answers with code examples")
    print("4. Vote and interact with the platform")
    print()
    
    # Test server connection
    print("🏥 Testing server connection...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print("✅ Server is healthy!")
        else:
            print(f"❌ Server issue: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ Cannot connect to server: {e}")
        print(f"   Make sure the server is running at: {BASE_URL}")
        return
    
    # Run the Gemini simulator
    gemini = GeminiSimulator(BASE_URL)
    gemini.search_and_answer()

if __name__ == "__main__":
    gemini_demo()"""