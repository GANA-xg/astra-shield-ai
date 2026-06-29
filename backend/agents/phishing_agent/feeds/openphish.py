import os
import requests

CACHE_DIR = os.path.join(
    os.path.dirname(__file__),
    "cache",
)

CACHE_FILE = os.path.join(
    CACHE_DIR,
    "openphish.txt",
)

OPENPHISH_FEED = "https://openphish.com/feed.txt"


def download_feed():
    """
    Downloads the latest OpenPhish community feed.
    """

    os.makedirs(CACHE_DIR, exist_ok=True)

    response = requests.get(
        OPENPHISH_FEED,
        timeout=30,
    )

    response.raise_for_status()

    with open(CACHE_FILE, "w") as f:
        f.write(response.text)

    print("OpenPhish feed updated.")


def load_feed():
    """
    Loads cached URLs into memory.
    """

    if not os.path.exists(CACHE_FILE):
        return set()

    with open(CACHE_FILE) as f:
        return set(
            line.strip()
            for line in f
            if line.strip()
        )


def is_blacklisted(url: str) -> bool:
    """
    Checks whether URL exists in cached feed.
    """

    urls = load_feed()

    return url in urls