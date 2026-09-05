import time
import aiosqlite

DB_PATH = "rate_limiter.db"
MAX_TOKENS_PER_MINUTE = 50000
WINDOW_SECONDS = 60


async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS token_usage (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                api_key TEXT NOT NULL,
                tokens INTEGER NOT NULL,
                timestamp REAL NOT NULL
            )
        """)
        await db.commit()


async def record_usage(api_key: str, tokens: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO token_usage (api_key, tokens, timestamp) VALUES (?, ?, ?)",
            (api_key, tokens, time.time()),
        )
        await db.commit()


async def check_rate_limit(api_key: str) -> tuple[bool, int]:
    cutoff = time.time() - WINDOW_SECONDS

    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("DELETE FROM token_usage WHERE timestamp < ?", (cutoff,))
        await db.commit()

        async with db.execute(
            "SELECT COALESCE(SUM(tokens), 0) FROM token_usage WHERE api_key = ? AND timestamp >= ?",
            (api_key, cutoff),
        ) as cursor:
            row = await cursor.fetchone()
            used = row[0]

    return used < MAX_TOKENS_PER_MINUTE, used