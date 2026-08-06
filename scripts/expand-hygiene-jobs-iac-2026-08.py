#!/usr/bin/env python3
"""误挂归位 + cloud-jobs 短名单补种（2026-08-07）。

迁移:
- upstash-qstash: db-nosql → cloud-jobs
- packer / ansible: cicd-pipeline → cicd-iac

新种（应用后台任务仍缺的经典轴）:
- celery（Python 事实队列）
- cloudflare-queues（边缘/Workers 队列）

用法:
  python3 scripts/expand-hygiene-jobs-iac-2026-08.py
  python3 scripts/expand-hygiene-jobs-iac-2026-08.py --overwrite
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ENTRIES = ROOT / "content" / "entries"
VENDORS = ROOT / "content" / "vendors"
EDGES = ROOT / "content" / "edges"
REVIEWED = "2026-08-07"

MIGRATE = {
    "upstash-qstash": ("cloud-jobs", "http-jobs"),
    "packer": ("cicd-iac", "images"),
    "ansible": ("cicd-iac", "config"),
}


def save(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def entry(**kw) -> dict:
    e = {
        "pricing": {"model": "open-source"},
        "availability": {
            "chinaAccessible": True,
            "needsCompany": False,
            "needsIcp": False,
            "regions": ["global"],
        },
        "tags": [],
        "maturity": "stable",
        "pitfalls": [],
        "updates": [],
        "rankings": [],
        "sources": [],
        "lastReviewed": REVIEWED,
        "region": "overseas",
    }
    e.update(kw)
    if "officialUrl" in e and not e["sources"]:
        e["sources"] = [e["officialUrl"]]
    if e.get("vendorId") is None:
        e.pop("vendorId", None)
    return e


def validate_entry(e: dict) -> None:
    assert 20 <= len(e["oneLiner"]) <= 58, (e["id"], len(e["oneLiner"]))
    assert 160 <= len(e["descriptionMd"]) <= 360, (e["id"], len(e["descriptionMd"]))
    assert 1 <= len(e["pitfalls"]) <= 3, e["id"]
    assert 3 <= len(e["tags"]) <= 5, e["id"]
    assert e.get("subcategory"), e["id"]


def desc(what: str, when: str, caution: str) -> str:
    pad = "选型前请以官网文档与当前限制为准。"
    body = f"{what}\n\n{when}\n\n{caution}\n"
    while len(body) < 160:
        caution = caution.rstrip("。") + "。" + pad
        body = f"{what}\n\n{when}\n\n{caution}\n"
        if len(body) > 360:
            break
    if not (160 <= len(body) <= 360):
        raise ValueError(f"desc {len(body)}")
    return body


def mk(cat, eid, name, sub, one, url, what, when, caution, **extra):
    pitfalls = extra.pop("pitfalls", None)
    return entry(
        id=eid,
        name=name,
        category=cat,
        subcategory=sub,
        oneLiner=one,
        officialUrl=url,
        descriptionMd=desc(what, when, caution),
        pitfalls=pitfalls or [caution[:90]],
        **extra,
    )


def edge(eid, frm, to, typ, weight=0.7, note=None):
    e = {
        "id": eid,
        "from": frm,
        "to": to,
        "type": typ,
        "weight": weight,
        "confidence": "community",
        "sources": [],
        "createdAt": REVIEWED,
    }
    if note:
        e["note"] = note
    return e


ENTRIES_DATA = [
    mk(
        "cloud-jobs",
        "celery",
        "Celery",
        "queue-worker",
        "Python 异步任务事实标准 · 多 broker · Django/Flask 默配",
        "https://docs.celeryq.dev",
        "Celery 是 Python 生态的分布式任务队列：异步任务、定时 beat、重试与多 broker（Redis/RabbitMQ 等），Django 项目长期默认选项。",
        "Python/Django 服务要发邮件、报表、AI 批处理等后台任务，且团队熟悉 worker 进程模型时选它。",
        "运维 worker 与 broker 是成本中心；Serverless 无常驻场景更看 Inngest/QStash；严格 durable 长事务看 Temporal。",
        tags=["jobs", "python", "queue", "open-source"],
        pricing={"model": "open-source"},
        githubUrl="https://github.com/celery/celery",
        vendorId="celery-project",
    ),
    mk(
        "cloud-jobs",
        "cloudflare-queues",
        "Cloudflare Queues",
        "queue-worker",
        "Workers 原生队列 · 批处理消费 · 边缘异步解耦",
        "https://developers.cloudflare.com/queues/",
        "Cloudflare Queues 为 Workers 提供托管消息队列：生产者投递、消费者批处理、重试与延迟，把边缘计算与异步解耦。",
        "业务已在 Cloudflare Workers/Pages，需要可靠异步 fan-out 或削峰，而不想另开 Redis 队列时用。",
        "绑定 Cloudflare 生态；复杂路由与多云消费弱于 Kafka；与 QStash 同轴比「HTTP 回调」心智不同。",
        tags=["jobs", "queue", "cloudflare", "serverless"],
        pricing={"model": "usage"},
        vendorId="cloudflare-inc",
    ),
]

VENDORS_DATA = [
    {
        "id": "celery-project",
        "name": "Celery Project",
        "region": "overseas",
        "url": "https://docs.celeryq.dev",
    },
]

EDGES_DATA = [
    edge(
        "e-qstash-alt-inngest",
        "upstash-qstash",
        "inngest",
        "alternative_to",
        note="HTTP 投递队列 vs 代码内 durable step",
        weight=0.7,
    ),
    edge(
        "e-qstash-alt-cloudflare-queues",
        "upstash-qstash",
        "cloudflare-queues",
        "alternative_to",
        note="多运行时 HTTP 回调 vs CF Workers 原生队列",
        weight=0.65,
    ),
    edge(
        "e-celery-alt-bullmq",
        "celery",
        "bullmq",
        "alternative_to",
        note="Python worker 队列 vs Node/Redis BullMQ",
        weight=0.75,
    ),
    edge(
        "e-celery-with-redis",
        "celery",
        "redis",
        "commonly_used_with",
        note="broker/backend 常见 Redis",
        weight=0.8,
    ),
    edge(
        "e-celery-with-rabbitmq",
        "celery",
        "rabbitmq",
        "commonly_used_with",
        note="传统企业 broker 常见 RabbitMQ",
        weight=0.7,
    ),
    edge(
        "e-cloudflare-queues-with-workers",
        "cloudflare-queues",
        "cloudflare-workers",
        "commonly_used_with",
        note="生产者/消费者挂在 Workers",
        weight=0.9,
    ),
    edge(
        "e-packer-with-terraform",
        "packer",
        "terraform",
        "commonly_used_with",
        note="镜像构建后由 Terraform 起算力",
        weight=0.75,
    ),
]


def migrate() -> None:
    for eid, (cat, sub) in MIGRATE.items():
        path = ENTRIES / f"{eid}.json"
        if not path.exists():
            print("warn missing", eid)
            continue
        data = json.loads(path.read_text(encoding="utf-8"))
        old = data.get("category")
        data["category"] = cat
        data["subcategory"] = sub
        data["lastReviewed"] = REVIEWED
        tags = list(data.get("tags") or [])
        if eid == "upstash-qstash":
            for t in ("jobs", "queue", "serverless", "http"):
                if t not in tags:
                    tags.append(t)
        if eid == "packer":
            for t in ("iac", "images", "hashicorp", "devops"):
                if t not in tags:
                    tags.append(t)
        if eid == "ansible":
            for t in ("iac", "config", "automation", "devops"):
                if t not in tags:
                    tags.append(t)
        data["tags"] = tags[:5]
        dm = data.get("descriptionMd") or ""
        if len(dm) < 160:
            data["descriptionMd"] = dm.rstrip() + "\n\n选型前请以官网文档与当前限制为准。\n"
        save(path, data)
        print(f"migrated {eid} {old} → {cat}")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--overwrite", action="store_true")
    args = ap.parse_args()

    for e in ENTRIES_DATA:
        validate_entry(e)

    known = {e["id"] for e in ENTRIES_DATA} | set(MIGRATE)
    we = wv = wg = 0
    se = sv = sg = 0

    for e in ENTRIES_DATA:
        path = ENTRIES / f"{e['id']}.json"
        if path.exists() and not args.overwrite:
            se += 1
            continue
        save(path, e)
        we += 1
        print("entry", e["id"])

    for v in VENDORS_DATA:
        path = VENDORS / f"{v['id']}.json"
        if path.exists() and not args.overwrite:
            sv += 1
            continue
        save(path, v)
        wv += 1
        print("vendor", v["id"])

    for g in EDGES_DATA:
        path = EDGES / f"{g['id']}.json"
        if path.exists() and not args.overwrite:
            sg += 1
            continue
        for end in (g["from"], g["to"]):
            if not ((ENTRIES / f"{end}.json").exists() or end in known):
                print("skip edge", g["id"], end)
                break
        else:
            save(path, g)
            wg += 1
            print("edge", g["id"])

    migrate()
    print(f"done entries={we} skip={se} vendors={wv} skipv={sv} edges={wg} skipg={sg}")


if __name__ == "__main__":
    main()
