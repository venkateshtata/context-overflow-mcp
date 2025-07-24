from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

# Constants for vote and target types
VOTE_UPVOTE = 1
VOTE_DOWNVOTE = -1
TARGET_QUESTION = "question"
TARGET_ANSWER = "answer"

class Question(Base):
    __tablename__ = "questions"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False, index=True)
    content = Column(Text, nullable=False)
    author = Column(String(100), nullable=False)
    tags = Column(String(500))  # JSON string or comma-separated
    votes = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    answers = relationship("Answer", back_populates="question", cascade="all, delete-orphan")
    # Relationships will be handled via foreign keys without complex joins

class Answer(Base):
    __tablename__ = "answers"
    
    id = Column(Integer, primary_key=True, index=True)
    question_id = Column(Integer, ForeignKey("questions.id"), nullable=False)
    content = Column(Text, nullable=False)
    author = Column(String(100), nullable=False)
    code_examples = Column(Text)  # JSON string to store code examples
    votes = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    question = relationship("Question", back_populates="answers")

class Vote(Base):
    __tablename__ = "votes"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(100), nullable=False, index=True)
    target_id = Column(Integer, nullable=False, index=True)
    target_type = Column(String(20), nullable=False)  # "question" or "answer"
    vote_value = Column(Integer, nullable=False)  # 1 for upvote, -1 for downvote
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Composite index to prevent duplicate votes
    __table_args__ = (
        # Unique constraint to prevent duplicate votes from same user on same target
        {'sqlite_autoincrement': True}
    )