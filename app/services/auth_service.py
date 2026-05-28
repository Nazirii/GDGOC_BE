from datetime import datetime, timedelta
from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.models.user import User, Session as UserSession
from app.core.security import hash_password, verify_password, create_access_token, create_refresh_token
from app.core.config import settings
from app.schemas.user import UserRegister


def register_user(data: UserRegister, db: Session) -> User:
    if db.query(User).filter(User.email == data.email).first():
        raise HTTPException(status_code=400, detail="Email sudah terdaftar")

    user = User(
        email=data.email,
        full_name=data.full_name,
        phone=data.phone,
        address=data.address,
        password_hash=hash_password(data.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def login_user(email: str, password: str, db: Session, device_info: str = None, ip: str = None):
    user = db.query(User).filter(User.email == email).first()
    if not user or not verify_password(password, user.password_hash):
        raise HTTPException(status_code=401, detail="Email atau password salah")
    
    access_token  = create_access_token(user.id)
    refresh_token = create_refresh_token(user.id)

    # Simpan refresh token ke DB
    session = UserSession(
        user_id=user.id,
        refresh_token=refresh_token,
        device_info=device_info,
        ip_address=ip,
        expires_at=datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
    )
    db.add(session)
    db.commit()

    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}


def logout_user(refresh_token: str, db: Session):
    session = db.query(UserSession).filter(UserSession.refresh_token == refresh_token).first()
    if session:
        db.delete(session)
        db.commit()
