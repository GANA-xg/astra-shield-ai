<<<<<<< HEAD
from core.config import settings

driver = None


def _get_driver():
    """Lazy-init the Neo4j driver so import doesn't crash when neo4j isn't installed."""
    global driver
    if driver is not None:
        return driver
    try:
        from neo4j import GraphDatabase

        driver = GraphDatabase.driver(
            settings.NEO4J_URI,
            auth=(
                settings.NEO4J_USERNAME,
                settings.NEO4J_PASSWORD,
            ),
        )
    except Exception:
        driver = None
    return driver


def check_neo4j_connection() -> bool:
    """
    Verify that the application can connect to Neo4j.
    """
    d = _get_driver()
    if d is None:
        return False

    try:
        d.verify_connectivity()
        return True
    except Exception:
        return False


def close_neo4j_connection() -> None:
    """
    Close the Neo4j driver cleanly.
    """
    global driver
    if driver is not None:
        try:
            driver.close()
        except Exception:
            pass
        driver = None
=======
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
>>>>>>> origin/main
