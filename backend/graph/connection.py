from neo4j import GraphDatabase

from core.config import settings


driver = GraphDatabase.driver(
    settings.NEO4J_URI,
    auth=(
        settings.NEO4J_USERNAME,
        settings.NEO4J_PASSWORD,
    ),
)


def check_neo4j_connection() -> bool:
    """
    Verify that the application can connect to Neo4j.
    """

    try:
        driver.verify_connectivity()
        return True

    except Exception:
        return False


def close_neo4j_connection() -> None:
    """
    Close the Neo4j driver cleanly.
    """

    driver.close()