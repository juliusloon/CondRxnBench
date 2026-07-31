#!/usr/bin/env python3
"""Audit Perera Suzuki--Miyaura HTE data and enumerate single-factor pairs."""
from __future__ import annotations

from itertools import combinations
import json
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "data" / "processed" / "perera_suzuki_miyaura_main_matrix.csv"
REPORT = ROOT / "reports" / "Suzuki-Miyaura-HTE" / "perera_qc_report.md"
PAIR_OUTPUT = ROOT / "data" / "processed" / "perera_suzuki_miyaura_single_factor_pairs.csv"
SUMMARY = ROOT / "reports" / "Suzuki-Miyaura-HTE" / "perera_qc_summary.json"
FACTORS = ["ligand", "base", "solvent_1"]


def frequency_table(df: pd.DataFrame, factor: str) -> pd.DataFrame:
    return (df.groupby(factor, dropna=False)
            .agg(records=("reaction_id", "size"), zero_yield=("zero_yield", "sum"),
                 zero_yield_rate=("zero_yield", "mean"), median_yield=("yield_percent", "median"))
            .reset_index())


def make_pairs(df: pd.DataFrame) -> pd.DataFrame:
    """Enumerate every pair sharing a substrate group and two fixed factors."""
    records: list[dict[str, object]] = []
    observed = df.loc[df["yield_observed"]].copy()
    for changed_factor in FACTORS:
        fixed = [factor for factor in FACTORS if factor != changed_factor]
        for _, group in observed.groupby(["reaction_group_id", *fixed], dropna=False):
            group = group.sort_values([changed_factor, "reaction_id"])
            for (_, left), (_, right) in combinations(group.iterrows(), 2):
                changed = [factor for factor in FACTORS if left[factor] != right[factor]]
                if changed != [changed_factor]:
                    continue
                records.append({
                    "pair_id": f"{left.reaction_id}__{right.reaction_id}",
                    "reaction_id_a": left.reaction_id, "reaction_id_b": right.reaction_id,
                    "reaction_group_id": left.reaction_group_id, "changed_factor": changed_factor,
                    "n_changed_factors": 1, "condition_a": left[changed_factor],
                    "condition_b": right[changed_factor], "yield_a": left.yield_percent,
                    "yield_b": right.yield_percent,
                    "delta_yield": right.yield_percent - left.yield_percent,
                    "abs_delta_yield": abs(right.yield_percent - left.yield_percent),
                })
    return pd.DataFrame(records).sort_values(["changed_factor", "pair_id"]).reset_index(drop=True)


def markdown_table(df: pd.DataFrame) -> str:
    return df.to_markdown(index=False, floatfmt=".3f")


def main() -> None:
    df = pd.read_csv(DATA)
    assert len(df) == 5760 and df["reaction_id"].is_unique
    assert df["yield_observed"].all() and df["zero_yield"].sum() == 275
    assert df["reaction_group_id"].nunique() == 15
    assert (df.groupby("reaction_group_id").size() == 384).all()
    assert not df.duplicated(["reaction_group_id", *FACTORS]).any()

    pairs = make_pairs(df)
    expected_counts = {"ligand": 31680, "base": 20160, "solvent_1": 8640}
    actual_counts = pairs["changed_factor"].value_counts().to_dict()
    assert actual_counts == expected_counts, actual_counts
    assert len(pairs) == sum(expected_counts.values()) and pairs["n_changed_factors"].eq(1).all()
    pairs.to_csv(PAIR_OUTPUT, index=False)

    frequencies = {factor: frequency_table(df, factor) for factor in FACTORS}
    pair_counts = (pairs.groupby("changed_factor").size().rename("pairs").reset_index()
                   .sort_values("changed_factor"))
    quantiles = (pairs.groupby("changed_factor")["abs_delta_yield"].quantile([.5, .75, .9, .95])
                 .unstack().reset_index().rename(columns={.5: "p50", .75: "p75", .9: "p90", .95: "p95"}))
    summary = {
        "records": int(len(df)), "reaction_groups": int(df["reaction_group_id"].nunique()),
        "observed_yields": int(df["yield_observed"].sum()), "zero_yields": int(df["zero_yield"].sum()),
        "pair_counts": {key: int(value) for key, value in actual_counts.items()},
        "total_single_factor_pairs": int(len(pairs)),
    }
    SUMMARY.write_text(json.dumps(summary, indent=2) + "\n")

    lines = [
        "# Perera Suzuki--Miyaura HTE: reconstruction QC", "", "## Matrix integrity", "",
        "- The design is **15 substrate pairs × 12 ligand settings × 8 base settings × 4 carrier solvents = 5,760** records.",
        f"- Reconstructed records: **{len(df):,}**; substrate reaction groups: **{df['reaction_group_id'].nunique()}**; duplicate normalized condition combinations: **{int(df.duplicated(['reaction_group_id', *FACTORS]).sum())}**.",
        f"- Analytical outcomes observed: **{int(df['yield_observed'].sum()):,}**; observed zero yields: **{int(df['zero_yield'].sum()):,}** ({df['zero_yield'].mean():.1%}). Zero is retained as an observation.",
        "- Literal `None` in Data File S1 is encoded as `NULL_COMPONENT`, not missingness.",
        "- `MeOH/H2O_V2 9:1` → `MeOH` and `THF_V2` → `THF` only for the normalized carrier-solvent field. The raw label remains in `solvent_1_raw`; the supporting PDF specifies a four-solvent 9:1 organic/water design.",
        "", "## Field-level frequencies and response distribution", "",
    ]
    for factor, table in frequencies.items():
        lines.extend([f"### {factor}", "", markdown_table(table), ""])
    lines.extend([
        "## Single-factor perturbation pairs", "",
        "Pairs were enumerated before any cliff threshold. Both endpoints share one strict `reaction_group_id`; exactly one of `ligand`, `base`, or normalized `solvent_1` changes. Blank ligand/base settings and zero outcomes remain eligible.",
        "", markdown_table(pair_counts), "", "### Absolute Δyield distribution (percentage points)", "",
        markdown_table(quantiles), "",
        "No cliff threshold is set in this report. These quantiles are descriptive inputs for a later pre-registered threshold decision, not a rule used to select pairs.", "",
    ])
    REPORT.write_text("\n".join(lines))


if __name__ == "__main__":
    main()
