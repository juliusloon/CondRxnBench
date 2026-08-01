#!/usr/bin/env python3
"""Materialize contract-bound benchmark metrics from frozen baseline predictions.

This is deliberately evaluation-only: it rejects incomplete prediction coverage
and never reads validation values for model selection.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import average_precision_score, f1_score, mean_absolute_error, mean_squared_error, ndcg_score, r2_score, roc_auc_score

ROOT = Path(__file__).resolve().parents[1]
CORE = ROOT / "data" / "processed" / "core_v0_2" / "reaction_records.parquet"
PAIRS = ROOT / "data" / "processed" / "benchmark_v0_1" / "strict_pairs.parquet"
PAIR_SPLITS = ROOT / "data" / "processed" / "benchmark_v0_1_splits_candidate" / "pair_splits.parquet"
FEASIBILITY = ROOT / "metadata" / "benchmark_v0_1_task_split_feasibility_matrix.json"
OUT = ROOT / "results" / "benchmark_v0_1_baselines_candidate"


def canonical_sha(rows: pd.DataFrame, columns: list[str]) -> str:
    payload = rows.loc[:, columns].sort_values(columns).to_json(orient="records", date_format="iso", double_precision=15)
    return hashlib.sha256(payload.encode()).hexdigest()


def corr(a: pd.Series, b: pd.Series, method: str) -> float | None:
    if len(a) < 2 or a.nunique() < 2 or b.nunique() < 2:
        return None
    return float(a.corr(b, method=method))


def direction(v: pd.Series) -> pd.Series:
    return pd.Series(np.select([v < -10.0, v > 10.0], ["decrease", "increase"], default="invariant"), index=v.index)


def add(rows: list[dict], base: dict, task: str, metric: str, value: float | None, reason: str | None = None) -> None:
    rows.append({**base, "task": task, "metric_name": metric, "metric_value": value, "status": "completed" if value is not None else "not_supported", "reason": reason})


def main() -> None:
    predictions = pd.read_parquet(OUT / "prediction_records.parquet")
    records = pd.read_parquet(CORE)
    pairs = pd.read_parquet(PAIRS)
    pair_splits = pd.read_parquet(PAIR_SPLITS)
    feasible = json.loads(FEASIBILITY.read_text())["leaves"]
    formal = predictions.loc[predictions.control_type == "none"].copy()
    # Core stores the source-scoped design grouping as ``reaction_group_id``;
    # all metric groups are already source-stratified below.
    records = records.loc[(records.record_class == "main_matrix") & records.yield_observed.astype(bool), ["reaction_id", "source_dataset", "yield_type", "yield_percent", "reaction_group_id"]].rename(columns={"reaction_group_id": "design_group_id"})
    merged = formal.merge(records, on=["reaction_id", "source_dataset", "yield_type"], validate="many_to_one")
    if len(merged) != len(formal) or merged.yield_percent.isna().any():
        raise ValueError("formal predictions do not have complete, source-matched observed labels")
    rows: list[dict] = []
    group_cols = ["source_dataset", "yield_type", "split", "seed", "family", "run_id"]
    for key, d in merged.groupby(group_cols, sort=True):
        source, yield_type, split, seed, family, run_id = key
        base = {"source_dataset": source, "yield_type": yield_type, "split": split, "seed": int(seed), "family": family, "run_id": run_id,
                "prediction_sha256": canonical_sha(d, ["reaction_id", "y_pred"])}
        truth, pred = d.yield_percent, d.y_pred
        add(rows, base, "Task1_absolute_yield", "mae", float(mean_absolute_error(truth, pred)))
        add(rows, base, "Task1_absolute_yield", "rmse", float(mean_squared_error(truth, pred) ** 0.5))
        add(rows, base, "Task1_absolute_yield", "r2", float(r2_score(truth, pred)) if truth.nunique() > 1 else None, "constant_truth" if truth.nunique() < 2 else None)
        var = d.groupby("design_group_id").apply(lambda x: x.y_pred.var(ddof=0) / x.yield_percent.var(ddof=0) if len(x) > 1 and x.yield_percent.var(ddof=0) > 0 else np.nan, include_groups=False).dropna()
        add(rows, base, "Task1_absolute_yield", "within_group_variance_ratio", float(var.mean()) if len(var) else None, "no_group_with_nonzero_observed_variance" if not len(var) else None)
        # Task 7 is an OOD reporting view; it repeats the source-stratified Task 1 MAE without claiming a new model head.
        add(rows, base, "Task7_OOD_framework", "underlying_task1_mae", float(mean_absolute_error(truth, pred)))

        lookup = d.set_index("reaction_id").y_pred
        ps = pair_splits.loc[(pair_splits.source_dataset == source) & (pair_splits.split == split) & (pair_splits.partition == "test"), ["pair_id"]]
        p = pairs.loc[pairs.source_dataset == source].merge(ps, on="pair_id", validate="one_to_one")
        p["pred_a"], p["pred_b"] = p.reaction_id_a.map(lookup), p.reaction_id_b.map(lookup)
        if p[["pred_a", "pred_b"]].isna().any().any():
            raise ValueError(f"incomplete test prediction coverage for {run_id}")
        p["pred_delta"] = p.pred_b - p.pred_a
        true_delta, pred_delta = p.delta_yield, p.pred_delta
        pair_base = {**base, "prediction_sha256": canonical_sha(p, ["pair_id", "pred_delta"])}
        add(rows, pair_base, "Task2_delta_yield", "delta_mae", float(mean_absolute_error(true_delta, pred_delta)))
        add(rows, pair_base, "Task2_delta_yield", "delta_rmse", float(mean_squared_error(true_delta, pred_delta) ** 0.5))
        add(rows, pair_base, "Task2_delta_yield", "delta_pearson", corr(true_delta, pred_delta, "pearson"), "constant_or_too_small" if corr(true_delta, pred_delta, "pearson") is None else None)
        add(rows, pair_base, "Task2_delta_yield", "delta_spearman", corr(true_delta, pred_delta, "spearman"), "constant_or_too_small" if corr(true_delta, pred_delta, "spearman") is None else None)
        observed_dir, predicted_dir = direction(true_delta), direction(pred_delta)
        add(rows, pair_base, "Task3_direction", "direction_accuracy", float((observed_dir == predicted_dir).mean()))
        add(rows, pair_base, "Task3_direction", "direction_macro_f1", float(f1_score(observed_dir, predicted_dir, labels=["decrease", "invariant", "increase"], average="macro", zero_division=0)))
        add(rows, pair_base, "Task2_delta_yield", "sensitivity_ratio", float(pred_delta.abs().mean() / true_delta.abs().mean()) if true_delta.abs().mean() else None, "zero_observed_delta_denominator" if not true_delta.abs().mean() else None)
        factor_mae = p.groupby("changed_factor", sort=True).apply(lambda x: mean_absolute_error(x.delta_yield, x.pred_delta), include_groups=False)
        add(rows, pair_base, "Task2_delta_yield", "factor_wise_sensitivity", float(factor_mae.mean()) if len(factor_mae) else None, "empty_pair_set" if not len(factor_mae) else None)
        strong = (p.abs_delta_yield >= 30.0).astype(int)
        score = (p.pred_delta.abs() / 30.0).clip(0.0, 1.0)
        add(rows, pair_base, "Task4_cliff", "cliff_auprc", float(average_precision_score(strong, score)) if strong.nunique() == 2 else None, "single_class_cliff" if strong.nunique() < 2 else None)
        add(rows, pair_base, "Task4_cliff", "cliff_auroc", float(roc_auc_score(strong, score)) if strong.nunique() == 2 else None, "single_class_cliff" if strong.nunique() < 2 else None)
        add(rows, pair_base, "Task4_cliff", "cliff_f1", float(f1_score(strong, score >= 0.5, zero_division=0)))

        if split == "S1":
            rank_groups = [x for _, x in d.groupby("design_group_id", sort=True) if len(x) >= 2]
            ndcgs, rank_spearmans, regrets = [], [], []
            topk = {1: [], 3: [], 5: []}
            for x in rank_groups:
                truth_x, pred_x = x.yield_percent.to_numpy(), x.y_pred.to_numpy()
                ndcgs.append(float(ndcg_score([truth_x], [pred_x])))
                # pandas uses average ranks for tied values, as frozen in the
                # Task 5 contract.  Selection below is separately lexical.
                rho = corr(x.yield_percent, x.y_pred, "spearman")
                if rho is not None: rank_spearmans.append(rho)
                order = np.lexsort((x.reaction_id.to_numpy(), -pred_x))
                regrets.append(float(truth_x.max() - truth_x[order[0]]))
                for k in topk:
                    topk[k].append(float(truth_x[order[:min(k, len(order))]].max() == truth_x.max()))
            add(rows, base, "Task5_ranking", "ndcg", float(np.mean(ndcgs)) if ndcgs else None, "no_group_with_two_test_candidates" if not ndcgs else None)
            add(rows, base, "Task5_ranking", "spearman", float(np.mean(rank_spearmans)) if rank_spearmans else None, "all_ranking_groups_constant_or_too_small" if not rank_spearmans else None)
            for k, values in topk.items(): add(rows, base, "Task5_ranking", f"top_{k}_recall", float(np.mean(values)) if values else None, "no_group_with_two_test_candidates" if not values else None)
            add(rows, base, "Task6_recommendation", "regret", float(np.mean(regrets)) if regrets else None, "no_group_with_two_test_candidates" if not regrets else None)
            for k, values in topk.items(): add(rows, base, "Task6_recommendation", f"top_{k}_contains_group_optimum", float(np.mean(values)) if values else None, "no_group_with_two_test_candidates" if not values else None)

    # The coverage matrix is part of the release contract.  Mirror every
    # explicitly non-supported task/split in the leaderboard so an omitted
    # metric can never be mistaken for an unreported successful result.
    feasibility_by_key = {(x["source_dataset"], x["task"], x["split"]): x for x in feasible}
    formal_runs = merged.loc[:, group_cols].drop_duplicates().to_dict("records")
    for run in formal_runs:
        for task in ("Task5_ranking", "Task6_recommendation"):
            entry = feasibility_by_key[(run["source_dataset"], task, run["split"])]
            if entry["status"] != "supported":
                rows.append({"source_dataset": run["source_dataset"], "yield_type": merged.loc[(merged.run_id == run["run_id"]) & (merged.source_dataset == run["source_dataset"]), "yield_type"].iloc[0],
                             "task": task, "split": run["split"], "seed": int(run["seed"]), "family": run["family"], "run_id": run["run_id"],
                             "metric_name": "not_applicable", "metric_value": None, "status": "not_supported", "reason": entry["reason"], "prediction_sha256": None})
    result = pd.DataFrame(rows, columns=["source_dataset", "yield_type", "task", "split", "seed", "family", "run_id", "metric_name", "metric_value", "status", "reason", "prediction_sha256"])
    result.to_parquet(OUT / "leaderboard.parquet", index=False)
    complete = result.loc[result.status == "completed"]
    summary = complete.groupby(["source_dataset", "yield_type", "task", "split", "family", "metric_name"], as_index=False).agg(metric_mean=("metric_value", "mean"), metric_std=("metric_value", "std"), n_seeds=("seed", "nunique"))
    summary.to_parquet(OUT / "leaderboard_summary.parquet", index=False)
    ledger = pd.DataFrame(feasible)
    ledger.to_parquet(OUT / "task_split_coverage_ledger.parquet", index=False)
    manifest = json.loads((OUT / "manifest.json").read_text())
    manifest["metric_rows"] = len(result)
    manifest["metric_summary_rows"] = len(summary)
    manifest["metric_materialization"] = "evaluation_only_from_frozen_predictions"
    (OUT / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"metric_rows": len(result), "metric_summary_rows": len(summary)}, sort_keys=True))


if __name__ == "__main__":
    main()
