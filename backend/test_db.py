from sqlalchemy import text

from db.session import engine


def test_connection():
    try:
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))

            print("✅ PostgreSQL Connected Successfully")
            print(f"Result: {result.scalar()}")

    except Exception as e:
        print("❌ Database Connection Failed")
        print(e)


if __name__ == "__main__":
    test_connection()