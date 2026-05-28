from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base


class ChatSession(Base):
    __tablename__ = "chat_sessions"

    id         = Column(Integer, primary_key=True, index=True)
    user_id    = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id", ondelete="SET NULL"), nullable=True)
    title      = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user       = relationship("User", back_populates="chat_sessions")
    product    = relationship("Product", back_populates="chat_sessions")
    messages   = relationship("ChatMessage", back_populates="session")


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id          = Column(Integer, primary_key=True, index=True)
    session_id  = Column(Integer, ForeignKey("chat_sessions.id", ondelete="CASCADE"), nullable=False)
    role        = Column(String(20), nullable=False)   # 'user' atau 'assistant'
    content     = Column(Text, nullable=False)
    token_count = Column(Integer, nullable=True)
    created_at  = Column(DateTime, default=datetime.utcnow)

    session     = relationship("ChatSession", back_populates="messages")
