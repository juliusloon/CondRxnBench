#!/usr/bin/env python3
"""Verify Core table CSV-to-Parquet round trips without changing release data."""
from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
CORE = ROOT / "data" / "processed" / "core_v0_1"
TABLES = ("reaction_records", "condition_pairs", "condition_registry")
SENTINELS = ("not_reported", "NULL_COMPONENT", "not_assigned")
PRIMARY_KEYS = {
    "reaction_records": "reaction_id",
    "condition_pairs": "pair_id",
    "condition_registry": "component_id",
}


def sentinel_counts(frame: pd.DataFrame) -> dict[str, int]:
    return {
        sentinel: int(frame.eq(sentinel).sum().sum())
        for sentinel in SENTINELS
    }


def main() -> None:
    with TemporaryDirectory(prefix="condrxnbench-parquet-") as directory:
        out = Path(directory)
        for table in TABLES:
            csv_path = CORE / f"{table}.csv"
            parquet_path = out / f"{table}.parquet"
            before = pd.read_csv(csv_path)
            before_sentinels = sentinel_counts(before)
            before_bool = {
                column: before[column].copy()
                for column in before.columns
                if before[column].dtype == bool
            }
            key = PRIMARY_KEYS[table]
            assert before[key].is_unique, (table, key)

            before.to_parquet(parquet_path, index=False, engine="pyarrow")
            after = pd.read_parquet(parquet_path, engine="pyarrow")

            assert before.columns.tolist() == after.columns.tolist(), table
            assert len(before) == len(after), table
            assert before[key].tolist() == after[key].tolist(), table
            assert sentinel_counts(after) == before_sentinels, table
            for column, values in before_bool.items():
                assert after[column].dtype == bool, (table, column, after[column].dtype)
                assert after[column].equals(values), (table, column)
            pd.testing.assert_frame_equal(before, after, check_dtype=False, check_exact=True)
    print("Parquet round-trip verification passed for all Core v0.1 tables.")


if __name__ == "__main__":
    main()
