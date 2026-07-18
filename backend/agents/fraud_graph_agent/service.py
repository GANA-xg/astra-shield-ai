from graph.queries import graph_queries


class FraudGraphService:

    def get_money_mules(self):
        return graph_queries.find_money_mules()
    def get_people_using_device(self, device_id: str):
        return graph_queries.find_people_using_device(device_id)
    
    def trace_money_flow(self, account_number: str, depth: int = 5):
        return graph_queries.trace_money_flow(account_number, depth)
    def get_shortest_path(
        self,
        source_account: str,
        target_account: str,
    ):
        return graph_queries.shortest_path(
            source_account,
            target_account,
        )
    
    def get_fraud_rings(
        self,
        minimum_connections: int = 2,
    ):
        return graph_queries.detect_fraud_rings(
            minimum_connections,
        )


fraud_graph_service = FraudGraphService()