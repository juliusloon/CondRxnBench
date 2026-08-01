#!/usr/bin/env python3
"""Independent, contract-level verifier for baseline candidate artifacts."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "configs" / "benchmark_v0_1_baseline_experiment_contract.json"
OUT = ROOT / "results" / "benchmark_v0_1_baselines_candidate"
PRETEST = ROOT / "metadata" / "benchmark_v0_1_pretest_winner_freeze.jsonl"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def freeze_manifest_hash(rows: list[dict]) -> str:
    ordered = sorted(rows, key=lambda x: (x["source_dataset"], x["split"], x["seed"], x["family"], x["run_id"]))
    return hashlib.sha256("\n".join(row["freeze_sha256"] for row in ordered).encode()).hexdigest()


def jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text().splitlines() if line]


def main() -> None:
    contract = json.loads(CONTRACT.read_text())
    manifest = json.loads((OUT / "manifest.json").read_text())
    assert manifest["status"] == "candidate_not_promoted"
    assert manifest["contract_sha256"] == sha(CONTRACT)

    frozen, materialized = jsonl(PRETEST), jsonl(OUT / "winner_freeze.jsonl")
    assert frozen == materialized, "test output does not exactly match the pre-test freeze"
    assert len(materialized) == 216
    assert manifest["winner_manifest_sha256"] == freeze_manifest_hash(materialized)

    predictions = pd.read_parquet(OUT / "prediction_records.parquet")
    runs = pd.read_parquet(OUT / "run_ledger.parquet")
    controls = pd.read_parquet(OUT / "negative_control_ledger.parquet")
    failures = pd.read_parquet(OUT / "failure_ledger.parquet")
    unsupported = pd.read_parquet(OUT / "unsupported_family_ledger.parquet")
    assert list(failures.columns) == contract["schemas"]["failure_ledger"] and failures.empty
    assert len(runs) == manifest["run_rows"] == 324 and runs.run_id.is_unique
    assert len(controls) == manifest["control_rows"] == 108
    assert len(predictions) == manifest["prediction_rows"] == 239652
    assert set(contract["schemas"]["prediction_records"]).issubset(predictions.columns)
    assert set(contract["schemas"]["run_ledger"]).issubset(runs.columns)
    formal = predictions.loc[predictions.control_type == "none"]
    assert formal.run_id.nunique() == len(materialized) == 216
    assert set(formal.winner_freeze_sha256) == {row["freeze_sha256"] for row in materialized}
    assert len(unsupported) == 4 and set(unsupported.status) == {"not_supported"}
    assert set(controls.control_type) == set(contract["negative_control_coverage"]["required_controls"])
    assert set(runs.status) == {"completed"} and set(predictions.prediction_status) == {"completed"}
    print(json.dumps({"baseline_candidate_verification": "passed", "winner_manifest_sha256": manifest["winner_manifest_sha256"], "formal_runs": 216, "control_runs": 108}, sort_keys=True))


if __name__ == "__main__":
    main()
