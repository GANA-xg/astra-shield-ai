from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import Float
from sqlalchemy import Integer
from sqlalchemy import JSON
from sqlalchemy import String
from sqlalchemy.sql import func

from .database import Base


class Detection(Base):
    __tablename__ = "detections"

    id = Column(Integer, primary_key=True, index=True)

    scan_type = Column(
        String(20),
        nullable=False,
    )

    input_text = Column(
        String,
        nullable=False,
    )

    risk_score = Column(
        Integer,
        nullable=False,
    )

    risk_level = Column(
        String(20),
        nullable=False,
    )

    recommendation = Column(
        String,
        nullable=False,
    )

    ml_probability = Column(
        Float,
        nullable=True,
    )

    signals = Column(
        JSON,
        nullable=True,
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )


class EvidenceLog(Base):
    __tablename__ = "evidence_logs"

    id = Column(Integer, primary_key=True, index=True)

    case_id = Column(
        String(100),
        nullable=False,
        unique=True,
    )

    account_number = Column(
        String(50),
        nullable=False,
    )

    risk_score = Column(
        Float,
        nullable=False,
    )

    risk_level = Column(
        String(20),
        nullable=False,
    )

    integrity_hash = Column(
        String(64),
        nullable=False,
    )

    entity_count = Column(
        Integer,
        nullable=False,
    )

    relationship_count = Column(
        Integer,
        nullable=False,
    )

    requested_by = Column(
        String(100),
        nullable=True,
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )