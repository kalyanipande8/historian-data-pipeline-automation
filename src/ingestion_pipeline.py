"""Real streaming ingestion pipeline: consumes the historian event
generator in batches and writes to a genuine SQLite database
incrementally, rather than loading one static file -- the real
analogue of a continuous-ingestion historian integration."""
from __future__ import annotations

import sqlite3
import time

from .simulate_historian_stream import generate_stream

BATCH_SIZE = 2000


def ingest_to_sqlite(db_path: str, n_assets: int, duration_hours: int, seed: int) -> dict:
    conn = sqlite3.connect(db_path)
    conn.execute("DROP TABLE IF EXISTS readings")
    conn.execute("""CREATE TABLE readings (
        timestamp TEXT, asset_id INTEGER, tag TEXT, value REAL
    )""")
    conn.execute("CREATE INDEX idx_asset ON readings(asset_id)")
    conn.execute("CREATE INDEX idx_tag ON readings(tag)")

    start = time.perf_counter()
    batch = []
    n_rows = 0
    for ts, asset_id, tag, value in generate_stream(n_assets, duration_hours, seed):
        batch.append((ts.isoformat(), asset_id, tag, value))
        if len(batch) >= BATCH_SIZE:
            conn.executemany("INSERT INTO readings VALUES (?, ?, ?, ?)", batch)
            n_rows += len(batch)
            batch = []
    if batch:
        conn.executemany("INSERT INTO readings VALUES (?, ?, ?, ?)", batch)
        n_rows += len(batch)
    conn.commit()
    elapsed = time.perf_counter() - start
    conn.close()

    return {"n_rows_ingested": n_rows, "elapsed_sec": round(elapsed, 3),
            "rows_per_sec": round(n_rows / elapsed, 1) if elapsed > 0 else None}
