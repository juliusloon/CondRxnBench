# CondRxnBench Core v0.2 -> Benchmark v0.1 execution state

本文件为 append-only 执行状态。原始输入不在此处复制；以仓库路径、hash 和命令引用。

## Iteration 1 — 2026-07-31 — Phase 0 preflight

### Hypothesis

在不修改 `data/raw/`、不覆盖现有工作树改动的条件下，可在隔离副本重建两源数据、Core v0.1 并验证其不变量；Ahneman QC 的失败来自可最小修复的仓库根路径解析错误。

### Inputs and hashes

- Git HEAD: `80ee279e1bfaeb0750807d2d09a15b1f4d1e2dd4`。
- 原始文件清单快照：`/private/tmp/condrxnbench_raw_current.sha256`，清单 SHA-256: `b5809076de73336be86d78ba1dbb71962b2ff5f14cfdb6b2d6ddc378acafc5c8`。
- Perera 工作簿 / 补充材料 hash 与 `HEAD:data/raw_metadata/perera_raw_input_manifest.json` 一致；主工作树中的该 manifest 当前由既有改动删除，未在主工作树恢复。

### Agent/role

- root: Phase 0 integrator。
- evidence_auditor: 独立输入/manifest 审计（进行中）。

### Files changed

- `scripts/Buchwald-Hartwig-HTE/qc_and_pairs.py`: 修正仓库根目录解析。
- 本状态文件与对应过程笔记。

### Commands run

- `python3 scripts/Buchwald-Hartwig-HTE/build_dataset.py`（隔离副本）
- `python3 scripts/Buchwald-Hartwig-HTE/qc_and_pairs.py`（修复前隔离副本，预期外失败）
- `python3 scripts/Suzuki-Miyaura-HTE/build_dataset.py`（隔离副本）
- `python3 scripts/Suzuki-Miyaura-HTE/qc_and_pairs.py`（隔离副本）
- `python3 scripts/build_core_v0_1.py`（隔离副本）
- `python3 tests/verify_core_v0_1.py`（隔离副本）

### Fast validation

- Perera 构建与 QC 通过；Core 重建输出 9,900 records、116,156 strict pairs，文件 hash 与既有 Core v0.1 manifest 相同；独立 verifier 通过。
- Ahneman QC 修复前失败：`parents[1]` 解析为 `<repo>/scripts`，错误查找 `<repo>/scripts/data/processed/...`。

### Full validation

- 待修复后在隔离副本完整重跑两源构建、QC、Core build 与 verifier。

### Independent review

- 进行中；不将 root 的诊断作为验收结论。

### Metrics and deltas

- 目标基线：Ahneman 4,140 main / 468 controls / 4,132 observed / 273 zero / 55,676 pairs；Perera 5,760 main / 275 zero / 60,480 pairs；Core 9,900 / 116,156。

### Reflection and failure mechanism

该错误是脚本路径层级的确定性 off-by-one，不涉及原始数据、规则或测量语义。修复仅使文档中的命令与实际仓库布局一致。

### Decision: revise

应用最小路径修复后，重新执行受影响的完整 Phase 0 验证及独立复核。

### Next single hypothesis

修正 `ROOT` 后，隔离副本中的 Ahneman QC 将从仓库级 `data/processed/` 读取输入，生成既有计数并使完整 Core v0.1 重建验证通过。

## Iteration 2 — 2026-07-31 — Phase 0 registry identity and runtime gate

### Hypothesis

将 condition entity ID 作用域限制到 `source_dataset`，可消除未经证据支持的跨源实体合并，而不改变 records、strict pairs 或原始输入。

### Inputs and hashes

- Iteration 1 raw snapshot 不变；Core v0.1 records/pairs hash 仍为 manifest 所列值。
- 发现条件词典 60 行中 59 个唯一 `component_id`：唯一碰撞是 Ahneman 与 Perera 的 `ligand=XPhos`。

### Agent/role

- root: 最小实现与隔离验证。
- evidence_auditor: 已独立审计 raw manifest 候选内容；待审计本轮 registry 身份修复与环境门禁。

### Files changed

- `scripts/build_core_v0_1.py`、registry ontology/API、Parquet round-trip verifier。
- 已加入候选 raw manifest、Phase 0 verifier、Proposed ADR 0003 和 Python 3.11 runtime spec。

### Commands run

- `python3 tests/verify_phase0_inputs.py`：20 个 raw inputs 通过。
- `python3 tests/verify_core_v0_1.py`：通过。
- 在临时 Python 3.11 环境运行 `tests/verify_parquet_roundtrip.py`：暴露未作用域的 registry ID。

### Fast validation

- 失败机制可重现且局限于同名 `XPhos` 的跨源 ID 碰撞；它不证明化学等价，因而不得共享 entity ID。

### Full validation

- 待在隔离副本重建 Core、验证新的 registry ID 唯一性、Parquet round-trip 和原始 hash 守恒。

### Independent review

- 候选 raw manifests 已由独立 evidence_auditor 复核通过，见 `reports/execution/phase0_candidate_manifest_review_2026-07-31.md`。
- 本轮 registry/runtime 审查待执行。

### Metrics and deltas

- 预期：registry 仍为 60 行但 `component_id` 唯一数从 59 改为 60；reaction records 9,900、pairs 116,156 不变。

### Reflection and failure mechanism

文本名称相同不能替代结构、证据或人工复核的跨源等价 mapping。该修正只改变条件词典标识符，不改动条件原始标签或记录级值。

### Decision: revise

完成 isolation rebuild、Parquet round-trip 和独立复核后才将此变更作为新的 Core 基线接受。

### Next single hypothesis

source-scoped ID 重建后，60 条 registry 的 `component_id` 将全部唯一，且 CSV-to-Parquet-to-DataFrame round-trip 保留所有主键、布尔值、数值和语义哨兵。

## Iteration 3 — 2026-07-31 — Phase 0 clean runtime revision

### Hypothesis

将实际调用但遗漏的 `openpyxl` 和 `tabulate` 固定到 Python 3.11 requirements，并以新的 acceptance 记录串联历史候选审计，可使全链路在干净环境中可复跑且 raw manifest 的状态无歧义。

### Inputs and hashes

- 20 个 accepted raw inputs 的 hash 均由 `tests/verify_phase0_inputs.py` 重算。
- records / pairs 保持原有 SHA-256；registry 预期保持 identity-only 新 hash `d757048413965999a22405c4485486082f0622c3463070097a4a4d9e1e115b40`。

### Agent/role

- root: environment contract 修订、受控主工作树重建与选择性暂存。
- independent_reviewer: Iteration 2 Round C 失败复核；Iteration 3 新鲜环境复核进行中。

### Files changed

- `environment/core_v0_2_py311_requirements.txt`：添加 `openpyxl==3.1.5`、`tabulate==0.10.0`。
- `reports/execution/phase0_manifest_acceptance_2026-07-31.md`：明确候选审计的时间顺序与正式 acceptance。
- 同步重建 `data/processed/core_v0_1/` 的 registry 与 manifest；仅 registry hash 变化。

### Commands run

- `uv pip install ... -r environment/core_v0_2_py311_requirements.txt`；`uv pip check`（32 packages compatible）。
- 在新的隔离副本以 Python 3.11 完整运行两源 build/QC、Core build、`verify_core_v0_1.py`、`verify_phase0_inputs.py`、`verify_parquet_roundtrip.py`。

### Fast validation

- 隔离副本全链路通过：4,140 Ahneman 主矩阵 / 468 controls / 55,676 pairs；5,760 Perera / 60,480 pairs；Core 9,900 / 116,156。
- records 与 pairs hash 未变；registry 为 60 rows / 60 unique IDs；Parquet round-trip 通过。

### Full validation

- 新鲜环境的独立 Round C 复核进行中；未通过前不 promotion。

### Independent review

- Iteration 2 复核为 FAIL，原因已记录在 `reports/execution/phase0_independent_review_2026-07-31.md`，未被改写。
- Iteration 3 复核必须验证 requirements、staged contract、acceptance chain 和完整命令链。

### Metrics and deltas

- 环境直接依赖从 8 项补足为 10 项；完整解析包从 29 项变为 32 项。
- 原始输入、records 和 pairs 无变化；registry ID 唯一数从 59 提升为 60。

### Reflection and failure mechanism

只列出数据分析包不足以复现实际 I/O 和报告路径。运行时合约必须由完整 build/QC 链而非单个 import 或 Core verifier 证明。

### Decision: revise

修订已经在 root 隔离副本验证，等待独立 reviewer 判定。

### Next single hypothesis

在新创建的 Python 3.11 环境中，仅依赖版本化 requirements 即可复跑全 Phase 0 命令链，并由独立 reviewer 解除 promotion blocker。

## Iteration 4 — 2026-07-31 — Phase 1 contract review

### Hypothesis

在不扩大结构证据边界的前提下，显式冻结 raw/normalized、source-scoped component、单位、outcome、quality 和 `NA` 语义，可为 Core v0.2 实现提供可审计且可独立审查的最小合约。

### Inputs and hashes

- Phase 0 accepted raw manifests、Core v0.1 9,900-record / 116,156-pair baseline。
- Phase 1 evidence coverage audit 和 schema-gap analysis。

### Agent/role

- evidence_auditor：只读 coverage 审计，结论为 v0.2 implementation 前的 contract FAIL。
- standardization_maker：只读 schema-gap analysis；root 整合为 Proposed ADR/config。

### Files changed

- Proposed ADR 0004、`configs/core_v0_2_contract.json`、ADR index 与本状态文件。

### Commands run

- Core/source coverage profile；`python3 tests/verify_core_v0_1.py`；两份独立只读审计。

### Fast validation

- 合约将 `NULL_COMPONENT`、`not_reported`、typed `NA` 和 observed zero 明确分离；禁止无 mapping 的跨源等价和结构补造。

### Full validation

- 待独立 reviewer 对 ADR/config 执行 Contract Review；此之前不生成 Core v0.2 候选数据。

### Independent review

- 待执行。

### Metrics and deltas

- 基线不变：9,900 records；Ahneman 4,132 observed/8 missing/273 zero；Perera 5,760 observed/275 zero；当前 Core pairs 116,156。

### Reflection and failure mechanism

审计已证明 source coverage 不均匀。把 4,140 条 Ahneman substrate SMILES 的 parse 成功率当作两个来源的 reaction coverage，或用 Perera 名称推断结构，都会制造伪证据。

### Decision: revise

将 Proposed contract 交由独立 reviewer；仅在 contract pass 后实现 v0.2 builder 和 validators。

### Next single hypothesis

独立 reviewer 能确认 ADR 0004 / contract 覆盖 Phase 1 sentinel、evidence、source-boundary 和 conservation hard gates，且不存在把结构缺失或空条件折叠的漏洞。

## Iteration 5 — 2026-07-31 — Phase 1 contract adversarial review

### Hypothesis

ADR 0004 与 v0.2 contract 已充分冻结 Phase 1 的数据语义，可安全进入 candidate data implementation。

### Inputs and hashes

- ADR 0004、`configs/core_v0_2_contract.json`、两份 Phase 1 只读审计和 Core v0.1 conservation baseline。

### Agent/role

- independent_reviewer：Round A adversarial contract review。

### Files changed

- `reports/execution/phase1_contract_review_2026-07-31.md`（reviewer report）与本 append-only state。

### Commands run

- JSON syntax、sentinel/source-boundary text scan、independent adversarial review。

### Fast validation

- JSON 合法且明确禁止 Perera 结构补造、跨源自动等价、空条件/缺失/零值折叠。

### Full validation

- FAIL：Round A 未通过，不能生成 Core v0.2 数据。

### Independent review

- FAIL，见 `reports/execution/phase1_contract_review_2026-07-31.md`。

### Metrics and deltas

- 无数据、raw hash、Core v0.1 records/pairs 或标签变化。

### Reflection and failure mechanism

- Contract 原则正确但无法作为实现规格：遗漏 Ahneman `substrate_1` 的 source-backed assertion 许可；缺 canonical/InChIKey/error/逐特征状态；未冻结盐/金属/离子/R-group 策略；mapping target/scope/attribute provenance、units/mixture、outcome domains/yield conservation 与 Arrow equivalence 均不足。

### Decision: revise

仅修订 Proposed ADR/config 与测试设计；重跑 Round A 前不改数据或 builder。

### Next single hypothesis

补足 reviewer 指出的所有字段、allowed-state、conservation 和 policy config 后，contract 将足以约束保守实现，并通过独立 Round A。

## Iterations 6–8 — 2026-07-31 — Phase 1 contract revisions

### Hypothesis

将结构、mapping、单位、状态、coverage 与 storage 的完整 machine contract 及其负向用例冻结后，可安全授权候选 v0.2 builder/validator 的最小实现。

### Inputs and hashes

- ADR 0004、`configs/core_v0_2_contract.json`、Core v0.1 conservation baseline。

### Agent/role

- independent_reviewer：连续 Round A adversarial reviews。

### Files changed

- ADR 0004、`configs/core_v0_2_contract.json`，以及 iteration 6–8 review reports。

### Commands run

- JSON parse、contract self-check、三次独立 Round A review。

### Fast validation

- proposed.3 冻结 Ahneman `substrate_1` allowlist、Perera default deny、source+role FK、closed continuous state domain、100%/>99% coverage gate、结构和 mapping 字段、保守 RDKit policy、每源 outcome conservation 与 Arrow/CSV equivalence。

### Full validation

- PASS：`reports/execution/phase1_contract_review_iteration8_2026-07-31.md`。

### Independent review

- Iteration 6/7 FAIL 已保留历史；Iteration 8 PASS，仅授权 candidate Core v0.2 builder/validator。

### Metrics and deltas

- 无 raw、Core v0.1、pair、graph、split、label 或模型变化。

### Reflection and failure mechanism

- Round A 只有当语义规则、版本身份和每项规则的负向反例都 machine-checkable 时才可通过；ADR prose 不能替代可执行 contract。

### Decision: promote

允许在新目录实现 candidate Core v0.2 标准化与 validators；不允许 promotion 或任何下游 benchmark 产物。

### Next single hypothesis

候选 v0.2 builder 可在不改变 v0.1/raw 的条件下，生成保守结构 assertions、source-scoped refs、units/mixture/outcome side tables和Parquet/CSV mirrors，并通过 contract validators。

## Iterations 9–10 — 2026-07-31 — Phase 1 candidate implementation and independent gates

### Hypothesis

在冻结的 proposed.3 contract 下，最小 candidate builder 可将 immutable Core v0.1 标准化为新的 Parquet-authoritative side-table layout，而不补造结构、不折叠 sentinel，也不生成任何 benchmark 关系或模型产物。

### Inputs and hashes

- 接受的 18 项 Ahneman 与 2 项 Perera raw-input manifests；Core v0.1 `reaction_records.csv`、`condition_registry.csv`、`condition_pairs.csv` 与 `manifest.json`。
- v0.1 strict-pair baseline：116,156；候选输出不包含该表。

### Agent/role

- standardization_maker：最小 builder/validator 实现。
- root：修复序列化比较与落盘 schema manifest，并在新 `core_v0_2` 目录整合候选。
- independent_reviewer：Round B clean-copy reproduction 与 Round C role/mapping adversarial audit。

### Files changed

- `scripts/build_core_v0_2.py`、`tests/verify_core_v0_2.py`、`data/processed/core_v0_2/`。
- ADR 0004、machine contract、data dictionary、dataset cards、API/architecture 与本 state 文件。

### Commands run

```bash
/private/tmp/condrxnbench-core-v0_2-py311/bin/python scripts/build_core_v0_2.py --out-dir /private/tmp/condrxnbench-core_v0_2-fresh2
/private/tmp/condrxnbench-core-v0_2-py311/bin/python tests/verify_core_v0_2.py --out-dir /private/tmp/condrxnbench-core_v0_2-fresh2
/private/tmp/condrxnbench-core-v0_2-py311/bin/python scripts/build_core_v0_2.py --out-dir data/processed/core_v0_2
/private/tmp/condrxnbench-core-v0_2-py311/bin/python tests/verify_core_v0_2.py --out-dir data/processed/core_v0_2
```

### Fast validation

- 修复 CSV/Parquet comparator 的 Arrow row 顺序、布尔文本和 nullable numeric 表示；manifest 改为记录 Parquet 落盘后的 schema fingerprint。
- 全新临时目录重建验证通过：9,900 records、468 controls、63 registry entities、108,900 structure assertions、108,900 continuous observations、11,520 mixture rows、2 pending mappings、0 attributes。

### Full validation

- workspace candidate 重建与 verifier 通过；Perera 没有 source-supported structure，Ahneman 仅四个 allowlisted roles 有 `source_reported` assertion。
- 记录/结果守恒：Ahneman 4,140/4,132 observed/8 missing/273 zero；Perera 5,760/5,760 observed/275 zero。
- CSV/Parquet 主键、行数、schema fingerprint、typed null/state、canonical JSON 和数值语义等价；candidate 无 pairs、graphs、splits、labels 或模型。

### Independent review

- Round B PASS：`reports/execution/phase1_independent_review_iteration9_2026-07-31.md` 在 clean copied worktree 重跑，20 raw 与四个 Core v0.1 文件 hash 均未变。
- Round C PASS：`reports/execution/phase1_independent_review_iteration10_2026-07-31.md` 完成每源/每 role 抽样、pending mapping 与 mixture 审计，并验证跨源/跨 role FK、Perera synthetic structure 和 domain-external continuous state 的构造负例被拒。

### Metrics and deltas

- 历史 records/pairs/labels 无变化；新增 candidate 仅包含标准化 records、controls 和审计 side tables。
- structure coverage 是 source/role 受限证据：Ahneman source-reported assertions 16,560（4 × 4,140）；Perera 63,360 均 `not_supported`。

### Reflection and failure mechanism

Parquet 的 map 子字段名会在持久化时规范化，清单必须对落盘 schema 而非内存 schema 指纹化；同时空字符串若被 typed numeric coercion 为 Arrow null，CSV mirror 必须显式写为 `NA`。这两项均为序列化层错误，未改变记录或科学语义。

### Decision: promote

Phase 1 candidate gate 已通过。ADR 0004 与 contract 接受用于 candidate build；`data/processed/core_v0_2/manifest.json` 仍明确为 `candidate_not_promoted`，因为它不是 Benchmark v0.1，且不授权下游 pairs/graphs/splits/labels/models。

### Next single hypothesis

先冻结 Benchmark v0.1 的 group、pair、graph、cliff 和 split 协议（Phase 2 Round A），再从 v0.2 candidate 全量枚举新的 pair universe；不得先看模型或高 delta 样本。

## Iterations 11–12 — 2026-07-31 — Phase 2 strict pair and graph candidate

### Hypothesis

将来源设计 group 与结构 group 明确分离，在完整 observed-record universe 上先枚举严格 pair、再计算 delta/cliff，并以 pair-ID 双射生成图，可得到不混入无证据结构推断的 Benchmark v0.1 strict candidate。

### Inputs and hashes

- `data/processed/core_v0_2/manifest.json`（`candidate_not_promoted`）和 immutable Core v0.1 strict-pair baseline 116,156。
- Phase 2 contract 记录 source×factor baseline：Ahneman catalyst_system/base/additive 为 6,187/4,124/45,365；Perera ligand/base/solvent_1 为 31,680/20,160/8,640。

### Agent/role

- root：协议修订、strict builder/validator 与 workspace candidate integration。
- independent_reviewer：Round A 合同审查（先 FAIL、修订后 PASS）以及 Round B/C clean-copy rebuild 和 pair 抽样审查。

### Files changed

- ADR 0005、`configs/benchmark_v0_1_group_pair_graph_contract.json`。
- `scripts/build_benchmark_v0_1.py`、`tests/verify_benchmark_v0_1.py`、`data/processed/benchmark_v0_1/`。

### Commands run

```bash
/private/tmp/condrxnbench-core-v0_2-py311/bin/python scripts/build_benchmark_v0_1.py --out-dir /private/tmp/condrxnbench-benchmark_v0_1-prototype2
/private/tmp/condrxnbench-core-v0_2-py311/bin/python tests/verify_benchmark_v0_1.py --out-dir /private/tmp/condrxnbench-benchmark_v0_1-prototype2
/private/tmp/condrxnbench-core-v0_2-py311/bin/python scripts/build_benchmark_v0_1.py --out-dir data/processed/benchmark_v0_1
/private/tmp/condrxnbench-core-v0_2-py311/bin/python tests/verify_benchmark_v0_1.py --out-dir data/processed/benchmark_v0_1
```

### Fast validation

- 首次 Round A FAIL 保留在 `phase2_contract_review_2026-07-31.md`：缺 source×factor ledger、universe-before-label invariant 和 graph schema；仅修 ADR/config 后 Iteration 11 Round A PASS。
- 临时输出验证：116,156 strict pairs、30 graphs、9,900 graph nodes、116,156 graph edges、6-row reconciliation ledger。

### Full validation

- workspace candidate verifier PASS：所有 pair 同源/同 group/observed/no self loop/one factor；primary cliff bins 与 20/40 pp sensitivity 语义闭合；node 集是全部 main records，edge 集与 pair IDs 双射。

### Independent review

- Round A PASS：`reports/execution/phase2_contract_review_iteration11_2026-07-31.md`。
- Round B/C PASS：`reports/execution/phase2_independent_review_iteration12_2026-07-31.md` clean-copy 重建/验证，并按六个 source×factor strata 确定性抽样 240 pairs；identity/group/observed yield/factor view/delta/pair_id 准确率 100.0%，关键 reaction identity error=0。

### Metrics and deltas

- strict pairs 与 v0.1 总量一致：116,156；pair counts 的 six-strata baseline 全部一致。
- Perera raw-solvent factor view 保留后，ledger 对 8,640 solvent pairs 记录 4,032 endpoint intersection、4,608 v0.1-only、4,608 current-only，理由为 `perera_raw_solvent_identity_preserved`；未把 pending mapping 当成 accepted。

### Reflection and failure mechanism

无 source×factor reconciliation 时，总数一致也可能掩盖 factor identity 改变；无 `pair_id` graph edge schema 时 endpoint 相同也可能掩盖边遗漏。两项均在实现前由 Round A 阻断并冻结为 machine contract。

### Decision: promote

Phase 2 strict pair/graph candidate gate 通过。`data/processed/benchmark_v0_1/manifest.json` 仍为 `candidate_not_promoted`；本次只生成 strict relationship layer，不含 extended pairs/graphs、splits 或 model results。

### Next single hypothesis

Phase 3 先对 strict candidate 执行 bias/confounding/leakage 审计并验证正负对照；任何 P0 风险未解除前，不冻结任务或 split。

## Iteration 13 — 2026-07-31 — Phase 3 bias, confounding and leakage audit

### Hypothesis

对 Core v0.2 和 strict Benchmark candidate 的来源、条件、pair 与 graph 关系执行可证伪审计，并用正负对照检验 audit predicate，可在 split/model 前发现自动 identity/group/pair leakage 与当前范围的 P0 风险。

### Inputs and hashes

- immutable raw/Core v0.1 与已验证 Core v0.2 / strict Benchmark candidate。
- `data/processed/benchmark_v0_1/strict_pairs.csv`、`graph_nodes.csv`、`graph_edges.csv`。

### Agent/role

- root：审计实现、两次 typed-read/serialization 缺陷的最小修复与重跑。
- independent_reviewer：clean-copy adversarial audit。

### Files changed

- `scripts/audit_phase3_bias_leakage.py`、`reports/execution/phase3_bias_leakage_audit_2026-07-31.json`。

### Commands run

```bash
/private/tmp/condrxnbench-core-v0_2-py311/bin/python scripts/audit_phase3_bias_leakage.py
/private/tmp/condrxnbench-core-v0_2-py311/bin/python -m json.tool reports/execution/phase3_bias_leakage_audit_2026-07-31.json
```

### Fast validation

- 首次运行暴露 `yield_percent` object mean 和 set/JSON tuple-key 序列化错误；仅修 audit typed-read/serialization 后重跑。
- 每项风险输出 `tested` / `not_testable` / `not_applicable`、量化/理由、impact 和 control。

### Full validation

- 自动 identity/group/pair：invalid pairs、duplicate pair IDs、duplicate graph edge keys 均为 0。
- measurement source/yield type 分离；缺失/零值、plate means、condition covariation、pair degree、controls isolation 均量化；scaffold/template 不支持与无预训练均明确标注，不伪装为通过。
- 审计正对照检测 synthetic cross-source，负对照接受实际 strict pair。

### Independent review

- PASS：`reports/execution/phase3_independent_review_iteration13_2026-07-31.md`。reviewer 在 clean copy 重跑并独立构造真实跨源 endpoint pair，predicate 明确拒绝；无 P0 或当前范围内未捕捉的关键 leakage。

### Metrics and deltas

- 控制与主矩阵 reaction IDs 重叠 0，pairs 引用 controls 0；8 个 Ahneman missing analysis records 是 graph isolated nodes，但不进入 observed-endpoint pairs。

### Reflection and failure mechanism

审计本身必须以数值类型和 JSON-safe key 运行，否则无法量化 plate/batch 风险；这类脚本错误不能被当作“无风险”。修复后同一审计还通过独立正负对照证明 predicate 非空转。

### Decision: promote

Phase 3 gate PASS；严格候选可进入 Phase 4 protocol-first 设计。该决定不生成 split、task label、metrics result 或模型。

### Next single hypothesis

冻结 Task 1–7 feasibility、S0–S5 split units/seed/held-out policy、pair partition rule 和 source-stratified metrics contract，再实施任何正式 split 或评价。

## Iterations 14–25 — 2026-07-31 — Phase 4 task/split/metrics protocol and split candidate

### Hypothesis

若先以 machine contract 冻结 Task 1–7、S0–S5、标签、pair partition、source-stratified metric edge behavior 与 test-first selection，再物化 record/pair manifests，则可在不读取数值 yield 或 pair labels 进行 held-out 选择的条件下得到可复现、可审计的 split candidate。

### Inputs and hashes

- Core v0.2 candidate manifest SHA-256：`101e9d5b1c29718d37f65e4b3a8dad77aa0edc415421b40bbe3b3e45ac1f05e2`。
- strict Benchmark candidate manifest SHA-256：`79066267d1b9a827565805195d907903631a64785e1afa407339395c21c78e33`。
- 接受的 split/metrics contract：`CondRxnBench-Benchmark-v0.1-task-split-metrics-accepted.2`，SHA-256 `c0763c551752dacbeba04edf542e030a0db3d751ece7d2a14e905b157e56f76b`，seed `20260731`。

### Agent/role

- root：合同最小修订、split builder/verifier 与 candidate integration。
- phase4_reviewer：独立 Round A 合同审阅（iterations 14–24）及 Round C split 对抗审计（iteration 25）。

### Files changed

- ADR 0006、`configs/benchmark_v0_1_task_split_metrics_contract.json`、21-case metric fixture/verifier、feasibility matrix builder。
- `scripts/build_benchmark_v0_1_splits.py`、`tests/verify_benchmark_v0_1_splits.py`、`data/processed/benchmark_v0_1_splits_candidate/`。
- Phase 4 review reports、feasibility matrix 与本 state/过程笔记。

### Commands run

```bash
/private/tmp/condrxnbench-core-v0_2-py311/bin/python tests/verify_metrics_v0_1_toy.py
/private/tmp/condrxnbench-core-v0_2-py311/bin/python scripts/build_benchmark_v0_1_splits.py
/private/tmp/condrxnbench-core-v0_2-py311/bin/python tests/verify_benchmark_v0_1_splits.py
/private/tmp/condrxnbench-core-v0_2-py311/bin/python scripts/build_benchmark_v0_1_splits.py --out-dir /private/tmp/condrxnbench_splits_rebuild_accepted2
/private/tmp/condrxnbench-core-v0_2-py311/bin/python tests/verify_benchmark_v0_1_splits.py --out-dir /private/tmp/condrxnbench_splits_rebuild_accepted2
```

### Fast validation

- Round A 的历史 FAIL 均保留为 `phase4_contract_review_iteration14` 至 `22`：逐项补足 source-free task scope、fixture coverage、Pearson/variance/negative behavior 与 fixture-key closure；iteration 23 PASS。
- S5 source-specific tuple roles 随后显式写入 accepted.2；iteration 24 独立复核 PASS，未改变 seed、threshold、metrics 或 held-out predicate。
- 21 个 required fixture keys 与 toy fixture 精确闭合；metrics boundary/negative verifier PASS；matrix config/input provenance 与 84 leaves 通过静态检查。

### Full validation

- candidate 输出 54,602 条 record assignments、423,645 条 same-partition pair assignments、273,291 条 pair exclusions；S5 的 4,750 个非对角 group×tuple records 在独立 record exclusion ledger 中明确保留。
- S0–S4 覆盖每个 source 的全部 observed main records；S5 只保留同 partition 的 group×tuple 对角 cells，train/val/test 均非空。
- 同一 accepted.2 输入在隔离目录重建得到 byte-identical manifest 与六个关键 CSV hashes；workspace 和隔离 verifier 均 PASS。
- feasibility matrix v3：64 leaves `supported`；20 leaves `not_supported`，且全部是合同明确限制的 Task 5/6 非 S1，不生成空评分。

### Independent review

- Round A PASS：`reports/execution/phase4_contract_review_iteration23_2026-07-31.md`；S5 roles 澄清后 iteration 24 PASS。
- Round C PASS：`reports/execution/phase4_split_independent_review_iteration25_2026-07-31.md`。独立临时重建、hash comparison 与对抗检查确认 S2/S5 group、S3 component、S4 tuple+marginal、S5 diagonal 双 OOD、pair endpoint/ledger coverage 与 test-first predicate 均符合合同。

### Metrics and deltas

- 所有 12 个 source×split record partition 均非空；Ahneman/Perera 的 S5 分别保留 2,134/3,008 records（其余 1,998/2,752 明确排除）。
- 64 个可支持叶节点尚无模型预测或指标结果；candidate manifest 显式列出 `model_predictions`、`metric_results`、`benchmark_promotion` 为未实现。

### Reflection and failure mechanism

将 fixture case ID 误放入 Task 5 metric list、或让 S5 tuple role 仅由代码注释继承，都会把测试覆盖/实现假设混同于科学协议。两处均在生成可接受 split 前被独立审阅阻断，并以最小 contract 修复和全量重建解除。

### Decision: promote

Phase 4 split candidate gate PASS。ADR 0006 已接受用于 split materialization；`benchmark_v0_1_splits_candidate` 仍为 `candidate_not_promoted`，不代表 Benchmark release，也不授权任何模型、预测、结果或 leaderboard 声明。

### Next single hypothesis

冻结 Phase 5 baseline experiment contract（family eligibility、features、seed、train/val-only tuning、negative controls、prediction schema 与 resource budget）并经独立 review 后，才训练任何候选基线。

## Iterations 26–32 — 2026-07-31 — Phase 5 baseline materialization

### Hypothesis

冻结的 train/val winner、source-stratified test predictions、显式 N/A/negative controls 和 contract-bound metrics 可在不接触 test 选择的条件下物化并独立复验。

### Full validation and independent review

- 36 个 source×split×seed shards 聚合为 216 formal、108 control、239,652 prediction；freeze hash 为 `c02ebfe1dd06ddecd2a76737cfb6e08ecd5ef8cd079acfb5f838ae5c6da9d8fb`。
- `scripts/verify_benchmark_v0_1_baselines.py` 通过；Task 1–7 metric ledger 为 4,140 rows / 1,208 summaries，Task 5 S1 包含 Spearman/NDCG/top-1/3/5，Task 5/6 非 S1 360 格显式 N/A。
- `phase5_baseline_implementation_review_iteration32_2026-07-31.md`：PASS。

### Reflection and decision

长 CPU run 的前台工具回收会造成空 candidate；runner 改为 staging，且正式 materialization 由可独立验证的 source×split×seed shards 原子聚合。新 `chem` 环境用于验证和指标，冻结 winner 仍依赖 Python 3.11/sklearn 1.5.2，以避免语义不一致。

### Decision: promote

Phase 5 baseline gate PASS；进入 Phase 6 maintenance handoff。

## Iteration 33 — 2026-07-31 — Phase 6 final release and handoff

### Final acceptance evidence

- release wrapper：`releases/condrxnbench-benchmark-v0_1/manifest.json` 的四项输入 SHA-256 精确匹配。
- final matrix：Phase 0 inputs、Core v0.1/v0.2、Benchmark pairs/graphs、S0–S5 splits、metric toy/boundary cases 与 baseline freeze verifier 全部 PASS。
- independent final review：`reports/execution/final_independent_review_2026-07-31.md` PASS，残留 P0 为 0。

### Decision: complete

本地 `CondRxnBench-Benchmark v0.1` 已提升。候选目录保留为不可改写的 provenance layer；release wrapper 是交付边界。后续模型、结构证据或数据源扩展必须建立新 goal、freeze 和版本。
