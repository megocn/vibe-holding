#!/usr/bin/env python3
"""条目外链可达性抽检。

扩种后用来揪出编造的 URL：并发访问 `officialUrl` / `sources` / 一等外链，
报告 4xx / DNS 失败 / 连接错误。403 与 405 单列——不少站点拦爬虫但页面真实存在。

用法:
  python3 scripts/check-entry-links.py                    # 全量
  python3 scripts/check-entry-links.py --since 2026-08-05 # 只查该日复核的条目
  python3 scripts/check-entry-links.py --ids a,b,c
  python3 scripts/check-entry-links.py --fields officialUrl
"""
from __future__ import annotations

import argparse
import json
import ssl
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ENTRIES = ROOT / "content" / "entries"

UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0 Safari/537.36"
LINK_FIELDS = (
    "officialUrl",
    "docsUrl",
    "githubUrl",
    "pricingUrl",
    "statusUrl",
    "consoleUrl",
    "playgroundUrl",
    "changelogUrl",
    "loginUrl",
)
CTX = ssl.create_default_context()
CTX.check_hostname = False
CTX.verify_mode = ssl.CERT_NONE


def probe(url: str, timeout: float = 15.0) -> tuple[str, int | str]:
    req = urllib.request.Request(url, headers={"User-Agent": UA}, method="GET")
    try:
        with urllib.request.urlopen(req, timeout=timeout, context=CTX) as resp:
            return url, resp.status
    except urllib.error.HTTPError as e:
        return url, e.code
    except Exception as e:  # DNS / TLS / timeout / 连接重置
        return url, type(e).__name__


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--since", help="只查 lastReviewed >= 该日期的条目")
    ap.add_argument("--ids", help="逗号分隔的条目 id")
    ap.add_argument("--fields", default="officialUrl", help="逗号分隔；all 表示全部外链字段")
    ap.add_argument("--workers", type=int, default=16)
    args = ap.parse_args()

    fields = LINK_FIELDS if args.fields == "all" else tuple(args.fields.split(","))
    want_ids = set(args.ids.split(",")) if args.ids else None

    targets: dict[str, list[tuple[str, str]]] = {}  # url -> [(entryId, field)]
    for f in sorted(ENTRIES.glob("*.json")):
        d = json.loads(f.read_text(encoding="utf-8"))
        if want_ids and d["id"] not in want_ids:
            continue
        if args.since and d.get("lastReviewed", "") < args.since:
            continue
        urls: list[tuple[str, str]] = []
        for field in fields:
            if d.get(field):
                urls.append((field, d[field]))
        for i, src in enumerate(d.get("sources") or []):
            if "sources" in fields or args.fields == "all":
                urls.append((f"sources[{i}]", src))
        for field, url in urls:
            targets.setdefault(url, []).append((d["id"], field))

    if not targets:
        print("没有匹配的条目/链接")
        return

    print(f"抽检 {len(targets)} 个链接…")
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        results = dict(pool.map(probe, targets.keys()))

    ok, soft, bad = [], [], []
    for url, status in results.items():
        owners = ", ".join(f"{eid}.{field}" for eid, field in targets[url])
        row = (status, url, owners)
        if isinstance(status, int) and 200 <= status < 400:
            ok.append(row)
        elif status in (403, 405, 406, 429, 503):
            soft.append(row)
        else:
            bad.append(row)

    if soft:
        print(f"\n可疑但多为反爬 ({len(soft)}):")
        for status, url, owners in sorted(soft, key=lambda r: str(r[0])):
            print(f"  [{status}] {url}  <- {owners}")
    if bad:
        print(f"\n需人工核对 ({len(bad)}):")
        for status, url, owners in sorted(bad, key=lambda r: str(r[0])):
            print(f"  [{status}] {url}  <- {owners}")

    print(f"\n通过 {len(ok)} · 反爬类 {len(soft)} · 需核对 {len(bad)}")


if __name__ == "__main__":
    main()
