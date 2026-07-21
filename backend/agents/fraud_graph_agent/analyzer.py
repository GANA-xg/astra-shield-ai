"""Analyzer that orchestrates risk scoring across accounts.

Pulls graph data for an account (or all accounts), computes risk scores
via the risk engine, and returns structured RiskResponse objects.
"""

from typing import List

from agents.fraud_graph_agent.risk_engine import compute_risk_score
from agents.fraud_graph_agent.schemas import RiskResponse
from graph.queries import graph_queries
from graph.connection import _session
from core.logging import logger


class FraudAnalyzer:

    def _gather_account_signals(self, account_number: str) -> dict:
        """Fetch all risk signals for a single account from Neo4j."""
        signals = {
            "account_number": account_number,
            "distinct_incoming_senders": 0,
            "in_fraud_ring": False,
            "fraud_ring_connections": 0,
            "flagged_device_sharers": 0,
            "total_device_sharers": 0,
            "transaction_velocity_6h": 0,
            "large_transactions": 0,
            "avg_transaction_amount": 0.0,
            "round_amount_ratio": 0.0,
        }

        with _session() as session:
            if session is None:
                return signals

            # --- 1. Distinct incoming senders (money-mule signal) ---
            result = session.run(
                """
                MATCH (src:Account)-[:SENT]->(:Transaction)-[:RECEIVED_BY]->
                      (tgt:Account {account_number:$acct})
                RETURN COUNT(DISTINCT src) AS senders
                """,
                acct=account_number,
            )
            rec = result.single()
            if rec:
                signals["distinct_incoming_senders"] = rec["senders"]

            # --- 2. Fraud ring membership ---
            result = session.run(
                """
                MATCH (a:Account {account_number:$acct})-[:SENT]->(:Transaction)-[:RECEIVED_BY]->(b:Account)
                WITH a, collect(DISTINCT b.account_number) AS ring, COUNT(DISTINCT b) AS cnt
                WHERE cnt >= 2
                RETURN cnt AS ring_size
                """,
                acct=account_number,
            )
            rec = result.single()
            if rec and rec["ring_size"] is not None:
                signals["in_fraud_ring"] = True
                signals["fraud_ring_connections"] = rec["ring_size"]

            # --- 3. Device sharing ---
            result = session.run(
                """
                MATCH (a:Account {account_number:$acct})<-[:OWNS]-(p:Person)-[:USES]->(d:Device)
                MATCH (other:Person)-[:USES]->(d)
                WHERE other.person_id <> p.person_id
                OPTIONAL MATCH (other_flagged:Person)-[:USES]->(d)
                OPTIONAL MATCH (other_flagged)-[:OWNS]->(flagged_acct:Account)
                WHERE flagged_acct.account_number <> $acct
                WITH d, COLLECT(DISTINCT other.person_id) AS sharers,
                     COLLECT(DISTINCT other_flagged.person_id) AS all_sharers
                RETURN
                    SIZE(all_sharers) AS total_sharers,
                    SIZE(all_sharers) AS flagged_sharers
                LIMIT 1
                """,
                acct=account_number,
            )
            rec = result.single()
            if rec:
                signals["total_device_sharers"] = rec["total_sharers"]
                signals["flagged_device_sharers"] = rec["flagged_sharers"]

            # --- 4. Transaction velocity (last 6 hours) ---
            result = session.run(
                """
                MATCH (a:Account {account_number:$acct})-[:SENT]->(t:Transaction)
                WHERE t.timestamp >= datetime() - duration('PT6H')
                RETURN COUNT(t) AS tx_count
                """,
                acct=account_number,
            )
            rec = result.single()
            if rec:
                signals["transaction_velocity_6h"] = rec["tx_count"]

            # --- 5. Large transactions and amount patterns ---
            result = session.run(
                """
                MATCH (a:Account {account_number:$acct})-[:SENT]->(t:Transaction)
                RETURN
                    COUNT(t) AS total_tx,
                    COUNT(CASE WHEN t.amount > 50000 THEN 1 END) AS large_tx,
                    AVG(t.amount) AS avg_amount,
                    COUNT(CASE WHEN t.amount = toInteger(t.amount / 1000) * 1000
                               AND t.amount > 0 THEN 1 END) AS round_tx
                """,
                acct=account_number,
            )
            rec = result.single()
            if rec:
                total = rec["total_tx"] or 0
                signals["large_transactions"] = rec["large_tx"] or 0
                signals["avg_transaction_amount"] = float(rec["avg_amount"] or 0)
                round_tx = rec["round_tx"] or 0
                signals["round_amount_ratio"] = round_tx / max(total, 1)

        return signals

    def analyze_account(self, account_number: str) -> RiskResponse:
        """Compute risk score for a single account."""
        signals = self._gather_account_signals(account_number)
        result = compute_risk_score(signals)
        return RiskResponse(
            account_number=account_number,
            score=result["score"],
            risk=result["risk"],
        )

    def analyze_all_accounts(self) -> List[RiskResponse]:
        """Analyze all accounts in the graph."""
        results = []
        with _session() as session:
            if session is None:
                return results
            result = session.run("MATCH (a:Account) RETURN a.account_number AS acct")
            accounts = [record["acct"] for record in result]

        for acct in accounts:
            try:
                results.append(self.analyze_account(acct))
            except Exception as e:
                logger.warning("Failed to analyze account %s: %s", acct, e)
        return results

    def analyze_account_detailed(self, account_number: str) -> dict:
        """Return full risk breakdown including signal details."""
        signals = self._gather_account_signals(account_number)
        result = compute_risk_score(signals)
        return {
            "account_number": account_number,
            "score": result["score"],
            "risk": result["risk"],
            "signals": result["signals"],
            "raw_signals": signals,
        }


fraud_analyzer = FraudAnalyzer()
