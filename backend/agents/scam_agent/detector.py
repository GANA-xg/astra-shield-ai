import os
import json
from .schemas import ScamResponse
from dotenv import load_dotenv
import google.generativeai as genai

from .prompts import SYSTEM_PROMPT
from .utils import extract_keywords
from .call_pattern_analyzer import analyze_call_pattern

load_dotenv()

# Configure Gemini
genai.configure(api_key=os.getenv("GOOGLE_GEMINI_API_KEY"))

# Create the model
model = genai.GenerativeModel("gemini-2.5-flash")


def detect_scam(transcript: str, **call_metadata):
    """
    Analyze a phone call transcript for scam indicators.

    Runs both the LLM-based scam detection and the rule-based digital
    arrest pattern analyzer, then merges results.
    """

    keywords = extract_keywords(transcript)

    # --- Rule-based digital arrest analysis (always runs, no API needed) ---
    da_result = analyze_call_pattern(transcript, **call_metadata)

    # --- LLM-based general scam detection ---
    prompt = f"""
{SYSTEM_PROMPT}

Transcript:
{transcript}

Detected scam keywords:
{keywords}

Return ONLY valid JSON.
"""

    response = model.generate_content(prompt)

    # Gemini sometimes wraps JSON in ```json ... ```
    text = response.text.strip()

    if text.startswith("```json"):
        text = text.replace("```json", "").replace("```", "").strip()
    elif text.startswith("```"):
        text = text.replace("```", "").strip()

    parsed = json.loads(text)

    # Merge digital arrest signals into the response
    da_signals = [r["detail"] for r in da_result["matched_rules"]]

    return ScamResponse(
        is_scam=parsed.get("is_scam", False),
        risk_score=max(parsed.get("risk_score", 0), int(da_result["score"])),
        scam_type=parsed.get("scam_type", "Unknown"),
        confidence=parsed.get("confidence", "Low"),
        detected_keywords=parsed.get("detected_keywords", keywords),
        reason=parsed.get("reason", ""),
        recommendation=parsed.get("recommendation", []),
        is_digital_arrest_pattern=da_result["is_digital_arrest_pattern"],
        digital_arrest_confidence=min(da_result["score"] / 100.0, 1.0),
        digital_arrest_signals=da_signals,
    )
