from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.product import Product
from app.models.review import Review, Insight
from app.schemas.review import ReviewIngest, InsightResponse
from app.services import analysis_service

router = APIRouter(prefix="/api/reviews", tags=["Reviews"])


@router.post("/{product_id}/ingest")
async def ingest_reviews(
    product_id: int,
    reviews: List[ReviewIngest],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    product = db.query(Product).filter(
        Product.id == product_id,
        Product.user_id == current_user.id,
    ).first()
    if not product:
        raise HTTPException(404, "Produk tidak ditemukan")

    inserted = 0
    for r in reviews:
        # Skip duplikat
        if r.external_id:
            exists = db.query(Review).filter(
                Review.product_id == product_id,
                Review.external_id == r.external_id,
            ).first()
            if exists:
                continue

        review = Review(**r.model_dump(), product_id=product_id)
        db.add(review)
        inserted += 1

    db.commit()
    return {"message": f"{inserted} review berhasil dimasukkan"}


@router.get("/{product_id}/insights", response_model=List[InsightResponse])
async def get_insights(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    product = db.query(Product).filter(
        Product.id == product_id,
        Product.user_id == current_user.id,
    ).first()
    if not product:
        raise HTTPException(404, "Produk tidak ditemukan")

    return analysis_service.get_insights(product_id, db)


@router.post("/{product_id}/analyze")
async def analyze_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # TODO: trigger pipeline NER + Sentiment
    return {"message": "Analisis dijadwalkan (coming soon)"}
