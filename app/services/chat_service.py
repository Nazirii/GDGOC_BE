import json
import os
import urllib.error
import urllib.request
from typing import List, Optional, Tuple

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.chat import ChatSession, ChatMessage
from app.models.product import AnalysProduct
from app.models.design_reference import DesignReference
from app.models.review import Report


def get_sessions(user_id: int, db: Session):
    return db.query(ChatSession).filter(ChatSession.user_id == user_id).all()


def get_messages(session_id: int, db: Session):
    return (
        db.query(ChatMessage)
        .filter(ChatMessage.session_id == session_id)
        .order_by(ChatMessage.created_at)
        .all()
    )


def save_message(session_id: int, role: str, content: str, db: Session) -> ChatMessage:
    msg = ChatMessage(session_id=session_id, role=role, content=content)
    db.add(msg)
    db.commit()
    db.refresh(msg)
    return msg

def _get_recent_messages(session_id: int, db: Session, limit: int = 8) -> List[ChatMessage]:
    return (
        db.query(ChatMessage)
        .filter(ChatMessage.session_id == session_id)
        .order_by(ChatMessage.created_at.desc())
        .limit(limit)
        .all()[::-1]
    )


def _load_report_summary(report: Optional[Report]) -> Optional[dict]:
    if not report or not report.content:
        return None
    try:
        payload = json.loads(report.content)
    except json.JSONDecodeError:
        return {"raw": report.content}

    if isinstance(payload, dict):
        summary = payload.get("summary")
        if summary:
            return summary
    return payload if isinstance(payload, dict) else None


def _build_context(
    analys: Optional[AnalysProduct],
    design_ref: Optional[DesignReference],
    report_summary: Optional[dict],
) -> str:
    context = {
        "analysis": None,
        "design_reference": None,
        "report_summary": report_summary,
    }

    if analys:
        context["analysis"] = {
            "id": analys.id,
            "category": analys.category,
            "product_name": analys.product_name,
            "description": analys.description,
            "status": analys.status,
        }

    if design_ref:
        context["design_reference"] = {
            "id": design_ref.id,
            "title": design_ref.title,
            "description": design_ref.description,
            "image_url": design_ref.image_url,
            "tags": design_ref.tags or [],
        }

    return json.dumps(context, ensure_ascii=True)


def _build_prompt(context_text: str, history_text: str, user_message: str) -> str:
    return (
        "You are a helpful product design assistant. "
        "Use the provided context to answer. "
        "Return JSON only with keys: reply_text (string), needs_image (boolean), image_prompt (string or null). "
        "Do not include markdown or extra text.\n\n"
        f"Context JSON: {context_text}\n\n"
        f"Recent chat:\n{history_text}\n\n"
        f"User message: {user_message}"
    )


def _extract_json(text: str) -> Optional[dict]:
    trimmed = text.strip()
    if trimmed.startswith("```"):
        trimmed = trimmed.strip("`")
        trimmed = trimmed.replace("json\n", "", 1).strip()
    try:
        payload = json.loads(trimmed)
    except json.JSONDecodeError:
        return None
    return payload if isinstance(payload, dict) else None


def _call_gemini(prompt: str, api_key: str) -> str:
    url = (
        "https://generativelanguage.googleapis.com/v1beta/models/"
        "gemini-1.5-flash:generateContent?key="
        + api_key
    )
    body = {
        "contents": [
            {
                "role": "user",
                "parts": [{"text": prompt}],
            }
        ],
        "generationConfig": {
            "temperature": 0.4,
            "maxOutputTokens": 512,
        },
    }

    data = json.dumps(body).encode("utf-8")
    request = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    with urllib.request.urlopen(request, timeout=30) as response:
        payload = json.loads(response.read().decode("utf-8"))

    candidates = payload.get("candidates") or []
    if not candidates:
        return ""
    parts = candidates[0].get("content", {}).get("parts", [])
    if not parts:
        return ""
    return parts[0].get("text", "")


def chat_with_llm(
    session_id: int,
    user_id: int,
    user_message: str,
    db: Session,
    analys_product_id: Optional[int] = None,
    design_reference_id: Optional[int] = None,
) -> Tuple[str, Optional[str]]:
    save_message(session_id, "user", user_message, db)

    analys = None
    design_ref = None
    report_summary = None

    if analys_product_id is not None:
        analys = db.query(AnalysProduct).filter(
            AnalysProduct.id == analys_product_id,
            AnalysProduct.user_id == user_id,
        ).first()
        if not analys:
            raise HTTPException(404, "Analisis tidak ditemukan")

        report = db.query(Report).filter(
            Report.analys_product_id == analys_product_id,
        ).order_by(Report.id.desc()).first()
        report_summary = _load_report_summary(report)

    if design_reference_id is not None:
        design_ref = db.query(DesignReference).filter(
            DesignReference.id == design_reference_id,
            DesignReference.analys_product_id == analys_product_id,
        ).first()
        if not design_ref:
            raise HTTPException(404, "Referensi desain tidak ditemukan")

    recent_messages = _get_recent_messages(session_id, db, limit=8)
    history_text = "\n".join(f"{m.role}: {m.content}" for m in recent_messages)
    context_text = _build_context(analys, design_ref, report_summary)

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        reply = "GEMINI_API_KEY belum diset. Set env ini untuk mengaktifkan chatbot."
        image_prompt = None
    else:
        prompt = _build_prompt(context_text, history_text, user_message)
        try:
            raw_text = _call_gemini(prompt, api_key)
        except (urllib.error.URLError, TimeoutError, ValueError):
            raw_text = ""

        payload = _extract_json(raw_text) if raw_text else None
        if not payload:
            reply = "Maaf, aku gagal memproses jawaban AI saat ini."
            image_prompt = None
        else:
            reply = payload.get("reply_text") or ""
            needs_image = bool(payload.get("needs_image"))
            image_prompt = payload.get("image_prompt") if needs_image else None

    save_message(session_id, "assistant", reply, db)
    return reply, image_prompt
