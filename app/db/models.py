from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import String, Text, DateTime, Integer
from datetime import datetime


class Base(DeclarativeBase):
	pass


class Analysis(Base):
	__tablename__ = "analyses"

	id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
	input_text: Mapped[str] = mapped_column(Text, nullable=False)
	summary: Mapped[str] = mapped_column(Text, nullable=False)
	title: Mapped[str] = mapped_column(String(255), nullable=False)
	topics: Mapped[str] = mapped_column(Text, nullable=False)  # JSON string
	sentiment: Mapped[str] = mapped_column(String(32), nullable=False)
	keywords: Mapped[str] = mapped_column(Text, nullable=False)  # JSON string
	created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
