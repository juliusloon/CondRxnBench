# Dataset Card：Perera Suzuki--Miyaura HTE

## 身份与范围

- 来源：Perera *et al.*, *Science* 2018, DOI 10.1126/science.aap9112。
- 原始表 `aap9112_Data_File_S1.xlsx` 固定自 `rxn4chemistry/rxn_yields` 提交 `d9e6b87ce1b881978490d68bfc00021e3b48127a`；原始文件 SHA-256 与来源说明见 `data/raw/perera_suzuki_miyaura/SOURCE.md`。
- Core 记录：5,760（15 substrate pairs × 12 ligand settings × 8 base settings × 4 carrier solvents）。

## 响应与质量

- 响应为 `Product_Yield_PCT_Area_UV`，Core 标记为 `lc_ms_uv_area_percent_reported`，测量方法为 `UPLC-MS/DAD; UV area percent`。
- 5,760 条响应均被观测，275 条为真实零值；不能把它们改写为 isolated yield 或缺失。
- 原始 `None` 配体/碱被规范为 `NULL_COMPONENT`，是实际条件水平而非空值。
- `MeOH/H2O_V2 9:1` 和 `THF_V2` 的载体溶剂规范化保留在处理表，原始标签不删除。

## 配对与适用任务

- 60,480 个 strict pair；在同一 electrophile×nucleophile 组内仅改变 `ligand`、`base` 或规范化 `solvent_1`。
- 适用于 leave-one-substrate、component OOD、组合 OOD 和条件可迁移性研究。
- 底物及产品结构在当前可审计来源中未建立，故 SMILES 字段为 `not_reported`，不使用推断结构填补。

## 限制

所有结果来自单一 Suzuki--Miyaura 流动 HTE 设计。与 Ahneman 跨源比较时，应按来源分层；优先比较组内相对条件效应。

## Core v0.2 candidate 标准化状态

v0.2 candidate 保存 source-scoped condition registry、`NULL_COMPONENT`、连续字段状态和 9:1 mixture composition，但没有将名称推断为结构：全部 Perera structure assertions 均为 `not_supported`，不会产生伪 SMILES、InChIKey 或 fingerprint。两条 legacy solvent 规范化行仍是 `pending` mapping，主记录继续引用来源 raw entity。
