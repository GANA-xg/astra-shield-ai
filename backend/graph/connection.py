import os
import traceback

import certifi

os.environ["SSL_CERT_FILE"] = certifi.where()

from neo4j import GraphDatabase, READ_ACCESS
from core.config import settings
from core.logging import logger

driver = None


def _get_driver():
    """Lazy-init the Neo4j driver as a singleton so import doesn't crash."""
    global driver
    if driver is not None:
        return driver

    if not settings.NEO4J_URI or not settings.NEO4J_USERNAME or not settings.NEO4J_PASSWORD:
        logger.warning("Neo4j not configured — skipping driver creation")
        return None

    try:
        driver = GraphDatabase.driver(
            settings.NEO4J_URI,
            auth=(
                settings.NEO4J_USERNAME,
                settings.NEO4J_PASSWORD,
            ),
        )
        logger.info("Neo4j driver created (%s)", settings.NEO4J_URI)
    except Exception:
        logger.error("Failed to create Neo4j driver:\n%s", traceback.format_exc())
        driver = None

    return driver


def _session():
    """Open a read-only session against Neo4j Aura.

    Aura single-node clusters do not provide a separate WRITE endpoint,
    so all queries must be routed as READ_ACCESS.
    """
    d = _get_driver()
    if d is None:
        return None
    return d.session(
        database=settings.NEO4J_DATABASE or None,
        default_access_mode=READ_ACCESS,
    )


def check_neo4j_connection() -> bool:
    d = _get_driver()
    if d is None:
        return False

    try:
        d.verify_connectivity()
        return True
    except Exception:
        logger.error("Neo4j connectivity check failed:\n%s", traceback.format_exc())
        return False


def close_neo4j_connection() -> None:
    global driver
    if driver is not None:
        try:
            driver.close()
        finally:
            driver = None
