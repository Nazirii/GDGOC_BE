from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_user
from app.schemas.user import UserRegister, UserLogin, UserResponse, TokenResponse, PasswordChangeRequest
from app.services import auth_service
from app.models.user import User

router = APIRouter(prefix="/api/auth", tags=["Auth"])


@router.post("/register", response_model=UserResponse)
async def register(data: UserRegister, db: Session = Depends(get_db)):
    return auth_service.register_user(data, db)


@router.post("/login", response_model=TokenResponse)
async def login(data: UserLogin, request: Request, db: Session = Depends(get_db)):
    device_info = request.headers.get("User-Agent")
    ip = request.client.host
    return auth_service.login_user(data.email, data.password, db, device_info, ip)


@router.post("/logout")
async def logout(refresh_token: str, db: Session = Depends(get_db)):
    auth_service.logout_user(refresh_token, db)
    return {"message": "Logout berhasil"}


@router.get("/me", response_model=UserResponse)
async def me(current_user: User = Depends(get_current_user)):
    return current_user
