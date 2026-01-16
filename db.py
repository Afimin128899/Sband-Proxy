import asyncpg
import os

DATABASE_URL = os.environ.get("DATABASE_URL")


async def init_db():
    conn = await asyncpg.connect(DATABASE_URL)
    await conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id BIGINT PRIMARY KEY,
            access_granted BOOLEAN DEFAULT FALSE
        )
    """)
    await conn.close()


async def add_user(user_id: int):
    conn = await asyncpg.connect(DATABASE_URL)
    await conn.execute(
        "INSERT INTO users (user_id) VALUES ($1) "
        "ON CONFLICT (user_id) DO NOTHING",
        user_id
    )
    await conn.close()


async def has_access(user_id: int) -> bool:
    conn = await asyncpg.connect(DATABASE_URL)
    row = await conn.fetchrow(
        "SELECT access_granted FROM users WHERE user_id = $1",
        user_id
    )
    await conn.close()
    return bool(row and row["access_granted"])


async def set_access_granted(user_id: int):
    conn = await asyncpg.connect(DATABASE_URL)
    await conn.execute(
        "UPDATE users SET access_granted = TRUE WHERE user_id = $1",
        user_id
    )
    await conn.close()


async def get_users():
    conn = await asyncpg.connect(DATABASE_URL)
    rows = await conn.fetch("SELECT user_id FROM users")
    await conn.close()
    return [r["user_id"] for r in rows]
