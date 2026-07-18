import traceback

from graph.connection import _session
from graph.queries import graph_queries
from core.logging import logger


class FraudGraphService:

    def build_graph(self, search_term: str) -> dict:
        try:
            s = _session()
            if s is None:
                return self._empty_graph("Neo4j is not connected")

            nodes = []
            edges = []

            with s:
                result = s.run(
                    """
                    MATCH (p:Person)
                    WHERE p.phone CONTAINS $search OR p.person_id CONTAINS $search
                    OPTIONAL MATCH (p)-[:OWNS]->(a:Account)
                    OPTIONAL MATCH (p)-[:USES]->(dev:Device)
                    OPTIONAL MATCH (a)-[:SENT]->(t:Transaction)-[:RECEIVED_BY]->(target:Account)
                    RETURN p, a, dev, t, target
                    """,
                    search=search_term,
                )

                seen_ids = set()

                for record in result:
                    person = record.get("p")
                    account = record.get("a")
                    device = record.get("dev")
                    transaction = record.get("t")
                    target = record.get("target")

                    if person:
                        pid = person.get("person_id", search_term)
                        if pid not in seen_ids:
                            seen_ids.add(pid)
                            nodes.append({
                                "id": pid,
                                "type": "phone",
                                "value": person.get("phone", pid),
                                "risk": "medium",
                            })

                    if account:
                        aid = account.get("account_number", "")
                        if aid not in seen_ids:
                            seen_ids.add(aid)
                            nodes.append({
                                "id": aid,
                                "type": "account",
                                "value": aid,
                                "risk": "low",
                            })

                    if device:
                        did = device.get("device_id", "")
                        if did not in seen_ids:
                            seen_ids.add(did)
                            nodes.append({
                                "id": did,
                                "type": "account",
                                "value": device.get("device_type", "Device"),
                                "risk": "medium",
                            })

                    if target:
                        tid = target.get("account_number", "")
                        if tid not in seen_ids:
                            seen_ids.add(tid)
                            nodes.append({
                                "id": tid,
                                "type": "account",
                                "value": tid,
                                "risk": "high",
                            })

                    if person and account:
                        edges.append({
                            "from": person.get("person_id", search_term),
                            "to": account.get("account_number", ""),
                            "relation": "owns",
                        })

                    if person and device:
                        edges.append({
                            "from": person.get("person_id", search_term),
                            "to": device.get("device_id", ""),
                            "relation": "uses",
                        })

                    if account and transaction and target:
                        edges.append({
                            "from": account.get("account_number", ""),
                            "to": target.get("account_number", ""),
                            "relation": f"sends {transaction.get('amount', 'unknown')} {transaction.get('mode', '')}",
                        })

            if not nodes:
                return self._empty_graph(
                    f"No fraud network data found for '{search_term}'. Try a phone number like '+919900000001'."
                )

            return {
                "nodes": nodes,
                "edges": edges,
                "summary": f"Found {len(nodes)} entity(s) with {len(edges)} connection(s) related to '{search_term}'.",
            }

        except Exception as e:
            logger.error("build_graph error: %s\n%s", e, traceback.format_exc())
            return self._empty_graph(f"Query failed: {str(e)}")

    def _empty_graph(self, summary: str) -> dict:
        return {"nodes": [], "edges": [], "summary": summary}

    def get_money_mules(self):
        return graph_queries.find_money_mules()

    def get_people_using_device(self, device_id: str):
        return graph_queries.find_people_using_device(device_id)

    def trace_money_flow(self, account_number: str, depth: int = 5):
        return graph_queries.trace_money_flow(account_number, depth)

    def get_shortest_path(self, source_account: str, target_account: str):
        return graph_queries.shortest_path(source_account, target_account)

    def get_fraud_rings(self, minimum_connections: int = 2):
        return graph_queries.detect_fraud_rings(minimum_connections)


fraud_graph_service = FraudGraphService()
