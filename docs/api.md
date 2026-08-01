# 数据与命令接口

当前项目没有网络服务 API；对外稳定接口是版本化的 CSV/Parquet 数据集、schema 和可重跑的 Python 命令。本文件定义 Core v0.1 与已审查的 Core v0.2 candidate 的最小使用约定。

## 构建与验证命令

```bash
# 从两套已处理主矩阵/pair 生成统一 Core 层
python3 scripts/build_core_v0_1.py

# 独立检查计数、主键、标签状态、pair 不变量和 manifest
python3 tests/verify_core_v0_1.py

# 从 immutable Core v0.1 和已固化输入构建 v0.2 candidate；默认写入新目录
python3 scripts/build_core_v0_2.py --out-dir data/processed/core_v0_2

# 检查 Arrow schema、CSV/Parquet 语义、source/role FK、states 与守恒
python3 tests/verify_core_v0_2.py --out-dir data/processed/core_v0_2
```

调用方应将命令的 Python 版本、依赖版本、git 提交和输出 manifest 一并保存。构建脚本覆盖的是派生交付物，不会修改 `data/raw/`。

## Core v0.1 文件合约

| 文件 | 主键 | 用途 |
| --- | --- | --- |
| `reaction_records.csv` | `reaction_id` | 统一的实验记录与响应/测量语义 |
| `condition_pairs.csv` | `pair_id` | 已枚举的、同组内的 strict 单因素条件对 |
| `condition_registry.csv` | source-scoped `component_id` | 从实际记录派生的条件词典；同名跨源条件默认不合并 |
| `manifest.json` | — | 行数、语义范围和文件 SHA-256 |

完整字段、可取值和跨文件规则见 [`../configs/core_v0_1_schema.json`](../configs/core_v0_1_schema.json) 与 [`../metadata/unified_schema.md`](../metadata/unified_schema.md)。

## Core v0.2 candidate 文件合约

`data/processed/core_v0_2/` 的 authoritative 格式为 Parquet，CSV 仅为人工核查镜像。它保留 9,900 条主矩阵、468 条独立 Ahneman controls，并新增 source-scoped registry、逐 record 结构 assertion、连续条件 observation、混合溶剂 composition 与 pending mapping side tables。读取 CSV 时必须关闭自动 NA 解析；`NA`、`not_reported`、`NULL_COMPONENT` 的语义由 [`../configs/core_v0_2_contract.json`](../configs/core_v0_2_contract.json) 定义。

该目录是 **candidate_not_promoted** 的标准化层：不包含 v0.2 pairs、graphs、splits、success/cliff labels 或模型结果，不能被当作 Benchmark v0.1。

## 必须遵守的读取约定

- 不要把 `not_reported` 当作空字符串或化学上的“无”。
- 只有 `yield_observed = true` 时才可使用 `yield_percent`；`zero_yield = true` 只表示观测到的 0。
- 仅当 `n_changed_factors = 1` 时将 pair 作为 strict 单因素比较；不得把它当作多因素对照。
- `success_label` 与 `cliff_label` 目前均为 `not_assigned`，下游代码不得将其视为训练标签。
- 比较绝对产率时必须按 `source_dataset` 和 `yield_type` 分层。
