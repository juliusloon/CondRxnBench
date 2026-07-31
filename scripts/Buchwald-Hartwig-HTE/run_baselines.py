#!/usr/bin/env python3
"""Minimal, reproducible yield baselines for Ahneman--Doyle HTE.

本脚本构建三种基线模型来预测 Buchwald-Hartwig HTE 产率：
1. condition_onehot_ridge:          仅条件因子（催化体系+碱+添加剂）的 OneHot + Ridge 回归
2. substrate_ecfp4_plus_condition_ridge:  底物 ECFP4 指纹 + 条件因子的 Ridge 回归
3. substrate_ecfp4_plus_condition_random_forest: 同上特征的随机森林

评估在两种数据划分下进行：
- random_80_20:             随机 80/20 划分
- additive_component_ood:   以 5 种添加剂为 OOD 测试集（组件外推）

OOD 测试组件通过固定种子随机采样一次，不根据结果选择。
"""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

# ── 运行时依赖检查 ──
# 必须安装 rdkit 和 sklearn，不接受部分回退方案
REQUIRED = ("numpy", "pandas", "sklearn", "rdkit")
missing = [name for name in REQUIRED if importlib.util.find_spec(name) is None]
if missing:
    raise SystemExit(
        "Missing runtime packages: " + ", ".join(missing) +
        ". Install requirements.txt in a dedicated CondRxnBench environment; "
        "do not use results from a partial fallback.")

import numpy as np
import pandas as pd
from rdkit import Chem, DataStructs
from rdkit.Chem import AllChem
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

# ── 全局常量 ──
ROOT = Path(__file__).resolve().parents[1]
SEED = 20260729  # 固定种子，确保完全可复现
CONDITION_COLUMNS = ["catalyst_system", "base", "additive"]  # 条件因子列


# ──────────────────────────────────────────────────────────────────────────────
# 特征工程
# ──────────────────────────────────────────────────────────────────────────────

def ecfp4(smiles: str, n_bits: int = 2048) -> np.ndarray:
    """将 SMILES 字符串转换为 ECFP4（Morgan radius=2）分子指纹。

    ECFP4 = Extended Connectivity Fingerprints with diameter 4（即 radius=2），
    是药物化学中最常用的分子指纹之一，2048 位固定长度向量。
    """
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        raise ValueError(f"Unparseable substrate SMILES: {smiles}")
    fp = AllChem.GetMorganFingerprintAsBitVect(mol, radius=2, nBits=n_bits)
    out = np.zeros(n_bits, dtype=np.int8)
    DataStructs.ConvertToNumpyArray(fp, out)
    return out


def condition_transformer() -> ColumnTransformer:
    """构建条件因子的 OneHot 编码器。

    将 catalyst_system、base、additive 三个分类变量转换为独热编码向量。
    handle_unknown="ignore" 确保 OOD 测试时遇到未知类别不会报错。
    """
    return ColumnTransformer(
        [("conditions", OneHotEncoder(handle_unknown="ignore"), CONDITION_COLUMNS)],
        remainder="drop")


def feature_frame(df: pd.DataFrame, with_fingerprint: bool) -> pd.DataFrame:
    """构建特征矩阵。

    参数:
        with_fingerprint: 是否拼接芳基卤化物的 ECFP4 指纹
                          False → 仅条件因子
                          True  → 条件因子 + 2048 位分子指纹
    """
    out = df[CONDITION_COLUMNS].copy()
    if with_fingerprint:
        fps = np.vstack([ecfp4(x) for x in df.aryl_halide_smiles])
        for i in range(fps.shape[1]):
            out[f"ecfp4_{i}"] = fps[:, i]
    return out


# ──────────────────────────────────────────────────────────────────────────────
# 模型评估
# ──────────────────────────────────────────────────────────────────────────────

def evaluate(name: str, estimator, x_train, y_train, x_test, y_test, split: str) -> dict:
    """训练模型并在测试集上评估，返回包含 MAE、RMSE、R² 的字典。"""
    estimator.fit(x_train, y_train)
    pred = estimator.predict(x_test)
    return {
        "split": split,
        "model": name,
        "n_train": len(y_train),
        "n_test": len(y_test),
        "mae": mean_absolute_error(y_test, pred),
        "rmse": mean_squared_error(y_test, pred) ** .5,
        "r2": r2_score(y_test, pred),
    }


def models(with_fingerprint: bool):
    """返回基线模型列表（Pipeline 形式）。

    每个 Pipeline 包含：
    1. prep:  预处理步骤（OneHot + 可选的 ECFP4 拼接）
    2. model: 回归模型（Ridge 或 RandomForest）
    """
    if with_fingerprint:
        # 保留稀疏的 OneHot 条件编码，同时 passthrough 数值型 ECFP 列
        prep = ColumnTransformer(
            [("conditions", OneHotEncoder(handle_unknown="ignore"), CONDITION_COLUMNS)],
            remainder="passthrough")
    else:
        prep = condition_transformer()

    return [
        # 模型 1：仅条件因子的 Ridge 回归
        ("condition_onehot_ridge",
         Pipeline([("prep", condition_transformer()),
                   ("model", Ridge(alpha=1.0))])),

        # 模型 2：ECFP4 + 条件因子的 Ridge 回归（alpha=10 更强正则化）
        ("substrate_ecfp4_plus_condition_ridge",
         Pipeline([("prep", prep),
                   ("model", Ridge(alpha=10.0))])),

        # 模型 3：ECFP4 + 条件因子的随机森林（500 棵树）
        ("substrate_ecfp4_plus_condition_random_forest",
         Pipeline([("prep", prep),
                   ("model", RandomForestRegressor(
                       n_estimators=500,
                       min_samples_leaf=2,
                       n_jobs=-1,
                       random_state=SEED))])),
    ]


# ──────────────────────────────────────────────────────────────────────────────
# 主流程
# ──────────────────────────────────────────────────────────────────────────────

def main() -> None:
    # ── 加载数据，仅保留有观测值的记录 ──
    df = pd.read_csv(ROOT / "data" / "processed" / "ahneman_buchwald_hartwig_main_matrix.csv")
    df = df.loc[df.yield_observed].reset_index(drop=True)

    # ── 准备两种特征矩阵 ──
    x_cond = feature_frame(df, with_fingerprint=False)  # 仅条件因子
    x_full = feature_frame(df, with_fingerprint=True)   # 条件因子 + ECFP4
    y = df.yield_percent.to_numpy()                      # 目标变量：产率百分比

    # ── 划分 1：随机 80/20 划分 ──
    random_train, random_test = train_test_split(
        np.arange(len(df)), test_size=.2, random_state=SEED)

    # ── 划分 2：添加剂组件 OOD 划分 ──
    # 随机抽取 5 种添加剂作为 OOD 测试集，其余作为训练集
    additives = sorted(df.additive.unique())
    rng = np.random.default_rng(SEED)
    heldout_additives = sorted(rng.choice(additives, size=5, replace=False).tolist())
    ood_test = np.flatnonzero(df.additive.isin(heldout_additives))
    ood_train = np.flatnonzero(~df.additive.isin(heldout_additives))

    # ── 在两种划分下训练和评估所有模型 ──
    results = []
    for split, train_idx, test_idx in (
        ("random_80_20", random_train, random_test),
        ("additive_component_ood", ood_train, ood_test),
    ):
        # 模型 1：每次重新实例化（Pipeline 内部状态不跨划分复用）
        condition_model = Pipeline([
            ("prep", condition_transformer()),
            ("model", Ridge(alpha=1.0)),
        ])
        results.append(evaluate(
            "condition_onehot_ridge", condition_model,
            x_cond.iloc[train_idx], y[train_idx],
            x_cond.iloc[test_idx], y[test_idx], split))

        # 模型 2 和 3
        for name, model in models(True)[1:]:
            results.append(evaluate(
                name, model,
                x_full.iloc[train_idx], y[train_idx],
                x_full.iloc[test_idx], y[test_idx], split))

    # ── 输出结果 ──
    out = ROOT / "results"
    out.mkdir(exist_ok=True)
    result_df = pd.DataFrame(results).sort_values(["split", "model"])
    result_df.to_csv(out / "ahneman_minimal_baselines.csv", index=False)

    # ── 输出实验协议（确保可复现） ──
    protocol = {
        "seed": SEED,
        "target": "LC/UV product_scaled percentage",
        "observed_records_only": int(len(df)),
        "random_split": "fixed 80/20 row split",
        "component_ood": {
            "component": "additive",
            "heldout_additives": heldout_additives,
        },
        "fingerprint": "RDKit Morgan radius=2, 2048 bits (ECFP4)",
        "condition_fields": CONDITION_COLUMNS,
    }
    (out / "ahneman_minimal_baselines_protocol.json").write_text(
        json.dumps(protocol, indent=2) + "\n")

    # ── 打印结果摘要 ──
    print(result_df.to_string(index=False, float_format=lambda x: f"{x:.3f}"))


if __name__ == "__main__":
    main()
