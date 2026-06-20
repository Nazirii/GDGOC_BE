from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.database import Base, engine
from app.api import auth, products, reviews, chat
from app.core.security import get_current_user
from app.models.user import User

# Buat semua table otomatis (development only)
# Production: pakai alembic migrate
# Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Apparel Review Analysis API",
    version="0.1.0",
    docs_url="/docs",
)

# CORS — sesuaikan origin kalau sudah ada frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def override_get_current_user():
    # Bikin dummy user, atau query ke DB kalau butuh data real
    # Pura-puranya ini user yang lagi login
    return User(id=1, email="dev@test.com", is_active=True)

# Timpa fungsi auth asli dengan fungsi bypass di atas
app.dependency_overrides[get_current_user] = override_get_current_user

# Register routers
app.include_router(auth.router)
app.include_router(products.router)
app.include_router(reviews.router)
app.include_router(chat.router)


@app.get("/health")
async def health():
    return {"status": "ok"}
