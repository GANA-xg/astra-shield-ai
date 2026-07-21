"""
Citizen Safety Advisor — AI-powered cybersecurity guidance agent.

Uses Gemini for intelligent responses with keyword-based fallback.
"""

import os
from .classifier import classify_query
from .safety_tips import get_safety_tips


CITIZEN_SYSTEM_PROMPT = """You are Astra Shield AI's Citizen Safety Advisor — an expert on Indian cybersecurity, digital fraud, and online safety.

Your role: Help citizens understand cyber threats, protect themselves from scams, and know what to do if they've been victimized.

Guidelines:
- Be clear, concise, and actionable. Citizens may not be technical.
- Always mention Indian-specific resources (Cyber Crime Portal: cybercrime.gov.in, helpline 1930, local cyber cell).
- If someone describes being scammed, prioritize: (1) immediate damage control, (2) reporting steps, (3) recovery.
- Never ask for personal information like bank details, OTPs, or passwords.
- For Digital Arrest Scams: explain the scam pattern, tell them to hang up, and report to 1930.
- For financial fraud: advise contacting bank immediately, filing cybercrime complaint.
- Use simple language. Avoid jargon.

Response format: Provide a direct answer, then actionable steps if relevant."""


def _get_gemini_client():
    """Get Gemini client if available."""
    api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        return None
    try:
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        return genai.GenerativeModel("gemini-2.0-flash")
    except Exception:
        return None


def _keyword_fallback(query: str) -> dict:
    """Fast keyword-based response when Gemini is unavailable."""
    classification = classify_query(query)
    category = classification["category"]
    tips = get_safety_tips(category)

    return {
        "response": tips.get("advice", ["Be cautious online."]),
        "category": category,
        "risk_level": classification.get("risk_level", tips.get("risk_level", "MEDIUM")),
        "source": "keyword_match",
        "recommended_actions": tips.get("recommended_actions", []),
    }


def get_citizen_advice(query: str, history: list = None) -> dict:
    """
    Get AI-powered cybersecurity advice for a citizen query.

    Args:
        query: The citizen's question or concern.
        history: Optional conversation history for context.

    Returns:
        dict with response, category, risk_level, source.
    """
    classification = classify_query(query)
    category = classification["category"]
    gemini = _get_gemini_client()

    if gemini is None:
        fallback = _keyword_fallback(query)
        fallback["ai_response"] = None
        return fallback

    try:
        context_parts = []
        if history:
            for msg in history[-6:]:
                role = msg.get("role", "user")
                content = msg.get("content", "")
                context_parts.append(f"{role}: {content}")

        prompt_parts = []
        if context_parts:
            prompt_parts.append("Previous conversation:\n" + "\n".join(context_parts))
        prompt_parts.append(f"Citizen question: {query}")
        prompt_parts.append(f"Detected category: {category}")
        prompt_parts.append(f"Risk level: {classification.get('risk_level', 'MEDIUM')}")
        prompt_parts.append("\nProvide helpful, actionable cybersecurity advice.")

        full_prompt = "\n\n".join(prompt_parts)
        response = gemini.generate_content(
            [CITIZEN_SYSTEM_PROMPT, full_prompt],
            generation_config={"temperature": 0.4, "max_output_tokens": 500},
        )

        ai_text = response.text

        return {
            "response": ai_text,
            "category": category,
            "risk_level": classification.get("risk_level", "MEDIUM"),
            "source": "ai",
            "recommended_actions": [],
        }

    except Exception as e:
        fallback = _keyword_fallback(query)
        fallback["ai_response"] = None
        fallback["ai_error"] = str(e)
        return fallback
