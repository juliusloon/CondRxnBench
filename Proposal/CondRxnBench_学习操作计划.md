# CondRxnBench 学习操作计划

## 1. 计划目标

这份计划不是“把机器学习课程上完”，而是让你从零起步，尽快进入下面这条具体路径：

`读懂代表性 HTE 论文 -> 理解 ORD/HTE 数据结构 -> 能独立清洗 Ahneman–Doyle 数据 -> 建立第一版条件敏感性分析 -> 为 CondRxnBench 的后续建模打底`

对应你在研究计划书里的主任务，这份学习计划优先服务四个能力：

1. 看懂反应产率预测论文在做什么，尤其是“条件效应”而不是泛化的分子性质预测。
2. 看懂并处理 HTE / ORD 这类结构化反应数据。
3. 把化学问题翻译成机器学习任务、标签、划分和指标。
4. 在 CondRxnBench 的第一个核心数据集上形成可复用的数据处理习惯。

## 2. 总体策略

从你的项目目标看，最容易走偏的有两种：

1. 先去学很大一套通用深度学习，结果几周后还没碰到真实反应数据。
2. 一上来就直接写模型，但对 reaction group、condition pair、数据泄漏和条件字段标准化没有感觉。

所以更稳的路径是：

1. **先建立问题感**：知道这篇 Ahneman–Doyle 到底解决了什么化学问题。
2. **再建立数据感**：知道 HTE / ORD 记录长什么样，字段为什么难处理。
3. **再建立任务感**：知道什么是 baseline、split、label leakage、OOD。
4. **最后再进入建模**：先做简单可解释模型，再碰 GNN / Transformer。

## 3. 分阶段路线

建议按 12 周组织。前 6 周完成“能独立读数据和跑简单实验”，后 6 周完成“能为 CondRxnBench 第一阶段出稳定中间产物”。

### 阶段 A：建立最小背景（第 1-2 周）

目标：把你从“第一次接触该领域”带到“能看懂这条赛道里的基本语言”。

你这一阶段要掌握的不是推公式，而是下面几个核心概念：

- reaction yield prediction 是什么
- HTE 是什么，为什么它比普通文献反应更适合做学习任务
- 为什么随机划分会泄漏
- 什么叫 substrate effect，什么叫 condition effect
- 什么叫 out-of-distribution generalization
- 什么叫 pairwise / condition-sensitive evaluation

建议动作：

1. 精读 Ahneman–Doyle 这篇文章。
2. 读你的研究计划书第 1、2、3 章，把里面出现的术语单独记成词表。
3. 自己写一页笔记，回答下面 5 个问题：
   - 这篇文章的预测对象是什么？
   - 输入里的“条件”具体有哪些？
   - 作者为什么说线性回归不够？
   - 随机森林给出的不只是预测，还给了什么机理线索？
   - 这篇数据为什么比普通专利数据更适合做条件敏感性研究？

阶段交付物：

- 一份 1-2 页的“领域入门笔记”
- 一份术语表：yield / HTE / ORD / reaction group / cliff / OOD / split / descriptor

判断是否过关：

- 你能不用看论文，口头讲清楚 Ahneman–Doyle 的数据矩阵和核心化学结论。

### 阶段 B：补最少量机器学习基础（第 2-4 周）

目标：只学处理 CondRxnBench 当前任务真正需要的那部分机器学习。

你现在不需要完整学一遍深度学习教材。优先掌握：

- 监督学习基本框架：`X -> y`
- 回归任务：MAE、RMSE、R²
- 训练/验证/测试集区别
- 特征、标签、过拟合、数据泄漏
- one-hot / numerical feature / categorical feature
- 随机森林、XGBoost、线性回归各自的优缺点
- 什么是 pairwise learning 和 ranking intuition

建议动作：

1. 用一个很小的 tabular 数据集，自己练习一次完整回归流程。
2. 重点理解为什么“低 RMSE 不等于模型懂条件”。
3. 学会用一句话区分：
   - 单条产率回归
   - 配对差值预测
   - 排序/相对优劣学习

阶段交付物：

- 一页“CondRxnBench 相关 ML 最小知识图”
- 一个最小 notebook：读表、划分、训练 `LinearRegression/RandomForest/XGBoost`、输出 RMSE

判断是否过关：

- 你能解释为什么随机划分在 HTE 上会过于乐观。

### 阶段 C：建立化学反应数据处理基础（第 3-5 周）

目标：掌握处理反应数据最基础的工具链，而不是先上复杂模型。

这里优先学三类东西：

1. **结构工具**
   - SMILES
   - reaction SMILES
   - canonicalization
   - InChIKey
   - scaffold

2. **化学信息学工具**
   - RDKit 基本读写
   - Morgan fingerprint / ECFP
   - reaction fingerprint（先了解 DRFP 概念即可）

3. **表格工程**
   - pandas / polars
   - 缺失值检查
   - 分组统计
   - 去重
   - schema 检查

建议动作：

1. 用 RDKit 读入几种论文里的底物、配体、碱、添加剂结构。
2. 练习把实体名映射成标准化字段。
3. 练习用 pandas 做：
   - groupby
   - duplicated
   - merge
   - missingness summary

阶段交付物：

- 一个 `data_sanity_check.ipynb`
- 一张“条件字段标准化草案表”

判断是否过关：

- 你能独立判断一个字段应该是“缺失值”还是“明确的无配体/无添加剂”。

### 阶段 D：专攻 Ahneman–Doyle 数据（第 4-7 周）

目标：把第一份核心 HTE 数据真正吃透，因为它会成为你理解整个基准设计的模板。

这阶段你要做的不是立刻建模，而是先把这份数据作为“实验设计对象”读懂：

- 反应主体是什么
- 哪些因素在变
- 理论组合数是多少
- 有效记录数是多少
- 哪些是缺失实验、失败实验、无效实验
- 哪些字段是离散条件
- 哪些字段可以定义 reaction group

建议动作：

1. 找到 Ahneman–Doyle 的原始补充数据来源，不依赖二手 CSV。
2. 建立第一版原始记录表：
   - aryl halide
   - ligand
   - base
   - additive
   - yield
   - record index
3. 做 4 个最重要的统计图/表：
   - 各条件成分频次
   - yield 分布
   - 反应矩阵完整性
   - 各单因素扰动下的 `|Δyield|` 分布
4. 尝试定义第一版 `reaction_group_id`
5. 尝试构造第一版 `condition_pairs`

阶段交付物：

- `ahneman_raw.parquet`
- `ahneman_clean.parquet`
- `ahneman_pair_table.parquet`
- 一份 2-3 页的数据审计笔记

判断是否过关：

- 你能明确指出：哪些 pair 是高置信度 ligand cliff，哪些只是多因素同时变化导致的不可解释 pair。

### 阶段 E：引入 ORD / ORDerly 思维（第 6-8 周）

目标：你要开始从“单个论文表格”切换到“通用反应数据库 schema”思维。

这一阶段最重要的不是把 ORD 全部解析完，而是明白：

- 为什么 ORD 是 schema，不只是一个数据包
- reaction input / condition / outcome / provenance 为什么要分开
- 为什么同样叫 yield，不同来源的含义可能不同

建议动作：

1. 阅读 ORD 的基本 schema 文档或示例 JSON。
2. 从 3-5 条真实 ORD 记录出发，手工标注：
   - inputs
   - roles
   - condition fields
   - outcomes
   - provenance
3. 写一个最小 parser，把你真正关心的字段抽出来。
4. 对照你的计划书第 3.4 节，想清楚你自己的内部统一 schema 长什么样。

阶段交付物：

- 一个最小 `ord_parser.py` 或 notebook
- 一份“ORD 内部字段映射表”

判断是否过关：

- 你能说清楚“为什么不能把 ORD 直接当普通 CSV 用”。

### 阶段 F：把任务定义成基准问题（第 8-10 周）

目标：从“我会清洗数据”升级到“我知道我要评估什么”。

这里你要开始把研究计划书里的抽象概念真正落成表结构和评估协议：

- reaction-level prediction
- pair-level condition sensitivity
- cliff detection
- OOD split

建议动作：

1. 给 Ahneman 数据先做第一版 split 草案：
   - random split
   - reaction-group split
   - leave-one-ligand-out
   - leave-one-additive-out
2. 为每个 split 写一句“它要回答什么科学问题”。
3. 给每个任务写清楚输入、输出、指标。
4. 尝试定义第一版 cliff 阈值，例如：
   - `n_changed_factors = 1`
   - `abs_delta_yield >= 某阈值`

阶段交付物：

- `split_manifest.yaml`
- `task_definitions.md`
- 第一版 cliff 定义说明

判断是否过关：

- 你能区分“整体拟合好”和“条件敏感性好”这两件事，并给出不同指标。

### 阶段 G：跑第一批简单基线（第 10-12 周）

目标：用最简单、最稳的模型先建立实验地板，不要一上来做复杂网络。

建议顺序：

1. 线性回归
2. 随机森林
3. XGBoost / LightGBM
4. 简单 MLP

输入特征建议从易到难：

1. 纯条件 one-hot
2. 底物 fingerprint + 条件 one-hot
3. 反应 fingerprint + 条件结构特征

每跑一个模型，都至少看四类结果：

- overall RMSE
- 各 split 表现
- pairwise `Δyield` 方向正确率
- cliff subset 上的表现

阶段交付物：

- 一个统一 baseline notebook 或脚本
- 第一版 benchmark result 表
- 一页“模型失效模式观察”

判断是否过关：

- 你能指出某个模型是“记住底物了”还是“真的在用条件信息”。

## 4. 每周固定操作模板

为了避免学着学着散掉，建议每周固定做这 5 件事：

1. **读一篇或半篇相关论文**
   - 不追数量，追“能复述它的任务、数据、标签、split、结论”

2. **处理一小块真实数据**
   - 不是只看教程，一定要碰真实脏数据

3. **写一页结构化笔记**
   - 本周新概念
   - 本周解决的问题
   - 本周没解决的问题

4. **产出一个小 artifact**
   - 一张表、一段 parser、一个 notebook、一个数据检查脚本

5. **做一次口头复述**
   - 尝试用 3 分钟讲清楚本周进展

## 5. 推荐的学习顺序

如果你问“我下周一具体先干嘛”，那就是这个顺序：

1. 重新读 [CondRxnBench_详细研究计划书_中文版_v2.md](/Users/juliusloon/Documents/Files/data/CondRxnBench/Proposal/CondRxnBench_详细研究计划书_中文版_v2.md) 的第 1-3 章，只抓术语和任务定义。
2. 结合 [paper.md](/Users/juliusloon/Documents/Files/data/CondRxnBench/Buchwald-Hartwig-HTE/paper.md) 再精读一遍 Ahneman–Doyle，重点看 `S001`、`S008-S013`。
3. 用你自己的话写出 Ahneman 数据的字段表和实验设计。
4. 搭一个最小 Python 环境，确认能用 `pandas + rdkit + scikit-learn`。
5. 开始做 Ahneman 原始数据的第一版清洗，不急着建模。

## 6. 工具建议

第一阶段只建议固定下面这一套，不要工具太多：

- Python
- pandas
- RDKit
- scikit-learn
- jupyter notebook
- pyarrow/parquet

第二阶段再加：

- xgboost 或 lightgbm
- polars
- seaborn / matplotlib

更后面再碰：

- PyTorch
- PyG / DGL
- Transformer 类反应模型

## 7. 三个容易踩的坑

### 坑 1：把“会跑模型”误当成“进入领域”

这条线里最难的往往不是模型，而是：

- 字段语义
- 数据来源偏差
- split 设计
- 条件实体标准化

### 坑 2：过早追复杂模型

在你还没把 `reaction_group` 和 `condition_pair` 定义稳之前，做 GNN 或 Transformer 的收益很低。

### 坑 3：把所有数据源混成一个大表

你的计划书已经写得很对：不同来源的 yield 含义、实验设计和 outcome 类型并不一致。先把 Ahneman 做成干净模板，再扩展到 Perera、ORD 和 HTE Reactome，路线会稳很多。

## 8. 12 周后的理想状态

如果这 12 周推进顺利，你应该达到下面这个状态：

1. 能独立讲清楚 CondRxnBench 为什么不是普通 yield benchmark。
2. 能独立清洗 Ahneman–Doyle 数据并构造第一版 condition pairs。
3. 能解释 random split、group split、component OOD split 的差别。
4. 能跑通第一批 tabular baseline。
5. 能开始进入你计划书第一阶段的正式数据工程工作。

## 9. 我建议我们接下来怎么配合

最有效的推进方式不是我一次给你很多资料，而是我们按“每周一个明确交付物”往前走。

我建议下一步直接做这三件事：

1. 我帮你把 **第 1 周任务单** 拆出来，具体到每天做什么。
2. 我帮你搭一个 **Ahneman 数据处理最小工作流**，从原始文件到 `clean parquet`。
3. 我帮你列一个 **只保留必要内容的入门阅读清单**，避免你一开始读太散。

