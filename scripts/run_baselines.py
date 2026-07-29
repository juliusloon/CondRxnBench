#!/usr/bin/env python3
"""Minimal, reproducible yield baselines for Ahneman--Doyle HTE.

Models: condition-only ridge; substrate ECFP4 + condition ridge; and random
forest on the same ECFP4/condition design.  Random and additive-component OOD
splits are reported side by side.  The OOD test components are sampled once
with a recorded seed, never chosen by outcome.
"""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

REQUIRED = ("numpy", "pandas", "sklearn", "rdkit")
missing = [name for name in REQUIRED if importlib.util.find_spec(name) is None]
if missing:
    raise SystemExit("Missing runtime packages: " + ", ".join(missing) +
                     ". Install requirements.txt in a dedicated CondRxnBench environment; do not use results from a partial fallback.")

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

ROOT = Path(__file__).resolve().parents[1]
SEED = 20260729
CONDITION_COLUMNS = ["catalyst_system", "base", "additive"]


def ecfp4(smiles: str, n_bits: int = 2048) -> np.ndarray:
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        raise ValueError(f"Unparseable substrate SMILES: {smiles}")
    fp = AllChem.GetMorganFingerprintAsBitVect(mol, radius=2, nBits=n_bits)
    out = np.zeros(n_bits, dtype=np.int8)
    DataStructs.ConvertToNumpyArray(fp, out)
    return out


def condition_transformer() -> ColumnTransformer:
    return ColumnTransformer([("conditions", OneHotEncoder(handle_unknown="ignore"), CONDITION_COLUMNS)], remainder="drop")


def feature_frame(df: pd.DataFrame, with_fingerprint: bool) -> pd.DataFrame:
    out = df[CONDITION_COLUMNS].copy()
    if with_fingerprint:
        fps = np.vstack([ecfp4(x) for x in df.aryl_halide_smiles])
        for i in range(fps.shape[1]):
            out[f"ecfp4_{i}"] = fps[:, i]
    return out


def evaluate(name: str, estimator, x_train, y_train, x_test, y_test, split: str) -> dict:
    estimator.fit(x_train, y_train)
    pred = estimator.predict(x_test)
    return {"split": split, "model": name, "n_train": len(y_train), "n_test": len(y_test),
            "mae": mean_absolute_error(y_test, pred), "rmse": mean_squared_error(y_test, pred) ** .5,
            "r2": r2_score(y_test, pred)}


def models(with_fingerprint: bool):
    if with_fingerprint:
        categorical = condition_transformer()
        # Preserve sparse one-hot conditions and append numerical ECFP columns.
        prep = ColumnTransformer([("conditions", OneHotEncoder(handle_unknown="ignore"), CONDITION_COLUMNS)],
                                 remainder="passthrough")
    else:
        prep = condition_transformer()
    return [
        ("condition_onehot_ridge", Pipeline([("prep", condition_transformer()), ("model", Ridge(alpha=1.0))])),
        ("substrate_ecfp4_plus_condition_ridge", Pipeline([("prep", prep), ("model", Ridge(alpha=10.0))])),
        ("substrate_ecfp4_plus_condition_random_forest", Pipeline([("prep", prep), ("model", RandomForestRegressor(n_estimators=500, min_samples_leaf=2, n_jobs=-1, random_state=SEED))])),
    ]


def main() -> None:
    df = pd.read_csv(ROOT / "data" / "processed" / "ahneman_buchwald_hartwig_main_matrix.csv")
    df = df.loc[df.yield_observed].reset_index(drop=True)
    x_cond = feature_frame(df, with_fingerprint=False)
    x_full = feature_frame(df, with_fingerprint=True)
    y = df.yield_percent.to_numpy()
    random_train, random_test = train_test_split(np.arange(len(df)), test_size=.2, random_state=SEED)
    additives = sorted(df.additive.unique())
    rng = np.random.default_rng(SEED)
    heldout_additives = sorted(rng.choice(additives, size=5, replace=False).tolist())
    ood_test = np.flatnonzero(df.additive.isin(heldout_additives))
    ood_train = np.flatnonzero(~df.additive.isin(heldout_additives))
    results = []
    # Every model is fitted afresh for each split.
    for split, train_idx, test_idx in (("random_80_20", random_train, random_test), ("additive_component_ood", ood_train, ood_test)):
        condition_model = Pipeline([("prep", condition_transformer()), ("model", Ridge(alpha=1.0))])
        results.append(evaluate("condition_onehot_ridge", condition_model, x_cond.iloc[train_idx], y[train_idx], x_cond.iloc[test_idx], y[test_idx], split))
        for name, model in models(True)[1:]:
            results.append(evaluate(name, model, x_full.iloc[train_idx], y[train_idx], x_full.iloc[test_idx], y[test_idx], split))
    out = ROOT / "results"; out.mkdir(exist_ok=True)
    result_df = pd.DataFrame(results).sort_values(["split", "model"])
    result_df.to_csv(out / "ahneman_minimal_baselines.csv", index=False)
    protocol = {"seed": SEED, "target": "LC/UV product_scaled percentage", "observed_records_only": int(len(df)),
                "random_split": "fixed 80/20 row split", "component_ood": {"component": "additive", "heldout_additives": heldout_additives},
                "fingerprint": "RDKit Morgan radius=2, 2048 bits (ECFP4)", "condition_fields": CONDITION_COLUMNS}
    (out / "ahneman_minimal_baselines_protocol.json").write_text(json.dumps(protocol, indent=2) + "\n")
    print(result_df.to_string(index=False, float_format=lambda x: f"{x:.3f}"))


if __name__ == "__main__":
    main()
