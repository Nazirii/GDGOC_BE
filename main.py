from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.database import Base, engine
from app.api import auth, products, reviews, chat

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

# Register routers
app.include_router(auth.router)
app.include_router(products.router)
app.include_router(reviews.router)
app.include_router(chat.router)


@app.get("/health")
async def health():
    return {"status": "ok"}
