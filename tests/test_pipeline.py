import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.ingestion_pipeline import ingest_to_sqlite
from src.report_automation import compare_report_generation
from src.unified_view import simulate_concurrent_engineers

N_ASSETS = 20
DURATION_HOURS = 4
SEED = 401
TEST_DB = "/tmp/test_historian.db"


def setup_module(module):
    ingest_to_sqlite(TEST_DB, N_ASSETS, DURATION_HOURS, SEED)


def test_ingestion_row_count_matches_expected():
    result = ingest_to_sqlite(TEST_DB, N_ASSETS, DURATION_HOURS, SEED)
    expected_rows = N_ASSETS * 4 * int(DURATION_HOURS * 60 / 5)
    assert result["n_rows_ingested"] == expected_rows


def test_report_automation_results_match_manual():
    result = compare_report_generation(TEST_DB, N_ASSETS)
    assert result["results_identical"] is True


def test_automated_report_is_faster_or_comparable():
    result = compare_report_generation(TEST_DB, N_ASSETS)
    assert result["automated_time_sec"] <= result["manual_time_sec"] * 1.5


def test_unified_view_handles_concurrent_engineers():
    result = simulate_concurrent_engineers(TEST_DB, n_engineers=15, n_assets=N_ASSETS)
    assert result["all_queries_succeeded"] is True


def test_ingestion_throughput_is_positive():
    result = ingest_to_sqlite(TEST_DB, N_ASSETS, DURATION_HOURS, SEED)
    assert result["rows_per_sec"] > 0
