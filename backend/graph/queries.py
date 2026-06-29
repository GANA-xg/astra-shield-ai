from graph.connection import driver


class GraphQueries:

    # ==========================================================
    # PERSON
    # ==========================================================

    def find_person(self, person_id: str):
        query = """
        MATCH (p:Person {person_id:$person_id})
        RETURN p
        """

        with driver.session() as session:
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

        with driver.session() as session:
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

        with driver.session() as session:
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

        with driver.session() as session:
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

        with driver.session() as session:
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

        with driver.session() as session:
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

        with driver.session() as session:
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

        with driver.session() as session:
            result = session.run(
                query,
                account_number=account_number,
            )

            return [record["path"] for record in result]


graph_queries = GraphQueries()