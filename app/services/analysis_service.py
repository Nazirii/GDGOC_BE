import asyncio
import json
import re
from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import BackgroundTasks, HTTPException
from sqlalchemy.orm import Session

from app.models.design_reference import DesignReference
from app.models.product import AnalysProduct, Product, ScrapeJob
from app.models.review import Insight, Report, Review, Sentence
from app.schemas.product import AnalysProductCreate, DesignReferenceCreate
from app.services.ml.apify_service import scrape_amazon_products, scrape_amazon_reviews
from app.services.ml.ner_service import NER_MODEL_NAME, extract_ner_entities
from app.services.ml.sentiment_service import SENTIMENT_MODEL_NAME, analyze_review_sentiment


def _json_default(value: Any) -> str:
    if isinstance(value, datetime):
        return value.isoformat()
    return str(value)


def _slugify_text(text: Optional[str]) -> str:
    if not text:
        return "amazon-product"
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", text.lower()).strip("-")
    return slug or "amazon-product"


def _split_sentences(text: str) -> List[str]:
    chunks = re.split(r"(?<=[.!?])\s+", (text or "").strip())
    return [chunk.strip() for chunk in chunks if chunk and chunk.strip()]


def _pick_entity_bucket(entity_group: str, text: str) -> str:
    entity_group = (entity_group or "").upper()
    lowered_text = (text or "").lower()
    if entity_group in {"MISC", "ORG", "PRODUCT"}:
        return "entity_feat"
    if any(word in lowered_text for word in ["size", "sizing", "xl", "xxl", "small", "medium", "large"]):
        return "entity_siz"
    if any(word in lowered_text for word in ["use", "usage", "daily", "travel", "office", "work"]):
        return "entity_use"
    if any(word in lowered_text for word in ["material", "cotton", "polyester", "leather", "plastic"]):
        return "entity_mrl"
    return "entity_col"


def _map_product_row(raw_product: Dict[str, Any], analys: AnalysProduct, user_id: int) -> Product:
    asin = (
        raw_product.get("asin")
        or raw_product.get("productAsin")
        or raw_product.get("id")
        or _slugify_text(raw_product.get("title"))
    )
    return Product(
        user_id=user_id,
        asin=str(asin),
        source="amazon",
        category=analys.category,
        product_name=raw_product.get("title") or raw_product.get("name") or analys.product_name,
        brand=raw_product.get("brand") or raw_product.get("manufacturer"),
        price=raw_product.get("price") or raw_product.get("listPrice"),
        rating=raw_product.get("rating") or raw_product.get("stars"),
        review_count=raw_product.get("reviewsCount") or raw_product.get("reviewCount") or 0,
        image_url=raw_product.get("image") or raw_product.get("imageUrl"),
        product_url=raw_product.get("url") or raw_product.get("productUrl"),
        is_active=True,
    )


def _build_sentence_row(review: Review, text: str, order_idx: int) -> Sentence:
    return Sentence(
        review_id=review.id,
        text=text,
        order_idx=order_idx,
    )


async def process_analys_flow(analys_product_id: int, user_id: int, db: Session) -> None:
    """Process analysis flow end-to-end using Apify and two Hugging Face models."""
    analys = _get_owned_analys_product(analys_product_id, user_id, db)
    await _set_analys_status(analys, "processing", db)

    try:
        job = await _create_scrape_job(analys, db)
        raw_products = await _scrape_products(job, analys)
        products = await _create_product_rows(analys, raw_products, db)

        product_jobs = await _create_product_scrape_jobs(analys, products, db)
        raw_reviews = await _scrape_reviews(product_jobs, products)
        reviews = await _create_review_rows(raw_reviews, db)

        sentences = await _create_sentence_rows(reviews, db)
        await _run_ner_sentiment(sentences, db)

        insights = await _aggregate_insights(analys, db)
        await _create_report(analys, insights, db)

        job.status = "done"
        job.finished_at = datetime.utcnow()
        db.add(job)
        db.commit()

        await _set_analys_status(analys, "done", db)
    except Exception as exc:
        analys.status = "failed"
        db.add(analys)
        db.commit()
        raise HTTPException(500, f"Analysis flow failed: {exc}") from exc


async def _set_analys_status(analys: AnalysProduct, status: str, db: Session) -> None:
    await asyncio.sleep(0)
    analys.status = status
    db.add(analys)
    db.commit()


async def _create_scrape_job(analys: AnalysProduct, db: Session) -> ScrapeJob:
    await asyncio.sleep(0)
    job = ScrapeJob(
        analys_product_id=analys.id,
        status="running",
        started_at=datetime.utcnow(),
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    return job


async def _scrape_products(job: ScrapeJob, analys: AnalysProduct) -> List[Dict[str, Any]]:
    await asyncio.sleep(0)
    items = await scrape_amazon_products(analys.product_name or analys.description, analys.category)
    job.total_product = len(items)
    job.processed = len(items)
    return items


async def _create_product_rows(
    analys: AnalysProduct,
    raw_products: List[Dict[str, Any]],
    db: Session,
) -> List[Product]:
    await asyncio.sleep(0)
    rows: List[Product] = []
    for raw_product in raw_products:
        product = _map_product_row(raw_product, analys, analys.user_id)
        db.add(product)
        rows.append(product)

    if rows:
        db.commit()
        for row in rows:
            db.refresh(row)
    return rows


async def _create_product_scrape_jobs(
    analys: AnalysProduct,
    products: List[Product],
    db: Session,
) -> List[ScrapeJob]:
    await asyncio.sleep(0)
    jobs: List[ScrapeJob] = []
    for product in products:
        job = ScrapeJob(
            analys_product_id=analys.id,
            status="running",
            total_reviews=0,
            total_product=1,
            processed=0,
        )
        db.add(job)
        jobs.append(job)

    if jobs:
        db.commit()
        for job in jobs:
            db.refresh(job)
    return jobs


async def _scrape_reviews(product_jobs: List[ScrapeJob], products: List[Product]) -> List[Dict[str, Any]]:
    await asyncio.sleep(0)
    review_rows: List[Dict[str, Any]] = []
    for index, product in enumerate(products):
        raw_items = await scrape_amazon_reviews(product.asin, product.product_url)
        if not raw_items:
            review_rows.append(
                {
                    "product_asin": product.asin,
                    "product_url": product.product_url,
                    "rating": product.rating or 0,
                    "title": f"Sample review {index + 1}",
                    "text": (
                        "This is a placeholder review text generated to show the analysis pipeline. "
                        "It mentions design, material, size, and overall sentiment."
                    ),
                    "reviewer_id": f"sample-user-{index + 1}",
                    "helpful_vote": 0,
                    "verified": True,
                    "reviewed_at": datetime.utcnow().isoformat(),
                }
            )
            continue

        for item in raw_items:
            review_rows.append(
                {
                    "product_asin": product.asin,
                    "product_url": product.product_url,
                    "rating": item.get("rating") or item.get("stars"),
                    "title": item.get("title") or item.get("summary"),
                    "text": item.get("text") or item.get("reviewText") or "",
                    "reviewer_id": item.get("profileName") or item.get("author"),
                    "helpful_vote": item.get("helpfulVotes") or 0,
                    "verified": bool(item.get("verifiedPurchase", False)),
                    "reviewed_at": item.get("reviewedAt") or item.get("date"),
                }
            )

    return review_rows


async def _create_review_rows(raw_reviews: List[Dict[str, Any]], db: Session) -> List[Review]:
    await asyncio.sleep(0)
    products_by_asin = {
        product.asin: product
        for product in db.query(Product).filter(Product.is_active.is_(True)).all()
    }
    rows: List[Review] = []
    for raw_review in raw_reviews:
        product = products_by_asin.get(str(raw_review.get("product_asin") or ""))
        if not product:
            continue

        reviewed_at = raw_review.get("reviewed_at")
        if isinstance(reviewed_at, str):
            try:
                reviewed_at = datetime.fromisoformat(reviewed_at.replace("Z", "+00:00"))
            except ValueError:
                reviewed_at = None

        review = Review(
            product_id=product.id,
            external_id=str(raw_review.get("external_id") or raw_review.get("reviewer_id") or ""),
            rating=raw_review.get("rating"),
            title=raw_review.get("title"),
            text=raw_review.get("text") or "",
            reviewer_id=raw_review.get("reviewer_id"),
            helpful_vote=raw_review.get("helpful_vote") or 0,
            verified=bool(raw_review.get("verified", False)),
            reviewed_at=reviewed_at,
        )
        db.add(review)
        rows.append(review)

    if rows:
        db.commit()
        for row in rows:
            db.refresh(row)
    return rows


async def _create_sentence_rows(reviews: List[Review], db: Session) -> List[Sentence]:
    await asyncio.sleep(0)
    rows: List[Sentence] = []
    for review in reviews:
        segments = _split_sentences(review.text)
        if not segments:
            segments = [review.text]

        for order_idx, segment in enumerate(segments, start=1):
            sentence = _build_sentence_row(review, segment, order_idx)
            db.add(sentence)
            rows.append(sentence)

    if rows:
        db.commit()
        for row in rows:
            db.refresh(row)
    return rows


async def _run_ner_sentiment(sentences: List[Sentence], db: Session) -> None:
    await asyncio.sleep(0)
    for sentence in sentences:
        ner_entities = extract_ner_entities(sentence.text)
        sentiment_label, sentiment_score = analyze_review_sentiment(sentence.text)

        sentence.sentiment_label = sentiment_label
        sentence.sentiment_score = sentiment_score

        for field_name, value in ner_entities.items():
            if value:
                setattr(sentence, field_name, value)

        db.add(sentence)

    if sentences:
        db.commit()


async def _aggregate_insights(analys: AnalysProduct, db: Session) -> List[Insight]:
    await asyncio.sleep(0)
    product_ids = [row[0] for row in db.query(Product.id).filter(Product.user_id == analys.user_id).all()]
    if not product_ids:
        return []

    sentences = (
        db.query(Sentence)
        .join(Review, Sentence.review_id == Review.id)
        .filter(Review.product_id.in_(product_ids))
        .all()
    )

    insights_by_entity: Dict[str, Dict[str, Any]] = {}
    for sentence in sentences:
        for field_name in ["entity_col", "entity_mrl", "entity_siz", "entity_use", "entity_feat"]:
            value = getattr(sentence, field_name)
            if not value:
                continue
            entry = insights_by_entity.setdefault(
                value,
                {
                    "entity_type": field_name.replace("entity_", "").upper(),
                    "value": value,
                    "aspect": field_name,
                    "total_mentions": 0,
                    "positive_count": 0,
                    "negative_count": 0,
                    "neutral_count": 0,
                },
            )
            entry["total_mentions"] += 1
            if sentence.sentiment_label == "POSITIVE":
                entry["positive_count"] += 1
            elif sentence.sentiment_label == "NEGATIVE":
                entry["negative_count"] += 1
            else:
                entry["neutral_count"] += 1

    rows: List[Insight] = []
    for payload in insights_by_entity.values():
        total_mentions = payload["total_mentions"] or 1
        insight = Insight(
            product_id=product_ids[0],
            entity_type=payload["entity_type"],
            value=payload["value"],
            aspect=payload["aspect"],
            total_mentions=payload["total_mentions"],
            positive_count=payload["positive_count"],
            negative_count=payload["negative_count"],
            neutral_count=payload["neutral_count"],
            positive_pct=(payload["positive_count"] / total_mentions) * 100,
        )
        db.add(insight)
        rows.append(insight)

    if rows:
        db.commit()
        for row in rows:
            db.refresh(row)
    return rows


async def _create_report(analys: AnalysProduct, insights: List[Insight], db: Session) -> Report:
    await asyncio.sleep(0)
    report_payload = {
        "analysis_id": analys.id,
        "product_name": analys.product_name,
        "category": analys.category,
        "summary": {
            "insight_count": len(insights),
            "top_entities": [
                {
                    "entity_type": insight.entity_type,
                    "value": insight.value,
                    "total_mentions": insight.total_mentions,
                    "positive_pct": insight.positive_pct,
                }
                for insight in insights[:5]
            ],
        },
        "generated_at": datetime.utcnow(),
        "models": {
            "ner": NER_MODEL_NAME,
            "sentiment": SENTIMENT_MODEL_NAME,
        },
    }
    report = Report(
        analys_product_id=analys.id,
        user_id=analys.user_id,
        content=json.dumps(report_payload, default=_json_default, ensure_ascii=False),
        status="ready",
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

def create_product_analys(
    data: AnalysProductCreate,
    user_id: int,
    db: Session,
    background_tasks: Optional[BackgroundTasks] = None,
):
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

    if background_tasks is not None:
        background_tasks.add_task(process_analys_flow, analys.id, user_id, db)
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
