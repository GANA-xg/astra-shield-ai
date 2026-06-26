from graph.connection import driver


def seed_graph():
    query = """
    // =========================
    // Create Persons
    // =========================
    MERGE (alice:Person {
        person_id: "P001",
        name: "Alice Johnson",
        phone: "+919900000001",
        email: "alice@example.com"
    })

    MERGE (bob:Person {
        person_id: "P002",
        name: "Bob Smith",
        phone: "+919900000002",
        email: "bob@example.com"
    })

    // =========================
    // Create Accounts
    // =========================
    MERGE (acc1:Account {
        account_number: "1234567890",
        bank_name: "State Bank of India",
        ifsc: "SBIN0001234",
        balance: 50000
    })

    MERGE (acc2:Account {
        account_number: "9876543210",
        bank_name: "HDFC Bank",
        ifsc: "HDFC0004321",
        balance: 75000
    })

    // =========================
    // Create Device
    // =========================
    MERGE (device:Device {
        device_id: "D001",
        ip_address: "192.168.1.100",
        device_type: "Android",
        location: "Hyderabad"
    })

    // =========================
    // Create Transactions
    // =========================
    MERGE (tx1:Transaction {
        transaction_id: "TX001",
        amount: 15000,
        timestamp: datetime(),
        status: "SUCCESS",
        mode: "UPI"
    })

    MERGE (tx2:Transaction {
        transaction_id: "TX002",
        amount: 25000,
        timestamp: datetime(),
        status: "SUCCESS",
        mode: "IMPS"
    })

    // =========================
    // Relationships
    // =========================

    MERGE (alice)-[:OWNS]->(acc1)

    MERGE (bob)-[:OWNS]->(acc2)

    MERGE (alice)-[:USES]->(device)

    MERGE (device)-[:USED_FOR]->(tx1)

    MERGE (acc1)-[:SENT]->(tx1)

    MERGE (tx1)-[:RECEIVED_BY]->(acc2)

    MERGE (acc2)-[:SENT]->(tx2)

    MERGE (tx2)-[:RECEIVED_BY]->(acc1)
    """

    with driver.session() as session:
        session.run(query)

    print("✅ Graph seeded successfully")


if __name__ == "__main__":
    seed_graph()