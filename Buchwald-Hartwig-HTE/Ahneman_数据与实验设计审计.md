# Ahneman-Doyle Buchwald-Hartwig HTE：数据与实验设计审计

## 先给结论

这不是一份来自彼此独立实验的普通“反应产率表”，而是一个**严格、稠密、但带有板式结构的部分全因子 HTE 矩阵**。它非常适合成为 CondRxnBench 的首个受控条件数据集：同一 C-N 偶联骨架在离散催化体系、碱和异噁唑添加剂下的条件效应能够被直接比较。但它不能被当作跨底物、跨尺度的通用产率数据，也不能把随机切分得到的高分直接理解为真正的化学外推能力。

本笔记以用户提供的正文 PDF、补充信息（SI）和已有的本地逐段读者为依据。正文 PDF 的正文页是图像型，数值与设计细节主要由 SI 交叉核验；正文引用 `paper.md` 的稳定段落锚点，SI 以其页码 `S#` 标注。

## 1. 实验到底在改变什么

反应是 Buchwald-Hartwig C-N 偶联：15 个芳基/杂芳基卤化物与固定的 *p*-toluidine 偶联；23 个异噁唑不是反应物主底物，而是以 1.0 当量加入的**片段添加剂**，用于探测其对偶联的抑制作用。因而，在 CondRxnBench 的条件本体中，`additive` 应是条件角色，不能误标为产物反应物。正文也明确说明，该策略是用添加剂筛选近似“底物嵌入异噁唑时的风险”，并不等价于直接预测该类真实底物。[`paper.md` S001](paper.md#S001)

| 因素 | 水平数 | 设计含义 | 建议标准化角色 |
| --- | ---: | --- | --- |
| 芳基/杂芳基卤化物 | 15 | 反应底物；含 5 组芳基/杂芳基骨架与 Cl/Br/I 变化 | `electrophile` |
| 胺 | 1 | 固定为 *p*-toluidine | `nucleophile` |
| Pd 催化体系 | 4 | 2-aminobiphenyl-Pd(II)-L-OTf 型 Buchwald 预催化剂，L 为 XPhos、t-BuXPhos、t-BuBrettPhos、AdBrettPhos | 首版保留为一个原子字段 `catalyst_system`；勿先拆成彼此独立的 Pd 与 ligand |
| 碱 | 3 | P2Et、BTMG、MTBD；选择理由是室温为液体、便于机器人加样 | `base` |
| 异噁唑添加剂 | 23 | 体系化扰动；添加剂 7 后续被作者剔除，但 SI 未说明具体原因 | `additive` |

**为什么催化体系先不要拆开。** 这四个水平是预先形成的 Pd-L 复合物，而不是一个恒定 Pd 源与四个可自由组合的游离配体。若在统一表中同时填写 `precatalyst=Pd` 和 `ligand=L`，模型或配对程序很容易虚构“同一 Pd 与任意 L 独立组合”的语义。应先把复合物作为完整条件实体保留；只有有充分的结构与制备信息时，再增加派生字段 `ligand_component`。

来源：SI S5-S8, Fig. S1, Tables S1-S2；正文 [`paper.md` S001](paper.md#S001)。

## 2. 1536 孔板如何组成 4,608 个孔位

每块板是 `32 行 x 48 列 = 1536` 孔；共 3 块板。

```text
行：4 个催化体系 x 8 个添加剂状态 = 32
列：3 个碱 x (15 个芳基卤化物 + 1 个无芳基卤化物对照) = 48
每板：32 x 48 = 1536
三板：3 x 1536 = 4608
```

Table S1 给出的关键细节是：Plate 1 包含 `additive = none, 1-7`，Plate 2 包含 `8-15`，Plate 3 包含 `16-23`；因此每个板恰有 8 个添加剂状态。Table S2 则让每种碱各占 16 列，其中第 16、32、48 列为 `aryl halide = none`。

由此可从版图直接推得下表，而不需要猜测“4,608”来自何处：

| 孔位类型 | 计算 | 数量 | 是否为带目标产物的主任务样本 |
| --- | --- | ---: | --- |
| 23 添加剂 x 15 芳基卤化物 x 4 催化体系 x 3 碱 | `23 x 15 x 4 x 3` | 4,140 | 是 |
| 无添加剂、但有芳基卤化物 | `1 x 15 x 4 x 3` | 180 | 是，可作为 `additive=None` 基线 |
| 无芳基卤化物对照 | `3 plates x 32 rows x 3 bases` | 288 | 否，不能与产物收率回归标签混合 |
| 总孔位 |  | 4,608 |  |

原文/已有读者所说的“4,608 个反应（含对照）”与这个重建完全一致。[`paper.md` S001](paper.md#S001)

作者在 Fig. S7 说明：用于建模的热图移除了“control reactions”和“含 additive 7 的反应”。若只保留 4,140 个主任务组合并移除 additive 7，对应 `4,140 - (15 x 4 x 3) = 3,960` 个组合。项目计划书记录的“约 3,955 条有效反应”与此相差 5 条；这很像额外的 UPLC/分析缺失值，但 **SI 只规定缺失产率应写为 `NA`，没有逐项列出这 5 条的孔位与原因**。在拿到原始 `yields.csv` 前，不应把“5 条”写成已证实的实验失败。

来源：SI S7-S12, Tables S1-S2, Fig. S7；项目计划书 [CondRxnBench_详细研究计划书_中文版_v2.md](../Proposal/CondRxnBench_详细研究计划书_中文版_v2.md)。

## 3. 一个孔里的化学条件与标签

机器人向每个反应孔分别加入 200 nL 的催化剂、芳基卤化物、toluidine、添加剂、碱的 DMSO 储液，总计 1.0 uL。由 SI 给出的储液浓度可反推实际条件：

| 项目 | 储液 | 每孔物质的量 | 反应中条件 |
| --- | ---: | ---: | --- |
| 芳基卤化物 | 0.50 M | 100 nmol | 1.0 equiv |
| *p*-Toluidine | 0.50 M | 100 nmol | 1.0 equiv |
| 添加剂 | 0.50 M | 100 nmol | 1.0 equiv |
| 碱 | 0.75 M | 150 nmol | 1.5 equiv |
| 催化体系 | 0.05 M | 10 nmol | 10 mol% |
| 总体积/浓度 | 1.0 uL | 100 nmol 限量底物 | 0.10 M |
| 温度/时间 | - | - | 60 C, 16 h |

反应在 N2 手套箱（典型 O2 < 5 ppm）中以 1536 孔板进行。反应后向每孔补加 3 uL、0.0025 M di-tert-butylbiphenyl 内标 DMSO 溶液，取样到 384 孔分析板，以 UPLC 的 UV 210 nm 峰面积和内标求得产率；SI 同时给出 ESI+ 检测配置。产品保留时间由放大反应所得产物建立。

这决定了标签的正确名称应为：

```text
yield_method = "UPLC_UV210_internal_standard"
yield_type   = "assay_yield"  # 不是 isolated yield
```

SI 没有报告逐个条件的独立重复、标准差、校准曲线或响应因子校正。因此每条 `yield` 应视为**单孔、高通量内标估计值**，而不是带已知测量方差的真值。作者认为实验与分析误差合计“可能至少为 5%”，这是合理的误差量级判断，但不是该数据集由重复实验估出的不确定性。[`paper.md` S001](paper.md#S001)

来源：SI S3-S5, S9-S10, Table S3。

## 4. 这个设计最强的地方

1. **局部可比性非常强。** 固定胺、溶剂、浓度、温度、时间和规模后，任一有效主任务孔只在四类离散因素中变化。对同一芳基卤化物，换碱、换催化体系或换添加剂的产率差可以作为明确的条件响应。

2. **组合覆盖是完整的。** 在每个添加剂所在的板内，`4 catalyst_system x 3 base x 15 electrophile` 是满矩阵，不是经验性挑选的一小部分条件。因此它天然支持单因素条件配对，以及相同底物下的“最优条件排序”任务。

3. **故意把机制风险压入条件空间。** 添加剂的电子性质被系统改变，且最终通过 N-O 氧化加成实验作了机制检验。这使“添加剂导致的条件悬崖”具有化学解释空间，而不只是数值噪声。[`paper.md` S012](paper.md#S012), [`paper.md` S013](paper.md#S013)

## 5. 设计中必须诚实保留的限制

### 5.1 Plate 与 additive 集合完全混杂

所有 additive 1-7/none 只在 Plate 1，8-15 只在 Plate 2，16-23 只在 Plate 3。也就是说，`plate_id` 与“添加剂属于哪个集合”完全共线。若三块板的密封、加样、蒸发、UPLC 批次或仪器漂移不同，模型可能把部分板效应学成添加剂效应；这个数据本身无法完全分离两者。

对 CondRxnBench：必须保存 `plate_id`、`row`、`column`、`well_id`，并把“plate-aware 分析”列为 QC。它们不应默认喂给主预测模型，以免将板次捷径当作化学信息；但应被用于残差按板分布、边缘孔效应和批次敏感性审计。

### 5.2 板内布局也不是随机化证据

行同时编码催化体系与添加剂，列同时编码碱与芳基卤化物；SI 给出的是固定映射，未说明随机化或板内重排。完整矩阵缓解了很多系统误差，但无法证明不存在行/列/边缘位置效应。没有原始孔位产率时，不能把 Fig. S4-S7 的热图视为位置效应已被排除的证据。

### 5.3 无重复意味着不能把“产率差”直接等同于 Condition Cliff

未来我们定义 condition cliff 时，阈值应包含测量误差缓冲，例如先以 `|delta_yield| >= 15 percentage points` 作为候选，再做 10/15/20 的敏感性分析；不能把 2-5 个百分点的单孔差异赋予机制意义。这个建议是基于单孔标签和作者约 5% 误差量级的推断，不是原文给出的阈值。

### 5.4 HTE 工艺条件限制了可迁移性

100 nmol、1 uL、DMSO、密封 1536 孔板、严格低氧、60 C/16 h 的结果，首先描述的是该 HTE 工艺窗口。它不自动外推至毫摩尔放大、其他溶剂、不同 Pd 前体、空气操作或改变温度/时间的 Buchwald-Hartwig 反应。放大产品的制备程序本身也使用了不同条件，不能拿来验证 HTE 标签的严格可迁移性。

### 5.5 添加剂消耗被观察但没有进入标签或特征

SI 尽可能记录剩余起始物与添加剂，但因为色谱峰重叠，添加剂剩余量不稳定，最终未用于建模。正文也据此提醒：当异噁唑嵌入真实底物时，模型可能受限。[`paper.md` S009](paper.md#S009), [`paper.md` S011](paper.md#S011)。这正是“片段添加剂筛选”与“底物反应预测”之间不可消失的差距。

## 6. 对原论文机器学习结果应怎样解读

| 论文设置 | 它实际衡量什么 | 不能证明什么 |
| --- | --- | --- |
| 随机 70/30 切分 | 在同一稠密组合矩阵内、共享大部分组分的插值 | 未见过的新添加剂/新芳基卤化物/新催化体系的泛化 |
| 10-fold CV（训练部分） | 同分布模型选择 | 独立化学域 OOD |
| Plate 1+2 训练、Plate 3 添加剂测试 | 未见添加剂的较强 OOD 检验 | 去除板次影响后的纯化学 OOD，因为 additive set 与 plate 混杂 |
| ArBr 训练，ArCl/ArI 测试 | 离去基团类别迁移失败的方向性 | 跨离去基团仍有可靠定量外推 |
| 仅低产率训练、高产率测试 | 向标签区间外插 | 反应优化中“找到高收率”的能力 |

还有三个实现/报告层面的注意点：

1. SI S25 说明描述符在数据切分**前**用全体数据的均值和标准差做了中心化和缩放；作者自己也写出“更合适但未使用”的训练集拟合、测试集变换方案。这是轻度预处理泄漏。对随机森林影响通常很小，但 CondRxnBench 的所有可缩放基线都应在每个训练折内 fit transformer。

2. 120 个描述符中存在强共线性，尤其是同一组分的电子/振动性质。随机森林的重要性不是因果效应；作者的 PCA 分析也显示 ligand、芳基卤化物和添加剂的相关描述符会改变重要性排序。把 `additive *C3 NMR shift` 视为机制假设生成器是合理的，把它直接视为唯一因果驱动则不成立。[`paper.md` S012](paper.md#S012)

3. 样本外添加剂测试的报告指标需要复现时重新核对：正文报告平均 RMSE 11.3%、R2 0.91；SI S36 报告平均 RMSE 11.0%、R2 0.83。二者可能来自不同聚合方式或版本，但当前材料未给出足以消除差异的说明。同样，“5% 约 230 个实验”的分母正好对应 4,608 个总孔位，而非 3,955/3,960 个剔除后有效样本；稀疏实验曲线也应以原始代码和标签文件复算。

## 7. 写入 CondRxnBench 的最小数据契约

建议将这个数据源拆成两个层次，而不是只保存一个扁平 CSV：

| 层次 | 记录范围 | 用途 |
| --- | --- | --- |
| `raw_screen` | 4,608 个设计孔位；包括无芳基卤化物和无添加剂控制 | 保留实验设计、缺失/对照和孔位 provenance |
| `yield_modeling` | 原作者实际使用的有效产率子集；保留 0 收率，剔除无定义产品标签 | 基线回归与可比复现 |
| `condition_pairs` | 同一 `reaction_group` 下恰变 1 个条件因素的成对记录 | Condition Cliff 和条件效应任务 |

最低字段应包括：

```text
source_dataset              = "ahneman_doyle_2018_buchwald_hartwig_hte"
source_paper_doi            = "10.1126/science.aar5169"
plate_id, row, column, well_id
electrophile_id, electrophile_smiles, electrophile_halide
nucleophile_id              = "p_toluidine"
catalyst_system_id, catalyst_system_smiles, ligand_name
base_name, additive_id, additive_smiles
solvent_1                   = "DMSO"
temperature_C = 60, time_h = 16, concentration_M = 0.1
scale_mmol = 0.0001, catalyst_loading_mol_pct = 10
electrophile_equiv = 1, nucleophile_equiv = 1, base_equiv = 1.5, additive_equiv = 1
yield, yield_method, label_status, control_type, analytical_missing_reason
source_file, source_page, source_figure_or_table, provenance_path
```

其中 `reaction_group_id` 应固定为“同一 electrophile + 固定 p-toluidine + 同一目标 C-N 成键”，**不应**把 additive 放进反应身份；它是要比较的条件。`catalyst_system_id`、`base_name`、`additive_id` 则是条件节点。

## 8. 我们下一步应实际做什么

1. 从原始 `rxnpredict` 数据/`yields.csv` 导入，而不是从热图人工抄数；先验证总行数、`NA`、0 产率、additive 7 和所有控制的具体状态。
2. 用 Tables S1-S2 程序化重建 3 x 32 x 48 设计表，再与原始产率按 `plate,row,column` 严格连接；连接后必须得到一个可解释的 4,608 孔位审计表。
3. 输出一份 QC：`observed/missing` 交叉表、每板/每行/每列的产率分布、边缘孔与中心孔残差、以及去掉 `plate_id` 后的模型残差比较。
4. 发布至少五套划分：random、leave-one-additive、leave-one-catalyst-system、leave-one-electrophile、leave-one-halide-class；所有 scaler/feature selection 只在训练折拟合。
5. Condition Cliff 先限定在满配对、同一反应组、单一条件改变的记录；输出每个 cliff 的 `changed_factor`、`delta_yield`、原始孔位和板次，而不是只输出二元标签。

## 术语

| 术语 | 本项目中的固定含义 |
| --- | --- |
| HTE / UHTE | high-/ultra-high-throughput experimentation；这里指 1536 孔、纳摩尔尺度自动化实验 |
| assay yield | 由 UPLC 内标估计的产率，不等同于分离产率 |
| catalyst system | 此数据中以预形成 Pd-L 复合物为单位的催化条件 |
| reaction group | 固定底物和目标转化、允许条件变化的一组实验 |
| condition pair | 同一 reaction group 且仅一个条件字段不同的两条记录 |
| condition cliff | 在严格 condition pair 上出现显著产率跃迁的现象；阈值需结合标签不确定性定义 |

## 来源定位

- 正文的实验空间与解释：[`paper.md` S001](paper.md#S001), [`paper.md` S008-S013](paper.md#S008)
- SI 的反应设置与分析：SI S3-S12
- SI 的描述符、训练与 OOD：SI S23-S41
- 本地原始文件：`/Users/juliusloon/Zotero/storage/L6NSN2VY/Ahneman et al. - 2018 - Predicting reaction performance in C–N cross-coupling using machine learning.pdf`；`/Users/juliusloon/Zotero/storage/EGYHDL42/aar5169-ahenman-sm_revision_1.pdf`
