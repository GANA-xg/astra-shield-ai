from graph.connection import driver
from core.config import settings

class GraphQueries:

    # ==========================================================
    # PERSON
    # ==========================================================

    def find_person(self, person_id: str):
        query = """
        MATCH (p:Person {person_id:$person_id})
        RETURN p
        """

        with driver.session(
            database=settings.NEO4J_DATABASE
        ) as session:
            result = session.run(query, person_id=person_id)

            record = result.single()

            if not record:
                return None

            return dict(record["p"])

    # ==========================================================
    # ACCOUNT
    # ==========================================================

    def find_account(self, account_number: str):
        query = """
        MATCH (a:Account {account_number:$account_number})
        RETURN a
        """

        with driver.session(
            database=settings.NEO4J_DATABASE
        ) as session:
            result = session.run(
                query,
                account_number=account_number,
            )

            record = result.single()

            if not record:
                return None

            return dict(record["a"])

    # ==========================================================
    # DEVICE
    # ==========================================================

    def find_device(self, device_id: str):
        query = """
        MATCH (d:Device {device_id:$device_id})
        RETURN d
        """

        with driver.session(
            database=settings.NEO4J_DATABASE
        ) as session:
            result = session.run(
                query,
                device_id=device_id,
            )

            record = result.single()

            if not record:
                return None

            return dict(record["d"])

    # ==========================================================
    # TRANSACTION
    # ==========================================================

    def find_transaction(self, transaction_id: str):
        query = """
        MATCH (t:Transaction {transaction_id:$transaction_id})
        RETURN t
        """

        with driver.session(
            database=settings.NEO4J_DATABASE
        ) as session:
            result = session.run(
                query,
                transaction_id=transaction_id,
            )

            record = result.single()

            if not record:
                return None

            return dict(record["t"])

    # ==========================================================
    # ACCOUNT TRANSACTION HISTORY
    # ==========================================================

    def get_account_transactions(self, account_number: str):
        query = """
        MATCH (a:Account {account_number:$account_number})
        -[:SENT]->
        (t:Transaction)

        RETURN t
        """

        with driver.session(
            database=settings.NEO4J_DATABASE
        ) as session:
            result = session.run(
                query,
                account_number=account_number,
            )

            return [dict(record["t"]) for record in result]

    # ==========================================================
    # CONNECTED ACCOUNTS
    # ==========================================================

    def find_connected_accounts(self, account_number: str):
        query = """
        MATCH
        (a:Account {account_number:$account_number})
        -[:SENT]->
        (:Transaction)
        -[:RECEIVED_BY]->
        (other:Account)

        RETURN DISTINCT other
        """

        with driver.session(
            database=settings.NEO4J_DATABASE
        ) as session:
            result = session.run(
                query,
                account_number=account_number,
            )

            return [dict(record["other"]) for record in result]

    # ==========================================================
    # SHARED DEVICES
    # ==========================================================

    def find_people_using_device(self, device_id: str):
        query = """
        MATCH
        (p:Person)
        -[:USES]->
        (d:Device {device_id:$device_id})

        RETURN p
        """

        with driver.session(
            database=settings.NEO4J_DATABASE
        ) as session:
            result = session.run(
                query,
                device_id=device_id,
            )

            return [dict(record["p"]) for record in result]

    # ==========================================================
    # MONEY FLOW
    # ==========================================================

    def trace_money_flow(
        self,
        account_number: str,
        depth: int = 5,
    ):
        query = f"""
        MATCH path=
        (a:Account {{account_number:$account_number}})
        -[:SENT|RECEIVED_BY*1..{depth}]-
        (n)

        RETURN path
        """

        with driver.session(
            database=settings.NEO4J_DATABASE
        ) as session:
            result = session.run(
                query,
                account_number=account_number,
            )

            paths = []

            for record in result:
                path = record["path"]

                nodes = []

                for node in path.nodes:
                    labels = list(node.labels)

                    if "Account" in labels:
                        nodes.append({
                            "type": "Account",
                            "account_number": node.get("account_number"),
                            "bank": node.get("bank_name"),
                        })

                    elif "Transaction" in labels:
                        nodes.append({
                            "type": "Transaction",
                            "transaction_id": node.get("transaction_id"),
                            "amount": node.get("amount"),
                            "status": node.get("status"),
                        })

                paths.append({
                    "path": nodes
                })

            return paths
        
    def shortest_path(
        self,
        source_account: str,
        target_account: str,
    ):
        query = """
        MATCH path = shortestPath(
            (a:Account {account_number:$source_account})
            -[*..10]-
            (b:Account {account_number:$target_account})
        )

        RETURN path
        """

        with driver.session(
            database=settings.NEO4J_DATABASE
        ) as session:
            result = session.run(
                query,
                source_account=source_account,
                target_account=target_account,
            )

            record = result.single()

            if not record:
                return {"message": "No path found"}

            path = record["path"]

            nodes = []

            for node in path.nodes:
                labels = list(node.labels)

                if "Account" in labels:
                    nodes.append({
                        "type": "Account",
                        "account_number": node.get("account_number"),
                        "bank": node.get("bank_name"),
                    })

                elif "Transaction" in labels:
                    nodes.append({
                        "type": "Transaction",
                        "transaction_id": node.get("transaction_id"),
                        "amount": node.get("amount"),
                    })

            return {
                "path": nodes
            }
        
    def detect_fraud_rings(
        self,
        minimum_connections: int = 2,
    ):
        query = """
        MATCH (a:Account)-[:SENT]->(:Transaction)-[:RECEIVED_BY]->(b:Account)

        WITH
            a,
            collect(DISTINCT b.account_number) AS connected_accounts,
            COUNT(DISTINCT b) AS connections

        WHERE connections >= $minimum_connections

        RETURN
            a.account_number AS account,
            connected_accounts,
            connections

        ORDER BY connections DESC
        """

        with driver.session(
            database=settings.NEO4J_DATABASE
        ) as session:
            result = session.run(
                query,
                minimum_connections=minimum_connections,
            )

            return [
                dict(record)
                for record in result
            ]
        
    def find_money_mules(
        self,
        minimum_sources: int = 5,
    ):
        query = """
        MATCH
        (src:Account)-[:SENT]->
        (:Transaction)-[:RECEIVED_BY]->
        (target:Account)

        WITH
        target,
        COUNT(DISTINCT src) AS senders

        WHERE senders >= $minimum_sources

        RETURN
        target.account_number AS account_number,
        senders

        ORDER BY senders DESC
        """

        with driver.session(
            database=settings.NEO4J_DATABASE
        ) as session:
            result = session.run(
                query,
                minimum_sources=minimum_sources,
            )

            return [
                dict(record)
                for record in result
            ]
    # ==========================================================
    # MONEY MULE DETECTION
    # ==========================================================

    def find_money_mules(self, minimum_sources: int = 5):
        """
        Detect accounts receiving money from many different accounts.
        These are potential money mule accounts.
        """

        query = """
        MATCH
        (src:Account)-[:SENT]->
        (:Transaction)-[:RECEIVED_BY]->
        (target:Account)

        WITH
        target,
        COUNT(DISTINCT src) AS sender_count

        WHERE sender_count >= $minimum_sources

        RETURN
        target.account_number AS account_number,
        sender_count

        ORDER BY sender_count DESC
        """

        with driver.session(
            database=settings.NEO4J_DATABASE
        ) as session:
            result = session.run(
                query,
                minimum_sources=minimum_sources,
            )

            return [
                dict(record)
                for record in result
            ]
        
        


graph_queries = GraphQueries()