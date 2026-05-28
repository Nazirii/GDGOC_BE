from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class ReviewIngest(BaseModel):
    external_id: Optional[str]
    rating: Optional[float]
    title: Optional[str]
    text: str
    reviewer_id: Optional[str]
    helpful_vote: Optional[int] = 0
    verified: Optional[bool] = False


class InsightResponse(BaseModel):
    entity_type: Optional[str]
    value: Optional[str]
    aspect: Optional[str]
    total_mentions: int
    positive_count: int
    negative_count: int
    positive_pct: Optional[float]

    class Config:
        from_attributes = True
