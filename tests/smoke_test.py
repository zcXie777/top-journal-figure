#!/usr/bin/env python3
"""Offline smoke tests for corpus integrity and deterministic helpers."""

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from copy import deepcopy
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load(path: Path) -> object:
    return json.loads(path.read_text(encoding="utf-8"))


def import_script(name: str):
    path = ROOT / "scripts" / f"{name}.py"
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader
    spec.loader.exec_module(module)
    return module


def main() -> int:
    cases = load(ROOT / "assets" / "generated" / "pubcns-cases.json")
    styles = load(ROOT / "assets" / "generated" / "pubcns-style-index.json")
    manifest = load(ROOT / "assets" / "catalog-manifest.json")
    case_ids = [item["stable_id"] for item in cases["items"]]
    style_ids = [item["stable_id"] for item in styles["items"]]
    assert len(case_ids) == 122
    assert len(case_ids) == len(set(case_ids))
    assert set(case_ids) == set(style_ids)
    assert all(item["status"] == "ok" for item in styles["items"])
    assert manifest["case_count"] == len(case_ids)
    assert manifest["style_count"] == len(style_ids)

    validator = import_script("validate_figure_spec")
    example = load(ROOT / "assets" / "example-figure-spec.json")
    assert validator.validate(example) == []
    invalid_selection = deepcopy(example)
    invalid_selection["selection"]["mode"] = "silent_default"
    assert any("selection.mode" in error for error in validator.validate(invalid_selection))

    completed = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts" / "recommend_style.py"),
            "--goal",
            "relationship",
            "--family",
            "multi-panel result",
            "--tone",
            "restrained",
            "--limit",
            "2",
            "--json",
        ],
        text=True,
        capture_output=True,
        check=True,
    )
    recommendations = json.loads(completed.stdout)
    assert recommendations["archetypes"]
    assert len(recommendations["corpus_matches"]) == 2
    print("OK: corpus, manifest, spec validator, and recommender")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
