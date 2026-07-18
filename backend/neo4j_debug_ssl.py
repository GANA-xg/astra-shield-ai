import sys
from neo4j import GraphDatabase
from neo4j.debug import watch

watch("neo4j", out=sys.stdout)

driver = GraphDatabase.driver(
    "neo4j+s://c62227b3.databases.neo4j.io",
    auth=("c62227b3", "wlmjtUfHHma9Th2Iel3RZr5gfQYB9nQPUvoz0YQrQqo"),
)

driver.verify_connectivity()