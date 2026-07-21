"""
Safety tips database for the Citizen Safety Advisor.

Each category has structured tips for keyword-based fallback responses.
"""

SAFETY_TIPS = {
    "OTP Fraud": {
        "risk_level": "HIGH",
        "advice": [
            "Never share your OTP with anyone — banks and service providers never ask for it.",
            "If you receive an OTP you didn't request, someone is trying to access your account.",
            "OTP scams often come as fake bank calls or SMS asking you to 'verify' your account.",
        ],
        "recommended_actions": [
            "If you shared an OTP, immediately call your bank's fraud helpline.",
            "Change your banking passwords right away.",
            "Enable transaction alerts on your bank account.",
            "File a complaint at cybercrime.gov.in or call 1930.",
        ],
    },
    "UPI Scam": {
        "risk_level": "HIGH",
        "advice": [
            "Never share your UPI PIN — receiving money does NOT require entering a PIN.",
            "Fake payment requests can look like real ones. Always verify in your bank app.",
            "QR code scams trick you into paying instead of receiving money.",
        ],
        "recommended_actions": [
            "Check your UPI transaction history for unauthorized payments.",
            "Block your UPI ID temporarily if compromised.",
            "Report to your bank and file a cybercrime complaint.",
        ],
    },
    "KYC Scam": {
        "risk_level": "HIGH",
        "advice": [
            "Banks never ask for KYC updates via SMS links or phone calls asking for card details.",
            "KYC scam messages create urgency — 'update KYC or account will be blocked'.",
            "Never download apps or share card numbers for KYC verification.",
        ],
        "recommended_actions": [
            "Visit your bank branch in person for any KYC updates.",
            "Do not click on any KYC update links in SMS or WhatsApp.",
            "Report the scam message to 1930.",
        ],
    },
    "Banking Scam": {
        "risk_level": "HIGH",
        "advice": [
            "Fake bank calls often spoof official numbers. Verify by calling the number on your bank card.",
            "Never share net banking credentials, card numbers, or CVV over phone or email.",
            "Bank employees will never ask you to transfer money to a 'safe account'.",
        ],
        "recommended_actions": [
            "Call your bank's official helpline immediately.",
            "Freeze your card if details were shared.",
            "File a complaint at cybercrime.gov.in.",
        ],
    },
    "Phishing Attack": {
        "risk_level": "HIGH",
        "advice": [
            "Check the sender's email address carefully — fake domains often have slight misspellings.",
            "Never click on links in unsolicited emails asking you to 'verify' or 'update' your account.",
            "Look for HTTPS and the correct domain before entering any credentials.",
        ],
        "recommended_actions": [
            "Report phishing emails to your email provider.",
            "If you clicked a link, change your passwords immediately.",
            "Report to cybercrime.gov.in.",
        ],
    },
    "QR Code Scam": {
        "risk_level": "MEDIUM",
        "advice": [
            "QR codes can initiate payments — never scan codes from strangers.",
            "A QR code is for receiving payment, not sending. If someone asks you to scan to receive money, it's a scam.",
            "Verify QR payment amounts before confirming.",
        ],
        "recommended_actions": [
            "Check your bank/UPI app for any unauthorized transactions.",
            "Report suspicious QR code attempts.",
        ],
    },
    "Job Scam": {
        "risk_level": "MEDIUM",
        "advice": [
            "Legitimate companies never ask for money upfront for job applications.",
            "Fake job offers often promise unusually high salaries for minimal work.",
            "Verify company details independently before sharing personal information.",
        ],
        "recommended_actions": [
            "Report fake job postings to the platform.",
            "Do not pay any registration or processing fees.",
            "Verify the company on MCA (Ministry of Corporate Affairs) website.",
        ],
    },
    "Investment Scam": {
        "risk_level": "HIGH",
        "advice": [
            "Guaranteed high returns are always a scam — legitimate investments carry risk.",
            "Ponzi schemes recruit through social media and messaging apps.",
            "Never invest based on tips from unknown people on Telegram or WhatsApp groups.",
        ],
        "recommended_actions": [
            "Stop all communication with the scammer immediately.",
            "Report to SEBI if it involves securities, or to local police.",
            "File a complaint at cybercrime.gov.in.",
        ],
    },
    "Lottery Scam": {
        "risk_level": "MEDIUM",
        "advice": [
            "You cannot win a lottery you never entered — this is always a scam.",
            "Legitimate lotteries never ask for upfront fees to release winnings.",
            "Scammers create fake prize notifications to steal personal information.",
        ],
        "recommended_actions": [
            "Do not respond or pay any fees.",
            "Block the sender.",
            "Report the scam to 1930.",
        ],
    },
    "Parcel Scam": {
        "risk_level": "MEDIUM",
        "advice": [
            "Fake courier messages claim a package is held at customs and needs payment.",
            "Legitimate courier companies do not ask for payment via UPI links from unknown numbers.",
            "Track packages only through official courier websites.",
        ],
        "recommended_actions": [
            "Do not click any payment links in parcel messages.",
            "Contact the courier company directly using their official website.",
            "Report the scam message.",
        ],
    },
    "Remote Access Scam": {
        "risk_level": "CRITICAL",
        "advice": [
            "Never allow remote access to your device to someone who called you unsolicited.",
            "Tech support scams claim your computer is infected and ask for remote access.",
            "Legitimate companies do not call you about computer problems.",
        ],
        "recommended_actions": [
            "If you granted access, disconnect from the internet immediately.",
            "Run a full antivirus scan.",
            "Change all passwords from a different device.",
            "Report to cybercrime.gov.in and call 1930.",
        ],
    },
    "General Cyber Safety": {
        "risk_level": "LOW",
        "advice": [
            "Use strong, unique passwords for each online account.",
            "Enable two-factor authentication wherever possible.",
            "Keep your devices and apps updated.",
            "Be skeptical of unsolicited messages asking for personal information.",
        ],
        "recommended_actions": [
            "Review your privacy settings on social media.",
            "Install a reputable antivirus app on your phone and computer.",
            "Save the Cyber Crime Helpline number: 1930.",
        ],
    },
}


def get_safety_tips(category: str) -> dict:
    """
    Get safety tips for a given category.

    Args:
        category: The scam/fraud category.

    Returns:
        dict with advice, risk_level, and recommended_actions.
    """
    return SAFETY_TIPS.get(category, SAFETY_TIPS["General Cyber Safety"])
