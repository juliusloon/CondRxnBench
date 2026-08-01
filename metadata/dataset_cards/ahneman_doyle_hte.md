# Dataset Card：Ahneman--Doyle Buchwald--Hartwig HTE

## 身份与范围

- 来源：Ahneman *et al.*, *Science* 2018；重建输入固定自 `doylelab/rxnpredict` 提交 `57e15fdb7f7483c6bf3a601df69f6ac9e5af6965`。
- Core 记录：4,140 个主矩阵单元（15 aryl halides × 4 pre-formed Pd--ligand catalyst systems × 3 bases × 23 additives）。
- 不纳入 Core 的对照：468 条，单独保留在 `data/processed/ahneman_buchwald_hartwig_controls.csv`。
- 原始层：`data/raw/ahneman_doyle_rxnpredict/`；重建脚本：`scripts/Buchwald-Hartwig-HTE/`。

## 响应与质量

- 响应为逐孔 LC/UV 导出经内标校正的 `product_scaled` 百分数；**不是已验证的 isolated yield**。
- 4,132 个观测结果，8 个分析结果缺失，273 个真实零产率。Core 保留全部 4,140 个设计单元和缺失指示；8 个没有原始分析导出路径的设计单元在规范表中明确标为 `not_reported`，而非补造孔位来源。
- 每个四因子组合一次，设计覆盖率 100%；QC 见 `reports/Buchwald-Hartwig-HTE/ahneman_qc_report_zh.md`。

## 配对与适用任务

- 55,676 个 strict pair；固定 aryl halide，仅改变 `catalyst_system`、`base` 或 `additive` 中的一个。
- 用于 within-group 条件补全、条件效应、条件排序和因素分层分析。
- `reaction_group_id` 当前按 aryl halide 实验设计建立；产品、完整反应 SMILES 和键变化尚未在本版证实，均保持 `not_reported`。

## 限制

这是单一 C--N 偶联体系，且 `catalyst_system` 是不可强行拆分的预形成体系。其绝对响应不应与 Perera 的 UV-area response 混合汇总。

## Core v0.2 candidate 标准化状态

v0.2 candidate 对 4,140 条主矩阵逐条保存结构 assertion。仅原始 component lists 支持 `substrate_1`、`ligand`、`base`、`additive`；这四个 role 的 source-reported SMILES 均经固定 RDKit 版本 parse/sanitize/canonicalize 并保存 InChIKey。`catalyst_system`、第二底物、产品、atom mapping 和 bond changes 仍为 `not_supported`，不会补造 feature。
