from .openphish import download_feed


def refresh_feeds():
    print("Refreshing threat intelligence feeds...")

    try:
        download_feed()
    except Exception as e:
        print("OpenPhish:", e)

    print("Feed refresh complete.")