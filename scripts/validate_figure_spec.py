#!/usr/bin/env python3
"""Dependency-free validation for the required figure-spec contract."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


HEX = re.compile(r"^#[0-9A-Fa-f]{6}$")
STATUSES = {"observed", "derived", "modelled", "assumed", "illustrative"}
SELECTION_MODES = {"user_confirmed", "user_specified", "explicit_auto_bypass"}


def validate(data: dict) -> list[str]:
    errors = []
    if not str(data.get("core_claim", "")).strip():
        errors.append("core_claim is required")
    selection = data.get("selection")
    if not isinstance(selection, dict):
        errors.append("selection must be an object")
    else:
        if selection.get("mode") not in SELECTION_MODES:
            errors.append(f"selection.mode must be one of {sorted(SELECTION_MODES)}")
        if not str(selection.get("chosen_type", "")).strip():
            errors.append("selection.chosen_type is required")
        candidates = selection.get("candidates")
        if candidates is not None and (
            not isinstance(candidates, list)
            or not all(isinstance(item, str) and item.strip() for item in candidates)
        ):
            errors.append("selection.candidates must be a list of non-empty strings")
    evidence = data.get("evidence")
    if not isinstance(evidence, list) or not evidence:
        errors.append("evidence must be a non-empty list")
    else:
        for index, item in enumerate(evidence):
            if not item.get("source"):
                errors.append(f"evidence[{index}].source is required")
            if item.get("status") not in STATUSES:
                errors.append(f"evidence[{index}].status must be one of {sorted(STATUSES)}")
    panels = data.get("panels")
    if not isinstance(panels, list) or not panels:
        errors.append("panels must be a non-empty list")
    else:
        for index, panel in enumerate(panels):
            for field in ("id", "role", "form"):
                if not panel.get(field):
                    errors.append(f"panels[{index}].{field} is required")
    palette = data.get("palette")
    if not isinstance(palette, dict):
        errors.append("palette must be an object")
    else:
        for field in ("ink", "neutral", "primary"):
            if not HEX.match(str(palette.get(field, ""))):
                errors.append(f"palette.{field} must be a six-digit HEX color")
        for field, value in palette.items():
            if not HEX.match(str(value)):
                errors.append(f"palette.{field} must be a six-digit HEX color")
    output = data.get("output")
    if not isinstance(output, dict):
        errors.append("output must be an object")
    else:
        if not isinstance(output.get("width_mm"), (int, float)) or output.get("width_mm", 0) <= 0:
            errors.append("output.width_mm must be positive")
        if not isinstance(output.get("formats"), list) or not output["formats"]:
            errors.append("output.formats must be a non-empty list")
        if not isinstance(output.get("editable"), bool):
            errors.append("output.editable must be boolean")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("spec", type=Path)
    args = parser.parse_args()
    data = json.loads(args.spec.read_text(encoding="utf-8"))
    errors = validate(data)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print("OK: figure specification is valid")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
