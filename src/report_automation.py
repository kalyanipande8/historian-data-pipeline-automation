"""Real timing comparison between a naive manual-style report process
(per-asset Python loop issuing one query each, as an analyst manually
pulling data asset-by-asset would) and the automated pipeline's single
set-based SQL aggregate report -- a genuine, measured speedup, not an
asserted percentage."""
from __future__ import annotations

import sqlite3
import time

import pandas as pd


def manual_style_report(db_path: str, asset_ids: list) -> tuple:
    conn = sqlite3.connect(db_path)
    start = time.perf_counter()
    results = []
    for asset_id in asset_ids:
        for tag in ["temperature", "pressure", "vibration", "flow_rate"]:
            row = conn.execute(
                "SELECT AVG(value), MIN(value), MAX(value) FROM readings WHERE asset_id=? AND tag=?",
                (asset_id, tag),
            ).fetchone()
            results.append((asset_id, tag, *row))
    elapsed = time.perf_counter() - start
    conn.close()
    return pd.DataFrame(results, columns=["asset_id", "tag", "avg", "min", "max"]), elapsed


def automated_report(db_path: str) -> tuple:
    conn = sqlite3.connect(db_path)
    start = time.perf_counter()
    df = pd.read_sql_query(
        "SELECT asset_id, tag, AVG(value) as avg, MIN(value) as min, MAX(value) as max "
        "FROM readings GROUP BY asset_id, tag", conn,
    )
    elapsed = time.perf_counter() - start
    conn.close()
    return df, elapsed


def compare_report_generation(db_path: str, n_assets: int) -> dict:
    asset_ids = list(range(n_assets))
    manual_df, manual_time = manual_style_report(db_path, asset_ids)
    auto_df, auto_time = automated_report(db_path)

    manual_sorted = manual_df.sort_values(["asset_id", "tag"]).reset_index(drop=True)
    auto_sorted = auto_df.sort_values(["asset_id", "tag"]).reset_index(drop=True)
    results_match = manual_sorted[["avg", "min", "max"]].round(3).equals(
        auto_sorted[["avg", "min", "max"]].round(3))

    reduction_pct = round(100 * (manual_time - auto_time) / manual_time, 2) if manual_time > 0 else None

    return {"manual_time_sec": round(manual_time, 4), "automated_time_sec": round(auto_time, 4),
            "time_reduction_pct": reduction_pct, "results_identical": bool(results_match)}
