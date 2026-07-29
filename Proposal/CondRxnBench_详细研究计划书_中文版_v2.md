
**研究计划书（Research Proposal）**


**CondRxnBench：面向化学反应条件敏感性、产率悬崖与分布外泛化的基准数据集**


*A Benchmark for Condition-Sensitive Reaction Yield Prediction, Condition Cliffs and Out-of-Distribution Generalization*


项目负责人：龙锦轩、申万祥


建议周期：第一阶段 6 个月；完整论文 9–12 个月


版本：中文版 v2.0


日期：2026年7月


# 项目摘要


化学反应产率预测模型常在随机划分上取得较低的均方根误差，但这一结果并不能证明模型真正理解了催化剂、配体、碱、溶剂、添加剂、温度和浓度等反应条件。现实中，同一组反应物与产物仅改变一种条件，产率即可从接近定量骤降至几乎无反应；而现有模型可能因过度依赖底物和产物结构、数据集中的条件频率偏差以及高产率样本偏好，对这种局部条件变化表现出明显的不敏感。


本项目拟构建 CondRxnBench：一个以“同一反应在多个受控条件下的实验矩阵”为核心组织形式的公开基准。项目将汇集公开高通量实验（HTE）、Open Reaction Database（ORD）、公开真实世界 ELN 数据、文献优化表和部分专利产率数据，建立反应与条件标准化流程；通过严格反应分组、单因素条件扰动配对和反应条件图，定义 Reaction Condition Cliff；并建立随机、反应组外、条件成分外、条件组合外和双重分布外等多级评价协议。


项目最终交付包括：标准化反应级数据表、条件配对表、反应条件图、可复现数据处理代码、质量控制报告、多种基准划分、传统与条件敏感性评价指标，以及基于 DRFP、树模型、图神经网络、Transformer 和条件悬崖感知损失的基线结果。该项目的核心不是单纯扩大反应数量，而是建立一个能够回答“模型是否真正感知反应条件变化”的研究范式。


| **阶段** | **目标** | **核心交付物** |
| --- | --- | --- |
| 阶段I：数据工程 | 完成公开数据源收集、统一模式和质量控制 | CondRxnBench-Core；处理脚本；数据字典 |
| 阶段II：基准构建 | 建立反应组、条件配对、Condition Cliff 和 OOD 划分 | pair-level benchmark；五类 split；指标库 |
| 阶段III：模型与论文 | 建立强基线、提出 CYC-Loss/CondFormer 并完成论文 | 模型代码；实验报告；论文初稿 |


# 1. 研究背景与问题定义


## 1.1 现有反应产率预测的隐含假设


现有反应产率预测通常把一条反应表示为反应物、试剂、产物和条件的组合，并以单条实验的绝对产率为监督信号。该范式默认：只要模型能够准确拟合每条记录的产率，就已经学会了条件效应。然而，在训练数据中，底物结构、反应类型和条件往往同步变化，模型可以仅依靠底物/产物结构或条件的全局平均成功率取得较好结果，无须学习“特定条件对特定反应”的交互作用。

- 随机划分会把同一优化实验矩阵中的近重复反应分散到训练集和测试集，导致显著的信息泄漏。
- 专利与文献通常优先报告最佳或可接受条件，低产率和失败反应缺失，造成选择偏差。
- 条件常被编码为无序字符串或混入反应 SMILES，模型难以分辨催化剂、配体、溶剂等角色。
- 仅使用 MAE、RMSE 和 R²，无法发现模型对条件变化幅度的系统性压缩。

## 1.2 反应条件敏感性与 Condition Cliff


本项目将“反应条件敏感性”定义为：在保持反应主体基本不变时，模型对条件扰动引发的产率方向和幅度变化进行正确响应的能力。若两个实验具有相同反应主体，条件距离很小，但产率差异显著，则定义为反应条件悬崖（Reaction Condition Cliff）。


```text
同一反应：Reactants + Product + Reaction Center 固定
实验 A：Ligand=L1, Base=B1, Solvent=S1, 80 ℃ → Yield=88%
实验 B：Ligand=L2, Base=B1, Solvent=S1, 80 ℃ → Yield=17%
仅配体改变，|ΔYield|=71%，构成高置信度 Ligand Condition Cliff。
```


## 1.3 科学问题

1. 模型的低 RMSE 是否伴随真实的条件敏感性，还是主要来自底物和反应类别记忆？
2. 不同模型对 ligand、base、solvent、catalyst、temperature 等条件类型的敏感性是否不同？
3. 模型能否对训练中未见过的条件成分、条件组合和反应主体进行泛化？
4. 显式的条件配对监督和 Condition Cliff-aware loss 能否缓解预测差异被压缩的问题？
5. 条件变化的实验效应能否通过可解释的 reaction-condition graph 学习和归因？

# 2. 总体目标、具体目标与预期创新


## 2.1 总体目标


建立一个覆盖数据、定义、任务、划分、指标和模型的完整反应条件敏感性研究体系，使模型评价从“能否拟合单条反应产率”升级为“能否理解局部条件扰动、识别条件悬崖并在新反应与新条件上保持稳健”。


## 2.2 具体目标

1. 构建 CondRxnBench-Core：以公开 HTE 数据为主体的高质量受控条件矩阵。
2. 构建 CondRxnBench-Real：整合 ORD、ELN、文献优化表和经严格过滤的专利数据。
3. 建立统一的反应与条件 schema、实体规范化字典和质量评分体系。
4. 提出 Reaction Group、Single-Condition Perturbation Pair、Condition Graph 和 Condition Cliff 的统一定义。
5. 建立五类数据划分和一套专门的条件敏感性指标。
6. 训练传统、深度学习和配对学习基线，并开发 CYC-Loss 或 CondFormer 原型。

## 2.3 预期创新点


| **创新维度** | **具体内容** |
| --- | --- |
| 研究范式创新 | 首次把“条件敏感性”作为独立于整体产率误差的核心评价目标。 |
| 数据组织创新 | 从单条反应表升级为“反应组—条件矩阵—扰动边”的多层数据结构。 |
| 概念定义创新 | 系统定义 Condition Cliff，并区分 ligand/base/solvent/temperature 等类型特异悬崖。 |
| 评价协议创新 | 建立未见反应、未见条件、未见组合和双重 OOD 等严格划分。 |
| 方法创新 | 通过 pairwise ΔYield、排序、幅度和不变性约束，使模型显式学习条件效应。 |


# 3. 数据来源与数据库处理方案


数据源按“受控程度优先于规模”的原则分层。第一版核心基准不追求最大反应数，而优先保证同一反应具有多个条件、低/零产率被保留、条件字段明确且实验来源可追溯。


| **数据源** | **规模/内容** | **获取方式** | **在本项目中的用途** | **主要处理要点** |
| --- | --- | --- | --- | --- |
| Ahneman–Doyle Buchwald–Hartwig HTE | 约3,955条有效反应；15种芳基卤化物、4种配体、3种碱、23种添加剂的组合 | 公开论文/补充数据 | 核心：离散条件矩阵、Condition Cliff、OOD ligand/additive | 检查原始4,608组合与缺失/无效记录差异；保留0产率 |
| Perera Suzuki–Miyaura HTE | 约5,760个组合；5 electrophiles×7 nucleophiles×11 ligand设置×7 base设置×4 solvents | 公开论文/数据仓库 | 核心：底物和条件双重组合泛化 | 核验空白配体/空白碱的语义；统一 LC/MS 或相对产率 |
| HTE Reactome / 39k+ | 超过39,000条此前专有、后公开的HTE反应，含交叉偶联和手性盐拆分 | 论文及配套仓库/ORD | 扩展：多反应类型、条件作用分析 | 逐子数据集解析；不同 outcome 不强制混成同一 yield任务 |
| ORD | 开放 schema 与中央仓库，支持台式、HTE、流动化学 | ORD GitHub/API/数据快照 | 核心容器与扩展来源 | 从 protocol buffer/JSON 解析 inputs、conditions、workups、outcomes、provenance |
| ORDerly | 对ORD进行清洗、整理和基准化的数据集工具 | 公开代码与数据 | 用于获取更易处理的标准化 ORD 子集 | 仍需回溯原始 ORD 记录以恢复完整条件与来源 |
| 公开工业ELN数据 | 真实药企ELN反应，已用于HTE与真实世界产率比较 | 论文配套数据（按许可） | 验证现实分布与选择偏差 | 条件缺失率高；不作为纯受控核心集，单独建 Real split |
| 文献优化表/SI | 论文中的 ligand/base/solvent/temperature screening tables | 期刊SI、手工/半自动抽取 | 扩充高质量单变量配对 | 必须绑定同一表、同一底物、同一测量方法；人工复核 |
| USPTO yield / TDC | 大规模专利反应，约5万至85万量级的不同整理版本 | 公开衍生数据 | 预训练、结构表示学习、背景分布 | 不作为核心Condition Cliff测试；最佳条件偏差、低产率缺失、scale偏差 |
| Pistachio | 商业专利/文献反应库 | 商业许可 | 可选内部预训练与外部验证 | 不可直接公开再分发；必须按许可处理 |
| Reaxys/SciFinder | 商业检索数据库 | 机构订阅 | 用于人工查证和补充来源 | 不进行未经许可的批量导出或公开发布 |


## 3.1 Ahneman–Doyle Buchwald–Hartwig HTE 数据处理


该数据是第一批必须完成的核心数据。它具有典型的组合式 HTE 设计，适合严格验证“固定或相近底物时，配体、碱和添加剂变化对产率的影响”。公开文献常见的有效记录数约为3,955，而理论组合数可更高，因此必须保留原始行号、原始组合和缺失原因，不能直接把过滤后的表当成完整实验矩阵。

- 下载原始补充数据并保存校验值；不得只使用二次转载 CSV。
- 识别 aryl halide、additive、base、ligand 的实体名称和结构；生成标准 SMILES/InChIKey。
- 将“无添加剂”“无配体”作为明确的 NULL_COMPONENT 类别，而不是缺失值。
- 校验 yield 范围、重复组合、缺失实验和异常值；生成 matrix completeness 报告。
- 构造单因素配体、碱、添加剂变化 pair；底物变化 pair 单独用于结构敏感性对照。
- 以 aryl halide scaffold、additive 和 ligand 为单位建立 OOD 划分。

## 3.2 Perera Suzuki–Miyaura HTE 数据处理


该数据同时系统改变 electrophile、nucleophile、ligand、base 和 solvent，适合测试“条件成分是否在不同底物组合中具有可迁移作用”。学生需优先确认每个字段的实验角色、空白组设置和产率/转化率测量定义。

- 建立 electrophile×nucleophile 的 reaction-group key；product 可由映射反应或已知组合核验。
- 将 ligand、base、solvent 分别规范化，处理混合溶剂和空白条件。
- 计算每个底物对下的条件覆盖率与有效产率范围，剔除没有任何变化信息的 group。
- 构造 leave-one-electrophile-out、leave-one-nucleophile-out、leave-one-ligand-out 和 unseen-combination split。
- 比较同一条件跨底物对的效应一致性，识别条件主效应与 reaction×condition 交互。

## 3.3 HTE Reactome 39k+ 数据处理


该公开资源提供跨化学类型的大规模 HTE 数据，但不同子集可能具有不同的结果定义，例如连续产率、二分类成功、选择性或成盐结果。因此不能粗暴合并为单一回归表。应先建立 dataset card，再决定哪些子集进入 CondRxnBench-Yield、CondRxnBench-Success 或扩展任务。

- 逐个数据包记录反应类型、实验设计、outcome 类型、检测方法、条件维度和许可。
- 只把可映射到0–100连续产率且测量含义一致的子集放入主回归任务。
- 二分类和选择性子集保留为独立扩展任务，避免伪造连续产率。
- 使用原始实验 plate/batch 信息进行 batch-aware split，防止板内泄漏。
- 记录每个子集的条件正交性、失败反应比例和重复实验情况。

## 3.4 ORD 与 ORDerly 数据处理


ORD 不只是一个下载数据集，而是本项目推荐的标准容器。其 schema 能区分 reaction input、compound role、amount、reaction setup、temperature、pressure、illumination、workup、measurement 和 outcome。学生应先学习 ORD schema，再写稳定的 parser，把原始记录转为项目内部的规范表。

- 固定一个 ORD 数据快照或 commit，记录版本和下载日期。
- 解析 ReactionInput 中每个 component 的 role、amount、equivalent 和 identifiers。
- 解析 conditions 中的 temperature、pressure、stirring、flow、illumination、electrochemistry 等字段。
- 从 outcomes 中提取 product、yield、conversion、selectivity、measurement type 和 uncertainty。
- 保留 provenance、dataset_id、reaction_id 与原始 JSON 路径，保证可追溯。
- 使用 ORDerly 作为快速入口，但关键记录需与原始 ORD 对照，避免清洗过程丢失条件。

## 3.5 文献优化表和补充信息处理


文献优化表是单变量条件配对的高质量来源，但自动抽取风险较高。第一阶段建议选择20–50篇具有清晰优化表、固定底物和明确产率测量方式的论文，采用半自动抽取与双人复核。

- 每个优化表生成唯一 table_id，并记录 DOI、页码/表号、底物图、标准条件和注释。
- 把“entry 1–n”转成结构化条件，不允许仅保存截图。
- 对 catalyst loading、ligand loading、equivalents、temperature、time 和 solvent volume 进行单位统一。
- 表内 yield 与正文最终 isolated yield 不得混用；优先采用同一分析方法的表内数据。
- 由第二名学生或导师抽查至少20%的记录，目标字段准确率>98%。

## 3.6 USPTO、TDC、Pistachio 等大规模数据处理


这类数据适合预训练反应表示、反应分类或构建外部真实世界测试，但不适合作为严格条件敏感性基准的主体。专利中的条件通常不是系统设计的，且成功条件被选择性报告。

- USPTO/TDC 数据仅用于预训练和背景对照，核心测试集不得与其近重复反应交叉。
- 对 reaction SMILES 做标准化、去 atom-map 冲突、质量守恒和产率范围检查。
- 使用反应模板、产物 scaffold 和文献/专利标识去重，避免预训练测试泄漏。
- Pistachio 和 Reaxys/SciFinder 仅在许可范围内使用，不把原始记录公开再分发。

# 4. 数据模式（Schema）与字段设计


建议同时维护三层数据：反应实验层、条件扰动配对层和反应条件图层。所有派生数据必须保留到原始记录的可追溯指针。


## 4.1 reaction_records.parquet：单条实验表


| **字段组** | **建议字段** |
| --- | --- |
| 标识与来源 | reaction_id, source_dataset, source_record_id, DOI/patent_id, plate_id, batch_id, provenance_path |
| 反应结构 | reactant_smiles, reagent_smiles, product_smiles, atom_mapped_rxn, canonical_rxn, reaction_class, template_id, bond_changes |
| 离散条件 | catalyst, precatalyst, ligand, base, additive, oxidant, reductant, photocatalyst, solvent_1/2, atmosphere, vessel |
| 连续条件 | temperature_C, time_h, concentration_M, pressure_bar, wavelength_nm, scale_mmol, component_equivalents, catalyst_loading |
| 实验结果 | yield_value, yield_type, conversion, selectivity, product_ratio, success_label, measurement_method, uncertainty |
| 质量字段 | qc_flags, confidence_grade, duplicate_group, parse_version, manual_review_status |
| 划分字段 | reaction_group_id, scaffold_id, condition_component_ids, split_random, split_group, split_condition, split_double_ood |


## 4.2 condition_pairs.parquet：条件扰动配对表


| **字段** | **定义** |
| --- | --- |
| pair_id | 配对唯一标识 |
| reaction_group_id | 所属严格反应组 |
| reaction_id_a / reaction_id_b | 两个实验记录 |
| changed_factor | ligand/base/solvent/catalyst/additive/temperature/time/concentration/multi |
| condition_a / condition_b | 变化前后实体或数值 |
| n_changed_factors | 改变的条件因素数量 |
| delta_yield / abs_delta_yield | 带方向与绝对产率差 |
| condition_distance | 离散+连续条件距离 |
| pair_type | cliff/moderate/invariant |
| confidence_grade | 配对可信度 |
| split | 训练/验证/测试及OOD类型 |


## 4.3 condition_graphs：反应条件图


每个 reaction group 构建一个图：节点为单个实验条件组合，节点属性包括完整条件与产率；边连接条件距离低于阈值的实验，边属性记录改变的因素、条件距离和 ΔYield。严格图仅连接 n_changed_factors=1 的节点；扩展图允许两种条件同步变化，但需单独标记。


# 5. 数据清洗、实体标准化与质量控制


## 5.1 分子结构标准化

- 使用 RDKit 进行 SMILES parse、sanitize、去盐/保留有机主成分的可配置处理。
- 保留原始结构和标准化结构，避免不可逆清洗。
- 处理 atom mapping：标准化原子映射编号，检测重复映射、未映射产品原子和不合理键变化。
- 生成 canonical SMILES、InChIKey、Murcko scaffold、ECFP4/6、DRFP 和 reaction-center fingerprint。
- 对金属配合物、离子对、聚合物和未知 R-group 设置专门 QC flag，不盲目删除。

## 5.2 条件实体标准化


条件实体规范化是项目成败的关键。必须建立 condition ontology/registry，使字符串、结构、角色和类别统一。


| **处理对象** | **规范** |
| --- | --- |
| 名称规范化 | THF / tetrahydrofuran / Tetrahydrofuran → 同一 normalized_name |
| 结构映射 | 可定义小分子条件映射至 canonical SMILES 与 InChIKey |
| 角色拆分 | Pd2(dba)3/XPhos → precatalyst 与 ligand 分列 |
| 复合条件 | 混合溶剂保存 solvent_1、solvent_2 和体积比 |
| 无成分条件 | no ligand/no base 作为显式类别，不等同于 missing |
| 类别标签 | ligand family、base strength/type、solvent polarity/proticity 等派生属性 |
| 连续变量 | 温度、时间、浓度、压力、波长、当量和负载量统一单位 |


## 5.3 产率与结果标准化

- 严格区分 isolated yield、assay yield、LC/GC/NMR yield、conversion 和 success/failure。
- 主回归任务优先在同一数据子集、同一测量方式内比较；跨方法建模需加入 measurement embedding。
- 0 表示真实检测到零产率或未检出；空值表示未测量，二者绝不能互换。
- 超出0–100范围的记录先核验单位或小数/百分数错误，再决定修正或排除。
- 重复实验保留 replicate_id，计算均值、标准差和实验噪声；不直接去重丢弃。

## 5.4 质量等级


| **等级** | **标准** | **用途** |
| --- | --- | --- |
| A | 同一实验批次/plate；条件字段完整；有重复或误差；测量方式一致 | 严格测试集 |
| B | 同一数据集和实验体系；字段完整；无重复但来源清晰 | 核心训练与测试 |
| C | 文献表内人工抽取；大部分字段完整；经过双人复核 | 扩展训练/外部测试 |
| D | 专利/ELN自动抽取；条件不完全或测量定义不统一 | 预训练与稳健性分析 |
| E | 结构或条件存在严重歧义 | 默认排除，仅保留审计 |


# 6. 反应分组、条件距离和配对构建


## 6.1 Reaction Group 定义


严格 reaction group 应同时满足主要反应物集合一致、主要产物一致、反应中心/键变化一致。对 HTE 数据可利用实验设计中的 substrate IDs 直接建组，但仍需用结构和原子映射验证。


```text
strict_group_key = hash(
  sorted(canonical_major_reactants),
  canonical_major_product,
  sorted(bond_changes),
  reaction_class
)
```


另建立 scaffold-level group 和 template-level group，用于更宽松的泛化研究，但不能与严格组混用。


## 6.2 条件距离


条件距离由离散因素与连续因素组成。离散成分可采用是否变化或结构距离；连续条件先按化学合理范围标准化。


```text
d_cond(i,j) = Σ_k w_k·I(c_i^k ≠ c_j^k) + Σ_m v_m·|z(x_i^m)-z(x_j^m)|
其中 k 为 ligand/base/solvent 等离散条件，m 为 temperature/time/concentration 等连续条件。
```


## 6.3 单因素扰动配对

- 严格 pair：仅一个条件因素变化，其他条件完全一致或在预设容差内一致。
- 数值 pair：如温度变化时，其他因素不变，且温度差达到最小可解释阈值。
- 多因素 pair：仅作为扩展任务，不进入第一版严格 Condition Cliff 测试。
- 每个 group 内避免全 O(n²) 爆炸：优先单因素边、最近邻边和具有代表性的高/中/低 ΔYield 边。

## 6.4 Condition Cliff 标签


建议同时发布连续 ΔYield 和多阈值标签，不把某一个阈值永久写死。主分析可采用 |ΔYield|≥30 个百分点作为强悬崖，10–30 为中等效应，≤10 为近似不变。对于存在重复实验的数据，再要求效应显著高于测量噪声。


| **标签** | **定义** |
| --- | --- |
| Strong cliff | \|Δy\|≥30，且方向稳定；有重复时 z-effect≥2 |
| Moderate | 10<\|Δy\|<30 |
| Invariant | \|Δy\|≤10，且实验误差允许范围内 |
| Uncertain | 条件或测量方式不一致、误差过大、存在混杂因素 |


# 7. 偏差、混杂因素与泄漏控制


| **风险** | **表现** | **控制措施** |
| --- | --- | --- |
| 条件频率捷径 | 某 ligand 在训练中几乎总是高产，模型只记忆平均值 | 报告 condition-only baseline；控制条件频率；构建跨底物正负效应 |
| 同一优化表泄漏 | 同一 reaction group 被随机分到训练与测试 | group-aware split；table/plate-aware split |
| 底物泄漏 | 同一 scaffold 或近重复结构跨集 | Murcko scaffold、reaction template 和指纹相似度联合去重 |
| 预训练污染 | 公开 HTE 数据可能已进入通用预训练语料或专利集 | 结构级近重复检索；报告污染敏感分析 |
| 测量方式混杂 | isolated/LC/GC yield 混合 | 分层建模或 measurement embedding；严格测试保持一致 |
| 批次/板效应 | plate、仪器或批次与产率相关 | 保留 batch/plate；batch-aware split；加入批次诊断 |
| 失败缺失 | 文献和专利缺少失败实验 | 核心集以 HTE 为主；Real 数据单独报告 |
| 条件共变 | 配体与催化剂总是成套出现 | 角色拆分；因子设计分析；只把真正单变量变化作为严格pair |


# 8. 基准任务与数据划分


## 8.1 基准任务


| **任务** | **定义** | **主要指标** |
| --- | --- | --- |
| Task 1 绝对产率预测 | 输入反应与完整条件，预测 y | MAE/RMSE/R² |
| Task 2 ΔYield预测 | 输入同一反应的两组条件，预测 yB-yA | ΔMAE、ΔRMSE、相关系数 |
| Task 3 条件方向判断 | 判断条件改变使产率升高/降低/不变 | Direction accuracy、macro-F1 |
| Task 4 Condition Cliff检测 | 识别小条件变化造成的大产率变化 | AUPRC、AUROC、F1 |
| Task 5 条件排序 | 对同一反应的候选条件排序 | Spearman、NDCG、top-k recall |
| Task 6 最佳条件推荐 | 选择最优或接近最优条件 | Top-k success、regret |
| Task 7 OOD泛化 | 在新底物、新条件和新组合上评价 | 以上指标按OOD类型分层 |


## 8.2 五类推荐划分


| **划分** | **规则** | **用途** |
| --- | --- | --- |
| S0 Random | 反应记录随机划分 | 仅用于与历史工作对照；不作为主要结论 |
| S1 Within-group interpolation | 同一reaction group部分条件训练、部分条件测试 | 模拟已做少量实验后的条件补全 |
| S2 Reaction-group OOD | 整个reaction group只进入一个集合 | 测试新反应泛化 |
| S3 Component OOD | 测试集中某些ligand/base/solvent未在训练出现 | 测试新条件成分 |
| S4 Combination OOD | 成分单独见过，但组合未见 | 测试组合泛化 |
| S5 Double OOD | 新reaction group + 新条件/组合 | 最严格现实泛化 |


## 8.3 划分实施细节

- 所有 pair 的两个端点必须位于同一 split，避免 pair-level 泄漏。
- 同一 source table、plate 或 batch 优先作为不可拆分单元。
- 先固定测试集，再从剩余数据生成训练/验证集，防止调参污染。
- 每个 split 发布固定 seed 与 manifest，同时提供生成脚本。
- OOD 测试需报告条件实体覆盖、结构相似度和产率分布，确认难度真实存在。

# 9. 条件敏感性评价指标


| **指标** | **定义** | **解释** |
| --- | --- | --- |
| Absolute MAE/RMSE | 单条反应绝对误差 | 与既有产率预测工作可比 |
| Pairwise ΔMAE | \|(ŷB-ŷA)-(yB-yA)\| 的平均值 | 直接评价条件效应幅度 |
| Direction Accuracy | sign(Δŷ)=sign(Δy) | 评价升/降方向 |
| Sensitivity Ratio | E\|Δŷ\| / E\|Δy\| | <1 表示敏感性被压缩；>1 表示过度反应 |
| ΔPearson/ΔSpearman | 预测与真实Δyield相关 | 幅度与排序一致性 |
| Cliff AUPRC | 强悬崖识别精度 | 适合类别不平衡 |
| Top-k Success | 模型前k条件是否含高产条件 | 对应筛选效率 |
| Condition Regret | 真实最优产率−模型推荐条件真实产率 | 直接反映实验损失 |
| Within-group variance ratio | 预测组内方差/真实组内方差 | 诊断回归均值化 |
| Factor-wise sensitivity | 按ligand/base/solvent等分层计算 | 识别模型对哪类条件不敏感 |


# 10. 基线模型与方法开发


## 10.1 必须建立的基线


| **模型** | **输入/方法** | **目的** |
| --- | --- | --- |
| Mean/group mean | 全局平均、反应组平均、条件平均 | 检查是否只是频率和均值问题 |
| Condition-only | 仅输入条件，不输入反应结构 | 量化条件捷径 |
| Reaction-only | 仅输入底物/产物，不输入条件 | 量化结构主导程度 |
| DRFP + RF/XGBoost | 反应指纹与树模型 | 强、快速、可解释的传统基线 |
| Molecular descriptors + RF | 组分描述符拼接 | 复现HTE经典范式 |
| Yield-BERT/ChemBERTa regression | reaction SMILES Transformer | 文本模型基线 |
| Graph model | 反应物/产物/条件分子图编码 | 结构基线 |
| Multimodal Transformer | 反应结构token + 条件角色token + 连续变量 | 主深度模型 |


## 10.2 CYC-Loss：Condition Yield Cliff-aware Loss


在单条反应回归损失之外，增加同一 reaction group 内条件配对的差值、方向和幅度监督。第一版可采用 Huber 回归 + pairwise ΔHuber + ranking loss。


```text
L_total = L_abs + λΔ·Huber((ŷ_i-ŷ_j),(y_i-y_j))
          + λrank·Softplus[-sign(Δy_ij)(ŷ_i-ŷ_j)]
          + λinv·I(|Δy|≤τ_inv)|ŷ_i-ŷ_j|
```


训练时使用 group-aware sampler：每个 batch 同时采样多个 reaction groups，每个 group 至少采样2–4个不同条件，从而保证可形成有效配对。λ 采用 warm-up，避免早期 pair loss 过强。


## 10.3 CondFormer 原型

- Reaction encoder：编码反应物、产物和反应中心。
- Condition encoder：按角色分别编码 catalyst、ligand、base、solvent、additive，并编码连续条件。
- Interaction module：cross-attention 或双线性层建模 reaction×condition 交互。
- Group/pair head：同时输出绝对产率、ΔYield、cliff probability 和条件排序分数。
- 解释模块：报告条件角色注意力、成分替换敏感性和反事实条件。

# 11. 统计分析与关键实验设计


| **实验** | **内容** |
| --- | --- |
| E1 数据统计 | 各数据源反应数、group数、每组条件数、失败率、条件完整率、产率分布 |
| E2 条件效应谱 | 按因素统计ΔYield分布、cliff率、条件主效应与交互效应 |
| E3 模型敏感性诊断 | 比较reaction-only、condition-only和full model，分析shortcut |
| E4 随机 vs OOD | 量化随机划分对性能的高估程度 |
| E5 Cliff专属评价 | 仅在强cliff、moderate和invariant pair分别评价 |
| E6 CYC-Loss消融 | Δloss、ranking、invariance、sampling、阈值与λ消融 |
| E7 条件类型消融 | 移除ligand/base/solvent/temperature字段，观察性能变化 |
| E8 噪声与置信度 | A/B/C级数据分层；重复实验误差敏感性 |
| E9 跨数据集迁移 | HTE训练→另一个HTE/Real测试；预训练→微调 |
| E10 推荐模拟 | 给定固定预算top-k，比较找到最佳/高产条件的概率和regret |


# 12. 数据处理与代码实现流程


```text
Raw datasets
  ├─ HTE original files
  ├─ ORD protobuf/JSON
  ├─ literature tables
  └─ patent/ELN auxiliary data
        ↓
01_ingest → 02_standardize_structure → 03_normalize_conditions
        ↓
04_extract_outcomes → 05_atom_mapping_qc → 06_build_groups
        ↓
07_generate_pairs → 08_label_cliffs → 09_make_splits
        ↓
10_export_benchmark → 11_train_baselines → 12_analysis
```


## 12.1 推荐 GitHub 目录


```text
CondRxnBench/
├── README.md
├── configs/
├── data/raw/                 # 不提交受限数据
├── data/interim/
├── data/processed/
├── metadata/dataset_cards/
├── condrxn/
│   ├── ingest/
│   ├── chemistry/
│   ├── conditions/
│   ├── outcomes/
│   ├── grouping/
│   ├── pairs/
│   ├── splits/
│   └── metrics/
├── baselines/
├── notebooks/
├── tests/
├── scripts/
└── docs/
```


## 12.2 工程规范

- 所有数据处理由配置文件驱动，禁止在 notebook 中手工修改最终数据。
- 每一步输出 manifest、行数变化、过滤原因统计和数据 hash。
- 为关键函数编写单元测试：名称标准化、单位转换、group key、pair生成、split泄漏检查。
- 采用 parquet 保存主表，JSON/ORD用于交换，CSV仅用于人工检查。
- 固定环境文件和随机种子；使用数据版本号 v0.1/v0.2/v1.0。

# 13. 学生执行计划、里程碑与验收标准


| **时间** | **任务** | **具体工作** | **验收物** |
| --- | --- | --- | --- |
| 第1–2周 | 文献与数据盘点 | 完成数据源登记表、许可核查、下载原始文件；复现Ahneman数据读取 | dataset_inventory.xlsx；2页调研报告；raw manifest |
| 第3–4周 | 统一schema与条件词典 | 定义reaction_records和condition registry；完成RDKit结构标准化 | schema v0.1；条件词典；单元测试 |
| 第5–6周 | Ahneman数据集 | 完成清洗、分组、pair和五类split | Core-Ahneman v0.1；QC报告；baseline notebook |
| 第7–8周 | Perera数据集 | 完成底物对group和条件组合OOD | Core-Perera v0.1；交叉数据统计 |
| 第9–11周 | ORD/ORDerly | 写ORD parser；筛选可用HTE/优化数据 | ORD subset v0.1；dataset cards |
| 第12–14周 | 39k+ HTE与文献表 | 按子集处理；抽取首批20篇优化表 | Extended v0.1；人工复核报告 |
| 第15–16周 | 统一pair与cliff标签 | 完成质量等级、阈值分析和condition graph | pairs v0.5；graph files；泄漏审计 |
| 第17–19周 | 基线模型 | Mean/RF/XGB/DRFP/Transformer；全部split | baseline leaderboard v0.1 |
| 第20–22周 | CYC-Loss/CondFormer | 实现配对损失和group sampler；消融 | method results；模型代码 |
| 第23–24周 | 论文图表与初稿 | 完成Figure 1–6、主表和方法部分 | 论文初稿v0.1；公开发布清单 |


## 13.1 每周汇报模板

- 本周新增/处理的数据源与记录数。
- 原始→处理后行数变化及所有过滤原因。
- 发现的字段歧义、结构错误和条件规范化问题。
- 一个可复现结果：统计图、单元测试或模型表。
- 下周任务、风险和需要导师决定的问题。

## 13.2 阶段验收硬指标


| **指标** | **验收要求** |
| --- | --- |
| 数据可追溯 | 100%记录可追溯至source_dataset与source_record_id |
| 条件字段质量 | 核心HTE离散条件完整率>99%；连续条件按原数据完整性报告 |
| 结构成功率 | 核心数据SMILES解析/标准化成功率>99%，失败有QC列表 |
| 配对准确率 | 随机抽查200个strict pairs，单因素变化准确率≥98% |
| 无泄漏 | 所有pair端点同split；group/plate泄漏检查为0 |
| 可复现 | 从raw到benchmark可单命令运行；固定hash一致 |
| 基线完整 | 至少8类基线，全部在S0–S5上报告核心指标 |


# 14. 风险评估与替代方案


| **风险** | **表现** | **应对** |
| --- | --- | --- |
| 公开数据量不足 | 严格单因素pair数量低 | 优先合并多个HTE；半自动抽取优化表；与实验组合作生成小规模验证矩阵 |
| ORD记录异质 | 很多记录条件或yield不完整 | 先筛HTE/optimization标签；建立质量等级；不强行纳入主任务 |
| 条件名称难规范 | 同义词、商品名、复合催化体系 | 建立人工维护registry；结构/InChIKey与角色双重映射 |
| 原子映射失败 | 金属、离子、复杂反应导致错误 | HTE用设计元数据辅助；失败记录保留并按group元数据处理 |
| 模型提升有限 | CYC-Loss只改善cliff但损害整体MAE | 多任务权重warm-up；分层采样；Pareto报告而非只看单指标 |
| 论文被视为数据清洗 | 缺乏方法创新 | 突出Condition Cliff定义、condition graph、OOD协议、敏感性指标与CYC-Loss |
| 版权/许可限制 | 商业或论文数据不能再分发 | 发布处理代码、索引和可公开子集；受限数据只发布派生统计和说明 |


# 15. 预期论文结构与图表设计


| **图表** | **内容** |
| --- | --- |
| Figure 1 | 问题与总体框架：传统单条产率预测为何不敏感；CondRxnBench数据流程 |
| Figure 2 | 数据来源、reaction group、condition matrix和condition graph |
| Figure 3 | Condition Cliff定义、不同因素的ΔYield与cliff统计 |
| Figure 4 | 五类数据划分与泄漏示意 |
| Figure 5 | 基线模型在绝对误差与敏感性指标上的对比 |
| Figure 6 | CYC-Loss/CondFormer架构、消融和解释案例 |
| Table 1 | 各数据集规模、条件维度、失败比例和质量等级 |
| Table 2 | 各模型在S0–S5上的MAE、ΔMAE、DirectionAcc、Cliff AUPRC和Regret |


# 16. 最终交付物与发布策略

1. CondRxnBench-Core v1.0：可公开的HTE核心数据。
2. CondRxnBench-Extended：ORD和文献优化表扩展数据，以及许可说明。
3. reaction_records.parquet、condition_pairs.parquet、condition_graphs目录。
4. 数据字典、condition ontology、dataset cards和QC报告。
5. 固定的S0–S5 split manifests和泄漏检查报告。
6. 指标Python包与基线训练代码。
7. 公开GitHub、Zenodo/ORD数据版本、项目网站和排行榜。
8. 论文与Supplementary Methods，包括所有阈值、过滤规则和审计结果。

# 附录A：学生数据处理SOP


| **步骤** | **操作要求** |
| --- | --- |
| 原始数据登记 | 记录来源、许可、URL/DOI、下载日期、文件hash和原始列说明。 |
| 只读保存 | raw文件只读，不直接修改；任何修复写入interim层。 |
| 字段映射 | 把原始列映射到统一schema，并记录无法映射的字段。 |
| 结构标准化 | 解析、sanitize、canonicalize、InChIKey、scaffold和atom-map QC。 |
| 条件标准化 | 名称词典→结构映射→角色拆分→单位转换→缺失语义。 |
| 结果标准化 | 区分yield/conversion/selectivity，校验范围与测量方法。 |
| 去重与重复 | 区分重复记录和重复实验；重复实验不随意删除。 |
| 反应分组 | 生成strict/scaffold/template group，并抽样人工检查。 |
| 配对构建 | 优先单因素变化；保存改变字段和容差判断。 |
| 质量评分 | A–E级，记录所有QC flags。 |
| 数据划分 | 先组级/plate级划分，再生成pair，执行泄漏测试。 |
| 导出与版本化 | 生成parquet、manifest、stats和changelog。 |


# 附录B：数据集接入检查表

- □ 是否包含同一反应的多个条件？
- □ 是否明确保留低产率和失败实验？
- □ 是否能区分反应物、试剂、催化剂、配体、碱和溶剂？
- □ 产率类型和测量方法是否明确？
- □ 是否有plate、batch、table或实验系列标识？
- □ 是否有重复实验或误差？
- □ 是否允许公开再分发？
- □ 是否可追溯至原始记录？
- □ 能否构造至少一个单因素变化pair？
- □ 是否存在结构或条件字段系统性缺失？

# 参考文献与核心资源


1. Ahneman, D. T.; Estrada, J. G.; Lin, S.; Dreher, S. D.; Doyle, A. G. Predicting Reaction Performance in C–N Cross-Coupling Using Machine Learning. Science 2018, 360, 186–190.


2. Perera, D. et al. A Platform for Automated Nanomole-Scale Reaction Screening and Micromole-Scale Synthesis in Flow. Science 2018, 359, 429–434.


3. Kearnes, S. M. et al. The Open Reaction Database. Journal of the American Chemical Society 2021, 143, 18820–18826.


4. King-Smith, E. et al. Probing the Chemical Reactome with High-Throughput Experimentation Data. Nature Chemistry 2024.


5. Saebi, M. et al. On the Use of Real-World Datasets for Reaction Yield Prediction. Chemical Science 2023, 14, 4997–5005.


6. Schwaller, P. et al. Predicting Chemical Reaction Yields Using Deep Learning. Machine Learning: Science and Technology 2021.


7. ORDerly: Data Sets and Benchmarks for Chemical Reaction Data. Journal of Chemical Information and Modeling 2024.


8. Open Reaction Database documentation and public repository, accessed July 2026.


9. Therapeutics Data Commons: Reaction Yield Prediction tasks and dataset documentation.


10. Fitzner, M. et al. Machine Learning C–N Couplings: Obstacles for a General-Purpose Reaction Yield Prediction. ACS Omega 2023.


说明：项目启动时，学生应对所有公开数据源的最新版本、许可条款、下载入口和记录规模进行再次核验，并在 dataset card 中记录。本文中的规模用于项目规划，不代替最终数据审计。
