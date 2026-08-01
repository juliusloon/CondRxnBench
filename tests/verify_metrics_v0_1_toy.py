#!/usr/bin/env python3
"""Executable toy/boundary/negative checks for the frozen metric contract."""
from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np
from scipy.stats import pearsonr, rankdata, spearmanr
from sklearn.metrics import accuracy_score, average_precision_score, f1_score, mean_absolute_error, mean_squared_error, ndcg_score, r2_score, roc_auc_score

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "tests" / "fixtures" / "metrics_v0_1_toy_cases.json"


def not_supported_if(condition: bool) -> str | None:
    return "not_supported_with_reason" if condition else None


def validate_numeric_input(y: list[float], p: list[float | None]) -> str | None:
    if not y:
        return "not_supported_with_reason"
    return "reject_input" if len(y) != len(p) or any(value is None for value in p) else None


def direction(delta: float) -> str:
    return "decrease" if delta < -10 else "increase" if delta > 10 else "invariant"


def corr(y: list[float], p: list[float]) -> float | str:
    if len(y) < 2 or len(set(y)) < 2 or len(set(p)) < 2:
        return "not_supported_with_reason"
    return float(spearmanr(y, p).statistic)


def pearson_contract(y: list[float], p: list[float]) -> float | str:
    if len(y) < 2 or len(set(y)) < 2 or len(set(p)) < 2:
        return "not_supported_with_reason"
    return float(pearsonr(y, p).statistic)


def r2_contract(y: list[float], p: list[float]) -> float | str:
    return "not_supported_with_reason" if len(y) < 2 or len(set(y)) < 2 else float(r2_score(y, p))


def top_k_recall(optimum: set[str], predicted: list[str], k: int) -> float | str:
    return "not_supported_with_reason" if not optimum or not predicted or k < 1 else float(bool(optimum & set(predicted[:k])))


def sensitivity_ratio(observed: list[float], predicted: list[float]) -> float | str:
    denominator = float(np.mean(np.abs(observed)))
    return "not_supported_with_reason" if denominator == 0 else float(np.mean(np.abs(predicted)) / denominator)


def direction_macro_f1(true: list[str], pred: list[str]) -> float | str:
    labels = {"decrease", "invariant", "increase"}
    return "not_supported_with_reason" if not labels <= set(true) else float(f1_score(true, pred, labels=sorted(labels), average="macro", zero_division=0))


def cliff_metrics(y: list[int], score: list[float]) -> dict[str, float | str]:
    if len(set(y)) < 2:
        return {"auprc": "not_supported_with_reason", "auroc": "not_supported_with_reason", "f1": "not_supported_with_reason"}
    return {"auprc": float(average_precision_score(y, score)), "auroc": float(roc_auc_score(y, score)), "f1": float(f1_score(y, [x >= 0.5 for x in score], zero_division=0))}


def main() -> None:
    fixture = json.loads(FIXTURE.read_text())
    # Input rejection / error metrics / correlation edge behavior.
    assert validate_numeric_input(fixture["empty"]["y_true"], fixture["empty"]["y_pred"]) == fixture["empty"]["expected"]
    assert validate_numeric_input(fixture["missing_prediction"]["y_true"], fixture["missing_prediction"]["y_pred"]) == fixture["missing_prediction"]["expected"]
    numeric = fixture["numeric_metrics"]; y, p = numeric["y_true"], numeric["y_pred"]
    assert mean_absolute_error(y, p) == numeric["mae"] and math.isclose(mean_squared_error(y, p) ** 0.5, numeric["rmse"])
    assert r2_contract(y, p) == numeric["r2"]
    assert r2_contract([1, 1], [1, 2]) == fixture["constant_truth"]["expected_r2"]
    assert corr([1, 1], [1, 2]) == "not_supported_with_reason"
    assert math.isclose(float(corr(y, p)), numeric["spearman"])
    assert math.isclose(float(pearson_contract(y, p)), numeric["pearson"])
    distinct = fixture["pearson_spearman_distinct"]; assert math.isclose(float(pearson_contract(distinct["truth"], distinct["pred"])), distinct["pearson"]) and math.isclose(float(corr(distinct["truth"], distinct["pred"])), distinct["spearman"]) and distinct["pearson"] != distinct["spearman"]
    constant_p = fixture["pearson_constant_prediction"]; assert pearson_contract(constant_p["truth"], constant_p["pred"]) == constant_p["expected"]
    # Direction and cliff boundaries including 20/40 sensitivity nesting.
    assert [direction(x) for x in fixture["direction_boundaries_-10_0_10"]["delta"]] == fixture["direction_boundaries_-10_0_10"]["expected"]
    cliff = fixture["cliff_boundaries_10_20_30_40"]
    got_primary = ["invariant" if x <= 10 else "moderate" if x < 30 else "strong" for x in cliff["abs_delta"]]
    assert got_primary == cliff["primary"]
    assert [x >= 20 for x in cliff["abs_delta"]] == cliff["strong_20"] and [x >= 40 for x in cliff["abs_delta"]] == cliff["strong_40"]
    assert all(not b or a for a, b in zip(cliff["strong_20"], cliff["strong_40"]))
    single = cliff_metrics(fixture["single_class_cliff"]["y_true"], [0.1, 0.2]); assert single == {"auprc": fixture["single_class_cliff"]["expected_auprc"], "auroc": fixture["single_class_cliff"]["expected_auroc"], "f1": fixture["single_class_cliff"]["expected_f1"]}
    binary = fixture["cliff_binary"]; metrics = cliff_metrics(binary["true"], binary["score"]); assert all(metrics[key] == binary[key] for key in metrics)
    direction_case = fixture["direction_macro_f1"]; assert accuracy_score(direction_case["true"], direction_case["pred"]) == direction_case["accuracy"] and math.isclose(direction_macro_f1(direction_case["true"], direction_case["pred"]), direction_case["macro_f1"])
    absent = fixture["direction_absent_class"]; assert direction_macro_f1(absent["true"], absent["pred"]) == absent["expected"]
    # Ranking, NDCG, top-k group optimum and regret, including tied optima.
    tied = fixture["ranking_tie"]; assert rankdata([-x for x in tied["observed"]], method="average").tolist() == tied["expected_rank"]
    rank_case = fixture["ranking_ndcg_topk"]; assert ndcg_score([rank_case["truth"]], [rank_case["score"]], k=3) == rank_case["ndcg"] and top_k_recall({"R1"}, ["R1", "R2"], 1) == rank_case["top_k_recall"]
    opt = fixture["recommendation_multiple_optima"]; assert top_k_recall(set(opt["reaction_id"]), opt["predicted_ids"], opt["k"]) == opt["expected"]
    regret = fixture["recommendation_regret"]; assert max(regret["observed"]) - regret["observed"][regret["predicted_order"][0]] == regret["regret"] and regret["top_1_hit"] == 0
    # Direct-delta sensitivity ratio, endpoint-yield variance ratio, factor-wise delta MAE.
    positive = fixture["sensitivity_positive"]; assert sensitivity_ratio(positive["observed_delta"], positive["predicted_delta"]) == positive["expected"]
    assert sensitivity_ratio(fixture["sensitivity_zero_denominator"]["observed_delta"], fixture["sensitivity_zero_denominator"]["predicted_delta"]) == fixture["sensitivity_zero_denominator"]["expected"]
    topk = fixture["top_k_recall"]; assert top_k_recall(set(topk["truth_optimum_ids"]), topk["predicted_ids"], topk["k"]) == topk["expected"]
    observed_y, predicted_y = np.array([1.0, 3.0, 2.0, 4.0]), np.array([1.0, 2.0, 2.0, 3.0])
    variance = fixture["variance_ratio_multi_group"]; assert math.isclose(np.mean([np.var(x) for x in variance["predicted"]]) / np.mean([np.var(x) for x in variance["observed"]]), variance["ratio"])
    factor = fixture["factor_macro_sensitivity"]; assert math.isclose(np.mean([mean_absolute_error(a, b) for a, b in zip(factor["observed"], factor["predicted"])]), factor["macro"])
    print("Benchmark v0.1 metric toy/boundary/negative verification passed.")


if __name__ == "__main__":
    main()
