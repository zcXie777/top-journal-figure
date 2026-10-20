#!/usr/bin/env python3
"""Rank figure archetypes and corpus-derived palette precedents."""

from __future__ import annotations

import argparse
import colorsys
import json
from pathlib import Path


TONE_ALIASES = {
    "restrained": {"muted", "balanced"},
    "contrast-led": {"balanced", "vivid"},
    "vivid-but-controlled": {"vivid", "balanced"},
    "colorblind-first": {"muted", "balanced"},
    "corpus match": {"muted", "balanced", "vivid"},
    "auto": {"muted", "balanced", "vivid"},
}


def score_case(case: dict, tone: str, journal: str) -> float:
    if case.get("status") != "ok":
        return -100.0
    score = 3.0 if case.get("tone") in TONE_ALIASES.get(tone, {tone}) else 0.0
    if journal and journal.lower() in case.get("journal", "").lower():
        score += 5.0
    score += max(0.0, 1.5 - abs(case.get("whitespace_ratio", 0.4) - 0.38) * 3)
    score += 0.5 if case.get("density") == "balanced" else 0
    return score


def semantic_palette(case: dict) -> tuple[dict, list[str]]:
    items = case.get("palette", [])
    ink = next((item["hex"] for item in items if item["role"] == "ink"), "#222222")
    neutral = next((item["hex"] for item in items if item["role"] == "neutral"), "#B8BDC5")
    candidates = []
    for item in items:
        if item["role"] in {"background", "ink"}:
            continue
        if item["hex"] in {ink, neutral}:
            continue
        r, g, b = [value / 255 for value in item["rgb"]]
        _, saturation, value = colorsys.rgb_to_hsv(r, g, b)
        if saturation >= 0.07 and 0.24 <= value <= 0.94:
            candidates.append((saturation * 2 + item.get("share", 0), item))
    candidates.sort(key=lambda pair: -pair[0])
    accents = []
    for _, item in candidates:
        if all(sum((a - b) ** 2 for a, b in zip(item["rgb"], prior["rgb"])) ** 0.5 >= 42 for prior in accents):
            accents.append(item)
        if len(accents) == 5:
            break
    if not accents:
        accents = [{"hex": "#3B6FB6", "rgb": [59, 111, 182]}, {"hex": "#D97A45", "rgb": [217, 122, 69]}]
    mapping = {"ink": ink, "neutral": neutral, "primary": accents[0]["hex"]}
    if len(accents) > 1:
        mapping["secondary"] = accents[1]["hex"]
    for index, item in enumerate(accents[2:5], 1):
        mapping[f"support_{index}"] = item["hex"]
    warnings = []
    if len(accents) > 1:
        hues = []
        values = []
        for item in accents[:2]:
            r, g, b = [value / 255 for value in item["rgb"]]
            hue, _, value = colorsys.rgb_to_hsv(r, g, b)
            hues.append(hue)
            values.append(value)
        red_green = (hues[0] < 0.08 and 0.22 < hues[1] < 0.46) or (hues[1] < 0.08 and 0.22 < hues[0] < 0.46)
        if red_green and abs(values[0] - values[1]) < 0.18:
            warnings.append("primary/secondary may be difficult under red-green color-vision deficiency; add shape/line encoding")
    return mapping, warnings


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser()
    parser.add_argument("--goal", default="auto")
    parser.add_argument("--family", default="auto")
    parser.add_argument("--tone", default="corpus match")
    parser.add_argument("--journal", default="")
    parser.add_argument("--limit", type=int, default=5)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    archetypes = json.loads((root / "assets" / "archetypes.json").read_text(encoding="utf-8"))
    corpus_path = root / "assets" / "generated" / "pubcns-style-index.json"
    corpus_payload = json.loads(corpus_path.read_text(encoding="utf-8")) if corpus_path.exists() else {"items": []}
    overrides_path = root / "assets" / "curated" / "overrides.json"
    overrides = json.loads(overrides_path.read_text(encoding="utf-8")).get("overrides", {})
    corpus = []
    for item in corpus_payload.get("items", []):
        merged = dict(item)
        merged.update(overrides.get(item.get("stable_id"), {}))
        corpus.append(merged)
    goal = args.goal.lower()
    family = args.family.lower()
    ranked_archetypes = []
    for item in archetypes:
        score = 0
        if goal == "auto" or goal in [value.lower() for value in item["goals"]]:
            score += 5
        if family == "auto" or family in [value.lower() for value in item["families"]]:
            score += 3
        ranked_archetypes.append((score, item))
    ranked_archetypes.sort(key=lambda pair: (-pair[0], pair[1]["id"]))
    ranked_cases = sorted(corpus, key=lambda case: (-score_case(case, args.tone, args.journal), case.get("sequence") or 10**9))
    matches = []
    for item in ranked_cases:
        if item.get("status") != "ok" or len(matches) >= max(1, args.limit):
            continue
        mapping, warnings = semantic_palette(item)
        matches.append(
            {
                "stable_id": item.get("stable_id"),
                "sequence": item.get("sequence"),
                "title": item.get("title"),
                "journal": item.get("journal"),
                "tone": item.get("tone"),
                "density": item.get("density"),
                "semantic_palette": mapping,
                "accessibility_warnings": warnings,
                "article_url": item.get("article_url"),
            }
        )
    payload = {
        "request": {"goal": args.goal, "family": args.family, "tone": args.tone, "journal": args.journal},
        "archetypes": [item for score, item in ranked_archetypes[:3] if score > 0],
        "corpus_matches": matches,
    }
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        for item in payload["archetypes"]:
            print(f"archetype: {item['id']} — {item['layout']}")
        for item in matches:
            colors = ", ".join(item["semantic_palette"].values())
            print(f"case {item['sequence']}: {item['title']} — {colors}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
