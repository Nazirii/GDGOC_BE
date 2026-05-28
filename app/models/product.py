from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base


class Product(Base):
    __tablename__ = "products"

    id           = Column(Integer, primary_key=True, index=True)
    user_id      = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    asin         = Column(String(50), nullable=False)
    source       = Column(String(20), default="amazon")   # 'amazon', 'etsy'
    category     = Column(String(50), nullable=True)       # 'pakaian', 'kerajinan'
    product_name = Column(String(500), nullable=True)
    brand        = Column(String(255), nullable=True)
    price        = Column(Float, nullable=True)
    rating       = Column(Float, nullable=True)
    review_count = Column(Integer, default=0)
    image_url    = Column(Text, nullable=True)
    product_url  = Column(Text, nullable=True)
    is_active    = Column(Boolean, default=True)
    created_at   = Column(DateTime, default=datetime.utcnow)
    updated_at   = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relasi
    user         = relationship("User", back_populates="products")
    scrape_jobs  = relationship("ScrapeJob", back_populates="product")
    reviews      = relationship("Review", back_populates="product")
    insights     = relationship("Insight", back_populates="product")
    reports      = relationship("Report", back_populates="product")
    chat_sessions= relationship("ChatSession", back_populates="product")

class AnalysProduct(Base):
    __tablename__ = "analys_products"

    id           = Column(Integer, primary_key=True, index=True)
    user_id      = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    category     = Column(String(50), nullable=True)       # 'pakaian', 'kerajinan'
    product_name = Column(String(500), nullable=True)
    description  = Column(Text, nullable=True) 
    image_url    = Column(Text, nullable=True)
    status       = Column(String(20), default="pending")   # pending, processing, done, failed
    created_at   = Column(DateTime, default=datetime.utcnow)
    updated_at   = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relasi
    user         = relationship("User", back_populates="analys_products")
    scrape_jobs  = relationship("ScrapeJob", back_populates="analys_product")
    design_references = relationship(
        "DesignReference",
        back_populates="analys_product",
        cascade="all, delete-orphan",
        order_by="DesignReference.sort_order",
    )

class ScrapeJob(Base):
    __tablename__ = "scrape_jobs"

    id            = Column(Integer, primary_key=True, index=True)
    analys_product_id  = Column(Integer, ForeignKey("analys_products.id", ondelete="CASCADE"), nullable=False)
    status        = Column(String(20), default="pending")  # pending, running, done, failed
    total_reviews = Column(Integer, default=0)
    total_product = Column(Integer, default=0)    
    processed     = Column(Integer, default=0)
    error_message = Column(Text, nullable=True)
    started_at    = Column(DateTime, nullable=True)
    finished_at   = Column(DateTime, nullable=True)
    created_at    = Column(DateTime, default=datetime.utcnow)

    analys_product = relationship("AnalysProduct", back_populates="scrape_jobs")
