import re
import os
from pathlib import Path


def clean_text(text: str) -> str:
	"""Clean text by removing control characters and normalizing whitespace."""
	# Remove all control characters that can break JSON
	text = re.sub(r'[\x00-\x1F\x7F-\x9F]', '', text)
	
	# Replace problematic Unicode characters that might cause JSON issues
	text = text.replace('\u2018', "'")  # Left single quotation mark
	text = text.replace('\u2019', "'")  # Right single quotation mark
	text = text.replace('\u201C', '"')  # Left double quotation mark
	text = text.replace('\u201D', '"')  # Right double quotation mark
	text = text.replace('\u2013', '-')  # En dash
	text = text.replace('\u2014', '-')  # Em dash
	text = text.replace('\u2026', '...')  # Horizontal ellipsis
	
	# Normalize whitespace
	text = re.sub(r'\s+', ' ', text)
	
	# Strip leading/trailing whitespace
	text = text.strip()
	
	return text

def make_json_valid(json_str: str) -> str:
    """Fix malformed JSON by properly escaping the text field."""
    try:
        # Find the text field and extract its content
        text_match = re.search(r'"text"\s*:\s*"([^"]*)"', json_str, re.DOTALL)
        
        if text_match:
            text_content = text_match.group(1)
            
            # Clean and escape the text content
            # Remove control characters that break JSON
            text_content = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', text_content)
            
            # Escape special characters
            text_content = text_content.replace('\\', '\\\\')  # Escape backslashes first
            text_content = text_content.replace('"', '\\"')    # Escape quotes
            text_content = text_content.replace('\n', '\\n')   # Escape newlines
            text_content = text_content.replace('\r', '\\r')   # Escape carriage returns
            text_content = text_content.replace('\t', '\\t')   # Escape tabs
            
            # Replace the original text field with the cleaned version
            fixed_json = json_str[:text_match.start()] + f'"text": "{text_content}"' + json_str[text_match.end():]
            return fixed_json
        else:
            # If no text field found, just remove control characters
            return re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', json_str)
            
    except Exception as e:
        logger.error(f"Error fixing JSON: {e}")
        return json_str

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
