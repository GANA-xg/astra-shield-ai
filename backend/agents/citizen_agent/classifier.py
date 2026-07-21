"""Classify citizen queries into scam/safety categories.

Uses Gemini for intelligent classification with keyword-based fallback
when the API is unavailable.
"""

import os
import json
from typing import Dict, Any

from .safety_categories import SAFETY_CATEGORIES
from .safety_tips import get_safety_tips

CLASSIFICATION_PROMPT = """You are a cybersecurity classification engine for Indian citizens.

Classify the following user query into exactly ONE of these categories:
{categories}

Also determine the risk level: LOW, MEDIUM, HIGH, or CRITICAL.

User query: "{query}"

Return ONLY valid JSON in this exact format:
{{
  "category": "<category name>",
  "risk_level": "<LOW|MEDIUM|HIGH|CRITICAL>",
  "confidence": "<high|medium|low>"
}}

Rules:
- Pick the SINGLE most relevant category
- If the query describes an active scam in progress, risk is HIGH or CRITICAL
- If the query is a general safety question, risk is LOW
- If the query mentions specific financial loss, risk is HIGH
"""


def _get_gemini_model():
    """Get Gemini model if API key is available."""
    api_key = os.environ.get("GOOGLE_GEMINI_API_KEY") or os.environ.get("GEMINI_API_KEY")
    if not api_key:
        return None
    try:
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        return genai.GenerativeModel("gemini-2.0-flash")
    except Exception:
        return None


def _keyword_classify(query: str) -> Dict[str, Any]:
    """Fast keyword-based classification when Gemini is unavailable."""
    query_lower = query.lower()

    for keyword, category in SAFETY_CATEGORIES.items():
        if keyword in query_lower:
            tips = get_safety_tips(category)
            return {
                "category": category,
                "risk_level": tips.get("risk_level", "MEDIUM"),
                "confidence": "medium",
            }

    tips = get_safety_tips("General Cyber Safety")
    return {
        "category": "General Cyber Safety",
        "risk_level": tips.get("risk_level", "LOW"),
        "confidence": "low",
    }


def classify_query(query: str) -> Dict[str, Any]:
    """Classify a citizen query using Gemini with keyword fallback.

    Args:
        query: The citizen's question or concern.

    Returns:
        Dict with category, risk_level, confidence.
    """
    model = _get_gemini_model()

    if model is None:
        return _keyword_classify(query)

    try:
        categories = "\n".join(f"- {cat}" for cat in SAFETY_CATEGORIES.values())
        prompt = CLASSIFICATION_PROMPT.format(
            categories=categories,
            query=query,
        )

        response = model.generate_content(
            prompt,
            generation_config={"temperature": 0.1, "max_output_tokens": 200},
        )

        text = response.text.strip()
        if text.startswith("```json"):
            text = text.replace("```json", "").replace("```", "").strip()
        elif text.startswith("```"):
            text = text.replace("```", "").strip()

        parsed = json.loads(text)

        return {
            "category": parsed.get("category", "General Cyber Safety"),
            "risk_level": parsed.get("risk_level", "MEDIUM"),
            "confidence": parsed.get("confidence", "medium"),
        }

    except Exception:
        return _keyword_classify(query)
