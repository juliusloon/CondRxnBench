# CondRxnBench default `chem` runtime

Validated 2026-07-31 direct interpreter:

```text
/Users/juliusloon/miniforge3/envs/chem/bin/python
Python 3.12.13; numpy 2.4.6; pandas 2.3.3; pyarrow 24.0.0;
scikit-learn 1.8.0; RDKit 2025.09.5; networkx 3.6.1; pytest 8.4.2
```

Installed during this execution: `scikit-learn 1.8.0`, `pytest 8.4.2`, and their pip dependencies (`joblib`, `threadpoolctl`, `iniconfig`, `pluggy`). Use this interpreter directly: the local `conda run` frontend currently panics in its Rattler system-configuration plugin under the sandbox.

`chem` is the default validation/evaluation environment. The frozen Phase 5 winner selection must remain on `environment/core_v0_2_py311_requirements.txt` (scikit-learn 1.5.2) until a new contract and pre-test freeze are deliberately created.
