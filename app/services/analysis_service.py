# Placeholder — akan diisi logic NER + Sentiment nanti
import asyncio
import json
from typing import Any, Dict, List, Optional

from fastapi import HTTPException
from sqlalchemy.orm import Session
from fastapi import BackgroundTasks
from app.models.design_reference import DesignReference
from app.models.product import AnalysProduct, Product, ScrapeJob
from app.models.review import Insight, Report, Review, Sentence
from app.schemas.product import AnalysProductCreate, DesignReferenceCreate


async def process_analys_flow(analys_product_id: int, user_id: int, db: Session) -> None:
    """Process analysis flow end-to-end (skeleton only)."""
    analys = _get_owned_analys_product(analys_product_id, user_id, db)
    await _set_analys_status(analys, "processing", db)

    job = await _create_scrape_job(analys, db)
    raw_products = await _scrape_products(job, analys)
    products = await _create_product_rows(analys, raw_products, db)

    product_jobs = await _create_product_scrape_jobs(analys, products, db)
    raw_reviews = await _scrape_reviews(product_jobs)
    reviews = await _create_review_rows(raw_reviews, db)

    sentences = await _create_sentence_rows(reviews, db)
    await _run_ner_sentiment(sentences, db)

    insights = await _aggregate_insights(analys, db)
    await _create_report(analys, insights, db)

    await _set_analys_status(analys, "done", db)


async def _set_analys_status(analys: AnalysProduct, status: str, db: Session) -> None:
    await asyncio.sleep(0)
    analys.status = status
    db.add(analys)
    db.commit()


async def _create_scrape_job(analys: AnalysProduct, db: Session) -> ScrapeJob:
    await asyncio.sleep(0)
    job = ScrapeJob(analys_product_id=analys.id, status="pending")
    db.add(job)
    db.commit()
    db.refresh(job)
    return job


async def _scrape_products(job: ScrapeJob, analys: AnalysProduct) -> List[Dict[str, Any]]:
    await asyncio.sleep(0)
    return []


async def _create_product_rows(
    analys: AnalysProduct,
    raw_products: List[Dict[str, Any]],
    db: Session,
) -> List[Product]:
    await asyncio.sleep(0)
    return []


async def _create_product_scrape_jobs(
    analys: AnalysProduct,
    products: List[Product],
    db: Session,
) -> List[ScrapeJob]:
    await asyncio.sleep(0)
    return []


async def _scrape_reviews(product_jobs: List[ScrapeJob]) -> List[Dict[str, Any]]:
    await asyncio.sleep(0)
    return []


async def _create_review_rows(raw_reviews: List[Dict[str, Any]], db: Session) -> List[Review]:
    await asyncio.sleep(0)
    return []


async def _create_sentence_rows(reviews: List[Review], db: Session) -> List[Sentence]:
    await asyncio.sleep(0)
    return []


async def _run_ner_sentiment(sentences: List[Sentence], db: Session) -> None:
    await asyncio.sleep(0)


async def _aggregate_insights(analys: AnalysProduct, db: Session) -> List[Insight]:
    await asyncio.sleep(0)
    return []


async def _create_report(analys: AnalysProduct, insights: List[Insight], db: Session) -> Report:
    await asyncio.sleep(0)
    report = Report(
        analys_product_id=analys.id,
        user_id=analys.user_id,
        content=None,
        status="draft",
    )
    db.add(report)
    db.commit()
    db.refresh(report)
    return report

def _get_owned_analys_product(analys_product_id: int, user_id: int, db: Session) -> AnalysProduct:
    analys = db.query(AnalysProduct).filter(
        AnalysProduct.id == analys_product_id,
        AnalysProduct.user_id == user_id,
    ).first()
    if not analys:
        raise HTTPException(404, "Produk tidak ditemukan")
    return analys

def create_product_analys(data: AnalysProductCreate, user_id: int, db: Session):
    analys = AnalysProduct(
        user_id=user_id,
        category=data.category,
        product_name=data.product_name,
        description=data.description,
        status="pending",
    )
    db.add(analys)
    db.commit()
    db.refresh(analys)

    # generate_insights(analys.id, db)  # Jalankan pipeline analisis (placeholder)
    BackgroundTasks.add_task(process_analys_flow, analys.id, user_id, db)  # Jalankan pipeline analisis di background
    return analys

def get_product_analys(analys_product_id: int, user_id: int, db: Session):
    analys = _get_owned_analys_product(analys_product_id, user_id, db)

    report = db.query(Report).filter(
        Report.analys_product_id == analys_product_id,
    ).order_by(Report.id.desc()).first()

    report_content = None
    if report and report.content:
        try:
            report_content = json.loads(report.content)
        except json.JSONDecodeError:
            report_content = report.content

    design_references = [
        {
            "id": ref.id,
            "analys_product_id": ref.analys_product_id,
            "title": ref.title,
            "description": ref.description,
            "image_url": ref.image_url,
            "tags": ref.tags or [],
            "sort_order": ref.sort_order,
            "created_at": ref.created_at,
            "updated_at": ref.updated_at,
        }
        for ref in db.query(DesignReference)
        .filter(DesignReference.analys_product_id == analys_product_id)
        .order_by(DesignReference.sort_order.asc(), DesignReference.id.asc())
        .all()
    ]

    response = {
        "id": analys.id,
        "user_id": analys.user_id,
        "category": analys.category,
        "product_name": analys.product_name,
        "description": analys.description,
        "image_url": analys.image_url,
        "status": analys.status,
        "created_at": analys.created_at,
        "updated_at": analys.updated_at,
        "report": report_content,
        "design_references": design_references,
        "message": "Analisis sedang diproses, silakan cek kembali nanti",
    }

    if analys.status == "done":
        response.pop("message", None)

    return response


def list_design_references(analys_product_id: int, user_id: int, db: Session):
    _get_owned_analys_product(analys_product_id, user_id, db)
    return db.query(DesignReference).filter(
        DesignReference.analys_product_id == analys_product_id,
    ).order_by(DesignReference.sort_order.asc(), DesignReference.id.asc()).all()


def create_design_reference(
    analys_product_id: int,
    user_id: int,
    data: DesignReferenceCreate,
    db: Session,
):
    _get_owned_analys_product(analys_product_id, user_id, db)

    reference = DesignReference(
        analys_product_id=analys_product_id,
        title=data.title,
        description=data.description,
        image_url=data.image_url,
        tags=data.tags or [],
        sort_order=data.sort_order or 0,
    )
    db.add(reference)
    db.commit()
    db.refresh(reference)
    return reference
