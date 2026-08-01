# 阶段进展

本文件保留已发生阶段的简明、可追溯记录。当前工作状态以 `STATUS.md` 为准；重大技术取舍以 `adr/` 为准。

## 2026-07-31 — Benchmark/Baseline v0.1 本地提升与交接

### 已完成

- 新增 hash-bound `releases/condrxnbench-benchmark-v0_1/manifest.json`，提升已审计的 Core v0.2、strict pair/graph、S0–S5 split 和 baseline leaderboard，保留所有候选层 provenance。
- 基线以 36 个 source×split×seed shards 恢复并原子聚合；216 formal、108 control、239,652 prediction、4 个 structural-family N/A 与 4,140 metric rows 均通过独立终审。
- `chem` 环境补齐 scikit-learn/pytest 并通过核心 verifier、split verifier 和 metric toy verifier。

### 风险与下一步

- 不同 source 的 absolute yield 不可比较；结构不足的两个模型家族保持 N/A；Task 5/6 仅在 S1 适用。
- 下一步只能以新 goal 增加完整结构证据、额外 baseline 或新来源，并创建新的 freeze/version。

## 2026-07-31 — Core v0.2 candidate Phase 1：标准化与三道独立门禁通过

### 已完成

- 冻结并接受 ADR 0004 / `configs/core_v0_2_contract.json`：source-scoped registry、结构 allowlist/default deny、typed `NA`、显式 `NULL_COMPONENT`、outcome/continuous state、mixture/mapping 与 Parquet/CSV 等价规则。
- 从 immutable Core v0.1 生成 `data/processed/core_v0_2/`：9,900 主记录、468 controls、63 registry entities、108,900 structure assertions、108,900 continuous observations、11,520 mixture rows 和 2 条 pending mapping。
- 验证所有 v0.1/raw 输入不变；候选不包含 v0.2 pairs、graphs、splits、labels 或模型。
- 独立 reviewer 完成 Round B clean-copy reproduction 与 Round C mapping/role adversarial audit，均 PASS。

### 限制与下一步

- `manifest.json` 刻意保留 `candidate_not_promoted`；它是可供 Phase 2 协议工作消费的标准化层，不是 Benchmark v0.1 发布。
- 下一步先进行 Phase 2 Round A：协议/ADR/config 独立审查，再全量构建新的 pairs 与 graphs。

## 2026-07-31 — Core v0.2 / Benchmark v0.1 Phase 0：基线、环境与恢复契约通过

### 已完成

- 固化两源实际 reconstruction inputs 的相对路径 SHA-256 manifests；独立审计覆盖 Ahneman 18 项与 Perera 2 项，未恢复或覆盖既有删除的 `data/raw_metadata/perera_raw_input_manifest.json`。
- 修复 Ahneman QC 的仓库根目录解析，并将 condition registry ID 限制为 source-scoped；registry 为 60 行 / 60 个唯一 ID，records/pairs 的历史 hash 不变。
- 固定并独立验证 CPython 3.11 runtime（RDKit、pyarrow、scikit-learn、openpyxl、tabulate 等），完成 CSV-to-Parquet-to-DataFrame 语义 round-trip。
- 独立 reviewer 在新隔离副本完整重跑两源 build/QC、Core build、raw/Core/Parquet verifiers，结论 PASS。

### 新增/变更

- `environment/core_v0_2_py311_requirements.txt`、Phase 0 raw manifests/verifiers、执行审计报告和 Proposed ADR 0003。
- `condition_registry.csv` 与 manifest 的 registry hash 更新；跨源同名条件默认不共享 entity ID。

### 验证

- 见 `reports/execution/phase0_independent_review_iteration3_2026-07-31.md`。
- 结果：通过；raw 20 项 hash、9,900 records、116,156 pairs、60 unique registry IDs 与 Parquet round-trip 均通过。

### 问题与风险

- ADR 0003 仍为 Proposed；尚未发布 Core v0.2 Parquet、标准化 schema、benchmark split/label 或模型结果。
- 不同来源的绝对产率仍不可合并比较；结构缺失必须作为 coverage 报告，不能补造。

### 下一步

- [ ] 冻结并独立审查 Core v0.2 structure/condition/outcome/quality schema 合约，明确每个字段的 evidence 与 missingness 语义。

## 2026-07-31 — Core v0.1 统一可审计层完成，进入预发布

### 已完成

- 将两套 HTE 主矩阵统一为 Core v0.1：共 9,900 条反应记录和 116,156 个 `n_changed_factors = 1` 的 strict pair。
- 建立机器可读 schema、数据字典、条件词典、两份 dataset card 和带 SHA-256 的 manifest。
- 提供 `scripts/build_core_v0_1.py` 与独立的 `tests/verify_core_v0_1.py`，用于重建与完整性验证。
- 已运行独立校验，确认 9,900 条记录、116,156 个 strict pair 及主键/标签/pair 不变量。
- 将 `success_label`、`cliff_label` 显式保留为 `not_assigned`，避免在阈值策略确定前伪造标签。

### 新增

- `configs/core_v0_1_schema.json`
- `metadata/` 下的统一 schema、数据字典、条件本体规则和 dataset cards
- `data/processed/core_v0_1/` 的 CSV、manifest 与条件词典

### 问题与风险

- 缺少兼容的 RDKit、scikit-learn、pyarrow 运行环境，分子基线与 Parquet 还不能作为已验证成果。
- Ahneman--Doyle 与 Perera 的测量语义不同，跨源绝对产率比较仍不成立。

### 下一步

- 运行并记录 Core v0.1 发布前完整性检查。
- 设计并预注册 benchmark 划分、success 阈值和 cliff 敏感性方案。
- 在专用环境中执行化学特征基线，并按数据源分层报告。

## 2026-07-30 — Perera Suzuki--Miyaura HTE 原始数据归档与 QC

### 已完成

- 固化 `rxn4chemistry/rxn_yields` 指定提交中的 `aap9112_Data_File_S1.xlsx`，保留来源与校验信息。
- 重建 5,760 条主矩阵记录，保留显式空白 ligand/base 和 275 条观测零产率。
- 生成 60,480 个单因素 pair；响应标记为 UV-area 结果而非 isolated yield。

### 问题

- 上游补充 PDF 访问受 Cloudflare 影响；不能将未取得的证据写成已审计事实。

### 下一步

- 将该数据源与 Ahneman--Doyle 的可比字段按统一 schema 发布，并保持测量语义分层。

## 2026-07-29 — Ahneman--Doyle HTE 重建与条件配对

### 已完成

- 固化并校验来自 `doylelab/rxnpredict` 的原始输入，从逐孔分析导出和板布局重建 4,140 条主矩阵。
- 将 468 条对照独立保存；主矩阵保留 8 条分析缺失和 273 条观测零产率。
- 在固定 `reaction_group_id` 内生成 55,676 个单因素 pair，变化因素限于 `catalyst_system`、`base` 或 `additive`。

### 问题

- 当前环境未能运行 RDKit/scikit-learn，因此没有把未经验证的代理结果伪装成 baseline。

### 下一步

- 接入第二个 HTE 源，建立统一 schema，并准备泄漏安全的评测协议。
