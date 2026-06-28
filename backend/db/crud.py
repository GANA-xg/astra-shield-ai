from sqlalchemy import func
from sqlalchemy.orm import Session

from .models import Detection


def save_detection(
    db: Session,
    scan_type: str,
    input_text: str,
    risk_score: int,
    risk_level: str,
    recommendation: str,
    ml_probability: float | None,
    signals: list,
):
    detection = Detection(
        scan_type=scan_type,
        input_text=input_text,
        risk_score=risk_score,
        risk_level=risk_level,
        recommendation=recommendation,
        ml_probability=ml_probability,
        signals=signals,
    )

    db.add(detection)
    db.commit()
    db.refresh(detection)

    return detection


def get_detection_history(db: Session, limit: int = 50):
    return (
        db.query(Detection)
        .order_by(Detection.created_at.desc())
        .limit(limit)
        .all()
    )


def get_detection_stats(db: Session):
    total = db.query(Detection).count()

    by_scan_type = {
        scan_type: count
        for scan_type, count in (
            db.query(Detection.scan_type, func.count(Detection.id))
            .group_by(Detection.scan_type)
            .all()
        )
    }

    by_risk_level = {
        risk: count
        for risk, count in (
            db.query(Detection.risk_level, func.count(Detection.id))
            .group_by(Detection.risk_level)
            .all()
        )
    }

    return {
        "total_scans": total,
        "scan_types": by_scan_type,
        "risk_levels": by_risk_level,
    }