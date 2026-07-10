from .safety_categories import SAFETY_CATEGORIES

def classify_query(query: str):
    query = query.lower()

    for keyword, category in SAFETY_CATEGORIES.items():
        if keyword in query:
            return category

    return "General Cyber Safety"