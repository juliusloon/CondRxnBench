#!/usr/bin/env python3
"""Verify the candidate immutable raw-input manifests without touching raw data."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MANIFESTS = (
    ROOT / "metadata/raw_input_manifests/ahneman_doyle_rxnpredict_v0_2_candidate.json",
    ROOT / "metadata/raw_input_manifests/perera_suzuki_miyaura_v0_2_candidate.json",
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> None:
    checked = 0
    for manifest_path in MANIFESTS:
        manifest = json.loads(manifest_path.read_text())
        assert manifest["manifest_schema_version"] == "1.0"
        assert manifest["manifest_status"] == "accepted_after_independent_review_2026-07-31"
        assert manifest["files"]
        for item in manifest["files"]:
            path = ROOT / item["path"]
            assert path.is_file(), path
            assert sha256(path) == item["sha256"], path
            checked += 1
    assert checked == 20
    print(f"Phase 0 candidate input-manifest verification passed: {checked} raw inputs.")


if __name__ == "__main__":
    main()
