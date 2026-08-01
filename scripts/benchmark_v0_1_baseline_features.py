#!/usr/bin/env python3
"""Frozen, source-aware categorical feature views for baseline v0.1.

This module deliberately exposes no reaction-structure fallback.  Its only
eligible views are source-design groups and source-scoped condition component
references defined by the versioned feature config.
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FEATURE_CONFIG = ROOT / "configs" / "benchmark_v0_1_baseline_features.json"


def canonical_condition_tuple(refs: object, roles: list[str]) -> str:
    """Return the contract-ordered source-scoped component tuple."""
    if isinstance(refs, str):
        refs = json.loads(refs)
    mapping = {str(role): str(component) for role, component in refs}
    return json.dumps([[role, mapping[role]] for role in roles], separators=(",", ":"))


def load_config() -> dict[str, object]:
    return json.loads(FEATURE_CONFIG.read_text())
