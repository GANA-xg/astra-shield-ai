"""
Utility functions for the Scam Agent.
"""

from .keywords import SCAM_KEYWORDS


def extract_keywords(transcript: str):
    """
    Returns scam keywords found in the transcript.
    """

    transcript = transcript.lower()

    found = []

    for keyword in SCAM_KEYWORDS:
        if keyword.lower() in transcript:
            found.append(keyword)

    return found