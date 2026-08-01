# Phase 0 runtime record — 2026-07-31

## Environment

- Interpreter: CPython 3.11.15 (`/Users/juliusloon/.local/bin/python3.11`), macOS arm64.
- Isolated environment: `/private/tmp/condrxnbench-core-v0_2-py311` (ephemeral verification environment; rebuild from the versioned requirements file).
- Versioned input: `environment/core_v0_2_py311_requirements.txt`.

| Package | Resolved version |
| --- | ---: |
| numpy | 1.26.4 |
| pandas | 2.2.3 |
| pyarrow | 17.0.0 |
| scikit-learn | 1.5.2 |
| rdkit | 2024.03.6 |
| pandera | 0.20.4 |
| pytest | 8.3.3 |
| networkx | 3.3 |
| openpyxl | 3.1.5 |
| tabulate | 0.10.0 |

## Commands and result

```bash
/Users/juliusloon/.local/bin/uv venv /private/tmp/condrxnbench-core-v0_2-py311 \\
  --python /Users/juliusloon/.local/bin/python3.11
/Users/juliusloon/.local/bin/uv pip install \\
  --python /private/tmp/condrxnbench-core-v0_2-py311/bin/python \\
  -r environment/core_v0_2_py311_requirements.txt
env UV_CACHE_DIR=/private/tmp/condrxnbench-uv-cache \\
  /Users/juliusloon/.local/bin/uv pip check \\
  --python /private/tmp/condrxnbench-core-v0_2-py311/bin/python
```

The initial independent review found that `openpyxl` and `tabulate` were
missing from the first candidate specification. They were added and the
resolver installed 32 packages in total; `uv pip check` reported all installed
packages compatible. The v0.2 environment contract remains **Proposed** in
ADR 0003 until independent review accepts the Phase 0 gate.
