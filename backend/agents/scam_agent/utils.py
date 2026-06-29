"""
Utility functions for the Scam Agent.
"""

from .keywords import SCAM_KEYWORDS


def extract_keywords(transcript: str) -> list[str]:
    """
    Extract scam-related keywords from the transcript.
    """

    transcript = transcript.lower()

    found = []

    for keyword in SCAM_KEYWORDS:
        if keyword.lower() in transcript and keyword not in found:
            found.append(keyword)

    return found