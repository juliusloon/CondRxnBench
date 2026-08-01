# 2026-07-31 — Core v0.2 与 Benchmark v0.1：Phase 0 启动

## 目标

- 在不更改原始输入、不清理既有工作树改动的约束下，冻结 Core v0.1 证据基线，并建立可复跑的环境与验证链路。
- 本轮只验证一个假设：Ahneman QC 的失败由仓库根路径解析错误造成。

## 输入与约束

- Git 基线：`80ee279e1bfaeb0750807d2d09a15b1f4d1e2dd4`。
- 原始输入 hash 清单：`/private/tmp/condrxnbench_raw_current.sha256`（清单 SHA-256 `b5809076de73336be86d78ba1dbb71962b2ff5f14cfdb6b2d6ddc378acafc5c8`）。
- 主工作树已有 `.gitignore`、README、维护文档及 Core v0.1 产物等未提交变更；尤其 `data/raw_metadata/perera_raw_input_manifest.json` 已删除。未恢复、未清理这些既有改动。

## 实际命令与结果

- 在 `/private/tmp/condrxnbench-phase0.rCwaU9` 隔离副本运行两源构建、QC、Core build 和 verifier。
- Perera 构建与 QC 成功；Core 重建产生 9,900 条 records 和 116,156 条 strict pairs，独立 verifier 成功。
- Ahneman 构建成功，但 QC 失败并定位到 `scripts/Buchwald-Hartwig-HTE/qc_and_pairs.py` 的 `ROOT = ...parents[1]`：该值是 `<repo>/scripts`，不是仓库根。
- 对应最小修复改为 `parents[2]`；后续将复制到隔离副本后完成完整重跑。

## 环境

- 默认 `python3`：Python 3.13.2，pandas 3.0.2；可执行 CSV 重建。
- 已发现 Python 3.11.15，但没有 pandas、numpy、RDKit、pyarrow、scikit-learn 等包。安装版本化依赖需要单独授权，尚未执行。

## 风险与下一步

- `data/raw_metadata/perera_raw_input_manifest.json` 的既有删除使其不能作为工作树中的可恢复 input manifest；需要在不覆盖该用户改动的前提下决定如何恢复版本化发布记录。
- [ ] 在隔离副本验证 Ahneman QC 路径修复及端到端 Core v0.1 重建。
- [ ] 获取独立 evidence audit，记录 raw/manifest 判定。
- [ ] 在得到依赖安装授权后，建立固定的 Python 3.11 环境并完成 Parquet round-trip gate。

## Phase 4 续记：任务、split 与指标 candidate

- ADR 0006 已由独立 Round A 接受；S0–S5 的 seed、unit、held-out predicate、pair exclusion、source-stratified metrics 和 edge behavior 均已冻结。
- `data/processed/benchmark_v0_1_splits_candidate/` 是可复现的 record/pair split candidate；独立隔离重建 manifest 完全一致，S2/S5 group、S3 component、S4 tuple OOD 均通过。
- `metadata/benchmark_v0_1_task_split_feasibility_matrix.json` 的 84 leaves 中 64 supported、20 not_supported；后者仅为 Task 5/6 的合同规定非 S1 情形。
- 尚未训练模型、生成 prediction、计算 benchmark metric 或 promotion。下一步必须先审阅 Phase 5 baseline experiment contract。
