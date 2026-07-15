"""
blacklist_checker.py

Checks a URL against multiple phishing intelligence sources.

Current Status:
- Google Safe Browsing: Implemented (via safe_browsing.py)
- PhishTank: Placeholder
- OpenPhish: Implemented (via cached feed)
- URLhaus: Placeholder
"""

from .safe_browsing import check_google_safe_browsing
import os
from urllib.parse import urlparse


def check_phishtank(url: str) -> bool:
    """
    Check URL against PhishTank.

    Placeholder implementation.
    Replace with API integration later.
    """
    try:
        return False
    except Exception:
        return False


def check_openphish(url: str) -> bool:
    """
    Check URL against OpenPhish.

    Loads the cached openphish.txt feed and checks if the URL
    matches any entry by exact string or by hostname.
    """
    try:
        # Parse the input URL
        parsed_input = urlparse(url)
        input_hostname = None
        if parsed_input.hostname:
            input_hostname = parsed_input.hostname.lower()

        # Build the path to the feed file
        base_dir = os.path.dirname(__file__)
        feed_path = os.path.join(base_dir, 'feeds', 'cache', 'openphish.txt')

        # Read the feed file
        with open(feed_path, 'r') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue

                # Exact match
                if line == url:
                    return True

                # Hostname match
                if input_hostname:
                    try:
                        parsed_line = urlparse(line)
                        if parsed_line.hostname:
                            line_hostname = parsed_line.hostname.lower()
                            if line_hostname == input_hostname:
                                return True
                    except Exception:
                        # If the line is not a valid URL, skip for hostname matching
                        pass
    except FileNotFoundError:
        # If the file is not found, we fail safe (return False)
        return False
    except Exception:
        # For any other error, fail safe
        return False

    return False


def check_urlhaus(url: str) -> bool:
    """
    Check URL against URLhaus.

    Placeholder implementation.
    Replace with API integration later.
    """
    try:
        return False
    except Exception:
        return False


def check_blacklists(url: str, safe_browsing_result: dict | None = None) -> dict:
    """
    Run all blacklist checks and return a unified result.

    Returns:
    {
        "google_safe_browsing": bool,
        "phishtank": bool,
        "openphish": bool,
        "urlhaus": bool
    }
    """

    if safe_browsing_result is None:
        safe_browsing_result = check_google_safe_browsing(url)

    return {
        "google_safe_browsing": safe_browsing_result.get("malicious", False),
        "phishtank": check_phishtank(url),
        "openphish": check_openphish(url),
        "urlhaus": check_urlhaus(url),
    }