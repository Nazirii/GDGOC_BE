from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.services import analysis_service
from app.models.product import AnalysProduct
from app.schemas.product import (
    AnalysProductCreate,
    AnalysProductResponse,
    AnalysProductDescriptionResponse,
    DesignReferenceCreate,
    DesignReferenceResponse,
)

router = APIRouter(prefix="/api/analys_products", tags=["Products"])


@router.post("/", response_model=AnalysProductResponse)
async def create_analys_product(
    data: AnalysProductCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return analysis_service.create_product_analys(
        data,
        current_user.id,
        db,
        background_tasks,
    )


@router.get("/", response_model=List[AnalysProductResponse])
async def list_analys_products(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return db.query(AnalysProduct).filter(AnalysProduct.user_id == current_user.id).all()


@router.get("/{analys_product_id}", response_model=AnalysProductDescriptionResponse)
async def get_analys_product(
    analys_product_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return analysis_service.get_product_analys(analys_product_id, current_user.id, db)


@router.delete("/{analys_product_id}")
async def delete_product(
    analys_product_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    analys_product = db.query(AnalysProduct).filter(
        AnalysProduct.id == analys_product_id,
        AnalysProduct.user_id == current_user.id,
    ).first()
    if not analys_product:
        raise HTTPException(404, "Produk tidak ditemukan")
    db.delete(analys_product)
    db.commit()
    return {"message": "Produk dihapus"}


@router.get("/{analys_product_id}/design-references", response_model=List[DesignReferenceResponse])
async def list_design_references(
    analys_product_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return analysis_service.list_design_references(analys_product_id, current_user.id, db)


@router.post("/{analys_product_id}/design-references", response_model=DesignReferenceResponse)
async def create_design_reference(
    analys_product_id: int,
    data: DesignReferenceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return analysis_service.create_design_reference(analys_product_id, current_user.id, data, db)
