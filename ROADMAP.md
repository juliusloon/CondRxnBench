# 路线图

优先级按可复现性与结论风险排序，而非按实现便利性排序。完成时将条目移入 `PROGRESS.md`，并更新 `STATUS.md`。

## 已完成 — Phase 0：固定 Core v0.1 可复跑基线

- [x] 运行 `python3 tests/verify_core_v0_1.py`，已确认 9,900 条记录与 116,156 个 strict pair 的核心不变量。
- [x] 审核 Core CSV、manifest、source manifests、构建脚本和 verifier；独立 clean-environment review 通过。
- [x] 记录 condition registry 的 source-scoped ID 修复和环境兼容性约束；发布标签/commit 仍需用户另行授权。

**完成标准：** 从原始输入执行构建与校验后，得到 9,900 条记录和 116,156 个 strict pair，且 manifest 一致。

## 已完成 — P1：Core v0.2 candidate 标准化合约与证据覆盖

- [x] 写入并独立审查 structure evidence、condition entity、单位、outcome 与 quality grade 的版本化 schema/config；保留 raw/normalized 双字段。
- [x] 报告每源、每角色的结构覆盖、parse/sanitize 结果、error class 与 disposition；不以缺失结构伪造特征或过滤历史 records。
- [x] 生成 candidate Parquet + CSV mirror，验证 v0.2 schema/语义守恒，并更新 data dictionary/dataset cards。

**完成标准（已满足，candidate 层）：** 9,900 条历史主矩阵 records 完整保留，所有 mapping 可追溯且由独立 reviewer 审查；Core v0.2 candidate schema、Parquet 和 coverage/QC 通过。

## 已完成 — P2：Benchmark 协议与 S0–S5 划分

- [x] 定义并版本化 S0–S5、strict pair partition、30 pp cliff 与 source-stratified metrics。
- [x] 物化并独立复核 record/pair manifests 和 84-cell feasibility matrix。

**完成标准：** 协议可由第三方从 Core 数据重跑，且任何阈值都可追溯到 ADR 与版本化配置。

## 已完成 — P3：Baseline leaderboard v0.1

- [x] 固定并验证六个有效 baseline families、三个 seeds、negative controls、N/A/failure ledger 和预测级 provenance。
- [x] 输出 source-stratified absolute/pair/direction/cliff/ranking/recommendation metrics 与完整 N/A coverage。

**完成标准：** 不依赖不可审计的代理特征，基线结果可复跑且不跨测量语义混报。

## P4 — 下一版本或研究 goal

- [ ] 在符合许可、具备原始证据和字段映射的前提下接入 ORD/CRD、文献优化表、专利或 ELN。
- [ ] 对每个新来源新增 dataset card、来源清单、质量审计和条件词典映射。
- [ ] 仅在结构与反应变换被验证后，扩展 reaction-level / product-level 任务。

**完成标准：** 每个新增来源均能独立重建、审计与按测量语义评测。
