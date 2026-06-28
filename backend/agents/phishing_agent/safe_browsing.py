import os
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("GOOGLE_SAFE_BROWSING_API_KEY")

API_URL = (
    "https://safebrowsing.googleapis.com/v4/threatMatches:find"
)


def check_google_safe_browsing(url: str) -> dict:
    """
    Check a URL against Google Safe Browsing.

    Returns:
        {
            "malicious": bool,
            "threat_type": str | None,
            "platform_type": str | None,
            "threat_entry_type": str | None
        }
    """

    if not API_KEY:
        return {
            "malicious": False,
            "error": "Google Safe Browsing API key not configured"
        }

    payload = {
        "client": {
            "clientId": "astra-shield",
            "clientVersion": "1.0"
        },
        "threatInfo": {
            "threatTypes": [
                "MALWARE",
                "SOCIAL_ENGINEERING",
                "UNWANTED_SOFTWARE",
                "POTENTIALLY_HARMFUL_APPLICATION"
            ],
            "platformTypes": [
                "ANY_PLATFORM"
            ],
            "threatEntryTypes": [
                "URL"
            ],
            "threatEntries": [
                {
                    "url": url
                }
            ]
        }
    }

    try:

        response = requests.post(
            f"{API_URL}?key={API_KEY}",
            json=payload,
            timeout=10
        )

        response.raise_for_status()

        result = response.json()

        matches = result.get("matches", [])

        if not matches:
            return {
                "malicious": False
            }

        match = matches[0]

        return {
            "malicious": True,
            "threat_type": match.get("threatType"),
            "platform_type": match.get("platformType"),
            "threat_entry_type": match.get("threatEntryType")
        }

    except requests.RequestException as e:

        return {
            "malicious": False,
            "error": str(e)
        }