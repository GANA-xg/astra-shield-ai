"""Risk scoring engine for fraud graph analysis.

Computes a numeric risk score (0-100) for an account based on graph
relationship signals: money-mule patterns, fraud ring membership,
device sharing, and transaction velocity.
"""

from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta


# --- Thresholds for risk signals ---
MONEY_MULE_SENDER_THRESHOLDS = {2: 10, 5: 25, 10: 40, 20: 55}
FRAUD_RING_SCORE = 30
SHARED_DEVICE_PER_PERSON_PENALTY = 12
VELOCITY_WINDOW_HOURS = 6
VELOCITY_THRESHOLDS = {3: 10, 5: 20, 10: 35, 20: 50}
LARGE_TX_COUNT_THRESHOLDS = {3: 8, 5: 15}
TOTAL_RISK_CAP = 100.0


def _score_money_mule(account_data: Dict[str, Any]) -> float:
    """Score based on number of distinct incoming senders.

    A money-mule account receives funds from many unrelated sources
    in a short period — the hallmark of mule activity.
    """
    senders = account_data.get("distinct_incoming_senders", 0)
    score = 0.0
    for threshold, pts in sorted(MONEY_MULE_SENDER_THRESHOLDS.items()):
        if senders >= threshold:
            score = pts
    return score


def _score_fraud_ring(account_data: Dict[str, Any]) -> float:
    """Score if the account is part of a detected fraud ring."""
    in_ring = account_data.get("in_fraud_ring", False)
    ring_size = account_data.get("fraud_ring_connections", 0)
    if in_ring:
        return min(FRAUD_RING_SCORE + ring_size * 3, 45.0)
    return 0.0


def _score_shared_device(account_data: Dict[str, Any]) -> float:
    """Score based on device shared with flagged accounts.

    If the same device is used by multiple accounts that are themselves
    flagged, the risk compounds.
    """
    flagged_sharers = account_data.get("flagged_device_sharers", 0)
    total_sharers = account_data.get("total_device_sharers", 0)
    if total_sharers <= 1:
        return 0.0
    score = flagged_sharers * SHARED_DEVICE_PER_PERSON_PENALTY
    # Also penalize if many people share a device at all (even unflagged)
    if total_sharers > 5:
        score += 8.0
    return min(score, 30.0)


def _score_transaction_velocity(account_data: Dict[str, Any]) -> float:
    """Score based on burst transaction patterns.

    Multiple transactions in a short time window suggest automated
    or coordinated draining of accounts.
    """
    velocity = account_data.get("transaction_velocity_6h", 0)
    score = 0.0
    for threshold, pts in sorted(VELOCITY_THRESHOLDS.items()):
        if velocity >= threshold:
            score = pts
    return score


def _score_large_tx_count(account_data: Dict[str, Any]) -> float:
    """Score if there are many large transactions (potential structuring)."""
    large_tx = account_data.get("large_transactions", 0)
    score = 0.0
    for threshold, pts in sorted(LARGE_TX_COUNT_THRESHOLDS.items()):
        if large_tx >= threshold:
            score = pts
    return score


def _score_transaction_amount_pattern(account_data: Dict[str, Any]) -> float:
    """Score unusual transaction amount patterns.

    E.g. all transactions at round numbers, or all just below reporting
    thresholds (structuring).
    """
    avg_amount = account_data.get("avg_transaction_amount", 0)
    round_ratio = account_data.get("round_amount_ratio", 0)

    score = 0.0
    # Many round-number transactions suggest structuring
    if round_ratio > 0.7 and avg_amount > 5000:
        score += 10.0
    # Very high average with many transactions
    if avg_amount > 100000:
        score += 8.0
    return min(score, 15.0)


def compute_risk_score(account_data: Dict[str, Any]) -> Dict[str, Any]:
    """Compute a risk score (0-100) and risk band for an account.

    Args:
        account_data: A dictionary of signals already fetched from Neo4j
            via graph queries. Expected keys:
            - distinct_incoming_senders (int)
            - in_fraud_ring (bool)
            - fraud_ring_connections (int)
            - flagged_device_sharers (int)
            - total_device_sharers (int)
            - transaction_velocity_6h (int)
            - large_transactions (int)
            - avg_transaction_amount (float)
            - round_amount_ratio (float)

    Returns:
        Dict with keys: score, risk, signals (list of contributing signals).
    """
    signals = []

    mule_score = _score_money_mule(account_data)
    if mule_score > 0:
        senders = account_data.get("distinct_incoming_senders", 0)
        signals.append({
            "signal": "money_mule_pattern",
            "score_contribution": mule_score,
            "detail": f"{senders} distinct incoming senders detected",
        })

    ring_score = _score_fraud_ring(account_data)
    if ring_score > 0:
        connections = account_data.get("fraud_ring_connections", 0)
        signals.append({
            "signal": "fraud_ring_membership",
            "score_contribution": ring_score,
            "detail": f"Account is part of a fraud ring with {connections} connections",
        })

    device_score = _score_shared_device(account_data)
    if device_score > 0:
        flagged = account_data.get("flagged_device_sharers", 0)
        total = account_data.get("total_device_sharers", 0)
        signals.append({
            "signal": "shared_device_with_flagged",
            "score_contribution": device_score,
            "detail": f"Device shared with {flagged} flagged accounts out of {total} total sharers",
        })

    velocity_score = _score_transaction_velocity(account_data)
    if velocity_score > 0:
        velocity = account_data.get("transaction_velocity_6h", 0)
        signals.append({
            "signal": "transaction_velocity_burst",
            "score_contribution": velocity_score,
            "detail": f"{velocity} transactions in last {VELOCITY_WINDOW_HOURS}h",
        })

    large_tx_score = _score_large_tx_count(account_data)
    if large_tx_score > 0:
        large = account_data.get("large_transactions", 0)
        signals.append({
            "signal": "large_transaction_count",
            "score_contribution": large_tx_score,
            "detail": f"{large} large transactions detected (potential structuring)",
        })

    amount_pattern_score = _score_transaction_amount_pattern(account_data)
    if amount_pattern_score > 0:
        signals.append({
            "signal": "unusual_amount_pattern",
            "score_contribution": amount_pattern_score,
            "detail": "Suspicious transaction amount pattern detected",
        })

    total_score = min(
        mule_score + ring_score + device_score + velocity_score + large_tx_score + amount_pattern_score,
        TOTAL_RISK_CAP,
    )

    if total_score > 85:
        risk = "CRITICAL"
    elif total_score > 60:
        risk = "HIGH"
    elif total_score > 30:
        risk = "MEDIUM"
    else:
        risk = "LOW"

    return {
        "score": round(total_score, 2),
        "risk": risk,
        "signals": signals,
    }
