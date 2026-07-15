"""
Scam-related keywords used for initial rule-based detection.
"""

SCAM_KEYWORDS = [
    # Banking
    "otp",
    "one time password",
    "bank account",
    "account blocked",
    "account suspended",
    "kyc",
    "verify your account",
    "update kyc",
    "debit card",
    "credit card",
    "cvv",
    "atm card",
    "net banking",

    # Payments
    "upi",
    "google pay",
    "phonepe",
    "paytm",
    "payment link",
    "refund",
    "cashback",

    # Urgency
    "urgent",
    "immediately",
    "right now",
    "within 10 minutes",
    "limited time",
    "last warning",
    "final notice",

    # Government / Police
    "aadhaar",
    "pan card",
    "income tax",
    "police",
    "cyber crime",
    "court notice",

    # Remote Access
    "anydesk",
    "teamviewer",
    "screen share",
    "install app",
    "download app",

    # Financial Fraud
    "lottery",
    "prize",
    "reward",
    "gift",
    "investment",
    "crypto",
    "bitcoin",

    # Threats
    "your account will be closed",
    "your sim will be blocked",
    "legal action",
    "arrest warrant",
    "fine",

    # Credentials
    "password",
    "pin",
    "security code",
    "verification code"
]