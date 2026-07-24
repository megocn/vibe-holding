#!/usr/bin/env python3
"""把 oneLiner 写成「选型特点」句（同层差异化维度），不是简介/适用场景。

以 scripts/oneliners-traits-2026-07.json 为唯一真相源（逐条手写）。
幂等：字典有则写回；缺 id 则跳过并告警。
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ENTRIES = ROOT / "content" / "entries"
TRAITS = ROOT / "scripts" / "oneliners-traits-2026-07.json"
MAX_LEN = 80


def main() -> None:
    traits: dict[str, str] = json.loads(TRAITS.read_text(encoding="utf-8"))
    updated = 0
    missing: list[str] = []
    too_long: list[str] = []
    for path in sorted(ENTRIES.glob("*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        eid = data["id"]
        if eid not in traits:
            missing.append(eid)
            continue
        new = traits[eid].strip()
        if len(new) > MAX_LEN:
            too_long.append(f"{eid}:{len(new)}")
            new = new[:MAX_LEN].rstrip("，；、 ·") + "…"
        if data.get("oneLiner") == new:
            continue
        data["oneLiner"] = new
        path.write_text(
            json.dumps(data, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        updated += 1

    print(f"updated {updated} · traits {len(traits)}")
    if missing:
        print(f"WARN missing traits for {len(missing)}:", ", ".join(missing[:20]))
    if too_long:
        print(f"WARN truncated {len(too_long)}:", ", ".join(too_long[:10]))
    if missing:
        sys.exit(1)


if __name__ == "__main__":
    main()
