# ADR 0004: Core v0.2 的证据保留标准化与缺失语义合约

## 状态

Accepted for Core v0.2 candidate build — 2026-07-31

## 背景

Phase 1 审计确认 Core v0.1 的 9,900 条 records、来源感知 outcome 语义与 strict-pair 基线可信，但缺少 raw/normalized 双字段、mapping evidence/review、结构 QC/disposition 和明确的 `NA` 合约。Ahneman 固化输入提供 aryl-halide、additive、base 和自由 ligand-component 的 SMILES；它不提供 pre-formed `catalyst_system`、第二底物、产品或 atom-mapped reaction 的结构证据。Perera 固化工作簿和 PDF 也不提供完整逐行的结构映射。

## 提议决策

1. Core v0.2 在新版本目录交付，逐字段保留 Core v0.1 值；不修改 `data/raw/`，不覆盖 v0.1，且不删除任何 record。
2. 结构、条件映射和条件组成使用 versioned side tables。所有结构保留 raw value、source artifact/locator、normalized/canonical values、RDKit parse/sanitize 状态、error/disposition 与 reviewer 状态；无证据的结构以 `not_reported`/`not_supported` 明示，而不是推断。
3. Ahneman 的 component-list SMILES 只可用于 `ligand`、`base`、`additive` 条件实体和 `substrate_1` 的 source-backed assertions。`catalyst_system` 保持原子性；不从 ligand 推导其结构。Perera substrate/product/reaction structures、atom mapping 和 bond changes 均保持 `not_reported`/`not_supported`。
4. `component_id` 永远 source-scoped。跨源同名、同结构或同义名称都不自动等价；非恒等 name/role/unit/structure mapping 必须有 evidence locator、rule/version 与独立 reviewer 的 accepted 状态。
5. `NULL_COMPONENT` 是来源报告的显式实验水平，永远不是 null 或 `not_reported`。`not_reported` 是文字语义哨兵，不是 registry entity。`NA` 只表示 typed missing/not-applicable 序列化：Parquet 为 Arrow null 并带显式 state，CSV mirror 为保留 token `NA`；CSV reader 必须禁用对 `NA`、`not_reported`、`NULL_COMPONENT` 的默认缺失转换。观测零值必须保持数值 0、`yield_observed=true`、`zero_yield=true`，不能变为任何缺失/检测限制状态。
6. 连续字段保留 raw value、raw unit、normalized value/unit、conversion rule 与 evidence。无单位证据不转换；Perera mixture solvent 保留 raw label、每个组分和 9:1 比例。绝对产率不会跨 `source_dataset`/`yield_type` 校准或合并。
7. `quality_grade` 的证据基础与 `eligibility_status` 分离；后者默认 `not_assessed`，不能作为训练过滤或倒推质量的依据。
8. 结构身份策略固定为保守默认：没有 source-backed、versioned rule 的情况下不去盐/选主成分、不拆金属或离子对、不处理 R-group 标记；只对成功 sanitize 的、允许角色的 source-backed SMILES 使用固定版本 RDKit canonical isomeric SMILES。任何失败保留 raw value，记录 error class/disposition，且不生成 feature。
9. 每个结构 assertion 保存 raw/normalized/canonical/InChIKey、assertion/version、parse 状态、error、逐项 feature status/reason、evidence 和 review；每个 non-identity mapping 保存显式 target/target scope、mapping/rule version、evidence/reviewer/disposition。连续值、组成比例与属性同样保存 raw/normalized、rule/version、evidence；属性必须标记为 `evidence_backed` 或 `derived`。
10. machine contract 必须冻结每源 observed/missing/zero counts、主键、Arrow logical types/schema fingerprint、canonical JSON CSV encoding 与跨格式等价检查；v0.2 build 以此作为 release blocker。
11. 每个 record→component reference 必须解析到同一 `source_dataset`、同一 role 的唯一 registry entity。Perera 没有任何获准的 condition-structure role；所有未列入 source allowlist 的 role 默认 `not_supported`。连续 observation 的 `value_state` 只能为 `observed_numeric`、`NA` 或 `not_reported`；每源明确列出的离散条件 role 必须达到 100% state coverage，且有效或显式空条件完整率至少 99%。

## 后果

- v0.2 新增 records extensions、structure assertions、registry/mapping 和 composition side tables，以及正式 Parquet 与 CSV mirrors。
- parse success 只在“source-backed 且声明可解析”的子集上计算；结构 coverage 单独按源/角色报告。
- 每个 non-identity mapping、结构失败和不支持特征都需要可审计 disposition，增加实现和审查成本。
- 本 ADR 未接受前不得生成正式 Core v0.2 产物、重建 pair/graph、split、cliff label 或模型结果。
