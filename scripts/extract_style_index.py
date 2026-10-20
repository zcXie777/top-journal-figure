#!/usr/bin/env python3
"""Derive compact palette and composition features from remote corpus images."""

from __future__ import annotations

import argparse
import colorsys
import io
import json
import math
import tempfile
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen

import numpy as np
from PIL import Image, ImageFilter


EXTRACTOR_VERSION = 1


def fetch_bytes(url: str, timeout: int = 30) -> bytes:
    request = Request(url, headers={"User-Agent": "Mozilla/5.0", "Referer": "https://mp.weixin.qq.com/"})
    with urlopen(request, timeout=timeout) as response:
        data = response.read(25_000_001)
    if len(data) > 25_000_000:
        raise ValueError("image exceeds 25 MB safety limit")
    return data


def hex_color(rgb: tuple[int, int, int]) -> str:
    return "#{:02X}{:02X}{:02X}".format(*rgb)


def analyze(case: dict) -> dict:
    result = {
        key: case.get(key)
        for key in ("stable_id", "content_hash", "visual_hash", "sequence", "title", "journal", "article_url")
    }
    result["extractor_version"] = EXTRACTOR_VERSION
    try:
        raw = fetch_bytes(case.get("cover_url") or case["thumbnail_url"])
        image = Image.open(io.BytesIO(raw)).convert("RGB")
        width, height = image.size
        working = image.copy()
        working.thumbnail((320, 320))
        arr = np.asarray(working, dtype=np.uint8)
        flat = arr.reshape(-1, 3)
        luminance = (0.2126 * flat[:, 0] + 0.7152 * flat[:, 1] + 0.0722 * flat[:, 2]) / 255.0
        maxc = flat.max(axis=1).astype(float)
        minc = flat.min(axis=1).astype(float)
        saturation = np.divide(maxc - minc, np.maximum(maxc, 1), out=np.zeros_like(maxc), where=maxc > 0)
        whitespace = float(np.mean((luminance > 0.94) & (saturation < 0.09)))

        quantized = working.quantize(colors=10, method=Image.Quantize.MEDIANCUT).convert("RGB")
        colors = quantized.getcolors(maxcolors=working.width * working.height) or []
        colors.sort(reverse=True)
        total = max(sum(count for count, _ in colors), 1)
        palette = []
        for count, rgb in colors:
            r, g, b = rgb
            _, sat, value = colorsys.rgb_to_hsv(r / 255, g / 255, b / 255)
            role = "accent"
            if value > 0.92 and sat < 0.10:
                role = "background"
            elif value < 0.20:
                role = "ink"
            elif sat < 0.15:
                role = "neutral"
            palette.append({"hex": hex_color(rgb), "rgb": list(rgb), "share": round(count / total, 4), "role": role})

        gray = working.convert("L")
        edge_arr = np.asarray(gray.filter(ImageFilter.FIND_EDGES), dtype=np.uint8)
        edge_density = float(np.mean(edge_arr > 32))
        mean_sat = float(np.mean(saturation))
        mean_lum = float(np.mean(luminance))
        non_bg = ~((luminance > 0.94) & (saturation < 0.09))
        non_bg_img = non_bg.reshape(arr.shape[:2])
        midpoint = non_bg_img.shape[1] // 2
        left = float(non_bg_img[:, :midpoint].mean()) if midpoint else 0.0
        right = float(non_bg_img[:, midpoint:].mean()) if midpoint else 0.0
        visual_weight = "balanced" if abs(left - right) < 0.06 else ("left" if left > right else "right")
        tone = "muted" if mean_sat < 0.18 else ("vivid" if mean_sat > 0.38 else "balanced")
        density_score = (1 - whitespace) * 0.65 + min(edge_density / 0.35, 1) * 0.35
        density = "sparse" if density_score < 0.38 else ("dense" if density_score > 0.68 else "balanced")
        hue_vector = [0.0, 0.0]
        for item in [item for item in palette if item["role"] == "accent"][:6]:
            r, g, b = [value / 255 for value in item["rgb"]]
            hue, sat, _ = colorsys.rgb_to_hsv(r, g, b)
            weight = item["share"] * sat
            hue_vector[0] += math.cos(2 * math.pi * hue) * weight
            hue_vector[1] += math.sin(2 * math.pi * hue) * weight
        hue = (math.atan2(hue_vector[1], hue_vector[0]) / (2 * math.pi)) % 1 if any(hue_vector) else 0
        temperature = "warm" if hue < 0.16 or hue > 0.90 else ("cool" if 0.42 < hue < 0.76 else "mixed")

        result.update(
            {
                "status": "ok",
                "image_size": [width, height],
                "aspect_ratio": round(width / max(height, 1), 4),
                "palette": palette[:8],
                "mean_saturation": round(mean_sat, 4),
                "mean_luminance": round(mean_lum, 4),
                "whitespace_ratio": round(whitespace, 4),
                "edge_density": round(edge_density, 4),
                "tone": tone,
                "temperature": temperature,
                "density": density,
                "visual_weight": visual_weight,
            }
        )
    except Exception as exc:
        result.update({"status": "error", "error": f"{type(exc).__name__}: {exc}"})
    return result


def atomic_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", delete=False, dir=path.parent, suffix=".tmp") as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=2)
        tmp = Path(handle.name)
    tmp.replace(path)


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, default=root / "assets" / "generated" / "pubcns-cases.json")
    parser.add_argument("--output", type=Path, default=root / "assets" / "generated" / "pubcns-style-index.json")
    parser.add_argument("--previous", type=Path)
    parser.add_argument("--workers", type=int, default=6)
    args = parser.parse_args()
    case_payload = json.loads(args.input.read_text(encoding="utf-8"))
    cases = case_payload["items"]
    previous_by_id = {}
    if args.previous and args.previous.exists():
        previous = json.loads(args.previous.read_text(encoding="utf-8"))
        previous_by_id = {item["stable_id"]: item for item in previous.get("items", [])}
    results = []
    pending = []
    for case in cases:
        old = previous_by_id.get(case["stable_id"])
        if old and old.get("visual_hash") == case.get("visual_hash") and old.get("extractor_version") == EXTRACTOR_VERSION:
            reused = dict(old)
            for key in ("content_hash", "visual_hash", "sequence", "title", "journal", "article_url"):
                reused[key] = case.get(key)
            results.append(reused)
        else:
            pending.append(case)
    print(f"reused={len(results)} pending={len(pending)}", flush=True)
    with ThreadPoolExecutor(max_workers=max(1, args.workers)) as pool:
        futures = {pool.submit(analyze, case): case for case in pending}
        for index, future in enumerate(as_completed(futures), 1):
            results.append(future.result())
            if index % 10 == 0 or index == len(pending):
                print(f"analyzed={index}/{len(pending)}", flush=True)
    results.sort(key=lambda row: (row.get("sequence") is None, row.get("sequence") or 10**9))
    payload = {
        "schema_version": 1,
        "extractor_version": EXTRACTOR_VERSION,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source_case_count": len(cases),
        "items": results,
    }
    atomic_json(args.output, payload)
    failures = sum(row.get("status") != "ok" for row in results)
    print(f"output={args.output.resolve()} failures={failures}")
    return 0 if results and failures < len(results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
