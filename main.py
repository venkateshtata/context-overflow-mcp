import logging
import time
import json
from datetime import datetime
from typing import Optional, List
from fastapi import FastAPI, Request, HTTPException, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
import uvicorn
from dotenv import load_dotenv
from database import init_database, check_database_health, get_db
from schemas import PostQuestionRequest, PostQuestionResponse, QuestionData, ErrorResponse, GetQuestionsResponse, GetQuestionsData, QuestionSummary, PostAnswerRequest, PostAnswerResponse, AnswerData, GetAnswersResponse, GetAnswersData, AnswerDetails, CodeExample, VoteRequest, VoteResponse, VoteData
from crud import QuestionCRUD, AnswerCRUD, VoteCRUD

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Context Overflow MCP Server",
    description="MCP Server for Context Overflow",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    
    # Log incoming request
    logger.info(f"Incoming request: {request.method} {request.url}")
    
    try:
        response = await call_next(request)
        process_time = time.time() - start_time
        logger.info(f"Request completed: {request.method} {request.url} - Status: {response.status_code} - Time: {process_time:.4f}s")
        return response
    except Exception as e:
        process_time = time.time() - start_time
        logger.error(f"Request failed: {request.method} {request.url} - Error: {str(e)} - Time: {process_time:.4f}s")
        raise

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception for {request.method} {request.url}: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "detail": "An unexpected error occurred"}
    )

# Include MCP server routes
from mcp_server_remote import create_mcp_server
mcp_app = create_mcp_server()

# Mount MCP server at /mcp-server path
app.mount("/mcp-server", mcp_app)

# Database startup event
@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    try:
        logger.info("Initializing database...")
        init_database()
        if check_database_health():
            logger.info("Database initialized and health check passed")
        else:
            logger.error("Database health check failed")
            raise Exception("Database health check failed")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint with database status"""
    db_healthy = check_database_health()
    return {
        "message": "MCP Server Running",
        "database": "healthy" if db_healthy else "unhealthy"
    }

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "Context Overflow MCP Server", "status": "running"}

# MCP Tools endpoints
@app.post("/mcp/post_question", response_model=PostQuestionResponse)
async def post_question(
    request: PostQuestionRequest,
    db: Session = Depends(get_db)
):
    """
    MCP Tool: Post a new question
    
    Creates a new question in the database with proper validation.
    """
    try:
        logger.info(f"Posting new question: {request.title[:50]}...")
        
        # Convert tags list to comma-separated string for database storage
        tags_str = ",".join(request.tags)
        
        # For now, use a default author - in production, this would come from authentication
        author = "anonymous"
        
        # Create question using CRUD
        question = QuestionCRUD.create(
            db=db,
            title=request.title,
            content=request.content,
            author=author,
            tags=tags_str
        )
        
        logger.info(f"Question created successfully with ID: {question.id}")
        
        # Return success response
        return PostQuestionResponse(
            success=True,
            data=QuestionData(
                question_id=question.id,
                status="posted"
            ),
            timestamp=datetime.utcnow()
        )
        
    except Exception as e:
        logger.error(f"Error posting question: {str(e)}")
        
        # Return error response
        error_response = ErrorResponse(
            error="Failed to post question",
            details=str(e),
            timestamp=datetime.utcnow()
        )
        
        raise HTTPException(
            status_code=500,
            detail=error_response.model_dump()
        )

# Error handler for validation errors
@app.exception_handler(422)
async def validation_exception_handler(request: Request, exc):
    """Handle Pydantic validation errors"""
    logger.error(f"Validation error for {request.method} {request.url}: {exc}")
    
    error_response = ErrorResponse(
        error="Invalid input data",
        details=str(exc),
        timestamp=datetime.utcnow()
    )
    
    return JSONResponse(
        status_code=422,
        content=error_response.model_dump()
    )

@app.get("/mcp/get_questions", response_model=GetQuestionsResponse)
async def get_questions(
    language: Optional[str] = Query(None, description="Filter by programming language"),
    tags: Optional[str] = Query(None, description="Comma-separated list of tags"),
    limit: int = Query(10, ge=1, le=100, description="Number of results per page"),
    offset: int = Query(0, ge=0, description="Pagination offset"),
    db: Session = Depends(get_db)
):
    """
    MCP Tool: Get questions with filtering and pagination
    
    Retrieves questions with optional filtering by language and tags.
    Includes vote counts and answer counts for each question.
    """
    try:
        logger.info(f"Getting questions - language: {language}, tags: {tags}, limit: {limit}, offset: {offset}")
        
        # Parse tags if provided
        tags_list = []
        if tags:
            tags_list = [tag.strip().lower() for tag in tags.split(",") if tag.strip()]
        
        # Get filtered questions
        questions = QuestionCRUD.get_filtered(
            db=db,
            language=language,
            tags=tags_list if tags_list else None,
            skip=offset,
            limit=limit
        )
        
        # Get total count for pagination
        total_count = QuestionCRUD.count_filtered(
            db=db,
            language=language,
            tags=tags_list if tags_list else None
        )
        
        # Convert questions to response format
        question_summaries = []
        for question in questions:
            # Parse tags from comma-separated string
            question_tags = [tag.strip() for tag in question.tags.split(",") if tag.strip()] if question.tags else []
            
            # Get answer count
            answer_count = QuestionCRUD.get_answer_count(db=db, question_id=question.id)
            
            question_summary = QuestionSummary(
                id=question.id,
                title=question.title,
                content=question.content,
                tags=question_tags,
                votes=question.votes,
                answer_count=answer_count,
                created_at=question.created_at
            )
            question_summaries.append(question_summary)
        
        # Calculate if there are more results
        has_more = (offset + limit) < total_count
        
        logger.info(f"Retrieved {len(question_summaries)} questions, total: {total_count}")
        
        return GetQuestionsResponse(
            success=True,
            data=GetQuestionsData(
                questions=question_summaries,
                total=total_count,
                has_more=has_more
            ),
            timestamp=datetime.utcnow()
        )
        
    except Exception as e:
        logger.error(f"Error getting questions: {str(e)}")
        
        error_response = ErrorResponse(
            error="Failed to get questions",
            details=str(e),
            timestamp=datetime.utcnow()
        )
        
        raise HTTPException(
            status_code=500,
            detail=error_response.model_dump()
        )

@app.post("/mcp/post_answer", response_model=PostAnswerResponse)
async def post_answer(
    request: PostAnswerRequest,
    db: Session = Depends(get_db)
):
    """
    MCP Tool: Post an answer to a specific question
    
    Creates a new answer linked to a question with optional code examples.
    Validates that the question exists before allowing the answer.
    """
    try:
        logger.info(f"Posting answer to question {request.question_id} by {request.author}")
        
        # Validate that the question exists
        question = QuestionCRUD.get_by_id(db=db, question_id=request.question_id)
        if not question:
            logger.warning(f"Question with ID {request.question_id} not found")
            error_response = ErrorResponse(
                error="Question not found",
                details=f"No question exists with ID {request.question_id}",
                timestamp=datetime.utcnow()
            )
            raise HTTPException(
                status_code=404,
                detail={
                    "success": False,
                    "error": "Question not found",
                    "details": f"No question exists with ID {request.question_id}",
                    "timestamp": datetime.utcnow().isoformat()
                }
            )
        
        # Convert code examples to JSON string for storage
        code_examples_json = None
        if request.code_examples:
            try:
                # Convert Pydantic models to dict for JSON serialization
                code_examples_data = [example.dict() for example in request.code_examples]
                code_examples_json = json.dumps(code_examples_data)
                logger.info(f"Storing {len(request.code_examples)} code examples")
            except Exception as e:
                logger.error(f"Error serializing code examples: {e}")
                error_response = ErrorResponse(
                    error="Invalid code examples format",
                    details=str(e),
                    timestamp=datetime.utcnow()
                )
                raise HTTPException(
                    status_code=400,
                    detail=error_response.model_dump()
                )
        
        # Create the answer
        answer = AnswerCRUD.create(
            db=db,
            question_id=request.question_id,
            content=request.content,
            author=request.author,
            code_examples=code_examples_json
        )
        
        logger.info(f"Answer created successfully with ID: {answer.id}")
        
        # Return success response
        return PostAnswerResponse(
            success=True,
            data=AnswerData(
                answer_id=answer.id,
                question_id=answer.question_id,
                status="posted"
            ),
            timestamp=datetime.utcnow()
        )
        
    except HTTPException:
        # Re-raise HTTP exceptions (like 404)
        raise
    except Exception as e:
        logger.error(f"Error posting answer: {str(e)}")
        
        error_response = ErrorResponse(
            error="Failed to post answer",
            details=str(e),
            timestamp=datetime.utcnow()
        )
        
        raise HTTPException(
            status_code=500,
            detail=error_response.model_dump()
        )

@app.get("/mcp/get_answers/{question_id}", response_model=GetAnswersResponse)
async def get_answers(
    question_id: int,
    db: Session = Depends(get_db)
):
    """
    MCP Tool: Get all answers for a specific question
    
    Returns all answers for a question sorted by vote count (highest first).
    Includes code examples and author information.
    """
    try:
        logger.info(f"Getting answers for question {question_id}")
        
        # Validate that the question exists
        question = QuestionCRUD.get_by_id(db=db, question_id=question_id)
        if not question:
            logger.warning(f"Question with ID {question_id} not found")
            raise HTTPException(
                status_code=404,
                detail={
                    "success": False,
                    "error": "Question not found",
                    "details": f"No question exists with ID {question_id}",
                    "timestamp": datetime.utcnow().isoformat()
                }
            )
        
        # Get answers for the question (already sorted by votes desc, then created_at)
        answers = AnswerCRUD.get_by_question(db=db, question_id=question_id)
        
        # Convert answers to response format
        answer_details = []
        for answer in answers:
            # Parse code examples from JSON storage
            code_examples = []
            if answer.code_examples:
                try:
                    code_examples_data = json.loads(answer.code_examples)
                    # Convert dict data back to CodeExample objects
                    for example_data in code_examples_data:
                        code_example = CodeExample(
                            language=example_data.get("language", ""),
                            code=example_data.get("code", "")
                        )
                        code_examples.append(code_example)
                except json.JSONDecodeError as e:
                    logger.warning(f"Failed to parse code examples for answer {answer.id}: {e}")
                    # Continue with empty code_examples list
            
            answer_detail = AnswerDetails(
                id=answer.id,
                content=answer.content,
                code_examples=code_examples,
                author=answer.author,
                votes=answer.votes,
                created_at=answer.created_at
            )
            answer_details.append(answer_detail)
        
        logger.info(f"Retrieved {len(answer_details)} answers for question {question_id}")
        
        return GetAnswersResponse(
            success=True,
            data=GetAnswersData(
                question_id=question_id,
                answers=answer_details
            ),
            timestamp=datetime.utcnow()
        )
        
    except HTTPException:
        # Re-raise HTTP exceptions (like 404)
        raise
    except Exception as e:
        logger.error(f"Error getting answers for question {question_id}: {str(e)}")
        
        error_response = ErrorResponse(
            error="Failed to get answers",
            details=str(e),
            timestamp=datetime.utcnow()
        )
        
        raise HTTPException(
            status_code=500,
            detail=error_response.model_dump()
        )

@app.post("/mcp/vote", response_model=VoteResponse)
async def vote(
    request: VoteRequest,
    db: Session = Depends(get_db)
):
    """
    MCP Tool: Vote on questions or answers
    
    Allows users to upvote or downvote questions and answers.
    Prevents duplicate votes and handles vote changes.
    Updates aggregate vote counts in real-time.
    """
    try:
        logger.info(f"Processing vote: {request.user_id} voting {request.vote_type} on {request.target_type} {request.target_id}")
        
        # Validate that the target exists
        if request.target_type == "question":
            target = QuestionCRUD.get_by_id(db=db, question_id=request.target_id)
            if not target:
                logger.warning(f"Question with ID {request.target_id} not found")
                raise HTTPException(
                    status_code=404,
                    detail={
                        "success": False,
                        "error": "Question not found",
                        "details": f"No question exists with ID {request.target_id}",
                        "timestamp": datetime.utcnow().isoformat()
                    }
                )
        else:  # answer
            target = AnswerCRUD.get_by_id(db=db, answer_id=request.target_id)
            if not target:
                logger.warning(f"Answer with ID {request.target_id} not found")
                raise HTTPException(
                    status_code=404,
                    detail={
                        "success": False,
                        "error": "Answer not found",
                        "details": f"No answer exists with ID {request.target_id}",
                        "timestamp": datetime.utcnow().isoformat()
                    }
                )
        
        # Process the vote
        vote_result = VoteCRUD.process_vote(
            db=db,
            user_id=request.user_id,
            target_id=request.target_id,
            target_type=request.target_type,
            vote_type=request.vote_type
        )
        
        # Update aggregate vote count in the target table
        if request.target_type == "question":
            QuestionCRUD.update_vote_count(db=db, question_id=request.target_id)
        else:
            AnswerCRUD.update_vote_count(db=db, answer_id=request.target_id)
        
        # Determine the actual vote type for response (could be None if vote was removed)
        actual_vote_type = request.vote_type if vote_result['action'] != 'removed' else None
        
        logger.info(f"Vote processed: {vote_result['action']} - new total: {vote_result['new_total']}")
        
        return VoteResponse(
            success=True,
            data=VoteData(
                target_id=request.target_id,
                target_type=request.target_type,
                vote_type=actual_vote_type,
                new_vote_total=vote_result['new_total'],
                previous_vote=vote_result['previous_vote']
            ),
            timestamp=datetime.utcnow()
        )
        
    except HTTPException:
        # Re-raise HTTP exceptions (like 404)
        raise
    except Exception as e:
        logger.error(f"Error processing vote: {str(e)}")
        
        error_response = ErrorResponse(
            error="Failed to process vote",
            details=str(e),
            timestamp=datetime.utcnow()
        )
        
        raise HTTPException(
            status_code=500,
            detail=error_response.model_dump()
        )

if __name__ == "__main__":
    import os
    port = int(os.getenv("PORT", 8000))
    logger.info(f"Starting Context Overflow MCP Server on port {port}...")
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=False,  # Disable reload in production
        log_level="info"
    )