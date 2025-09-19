from pydantic import BaseModel, Field, field_validator
from typing import List
from datetime import datetime
from app.utils.text_utils import clean_text


class AnalysisRequest(BaseModel):
	text: str = Field(min_length=1)
	
	@field_validator('text')
	@classmethod
	def clean_text_field(cls, v: str) -> str:
		"""Clean the text field to remove control characters and problematic Unicode."""
		return clean_text(v)


class AnalysisResponse(BaseModel):
	id: int
	summary: str
	title: str
	topics: List[str]
	sentiment: str
	keywords: List[str]
	created_at: datetime

	class Config:
		from_attributes = True
