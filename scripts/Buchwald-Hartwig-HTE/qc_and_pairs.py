#!/usr/bin/env python3
"""Quality control and exhaustive single-factor pair construction.

此脚本执行两项核心任务：
1. 质量控制（QC）：验证重建数据集的完整性，生成字段级频率表和跨组合覆盖率报告
2. 单因子扰动对构建：枚举所有恰好只有一个条件因子不同的反应对，用于后续的"条件悬崖"分析
"""
from __future__ import annotations

from itertools import combinations
from pathlib import Path
import json

import pandas as pd

# ── 路径常量 ──
ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "processed" / "ahneman_buchwald_hartwig_main_matrix.csv"
REPORT = ROOT / "reports" / "Buchwald-Hartwig-HTE" / "ahneman_qc_report.md"


# ──────────────────────────────────────────────────────────────────────────────
# QC 工具函数
# ──────────────────────────────────────────────────────────────────────────────

def frequency_table(df: pd.DataFrame, factor: str) -> pd.DataFrame:
    """计算单个因子（如 aryl_halide、base 等）的频率统计表。

    统计内容包括：
    - records:        该因子水平出现的总记录数
    - missing_yield:  产率缺失（NA）的记录数
    - zero_yield:     产率为零的记录数
    - zero_yield_rate: 零产率占比
    - median_yield:   产率中位数
    """
    return (df.groupby(factor, dropna=False)
            .agg(records=("reaction_id", "size"),
                 missing_yield=("yield_observed", lambda x: int((~x).sum())),
                 zero_yield=("zero_yield", "sum"),
                 zero_yield_rate=("zero_yield", "mean"),
                 median_yield=("yield_percent", "median"))
            .reset_index())


# ──────────────────────────────────────────────────────────────────────────────
# 单因子扰动对构建
# ──────────────────────────────────────────────────────────────────────────────

def make_pairs(df: pd.DataFrame) -> pd.DataFrame:
    """枚举所有恰好只有一个条件因子不同的反应对（单因子扰动对）。

    约束条件：
    - 两个端点必须都有观测产率（yield_observed == True）
    - 两个端点必须属于同一反应组（reaction_group_id 相同，即同一芳基卤化物底物）
    - catalyst_system、base、additive 三个因子中恰好有一个不同
    - aryl_halide 被刻意排除：底物扰动是另一个独立任务

    返回的 DataFrame 包含：
    - pair_id:           对的唯一标识（reaction_id_a + __ + reaction_id_b）
    - changed_factor:    变化的因子名
    - condition_a/b:     变化因子在两端的值
    - yield_a/b:         两端的产率
    - delta_yield:       产率差（b - a）
    - abs_delta_yield:   |Δyield|（绝对值）
    """
    factors = ["catalyst_system", "base", "additive"]
    records = []
    observed = df.loc[df.yield_observed].copy()

    # 对每个可能变化的因子进行枚举
    for changed in factors:
        fixed = [f for f in factors if f != changed]
        # 按 (reaction_group_id, 固定因子) 分组
        for _, group in observed.groupby(["reaction_group_id", *fixed], dropna=False):
            group = group.sort_values(changed)
            # 在组内两两配对
            for (_, a), (_, b) in combinations(group.iterrows(), 2):
                # 验证确实只有一个因子不同
                changed_fields = [f for f in factors if a[f] != b[f]]
                if len(changed_fields) != 1:
                    continue
                records.append({
                    "pair_id": f"{a.reaction_id}__{b.reaction_id}",
                    "reaction_id_a": a.reaction_id,
                    "reaction_id_b": b.reaction_id,
                    "reaction_group_id": a.reaction_group_id,
                    "changed_factor": changed_fields[0],
                    "n_changed_factors": len(changed_fields),
                    "condition_a": a[changed],
                    "condition_b": b[changed],
                    "yield_a": a.yield_percent,
                    "yield_b": b.yield_percent,
                    "delta_yield": b.yield_percent - a.yield_percent,
                    "abs_delta_yield": abs(b.yield_percent - a.yield_percent),
                })

    pairs = pd.DataFrame(records)
    return pairs.sort_values(["changed_factor", "pair_id"]).reset_index(drop=True)


def to_md_table(df: pd.DataFrame) -> str:
    """将 DataFrame 转换为 Markdown 表格字符串，保留三位小数。"""
    return df.to_markdown(index=False, floatfmt=".3f")


# ──────────────────────────────────────────────────────────────────────────────
# 主流程
# ──────────────────────────────────────────────────────────────────────────────

def main() -> None:
    # ── 加载数据 ──
    df = pd.read_csv(DATA)
    factors = ["aryl_halide", "catalyst_system", "base", "additive"]

    # ── 矩阵完整性验证 ──
    expected = 15 * 4 * 3 * 23  # 理论全因子单元数
    actual_combinations = df[factors].drop_duplicates().shape[0]  # 实际唯一组合数
    duplicate_combinations = int(df.duplicated(factors).sum())     # 重复组合数（应为 0）
    missing_wells = int((~df.yield_observed).sum())                # 产率缺失的孔数
    observed = df.loc[df.yield_observed]                           # 有观测值的子集

    # ── 字段级频率表 ──
    frequency = {factor: frequency_table(df, factor) for factor in factors}

    # ── 交叉组合完整性检查 ──
    cross = (df.groupby(factors, dropna=False)
             .agg(records=("reaction_id", "size"),
                  observed_yields=("yield_observed", "sum"))
             .reset_index())

    # ── 构建单因子扰动对 ──
    pairs = make_pairs(df)
    pairs.to_csv(ROOT / "data" / "processed" / "ahneman_buchwald_hartwig_single_factor_pairs.csv", index=False)

    # ── 输出各因子的频率 CSV ──
    for factor, table in frequency.items():
        table.to_csv(ROOT / "reports" / "Buchwald-Hartwig-HTE" / f"ahneman_qc_frequency_{factor}.csv", index=False)

    # ── 统计扰动对的分布 ──
    pair_counts = pairs.changed_factor.value_counts().rename_axis("changed_factor").reset_index(name="pairs")
    # 按因子分组计算 |Δyield| 的分位数（p50, p75, p90, p95）
    delta_quantiles = (pairs.groupby("changed_factor")
                       .abs_delta_yield.quantile([.5, .75, .9, .95])
                       .unstack().reset_index())
    delta_quantiles.columns = ["changed_factor", "p50", "p75", "p90", "p95"]

    # ── 生成 JSON 摘要 ──
    summary = {
        "theoretical_main_cells": expected,
        "reconstructed_main_cells": int(len(df)),
        "unique_condition_combinations": int(actual_combinations),
        "duplicate_condition_combinations": duplicate_combinations,
        "missing_analytical_outcomes": missing_wells,
        "observed_outcomes": int(len(observed)),
        "zero_yield_count": int(observed.zero_yield.sum()),
        "zero_yield_rate_observed": float(observed.zero_yield.mean()),
        "single_factor_pairs_observed_only": int(len(pairs)),
        "pair_counts": pair_counts.to_dict("records"),
    }
    (ROOT / "reports" / "Buchwald-Hartwig-HTE" / "ahneman_qc_summary.json").write_text(json.dumps(summary, indent=2) + "\n")

    # ── 生成 Markdown QC 报告 ──
    lines = [
        "# Ahneman--Doyle HTE: reconstruction QC", "",

        # ── 第一节：矩阵完整性 ──
        "## Matrix integrity", "",
        f"- Theoretical main factorial cells: **{expected:,}** "
        f"(15 aryl halides × 4 catalyst systems × 3 bases × 23 additives).",
        f"- Reconstructed main cells: **{len(df):,}**; "
        f"unique condition combinations: **{actual_combinations:,}**; "
        f"duplicate combinations: **{duplicate_combinations:,}**.",
        f"- Analytical outcomes missing: **{missing_wells:,}**; "
        f"observed yields: **{len(observed):,}**.",
        f"- Observed zero yields: **{int(observed.zero_yield.sum()):,}** "
        f"({observed.zero_yield.mean():.1%}). "
        f"Zero is retained as an observed outcome, never recoded as missing.",
        "",

        # ── 第二节：字段级频率表 ──
        "## Field-level frequencies, missingness, and zero yields", "",
    ]
    for factor in factors:
        lines += [f"### {factor}", "", to_md_table(frequency[factor]), ""]

    # ── 第三节：交叉组合完整性 ──
    lines += [
        "## Cross-combination completeness", "",
        "Every named four-factor combination is represented once in the physical design. "
        "Outcome completeness is assessed separately, so an analytical NA cannot masquerade "
        "as an absent experiment.", "",
        f"- Design coverage: **{actual_combinations / expected:.1%}**",
        f"- Outcome coverage: **{len(observed) / expected:.1%}**", "",
    ]

    # ── 第四节：单因子扰动对统计 ──
    lines += [
        "## Single-factor perturbation pairs", "",
        "Pairs were enumerated before any cliff label or threshold. "
        "Both endpoints must have observed yields and the same `reaction_group_id`; "
        "exactly one of `catalyst_system`, `base`, and `additive` may differ.", "",
        to_md_table(pair_counts), "",
        "### Absolute Δyield distribution (percentage points)", "",
        to_md_table(delta_quantiles), "",
        "No cliff threshold is set in this report. "
        "The quantiles are descriptive inputs for a pre-registered threshold decision, "
        "not a post hoc sample-selection rule.", "",
    ]

    REPORT.write_text("\n".join(lines))


if __name__ == "__main__":
    main()
