#!/usr/bin/env python3
"""优质扩种主脚本：合并 Wave1–3，幂等写入 entries / vendors / edges。

用法:
  python3 scripts/expand-rich-2026-07.py
  python3 scripts/expand-rich-2026-07.py --wave 1
  python3 scripts/expand-rich-2026-07.py --prune-only
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from expand_rich import wave1_afj, wave2_gilkv, wave3_mu  # noqa: E402

CONTENT = ROOT / "content"
ENTRIES = CONTENT / "entries"
EDGES = CONTENT / "edges" / "seed.json"
VENDORS = CONTENT / "vendors" / "seed.json"
REVIEWED = "2026-07-23"
VALID_PRICING = {"free", "freemium", "subscription", "usage", "open-source"}

WAVES = {
    1: wave1_afj,
    2: wave2_gilkv,
    3: wave3_mu,
}

SYM_EDGE_TYPES = {
    "alternative_to",
    "open_source_alternative_to",
    "commonly_used_with",
    "compatible_with",
    "conflicts_with",
    "related_concept",
}


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def save_json(path: Path, data) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def normalize_entry(e: dict) -> dict:
    e = dict(e)
    pricing = dict(e.get("pricing") or {"model": "freemium"})
    if pricing.get("model") not in VALID_PRICING:
        pricing["notes"] = (pricing.get("notes") or "") + f"（原 model={pricing.get('model')}）"
        pricing["model"] = "freemium"
    e["pricing"] = pricing
    return e


def write_entry(e: dict, overwrite: bool = False) -> bool:
    path = ENTRIES / f"{e['id']}.json"
    if path.exists() and not overwrite:
        return False
    save_json(path, normalize_entry(e))
    return True


def merge_by_id(existing: list, new_items: list) -> int:
    ids = {x["id"] for x in existing}
    added = 0
    for item in new_items:
        if item["id"] not in ids:
            existing.append(item)
            ids.add(item["id"])
            added += 1
    return added


def rename_colliding_vendors(
    vendors: list[dict], entry_ids: set[str]
) -> dict[str, str]:
    """返回 old→new；就地改 vendors[].id。"""
    used = {v["id"] for v in vendors} | entry_ids
    id_map: dict[str, str] = {}
    for v in vendors:
        old = v["id"]
        if old not in entry_ids:
            continue
        new = f"{old}-inc"
        while new in used:
            new = f"{new}-v"
        id_map[old] = new
        used.add(new)
        v["id"] = new
    return id_map


def apply_vendor_map_to_entries(entries: list[dict], id_map: dict[str, str]) -> None:
    for e in entries:
        vid = e.get("vendorId")
        if vid in id_map:
            e["vendorId"] = id_map[vid]


def dedupe_sym_edges(edges: list[dict]) -> list[dict]:
    seen: set[tuple] = set()
    out: list[dict] = []
    for ed in edges:
        typ = ed["type"]
        if typ in SYM_EDGE_TYPES:
            key = (typ, tuple(sorted([ed["from"], ed["to"]])))
            if key in seen:
                continue
            seen.add(key)
        out.append(ed)
    return out


def prune_stale() -> None:
    path = ENTRIES / "lemonsqueezy.json"
    if not path.exists():
        print("prune skip: lemonsqueezy missing")
        return
    e = load_json(path)
    tags = list(e.get("tags") or [])
    changed = False
    for t in ("not-for-greenfield", "legacy-caution"):
        if t not in tags:
            tags.append(t)
            changed = True
    pitfalls = list(e.get("pitfalls") or [])
    note = "新绿场项目勿默认选 LS；优先 Paddle / Polar / Creem"
    if note not in pitfalls:
        pitfalls.append(note)
        changed = True
    if changed:
        e["tags"] = tags
        e["pitfalls"] = pitfalls
        e["lastReviewed"] = REVIEWED
        save_json(path, e)
        print("prune: lemonsqueezy tagged not-for-greenfield")
    else:
        print("prune: lemonsqueezy already annotated")


def run_waves(wave_ids: list[int]) -> None:
    vendors = load_json(VENDORS)
    edges = load_json(EDGES)
    entry_added = vendor_added = edge_added = 0

    for wid in wave_ids:
        mod = WAVES[wid]
        print(f"=== Wave {wid} ({mod.__name__}) ===")
        entry_ids = {p.stem for p in ENTRIES.glob("*.json")} | {
            e["id"] for e in mod.ENTRIES
        }
        batch_entries = [normalize_entry(dict(e)) for e in mod.ENTRIES]
        batch_vendors = [dict(v) for v in mod.VENDORS]
        id_map = rename_colliding_vendors(batch_vendors, entry_ids)
        apply_vendor_map_to_entries(batch_entries, id_map)

        for e in batch_entries:
            if write_entry(e):
                entry_added += 1
        vendor_added += merge_by_id(vendors, batch_vendors)
        before_edges = len(edges)
        edge_added += merge_by_id(edges, mod.EDGES)
        print(f"  edges merge +{len(edges) - before_edges}")

    # 全库 vendor↔entry 再消解一次（防漏网）
    entry_ids = {p.stem for p in ENTRIES.glob("*.json")}
    id_map = rename_colliding_vendors(vendors, entry_ids)
    if id_map:
        for p in ENTRIES.glob("*.json"):
            e = load_json(p)
            if e.get("vendorId") in id_map:
                e["vendorId"] = id_map[e["vendorId"]]
                save_json(p, e)
        print(f"renamed colliding vendors: {len(id_map)}")

    edges = dedupe_sym_edges(edges)
    save_json(VENDORS, vendors)
    save_json(EDGES, edges)
    total = len(list(ENTRIES.glob("*.json")))
    print(
        f"done: +entries={entry_added} +vendors={vendor_added} +edges={edge_added} "
        f"total_entries={total} edges_kept={len(edges)}"
    )


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--wave", type=int, choices=[1, 2, 3], action="append")
    ap.add_argument("--prune-only", action="store_true")
    args = ap.parse_args()

    if args.prune_only:
        prune_stale()
        return

    prune_stale()
    run_waves(args.wave or [1, 2, 3])


if __name__ == "__main__":
    main()
