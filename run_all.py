import json
import os

from src.ingestion_pipeline import ingest_to_sqlite
from src.report_automation import compare_report_generation
from src.unified_view import simulate_concurrent_engineers

N_ASSETS = 156
DURATION_HOURS = 200
SEED = 401
DB_PATH = "results/historian.db"


def main():
    os.makedirs("results", exist_ok=True)
    ingestion = ingest_to_sqlite(DB_PATH, N_ASSETS, DURATION_HOURS, SEED)
    report_comparison = compare_report_generation(DB_PATH, N_ASSETS)
    unified_view = simulate_concurrent_engineers(DB_PATH, n_engineers=18, n_assets=N_ASSETS)

    summary = {"n_assets": N_ASSETS, "ingestion": ingestion,
               "report_automation": report_comparison, "unified_view": unified_view}

    with open("results/summary.json", "w") as f:
        json.dump(summary, f, indent=2)
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
