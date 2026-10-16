"""Simulate a real-time historian sensor data stream from 150+ facility
assets -- each asset emits multiple tags (temperature, pressure,
vibration, flow) at a fixed sampling interval, mirroring how an
industrial historian (PI, Wonderware, etc.) actually produces data."""
from __future__ import annotations

import numpy as np
import pandas as pd

N_ASSETS = 156
TAGS_PER_ASSET = ["temperature", "pressure", "vibration", "flow_rate"]
SAMPLE_INTERVAL_MIN = 5
DURATION_HOURS = 48
SEED = 401


def generate_stream(n_assets: int = N_ASSETS, duration_hours: int = DURATION_HOURS, seed: int = SEED):
    """Yields (timestamp, asset_id, tag, value) tuples in time order,
    simulating a real streaming historian feed rather than a static
    pre-built table."""
    rng = np.random.default_rng(seed)
    n_samples = int(duration_hours * 60 / SAMPLE_INTERVAL_MIN)
    timestamps = pd.date_range("2026-01-01", periods=n_samples, freq=f"{SAMPLE_INTERVAL_MIN}min")

    asset_baselines = {
        asset_id: {tag: rng.normal(loc, scale) for tag, (loc, scale) in
                   zip(TAGS_PER_ASSET, [(75, 8), (120, 15), (0.4, 0.1), (50, 10)])}
        for asset_id in range(n_assets)
    }

    for ts in timestamps:
        for asset_id in range(n_assets):
            for tag in TAGS_PER_ASSET:
                base = asset_baselines[asset_id][tag]
                noise_scale = {"temperature": 2.0, "pressure": 4.0, "vibration": 0.05, "flow_rate": 3.0}[tag]
                value = base + rng.normal(0, noise_scale)
                yield ts, asset_id, tag, round(float(value), 3)


def collect_stream_to_dataframe(n_assets: int = N_ASSETS, duration_hours: int = DURATION_HOURS,
                                 seed: int = SEED) -> pd.DataFrame:
    rows = list(generate_stream(n_assets, duration_hours, seed))
    return pd.DataFrame(rows, columns=["timestamp", "asset_id", "tag", "value"])


if __name__ == "__main__":
    df = collect_stream_to_dataframe()
    print(df.shape, df["asset_id"].nunique(), "assets")
