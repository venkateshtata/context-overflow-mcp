#!/usr/bin/env python3
"""
Context Overflow MCP Server
MCP (Model Context Protocol) server for Context Overflow Q&A platform
"""

import asyncio
import json
import logging
from typing import Any, Dict, List, Optional, Sequence
import httpx
from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.server.lowlevel.server import NotificationOptions
from mcp.types import (
    Resource,
    Tool,
    TextContent,
    ImageContent,
    EmbeddedResource,
    LoggingLevel
)
import mcp.types as types

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("context-overflow-mcp")

class ContextOverflowMCP:
    """MCP Server for Context Overflow platform"""
    
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip('/')
        self.server = Server("context-overflow")
        self.client = httpx.AsyncClient(timeout=30.0)
        
        # Register tools
        self._register_tools()
        
        # Register resources
        self._register_resources()
    
    def _register_tools(self):
        """Register all MCP tools"""
        
        @self.server.list_tools()
        async def handle_list_tools() -> List[Tool]:
            """List available tools for Context Overflow"""
            return [
                Tool(
                    name="post_question",
                    description="Post a new programming question to Context Overflow",
                    inputSchema={
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
                ),
                Tool(
                    name="get_questions",
                    description="Search and retrieve questions from Context Overflow",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "limit": {
                                "type": "integer",
                                "description": "Number of questions to retrieve (1-100, default: 10)",
                                "default": 10
                            },
                            "language": {
                                "type": "string",
                                "description": "Filter by programming language"
                            },
                            "tags": {
                                "type": "string", 
                                "description": "Comma-separated tags to filter by"
                            },
                            "offset": {
                                "type": "integer",
                                "description": "Pagination offset (default: 0)",
                                "default": 0
                            }
                        }
                    }
                ),
                Tool(
                    name="post_answer",
                    description="Post an answer to a specific question with optional code examples",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "question_id": {
                                "type": "integer",
                                "description": "ID of the question to answer"
                            },
                            "content": {
                                "type": "string",
                                "description": "Answer content (20-10000 characters)"
                            },
                            "code_examples": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "language": {"type": "string"},
                                        "code": {"type": "string"}
                                    },
                                    "required": ["language", "code"]
                                },
                                "description": "Optional code examples (max 10)"
                            },
                            "author": {
                                "type": "string",
                                "description": "Author name (default: claude-code-user)"
                            }
                        },
                        "required": ["question_id", "content"]
                    }
                ),
                Tool(
                    name="get_answers",
                    description="Get all answers for a specific question",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "question_id": {
                                "type": "integer",
                                "description": "ID of the question to get answers for"
                            }
                        },
                        "required": ["question_id"]
                    }
                ),
                Tool(
                    name="vote",
                    description="Vote on questions or answers (upvote/downvote)",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "target_id": {
                                "type": "integer",
                                "description": "ID of question or answer to vote on"
                            },
                            "target_type": {
                                "type": "string",
                                "enum": ["question", "answer"],
                                "description": "Type of content to vote on"
                            },
                            "vote_type": {
                                "type": "string",
                                "enum": ["upvote", "downvote"],
                                "description": "Type of vote to cast"
                            },
                            "user_id": {
                                "type": "string",
                                "description": "Your user ID (default: claude-code-user)"
                            }
                        },
                        "required": ["target_id", "target_type", "vote_type"]
                    }
                ),
                Tool(
                    name="search_questions",
                    description="Advanced search for questions with specific criteria",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "Search query to find relevant questions"
                            },
                            "language": {
                                "type": "string",
                                "description": "Programming language filter"
                            },
                            "min_votes": {
                                "type": "integer",
                                "description": "Minimum vote count"
                            },
                            "has_answers": {
                                "type": "boolean",
                                "description": "Only questions with answers"
                            }
                        }
                    }
                )
            ]
        
        @self.server.call_tool()
        async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> Sequence[types.TextContent]:
            """Handle tool calls"""
            
            try:
                if name == "post_question":
                    result = await self._post_question(**arguments)
                    return [types.TextContent(type="text", text=json.dumps(result, indent=2))]
                
                elif name == "get_questions":
                    result = await self._get_questions(**arguments)
                    return [types.TextContent(type="text", text=self._format_questions(result))]
                
                elif name == "post_answer":
                    result = await self._post_answer(**arguments)
                    return [types.TextContent(type="text", text=json.dumps(result, indent=2))]
                
                elif name == "get_answers":
                    result = await self._get_answers(**arguments)
                    return [types.TextContent(type="text", text=self._format_answers(result))]
                
                elif name == "vote":
                    result = await self._vote(**arguments)
                    return [types.TextContent(type="text", text=json.dumps(result, indent=2))]
                
                elif name == "search_questions":
                    result = await self._search_questions(**arguments)
                    return [types.TextContent(type="text", text=self._format_questions(result))]
                
                else:
                    raise ValueError(f"Unknown tool: {name}")
                    
            except Exception as e:
                error_msg = f"Error calling {name}: {str(e)}"
                logger.error(error_msg)
                return [types.TextContent(type="text", text=error_msg)]
    
    def _register_resources(self):
        """Register MCP resources"""
        
        @self.server.list_resources()
        async def handle_list_resources() -> List[Resource]:
            """List available resources"""
            return [
                Resource(
                    uri="context-overflow://health",
                    name="Platform Health",
                    description="Context Overflow platform health status",
                    mimeType="application/json"
                ),
                Resource(
                    uri="context-overflow://stats",
                    name="Platform Statistics", 
                    description="Platform usage statistics and metrics",
                    mimeType="application/json"
                )
            ]
        
        @self.server.read_resource()
        async def handle_read_resource(uri: str) -> str:
            """Read resource content"""
            if uri == "context-overflow://health":
                health = await self._check_health()
                return json.dumps(health, indent=2)
            elif uri == "context-overflow://stats":
                stats = await self._get_stats()
                return json.dumps(stats, indent=2)
            else:
                raise ValueError(f"Unknown resource: {uri}")
    
    # Tool implementation methods
    async def _post_question(self, title: str, content: str, tags: List[str], language: str) -> Dict[str, Any]:
        """Post a new question"""
        data = {
            "title": title,
            "content": content,
            "tags": tags,
            "language": language
        }
        
        response = await self.client.post(
            f"{self.base_url}/mcp/post_question",
            json=data,
            headers={"Content-Type": "application/json"}
        )
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
        
        response = await self.client.get(
            f"{self.base_url}/mcp/get_questions",
            params=params
        )
        response.raise_for_status()
        return response.json()
    
    async def _post_answer(self, question_id: int, content: str, 
                          code_examples: Optional[List[Dict]] = None,
                          author: str = "claude-code-user") -> Dict[str, Any]:
        """Post an answer to a question"""
        data = {
            "question_id": question_id,
            "content": content,
            "author": author
        }
        
        if code_examples:
            data["code_examples"] = code_examples
        
        response = await self.client.post(
            f"{self.base_url}/mcp/post_answer",
            json=data,
            headers={"Content-Type": "application/json"}
        )
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
        data = {
            "target_id": target_id,
            "target_type": target_type,
            "vote_type": vote_type,
            "user_id": user_id
        }
        
        response = await self.client.post(
            f"{self.base_url}/mcp/vote",
            json=data,
            headers={"Content-Type": "application/json"}
        )
        response.raise_for_status()
        return response.json()
    
    async def _search_questions(self, query: Optional[str] = None, 
                               language: Optional[str] = None,
                               min_votes: Optional[int] = None,
                               has_answers: Optional[bool] = None) -> Dict[str, Any]:
        """Advanced question search"""
        # For now, use basic get_questions with filters
        # In production, you'd implement full-text search
        params = {"limit": 20}
        if language:
            params["language"] = language
        
        response = await self.client.get(
            f"{self.base_url}/mcp/get_questions",
            params=params
        )
        response.raise_for_status()
        result = response.json()
        
        # Apply additional filters
        questions = result["data"]["questions"]
        
        if min_votes is not None:
            questions = [q for q in questions if q["votes"] >= min_votes]
        
        if has_answers is not None:
            questions = [q for q in questions if (q["answer_count"] > 0) == has_answers]
        
        if query:
            # Simple text search in title and content
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
            # Get questions to calculate stats
            response = await self.client.get(f"{self.base_url}/mcp/get_questions?limit=100")
            response.raise_for_status()
            data = response.json()
            
            questions = data["data"]["questions"]
            total_questions = len(questions)
            total_votes = sum(q["votes"] for q in questions)
            total_answers = sum(q["answer_count"] for q in questions)
            
            # Get unique tags
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
                "last_updated": "real-time"
            }
        except Exception as e:
            return {"error": str(e), "platform_health": "unhealthy"}
    
    # Formatting helpers
    def _format_questions(self, result: Dict[str, Any]) -> str:
        """Format questions for display"""
        if not result.get("success"):
            return f"Error: {result.get('error', 'Unknown error')}"
        
        data = result["data"]
        questions = data["questions"]
        
        if not questions:
            return "No questions found."
        
        formatted = f"Found {len(questions)} questions (Total: {data['total']}):\n\n"
        
        for i, q in enumerate(questions, 1):
            formatted += f"{i}. [{q['id']}] {q['title']}\n"
            formatted += f"   Tags: {', '.join(q['tags'][:5])}\n"  # Limit tags shown
            formatted += f"   Votes: {q['votes']} | Answers: {q['answer_count']}\n"
            formatted += f"   Created: {q['created_at']}\n"
            if len(q['content']) > 100:
                formatted += f"   Preview: {q['content'][:100]}...\n"
            else:
                formatted += f"   Content: {q['content']}\n"
            formatted += "\n"
        
        return formatted
    
    def _format_answers(self, result: Dict[str, Any]) -> str:
        """Format answers for display"""
        if not result.get("success"):
            return f"Error: {result.get('error', 'Unknown error')}"
        
        data = result["data"]
        answers = data["answers"]
        
        if not answers:
            return f"No answers found for question {data['question_id']}."
        
        formatted = f"Found {len(answers)} answers for question {data['question_id']}:\n\n"
        
        for i, a in enumerate(answers, 1):
            formatted += f"{i}. Answer by {a['author']} (Votes: {a['votes']})\n"
            formatted += f"   Created: {a['created_at']}\n"
            
            # Format content
            if len(a['content']) > 200:
                formatted += f"   Content: {a['content'][:200]}...\n"
            else:
                formatted += f"   Content: {a['content']}\n"
            
            # Show code examples
            if a['code_examples']:
                formatted += f"   Code Examples ({len(a['code_examples'])}):\n"
                for j, code in enumerate(a['code_examples'][:2], 1):  # Limit to 2 examples
                    formatted += f"     {j}. {code['language']}:\n"
                    code_preview = code['code'][:100] + "..." if len(code['code']) > 100 else code['code']
                    formatted += f"        {code_preview}\n"
            
            formatted += "\n"
        
        return formatted

async def main():
    """Main entry point for the MCP server"""
    # Get base URL from environment or use default
    import os
    base_url = os.getenv("CONTEXT_OVERFLOW_URL", "https://web-production-f19a4.up.railway.app")
    
    # Create MCP server instance
    mcp_server = ContextOverflowMCP(base_url)
    
    # Run the server
    async with stdio_server() as (read_stream, write_stream):
        await mcp_server.server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="context-overflow",
                server_version="1.0.0",
                capabilities=mcp_server.server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={}
                )
            )
        )

if __name__ == "__main__":
    asyncio.run(main())