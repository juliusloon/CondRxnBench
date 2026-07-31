# CondRxnBench

[English](README.md) | 中文

用于 **CondRxnBench** 的可复现构建与评估代码，现覆盖 Ahneman–Doyle Buchwald–Hartwig 与 Perera Suzuki–Miyaura 高通量实验筛选。

## 当前数据策略

该衍生数据集由带版本号的原始逐孔分析导出文件（`data/raw/ahneman_doyle_rxnpredict/yield_data/plate*.csv`）和补充材料中的板布局表重建而成。这些输入文件复制自 `doylelab/rxnpredict` 仓库，对应提交为 `57e15fdb7f7483c6bf3a601df69f6ac9e5af6965`；详见原始源 README 及附带的许可证。

构建流程不会读取 `data_table.csv` 和响应 CSV 文件。输入清单记录了确切的源路径和 SHA-256 校验和。

15 × 4 × 3 × 23 的实验设计包含 4,140 个理论主矩阵单元。对照组被单独保留，而非被静默丢弃。

## 复现

```bash
python3 scripts/Buchwald-Hartwig-HTE/build_dataset.py
python3 scripts/Buchwald-Hartwig-HTE/qc_and_pairs.py
python3 scripts/Buchwald-Hartwig-HTE/run_baselines.py
python3 scripts/Suzuki-Miyaura-HTE/build_dataset.py
python3 scripts/Suzuki-Miyaura-HTE/qc_and_pairs.py
```

`run_baselines.py` 需要 `requirements.txt` 中列出的依赖包。若这些包不可用，请参阅 `reports/environment_gap.md`。

Perera 流程仅读取仓库中固化的 `Data File S1` 工作簿和补充材料 PDF：空白配体/碱条件与观测零结果均被保留；在选择任何 cliff 阈值前，先枚举全部 `n_changed_factors = 1` 的条件反应对。
