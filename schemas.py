"""
Pydantic schemas for request/response validation
"""

from pydantic import BaseModel, Field, validator
from typing import List, Optional
from datetime import datetime

# Request schemas
class PostQuestionRequest(BaseModel):
    title: str = Field(..., min_length=10, max_length=200, description="Question title")
    content: str = Field(..., min_length=20, max_length=5000, description="Question content")
    tags: List[str] = Field(..., min_items=1, max_items=10, description="Question tags")
    language: str = Field(..., min_length=2, max_length=50, description="Programming language")
    
    @validator('title')
    def validate_title(cls, v):
        if not v.strip():
            raise ValueError('Title cannot be empty or whitespace only')
        return v.strip()
    
    @validator('content')
    def validate_content(cls, v):
        if not v.strip():
            raise ValueError('Content cannot be empty or whitespace only')
        return v.strip()
    
    @validator('tags')
    def validate_tags(cls, v):
        if not v:
            raise ValueError('At least one tag is required')
        
        # Clean and validate each tag
        cleaned_tags = []
        for tag in v:
            if not isinstance(tag, str):
                raise ValueError('All tags must be strings')
            
            cleaned_tag = tag.strip().lower()
            if not cleaned_tag:
                raise ValueError('Tags cannot be empty or whitespace only')
            
            if len(cleaned_tag) > 30:
                raise ValueError('Each tag must be 30 characters or less')
            
            if cleaned_tag not in cleaned_tags:  # Remove duplicates
                cleaned_tags.append(cleaned_tag)
        
        if not cleaned_tags:
            raise ValueError('At least one valid tag is required')
        
        return cleaned_tags
    
    @validator('language')
    def validate_language(cls, v):
        if not v.strip():
            raise ValueError('Language cannot be empty or whitespace only')
        return v.strip().lower()

# Response schemas
class QuestionData(BaseModel):
    question_id: int
    status: str = "posted"

class PostQuestionResponse(BaseModel):
    success: bool
    data: QuestionData
    timestamp: datetime

class ErrorResponse(BaseModel):
    success: bool = False
    error: str
    details: Optional[str] = None
    timestamp: datetime
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

# Database response schemas (for internal use)
class QuestionDB(BaseModel):
    id: int
    title: str
    content: str
    author: str
    tags: str
    votes: int
    created_at: datetime
    
    class Config:
        from_attributes = True  # For SQLAlchemy 1.4 compatibility

class AnswerDB(BaseModel):
    id: int
    question_id: int
    content: str
    author: str
    votes: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class VoteDB(BaseModel):
    id: int
    user_id: str
    target_id: int
    target_type: str
    vote_value: int
    created_at: datetime
    
    class Config:
        from_attributes = True

# Get questions schemas
class QuestionSummary(BaseModel):
    id: int
    title: str
    content: str
    tags: List[str]
    votes: int
    answer_count: int
    created_at: datetime

class GetQuestionsData(BaseModel):
    questions: List[QuestionSummary]
    total: int
    has_more: bool

class GetQuestionsResponse(BaseModel):
    success: bool
    data: GetQuestionsData
    timestamp: datetime

# Post answer schemas
class CodeExample(BaseModel):
    language: str = Field(..., min_length=2, max_length=50, description="Programming language")
    code: str = Field(..., min_length=1, max_length=10000, description="Code example")
    
    @validator('language')
    def validate_language(cls, v):
        if not v.strip():
            raise ValueError('Language cannot be empty or whitespace only')
        return v.strip().lower()
    
    @validator('code')
    def validate_code(cls, v):
        if not v.strip():
            raise ValueError('Code cannot be empty or whitespace only')
        return v.strip()

class PostAnswerRequest(BaseModel):
    question_id: int = Field(..., gt=0, description="ID of the question to answer")
    content: str = Field(..., min_length=20, max_length=10000, description="Answer content")
    code_examples: Optional[List[CodeExample]] = Field(default=[], description="Code examples")
    author: str = Field(..., min_length=2, max_length=100, description="Author name")
    
    @validator('content')
    def validate_content(cls, v):
        if not v.strip():
            raise ValueError('Content cannot be empty or whitespace only')
        return v.strip()
    
    @validator('author')
    def validate_author(cls, v):
        if not v.strip():
            raise ValueError('Author cannot be empty or whitespace only')
        return v.strip()
    
    @validator('code_examples')
    def validate_code_examples(cls, v):
        if v and len(v) > 10:
            raise ValueError('Maximum 10 code examples allowed')
        return v

class AnswerData(BaseModel):
    answer_id: int
    question_id: int
    status: str = "posted"

class PostAnswerResponse(BaseModel):
    success: bool
    data: AnswerData
    timestamp: datetime

# Get answers schemas
class AnswerDetails(BaseModel):
    id: int
    content: str
    code_examples: List[CodeExample]
    author: str
    votes: int
    created_at: datetime

class GetAnswersData(BaseModel):
    question_id: int
    answers: List[AnswerDetails]

class GetAnswersResponse(BaseModel):
    success: bool
    data: GetAnswersData
    timestamp: datetime

# Vote schemas
class VoteRequest(BaseModel):
    target_id: int = Field(..., gt=0, description="ID of the question or answer to vote on")
    target_type: str = Field(..., description="Type of target: 'question' or 'answer'")
    vote_type: str = Field(..., description="Type of vote: 'upvote' or 'downvote'")
    user_id: str = Field(..., min_length=1, max_length=100, description="ID of the user voting")
    
    @validator('target_type')
    def validate_target_type(cls, v):
        if v.lower() not in ['question', 'answer']:
            raise ValueError('target_type must be "question" or "answer"')
        return v.lower()
    
    @validator('vote_type')
    def validate_vote_type(cls, v):
        if v.lower() not in ['upvote', 'downvote']:
            raise ValueError('vote_type must be "upvote" or "downvote"')
        return v.lower()
    
    @validator('user_id')
    def validate_user_id(cls, v):
        if not v.strip():
            raise ValueError('user_id cannot be empty or whitespace only')
        return v.strip()

class VoteData(BaseModel):
    target_id: int
    target_type: str
    vote_type: Optional[str] = None  # "upvote", "downvote", or None if vote was removed
    new_vote_total: int
    previous_vote: Optional[str] = None  # "upvote", "downvote", or None

class VoteResponse(BaseModel):
    success: bool
    data: VoteData
    timestamp: datetime