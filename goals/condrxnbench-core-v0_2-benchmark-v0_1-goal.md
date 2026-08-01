# CondRxnBench Core v0.2 → Benchmark v0.1 Goal Loop

> 状态：**Draft for human review — 禁止执行**  
> 启动口令：仅当用户明确批准本文件版本并要求执行后，才进入 Phase 0。  
> 适用仓库：`/Users/juliusloon/Documents/Files/data/CondRxnBench`  
> 依据：`CondRxnBench Proposal.md` 第 5–13 节、`docs/maintenance-workflow.md`、ADR 0001–0002。

## 1. Goal

将当前仅完成来源重建和初步 strict pair 的 **Core v0.1**，推进为：

1. **CondRxnBench-Core v0.2**：两套 HTE 数据的结构、条件实体、结果语义与质量状态经过版本化标准化；
2. **CondRxnBench-Benchmark v0.1**：拥有经审计的 reaction groups、strict pairs、condition graphs、S0–S5 划分、Task 1–7、指标库和可信基线；
3. **完整维护交接**：任何新执行者只读仓库即可恢复环境、输入、决策、命令、结果、失败和下一步。

最终完成不是“脚本能运行”，而是所有硬门禁均由可重跑命令、独立 reviewer 和维护记录共同证明。

## 2. Scientific acceptance boundary

以下证据层级不得混淆：

1. **Raw evidence**：固化的论文/SI/上游仓库原始输入与 hash；
2. **Reconstructed evidence**：Core v0.1 的逐条实验和初步 pair；
3. **Standardized evidence**：Core v0.2 中经 schema、registry、RDKit/QC 验证的字段；
4. **Benchmark-valid evidence**：通过 group、pair、graph、split 和 leakage 审计的任务数据；
5. **Model evidence**：只在适用数据源、任务和 split 上得到的可复跑结果。

低层证据不能被改名成高层成功。以下做法一律禁止：

- 修改或覆盖 `data/raw/`；
- 把 `not_reported`、`NA`、`NULL_COMPONENT` 和观测零值互换；
- 把两数据源的绝对产率混报；
- 为了凑齐结构特征而补造底物、产物、atom mapping 或反应中心；
- 从高 `abs_delta_yield` 样本反推 pair；必须先完整枚举 pair；
- 看过测试结果后再选择阈值、held-out component、seed 或 split；
- 用同一 agent 同时完成高风险规则的实现和最终批准；
- 将“不支持”伪装成 0 分、缺失模型或成功结果。

## 3. Baseline facts and prerequisites

执行前必须重新验证，不能只凭本文件相信：

- Ahneman 主矩阵 4,140 条、独立 controls 468 条、观测结果 4,132 条、观测零值 273 条、初步 strict pairs 55,676 条；
- Perera 主矩阵 5,760 条、观测零值 275 条、初步 strict pairs 60,480 条；
- Core v0.1 合计 9,900 条 records、116,156 条 pairs；
- `success_label` 和 `cliff_label` 当前均为 `not_assigned`；
- 当前 Python 3.13 缺少可用 RDKit、scikit-learn、pyarrow；
- 工作树存在未提交/未跟踪内容，任何执行不得覆盖不属于本 goal 的用户修改。

基线必读文件：

- `STATUS.md`, `PROGRESS.md`, `ROADMAP.md`, `CHANGELOG.md`；
- `docs/architecture.md`, `docs/api.md`, `docs/maintenance-workflow.md`；
- `metadata/`, `configs/core_v0_1_schema.json`；
- `adr/0001-*`, `adr/0002-*`；
- 两份 source metadata、QC reports 和 Core v0.1 manifest；
- proposal 第 5–13 节。

## 4. Loop contract

### TRIGGER

- Required：用户明确批准本 goal 的具体版本并发出执行指令。
- Forbidden：仅因 goal 文件存在、线程自动继续或 agent 认为“下一步显然”而启动。

### SCOPE

Required：只处理当前两套 HTE Core、其 controls、标准化、关系层、benchmark、指标和基线。

Allowed：从仓库内已固化论文/SI恢复缺失结构证据；必要时使用权威公开数据库核验，但必须记录来源、版本和许可。

Out of scope：新增 ORD/ELN/专利/39k HTE；CYC-Loss/CondFormer 的正式论文结论；付费云训练；任何外部发布、push 或 PR，除非用户另行授权。

### ACTION

每轮固定执行：

```text
diagnose → one falsifiable hypothesis → minimal implementation
→ fast validation → full validation → independent review
→ reflect → promote / revise / revert / stop
```

每轮只能有一个主要科学或数据语义变量。纯机械迁移可以批量执行，但必须单独验证。

### BUDGET

- 并发上限：4 个 agent（root + 最多 3 个 subagents）；
- 总闭环轮数上限：24；任一 phase 最多 5 轮；
- 同一 blocker 连续失败上限：3 轮；
- 单次人工启动的 wall-clock 上限：6 小时；到点必须落盘 state 后停止；
- 默认本地 CPU；使用 GPU、付费 API、云训练或新外部服务必须另行获得用户授权；
- 不设置隐含 token/cost 预算；若运行环境提供显式预算，以更严格者为准。

### STOP

出现任一条件立即停止当前执行并保存证据：

- raw hash 发生非预期变化；
- 需要无证据补造结构、测量方法或实验条件才能继续；
- 同一 blocker 连续 3 轮没有新增可执行信息；
- reviewer 发现身份泄漏、pair 泄漏或测试污染且无法在当前假设内修复；
- 只有低优先级指标改善，但严格证据指标退化；
- 运行超出批准的权限、资源或数据许可；
- 工作树冲突可能覆盖用户修改。

停止时不得标记 goal complete；必须写明 blocker、已尝试轮次、保留产物和恢复命令。

### REPORT

每轮追加 state；每个 phase 更新过程笔记；最终按 maintenance 清单更新全部维护入口。任何“通过”必须附命令、输入版本和输出路径。

## 5. Agent topology

Root agent 是 orchestrator/integrator，不得用自己的主观判断代替独立验收。

| 角色 | 主要职责 | 可修改范围 | 禁止事项 |
|---|---|---|---|
| `evidence_auditor` | 核对 raw、来源、字段覆盖、许可、测量语义；提出 evidence gaps | 默认只读；可写 audit report | 不实现自己审计的高风险转换 |
| `standardization_maker` | 结构、condition registry、单位、outcome、QC 实现 | `condrxn/chemistry`, `conditions`, `outcomes`, configs/tests | 不批准自己的 mappings 或 quality grade |
| `benchmark_maker` | groups、pairs、graphs、splits、metrics、baselines | `grouping`, `pairs`, `graphs`, `splits`, `metrics`, `baselines` | 不单独接受 split/cliff 协议 |
| `independent_reviewer` | 对候选产物做 adversarial audit、负对照和重跑 | tests/reports；修复建议默认只读 | 不直接改被审对象后立即批准 |
| root | 选择单一假设、协调依赖、解决冲突、执行 promotion | 集成与文档 | 不绕过 reviewer 或 circuit breaker |

并行规则：

- 同一 wave 最多 3 个 subagents；
- 可并行：证据覆盖审计、环境探测、schema gap 分析；
- 不可并行：标准化规则尚未冻结时生成正式 pair/graphs/splits；split ADR 未接受时训练正式模型；
- reviewer 必须读取 maker 的 diff、命令和输出，不继承 maker 的结论作为事实。

## 6. Persistent state and multi-round review

执行启动时创建：

- `goals/state/condrxnbench-v0_2-benchmark-v0_1-state.md`：append-only loop state；
- `notes/YYYY-MM-DD-core-v0_2-benchmark-v0_1.md`：符合 maintenance 的阶段过程笔记；
- `reports/execution/`：机器可读验证输出、diff summaries 和 audit reports。

每轮 state 格式：

```markdown
## Iteration N — timestamp — phase
### Hypothesis
### Inputs and hashes
### Agent/role
### Files changed
### Commands run
### Fast validation
### Full validation
### Independent review
### Metrics and deltas
### Reflection and failure mechanism
### Decision: promote | revise | revert | blocked
### Next single hypothesis
```

所有高风险 promotion 至少三道验收：

1. **Round A — Contract review**：规则/ADR/config 在看到模型测试结果前冻结；
2. **Round B — Implementation validation**：自动测试与全量构建通过；
3. **Round C — Independent adversarial review**：另一 agent 重跑、抽样、负对照并签署 pass/fail。

任一道失败即不得 promotion。修复后重新执行失败门禁及所有受影响的下游门禁。

## 7. Phase 0 — Preflight, environment and immutable baseline

### Hypothesis

仓库可以在不修改 raw 和不覆盖用户工作树的条件下，建立可复跑环境与 baseline snapshot。

### Required actions

- 审计 `git status`，列出 goal 内/外变更；不得擅自清理 dirty tree；
- 记录 raw/input manifests、git commit、Python/OS/依赖版本；
- 建立 Python 3.11（允许 3.10–3.12）环境，固定 RDKit、pandas、numpy、pyarrow、scikit-learn；按需加入 pandera/pytest/networkx/DRFP；
- 复跑两源构建、QC、Core v0.1 build 与 verifier；
- 创建 Proposed ADR：Core v0.2 schema/storage/environment compatibility；
- 输出 baseline coverage report，而不是把缺失结构当失败数据删除。

### Hard acceptance

- raw/input hash 与已接受 manifest 一致；差异必须阻断并人工裁决；
- Core v0.1 仍为 9,900 records、116,156 pairs；上述零值/缺失计数一致；
- 环境可从版本化文件重建；`python`, RDKit, pyarrow, sklearn 版本被记录；
- Parquet round-trip 不改变主键、行数、布尔值、语义哨兵或数值；
- goal 外工作树变更保持不变；
- reviewer 独立执行恢复命令并通过。

## 8. Phase 1 — Section 5 standardization loop → Core v0.2

### 1A. Structure evidence and normalization

- 建立 raw/normalized 双字段；不做不可逆覆盖；
- 对来源已报告或经证据恢复的 SMILES 执行 parse、sanitize、canonicalize、InChIKey；
- 去盐/主成分选择必须 config-driven，默认保守；金属、离子对、R-group 标记 QC，不静默删除；
- atom mapping、product、bond changes 只有在有证据时生成；
- Murcko、ECFP4/6、DRFP、reaction-center fingerprint 分别记录 `available/not_supported/failed`，不得用 `not_reported` 生成伪特征；
- 主动尝试从已固化 SI 恢复固定底物/产品结构，所有 curated mapping 必须有页码/表号/来源和 reviewer 状态。

### 1B. Condition registry and units

- 为名称、结构、角色、复合体系、显式空条件、类别属性建立版本化 registry；
- 每个非恒等映射必须有 source evidence；
- `catalyst_system` 在无证据时不得强拆为 catalyst+ligand；
- 混合溶剂保留组分、比例和 raw label；
- 连续字段统一单位并保存 raw value/unit；
- 类别属性（ligand family、base type、solvent polarity 等）必须区分 evidence-backed 与 derived。

### 1C. Outcomes and quality

- 维持 source-aware measurement semantics；
- 0、missing、not_reported、not detected 分开；
- 范围异常先列 audit，不直接修正；
- 重复实验有证据才建立 `replicate_id`/噪声；
- 逐记录质量等级与 eligibility 分开：grade 描述证据，不等同于训练过滤。

### Hard acceptance

- `reaction_records` 保留全部 9,900 主矩阵记录；任何 training exclusion 通过 flag 实现，不删历史；
- 100% records 有 `source_dataset`, `source_record_id`, `provenance_path` 或明确的 missing-export sentinel；
- raw hash 不变；标准化前后 yield observed/missing/zero 计数完全守恒，除非有 Accepted bug-fix ADR；
- 离散核心条件的状态覆盖率 100%，其中有效/显式空条件完整率 >99%；
- `NULL_COMPONENT != not_reported != NA` 的自动测试 100% 通过；
- 在“有结构且声明应可解析”的集合中 RDKit parse/sanitize 成功率 ≥99%；结构覆盖率必须单独报告，不能用 parse 成功率掩盖缺失；
- 100% 结构失败有 error class、raw value、source 和 disposition；
- 100% 非恒等名称/角色/单位映射有 evidence 和 reviewer status；
- Parquet 为正式交付，CSV 仅人工检查；两者主键、行数和核心值等价；
- schema、data dictionary、dataset cards、ADR 与实现同步；
- independent reviewer 对全部映射类别审计，并对每源/每角色抽样；任何关键角色误分为 hard fail。

## 9. Phase 2 — Section 6 grouping, pairs and graphs loop

### Group policy

- 同时维护 `design_group_id`、`strict_reaction_group_id`、`scaffold_group_id`、`template_group_id`；
- 当前结构不足时不得把 design group 宣称为 structure-verified strict group；必须有 `group_definition_version` 与 `group_confidence`；
- group 定义变化先写 Proposed ADR，接受后才重建 pair。

### Pair policy

- 从标准化 records 全量枚举候选 pair；先形成 pair universe，再计算/应用 cliff 标签；
- strict discrete pair 只允许一个角色改变；数值 pair 使用版本化容差；multi-factor 只进入扩展诊断层；
- 每个 pair 保存两端原始指针、group 版本、changed-factor vector、delta 和构建版本；
- Core v0.1 的 116,156 pairs 是 regression baseline；数量变化必须输出逐原因 reconciliation ledger。

### Graph policy

- 每个 group 一个 graph；node=record，strict edge=strict pair；
- 保存节点/边 Parquet 与机器可交换图格式（优先 GraphML 或 JSON），格式选择写 ADR；
- strict graph 与 multi-factor/nearest-neighbor extended graph 分开；
- graph 只是关系表示，不自动产生额外科学证据。

### Cliff policy

- 在查看模型测试结果前写 ADR/config；
- 主分析预注册建议：strong `|Δy| ≥ 30 pp`，moderate `10 < |Δy| < 30`，invariant `≤10`；敏感性阈值建议 20/40 pp；
- 有重复证据时加入噪声/z-effect；无重复时不得声称统计显著；
- 连续 delta 始终保留，分类标签可重建。

### Hard acceptance

- 100% strict pairs：同源、同 group、端点存在且 outcome observed、无 self-loop、`n_changed_factors=1`；
- 对标准化前后 pair 数量做完整 reconciliation，未解释差异为 hard fail；
- reviewer 分层抽查至少 200 pairs，覆盖两个数据源和全部 changed factors，准确率 ≥98%，且不得出现 reaction identity 变化这一关键错误；失败后修复并重新抽样；
- 每个 graph 的 node 集与所属 group records 精确一致；strict edge 集与 pair 表双射；重复边、跨组边、自环均为 0；
- graph summary 报告连通分量、度分布、孤立点和按因素边数；这些只作诊断，不作为删样本依据；
- cliff 标签由冻结 config 生成；修改阈值必须新版本，不得覆写旧标签。

## 10. Phase 3 — Section 7 bias, confounding and leakage review loop

### Required audits

- condition frequency shortcut 与 condition-only diagnostic；
- group/plate/batch/row/column effects；
- measurement-method separation；
- structure/scaffold near-duplicate coverage；
- missingness/failed-reaction pattern；
- catalyst–ligand/solvent–water 共变；
- pair coverage and degree imbalance；
- controls 与 main matrix 的隔离；
- 对任何预训练模型记录潜在公开数据污染风险，无法证明无污染时不得声称 clean pretraining。

### Hard acceptance

- 每项风险都有 `tested / not_testable / not_applicable`、证据、影响和控制措施；不能留空；
- 所有可自动检测的 identity/group/pair leakage 为 0；
- plate/batch/measurement 与 outcome 的关联被量化，不能仅口头说明；
- 至少一组正对照和一组负对照验证审计工具确实能发现已知泄漏；
- reviewer 提交 adversarial audit report；P0 风险必须修复或经用户接受的 ADR 降级，才能进入 Phase 4。

## 11. Phase 4 — Sections 8–9 tasks, splits and metrics loop

### Protocol-first rule

先写并接受以下 ADR/config，再生成任何正式测试结果：

- split units、seed、test-first policy；
- record split 与 pair split 的关系；
- success/direction/invariant/cliff label policy；
- S0–S5 的 held-out component/group/combination selection；
- source-stratified metrics 和不支持项处理。

### Task contract

实现 Task 1–7 的输入、标签、eligibility、split 和指标契约。Task 7 作为 OOD 分层评价框架，不得与单一预测 head 混淆。

建立 `task_split_feasibility_matrix`：每个 source×task×split 必须标为 `supported / limited / not_supported` 并给证据。不能为了“全部有分数”而生成化学上无意义的任务。

### Split contract

- S0 Random 仅用于历史对照；
- S1 within-group interpolation；
- S2 reaction-group OOD；
- S3 component OOD；
- S4 unseen combination OOD；
- S5 group + condition double OOD；
- record manifest 与 pair manifest 分开版本化；只有两端同属一个 partition 的 pair 才进入该 partition 的 pair 任务；跨 partition pairs 必须计数并排除，不能静默使用；
- 任何 evaluation-only anchor policy 必须单独 ADR，且 anchor labels 不得进入训练。

### Metrics contract

- absolute MAE/RMSE/R² 按 source/yield_type 分层；
- ΔMAE/ΔRMSE、direction accuracy、sensitivity ratio、ΔPearson/Spearman；
- Cliff AUPRC 优先于 accuracy；
- ranking：Spearman/NDCG/top-k；推荐：success/regret；
- within-group variance ratio 与 factor-wise sensitivity；
- 所有指标对空集合、常数数组、ties、missing predictions 和类别不平衡有显式行为。

### Hard acceptance

- manifests 固定 seed、配置 hash、数据 hash、train/val/test 主键；同一配置重跑 hash 一致；
- S2/S5 group leakage=0；S3 held-out component 在 train 出现次数=0；S4 held-out combination 在 train 出现次数=0；
- 所有纳入 pair 指标的 pair 两端处于同一 partition；cross-partition pair 使用数和泄漏数均为 0；
- train/val/test 非空且分布/覆盖报告存在；若某 source×task×split 不可行，必须是 `not_supported` 而非空分数；
- 每个指标至少有解析可验证 toy cases、边界测试和负对照；
- split auditor 与 metrics reviewer 均独立通过；
- 测试集 manifest 一旦冻结，不因模型结果改变；改变必须升 benchmark 版本。

## 12. Phase 5 — Baseline training and model-readiness loop

### Baseline hierarchy

按顺序执行，后者不能替代前者：

1. global/source mean；
2. group/condition mean（仅适用 split）；
3. condition-only；
4. reaction-only（仅在结构证据足够时）；
5. full reaction+condition Ridge；
6. Random Forest / XGBoost；
7. molecular descriptor + RF；
8. DRFP + tree model（仅完整 reaction representation）；
9. Transformer/graph baseline 为资源允许时的扩展，但不得取代简单基线。

### Required experiment design

- 固定 seed、环境、features、hyperparameter budget；
- tuning 只用 train/val，test 只在候选冻结后运行；
- 每个模型报告 absolute、pair、ranking/recommendation 和 OOD 适用指标；
- condition-only 与 reaction-only 是 shortcut 诊断，不只是排行榜模型；
- shuffled-y、shuffled-condition、constant predictor 为负对照；
- 失败运行和 N/A 进入结果表，不能删除。

### Hard acceptance

- 每个正式结果可由一个版本化命令和 config 重跑；保存 predictions，不只保存汇总指标；
- 训练/验证/测试身份泄漏为 0；测试集从未用于阈值、feature、seed 或 hyperparameter 选择；
- 所有绝对指标按 source/yield_type 分层；跨源仅做明确的 transfer experiment；
- 至少 8 个 proposal baseline families 在所有 `supported` task×split 上有结果；若结构证据使某 family 不成立，必须用 Accepted ADR 建立不低于 5 个独立、科学有效 families 的降级标准，依赖未安装不构成降级理由；
- 至少 3 个 seeds 或预注册的等价不确定性方案；报告均值、离散度和 paired comparison；
- 简单基线、negative controls、full model 均完整；任何复杂模型提升若伴随 strict/OOD/pair 指标退化，不得宣称全面改善；
- leaderboard 每格都有 result、N/A reason 或 failed-with-log；不得留无解释空白；
- independent reviewer 从干净环境重跑至少一个完整 source×split pipeline 和全部汇总校验。

### Promotion boundary

本 goal 的可信终点是 **Benchmark v0.1 + baseline leaderboard v0.1**。CYC-Loss/CondFormer 只有在上述基线通过后才可另开研究 goal；本轮可以生成 model-readiness design，但不得把未做消融的方法写成结论。

## 13. Phase 6 — Final release, rollback and maintenance handoff

### Final release artifacts

- Core v0.2 records、registry、controls、manifest 与 CSV inspection mirrors；
- Benchmark v0.1 pairs、strict/extended graphs、task/split manifests；
- metrics package、baseline configs、predictions、leaderboard、audit/QC reports；
- schema/data dictionary/dataset cards/API/architecture 更新；
- hypothesis-by-hypothesis iteration summary；
- promoted、reverted、blocked 和 not-supported 清单。

### Maintenance hard gate

按 `docs/maintenance-workflow.md` 顺序完成，缺一项不能标记 goal complete：

1. 完成并封存过程笔记，含目标、输入、实际命令、环境、结果、失败和下一步；
2. `PROGRESS.md` 新增阶段记录：已完成/新增/验证/风险/下一步；
3. `STATUS.md` 更新为最新可恢复快照；
4. `ROADMAP.md` 移走完成项，只保留可验收的未完成项；
5. `CHANGELOG.md` 记录用户可见数据、schema、CLI、版本和兼容性变化；
6. 所有长期语义决策进入 ADR；Accepted ADR 不改写历史，以新 ADR supersede；
7. 同步 `docs/`, `metadata/`, README、API 与 dataset cards；
8. 输出 `reports/execution/final_execution_summary.md` 和机器可读 manifest；
9. 运行最终 clean-build/validation matrix，记录未运行项及原因；
10. 审计 git diff，确认 raw 未变化、无密钥/受限内容、无意外大文件；
11. 若用户授权提交，提交信息引用版本和验证；未授权则只提供变更清单，不自行 commit/push。

### Final acceptance matrix

只有同时满足以下条件才能标记 complete：

- Core v0.2 standardization gate：PASS；
- grouping/pair/graph gate：PASS；
- bias/leakage gate：PASS；
- task/split/metrics gate：PASS；
- baseline gate：PASS 或有用户接受的、证据充分的 scope ADR；
- reproducibility clean run：PASS；
- independent final review：PASS；
- maintenance hard gate：PASS；
- 未解决 P0 scientific risk：0；
- raw unintended changes：0；
- 无证据的“完成”声明：0。

## 14. Rollback and resumption

- 每次 promotion 前记录旧 manifest 与 git diff；
- 失败变更优先 revert 该 iteration 的最小改动，不删除历史输出；
- 已发布数据不得原地覆写，使用新版本目录和 manifest；
- breaker 触发后保留 state、logs、candidate outputs，并在 `STATUS.md` 标为 blocked；
- 新 agent 恢复顺序：本 goal → state → STATUS → 最新 note → relevant ADR → failed command/log。

## 15. Human review checklist before execution

- 已同意本轮边界止于 Core v0.2 + Benchmark/Baseline v0.1；
- 已同意 primary cliff 建议 30 pp、invariant ≤10、敏感性 20/40，或提出替代；
- 已同意最多 3 个并行 subagents、24 轮、单次运行 6 小时；
- 已同意缺失结构必须分层报告，不能为了达到模型数量补造；
- 已同意 task/split 可被证据标为 `not_supported`，但必须经过 ADR/reviewer；
- 已同意执行时创建/更新 maintenance 文件；
- 已明确允许联网核验结构、安装依赖、使用 GPU、commit/push（这些权限不由本 goal 自动获得）。