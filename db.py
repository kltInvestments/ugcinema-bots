import asyncpg
from typing import Optional, List

_pool: Optional[asyncpg.Pool] = None

async def init_pool(dsn: str):
    global _pool
    if _pool is None:
        _pool = await asyncpg.create_pool(dsn, min_size=1, max_size=5)

async def fetch(query: str, *args) -> List[asyncpg.Record]:
    async with _pool.acquire() as conn:
        return await conn.fetch(query, *args)

async def fetchrow(query: str, *args) -> Optional[asyncpg.Record]:
    async with _pool.acquire() as conn:
        return await conn.fetchrow(query, *args)

async def execute(query: str, *args) -> str:
    async with _pool.acquire() as conn:
        return await conn.execute(query, *args)

# ---------- subscriptions ----------
async def upsert_subscription(telegram_id: int, username: Optional[str], phone: str, status: str, start_ts, expiry_ts):
    q = """
    INSERT INTO subscriptions (telegram_id, username, phone, status, start_date, expiry_date)
    VALUES ($1,$2,$3,$4,$5,$6)
    ON CONFLICT (telegram_id) DO UPDATE
    SET username=EXCLUDED.username, phone=EXCLUDED.phone, status=EXCLUDED.status, start_date=EXCLUDED.start_date, expiry_date=EXCLUDED.expiry_date;
    """
    return await execute(q, telegram_id, username, phone, status, start_ts, expiry_ts)

async def mark_expired(telegram_id: int):
    return await execute("UPDATE subscriptions SET status='expired' WHERE telegram_id=$1", telegram_id)

# ---------- uploads & engagement ----------
async def record_upload(uploader_id: int, title: str, category: str, free_or_paid: str):
    q = "INSERT INTO uploads (uploader_id, title, category, free_or_paid) VALUES ($1,$2,$3,$4)"
    return await execute(q, uploader_id, title, category, free_or_paid)

async def title_exists(title: str) -> bool:
    row = await fetchrow("SELECT id FROM uploads WHERE LOWER(title)=LOWER($1) LIMIT 1", title)
    return row is not None

async def recent_by_category(category: str, limit: int = 10) -> List[asyncpg.Record]:
    return await fetch("SELECT title, created_at FROM uploads WHERE category=$1 ORDER BY created_at DESC LIMIT $2", category, limit)

async def inc_engagement(telegram_id: int, username: Optional[str]):
    rec = await fetchrow("SELECT id, messages_count FROM engagement WHERE telegram_id=$1", telegram_id)
    from datetime import datetime, timezone
    now = datetime.now(timezone.utc)
    if rec is None:
        return await execute("INSERT INTO engagement (telegram_id, username, messages_count, last_seen) VALUES ($1,$2,$3,$4)", telegram_id, username or "", 1, now)
    else:
        return await execute("UPDATE engagement SET username=$1, messages_count=$2, last_seen=$3 WHERE telegram_id=$4", username or "", int(rec["messages_count"])+1, now, telegram_id)

# ---------- stats ----------
async def stats_snapshot():
    active = await fetchrow("SELECT COUNT(*) c FROM subscriptions WHERE status='active'")
    expired = await fetchrow("SELECT COUNT(*) c FROM subscriptions WHERE status='expired'")
    uploads = await fetchrow("SELECT COUNT(*) c FROM uploads")
    by_cat = await fetch("SELECT category, COUNT(*) c FROM uploads GROUP BY category ORDER BY c DESC")
    top_eng = await fetch("SELECT username, telegram_id, messages_count FROM engagement ORDER BY messages_count DESC NULLS LAST LIMIT 10")
    return {
        "active": active["c"] if active else 0,
        "expired": expired["c"] if expired else 0,
        "uploads": uploads["c"] if uploads else 0,
        "by_cat": [(r["category"], r["c"]) for r in by_cat],
        "top_eng": [(r["username"], r["telegram_id"], r["messages_count"]) for r in top_eng],
    }
