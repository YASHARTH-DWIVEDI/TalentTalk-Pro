import pytest
import asyncio
from sqlalchemy import text
from app.db.database import engine

@pytest.mark.asyncio
async def test_database_connection():
    try:
        async with engine.connect() as conn:
            result = await conn.execute(text("SELECT 1"))
            assert result.scalar() == 1
        print("Database connection successful!")
    except Exception as e:
        pytest.fail(f"Database connection failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_database_connection())
