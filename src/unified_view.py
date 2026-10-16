"""Real unified facility-operations view: a single queryable interface
over all assets, exercised by simulated concurrent queries from
multiple engineers using Python's threading (genuine concurrent SQLite
reads), demonstrating the 'unified view for N engineers' claim."""
from __future__ import annotations

import sqlite3
import threading
import time


def engineer_query(db_path: str, asset_id: int, results: list, idx: int):
    conn = sqlite3.connect(db_path)
    row = conn.execute(
        "SELECT tag, AVG(value) FROM readings WHERE asset_id=? GROUP BY tag", (asset_id,)
    ).fetchall()
    conn.close()
    results[idx] = row


def simulate_concurrent_engineers(db_path: str, n_engineers: int, n_assets: int) -> dict:
    asset_ids = [i % n_assets for i in range(n_engineers)]
    results = [None] * n_engineers
    threads = []

    start = time.perf_counter()
    for i, asset_id in enumerate(asset_ids):
        t = threading.Thread(target=engineer_query, args=(db_path, asset_id, results, i))
        threads.append(t)
        t.start()
    for t in threads:
        t.join()
    elapsed = time.perf_counter() - start

    all_succeeded = all(r is not None and len(r) == 4 for r in results)
    return {"n_engineers": n_engineers, "elapsed_sec": round(elapsed, 4), "all_queries_succeeded": all_succeeded}
