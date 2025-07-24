#!/usr/bin/env python3
"""
Database initialization script for Context Overflow MCP Server
"""

import logging
import sys
from database import init_database, check_database_health
from models import Question, Answer, Vote

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_sample_data():
    """Create some sample data for testing"""
    from database import get_db_session
    from models import Question, Answer, Vote, VOTE_UPVOTE, TARGET_QUESTION, TARGET_ANSWER
    
    try:
        with get_db_session() as db:
            # Check if sample data already exists
            existing_questions = db.query(Question).count()
            if existing_questions > 0:
                logger.info("Sample data already exists, skipping creation")
                return
            
            # Create sample question
            sample_question = Question(
                title="How to use FastAPI with SQLAlchemy?",
                content="I'm trying to set up a FastAPI application with SQLAlchemy. What's the best way to structure the database connections?",
                author="user1",
                tags="fastapi,sqlalchemy,python",
                votes=5
            )
            db.add(sample_question)
            db.flush()  # Get the ID
            
            # Create sample answer
            sample_answer = Answer(
                question_id=sample_question.id,
                content="You should use dependency injection with get_db() function to manage database sessions properly.",
                author="user2",
                votes=3
            )
            db.add(sample_answer)
            db.flush()
            
            # Create sample votes
            question_vote = Vote(
                user_id="user3",
                target_id=sample_question.id,
                target_type=TARGET_QUESTION,
                vote_value=VOTE_UPVOTE
            )
            
            answer_vote = Vote(
                user_id="user3",
                target_id=sample_answer.id,
                target_type=TARGET_ANSWER,
                vote_value=VOTE_UPVOTE
            )
            
            db.add(question_vote)
            db.add(answer_vote)
            
            logger.info("Sample data created successfully")
            
    except Exception as e:
        logger.error(f"Failed to create sample data: {e}")
        raise

def main():
    """Main initialization function"""
    try:
        logger.info("Starting database initialization...")
        
        # Initialize database (create tables)
        init_database()
        
        # Check database health
        if not check_database_health():
            logger.error("Database health check failed")
            sys.exit(1)
        
        # Create sample data
        create_sample_data()
        
        logger.info("Database initialization completed successfully")
        
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()