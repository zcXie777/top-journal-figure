#!/usr/bin/env python3
"""Collect public WeChat album metadata without redistributing source artwork."""

from __future__ import annotations

import argparse
import hashlib
import html
import json
import re
import sys
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import parse_qs, urlencode, urlparse, urlunparse
from urllib.request import Request, urlopen


DEFAULT_URL = (
    "https://mp.weixin.qq.com/mp/appmsgalbum?"
    "__biz=MzU0ODY3Njg5NA%3D%3D&action=getalbum&album_id=4505958088352628740"
)
SCHEMA_VERSION = 1

JOURNAL_ALIASES = {
    "nat commun": "Nature Communications",
    "nat communications": "Nature Communications",
    "nature commu": "Nature Communications",
    "nature communi": "Nature Communications",
    "nature communications": "Nature Communications",
    "nat nanotechnology": "Nature Nanotechnology",
    "nat. biomed. eng": "Nature Biomedical Engineering",
    "nature metabolism": "Nature Metabolism",
    "nature aging": "Nature Aging",
    "nature cancer": "Nature Cancer",
    "cell reports med": "Cell Reports Medicine",
    "drug resist updat": "Drug Resistance Updates",
    "sttt": "Signal Transduction and Targeted Therapy",
}


def fetch(url: str, timeout: int = 30) -> str:
    request = Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/126 Safari/537.36",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.6",
            "Referer": "https://mp.weixin.qq.com/",
        },
    )
    with urlopen(request, timeout=timeout) as response:
        return response.read().decode("utf-8", errors="replace")


def js_value(text: str, name: str) -> str:
    match = re.search(rf"{re.escape(name)}:\s*'([^']*)'", text)
    return html.unescape(match.group(1)) if match else ""


def int_value(text: str, name: str) -> int:
    match = re.search(rf"{re.escape(name)}:\s*'?(\d+)'?", text)
    return int(match.group(1)) if match else 0


def canonical_journal(value: str) -> str:
    cleaned = " ".join(value.split())
    return JOURNAL_ALIASES.get(cleaned.lower(), cleaned)


def parse_articles(page: str) -> list[dict]:
    marker = page.find("articleList:")
    if marker < 0:
        return []
    end = page.find("continue_flag:", marker)
    section = page[marker : end if end >= 0 else None]
    pattern = re.compile(
        r"title:\s*'(?P<title>[^']*)'"
        r"[\s\S]*?create_time:\s*'(?P<created>[^']*)'"
        r"[\s\S]*?cover_img_1_1:\s*'(?P<thumb>[^']*)'"
        r"[\s\S]*?cover_img_first:\s*'(?P<cover>[^']*)'"
        r"[\s\S]*?url:\s*'(?P<url>[^']*)'\.html\(false\)"
        r"[\s\S]*?msgid:\s*'(?P<msgid>[^']*)'"
        r"[\s\S]*?itemidx:\s*'(?P<itemidx>[^']*)'",
        re.MULTILINE,
    )
    rows: list[dict] = []
    for match in pattern.finditer(section):
        title = html.unescape(match.group("title"))
        seq_match = re.search(r"(?:配色|色)\s*(\d+)", title)
        journal_match = re.search(r"\|\s*(.+?)\s*$", title)
        timestamp = int(match.group("created") or 0)
        article_url = html.unescape(match.group("url")).replace("http://", "https://", 1)
        row = {
            "sequence": int(seq_match.group(1)) if seq_match else None,
            "title": title,
            "journal": canonical_journal(journal_match.group(1)) if journal_match else "",
            "published_at": datetime.fromtimestamp(timestamp, timezone.utc).isoformat() if timestamp else None,
            "article_url": article_url,
            "cover_url": html.unescape(match.group("cover")).replace("http://", "https://", 1),
            "thumbnail_url": html.unescape(match.group("thumb")).replace("http://", "https://", 1),
            "msgid": match.group("msgid"),
            "itemidx": match.group("itemidx"),
        }
        row["stable_id"] = f"wechat:{row['msgid']}:{row['itemidx']}"
        row["visual_hash"] = hashlib.sha256(
            json.dumps(
                {"cover_url": row["cover_url"], "thumbnail_url": row["thumbnail_url"]},
                ensure_ascii=False,
                sort_keys=True,
            ).encode("utf-8")
        ).hexdigest()
        digest_fields = {key: row[key] for key in sorted(row) if key not in {"content_hash"}}
        row["content_hash"] = hashlib.sha256(
            json.dumps(digest_fields, ensure_ascii=False, sort_keys=True).encode("utf-8")
        ).hexdigest()
        rows.append(row)
    return rows


def page_url(base_url: str, last: dict | None) -> str:
    parsed = urlparse(base_url)
    query = parse_qs(parsed.query)
    query["action"] = ["getalbum"]
    query["count"] = ["10"]
    query["is_reverse"] = ["0"]
    query.pop("mid", None)
    query.pop("idx", None)
    if last:
        query["begin_msgid"] = [last["msgid"]]
        query["begin_itemidx"] = [last["itemidx"]]
    else:
        query.pop("begin_msgid", None)
        query.pop("begin_itemidx", None)
    flat = [(key, value) for key, values in query.items() for value in values]
    return urlunparse(parsed._replace(query=urlencode(flat)))


def atomic_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", delete=False, dir=path.parent, suffix=".tmp") as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=2)
        tmp_path = Path(handle.name)
    tmp_path.replace(path)


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", default=DEFAULT_URL)
    parser.add_argument("--source-id", default="pubcns-wechat-colors")
    parser.add_argument("--output", type=Path, default=root / "assets" / "generated" / "pubcns-cases.json")
    parser.add_argument("--delay", type=float, default=0.15)
    parser.add_argument("--minimum", type=int, default=122)
    args = parser.parse_args()

    all_rows: list[dict] = []
    seen: set[str] = set()
    last: dict | None = None
    source_account = "PubCNS"
    album_title = "科研配色"
    declared_count = 0
    for page_number in range(1, 100):
        page = fetch(page_url(args.url, last))
        source_account = js_value(page, "nick_name") or source_account
        album_title = js_value(page, "title") or album_title
        declared_count = int_value(page, "article_count") or declared_count
        rows = parse_articles(page)
        new_rows = []
        for row in rows:
            if row["stable_id"] not in seen:
                seen.add(row["stable_id"])
                new_rows.append(row)
        all_rows.extend(new_rows)
        print(f"page={page_number} new={len(new_rows)} total={len(all_rows)}", flush=True)
        if declared_count and len(all_rows) >= declared_count:
            break
        if not new_rows or int_value(page, "continue_flag") == 0:
            break
        last = rows[-1]
        time.sleep(max(args.delay, 0))

    all_rows.sort(key=lambda row: (row["sequence"] is None, row["sequence"] or 10**9, row["title"]))
    retrieved = datetime.now(timezone.utc).isoformat()
    for row in all_rows:
        row.update(
            {
                "source_album": album_title,
                "source_account": source_account,
                "source_id": args.source_id,
                "retrieved_at": retrieved,
                "provenance": "public WeChat album metadata; artwork not redistributed",
            }
        )
    payload = {
        "schema_version": SCHEMA_VERSION,
        "source_id": args.source_id,
        "source_url": args.url,
        "generated_at": retrieved,
        "declared_count": declared_count,
        "items": all_rows,
    }
    valid = bool(all_rows) and len(all_rows) >= args.minimum and (not declared_count or len(all_rows) == declared_count)
    if not valid:
        print(
            f"error: collected={len(all_rows)} minimum={args.minimum} declared={declared_count}",
            file=sys.stderr,
        )
        return 2
    atomic_json(args.output, payload)
    print(str(args.output.resolve()))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
