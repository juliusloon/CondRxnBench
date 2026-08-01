#!/usr/bin/env python3
"""Contract-bound baseline materialization for Benchmark v0.1 candidates."""
from __future__ import annotations

import argparse
import hashlib, json, shutil
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

from benchmark_v0_1_baseline_features import canonical_condition_tuple, load_config

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "configs" / "benchmark_v0_1_baseline_experiment_contract.json"
CORE = ROOT / "data" / "processed" / "core_v0_2" / "reaction_records.parquet"
SPLITS = ROOT / "data" / "processed" / "benchmark_v0_1_splits_candidate"
OUT = ROOT / "results" / "benchmark_v0_1_baselines_candidate"
STAGING = OUT.with_name(OUT.name + ".staging")
PRETEST_FREEZE = ROOT / "metadata" / "benchmark_v0_1_pretest_winner_freeze.jsonl"
SOURCES = ("ahneman_doyle_buchwald_hartwig_2018", "perera_suzuki_miyaura_2018")

def sha(p: Path) -> str: return hashlib.sha256(p.read_bytes()).hexdigest()
def canon(x: object) -> str: return json.dumps(x, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
def digest(x: object) -> str: return hashlib.sha256(canon(x).encode()).hexdigest()

def model(family: str, candidate: dict, columns: list[str], seed: int):
    if family.endswith("ridge"):
        estimator = Ridge(alpha=candidate["alpha"], random_state=seed)
    else:
        estimator = RandomForestRegressor(n_estimators=candidate["n_estimators"], max_depth=candidate["max_depth"], random_state=seed, n_jobs=1)
    return Pipeline([("encode", ColumnTransformer([("categorical", OneHotEncoder(handle_unknown="ignore", sparse_output=False), columns)])), ("model", estimator)])

def candidates(spec: dict) -> list[dict]:
    if spec["kind"] == "mean" or spec["kind"] == "training_only_lookup": return [{"id": "default"}]
    if spec["kind"] == "ridge": return [{"id": f"alpha={x}", "alpha": x} for x in spec["alpha"]]
    return [{"id": f"trees={n};depth={d}", "n_estimators": n, "max_depth": d} for n in spec["n_estimators"] for d in spec["max_depth"]]

def predict_mean(family: str, train: pd.DataFrame, target: pd.DataFrame) -> tuple[np.ndarray, list[str]]:
    source_mean = float(train.yield_percent.mean())
    if family == "source_mean": return np.repeat(source_mean, len(target)), ["source_train_mean"] * len(target)
    lookup = train.groupby(["strict_reaction_group_id", "condition_tuple"], dropna=False).yield_percent.mean().to_dict()
    values, reason = [], []
    for row in target.itertuples(index=False):
        value = lookup.get((row.strict_reaction_group_id, row.condition_tuple))
        values.append(source_mean if value is None else value); reason.append("source_train_mean" if value is None else "group_condition_train_lookup")
    return np.asarray(values), reason

def freeze_row(row: dict) -> dict:
    payload = {k: row[k] for k in row if k != "freeze_sha256"}
    row["freeze_sha256"] = digest(payload); return row

def winner_manifest_hash(rows: list[dict]) -> str:
    """Contract hash: ordered row hashes, not raw JSONL serialization bytes."""
    ordered = sorted(rows, key=lambda x: (x["source_dataset"], x["split"], x["seed"], x["family"], x["run_id"]))
    return hashlib.sha256("\n".join(row["freeze_sha256"] for row in ordered).encode()).hexdigest()

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", choices=SOURCES)
    parser.add_argument("--split", choices=("S0", "S1", "S2", "S3", "S4", "S5"))
    parser.add_argument("--seed", type=int, choices=(20260731, 20260801, 20260802))
    parser.add_argument("--out-dir", type=Path, default=OUT)
    parser.add_argument("--skip-existing", action="store_true")
    parser.add_argument("--write-direct", action="store_true", help="Only for disposable, independently verified shards.")
    args = parser.parse_args()
    target = args.out_dir if args.out_dir.is_absolute() else ROOT / args.out_dir
    staging = target.with_name(target.name + ".staging")
    if args.skip_existing and (target / "manifest.json").exists():
        print(json.dumps({"status": "skipped_existing_complete_shard", "out_dir": str(target)})); return
    contract = json.loads(CONTRACT.read_text())
    if contract["status"] != "accepted_for_baseline_materialization_2026-07-31": raise ValueError("baseline contract not accepted")
    feature = load_config(); config_sha, split_sha, feature_sha = sha(CONTRACT), sha(SPLITS / "manifest.json"), sha(Path(feature["records"]).resolve() if Path(feature["records"]).is_absolute() else ROOT / feature["records"])
    if contract["feature_contract"]["sha256"] != sha(ROOT / contract["feature_contract"]["path"]): raise ValueError("feature config hash mismatch")
    if not PRETEST_FREEZE.exists(): raise ValueError("pre-test winner freeze is required before test materialization")
    frozen = {row["run_id"]: row for row in (json.loads(line) for line in PRETEST_FREEZE.read_text().splitlines() if line)}
    records = pd.read_parquet(CORE); records = records.loc[(records.record_class == "main_matrix") & records.yield_observed.astype(bool)].copy()
    records["strict_reaction_group_id"] = records.source_dataset + "::" + records.reaction_group_id
    records["condition_tuple"] = records.apply(lambda row: canonical_condition_tuple(row.condition_component_refs, feature["roles"][row.source_dataset]), axis=1)
    assignments = pd.read_parquet(SPLITS / "record_splits.parquet")
    # Materialize in a sibling staging directory.  A long CPU run must never
    # erase a previously auditable candidate merely because it is interrupted
    # before the final manifest write.
    if args.write_direct:
        if target.exists(): shutil.rmtree(target)
        target.mkdir(parents=True)
        out = target
    else:
        if staging.exists(): shutil.rmtree(staging)
        staging.mkdir(parents=True)
        out = staging
    predictions, runs, freezes, controls, failures, unsupported = [], [], [], [], [], []
    selected_sources = (args.source,) if args.source else SOURCES
    selected_splits = (args.split,) if args.split else tuple(sorted(assignments["split"].unique()))
    selected_seeds = (args.seed,) if args.seed is not None else tuple(contract["seeds"])
    for source in selected_sources:
      for family, detail in contract["family_eligibility"][source].items():
        if detail["status"] == "not_supported":
          unsupported.append({"source_dataset": source, "family": family, "status": "not_supported", "reason": detail["reason"], "evidence_path": detail["evidence_path"], "source_data_version": detail["source_data_version"]})
    for source in selected_sources:
      for split in selected_splits:
        assigned = assignments.loc[(assignments.source_dataset == source) & (assignments["split"] == split), ["reaction_id", "partition"]]
        data = records.loc[records.source_dataset == source].merge(assigned, on="reaction_id", validate="one_to_one")
        roles = feature["roles"][source]
        for seed in selected_seeds:
          for family, spec in contract["families"].items():
            if contract["family_eligibility"][source][family]["status"] != "supported": continue
            cols = roles if family.startswith("condition_only") else (["strict_reaction_group_id"] + roles if family.startswith("full_categorical") else [])
            train, val, test = (data.loc[data.partition == part].copy() for part in ("train", "val", "test"))
            best = None
            for candidate in candidates(spec):
              if spec["kind"] in {"mean", "training_only_lookup"}: pred, _ = predict_mean(family, train, val)
              else:
                m = model(family, candidate, cols, seed); m.fit(train[cols], train.yield_percent); pred = m.predict(val[cols])
              score = mean_absolute_error(val.yield_percent, pred)
              token = (score, candidate["id"])
              if best is None or token < best[0]: best = (token, candidate)
            candidate = best[1]
            run_id = digest({"contract": config_sha, "split": split_sha, "feature": contract["feature_contract"]["sha256"], "source": source, "split_name": split, "seed": seed, "family": family, "candidate": candidate["id"], "control": "none"})
            winner = freeze_row({"run_id": run_id, "source_dataset": source, "split": split, "seed": seed, "family": family, "candidate_id": candidate["id"], "candidate_config_sha256": digest(candidate), "feature_config_sha256": contract["feature_contract"]["sha256"], "train_record_ids_sha256": digest(sorted(train.reaction_id)), "val_record_ids_sha256": digest(sorted(val.reaction_id)), "val_metric_name": "mae", "val_metric_value": float(best[0][0]), "winner_reason": "lowest_val_mae_then_canonical_candidate_id"})
            if frozen.get(run_id) != winner: raise ValueError(f"winner differs from pre-test freeze: {run_id}")
            freezes.append(winner)
            final = pd.concat([train, val])
            if spec["kind"] in {"mean", "training_only_lookup"}: pred, fallback = predict_mean(family, final, test)
            else:
                m = model(family, candidate, cols, seed); m.fit(final[cols], final.yield_percent); pred = m.predict(test[cols]); fallback = ["not_applicable"] * len(test)
            for row, value, why in zip(test.itertuples(index=False), pred, fallback): predictions.append({"run_id": run_id, "winner_freeze_sha256": winner["freeze_sha256"], "source_dataset": source, "yield_type": row.yield_type, "split": split, "seed": seed, "family": family, "candidate_id": candidate["id"], "control_type": "none", "reaction_id": row.reaction_id, "partition": "test", "y_pred": float(value), "prediction_status": "completed", "fallback_reason": why, "split_manifest_sha256": split_sha, "input_manifest_sha256": sha(CORE), "feature_config_sha256": contract["feature_contract"]["sha256"]})
            runs.append({"run_id": run_id, "source_dataset": source, "split": split, "seed": seed, "family": family, "candidate_id": candidate["id"], "control_type": "none", "status": "completed", "command": "scripts/run_benchmark_v0_1_baselines.py", "environment_sha256": sha(ROOT / contract["environment"]["requirements_path"]), "feature_config_sha256": contract["feature_contract"]["sha256"], "started_at": "deterministic_local", "finished_at": "deterministic_local"})
          # Required controls use a fixed valid family and are logged independently.
          for control in contract["negative_control_coverage"]["required_controls"]:
            control_id = digest({"source":source,"split":split,"seed":seed,"control":control})
            if control == "constant_predictor":
                control_pred = np.repeat(float(train.yield_percent.mean()), len(test))
            else:
                control_train = train.copy(); rng = np.random.default_rng(seed)
                if control == "shuffled_y_train_only": control_train["yield_percent"] = rng.permutation(control_train.yield_percent.to_numpy())
                elif control == "shuffled_condition_train_only": control_train[cols] = control_train[cols].iloc[rng.permutation(len(control_train))].to_numpy()
                control_model = model("full_categorical_ridge", {"alpha": 1.0}, cols, seed)
                control_model.fit(control_train[cols], control_train.yield_percent); control_pred = control_model.predict(test[cols])
            for row, value in zip(test.itertuples(index=False), control_pred): predictions.append({"run_id": control_id, "winner_freeze_sha256": "negative_control_no_winner", "source_dataset": source, "yield_type": row.yield_type, "split": split, "seed": seed, "family": "full_categorical_ridge", "candidate_id": "alpha=1.0", "control_type": control, "reaction_id": row.reaction_id, "partition": "test", "y_pred": float(value), "prediction_status": "completed", "fallback_reason": "negative_control", "split_manifest_sha256": split_sha, "input_manifest_sha256": sha(CORE), "feature_config_sha256": contract["feature_contract"]["sha256"]})
            runs.append({"run_id": control_id, "source_dataset": source, "split": split, "seed": seed, "family": "full_categorical_ridge", "candidate_id": "alpha=1.0", "control_type": control, "status": "completed", "command": "scripts/run_benchmark_v0_1_baselines.py", "environment_sha256": sha(ROOT / contract["environment"]["requirements_path"]), "feature_config_sha256": contract["feature_contract"]["sha256"], "started_at": "deterministic_local", "finished_at": "deterministic_local"})
            controls.append({"run_id": control_id, "source_dataset":source,"split":split,"seed":seed,"family":"full_categorical_ridge","control_type":control,"status":"completed","reason":"actual_test_predictions_materialized"})
    pd.DataFrame(predictions).to_parquet(out / "prediction_records.parquet", index=False)
    pd.DataFrame(runs).to_parquet(out / "run_ledger.parquet", index=False)
    pd.DataFrame(failures, columns=["run_id", "status", "failure_reason", "log_path"]).to_parquet(out / "failure_ledger.parquet", index=False)
    pd.DataFrame(unsupported).to_parquet(out / "unsupported_family_ledger.parquet", index=False)
    freezes = sorted(freezes, key=lambda x: (x["source_dataset"],x["split"],x["seed"],x["family"],x["run_id"]))
    (out / "winner_freeze.jsonl").write_text("".join(canon(row)+"\n" for row in freezes))
    pd.DataFrame(controls).to_parquet(out / "negative_control_ledger.parquet", index=False)
    manifest = {"status":"candidate_not_promoted","contract_sha256":config_sha,"split_manifest_sha256":split_sha,"feature_config_sha256":contract["feature_contract"]["sha256"],"winner_manifest_sha256":winner_manifest_hash(freezes),"prediction_rows":len(predictions),"run_rows":len(runs),"control_rows":len(controls)}
    (out / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True)+"\n")
    if not args.write_direct:
        if target.exists(): shutil.rmtree(target)
        staging.replace(target)
    print(json.dumps(manifest, indent=2))

if __name__ == "__main__": main()
