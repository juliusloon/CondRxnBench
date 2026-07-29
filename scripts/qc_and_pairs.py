#!/usr/bin/env python3
"""Quality control and exhaustive single-factor pair construction."""
from __future__ import annotations

from itertools import combinations
from pathlib import Path
import json

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "processed" / "ahneman_buchwald_hartwig_main_matrix.csv"
REPORT = ROOT / "reports" / "ahneman_qc_report.md"


def frequency_table(df: pd.DataFrame, factor: str) -> pd.DataFrame:
    return (df.groupby(factor, dropna=False)
            .agg(records=("reaction_id", "size"), missing_yield=("yield_observed", lambda x: int((~x).sum())),
                 zero_yield=("zero_yield", "sum"), zero_yield_rate=("zero_yield", "mean"),
                 median_yield=("yield_percent", "median"))
            .reset_index())


def make_pairs(df: pd.DataFrame) -> pd.DataFrame:
    # `aryl_halide` defines the reaction group. It is deliberately excluded
    # from the condition-cliff table; substrate perturbation is a distinct task.
    factors = ["catalyst_system", "base", "additive"]
    records = []
    observed = df.loc[df.yield_observed].copy()
    for changed in factors:
        fixed = [f for f in factors if f != changed]
        for _, group in observed.groupby(["reaction_group_id", *fixed], dropna=False):
            group = group.sort_values(changed)
            for (_, a), (_, b) in combinations(group.iterrows(), 2):
                changed_fields = [f for f in factors if a[f] != b[f]]
                if len(changed_fields) != 1:
                    continue
                records.append({
                    "pair_id": f"{a.reaction_id}__{b.reaction_id}",
                    "reaction_id_a": a.reaction_id, "reaction_id_b": b.reaction_id,
                    "reaction_group_id": a.reaction_group_id,
                    "changed_factor": changed_fields[0], "n_changed_factors": len(changed_fields),
                    "condition_a": a[changed], "condition_b": b[changed],
                    "yield_a": a.yield_percent, "yield_b": b.yield_percent,
                    "delta_yield": b.yield_percent - a.yield_percent,
                    "abs_delta_yield": abs(b.yield_percent - a.yield_percent),
                })
    pairs = pd.DataFrame(records)
    return pairs.sort_values(["changed_factor", "pair_id"]).reset_index(drop=True)


def to_md_table(df: pd.DataFrame) -> str:
    return df.to_markdown(index=False, floatfmt=".3f")


def main() -> None:
    df = pd.read_csv(DATA)
    factors = ["aryl_halide", "catalyst_system", "base", "additive"]
    expected = 15 * 4 * 3 * 23
    actual_combinations = df[factors].drop_duplicates().shape[0]
    duplicate_combinations = int(df.duplicated(factors).sum())
    missing_wells = int((~df.yield_observed).sum())
    observed = df.loc[df.yield_observed]
    frequency = {factor: frequency_table(df, factor) for factor in factors}
    cross = (df.groupby(factors, dropna=False).agg(records=("reaction_id", "size"),
            observed_yields=("yield_observed", "sum")).reset_index())
    pairs = make_pairs(df)
    pairs.to_csv(ROOT / "data" / "processed" / "ahneman_buchwald_hartwig_single_factor_pairs.csv", index=False)
    for factor, table in frequency.items():
        table.to_csv(ROOT / "reports" / f"ahneman_qc_frequency_{factor}.csv", index=False)
    pair_counts = pairs.changed_factor.value_counts().rename_axis("changed_factor").reset_index(name="pairs")
    delta_quantiles = pairs.groupby("changed_factor").abs_delta_yield.quantile([.5, .75, .9, .95]).unstack().reset_index()
    delta_quantiles.columns = ["changed_factor", "p50", "p75", "p90", "p95"]
    summary = {
        "theoretical_main_cells": expected, "reconstructed_main_cells": int(len(df)),
        "unique_condition_combinations": int(actual_combinations), "duplicate_condition_combinations": duplicate_combinations,
        "missing_analytical_outcomes": missing_wells, "observed_outcomes": int(len(observed)),
        "zero_yield_count": int(observed.zero_yield.sum()), "zero_yield_rate_observed": float(observed.zero_yield.mean()),
        "single_factor_pairs_observed_only": int(len(pairs)), "pair_counts": pair_counts.to_dict("records"),
    }
    (ROOT / "reports" / "ahneman_qc_summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    lines = ["# Ahneman--Doyle HTE: reconstruction QC", "",
             "## Matrix integrity", "",
             f"- Theoretical main factorial cells: **{expected:,}** (15 aryl halides × 4 catalyst systems × 3 bases × 23 additives).",
             f"- Reconstructed main cells: **{len(df):,}**; unique condition combinations: **{actual_combinations:,}**; duplicate combinations: **{duplicate_combinations:,}**.",
             f"- Analytical outcomes missing: **{missing_wells:,}**; observed yields: **{len(observed):,}**.",
             f"- Observed zero yields: **{int(observed.zero_yield.sum()):,}** ({observed.zero_yield.mean():.1%}). Zero is retained as an observed outcome, never recoded as missing.",
             "", "## Field-level frequencies, missingness, and zero yields", ""]
    for factor in factors:
        lines += [f"### {factor}", "", to_md_table(frequency[factor]), ""]
    lines += ["## Cross-combination completeness", "",
              "Every named four-factor combination is represented once in the physical design. Outcome completeness is assessed separately, so an analytical NA cannot masquerade as an absent experiment.", "",
              f"- Design coverage: **{actual_combinations / expected:.1%}**", f"- Outcome coverage: **{len(observed) / expected:.1%}**", "",
              "## Single-factor perturbation pairs", "",
              "Pairs were enumerated before any cliff label or threshold. Both endpoints must have observed yields; all four named factors are compared exactly, and only `n_changed_factors = 1` is retained.", "",
              to_md_table(pair_counts), "", "### Absolute Δyield distribution (percentage points)", "", to_md_table(delta_quantiles), "",
              "No cliff threshold is set in this report. The quantiles are descriptive inputs for a pre-registered threshold decision, not a post hoc sample-selection rule.", ""]
    REPORT.write_text("\n".join(lines))


if __name__ == "__main__":
    main()
