from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Literal, Dict, Any
from app.utils.logger import get_logger

logger = get_logger(__name__)


class Settings(BaseSettings):
	# LLM Configuration
	llm_client: Literal["openai", "claude", "ollama", "mock"] = "mock"
	
	# OpenAI Configuration
	openai_api_key: str | None = None
	openai_model: str = "gpt-4o-mini"
	
	# Claude Configuration
	claude_api_key: str | None = None
	claude_model: str = "claude-3-haiku-20240307"
	
	# Local Llama Configuration
	llama_base_url: str = "http://localhost:11434"  # Ollama default
	llama_model: str = "llama3.2:3b"
	
	# Database Configuration
	database_url: str = "sqlite:///./app.db"
	
	# Logging Configuration
	log_level: str = "INFO"
	log_file: str | None = None

	class Config:
		env_file = ".env"
		case_sensitive = False


@lru_cache(maxsize=1)
def get_settings() -> Settings:
	settings = Settings()
	logger.info(f"Settings loaded - LLM Client: {settings.llm_client}, Log Level: {settings.log_level}")
	return settings


def get_llm_client_config() -> Dict[str, Any]:
	"""Get the configured LLM client configuration."""
	settings = get_settings()
	
	logger.debug(f"Getting LLM client config for: {settings.llm_client}")
	
	if settings.llm_client == "mock":
		logger.info("Using mock LLM client")
		return {"type": "mock"}
	elif settings.llm_client == "openai":
		if not settings.openai_api_key:
			logger.error("OpenAI API key not configured")
			raise ValueError("OpenAI API key not configured")
		logger.info(f"Using OpenAI client with model: {settings.openai_model}")
		return {
			"type": "openai",
			"api_key": settings.openai_api_key,
			"model": settings.openai_model
		}
	elif settings.llm_client == "claude":
		if not settings.claude_api_key:
			logger.error("Claude API key not configured")
			raise ValueError("Claude API key not configured")
		logger.info(f"Using Claude client with model: {settings.claude_model}")
		return {
			"type": "claude",
			"api_key": settings.claude_api_key,
			"model": settings.claude_model
		}
	elif settings.llm_client == "ollama":
		logger.info(f"Using Llama client with model: {settings.llama_model} at {settings.llama_base_url}")
		return {
			"type": "ollama",
			"base_url": settings.llama_base_url,
			"model": settings.llama_model
		}
	else:
		# Fallback to mock for unknown clients
		logger.warning(f"Unknown LLM client: {settings.llm_client}, falling back to mock")
		return {"type": "mock"}
