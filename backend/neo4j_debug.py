from neo4j import GraphDatabase
import traceback

URI = "neo4j+s://c62227b3.databases.neo4j.io"
AUTH = ("c62227b3", "PASTE_THE_SHARED_PASSWORD_HERE")

try:
    with GraphDatabase.driver(URI, auth=AUTH) as driver:
        driver.verify_connectivity()
        print("✅ Connected!")

        records, summary, keys = driver.execute_query(
            "RETURN 1 AS n",
            database_="c62227b3",
        )
        print(records)

except Exception:
    traceback.print_exc()