from typing import Dict
import json
import httpx
from app.config import get_llm_client_config
from app.utils.text_utils import load_prompt
from app.utils.logger import get_logger

logger = get_logger(__name__)


class LLMError(Exception):
	pass


def _get_mock_response(text: str) -> Dict:
	"""Generate mock response for offline/dev runs."""
	logger.info("Generating mock response for text analysis")
	return {
		"summary": text[:200] + ("..." if len(text) > 200 else ""),
		"title": "Auto Summary",
		"topics": ["General"],
		"sentiment": "neutral",
	}


def _analyze_with_openai(text: str, config: Dict) -> Dict:
	"""Analyze text using OpenAI."""
	from openai import OpenAI
	
	logger.info(f"Analyzing text with OpenAI model: {config['model']}")
	logger.debug(f"Text length: {len(text)} characters")
	
	client = OpenAI(api_key=config["api_key"])
	prompt_template = load_prompt()
	prompt = f"{prompt_template}\n{text}"
	
	logger.debug("Sending request to OpenAI API")
	resp = client.chat.completions.create(
		model=config["model"],
		messages=[{"role": "user", "content": prompt}],
		response_format={"type": "json_object"},
	)
	content = resp.choices[0].message.content
	logger.info("OpenAI API request completed successfully")
	return json.loads(content)


def _analyze_with_claude(text: str, config: Dict) -> Dict:
	"""Analyze text using Claude."""
	from anthropic import Anthropic
	
	logger.info(f"Analyzing text with Claude model: {config['model']}")
	logger.debug(f"Text length: {len(text)} characters")
	
	client = Anthropic(api_key=config["api_key"])
	prompt_template = load_prompt()
	prompt = f"{prompt_template}\n{text}"
	
	logger.debug("Sending request to Claude API")
	resp = client.messages.create(
		model=config["model"],
		max_tokens=1000,
		messages=[{"role": "user", "content": prompt}]
	)
	content = resp.content[0].text
	logger.info("Claude API request completed successfully")
	return json.loads(content)


def _analyze_with_llama(text: str, config: Dict) -> Dict:
	"""Analyze text using local Llama model via Ollama."""
	logger.info(f"Analyzing text with Llama model: {config['model']} at {config['base_url']}")
	logger.debug(f"Text length: {len(text)} characters")
	
	prompt_template = load_prompt()
	prompt = f"{prompt_template}\n{text}"
	
	payload = {
		"model": config["model"],
		"prompt": prompt,
		"stream": False,
		"format": "json"
	}
	
	logger.debug("Sending request to Ollama API")
	with httpx.Client(timeout=60.0) as client:
		response = client.post(
			f"{config['base_url']}/api/generate",
			json=payload
		)
		response.raise_for_status()
		result = response.json()
		logger.info("Ollama API request completed successfully")
		return json.loads(result["response"])


def analyze_text(text: str) -> Dict:
	"""
	Analyze text using the configured LLM client.
	The client selection is handled by the config layer.
	"""
	logger.info(f"Starting text analysis for {len(text)} characters")
	
	try:
		# Get the configured client config from config layer
		client_config = get_llm_client_config()
		logger.debug(f"Using client type: {client_config['type']}")
		
		# Route to appropriate provider based on config
		if client_config["type"] == "mock":
			result = _get_mock_response(text)
		elif client_config["type"] == "openai":
			result = _analyze_with_openai(text, client_config)
		elif client_config["type"] == "claude":
			result = _analyze_with_claude(text, client_config)
		elif client_config["type"] == "ollama":
			result = _analyze_with_llama(text, client_config)
		else:
			# Fallback to mock for unknown clients
			logger.warning(f"Unknown client type: {client_config['type']}, using mock")
			result = _get_mock_response(text)
		
		logger.info("Text analysis completed successfully")
		logger.debug(f"Analysis result: {result}")
		return result
		
	except Exception as exc:
		logger.error(f"LLM request failed: {str(exc)}", exc_info=True)
		raise LLMError(f"LLM request failed: {str(exc)}") from exc
