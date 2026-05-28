from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class AnalysProductCreate(BaseModel):
    category: Optional[str] = None   # 'pakaian', 'kerajinan'
    product_name: Optional[str] = None
    description: Optional[str] = None


class AnalysProductResponse(BaseModel):
    id: int
    user_id: int
    category: Optional[str]
    product_name: Optional[str]
    description: Optional[str]
    image_url: Optional[str]
    status: str
    created_at: datetime
    updated_at: datetime
    message: Optional[str] = "Analisis sedang diproses, silakan cek kembali nanti"

    class Config:
        from_attributes = True

class AnalysProductDescriptionResponse(BaseModel):
    id: int
    user_id: int
    category: Optional[str]
    product_name: Optional[str]
    description: Optional[str]
    image_url: Optional[str]
    report: Optional[dict] = None
    design_references: List[dict] = []
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ScrapeJobResponse(BaseModel):
    id: int
    analys_product_id: int
    status: str
    total_reviews: int
    processed: int
    error_message: Optional[str]
    started_at: Optional[datetime]
    finished_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True


class DesignReferenceCreate(BaseModel):
    title: str
    description: Optional[str] = None
    image_url: Optional[str] = None
    tags: List[str] = []
    sort_order: Optional[int] = 0


class DesignReferenceResponse(BaseModel):
    id: int
    analys_product_id: int
    title: str
    description: Optional[str]
    image_url: Optional[str]
    tags: List[str] = []
    sort_order: int = 0
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
