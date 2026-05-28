from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.chat import ChatSession, ChatMessage
from app.services import chat_service

router = APIRouter(prefix="/api/chat", tags=["Chat"])


class ChatRequest(BaseModel):
    message: str
    analys_product_id: Optional[int] = None
    design_reference_id: Optional[int] = None


class SessionCreate(BaseModel):
    title: Optional[str] = None
    product_id: Optional[int] = None


@router.post("/sessions")
async def create_session(
    data: SessionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    session = ChatSession(
        user_id=current_user.id,
        product_id=data.product_id,
        title=data.title or "New Chat",
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return {"id": session.id, "title": session.title}


@router.get("/sessions")
async def list_sessions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return chat_service.get_sessions(current_user.id, db)


@router.get("/sessions/{session_id}/messages")
async def get_messages(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    session = db.query(ChatSession).filter(
        ChatSession.id == session_id,
        ChatSession.user_id == current_user.id,
    ).first()
    if not session:
        raise HTTPException(404, "Session tidak ditemukan")
    return chat_service.get_messages(session_id, db)


@router.post("/sessions/{session_id}/send")
async def send_message(
    session_id: int,
    data: ChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    session = db.query(ChatSession).filter(
        ChatSession.id == session_id,
        ChatSession.user_id == current_user.id,
    ).first()
    if not session:
        raise HTTPException(404, "Session tidak ditemukan")

    reply, image_prompt = chat_service.chat_with_llm(
        session_id,
        current_user.id,
        data.message,
        db,
        analys_product_id=data.analys_product_id,
        design_reference_id=data.design_reference_id,
    )
    return {"reply": reply, "image_prompt": image_prompt}
