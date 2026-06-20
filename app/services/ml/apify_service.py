import asyncio
import json
import os
from typing import Any, Dict, List, Optional

APIFY_DEFAULT_PRODUCTS_ACTOR = os.getenv(
    "APIFY_AMAZON_PRODUCTS_ACTOR_ID",
    "apify/amazon-product-scraper",
)
APIFY_DEFAULT_REVIEWS_ACTOR = os.getenv(
    "APIFY_AMAZON_REVIEWS_ACTOR_ID",
    "apify/amazon-reviews-scraper",
)


async def _call_apify_actor(actor_id: str, payload: Dict[str, Any]) -> List[Dict[str, Any]]:
    await asyncio.sleep(0)

    token = os.getenv("APIFY_API_TOKEN")
    if not token:
        return []

    request_payload = json.dumps(payload).encode("utf-8")
    url = f"https://api.apify.com/v2/acts/{actor_id}/run-sync-get-dataset-items?token={token}"

    def _request() -> List[Dict[str, Any]]:
        import urllib.request

        request = urllib.request.Request(
            url,
            data=request_payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(request, timeout=120) as response:
            raw = response.read().decode("utf-8")
        data = json.loads(raw)
        return data if isinstance(data, list) else []

    try:
        return await asyncio.to_thread(_request)
    except Exception:
        return []


def build_amazon_product_payload(search_term: Optional[str], category: Optional[str]) -> Dict[str, Any]:
    keyword = search_term or category or "amazon"
    return {
        "searchTerms": [keyword],
        "maxItems": 10,
        "scrapeReviews": True,
        "sortBy": "relevance",
        "language": "en",
    }


def build_amazon_review_payload(asin: str, product_url: Optional[str]) -> Dict[str, Any]:
    return {
        "asin": asin,
        "productUrls": [product_url] if product_url else [],
        "maxReviews": 25,
        "sortBy": "recent",
        "proxyConfiguration": {"useApifyProxy": True},
    }


async def scrape_amazon_products(search_term: Optional[str], category: Optional[str]) -> List[Dict[str, Any]]:
    payload = build_amazon_product_payload(search_term, category)
    return await _call_apify_actor(APIFY_DEFAULT_PRODUCTS_ACTOR, payload)


async def scrape_amazon_reviews(asin: str, product_url: Optional[str]) -> List[Dict[str, Any]]:
    payload = build_amazon_review_payload(asin, product_url)
    return await _call_apify_actor(APIFY_DEFAULT_REVIEWS_ACTOR, payload)
