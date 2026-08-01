#!/usr/bin/env python3
"""Validate and atomically assemble source×split baseline materialization shards."""
from __future__ import annotations

import hashlib
import json
import shutil
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SHARDS = ROOT / "results" / "benchmark_v0_1_baseline_shards"
OUT = ROOT / "results" / "benchmark_v0_1_baselines_candidate"
SOURCES = ("ahneman_doyle_buchwald_hartwig_2018", "perera_suzuki_miyaura_2018")
SPLITS = ("S0", "S1", "S2", "S3", "S4", "S5")
SEEDS = (20260731, 20260801, 20260802)


def freeze_hash(rows: list[dict]) -> str:
    rows = sorted(rows, key=lambda x: (x["source_dataset"], x["split"], x["seed"], x["family"], x["run_id"]))
    return hashlib.sha256("\n".join(row["freeze_sha256"] for row in rows).encode()).hexdigest()


def main() -> None:
    paths = [SHARDS / source / split / str(seed) for source in SOURCES for split in SPLITS for seed in SEEDS]
    missing = [str(p) for p in paths if not (p / "manifest.json").exists()]
    if missing: raise ValueError("missing complete shards: " + ", ".join(missing))
    manifests = [json.loads((p / "manifest.json").read_text()) for p in paths]
    for key in ("contract_sha256", "split_manifest_sha256", "feature_config_sha256"):
        if len({m[key] for m in manifests}) != 1: raise ValueError(f"inconsistent {key}")
    prediction = pd.concat([pd.read_parquet(p / "prediction_records.parquet") for p in paths], ignore_index=True)
    runs = pd.concat([pd.read_parquet(p / "run_ledger.parquet") for p in paths], ignore_index=True)
    controls = pd.concat([pd.read_parquet(p / "negative_control_ledger.parquet") for p in paths], ignore_index=True)
    failures = pd.concat([pd.read_parquet(p / "failure_ledger.parquet") for p in paths], ignore_index=True)
    unsupported = pd.concat([pd.read_parquet(p / "unsupported_family_ledger.parquet") for p in paths], ignore_index=True).drop_duplicates()
    freezes = [json.loads(line) for p in paths for line in (p / "winner_freeze.jsonl").read_text().splitlines() if line]
    if len(freezes) != 216 or runs.run_id.duplicated().any() or len(runs) != 324: raise ValueError("unexpected duplicate or incomplete formal runs")
    if len(controls) != 108 or len(prediction) != 239652 or len(unsupported) != 4: raise ValueError("unexpected shard row counts")
    staging = OUT.with_name(OUT.name + ".staging")
    if staging.exists(): shutil.rmtree(staging)
    staging.mkdir(parents=True)
    prediction.to_parquet(staging / "prediction_records.parquet", index=False)
    runs.to_parquet(staging / "run_ledger.parquet", index=False)
    failures.iloc[:0].to_parquet(staging / "failure_ledger.parquet", index=False)
    unsupported.to_parquet(staging / "unsupported_family_ledger.parquet", index=False)
    ordered = sorted(freezes, key=lambda x: (x["source_dataset"], x["split"], x["seed"], x["family"], x["run_id"]))
    (staging / "winner_freeze.jsonl").write_text("".join(json.dumps(x, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n" for x in ordered))
    controls.to_parquet(staging / "negative_control_ledger.parquet", index=False)
    manifest = {"status": "candidate_not_promoted", **{key: manifests[0][key] for key in ("contract_sha256", "split_manifest_sha256", "feature_config_sha256")}, "winner_manifest_sha256": freeze_hash(ordered), "prediction_rows": len(prediction), "run_rows": len(runs), "control_rows": len(controls), "assembly": "validated_source_split_shards"}
    (staging / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    if OUT.exists(): shutil.rmtree(OUT)
    staging.replace(OUT)
    print(json.dumps(manifest, sort_keys=True))


if __name__ == "__main__": main()
