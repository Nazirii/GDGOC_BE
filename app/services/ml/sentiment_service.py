import importlib
import os
from typing import Optional, Tuple

SENTIMENT_MODEL_NAME = os.getenv(
    "SENTIMENT_MODEL_NAME",
    "nlptown/bert-base-multilingual-uncased-sentiment",
)
_SENTIMENT_PIPELINE = None


def _load_sentiment_pipeline():
    global _SENTIMENT_PIPELINE
    if _SENTIMENT_PIPELINE is not None:
        return _SENTIMENT_PIPELINE

    try:
        transformers_module = importlib.import_module("transformers")
        pipeline = transformers_module.pipeline
        _SENTIMENT_PIPELINE = pipeline(
            "sentiment-analysis",
            model=SENTIMENT_MODEL_NAME,
        )
    except Exception:
        _SENTIMENT_PIPELINE = None
    return _SENTIMENT_PIPELINE


def _normalize_sentiment_label(label: str) -> str:
    normalized = (label or "").upper()
    if "1" in normalized or "2" in normalized or "NEG" in normalized:
        return "NEGATIVE"
    if "3" in normalized or "NEU" in normalized:
        return "NEUTRAL"
    return "POSITIVE"


def analyze_review_sentiment(text: str) -> Tuple[str, Optional[float]]:
    pipeline = _load_sentiment_pipeline()
    if pipeline is None:
        return "NEUTRAL", None

    try:
        payload = pipeline(text or "")
        if isinstance(payload, list) and payload:
            payload = payload[0]
        if isinstance(payload, dict):
            label = _normalize_sentiment_label(str(payload.get("label", "")))
            score = payload.get("score")
            return label, float(score) if score is not None else None
    except Exception:
        pass

    return "NEUTRAL", None
