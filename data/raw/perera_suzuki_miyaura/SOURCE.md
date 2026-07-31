# Perera Suzuki–Miyaura HTE：原始数据来源与固定快照

## 文献来源

- Perera, D.; Tucker, J. W.; Brahmbhatt, S.; *et al.* **A platform for automated nanomole-scale reaction screening and micromole-scale synthesis in flow.** *Science* **2018**, *359* (6374), 429–434. DOI: [10.1126/science.aap9112](https://doi.org/10.1126/science.aap9112).
- 论文列出的补充材料包含 `Data File S1`；本目录中的 `aap9112_Data_File_S1.xlsx` 即其文件名一致的数据表副本。
- `aap9112_perera_sm.pdf` 是该论文的 Supporting Online Material（60 页），包含 Materials and Methods、Experiment 2 的完整条件和表 S1–S3。

## 可复现获取路径

由于 Science 的网页下载端点在本次获取时被 Cloudflare 的自动化访问挑战拦截（HTTP 403），数据表从公开复现实例 `rxn4chemistry/rxn_yields` 的固定提交中取得。该仓库 README 将其 `data/Suzuki-Miyaura` 目录明确归为 Perera 文献的 Suzuki–Miyaura HTE 数据，并以 MIT 许可证发布其仓库内容；这不改变原始论文及其补充材料自身的权利状态。

- 上游仓库：<https://github.com/rxn4chemistry/rxn_yields>
- 固定提交：`d9e6b87ce1b881978490d68bfc00021e3b48127a`
- 固定原始文件 URL：<https://raw.githubusercontent.com/rxn4chemistry/rxn_yields/d9e6b87ce1b881978490d68bfc00021e3b48127a/data/Suzuki-Miyaura/aap9112_Data_File_S1.xlsx>
- 获取日期：2026-07-31

## 完整性

| 文件 | SHA-256 | 行 × 列 | 备注 |
| --- | --- | ---: | --- |
| `aap9112_Data_File_S1.xlsx` | `a869e020ba31bd5676c67a4791c3b7384711b5216de6af444b8cd0a24c284640` | 5,760 × 16 | Excel 的第一张工作表；后两张工作表为空 |
| `aap9112_perera_sm.pdf` | `54e505db0b1e7200552dae79dfff5398d1d2cbae08fcbfe472239aaa86c81b30` | 60 页 | 论文补充材料；用于为派生层提供带页码的固定实验元数据 |
| `UPSTREAM_REPO_LICENSE.txt` | `4cd19ee3f984c4cf21234b36d941f80fe7cbac61b4a104a558813cd3948857ce` | — | 固定上游仓库的 MIT 许可证副本；不替代原始论文/补充材料的权利声明 |

这是原始层：未重命名字段、未填补空白配体/碱、未截断或重算产率。任何项目内的标准化表、反应对或划分都应另存为派生层，并指向 `Reaction_No`。
