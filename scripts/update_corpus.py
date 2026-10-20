#!/usr/bin/env python3
"""Preview or atomically refresh all generated corpus artifacts."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path


def load_json(path: Path, default: object) -> object:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else default


def run(command: list[str]) -> None:
    completed = subprocess.run(command, text=True, check=False)
    if completed.returncode:
        raise RuntimeError(f"command failed ({completed.returncode}): {' '.join(command)}")


def ids(payload: dict) -> set[str]:
    return {item["stable_id"] for item in payload.get("items", [])}


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="preview changes without replacing generated files")
    parser.add_argument("--workers", type=int, default=6)
    args = parser.parse_args()

    sources = load_json(root / "assets" / "sources.json", {"sources": []})
    source = next((item for item in sources["sources"] if item["id"] == "pubcns-wechat-colors"), None)
    if not source:
        raise SystemExit("missing pubcns-wechat-colors in assets/sources.json")
    generated = root / "assets" / "generated"
    current_cases_path = generated / "pubcns-cases.json"
    current_style_path = generated / "pubcns-style-index.json"
    old_cases = load_json(current_cases_path, {"items": []})

    with tempfile.TemporaryDirectory(prefix="top-journal-figure-update-") as temp_name:
        temp_dir = Path(temp_name)
        new_cases_path = temp_dir / "pubcns-cases.json"
        new_style_path = temp_dir / "pubcns-style-index.json"
        run(
            [
                sys.executable,
                str(root / "scripts" / "ingest_wechat_album.py"),
                "--url",
                source["url"],
                "--source-id",
                source["id"],
                "--minimum",
                str(source.get("minimum_items", 0)),
                "--output",
                str(new_cases_path),
            ]
        )
        command = [
            sys.executable,
            str(root / "scripts" / "extract_style_index.py"),
            "--input",
            str(new_cases_path),
            "--output",
            str(new_style_path),
            "--workers",
            str(args.workers),
        ]
        if current_style_path.exists():
            command.extend(["--previous", str(current_style_path)])
        run(command)

        new_cases = load_json(new_cases_path, {"items": []})
        new_style = load_json(new_style_path, {"items": []})
        new_ids = ids(new_cases)
        if len(new_ids) != len(new_cases["items"]):
            raise RuntimeError("duplicate stable IDs in refreshed corpus")
        style_ids = ids(new_style)
        if style_ids != new_ids:
            raise RuntimeError("case/style stable ID sets do not match")
        successes = sum(item.get("status") == "ok" for item in new_style["items"])
        if successes / max(len(new_ids), 1) < 0.95:
            raise RuntimeError(f"style extraction success rate below 95%: {successes}/{len(new_ids)}")

        old_ids = ids(old_cases)
        old_hashes = {item["stable_id"]: item.get("content_hash") for item in old_cases.get("items", [])}
        changed = sorted(
            stable_id
            for stable_id in new_ids & old_ids
            if next(item for item in new_cases["items"] if item["stable_id"] == stable_id).get("content_hash")
            != old_hashes.get(stable_id)
        )
        summary = {
            "old_count": len(old_ids),
            "new_count": len(new_ids),
            "added": sorted(new_ids - old_ids),
            "changed": changed,
            "removed": sorted(old_ids - new_ids),
            "style_successes": successes,
            "check_only": args.check,
        }
        print(json.dumps(summary, ensure_ascii=False, indent=2))
        if args.check:
            return 0

        generated.mkdir(parents=True, exist_ok=True)
        shutil.copy2(new_cases_path, current_cases_path)
        shutil.copy2(new_style_path, current_style_path)
        manifest_path = root / "assets" / "catalog-manifest.json"
        manifest = load_json(manifest_path, {})
        manifest.update(
            {
                "schema_version": 1,
                "corpus_version": int(manifest.get("corpus_version", 0)) + 1,
                "extractor_version": int(new_style.get("extractor_version", 1)),
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "source_ids": [source["id"]],
                "case_count": len(new_ids),
                "style_count": successes,
            }
        )
        temp_manifest = manifest_path.with_suffix(".tmp")
        temp_manifest.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        temp_manifest.replace(manifest_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
