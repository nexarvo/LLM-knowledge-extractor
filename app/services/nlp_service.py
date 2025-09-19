from typing import List
from collections import Counter
import re


def extract_top_nouns(text: str, top_k: int = 3) -> List[str]:
	"""
	Extract top nouns using simple regex-based approach to avoid NLTK dependency issues.
	This is a fallback implementation that works without external downloads.
	"""
	# Simple word extraction - split on whitespace and punctuation
	words = re.findall(r'\b[a-zA-Z][a-zA-Z-]*\b', text.lower())

	# Filter out common stop words and short words
	stop_words = {
		'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by',
		'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did',
		'will', 'would', 'could', 'should', 'may', 'might', 'must', 'can', 'this', 'that', 'these',
		'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her', 'us', 'them'
	}

	# Filter words: remove stop words, short words, and common verbs/adjectives
	filtered_words = [
		w for w in words 
		if len(w) > 2 and w not in stop_words and not w.endswith(('ing', 'ed', 'ly', 'er', 'est'))
	]

	# Count and return most common
	most_common = [w for w, _ in Counter(filtered_words).most_common(top_k)]
	return most_common
