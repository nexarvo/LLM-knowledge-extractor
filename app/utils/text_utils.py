import re
import os
from pathlib import Path


def clean_text(text: str) -> str:
	text = text.strip()
	text = re.sub(r"\s+", " ", text)
	return text


def load_prompt(prompt_name: str = "analysis") -> str:
	"""
	Load prompt template from prompts.txt file.
	"""
	# Get the directory where this file is located
	current_dir = Path(__file__).parent
	prompt_file = current_dir / "prompts.txt"

	try:
		with open(prompt_file, 'r', encoding='utf-8') as f:
			return f.read().strip()
	except FileNotFoundError:
		# Fallback prompt if file doesn't exist
		return (
			"Summarize the text in 1-2 sentences, propose a short title, "
			"list 3 topics (single words), and overall sentiment (positive/neutral/negative). "
			"Return strict JSON with keys: summary, title, topics, sentiment.\n\nText:"
		)
