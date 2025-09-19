from fastapi import FastAPI
from app.api.routes import router as api_router
from app.utils.logger import setup_logger, get_logger
from app.config import get_settings

# Setup logging
settings = get_settings()
logger = setup_logger(
    name="llm_knowledge_extractor",
    level=settings.log_level,
    log_file=settings.log_file
)

app = FastAPI(title="LLM Knowledge Extractor")

app.include_router(api_router)

logger.info("FastAPI application started successfully")
