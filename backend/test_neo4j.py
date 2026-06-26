from graph.connection import check_neo4j_connection
if check_neo4j_connection():
    print("✅ Neo4j Connected Successfully")
else:
    print("❌ Neo4j Connection Failed")
