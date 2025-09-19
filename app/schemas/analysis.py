from pydantic import BaseModel, Field
from typing import List
from datetime import datetime


class AnalysisRequest(BaseModel):
	text: str = Field(min_length=1)


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
