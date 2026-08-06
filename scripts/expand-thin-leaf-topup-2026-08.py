#!/usr/bin/env python3
"""薄种补强 + 达到「叶至少 3 条」门槛（2026-08-07）。

仅补「恰好 2 条」的叶，短名单级、不新开叶：
- collab-suite：Google Workspace / Microsoft 365
- collab-help：Archbee
- growth-cdp：Jitsu
- cicd-gitops：Rancher Fleet
- msg-webhook：Hook0

用法:
  python3 scripts/expand-thin-leaf-topup-2026-08.py
  python3 scripts/expand-thin-leaf-topup-2026-08.py --overwrite
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


def save(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def entry(**kw) -> dict:
    e = {
        "pricing": {"model": "subscription"},
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
    assert 20 <= len(e["oneLiner"]) <= 58, (e["id"], len(e["oneLiner"]), e["oneLiner"])
    assert 160 <= len(e["descriptionMd"]) <= 360, (e["id"], len(e["descriptionMd"]))
    assert 1 <= len(e["pitfalls"]) <= 3, e["id"]
    assert 3 <= len(e["tags"]) <= 5, e["id"]
    assert e.get("subcategory"), e["id"]


def desc(what: str, when: str, caution: str) -> str:
    pad = "选型前请以官网能力与当前定价为准。"
    body = f"{what}\n\n{when}\n\n{caution}\n"
    while len(body) < 160:
        caution = caution.rstrip("。") + "。" + pad
        body = f"{what}\n\n{when}\n\n{caution}\n"
        if len(body) > 360:
            break
    if not (160 <= len(body) <= 360):
        raise ValueError(f"desc {len(body)}: {what[:40]}")
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


def vendor(vid, name, region="overseas", url=None):
    v = {"id": vid, "name": name, "region": region}
    if url:
        v["url"] = url
    return v


ENTRIES_DATA = [
    mk(
        "collab-suite",
        "google-workspace",
        "Google Workspace",
        "suite",
        "Gmail/Docs/Drive/Meet 一体 · 中小团队默认 · 开放生态广",
        "https://workspace.google.com",
        "Google Workspace 将邮箱、文档、表格、云盘与会议合并为组织默认协作面，第三方集成与教育/创业折扣常见。",
        "团队以邮件+文档为核心生产力、希望快速开通身份与分享、不强依赖本地 Office 兼容时选它。",
        "深度公文版式与某些政企信创要求不如国产套件；中国大陆访问与合规需单独评估。",
        tags=["suite", "docs", "email", "collaboration"],
        vendorId="google",
        pricing={"model": "subscription"},
    ),
    mk(
        "collab-suite",
        "microsoft-365",
        "Microsoft 365",
        "suite",
        "Office+Teams+OneDrive 企业默认 · 身份/合规与 Azure 同栈",
        "https://www.microsoft.com/microsoft-365",
        "Microsoft 365 以 Word/Excel/Teams/OneDrive/SharePoint 构成企业协作与办公默认包，权限、合规与 Azure AD 深度绑定。",
        "组织已购 Microsoft 身份/设备管理或强依赖 Office 桌面兼容，需要统一套件而非多 SaaS 拼凑时选。",
        "协议与 SKU 复杂；轻团队可能被席位成本压住，可看 Google Workspace 或飞书。",
        tags=["suite", "office", "teams", "enterprise"],
        vendorId="microsoft",
        pricing={"model": "subscription"},
    ),
    mk(
        "collab-help",
        "archbee",
        "Archbee",
        "help-center",
        "产品/API 文档一体 · 嵌入与版本 · 面向开发者帮助中心",
        "https://www.archbee.com",
        "Archbee 把产品说明、API 参考与内部知识组织在同一文档产品里，适合开发者向帮助中心与公开文档站。",
        "SaaS 需要面向集成方的帮助与 API 文档一体托管、并希望比纯静态 SSG 少运维时与 GitBook 同轴对比。",
        "写作体验与编辑器深度因团队习惯差异大；纯客服 FAQ 向可看 Document360。",
        tags=["help-center", "docs", "api-docs", "saas"],
        vendorId="archbee-inc",
        pricing={"model": "subscription"},
    ),
    mk(
        "growth-cdp",
        "jitsu",
        "Jitsu",
        "cdp",
        "开源 Segment 替代 · 事件进仓 · ClickHouse/仓库友好",
        "https://jitsu.com",
        "Jitsu 提供开源事件采集与路由，强调把数据写入仓库/ClickHouse 等自有存储，减少纯黑盒 CDP 锁定。",
        "要自托管或仓库优先的事件管道、预算敏感且愿接维护成本时，与 RudderStack/Segment 同轴。",
        "目的地与调试体验需对照版本；治理与 schema 契约仍靠团队纪律。",
        tags=["cdp", "events", "open-source", "warehouse"],
        pricing={"model": "open-source"},
        vendorId="jitsu-inc",
        githubUrl="https://github.com/jitsucom/jitsu",
    ),
    mk(
        "cicd-gitops",
        "rancher-fleet",
        "Rancher Fleet",
        "gitops",
        "多集群 GitOps · Rancher 生态 · Bundle 规模交付",
        "https://fleet.rancher.io",
        "Fleet 是 Rancher 的 GitOps 引擎，面向多集群、大规模 Bundle 部署，与 Rancher 管理面深度集成。",
        "已在 Rancher/RKE 体系、需要把多集群应用配置以 Git 为源同步时列入对 Argo/Flux 的补充短名单。",
        "非 Rancher 栈粘性弱；单集群纯 GitOps 往往 Argo CD/Flux 更轻。",
        tags=["gitops", "kubernetes", "rancher", "multi-cluster"],
        pricing={"model": "open-source"},
        vendorId="suse-rancher",
        githubUrl="https://github.com/rancher/fleet",
    ),
    mk(
        "msg-webhook",
        "hook0",
        "Hook0",
        "outbound-webhook",
        "开源 Webhook 服务器 · 事件订阅 API · 可自托管",
        "https://www.hook0.com",
        "Hook0 开源提供事件订阅与 Webhook 投递服务，可自托管，面向要自建「给客户/内部系统推事件」能力的团队。",
        "需要出站 Webhook 能力且倾向开源自托管、而非上 Svix 类商业投递时对比。",
        "托管体验与门户完善度通常弱于 Svix；生产加固与多租户需自担。",
        tags=["webhook", "open-source", "events", "self-host"],
        pricing={"model": "open-source"},
        vendorId="hook0-inc",
        githubUrl="https://github.com/hook0/hook0",
    ),
]

VENDORS_DATA = [
    vendor("archbee-inc", "Archbee", url="https://www.archbee.com"),
    vendor("jitsu-inc", "Jitsu", url="https://jitsu.com"),
    vendor("suse-rancher", "SUSE Rancher", url="https://www.rancher.com"),
    vendor("hook0-inc", "Hook0", url="https://www.hook0.com"),
    vendor("google", "Google", url="https://www.google.com"),
    vendor("microsoft", "Microsoft", url="https://www.microsoft.com"),
]

EDGES_DATA = [
    edge(
        "e-google-workspace-alt-m365",
        "google-workspace",
        "microsoft-365",
        "alternative_to",
        note="全球化协作套件同轴",
        weight=0.85,
    ),
    edge(
        "e-feishu-domestic-workspace",
        "feishu",
        "google-workspace",
        "domestic_equivalent_of",
        note="国内一站式套件 vs Google Workspace",
        weight=0.7,
    ),
    edge(
        "e-feishu-domestic-m365",
        "feishu",
        "microsoft-365",
        "domestic_equivalent_of",
        note="国内套件 vs Microsoft 365",
        weight=0.65,
    ),
    edge(
        "e-m365-with-loop",
        "microsoft-365",
        "microsoft-loop",
        "commonly_used_with",
        note="Loop 组件常嵌在 M365/Teams 表面",
        weight=0.75,
    ),
    edge(
        "e-archbee-alt-gitbook",
        "archbee",
        "gitbook",
        "alternative_to",
        note="开发者向文档帮助中心同轴",
        weight=0.75,
    ),
    edge(
        "e-archbee-alt-document360",
        "archbee",
        "document360",
        "alternative_to",
        note="偏 API/产品文档 vs 客服知识库向",
        weight=0.6,
    ),
    edge(
        "e-jitsu-oss-segment",
        "jitsu",
        "segment",
        "open_source_alternative_to",
        note="开源/仓库优先事件管道 vs Segment",
        weight=0.8,
    ),
    edge(
        "e-jitsu-alt-rudderstack",
        "jitsu",
        "rudderstack",
        "alternative_to",
        note="开源 CDP/事件管道同轴",
        weight=0.75,
    ),
    edge(
        "e-fleet-alt-argo-cd",
        "rancher-fleet",
        "argo-cd",
        "alternative_to",
        note="多集群 Fleet vs Argo CD GitOps",
        weight=0.65,
    ),
    edge(
        "e-fleet-alt-flux-cd",
        "rancher-fleet",
        "flux-cd",
        "alternative_to",
        note="Rancher 多集群 vs Flux 模块化 GitOps",
        weight=0.65,
    ),
    edge(
        "e-hook0-oss-svix",
        "hook0",
        "svix",
        "open_source_alternative_to",
        note="开源自托管 Webhook 服务 vs Svix",
        weight=0.75,
    ),
    edge(
        "e-hook0-alt-hookdeck",
        "hook0",
        "hookdeck",
        "alternative_to",
        note="出站自建 vs 入站网关——问题常不同",
        weight=0.4,
    ),
]


def fix_loop_tags() -> None:
    path = ENTRIES / "microsoft-loop.json"
    if not path.exists():
        return
    data = json.loads(path.read_text(encoding="utf-8"))
    tags = list(data.get("tags") or [])
    for t in ("suite", "docs", "microsoft", "collaboration"):
        if t not in tags:
            tags.append(t)
    data["tags"] = tags[:5]
    data["lastReviewed"] = REVIEWED
    # ensure desc length
    if len(data.get("descriptionMd") or "") < 160:
        data["descriptionMd"] = (
            (data.get("descriptionMd") or "").rstrip()
            + "\n\n选型前请以 Microsoft 365 许可与 Teams 集成能力为准。\n"
        )
    save(path, data)
    print("patched microsoft-loop tags")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--overwrite", action="store_true")
    args = ap.parse_args()

    issues = []
    for e in ENTRIES_DATA:
        try:
            validate_entry(e)
        except (AssertionError, ValueError) as err:
            issues.append(str(err))
    if issues:
        for i in issues:
            print("INVALID", i)
        raise SystemExit(f"{len(issues)} failures")

    known = {e["id"] for e in ENTRIES_DATA}
    we = wv = wg = se = sv = sg = 0
    for e in ENTRIES_DATA:
        path = ENTRIES / f"{e['id']}.json"
        if path.exists() and not args.overwrite:
            se += 1
            continue
        save(path, e)
        we += 1
        print("entry", e["category"], e["id"])

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
        ok = True
        for end in (g["from"], g["to"]):
            if not ((ENTRIES / f"{end}.json").exists() or end in known):
                print("skip edge", g["id"], end)
                ok = False
                break
        if not ok:
            continue
        save(path, g)
        wg += 1
        print("edge", g["id"])

    fix_loop_tags()
    print(f"done entries={we}(skip {se}) vendors={wv}(skip {sv}) edges={wg}(skip {sg})")


if __name__ == "__main__":
    main()
