"""Generate realistic synthetic fraud graph data in Neo4j.

Creates 200+ persons, 250+ accounts, device-sharing clusters,
2-3 fraud rings (circular/star-shaped money flow), and randomized
but plausible transaction patterns.

Usage:
    cd backend && python -m graph.seed
"""

import random
import string
from datetime import datetime, timedelta

from neo4j import WRITE_ACCESS

from graph.connection import _get_driver
from core.config import settings

random.seed(42)

INDIAN_NAMES = [
    "Aarav Sharma", "Vivaan Patel", "Aditya Mehta", "Arjun Reddy", "Sai Kumar",
    "Rohan Gupta", "Vihaan Singh", "Kabir Verma", "Ayaan Desai", "Reyansh Rao",
    "Diya Nair", "Ananya Joshi", "Isha Tiwari", "Priya Chatterjee", "Nisha Agarwal",
    "Sneha Iyer", "Kavya Menon", "Riya Bhatt", "Aisha Khan", "Pooja Mishra",
    "Rahul Yadav", "Amit Singh", "Sanjay Pandey", "Vikram Chauhan", "Manish Dubey",
    "Suresh Kumar", "Rajesh Verma", "Ajay Thakur", "Deepak Joshi", "Vinod Sharma",
    "Sunita Devi", "Geeta Bai", "Meena Kumari", "Sarita Pandey", "Usha Rani",
    "Rekha Gupta", "Suman Devi", "Kamla Bai", "Indira Nehru", "Sarojini Naidu",
    "Vikas Singh", "Nitin Kumar", "Pankaj Tiwari", "Sumit Chauhan", "Gaurav Jain",
    "Prashant Dubey", "Mohit Bhat", "Tarun Verma", "Ashish Pandey", "Neeraj Kumar",
    "Shikha Mishra", "Pallavi Reddy", "Ritu Agarwal", "Deepika Chauhan", "Shruti Nair",
]

BANKS = [
    "State Bank of India", "HDFC Bank", "ICICI Bank", "Axis Bank", "Punjab National Bank",
    "Bank of Baroda", "Canara Bank", "Union Bank of India", "Bank of India", "IDBI Bank",
    "Kotak Mahindra Bank", "Yes Bank", "IndusInd Bank", "Federal Bank", "South Indian Bank",
]

DEVICE_TYPES = ["Android", "iOS", "Windows", "Linux"]
LOCATIONS = [
    "Mumbai", "Delhi", "Bangalore", "Hyderabad", "Chennai", "Kolkata", "Pune",
    "Ahmedabad", "Jaipur", "Lucknow", "Chandigarh", "Bhopal", "Patna", "Kochi",
]

TX_MODES = ["UPI", "IMPS", "NEFT", "RTGS", "NetBanking"]


def _gen_account_number():
    return "".join(random.choices(string.digits, k=10))


def _gen_ifsc():
    banks = ["SBIN", "HDFC", "ICIC", "UTIB", "PUNB", "BARB", "CNRB", "UBIN"]
    return random.choice(banks) + "000" + "".join(random.choices(string.digits, k=4))


def _gen_device_id():
    return "DEV" + "".join(random.choices(string.ascii_uppercase + string.digits, k=8))


def _gen_tx_id(seq):
    return f"TX{seq:06d}"


def seed_realistic_graph():
    """Generate and insert realistic synthetic fraud graph data."""
    d = _get_driver()
    if d is None:
        print("Neo4j not connected — skipping seed")
        return

    persons = []
    accounts = []
    devices = []
    transactions = []
    person_account_links = []
    person_device_links = []
    tx_links = []

    tx_seq = 1

    # ────────────────────────────────────────────────────────
    # 1. Create 210 persons
    # ────────────────────────────────────────────────────────
    for i in range(210):
        pid = f"P{i+1:04d}"
        name = random.choice(INDIAN_NAMES) + f" {i+1}"
        phone = f"+91{random.randint(6000000000, 9999999999)}"
        email = f"user{i+1}@example.com"
        persons.append({"person_id": pid, "name": name, "phone": phone, "email": email})

    # ────────────────────────────────────────────────────────
    # 2. Create 260 accounts (some persons get 2)
    # ────────────────────────────────────────────────────────
    acct_idx = 0
    for i, p in enumerate(persons):
        # Each person gets 1 account; persons 100-129 get a second account
        acct_num = _gen_account_number()
        bank = random.choice(BANKS)
        ifsc = _gen_ifsc()
        balance = round(random.uniform(5000, 500000), 2)
        accounts.append({"account_number": acct_num, "bank_name": bank, "ifsc": ifsc, "balance": balance})
        person_account_links.append((p["person_id"], acct_num))
        acct_idx += 1

        if 100 <= i < 130:
            acct_num2 = _gen_account_number()
            bank2 = random.choice(BANKS)
            ifsc2 = _gen_ifsc()
            balance2 = round(random.uniform(5000, 200000), 2)
            accounts.append({"account_number": acct_num2, "bank_name": bank2, "ifsc": ifsc2, "balance": balance2})
            person_account_links.append((p["person_id"], acct_num2))
            acct_idx += 1

    print(f"Created {len(persons)} persons, {len(accounts)} accounts")

    # ────────────────────────────────────────────────────────
    # 3. Create devices with sharing clusters
    # ────────────────────────────────────────────────────────
    # 150 unique devices
    for i in range(150):
        did = _gen_device_id()
        ip = f"192.168.{random.randint(0,255)}.{random.randint(1,254)}"
        dtype = random.choice(DEVICE_TYPES)
        loc = random.choice(LOCATIONS)
        devices.append({"device_id": did, "ip_address": ip, "device_type": dtype, "location": loc})

    # Each person uses 1-2 devices
    for p in persons:
        idx = int(p["person_id"][1:]) - 1
        did = devices[idx % len(devices)]["device_id"]
        person_device_links.append((p["person_id"], did))
        # 30% of persons use a second device
        if random.random() < 0.3:
            did2 = devices[(idx + 50) % len(devices)]["device_id"]
            person_device_links.append((p["person_id"], did2))

    # Create device-sharing clusters: persons 140-159 all share device DEV_CLUSTER1
    cluster_device_id = "DEVCLUSTER1"
    devices.append({"device_id": cluster_device_id, "ip_address": "10.0.0.99",
                     "device_type": "Android", "location": "Delhi"})
    for i in range(140, 160):
        pid = f"P{i+1:04d}"
        person_device_links.append((pid, cluster_device_id))

    print(f"Created {len(devices)} devices with sharing clusters")

    # ────────────────────────────────────────────────────────
    # 4. Normal transaction patterns
    # ────────────────────────────────────────────────────────
    now = datetime.utcnow()
    normal_tx_count = 0
    for _ in range(400):
        sender_idx = random.randint(0, len(accounts) - 1)
        receiver_idx = random.randint(0, len(accounts) - 1)
        while receiver_idx == sender_idx:
            receiver_idx = random.randint(0, len(accounts) - 1)

        amount = round(random.uniform(500, 50000), 2)
        mode = random.choice(TX_MODES)
        ts = now - timedelta(hours=random.randint(1, 720))
        tid = _gen_tx_id(tx_seq)
        tx_seq += 1

        transactions.append({
            "transaction_id": tid, "amount": amount,
            "timestamp": ts.isoformat(), "status": "SUCCESS", "mode": mode,
        })
        tx_links.append((accounts[sender_idx]["account_number"], tid, accounts[receiver_idx]["account_number"]))
        normal_tx_count += 1

    print(f"Created {normal_tx_count} normal transactions")

    # ────────────────────────────────────────────────────────
    # 5. Fraud Ring 1 — circular money flow (accounts 0-5)
    # ────────────────────────────────────────────────────────
    ring1_accounts = [accounts[i]["account_number"] for i in range(6)]
    ring1_tx_count = 0
    for cycle in range(3):
        for i in range(6):
            sender = ring1_accounts[i]
            receiver = ring1_accounts[(i + 1) % 6]
            amount = round(random.uniform(15000, 80000), 2)
            mode = random.choice(["UPI", "IMPS"])
            ts = now - timedelta(hours=random.randint(1, 48))
            tid = _gen_tx_id(tx_seq)
            tx_seq += 1
            transactions.append({
                "transaction_id": tid, "amount": amount,
                "timestamp": ts.isoformat(), "status": "SUCCESS", "mode": mode,
            })
            tx_links.append((sender, tid, receiver))
            ring1_tx_count += 1

    print(f"Fraud Ring 1: {ring1_tx_count} circular transactions across 6 accounts")

    # ────────────────────────────────────────────────────────
    # 6. Fraud Ring 2 — star pattern (hub account receives from many)
    # ────────────────────────────────────────────────────────
    hub_acct = accounts[200]["account_number"]
    star_accounts = [accounts[i]["account_number"] for i in range(200, 215)]
    ring2_tx_count = 0
    for _ in range(25):
        sender = random.choice(star_accounts)
        if sender == hub_acct:
            continue
        amount = round(random.uniform(10000, 100000), 2)
        mode = "UPI"
        ts = now - timedelta(hours=random.randint(1, 24))
        tid = _gen_tx_id(tx_seq)
        tx_seq += 1
        transactions.append({
            "transaction_id": tid, "amount": amount,
            "timestamp": ts.isoformat(), "status": "SUCCESS", "mode": mode,
        })
        tx_links.append((sender, tid, hub_acct))
        ring2_tx_count += 1

    # Hub sends out to mule accounts
    mule_accts = [accounts[i]["account_number"] for i in range(215, 225)]
    for _ in range(15):
        receiver = random.choice(mule_accts)
        amount = round(random.uniform(5000, 30000), 2)
        ts = now - timedelta(hours=random.randint(1, 24))
        tid = _gen_tx_id(tx_seq)
        tx_seq += 1
        transactions.append({
            "transaction_id": tid, "amount": amount,
            "timestamp": ts.isoformat(), "status": "SUCCESS", "mode": "NEFT",
        })
        tx_links.append((hub_acct, tid, receiver))
        ring2_tx_count += 1

    print(f"Fraud Ring 2: {ring2_tx_count} transactions in star pattern (hub + 15 senders + 10 mules)")

    # ────────────────────────────────────────────────────────
    # 7. Fraud Ring 3 — rapid burst (velocity anomaly)
    # ────────────────────────────────────────────────────────
    burst_acct = accounts[230]["account_number"]
    burst_receiver = accounts[231]["account_number"]
    burst_tx_count = 0
    for i in range(12):
        amount = round(random.uniform(9000, 49000), 2)
        ts = now - timedelta(minutes=random.randint(5, 180))
        tid = _gen_tx_id(tx_seq)
        tx_seq += 1
        transactions.append({
            "transaction_id": tid, "amount": amount,
            "timestamp": ts.isoformat(), "status": "SUCCESS", "mode": "UPI",
        })
        tx_links.append((burst_acct, tid, burst_receiver))
        burst_tx_count += 1

    print(f"Fraud Ring 3: {burst_tx_count} rapid transactions (velocity anomaly)")

    # ────────────────────────────────────────────────────────
    # 8. Insert everything into Neo4j
    # ────────────────────────────────────────────────────────
    with d.session(
        database=settings.NEO4J_DATABASE or None,
        default_access_mode=WRITE_ACCESS,
    ) as session:
        # Persons
        session.run("""
            UNWIND $rows AS row
            MERGE (p:Person {person_id: row.person_id})
            SET p.name = row.name, p.phone = row.phone, p.email = row.email
        """, rows=persons)
        print("  Inserted persons")

        # Accounts
        session.run("""
            UNWIND $rows AS row
            MERGE (a:Account {account_number: row.account_number})
            SET a.bank_name = row.bank_name, a.ifsc = row.ifsc, a.balance = row.balance
        """, rows=accounts)
        print("  Inserted accounts")

        # Devices
        session.run("""
            UNWIND $rows AS row
            MERGE (d:Device {device_id: row.device_id})
            SET d.ip_address = row.ip_address, d.device_type = row.device_type, d.location = row.location
        """, rows=devices)
        print("  Inserted devices")

        # Person-Account links
        session.run("""
            UNWIND $rows AS row
            MATCH (p:Person {person_id: row[0]})
            MATCH (a:Account {account_number: row[1]})
            MERGE (p)-[:OWNS]->(a)
        """, rows=person_account_links)
        print("  Linked persons to accounts")

        # Person-Device links
        session.run("""
            UNWIND $rows AS row
            MATCH (p:Person {person_id: row[0]})
            MATCH (d:Device {device_id: row[1]})
            MERGE (p)-[:USES]->(d)
        """, rows=person_device_links)
        print("  Linked persons to devices")

        # Transactions
        session.run("""
            UNWIND $rows AS row
            MERGE (t:Transaction {transaction_id: row.transaction_id})
            SET t.amount = row.amount, t.timestamp = datetime(row.timestamp),
                t.status = row.status, t.mode = row.mode
        """, rows=transactions)
        print("  Inserted transactions")

        # Transaction links
        session.run("""
            UNWIND $rows AS row
            MATCH (sender:Account {account_number: row[0]})
            MATCH (tx:Transaction {transaction_id: row[1]})
            MATCH (receiver:Account {account_number: row[2]})
            MERGE (sender)-[:SENT]->(tx)
            MERGE (tx)-[:RECEIVED_BY]->(receiver)
        """, rows=tx_links)
        print("  Linked transactions")

    print(f"\nSeed complete: {len(persons)} persons, {len(accounts)} accounts, "
          f"{len(devices)} devices, {len(transactions)} transactions")


if __name__ == "__main__":
    seed_realistic_graph()
