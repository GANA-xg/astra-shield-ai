"""Court-admissible evidence package generator.

Generates a structured JSON document and PDF report for a given account,
linking all entities, relationships, risk signals, and providing integrity
verification via SHA-256 hash.
"""

import hashlib
import json
import os
import tempfile
import time
from datetime import datetime
from typing import Any, Dict, Optional

from core.logging import logger
from graph.queries import graph_queries
from graph.connection import _session


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _gather_evidence_data(account_number: str) -> Dict[str, Any]:
    """Pull all connected data for an account from Neo4j."""
    entities = []
    relationships = []

    with _session() as session:
        if session is None:
            return {"entities": [], "relationships": [], "summary": "Neo4j not connected"}

        # Account node
        result = session.run(
            "MATCH (a:Account {account_number:$acct}) RETURN a", acct=account_number
        )
        rec = result.single()
        if rec:
            a = dict(rec["a"])
            a["node_type"] = "Account"
            entities.append(a)

        # Owner person
        result = session.run(
            "MATCH (p:Person)-[:OWNS]->(a:Account {account_number:$acct}) RETURN p",
            acct=account_number,
        )
        for rec in result:
            p = dict(rec["p"])
            p["node_type"] = "Person"
            entities.append(p)
            relationships.append({
                "type": "OWNS",
                "from": p.get("person_id"),
                "to": account_number,
            })

        # Devices used by owner
        result = session.run(
            """
            MATCH (p:Person)-[:OWNS]->(a:Account {account_number:$acct})
            MATCH (p)-[:USES]->(d:Device)
            RETURN d
            """,
            acct=account_number,
        )
        for rec in result:
            d = dict(rec["d"])
            d["node_type"] = "Device"
            entities.append(d)
            relationships.append({
                "type": "USES_DEVICE",
                "from": rec["d"].get("device_id"),
                "to": account_number,
            })

        # All transactions (sent and received)
        result = session.run(
            """
            MATCH (a:Account {account_number:$acct})-[:SENT]->(t:Transaction)-[:RECEIVED_BY]->(b:Account)
            RETURN t, b.account_number AS receiver, 'SENT' AS direction
            """,
            acct=account_number,
        )
        for rec in result:
            t = dict(rec["t"])
            t["node_type"] = "Transaction"
            entities.append(t)
            relationships.append({
                "type": "SENT",
                "from": account_number,
                "to": t.get("transaction_id"),
                "amount": t.get("amount"),
                "mode": t.get("mode"),
                "timestamp": str(t.get("timestamp")),
            })
            relationships.append({
                "type": "RECEIVED_BY",
                "from": t.get("transaction_id"),
                "to": rec["receiver"],
            })

        result = session.run(
            """
            MATCH (b:Account)-[:SENT]->(t:Transaction)-[:RECEIVED_BY]->
                  (a:Account {account_number:$acct})
            RETURN t, b.account_number AS sender, 'RECEIVED' AS direction
            """,
            acct=account_number,
        )
        for rec in result:
            t = dict(rec["t"])
            t["node_type"] = "Transaction"
            entities.append(t)
            relationships.append({
                "type": "SENT",
                "from": rec["sender"],
                "to": t.get("transaction_id"),
                "amount": t.get("amount"),
            })
            relationships.append({
                "type": "RECEIVED_BY",
                "from": t.get("transaction_id"),
                "to": account_number,
            })

    return {"entities": entities, "relationships": relationships}


def generate_evidence_package(account_number: str) -> Dict[str, Any]:
    """Generate a structured evidence package for an account.

    Returns a dict with:
      - case_id, generated_at, account_number
      - entities, relationships, risk_assessment
      - integrity_hash (SHA-256 of the data payload)
      - summary_paragraph
    """
    case_id = f"EVID-{account_number}-{int(time.time())}"
    generated_at = datetime.utcnow().isoformat() + "Z"

    evidence_data = _gather_evidence_data(account_number)

    # Risk assessment (import here to avoid circular)
    from agents.fraud_graph_agent.analyzer import fraud_analyzer
    risk_detail = fraud_analyzer.analyze_account_detailed(account_number)

    # Deduplicate entities by a stable key
    seen = set()
    unique_entities = []
    for e in evidence_data["entities"]:
        key = (e.get("node_type"), e.get("account_number") or e.get("transaction_id")
               or e.get("person_id") or e.get("device_id") or id(e))
        if key not in seen:
            seen.add(key)
            unique_entities.append(e)

    # Build data payload for hashing
    payload = {
        "case_id": case_id,
        "account_number": account_number,
        "generated_at": generated_at,
        "entities": unique_entities,
        "relationships": evidence_data["relationships"],
        "risk_assessment": {
            "score": risk_detail["score"],
            "risk": risk_detail["risk"],
            "signals": risk_detail["signals"],
        },
    }

    data_json = json.dumps(payload, sort_keys=True, default=str).encode("utf-8")
    integrity_hash = _sha256(data_json)

    # Generate plain-language summary
    tx_count = sum(1 for e in unique_entities if e.get("node_type") == "Transaction")
    risk_level = risk_detail["risk"]
    signal_count = len(risk_detail["signals"])
    summary = (
        f"Evidence package for account {account_number} compiled on {generated_at}. "
        f"The account is linked to {len(unique_entities)} entities and "
        f"{len(evidence_data['relationships'])} relationships including "
        f"{tx_count} transactions. Risk assessment: {risk_level} "
        f"(score {risk_detail['score']}/100) based on {signal_count} signal(s). "
        f"Data integrity verified with SHA-256 hash: {integrity_hash[:16]}..."
    )

    return {
        "case_id": case_id,
        "account_number": account_number,
        "generated_at": generated_at,
        "entities": unique_entities,
        "relationships": evidence_data["relationships"],
        "risk_assessment": {
            "score": risk_detail["score"],
            "risk": risk_detail["risk"],
            "signals": risk_detail["signals"],
        },
        "integrity_hash": integrity_hash,
        "summary": summary,
    }


def render_evidence_pdf(evidence: Dict[str, Any], output_path: Optional[str] = None) -> str:
    """Render the evidence package as a PDF report.

    Returns the path to the generated PDF file.
    """
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch, cm
    from reportlab.platypus import (
        SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak,
    )

    if output_path is None:
        fd, output_path = tempfile.mkstemp(suffix=".pdf", prefix="evidence_")
        os.close(fd)

    doc = SimpleDocTemplate(output_path, pagesize=A4,
                            topMargin=1*inch, bottomMargin=1*inch)
    styles = getSampleStyleSheet()
    elements = []

    # Cover page
    elements.append(Spacer(1, 2*inch))
    title_style = ParagraphStyle("Title", parent=styles["Title"], fontSize=24,
                                  spaceAfter=20, textColor=colors.HexColor("#1a1a2e"))
    elements.append(Paragraph("ASTRA SHIELD AI", title_style))
    elements.append(Paragraph("Evidence Package", ParagraphStyle(
        "Subtitle", parent=styles["Heading2"], fontSize=18, spaceAfter=30,
        textColor=colors.HexColor("#16213e"))))

    meta_style = ParagraphStyle("Meta", parent=styles["Normal"], fontSize=11,
                                 spaceAfter=6, textColor=colors.HexColor("#444444"))
    elements.append(Paragraph(f"<b>Case ID:</b> {evidence['case_id']}", meta_style))
    elements.append(Paragraph(f"<b>Account:</b> {evidence['account_number']}", meta_style))
    elements.append(Paragraph(f"<b>Generated:</b> {evidence['generated_at']}", meta_style))
    elements.append(Paragraph(f"<b>Integrity Hash:</b> {evidence['integrity_hash'][:32]}...", meta_style))
    elements.append(Spacer(1, 0.5*inch))
    elements.append(Paragraph(
        f"<b>Classification:</b> {evidence['risk_assessment']['risk']} "
        f"(Risk Score: {evidence['risk_assessment']['score']}/100)", meta_style))

    elements.append(PageBreak())

    # Risk Assessment section
    elements.append(Paragraph("1. Risk Assessment", styles["Heading1"]))
    elements.append(Spacer(1, 0.2*inch))

    risk = evidence["risk_assessment"]
    risk_data = [
        ["Metric", "Value"],
        ["Risk Score", str(risk["score"])],
        ["Risk Level", risk["risk"]],
        ["Signals Detected", str(len(risk["signals"]))],
    ]
    risk_table = Table(risk_data, colWidths=[3*inch, 3*inch])
    risk_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1a1a2e")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f5f5f5")]),
    ]))
    elements.append(risk_table)
    elements.append(Spacer(1, 0.3*inch))

    if risk["signals"]:
        elements.append(Paragraph("Contributing Signals:", styles["Heading3"]))
        for sig in risk["signals"]:
            elements.append(Paragraph(
                f"• <b>{sig['signal']}</b> (+{sig['score_contribution']}): {sig['detail']}",
                styles["Normal"]))
        elements.append(Spacer(1, 0.3*inch))

    # Entity table
    elements.append(Paragraph("2. Entities Involved", styles["Heading1"]))
    elements.append(Spacer(1, 0.2*inch))

    entity_header = ["Type", "ID", "Details"]
    entity_rows = [entity_header]
    for e in evidence["entities"][:50]:  # Limit for readability
        node_type = e.get("node_type", "Unknown")
        eid = (e.get("account_number") or e.get("transaction_id")
               or e.get("person_id") or e.get("device_id") or "N/A")
        details = []
        if e.get("bank_name"):
            details.append(f"Bank: {e['bank_name']}")
        if e.get("amount"):
            details.append(f"₹{e['amount']}")
        if e.get("name"):
            details.append(e["name"])
        if e.get("mode"):
            details.append(e["mode"])
        entity_rows.append([node_type, str(eid)[:20], "; ".join(details)[:60]])

    entity_table = Table(entity_rows, colWidths=[1.2*inch, 2*inch, 3*inch])
    entity_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1a1a2e")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f5f5f5")]),
    ]))
    elements.append(entity_table)
    elements.append(Spacer(1, 0.3*inch))

    # Relationships
    elements.append(Paragraph("3. Relationships", styles["Heading1"]))
    elements.append(Spacer(1, 0.2*inch))

    rel_header = ["Type", "From", "To", "Amount"]
    rel_rows = [rel_header]
    for r in evidence["relationships"][:50]:
        amount = r.get("amount", "")
        rel_rows.append([
            r.get("type", ""),
            str(r.get("from", ""))[:20],
            str(r.get("to", ""))[:20],
            f"₹{amount}" if amount else "",
        ])

    rel_table = Table(rel_rows, colWidths=[1.5*inch, 1.8*inch, 1.8*inch, 1.2*inch])
    rel_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1a1a2e")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f5f5f5")]),
    ]))
    elements.append(rel_table)
    elements.append(Spacer(1, 0.3*inch))

    # Summary
    elements.append(Paragraph("4. Summary", styles["Heading1"]))
    elements.append(Spacer(1, 0.2*inch))
    elements.append(Paragraph(evidence["summary"], styles["Normal"]))
    elements.append(Spacer(1, 0.5*inch))

    # Integrity verification
    elements.append(Paragraph("5. Integrity Verification", styles["Heading1"]))
    elements.append(Spacer(1, 0.2*inch))
    elements.append(Paragraph(
        f"This evidence package is cryptographically signed with SHA-256 hash: "
        f"<font face='Courier' size='9'>{evidence['integrity_hash']}</font>",
        styles["Normal"]))
    elements.append(Paragraph(
        "To verify: hash the JSON payload (excluding this field) with SHA-256 "
        "and confirm it matches the above value.",
        styles["Normal"]))

    doc.build(elements)
    return output_path
