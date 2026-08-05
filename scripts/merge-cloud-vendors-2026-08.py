#!/usr/bin/env python3
"""合并冗余的「云事业部」厂商节点，为云平台本体条目腾出 id。

问题：厂商层同时存在「腾讯」与「腾讯云」「阿里巴巴」与「阿里云」这类父子重复节点，
而 entry / vendor 共用同一 id 空间，导致「腾讯云」这个**可选型的云平台**无法建条目。

处理：把云事业部厂商并入母公司厂商（改 entry.vendorId 后删除冗余 vendor），
DigitalOcean 公司与产品同名，改用仓库既有的 `-inc` 后缀区分。

用法:
  python3 scripts/merge-cloud-vendors-2026-08.py --dry-run
  python3 scripts/merge-cloud-vendors-2026-08.py
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ENTRIES = ROOT / "content" / "entries"
VENDORS = ROOT / "content" / "vendors"

# 旧 vendorId -> 新 vendorId
MERGE = {
    "google-cloud": "google",
    "aliyun": "alibaba",
    "tencent-cloud": "tencent",
    "huawei-cloud": "huawei",
    "volcengine": "bytedance",
    "digitalocean": "digitalocean-inc",
}
# 需要新建（而非并入已有）的目标厂商
CREATE = {
    "digitalocean-inc": {
        "id": "digitalocean-inc",
        "name": "DigitalOcean",
        "region": "overseas",
        "url": "https://www.digitalocean.com",
    },
}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    for vid, data in CREATE.items():
        path = VENDORS / f"{vid}.json"
        if path.exists():
            continue
        print(f"create vendor {vid}")
        if not args.dry_run:
            path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    rewired = 0
    for f in sorted(ENTRIES.glob("*.json")):
        d = json.loads(f.read_text(encoding="utf-8"))
        old = d.get("vendorId")
        if old in MERGE:
            d["vendorId"] = MERGE[old]
            print(f"rewire  {d['id']:26s} {old} -> {d['vendorId']}")
            rewired += 1
            if not args.dry_run:
                f.write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    removed = 0
    for old, new in MERGE.items():
        path = VENDORS / f"{old}.json"
        if not path.exists():
            continue
        if not (VENDORS / f"{new}.json").exists():
            print(f"!! 目标厂商 {new} 不存在，保留 {old}")
            continue
        print(f"remove vendor {old} (merged into {new})")
        removed += 1
        if not args.dry_run:
            path.unlink()

    print(f"\ndone rewired={rewired} removed={removed} dry_run={args.dry_run}")


if __name__ == "__main__":
    main()
