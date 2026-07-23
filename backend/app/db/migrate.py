"""Lightweight column migrations for SQLite.

Base.metadata.create_all() only creates missing tables — it never alters an
existing table's columns. Since this app runs on a single always-on SQLite
file with no Alembic, new columns need an explicit ALTER TABLE guarded by a
PRAGMA table_info() check so it's a no-op once applied (and a no-op on a
brand-new DB where create_all() already included the column).
"""
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncConnection


async def _add_column_if_missing(conn: AsyncConnection, table: str, column: str, coltype: str) -> None:
    result = await conn.execute(text(f"PRAGMA table_info({table})"))
    cols = {row[1] for row in result.fetchall()}
    if column not in cols:
        await conn.execute(text(f"ALTER TABLE {table} ADD COLUMN {column} {coltype}"))


async def run_migrations(conn: AsyncConnection) -> None:
    await _add_column_if_missing(conn, "curriculum_items", "learning_goal", "TEXT")
    await _add_column_if_missing(conn, "curriculum_items", "key_topics", "JSON")
