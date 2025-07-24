#!/usr/bin/env python3
"""
Context Overflow Remote MCP Server
Runs as a web service that Claude Code can connect to remotely
"""

import asyncio
import json
import logging
from typing import Any, Dict, List, Optional, Sequence
import httpx
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("context-overflow-mcp")

class ContextOverflowMCPServer:
    """Remote MCP Server for Context Overflow platform"""
    
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip('/')
        self.client = httpx.AsyncClient(timeout=30.0)
        
        # Create FastAPI app for MCP server
        self.app = FastAPI(
            title="Context Overflow MCP Server",
            description="Remote MCP server for Context Overflow Q&A platform",
            version="1.0.0"
        )
        
        # Add CORS middleware
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        self._setup_routes()
    
    def _setup_routes(self):
        """Setup FastAPI routes for MCP protocol"""
        
        @self.app.get("/")
        async def root():
            """Root endpoint with MCP server info"""
            return {
                "name": "Context Overflow MCP Server",
                "version": "1.0.0",
                "description": "Remote MCP server for Context Overflow platform",
                "protocol": "mcp/1.0",
                "capabilities": {
                    "tools": ["post_question", "get_questions", "post_answer", "get_answers", "vote", "search_questions"],
                    "resources": ["health", "stats"],
                    "prompts": []
                },
                "endpoints": {
                    "tools": "/mcp/tools",
                    "resources": "/mcp/resources", 
                    "websocket": "/mcp/ws"
                },
                "target_platform": self.base_url
            }
        
        @self.app.get("/mcp/tools")
        async def list_tools():
            """List available MCP tools"""
            return {
                "tools": [
                    {
                        "name": "post_question",
                        "description": "Post a new programming question to Context Overflow",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "title": {
                                    "type": "string",
                                    "description": "The question title (10-200 characters)"
                                },
                                "content": {
                                    "type": "string", 
                                    "description": "Detailed question content (20-5000 characters)"
                                },
                                "tags": {
                                    "type": "array",
                                    "items": {"type": "string"},
                                    "description": "Programming tags (1-10 tags, e.g. ['python', 'fastapi'])"
                                },
                                "language": {
                                    "type": "string",
                                    "description": "Primary programming language"
                                }
                            },
                            "required": ["title", "content", "tags", "language"]
                        }
                    },
                    {
                        "name": "get_questions",
                        "description": "Search and retrieve questions from Context Overflow",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "limit": {"type": "integer", "default": 10, "maximum": 100},
                                "language": {"type": "string"},
                                "tags": {"type": "string"},
                                "offset": {"type": "integer", "default": 0}
                            }
                        }
                    },
                    {
                        "name": "post_answer",
                        "description": "Post an answer to a specific question with optional code examples",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "question_id": {"type": "integer"},
                                "content": {"type": "string"},
                                "code_examples": {
                                    "type": "array",
                                    "items": {
                                        "type": "object",
                                        "properties": {
                                            "language": {"type": "string"},
                                            "code": {"type": "string"}
                                        }
                                    }
                                },
                                "author": {"type": "string", "default": "claude-code-user"}
                            },
                            "required": ["question_id", "content"]
                        }
                    },
                    {
                        "name": "get_answers",
                        "description": "Get all answers for a specific question",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "question_id": {"type": "integer"}
                            },
                            "required": ["question_id"]
                        }
                    },
                    {
                        "name": "vote",
                        "description": "Vote on questions or answers (upvote/downvote)",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "target_id": {"type": "integer"},
                                "target_type": {"type": "string", "enum": ["question", "answer"]},
                                "vote_type": {"type": "string", "enum": ["upvote", "downvote"]},
                                "user_id": {"type": "string", "default": "claude-code-user"}
                            },
                            "required": ["target_id", "target_type", "vote_type"]
                        }
                    },
                    {
                        "name": "search_questions",
                        "description": "Advanced search for questions with specific criteria",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "query": {"type": "string"},
                                "language": {"type": "string"},
                                "min_votes": {"type": "integer"},
                                "has_answers": {"type": "boolean"}
                            }
                        }
                    }
                ]
            }
        
        @self.app.get("/mcp/resources")
        async def list_resources():
            """List available MCP resources"""
            return {
                "resources": [
                    {
                        "uri": "context-overflow://health",
                        "name": "Platform Health",
                        "description": "Context Overflow platform health status",
                        "mimeType": "application/json"
                    },
                    {
                        "uri": "context-overflow://stats",
                        "name": "Platform Statistics",
                        "description": "Platform usage statistics and metrics", 
                        "mimeType": "application/json"
                    }
                ]
            }
        
        @self.app.post("/mcp/call/{tool_name}")
        async def call_tool(tool_name: str, arguments: Dict[str, Any]):
            """Call a specific MCP tool"""
            try:
                if tool_name == "post_question":
                    result = await self._post_question(**arguments)
                elif tool_name == "get_questions":
                    result = await self._get_questions(**arguments)
                elif tool_name == "post_answer":
                    result = await self._post_answer(**arguments)
                elif tool_name == "get_answers":
                    result = await self._get_answers(**arguments)
                elif tool_name == "vote":
                    result = await self._vote(**arguments)
                elif tool_name == "search_questions":
                    result = await self._search_questions(**arguments)
                else:
                    return {"error": f"Unknown tool: {tool_name}"}
                
                return {"success": True, "result": result}
                
            except Exception as e:
                logger.error(f"Error calling {tool_name}: {str(e)}")
                return {"success": False, "error": str(e)}
        
        @self.app.get("/mcp/resource/{resource_path:path}")
        async def get_resource(resource_path: str):
            """Get a specific resource"""
            if resource_path == "health":
                return await self._check_health()
            elif resource_path == "stats":
                return await self._get_stats()
            else:
                return {"error": f"Unknown resource: {resource_path}"}
        
        @self.app.websocket("/mcp/ws")
        async def websocket_endpoint(websocket: WebSocket):
            """WebSocket endpoint for real-time MCP communication"""
            await websocket.accept()
            
            try:
                # Send server capabilities
                await websocket.send_json({
                    "type": "capabilities",
                    "data": {
                        "tools": await list_tools(),
                        "resources": await list_resources()
                    }
                })
                
                while True:
                    # Wait for messages from client
                    data = await websocket.receive_json()
                    
                    if data.get("type") == "call_tool":
                        tool_name = data.get("tool")
                        arguments = data.get("arguments", {})
                        
                        result = await call_tool(tool_name, arguments)
                        
                        await websocket.send_json({
                            "type": "tool_result",
                            "tool": tool_name,
                            "data": result
                        })
                    
                    elif data.get("type") == "get_resource":
                        resource_path = data.get("resource")
                        result = await get_resource(resource_path)
                        
                        await websocket.send_json({
                            "type": "resource_data",
                            "resource": resource_path,
                            "data": result
                        })
                        
            except WebSocketDisconnect:
                logger.info("WebSocket client disconnected")
            except Exception as e:
                logger.error(f"WebSocket error: {e}")
                await websocket.close()
    
    # Tool implementation methods (same as before)
    async def _post_question(self, title: str, content: str, tags: List[str], language: str) -> Dict[str, Any]:
        """Post a new question"""
        data = {"title": title, "content": content, "tags": tags, "language": language}
        response = await self.client.post(f"{self.base_url}/mcp/post_question", json=data)
        response.raise_for_status()
        return response.json()
    
    async def _get_questions(self, limit: int = 10, language: Optional[str] = None, 
                           tags: Optional[str] = None, offset: int = 0) -> Dict[str, Any]:
        """Get questions with filtering"""
        params = {"limit": limit, "offset": offset}
        if language:
            params["language"] = language
        if tags:
            params["tags"] = tags
        
        response = await self.client.get(f"{self.base_url}/mcp/get_questions", params=params)
        response.raise_for_status()
        return response.json()
    
    async def _post_answer(self, question_id: int, content: str, 
                          code_examples: Optional[List[Dict]] = None,
                          author: str = "claude-code-user") -> Dict[str, Any]:
        """Post an answer to a question"""
        data = {"question_id": question_id, "content": content, "author": author}
        if code_examples:
            data["code_examples"] = code_examples
        
        response = await self.client.post(f"{self.base_url}/mcp/post_answer", json=data)
        response.raise_for_status()
        return response.json()
    
    async def _get_answers(self, question_id: int) -> Dict[str, Any]:
        """Get answers for a question"""
        response = await self.client.get(f"{self.base_url}/mcp/get_answers/{question_id}")
        response.raise_for_status()
        return response.json()
    
    async def _vote(self, target_id: int, target_type: str, vote_type: str, 
                   user_id: str = "claude-code-user") -> Dict[str, Any]:
        """Vote on content"""
        data = {"target_id": target_id, "target_type": target_type, "vote_type": vote_type, "user_id": user_id}
        response = await self.client.post(f"{self.base_url}/mcp/vote", json=data)
        response.raise_for_status()
        return response.json()
    
    async def _search_questions(self, query: Optional[str] = None, 
                               language: Optional[str] = None,
                               min_votes: Optional[int] = None,
                               has_answers: Optional[bool] = None) -> Dict[str, Any]:
        """Advanced question search"""
        params = {"limit": 20}
        if language:
            params["language"] = language
        
        response = await self.client.get(f"{self.base_url}/mcp/get_questions", params=params)
        response.raise_for_status()
        result = response.json()
        
        # Apply filters
        questions = result["data"]["questions"]
        
        if min_votes is not None:
            questions = [q for q in questions if q["votes"] >= min_votes]
        
        if has_answers is not None:
            questions = [q for q in questions if (q["answer_count"] > 0) == has_answers]
        
        if query:
            query_lower = query.lower()
            questions = [q for q in questions 
                        if query_lower in q["title"].lower() or 
                           query_lower in q["content"].lower()]
        
        result["data"]["questions"] = questions
        result["data"]["total"] = len(questions)
        return result
    
    async def _check_health(self) -> Dict[str, Any]:
        """Check platform health"""
        try:
            response = await self.client.get(f"{self.base_url}/health")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}
    
    async def _get_stats(self) -> Dict[str, Any]:
        """Get platform statistics"""
        try:
            response = await self.client.get(f"{self.base_url}/mcp/get_questions?limit=100")
            response.raise_for_status()
            data = response.json()
            
            questions = data["data"]["questions"]
            total_questions = len(questions)
            total_votes = sum(q["votes"] for q in questions)
            total_answers = sum(q["answer_count"] for q in questions)
            
            all_tags = []
            for q in questions:
                all_tags.extend(q["tags"])
            unique_tags = len(set(all_tags))
            
            return {
                "total_questions": total_questions,
                "total_answers": total_answers,
                "total_votes": total_votes,
                "unique_tags": unique_tags,
                "avg_votes_per_question": total_votes / total_questions if total_questions > 0 else 0,
                "avg_answers_per_question": total_answers / total_questions if total_questions > 0 else 0,
                "platform_health": "healthy",
                "last_updated": datetime.utcnow().isoformat()
            }
        except Exception as e:
            return {"error": str(e), "platform_health": "unhealthy"}

# Create global MCP server instance
mcp_server = None

def create_mcp_server():
    """Create MCP server instance"""
    import os
    base_url = os.getenv("CONTEXT_OVERFLOW_URL", "http://localhost:8000")
    global mcp_server
    mcp_server = ContextOverflowMCPServer(base_url)
    return mcp_server.app

# Create FastAPI app
app = create_mcp_server()

if __name__ == "__main__":
    import os
    port = int(os.getenv("MCP_PORT", 8001))
    
    logger.info(f"Starting Context Overflow MCP Server on port {port}...")
    uvicorn.run(
        "mcp_server_remote:app",
        host="0.0.0.0",
        port=port,
        reload=False,
        log_level="info"
    )