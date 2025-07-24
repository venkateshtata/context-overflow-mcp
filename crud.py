"""
CRUD operations for Context Overflow models
"""

from sqlalchemy.orm import Session
from sqlalchemy import and_, desc
from typing import List, Optional
from models import Question, Answer, Vote, VOTE_UPVOTE, VOTE_DOWNVOTE, TARGET_QUESTION, TARGET_ANSWER
from datetime import datetime

# Question CRUD operations
class QuestionCRUD:
    @staticmethod
    def create(db: Session, title: str, content: str, author: str, tags: str = "") -> Question:
        """Create a new question"""
        question = Question(
            title=title,
            content=content,
            author=author,
            tags=tags
        )
        db.add(question)
        db.commit()
        db.refresh(question)
        return question
    
    @staticmethod
    def get_by_id(db: Session, question_id: int) -> Optional[Question]:
        """Get question by ID"""
        return db.query(Question).filter(Question.id == question_id).first()
    
    @staticmethod
    def get_all(db: Session, skip: int = 0, limit: int = 100) -> List[Question]:
        """Get all questions with pagination"""
        return db.query(Question).order_by(desc(Question.created_at)).offset(skip).limit(limit).all()
    
    @staticmethod
    def get_filtered(db: Session, language: str = None, tags: List[str] = None, skip: int = 0, limit: int = 100) -> List[Question]:
        """Get questions with optional filtering by language and tags"""
        query = db.query(Question)
        
        # Filter by language if provided
        if language:
            # Note: In the database, we store language info in tags for now
            # In production, you might want a separate language column
            query = query.filter(Question.tags.contains(language.lower()))
        
        # Filter by tags if provided
        if tags:
            for tag in tags:
                query = query.filter(Question.tags.contains(tag.lower()))
        
        return query.order_by(desc(Question.created_at)).offset(skip).limit(limit).all()
    
    @staticmethod
    def count_filtered(db: Session, language: str = None, tags: List[str] = None) -> int:
        """Count questions with optional filtering"""
        query = db.query(Question)
        
        # Apply same filters as get_filtered
        if language:
            query = query.filter(Question.tags.contains(language.lower()))
        
        if tags:
            for tag in tags:
                query = query.filter(Question.tags.contains(tag.lower()))
        
        return query.count()
    
    @staticmethod
    def get_answer_count(db: Session, question_id: int) -> int:
        """Get count of answers for a question"""
        return db.query(Answer).filter(Answer.question_id == question_id).count()
    
    @staticmethod
    def search_by_title(db: Session, title_query: str) -> List[Question]:
        """Search questions by title"""
        return db.query(Question).filter(Question.title.contains(title_query)).all()
    
    @staticmethod
    def get_by_author(db: Session, author: str) -> List[Question]:
        """Get questions by author"""
        return db.query(Question).filter(Question.author == author).all()
    
    @staticmethod
    def update(db: Session, question_id: int, **kwargs) -> Optional[Question]:
        """Update question"""
        question = db.query(Question).filter(Question.id == question_id).first()
        if question:
            for key, value in kwargs.items():
                if hasattr(question, key):
                    setattr(question, key, value)
            db.commit()
            db.refresh(question)
        return question
    
    @staticmethod
    def delete(db: Session, question_id: int) -> bool:
        """Delete question"""
        question = db.query(Question).filter(Question.id == question_id).first()
        if question:
            db.delete(question)
            db.commit()
            return True
        return False
    
    @staticmethod
    def update_vote_count(db: Session, question_id: int) -> Optional[Question]:
        """Recalculate and update vote count for question"""
        question = db.query(Question).filter(Question.id == question_id).first()
        if question:
            upvotes = db.query(Vote).filter(
                and_(
                    Vote.target_id == question_id,
                    Vote.target_type == TARGET_QUESTION,
                    Vote.vote_value == VOTE_UPVOTE
                )
            ).count()
            downvotes = db.query(Vote).filter(
                and_(
                    Vote.target_id == question_id,
                    Vote.target_type == TARGET_QUESTION,
                    Vote.vote_value == VOTE_DOWNVOTE
                )
            ).count()
            
            question.votes = upvotes - downvotes
            db.commit()
            db.refresh(question)
        return question

# Answer CRUD operations
class AnswerCRUD:
    @staticmethod
    def create(db: Session, question_id: int, content: str, author: str, code_examples: str = None) -> Answer:
        """Create a new answer with optional code examples"""
        answer = Answer(
            question_id=question_id,
            content=content,
            author=author,
            code_examples=code_examples
        )
        db.add(answer)
        db.commit()
        db.refresh(answer)
        return answer
    
    @staticmethod
    def get_by_id(db: Session, answer_id: int) -> Optional[Answer]:
        """Get answer by ID"""
        return db.query(Answer).filter(Answer.id == answer_id).first()
    
    @staticmethod
    def get_by_question(db: Session, question_id: int) -> List[Answer]:
        """Get all answers for a question"""
        return db.query(Answer).filter(Answer.question_id == question_id).order_by(desc(Answer.votes), Answer.created_at).all()
    
    @staticmethod
    def get_by_author(db: Session, author: str) -> List[Answer]:
        """Get answers by author"""
        return db.query(Answer).filter(Answer.author == author).all()
    
    @staticmethod
    def update(db: Session, answer_id: int, **kwargs) -> Optional[Answer]:
        """Update answer"""
        answer = db.query(Answer).filter(Answer.id == answer_id).first()
        if answer:
            for key, value in kwargs.items():
                if hasattr(answer, key):
                    setattr(answer, key, value)
            db.commit()
            db.refresh(answer)
        return answer
    
    @staticmethod
    def delete(db: Session, answer_id: int) -> bool:
        """Delete answer"""
        answer = db.query(Answer).filter(Answer.id == answer_id).first()
        if answer:
            db.delete(answer)
            db.commit()
            return True
        return False
    
    @staticmethod
    def update_vote_count(db: Session, answer_id: int) -> Optional[Answer]:
        """Recalculate and update vote count for answer"""
        answer = db.query(Answer).filter(Answer.id == answer_id).first()
        if answer:
            upvotes = db.query(Vote).filter(
                and_(
                    Vote.target_id == answer_id,
                    Vote.target_type == TARGET_ANSWER,
                    Vote.vote_value == VOTE_UPVOTE
                )
            ).count()
            downvotes = db.query(Vote).filter(
                and_(
                    Vote.target_id == answer_id,
                    Vote.target_type == TARGET_ANSWER,
                    Vote.vote_value == VOTE_DOWNVOTE
                )
            ).count()
            
            answer.votes = upvotes - downvotes
            db.commit()
            db.refresh(answer)
        return answer

# Vote CRUD operations
class VoteCRUD:
    @staticmethod
    def create_or_update(db: Session, user_id: str, target_id: int, target_type: str, vote_value: int) -> Vote:
        """Create or update a vote (prevents duplicate votes)"""
        existing_vote = db.query(Vote).filter(
            and_(
                Vote.user_id == user_id,
                Vote.target_id == target_id,
                Vote.target_type == target_type
            )
        ).first()
        
        if existing_vote:
            existing_vote.vote_value = vote_value
            db.commit()
            db.refresh(existing_vote)
            return existing_vote
        else:
            new_vote = Vote(
                user_id=user_id,
                target_id=target_id,
                target_type=target_type,
                vote_value=vote_value
            )
            db.add(new_vote)
            db.commit()
            db.refresh(new_vote)
            return new_vote
    
    @staticmethod
    def get_user_vote(db: Session, user_id: str, target_id: int, target_type: str) -> Optional[Vote]:
        """Get a user's vote on a specific target"""
        return db.query(Vote).filter(
            and_(
                Vote.user_id == user_id,
                Vote.target_id == target_id,
                Vote.target_type == target_type
            )
        ).first()
    
    @staticmethod
    def get_votes_for_target(db: Session, target_id: int, target_type: str) -> List[Vote]:
        """Get all votes for a target"""
        return db.query(Vote).filter(
            and_(Vote.target_id == target_id, Vote.target_type == target_type)
        ).all()
    
    @staticmethod
    def delete(db: Session, user_id: str, target_id: int, target_type: str) -> bool:
        """Delete a vote"""
        vote = db.query(Vote).filter(
            and_(
                Vote.user_id == user_id,
                Vote.target_id == target_id,
                Vote.target_type == target_type
            )
        ).first()
        
        if vote:
            db.delete(vote)
            db.commit()
            return True
        return False
    
    @staticmethod
    def get_vote_summary(db: Session, target_id: int, target_type: str) -> dict:
        """Get vote summary for a target"""
        upvotes = db.query(Vote).filter(
            and_(
                Vote.target_id == target_id,
                Vote.target_type == target_type,
                Vote.vote_value == VOTE_UPVOTE
            )
        ).count()
        
        downvotes = db.query(Vote).filter(
            and_(
                Vote.target_id == target_id,
                Vote.target_type == target_type,
                Vote.vote_value == VOTE_DOWNVOTE
            )
        ).count()
        
        return {
            "upvotes": upvotes,
            "downvotes": downvotes,
            "total": upvotes - downvotes
        }
    
    @staticmethod
    def process_vote(db: Session, user_id: str, target_id: int, target_type: str, vote_type: str) -> dict:
        """
        Process a vote and return comprehensive information about the vote action
        Returns: {
            'vote': Vote object,
            'previous_vote': str | None,
            'new_total': int,
            'action': 'created' | 'updated' | 'removed'
        }
        """
        # Convert vote_type to vote_value
        vote_value = VOTE_UPVOTE if vote_type == "upvote" else VOTE_DOWNVOTE
        
        # Check for existing vote
        existing_vote = db.query(Vote).filter(
            and_(
                Vote.user_id == user_id,
                Vote.target_id == target_id,
                Vote.target_type == target_type
            )
        ).first()
        
        previous_vote = None
        action = "created"
        
        if existing_vote:
            # Determine previous vote type
            previous_vote = "upvote" if existing_vote.vote_value == VOTE_UPVOTE else "downvote"
            
            # If same vote type, remove the vote (toggle behavior)
            if existing_vote.vote_value == vote_value:
                db.delete(existing_vote)
                action = "removed"
                vote = None
            else:
                # Different vote type, update it
                existing_vote.vote_value = vote_value
                action = "updated"
                vote = existing_vote
        else:
            # Create new vote
            vote = Vote(
                user_id=user_id,
                target_id=target_id,
                target_type=target_type,
                vote_value=vote_value
            )
            db.add(vote)
            action = "created"
        
        db.commit()
        
        if vote:
            db.refresh(vote)
        
        # Calculate new total
        vote_summary = VoteCRUD.get_vote_summary(db, target_id, target_type)
        new_total = vote_summary["total"]
        
        return {
            'vote': vote,
            'previous_vote': previous_vote,
            'new_total': new_total,
            'action': action
        }