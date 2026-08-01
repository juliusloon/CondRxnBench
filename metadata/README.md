# CondRxnBench-Core v0.1 元数据

本目录定义的是 **Core 数据发布版**，不是已经完成全部 S0--S5 划分和模型评测的 benchmark 发布版。

Core v0.1 只包含两套可审计的 HTE 主矩阵及其严格单因素配对：

- Ahneman--Doyle Buchwald--Hartwig：4,140 条主矩阵记录、55,676 个 pair；
- Perera Suzuki--Miyaura：5,760 条主矩阵记录、60,480 个 pair。

构建命令：

```bash
python3 scripts/build_core_v0_1.py
```

产物在 `data/processed/core_v0_1/`：

- `reaction_records.csv`：9,900 条规范化实验记录；
- `condition_pairs.csv`：116,156 个已枚举 strict pair；
- `condition_registry.csv`：仅从实际记录生成的条件实体清单；
- `manifest.json`：计数、语义范围和文件 SHA-256。

`not_reported` 表示来源或当前可审计重建中未报告，不能被解释为化学上的“无该成分”。`NULL_COMPONENT` 则表示 Perera 原始表中显式的 `None` 条件水平。两者绝不等价。

阅读顺序：

1. [统一 Schema](unified_schema.md)
2. [数据字典](data_dictionary.md)
3. [Ahneman--Doyle dataset card](dataset_cards/ahneman_doyle_hte.md)
4. [Perera dataset card](dataset_cards/perera_suzuki_miyaura_hte.md)
5. [条件词典规则](condition_registry/condition_ontology.md)
