#!/usr/bin/env python3
"""Rebuild Ahneman--Doyle HTE records from SI layout and raw per-well exports.

No derived rxnpredict table is used as an input.  The source repository stores
the SI layout tables and one LC/UV export per plate quadrant; joining those by
their physical well locations is the provenance-preserving reconstruction.

重建 Ahneman--Doyle 高通量实验（HTE）记录：基于补充信息（SI）的布局表和原始逐孔导出结果。

不使用任何派生的 rxnpredict 表作为输入。源代码仓库中保存了 SI 布局表，以及每个板块象限对应的
一份 LC/UV 导出文件；将这些数据按其物理孔位进行连接，才是保留完整溯源信息的重建方式。
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import pandas as pd


# ──────────────────────────────────────────────────────────────────────────────
# 工具函数
# ──────────────────────────────────────────────────────────────────────────────

def sha256(path: Path) -> str:
    """计算文件的 SHA-256 校验和，用于输入清单的溯源追踪。
    分块读取（每次 1 MB）以支持大文件。"""
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def location_to_row_col(location: str, block: int, plate: int) -> tuple[int, int]:
    """将板上的孔位字符串（如 'A:1' 或 '1:A'）转换为统一的 (row, col) 整数坐标。

    不同板的导出格式不同（plate 3 是 row:col，其余是 col:row），此函数统一处理。
    block 2/3/4 对应板的四个象限，需要对行列做偏移以映射到完整板坐标系。

    这个方向由 SI 板导出文件指定，并在原始 rxnpredict 重建工具中有独立文档记录。
    """
    first, second = location.split(":")
    if plate == 3:
        row_letter, col = first, int(second)
    else:
        col, row_letter = int(first), second
    row = ord(row_letter) - ord("A") + 1
    # 象限偏移：block 2 → 列 +24；block 3 → 行 +16；block 4 → 两者皆加
    if block == 2:
        col += 24
    elif block == 3:
        row += 16
    elif block == 4:
        row += 16
        col += 24
    return row, col


# ──────────────────────────────────────────────────────────────────────────────
# 读取原始逐孔 LC/UV 导出
# ──────────────────────────────────────────────────────────────────────────────

def read_wells(root: Path) -> tuple[pd.DataFrame, list[Path]]:
    """遍历 3 块板 × 4 个象限 = 12 个 CSV 文件，读取每个孔的分析结果。

    每个 CSV 包含一个象限内所有孔的 LC/UV 数据（样品名、数据文件、
    产物峰、内标、校正因子、换算产率等）。

    返回:
        frames: 合并后的 DataFrame，包含统一的 (plate, block, row, col) 坐标
        files:  所有读取过的文件路径列表（用于生成输入清单）
    """
    frames, files = [], []
    for plate in (1, 2, 3):
        for block in (1, 2, 3, 4):
            path = root / "yield_data" / f"plate{plate}.{block}.csv"
            raw = pd.read_csv(path)
            # 过滤空行（Location 列为空的记录）
            raw = raw.loc[raw["Location"].notna()].copy()
            # 将孔位字符串转换为统一的 (row, col) 坐标
            raw[["row", "col"]] = raw["Location"].map(
                lambda x: location_to_row_col(x, block, plate)
            ).apply(pd.Series)
            raw["plate"] = plate
            raw["block"] = block
            raw["source_file"] = str(path)      # 溯源：来源文件路径
            raw["source_well"] = raw["Location"] # 溯源：原始孔位标识
            # 只保留需要的列
            frames.append(raw[["plate", "block", "row", "col", "source_file", "source_well",
                               "Sample Name", "Data File", "product", "internal_standard",
                               "corr_factor", "product_scaled"]])
            files.append(path)
    return pd.concat(frames, ignore_index=True), files


# ──────────────────────────────────────────────────────────────────────────────
# 读取补充材料中的化合物列表与 SMILES
# ──────────────────────────────────────────────────────────────────────────────

def read_compounds(root: Path) -> dict[str, pd.DataFrame]:
    """读取四种试剂（添加剂、芳基卤化物、碱、配体）的名称-SMILES 对照表。

    注意碱和配体的布局表中直接存储名称（作为索引），而添加剂和芳基卤化物
    存储的是数字编号，需要后续通过编号关联。
    """
    names = {
        "additive": ("additive-list.csv", "component", "Additive_SMILES"),
        "aryl_halide": ("aryl_halide-list.csv", "component", "Aryl_halide_SMILES"),
        "base": ("base-list.csv", "name", "Base_SMILES"),
        "ligand": ("ligand-list.csv", "name", "Ligand_SMILES"),
    }
    out = {}
    for role, (filename, key, smiles) in names.items():
        df = pd.read_csv(root / "smiles" / filename)
        # 对于 base/ligand：布局表存储试剂名称本身，名称即索引，不再作为列。
        # 对于 additive/aryl_halide：布局表存储数字编号，需要额外保留 name 列。
        columns = [smiles] if key == "name" else ["name", smiles]
        out[role] = df.set_index(key)[columns].rename(columns={smiles: f"{role}_smiles"})
    return out


# ──────────────────────────────────────────────────────────────────────────────
# 从 SI 表 S1/S2 构建完整布局表
# ──────────────────────────────────────────────────────────────────────────────

def build_layout(root: Path) -> tuple[pd.DataFrame, list[Path]]:
    """根据 SI Table S1（行→配体+添加剂）和 Table S2（列→碱+芳基卤化物）构建
    15×4×3×23 全因子实验布局。

    每个 (plate, row, col) 单元格唯一对应一组 (ligand, base, additive, aryl_halide)。
    返回布局 DataFrame 和所有引用的源文件路径。
    """
    rows_path, cols_path = root / "layout" / "Table_S1.csv", root / "layout" / "Table_S2.csv"
    rows, cols, compounds = pd.read_csv(rows_path), pd.read_csv(cols_path), read_compounds(root)

    # 构建所有 (plate, row, col) 组合及其对应的试剂
    records = []
    for plate in (1, 2, 3):
        additive_column = f"Additive (Plate {plate})"  # 不同板的添加剂列名不同
        for _, r in rows.iterrows():
            for _, c in cols.iterrows():
                record = {
                    "plate": plate,
                    "row": int(r.Row),
                    "col": int(c.Column),
                    "ligand": r.Ligand,
                    "base": c.Base,
                    "additive_number": r[additive_column],
                    "aryl_halide_number": c["Aryl Halide"],
                }
                records.append(record)
    layout = pd.DataFrame(records)

    # 通过编号关联添加剂和芳基卤化物的名称与 SMILES
    for role, number_col in (("additive", "additive_number"), ("aryl_halide", "aryl_halide_number")):
        lookup = compounds[role].copy()
        lookup.index = pd.to_numeric(lookup.index)
        layout = layout.join(lookup, on=number_col)
        layout = layout.rename(columns={"name": role})

    # 碱和配体直接通过名称关联 SMILES
    for role in ("base", "ligand"):
        layout = layout.join(compounds[role], on=role)

    return layout, [rows_path, cols_path,
                    root / "smiles" / "additive-list.csv",
                    root / "smiles" / "aryl_halide-list.csv",
                    root / "smiles" / "base-list.csv",
                    root / "smiles" / "ligand-list.csv"]


# ──────────────────────────────────────────────────────────────────────────────
# 主流程：合并、分类、标记、输出
# ──────────────────────────────────────────────────────────────────────────────

def main() -> None:
    # ── 解析命令行参数 ──
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-root", type=Path,
                        default=Path("data/raw/ahneman_doyle_rxnpredict"),
                        help="versioned raw rxnpredict subset (default: %(default)s)")
    parser.add_argument("--out-root", type=Path, default=Path("."))
    args = parser.parse_args()
    root, out = args.source_root.resolve(), args.out_root.resolve()

    # ── 步骤 1：读取原始分析数据和实验布局 ──
    wells, well_files = read_wells(root)
    layout, layout_files = build_layout(root)

    # ── 步骤 2：按 (plate, row, col) 左连接，将布局与分析结果合并 ──
    merged = layout.merge(wells, how="left", on=["plate", "row", "col"], validate="one_to_one")

    # ── 步骤 3：标记对照组 ──
    # 对照组定义：添加剂或芳基卤化物缺失（NA）的记录
    merged["is_control"] = merged[["additive", "aryl_halide"]].isna().any(axis=1)
    merged["record_class"] = merged["is_control"].map({False: "main_matrix", True: "control"})
    # 对照类型细分：无添加剂、无芳基卤化物、空白对照
    merged["control_type"] = pd.NA
    merged.loc[merged["additive"].isna() & merged["aryl_halide"].notna(), "control_type"] = "additive_free_control"
    merged.loc[merged["additive"].notna() & merged["aryl_halide"].isna(), "control_type"] = "aryl_halide_free_control"
    merged.loc[merged["additive"].isna() & merged["aryl_halide"].isna(), "control_type"] = "blank_control"

    # ── 步骤 4：处理产率 ──
    merged["yield_percent"] = pd.to_numeric(merged["product_scaled"], errors="coerce")
    merged["yield_observed"] = merged["yield_percent"].notna()  # 是否有观测值
    merged["zero_yield"] = merged["yield_percent"].eq(0) & merged["yield_observed"]  # 观测到的零产率

    # ── 步骤 5：生成唯一标识符 ──
    # reaction_group_id：按芳基卤化物分组（同一底物的所有条件组合属于同一反应组）
    merged["reaction_group_id"] = merged["aryl_halide_number"].map(
        lambda x: f"AHNEMAN_BH_ARYL_{int(x):02d}" if pd.notna(x) else pd.NA
    )
    # reaction_id：唯一标识每个孔/反应（板号+行+列）
    merged["reaction_id"] = merged.apply(
        lambda x: f"AHNEMAN_BH_P{x.plate}_R{x.row:02d}_C{x.col:02d}", axis=1
    )
    # 催化体系 = 配体名称（本 HTE 中四个级别是预成型的 Pd(II)-配体预催化剂，
    # 不是可独立组合的游离配体/Pd 变量）
    merged["catalyst_system"] = merged["ligand"]

    # ── 步骤 6：分离主矩阵和对照组 ──
    main_cols = ["aryl_halide", "ligand", "base", "additive"]
    main = merged.loc[~merged.is_control].copy()
    controls = merged.loc[merged.is_control].copy()

    # 验证：预期的全因子单元数 = 15 × 4 × 3 × 23 = 4140
    expected = 15 * 4 * 3 * 23
    assert len(main) == expected, (len(main), expected)
    assert not main[main_cols].isna().any().any()  # 主矩阵不应有缺失因子

    # ── 步骤 7：输出处理后的数据 ──
    processed = out / "data" / "processed"
    meta = out / "data" / "raw_metadata"
    processed.mkdir(parents=True, exist_ok=True)
    meta.mkdir(parents=True, exist_ok=True)

    # 定义输出列
    keep = ["reaction_id", "reaction_group_id", "record_class", "is_control", "control_type",
            "plate", "block", "row", "col",
            "source_file", "source_well", "Sample Name", "Data File",
            "aryl_halide_number", "aryl_halide", "aryl_halide_smiles",
            "catalyst_system", "ligand", "ligand_smiles",
            "base", "base_smiles",
            "additive_number", "additive", "additive_smiles",
            "yield_percent", "yield_observed", "zero_yield",
            "product", "internal_standard", "corr_factor"]

    # 主矩阵和对照组分别输出
    main[keep].to_csv(processed / "ahneman_buchwald_hartwig_main_matrix.csv", index=False)
    controls[keep].to_csv(processed / "ahneman_buchwald_hartwig_controls.csv", index=False)

    # ── 步骤 8：生成输入清单（溯源元数据） ──
    manifest = {
        "source_repository": str(root),
        "input_policy": "SI layout + raw per-well LC/UV exports only; derived CSVs excluded",
        "files": [{"path": str(p), "sha256": sha256(p)} for p in sorted(well_files + layout_files)],
        "expected_main_cells": expected,
        "reconstructed_main_cells": int(len(main)),
        "controls": int(len(controls)),
    }
    (meta / "ahneman_raw_input_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")


if __name__ == "__main__":
    main()
