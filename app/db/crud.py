import json
from sqlalchemy.orm import Session
from sqlalchemy import select, or_
from app.utils.logger import get_logger

from app.db.models import Analysis

logger = get_logger(__name__)


def save_analysis(db: Session, data: dict) -> Analysis:
	"""Save analysis to database."""
	logger.debug(f"Saving analysis with title: {data.get('title', 'Unknown')}")
	
	analysis = Analysis(
		input_text=data["input_text"],
		summary=data["summary"],
		title=data["title"],
		topics=json.dumps(data["topics"]),
		sentiment=data["sentiment"],
		keywords=json.dumps(data["keywords"]),
	)
	db.add(analysis)
	db.commit()
	db.refresh(analysis)
	
	logger.info(f"Analysis saved successfully with ID: {analysis.id}")
	return analysis


def search_analyses(db: Session, search_term: str) -> list[Analysis]:
	"""
	Search analyses by both topic and keyword fields, returning unique results.
	"""
	logger.debug(f"Searching analyses for term: {search_term}")
	
	stmt = select(Analysis).where(
		or_(
			Analysis.topics.like(f"%{search_term}%"),
			Analysis.keywords.like(f"%{search_term}%")
		)
	)
	results = list(db.scalars(stmt).all())
	
	logger.debug(f"Search query executed, found {len(results)} results")
	return results
