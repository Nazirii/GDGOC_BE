from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import relationship

from app.core.database import Base


class DesignReference(Base):
    __tablename__ = "design_references"

    id = Column(Integer, primary_key=True, index=True)
    analys_product_id = Column(Integer, ForeignKey("analys_products.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    image_url = Column(Text, nullable=True)
    tags = Column(JSON, nullable=False, default=list)
    sort_order = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    analys_product = relationship("AnalysProduct", back_populates="design_references")