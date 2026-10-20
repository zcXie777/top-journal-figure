#!/usr/bin/env python3
"""Offline validation for a distributable Top Journal Figure skill repository."""

from __future__ import annotations

import json
import re
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
SEMVER = re.compile(r"^\d+\.\d+\.\d+(?:[-+][0-9A-Za-z.-]+)?$")
REQUIRED = [
    "SKILL.md",
    "VERSION",
    "LICENSE",
    "NOTICE",
    "README.md",
    "DATA_AND_THIRD_PARTY_NOTICE.md",
    "agents/openai.yaml",
    "assets/catalog-manifest.json",
    "assets/generated/pubcns-cases.json",
    "assets/generated/pubcns-style-index.json",
    "references/figure-selection.md",
    "references/figure-spec.schema.json",
]


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    errors: list[str] = []
    for relative in REQUIRED:
        if not (ROOT / relative).is_file():
            errors.append(f"missing required file: {relative}")

    version_path = ROOT / "VERSION"
    if version_path.is_file() and not SEMVER.fullmatch(version_path.read_text(encoding="utf-8").strip()):
        errors.append("VERSION must contain semantic version text")

    skill_path = ROOT / "SKILL.md"
    if skill_path.is_file():
        text = skill_path.read_text(encoding="utf-8")
        match = re.match(r"^---\s*\n(.*?)\n---\s*\n", text, flags=re.DOTALL)
        if not match:
            errors.append("SKILL.md must begin with YAML frontmatter")
        else:
            metadata = yaml.safe_load(match.group(1))
            if metadata.get("name") != ROOT.name:
                errors.append("SKILL.md name must match the repository folder name")
        if "references/figure-selection.md" not in text:
            errors.append("SKILL.md must route to the figure-selection gate")

    ui_path = ROOT / "agents" / "openai.yaml"
    if ui_path.is_file():
        ui = yaml.safe_load(ui_path.read_text(encoding="utf-8"))
        default_prompt = ui.get("interface", {}).get("default_prompt", "")
        if "$top-journal-figure" not in default_prompt:
            errors.append("agents/openai.yaml default_prompt must invoke $top-journal-figure")

    manifest_path = ROOT / "assets" / "catalog-manifest.json"
    cases_path = ROOT / "assets" / "generated" / "pubcns-cases.json"
    styles_path = ROOT / "assets" / "generated" / "pubcns-style-index.json"
    if manifest_path.is_file() and cases_path.is_file() and styles_path.is_file():
        manifest = load_json(manifest_path)
        cases = load_json(cases_path).get("items", [])
        styles = load_json(styles_path).get("items", [])
        if manifest.get("case_count") != len(cases):
            errors.append("manifest case_count does not match generated cases")
        if manifest.get("style_count") != len(styles):
            errors.append("manifest style_count does not match generated styles")
        if len({item.get("stable_id") for item in cases}) != len(cases):
            errors.append("generated case stable IDs must be unique")

    forbidden_extensions = {".png", ".jpg", ".jpeg", ".webp", ".gif", ".tif", ".tiff"}
    generated = ROOT / "assets" / "generated"
    if generated.exists():
        for path in generated.rglob("*"):
            if path.is_file() and path.suffix.lower() in forbidden_extensions:
                errors.append(f"source artwork must not be bundled in assets/generated: {path.name}")

    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print("OK: release structure, metadata, corpus manifest, and license boundary")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

