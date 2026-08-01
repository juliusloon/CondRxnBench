# 变更日志

本项目遵循 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/) 的分类方式；发布版本采用语义化版本号。尚未发布的工作放在 `Unreleased`，不可验证的计划不得写入“已发布”。

## Unreleased

### 新增

- 本地提升 `CondRxnBench-Benchmark v0.1`：Core v0.2、strict pairs/graphs、S0–S5 split、冻结 baseline predictions/leaderboard 与 hash-bound release manifest。
- 36 个可恢复 baseline shards、baseline verifier/metric materializer，以及 `chem` 默认验证运行时说明。

- Core v0.1 的统一数据层、schema、metadata、构建脚本和独立完整性校验。
- `STATUS.md`、`PROGRESS.md`、`ROADMAP.md`、`adr/` 和 `notes/`，用于可恢复、可追溯、可交接的项目维护。
- Phase 0 的相对路径 raw-input SHA-256 manifests、Python 3.11 runtime spec、Parquet round-trip verifier 与独立执行审计记录。
- Core v0.2 candidate 的 Parquet-authoritative records/controls、结构 assertions、source-scoped registry、continuous/mapping/mixture side tables、machine contract 与独立 Round B/C 审计记录；不含 benchmark pairs、graphs、splits、labels 或模型。

### 修复

- Ahneman QC 从仓库根目录定位输入；此前会错误查找 `scripts/data/`。
- condition registry entity ID 改为 source-scoped，避免将跨源同名 `XPhos` 在无证据时合并。

### 弃用

- 无。

## 0.1.0 - 待发布

### 新增

- 首个候选发布：Ahneman--Doyle 与 Perera 两套 HTE 主矩阵及严格单因素条件 pair。

### 修复

- 无。

### 弃用

- 无。
