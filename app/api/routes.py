from typing import List, Optional
import json
import re
from sqlalchemy.orm import Session
from fastapi import APIRouter, HTTPException, Depends, Query, Request

from app.schemas.analysis import AnalysisRequest, AnalysisResponse
from app.services.llm_service import analyze_text, LLMError
from app.services.nlp_service import extract_top_nouns
from app.db.database import SessionLocal
from app.db import crud
from app.db.models import Base
from app.db.database import engine
from app.utils.text_utils import clean_text, make_json_valid
from app.utils.logger import get_logger

# Create tables on import (simple bootstrap for assignment)
Base.metadata.create_all(bind=engine)

router = APIRouter()
logger = get_logger(__name__)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/analyze", response_model=AnalysisResponse)
async def analyze(request: Request, db: Session = Depends(get_db)):
    """Analyze the text and return summary and metadata"""
    try:
        # Read the raw body
        body = await request.body()
        body_str = body.decode('utf-8')
        
        logger.debug(f"Raw request body: {body_str[:200]}...")
        
        # Try to parse JSON
        try:
            data = json.loads(body_str)
        except json.JSONDecodeError as e:
            logger.info(f"JSON decode error, attempting to fix: {e}")
            
            # Make the JSON valid
            fixed_body = make_json_valid(body_str)
            logger.debug(f"Fixed body: {fixed_body[:200]}...")
            
            try:
                data = json.loads(fixed_body)
                logger.info("Successfully fixed and parsed JSON")
            except json.JSONDecodeError as e2:
                logger.error(f"Could not fix JSON: {e2}")
                raise HTTPException(
                    status_code=400, 
                    detail={"error": f"Invalid JSON format: {str(e)}"}
                )
        
        # Validate that we have the required text field
        if "text" not in data:
            raise HTTPException(status_code=400, detail={"error": "Missing 'text' field"})
        
        text = clean_text(data["text"])
        if not text:
            logger.warning("Empty text provided in analyze request")
            raise HTTPException(status_code=400, detail={"error": "Input text is required"})
        
        logger.info(f"Received analyze request for text of length: {len(text)}")
        
        try:
            logger.info("Starting LLM analysis")
            llm_result = analyze_text(text)
            logger.info("LLM analysis completed, extracting keywords")

            keywords = extract_top_nouns(text, top_k=3)
            logger.debug(f"Extracted keywords: {keywords}")

            analysis_data = {
                "input_text": text,
                "summary": llm_result["summary"],
                "title": llm_result["title"],
                "topics": llm_result.get("topics", []),
                "sentiment": llm_result.get("sentiment", "neutral"),
                "keywords": keywords,
            }

            logger.info("Saving analysis to database")
            row = crud.save_analysis(db, analysis_data)
            logger.info(f"Analysis saved with ID: {row.id}")

            return AnalysisResponse(
                id=row.id,
                summary=row.summary,
                title=row.title,
                topics=json.loads(row.topics),
                sentiment=row.sentiment,
                keywords=json.loads(row.keywords),
                created_at=row.created_at,
            )
        except LLMError as e:
            logger.error(f"LLM analysis failed: {str(e)}")
            raise HTTPException(status_code=500, detail={"error": "LLM request failed"})
        except Exception as e:
            logger.error(f"Unexpected error in analyze endpoint: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail={"error": "Internal server error"})
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in analyze endpoint: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail={"error": "Internal server error"})


@router.get("/search", response_model=List[AnalysisResponse])
async def search(topic: Optional[str] = Query(default=None), db: Session = Depends(get_db)):
    """
	Search analyses by topic. Searches both topic and keyword fields and returns unique results.
	"""
    logger.info(f"Received search request for topic: {topic}")
    
    if not topic:
        logger.warning("No topic provided in search request")
        return []

	# Search both topic and keyword fields for the given term
    logger.debug(f"Searching database for topic: {topic}")
    results = crud.search_analyses(db, topic)
    logger.info(f"Found {len(results)} matching analyses")

    return [
		AnalysisResponse(
			id=r.id,
			summary=r.summary,
			title=r.title,
			topics=json.loads(r.topics),
			sentiment=r.sentiment,
			keywords=json.loads(r.keywords),
			created_at=r.created_at,
		)
		for r in results
	]
