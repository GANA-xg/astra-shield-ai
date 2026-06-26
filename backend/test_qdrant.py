from qdrant.client import check_qdrant_connection

if check_qdrant_connection():
    print("✅ Qdrant Connected Successfully")
else:
    print("❌ Qdrant Connection Failed")