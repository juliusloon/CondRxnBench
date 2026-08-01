# 项目状态

> 最后更新：2026-07-31  
> 当前阶段：**CondRxnBench-Benchmark v0.1 已在本地提升，进入维护与后续研究准备**
> 维护规则：完成一个可验证阶段、发现/解除关键风险或调整下一步优先级时更新本文件；详细历史写入 `PROGRESS.md`。

## 当前可交付物

- `releases/condrxnbench-benchmark-v0_1/manifest.json` 是本地提升边界：它以 hash 绑定 Core v0.2、strict pair/graph、S0–S5 split 与 baseline leaderboard，而不覆写底层 candidate provenance。
- 基线结果有 216 个冻结 formal run、108 个实际 negative controls、239,652 条 source-stratified test predictions 与 4,140 条 per-seed metric records；终审 PASS。
- 默认验证环境为 `conda chem` 的直接解释器，详见 `environment/chem_condrxnbench_runtime.md`；冻结 winner 的重物化仍使用版本化 Python 3.11/sklearn 1.5.2 环境。

- 已从固化的原始证据重建 Ahneman--Doyle Buchwald--Hartwig 主矩阵（4,140 条）及独立对照（468 条），并生成 55,676 个严格单因素 pair。
- 已从固化的 Perera Suzuki--Miyaura `Data File S1` 重建主矩阵（5,760 条），并生成 60,480 个严格单因素 pair。
- 已生成 `data/processed/core_v0_1/`：9,900 条统一反应记录、116,156 个 strict pair、条件词典和 SHA-256 manifest。
- Phase 0 已通过独立 clean-environment review：20 个 raw reconstruction inputs 已由相对路径 hash manifest 固化，Python 3.11 环境可完整重跑两源 build/QC、Core 和 Parquet round-trip。
- 条件词典现有 60 条 source-scoped `component_id`；同名跨源 `XPhos` 不再被无证据合并。records 与 pairs 的历史 hash 保持不变。
- Phase 1 Core v0.2 candidate 已完成 Round A–C 独立门禁：Parquet-authoritative records/controls 与 structure、registry、continuous、mixture、mapping side tables 位于 `data/processed/core_v0_2/`，其 manifest 仍明示 `candidate_not_promoted`。

## 正在进行

- 后续研究仅可在新的 goal 中探索 CYC-Loss/CondFormer、补全有来源的 reaction representation 或新增数据源；不得改写 v0.1 freeze、split 或 baseline 结论。

## 主要风险与限制

| 风险/限制 | 影响 | 当前处置 |
| --- | --- | --- |
| 默认 Python 3.13 不适用于 v0.2 发布链 | 容易遗漏 RDKit/pyarrow/scikit-learn 与 Excel/QC 依赖 | 使用 `environment/core_v0_2_py311_requirements.txt` 建立独立 Python 3.11 环境；正式 v0.2 Parquet 仍待 Phase 1 schema gate |
| 两个数据源的产率测量语义不同 | 不能汇总或直接比较跨源绝对产率 | 所有绝对指标按 `source_dataset` 与 `yield_type` 分层 |
| 未注册的阈值会造成 cliff/success 选择偏差 | 结论不可复查 | 先使用连续 `delta_yield` 与 strict pair；阈值另行 ADR 和协议化 |

## 恢复工作顺序

```bash
# Default validation interpreter: /Users/juliusloon/miniforge3/envs/chem/bin/python
# Frozen baseline materialization: CPython 3.11 environment from environment/core_v0_2_py311_requirements.txt.
python scripts/Buchwald-Hartwig-HTE/build_dataset.py
python scripts/Buchwald-Hartwig-HTE/qc_and_pairs.py
python scripts/Suzuki-Miyaura-HTE/build_dataset.py
python scripts/Suzuki-Miyaura-HTE/qc_and_pairs.py
python scripts/build_core_v0_1.py
python tests/verify_core_v0_1.py
python tests/verify_phase0_inputs.py
python tests/verify_parquet_roundtrip.py
```

开始新阶段前先阅读 `PROGRESS.md`、相关 dataset card、`adr/` 中的已接受决策；完成后同步更新状态、进展、路线图和变更日志。
