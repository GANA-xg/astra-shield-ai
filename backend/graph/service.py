from neo4j import WRITE_ACCESS

from graph.connection import _get_driver
from core.config import settings


class GraphService:
    def __init__(self):
        pass

    def create_person(self, person_id: str, name: str, phone: str, email: str):
        query = """
        MERGE (p:Person {person_id:$person_id})
        SET p.name=$name, p.phone=$phone, p.email=$email
        """
        with _get_driver().session(
            database=settings.NEO4J_DATABASE or None,
            default_access_mode=WRITE_ACCESS,
        ) as session:
            session.run(query, person_id=person_id, name=name, phone=phone, email=email)

    def create_account(self, account_number: str, bank_name: str, ifsc: str, balance: float):
        query = """
        MERGE (a:Account {account_number:$account_number})
        SET a.bank_name=$bank_name, a.ifsc=$ifsc, a.balance=$balance
        """
        with _get_driver().session(
            database=settings.NEO4J_DATABASE or None,
            default_access_mode=WRITE_ACCESS,
        ) as session:
            session.run(query, account_number=account_number, bank_name=bank_name, ifsc=ifsc, balance=balance)

    def create_device(self, device_id: str, ip_address: str, device_type: str, location: str):
        query = """
        MERGE (d:Device {device_id:$device_id})
        SET d.ip_address=$ip_address, d.device_type=$device_type, d.location=$location
        """
        with _get_driver().session(
            database=settings.NEO4J_DATABASE or None,
            default_access_mode=WRITE_ACCESS,
        ) as session:
            session.run(query, device_id=device_id, ip_address=ip_address, device_type=device_type, location=location)

    def create_transaction(self, transaction_id: str, amount: float, status: str, mode: str):
        query = """
        MERGE (t:Transaction {transaction_id:$transaction_id})
        SET t.amount=$amount, t.status=$status, t.mode=$mode, t.timestamp=datetime()
        """
        with _get_driver().session(
            database=settings.NEO4J_DATABASE or None,
            default_access_mode=WRITE_ACCESS,
        ) as session:
            session.run(query, transaction_id=transaction_id, amount=amount, status=status, mode=mode)

    def link_person_account(self, person_id: str, account_number: str):
        query = """
        MATCH (p:Person {person_id:$person_id})
        MATCH (a:Account {account_number:$account_number})
        MERGE (p)-[:OWNS]->(a)
        """
        with _get_driver().session(
            database=settings.NEO4J_DATABASE or None,
            default_access_mode=WRITE_ACCESS,
        ) as session:
            session.run(query, person_id=person_id, account_number=account_number)

    def link_person_device(self, person_id: str, device_id: str):
        query = """
        MATCH (p:Person {person_id:$person_id})
        MATCH (d:Device {device_id:$device_id})
        MERGE (p)-[:USES]->(d)
        """
        with _get_driver().session(
            database=settings.NEO4J_DATABASE or None,
            default_access_mode=WRITE_ACCESS,
        ) as session:
            session.run(query, person_id=person_id, device_id=device_id)

    def link_transaction(self, sender_account: str, transaction_id: str, receiver_account: str):
        query = """
        MATCH (sender:Account {account_number:$sender})
        MATCH (receiver:Account {account_number:$receiver})
        MATCH (tx:Transaction {transaction_id:$tx})
        MERGE (sender)-[:SENT]->(tx)
        MERGE (tx)-[:RECEIVED_BY]->(receiver)
        """
        with _get_driver().session(
            database=settings.NEO4J_DATABASE or None,
            default_access_mode=WRITE_ACCESS,
        ) as session:
            session.run(query, sender=sender_account, receiver=receiver_account, tx=transaction_id)


graph_service = GraphService()
