from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base


class User(Base):
    __tablename__ = "users"

    id            = Column(Integer, primary_key=True, index=True)
    email         = Column(String(255), unique=True, nullable=False, index=True)
    phone         = Column(String(20), nullable=True)
    address       = Column(String(255), nullable=True)
    password_hash = Column(String(255), nullable=False)
    full_name     = Column(String(255), nullable=True)
    company_name  = Column(String(255), nullable=True)
    created_at    = Column(DateTime, default=datetime.utcnow)
    updated_at    = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relasi
    products      = relationship("Product", back_populates="user")
    analys_products = relationship("AnalysProduct", back_populates="user")
    chat_sessions = relationship("ChatSession", back_populates="user")
    sessions      = relationship("Session", back_populates="user")


class Session(Base):
    __tablename__ = "sessions"

    id            = Column(Integer, primary_key=True, index=True)
    user_id       = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    refresh_token = Column(String(500), unique=True, nullable=False)
    device_info   = Column(String(255), nullable=True)
    ip_address    = Column(String(50), nullable=True)
    expires_at    = Column(DateTime, nullable=False)
    created_at    = Column(DateTime, default=datetime.utcnow)

    user          = relationship("User", back_populates="sessions")


