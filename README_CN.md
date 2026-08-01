# CondRxnBench

[English](README.md) | 中文

用于 **CondRxnBench** 的可复现构建与评估代码，现覆盖 Ahneman–Doyle Buchwald–Hartwig 与 Perera Suzuki–Miyaura 高通量实验筛选。

## CondRxnBench-Core v0.1

当前本地发布为 **CondRxnBench-Benchmark v0.1**：以 [release manifest](releases/condrxnbench-benchmark-v0_1/manifest.json) 的 hash 绑定 Core v0.2、strict pair/graph、S0–S5 划分和来源分层 baseline leaderboard。它不跨来源混报绝对产率，也不补造缺失反应结构。

```bash
python3 scripts/build_core_v0_1.py
python3 tests/verify_core_v0_1.py
```

产物位于 `data/processed/core_v0_1/`。字段映射、数据字典和 dataset cards 见 `metadata/`；Core v0.2 的权威交付格式为 Parquet，CSV 仅供人工检查。

## 项目状态与交接入口

**当前本地发布：CondRxnBench-Benchmark v0.1。** 包含 9,900 条 Core records、
116,156 条 strict pairs、S0–S5 manifests 与来源分层的 baseline leaderboard。
success 分类不在 v0.1 定义；cliff 使用冻结的 30 pp 主阈值，结构不足的模型家族
以明确 N/A 记录而非伪造特征。

- [STATUS.md](STATUS.md)：当前可恢复的工作快照
- [PROGRESS.md](PROGRESS.md)：按阶段的完成记录、风险与下一步
- [ROADMAP.md](ROADMAP.md)：按优先级排列的后续计划
- [docs/](docs/README.md)：架构、数据接口与讨论入口
- [adr/](adr/README.md)：关键技术决策记录

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

## 贡献与同步规范

1. 区分原始证据、派生数据和报告，禁止用派生值覆盖固化的原始输入。
2. 改动 Core v0.1 的输入、schema 或构建脚本后，运行对应构建/QC 命令及
   `python3 tests/verify_core_v0_1.py`。
3. 语义变化同步更新 dataset card 或统一 schema。
4. 阶段状态变化同步更新 `STATUS.md`、`PROGRESS.md`、`ROADMAP.md`；持久的
   技术取舍另建 ADR。
5. 对用户可见的数据、接口或行为变化更新 `CHANGELOG.md`；未实际运行或未能
   可复现获取的结果不得写成已完成。
