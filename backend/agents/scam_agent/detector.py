import os
import json

from dotenv import load_dotenv
import google.generativeai as genai

from .prompts import SYSTEM_PROMPT
from .utils import extract_keywords

load_dotenv()

# Configure Gemini
genai.configure(api_key=os.getenv("GOOGLE_GEMINI_API_KEY"))

# Create the model
model = genai.GenerativeModel("gemini-1.5-flash")


def detect_scam(transcript: str):
    """
    Analyze a phone call transcript for scam indicators.
    """

    keywords = extract_keywords(transcript)

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

    return json.loads(text)