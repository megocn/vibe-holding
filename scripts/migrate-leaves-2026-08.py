#!/usr/bin/env python3
"""存量条目归位到 2026-08 新增叶类。

只改 `category`（必要时补 `subcategory`），不动文案、来源与 lastReviewed——
分类结构调整不等于内容复核。

用法:
  python3 scripts/migrate-leaves-2026-08.py --dry-run
  python3 scripts/migrate-leaves-2026-08.py
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ENTRIES = ROOT / "content" / "entries"

# 新叶 -> 迁入条目
MOVES: dict[str, list[str]] = {
    "fw-cross-platform": [
        "react-native",
        "expo",
        "flutter",
        "tauri",
        "electron",
        "capacitor",
    ],
    "fw-backend": [
        "express",
        "fastify",
        "nestjs",
        "hono",
        "django",
        "fastapi",
        "laravel",
        "rails",
        "spring-boot",
        "gin",
        "axum",
        "actix-web",
        "adonisjs",
        "phoenix",
    ],
    # 纯 UI 框架核心不应与元框架同榜
    "fw-ui-lib": ["angular", "svelte"],
    "oss-testing": ["jest", "vitest", "playwright", "cypress", "testing-library", "msw"],
    "oss-state": ["tanstack-query"],
    "db-search": ["elasticsearch", "meilisearch", "typesense", "vespa"],
    "db-timeseries": ["timescaledb"],
    "cloud-self-host": ["coolify", "caprover"],
    "obs-logs": ["loki", "axiom"],
    "obs-uptime": ["betterstack"],
    "ai-eval": ["braintrust"],
    "ai-memory": ["mem0", "letta"],
    "ai-search-api": ["firecrawl"],
    "ai-gpu-cloud": ["modal"],
    "collab-cms": ["strapi", "directus"],
    "sec-appsec": ["snyk", "trivy", "sonarqube", "checkov"],
    "growth-seo": ["ahrefs", "semrush", "google-search-console"],
}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    moved = skipped = missing = 0
    for leaf, ids in MOVES.items():
        for eid in ids:
            path = ENTRIES / f"{eid}.json"
            if not path.exists():
                print(f"missing  {eid}")
                missing += 1
                continue
            data = json.loads(path.read_text(encoding="utf-8"))
            if data.get("category") == leaf:
                skipped += 1
                continue
            print(f"move     {eid:24s} {data['category']:18s} -> {leaf}")
            data["category"] = leaf
            if not args.dry_run:
                path.write_text(
                    json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
                )
            moved += 1

    print(f"\ndone moved={moved} skipped={skipped} missing={missing} dry_run={args.dry_run}")


if __name__ == "__main__":
    main()
