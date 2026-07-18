import os
import certifi

os.environ["SSL_CERT_FILE"] = certifi.where()

from neo4j import GraphDatabase
from core.config import settings

driver = GraphDatabase.driver(
    settings.NEO4J_URI,
    auth=(
        settings.NEO4J_USERNAME,
        settings.NEO4J_PASSWORD,
    ),
)

def check_neo4j_connection():
    try:
        print("URI:", settings.NEO4J_URI)
        print("USERNAME:", settings.NEO4J_USERNAME)
        print("DATABASE:", settings.NEO4J_DATABASE)

        driver.verify_connectivity()

        with driver.session(database=settings.NEO4J_DATABASE) as session:
            result = session.run("RETURN 1 AS n")
            print(result.single())

        print("✅ Connected Successfully")
        return True

    except Exception as e:
        import traceback
        traceback.print_exc()
        return False


def close_neo4j_connection():
    driver.close()