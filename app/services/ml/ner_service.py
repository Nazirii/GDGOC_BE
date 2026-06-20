import importlib
import os
import re
from typing import Any, Dict, List, Optional

NER_MODEL_NAME = os.getenv("NER_MODEL_NAME", "distilbert-base-uncased")
_NER_PIPELINE = None


def _load_ner_pipeline():
    global _NER_PIPELINE
    if _NER_PIPELINE is not None:
        return _NER_PIPELINE

    try:
        transformers_module = importlib.import_module("transformers")
        pipeline = transformers_module.pipeline
        _NER_PIPELINE = pipeline(
            "token-classification",
            model=NER_MODEL_NAME,
            aggregation_strategy="simple",
        )
    except Exception:
        _NER_PIPELINE = None
    return _NER_PIPELINE


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


def extract_ner_entities(text: str) -> Dict[str, Optional[str]]:
    pipeline = _load_ner_pipeline()
    if pipeline is None:
        return {
            "entity_col": None,
            "entity_mrl": None,
            "entity_siz": None,
            "entity_use": None,
            "entity_feat": None,
        }

    try:
        entities = pipeline(text or "")
    except Exception:
        entities = []

    payload = {
        "entity_col": None,
        "entity_mrl": None,
        "entity_siz": None,
        "entity_use": None,
        "entity_feat": None,
    }

    for entity in entities or []:
        bucket = _pick_entity_bucket(str(entity.get("entity_group") or entity.get("entity") or ""), text)
        value = entity.get("word")
        if value and not payload[bucket]:
            payload[bucket] = re.sub(r"\s+", " ", str(value)).strip()

    return payload
