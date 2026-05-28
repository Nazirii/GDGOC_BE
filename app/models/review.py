from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base




class Review(Base):
    __tablename__ = "reviews"

    id            = Column(Integer, primary_key=True, index=True)
    product_id    = Column(Integer, ForeignKey("products.id", ondelete="CASCADE"), nullable=False)
    scrape_job_id = Column(Integer, ForeignKey("scrape_jobs.id", ondelete="SET NULL"), nullable=True)
    external_id   = Column(String(255), nullable=True)
    rating        = Column(Float, nullable=True)
    title         = Column(Text, nullable=True)
    text          = Column(Text, nullable=False)
    reviewer_id   = Column(String(255), nullable=True)
    helpful_vote  = Column(Integer, default=0)
    verified      = Column(Boolean, default=False)
    reviewed_at   = Column(DateTime, nullable=True)
    created_at    = Column(DateTime, default=datetime.utcnow)

    # Relasi
    product       = relationship("Product", back_populates="reviews")
    sentences     = relationship("Sentence", back_populates="review")


class Sentence(Base):
    __tablename__ = "sentences"

    id              = Column(Integer, primary_key=True, index=True)
    review_id       = Column(Integer, ForeignKey("reviews.id", ondelete="CASCADE"), nullable=False)
    text            = Column(Text, nullable=False)
    order_idx       = Column(Integer, nullable=False)
    entity_col      = Column(String(255), nullable=True)
    entity_mrl      = Column(String(255), nullable=True)
    entity_siz      = Column(String(255), nullable=True)
    entity_use      = Column(String(255), nullable=True)
    entity_feat     = Column(String(255), nullable=True)
    sentiment_label = Column(String(20), nullable=True)   # POSITIVE, NEGATIVE, NEUTRAL
    sentiment_score = Column(Float, nullable=True)

    # Relasi
    review          = relationship("Review", back_populates="sentences")


class Insight(Base):
    __tablename__ = "insights"
  
    id               = Column(Integer, primary_key=True, index=True)
    product_id       = Column(Integer, ForeignKey("products.id", ondelete="CASCADE"), nullable=False)
    entity_type      = Column(String(10), nullable=True)
    value            = Column(String(255), nullable=True)
    aspect           = Column(String(50), nullable=True)
    total_mentions   = Column(Integer, default=0)
    positive_count   = Column(Integer, default=0)
    negative_count   = Column(Integer, default=0)
    neutral_count    = Column(Integer, default=0)
    positive_pct     = Column(Float, nullable=True)
    generated_at     = Column(DateTime, default=datetime.utcnow)

    product          = relationship("Product", back_populates="insights")


class Report(Base):
    __tablename__ = "reports"

    id          = Column(Integer, primary_key=True, index=True)
    analys_product_id  = Column(Integer, ForeignKey("analys_products.id", ondelete="CASCADE"), nullable=False)
    user_id     = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    content     = Column(Text, nullable=True)
    status      = Column(String(20), default="draft")   # draft, ready
    created_at  = Column(DateTime, default=datetime.utcnow)

    product     = relationship("Product", back_populates="reports")
