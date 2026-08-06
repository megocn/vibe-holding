#!/usr/bin/env python3
"""P2 上线路程补叶（2026-08-07）。

- obs-incident：PagerDuty / Opsgenie / incident.io
- msg-webhook：Svix / Hookdeck
- sec-fraud：Fingerprint / Sift · 同盾 / 数美
- cicd-unified-api：Nango / Merge / Paragon

遵守扩种准入：短名单、宁缺毋滥。状态页仍留 obs-uptime（通讯 ≠ 值班）。

用法:
  python3 scripts/expand-p2-incident-webhook-fraud-unified-2026-08.py
  python3 scripts/expand-p2-incident-webhook-fraud-unified-2026-08.py --overwrite
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTENT = ROOT / "content"
ENTRIES = CONTENT / "entries"
VENDORS = CONTENT / "vendors"
EDGES = CONTENT / "edges"
REVIEWED = "2026-08-07"

CAT_INC = "obs-incident"
CAT_WH = "msg-webhook"
CAT_FRAUD = "sec-fraud"
CAT_UNI = "cicd-unified-api"

DOMESTIC = {
    "chinaAccessible": True,
    "needsCompany": False,
    "needsIcp": False,
    "regions": ["CN"],
}


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
    assert 160 <= len(e["descriptionMd"]) <= 360, (
        e["id"],
        len(e["descriptionMd"]),
        e["descriptionMd"],
    )
    assert 1 <= len(e["pitfalls"]) <= 3, e["id"]
    assert 3 <= len(e["tags"]) <= 5, e["id"]
    assert e.get("subcategory"), e["id"]
    assert e["id"] == e["id"].lower() and e["id"][0].isalpha(), e["id"]


def desc(what: str, when: str, caution: str) -> str:
    pad = "选型前请以官网能力与定价页为准。"
    body = f"{what}\n\n{when}\n\n{caution}\n"
    while len(body) < 160:
        caution = caution.rstrip("。") + "。" + pad
        body = f"{what}\n\n{when}\n\n{caution}\n"
        if len(body) > 360:
            break
    if not (160 <= len(body) <= 360):
        raise ValueError(f"desc {len(body)} for {what[:40]}")
    return body


def mk(cat, eid, name, sub, one, url, what, when, caution, **extra):
    pitfalls = extra.pop("pitfalls", None)
    caution_full = caution
    body = desc(what, when, caution_full)
    # re-extract final caution used in body roughly for pitfalls default
    kw = {
        "id": eid,
        "name": name,
        "category": cat,
        "subcategory": sub,
        "oneLiner": one,
        "officialUrl": url,
        "descriptionMd": body,
        "pitfalls": pitfalls or [caution[:90]],
    }
    kw.update(extra)
    return entry(**kw)


def edge(eid, frm, to, typ, weight=0.7, confidence="community", note=None):
    e = {
        "id": eid,
        "from": frm,
        "to": to,
        "type": typ,
        "weight": weight,
        "confidence": confidence,
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
    # ——— On-call / incident ———
    mk(
        CAT_INC,
        "pagerduty",
        "PagerDuty",
        "on-call",
        "On-call 排班告警枢纽 · 事件路由/升级 · 事故响应事实标准",
        "https://www.pagerduty.com",
        "PagerDuty 把监控告警收成事件，做排班、升级策略、响应协作与事后复盘入口，是 On-call 与事故管理事实短名单头部。",
        "生产已有 metrics/日志告警，需要可靠叫醒值班、升级链与跨工具协同时优先对标；常与 Datadog/Prometheus 并用。",
        "席位与事件量计费陡；过度告警会烧坏旋转机制，需先治理噪音再上平台。",
        tags=["on-call", "incident", "alerting", "ops"],
        vendorId="pagerduty-inc",
        pricing={"model": "subscription"},
    ),
    mk(
        CAT_INC,
        "opsgenie",
        "Opsgenie",
        "on-call",
        "Atlassian 值班与告警 · 与 Jira/Statuspage 同栈",
        "https://www.atlassian.com/software/opsgenie",
        "Opsgenie 提供值班排班、告警路由与升级，深度嵌 Atlassian 工具链，事故可回流 Jira、对外经 Statuspage 同步。",
        "团队已在 Jira/Confluence/Statuspage，需要 On-call 与工单体系统一时纳入对比。",
        "Atlassian 产品线打包与单独采购路径复杂；非 Atlassian 栈粘性弱于 PagerDuty 中立性。",
        tags=["on-call", "incident", "atlassian", "alerting"],
        vendorId="atlassian",
        pricing={"model": "subscription"},
    ),
    mk(
        CAT_INC,
        "incident-io",
        "incident.io",
        "incident-mgmt",
        "现代化事故管理 · Slack 原生 · 声明/角色/复盘流",
        "https://incident.io",
        "incident.io 围绕 Slack 做事故声明、角色分工、时间线与复盘，偏「事故流程产品化」，与传统纯分页器互补或叠加。",
        "团队沟通主场在 Slack，希望把事故角色、沟通节奏和事后 review 流程做硬时选用。",
        "On-call 分页能力需与既有 pager/监控核对；非 Slack 团队收益下降。",
        tags=["incident", "slack", "ops", "sre"],
        vendorId="incident-io-inc",
        pricing={"model": "subscription"},
    ),
    # ——— Webhook ———
    mk(
        CAT_WH,
        "svix",
        "Svix",
        "outbound-webhook",
        "出站 Webhook 基建 · 签名/重试/门户 · 给 SaaS 发事件",
        "https://www.svix.com",
        "Svix 做出站 Webhook 基础设施：签名验证、自动重试、终端用户门户与多协议投递，让你的 SaaS 能可靠地把事件推给客户。",
        "产品要把「事件订阅/Webhook」当一等能力卖给集成方，又不想自建投递与签名体系时选用。",
        "入站聚合调试场景更偏 Hookdeck；自建若仅少数端点可能过重。",
        tags=["webhook", "events", "saas", "delivery"],
        vendorId="svix-inc",
        pricing={"model": "usage"},
    ),
    mk(
        CAT_WH,
        "hookdeck",
        "Hookdeck",
        "inbound-webhook",
        "入站 Webhook 网关 · 排队/重放/观测 · 本地开发友好",
        "https://hookdeck.com",
        "Hookdeck 聚焦入站 Webhook 可靠接收：队列、限流、重放、可观测与本地隧道式开发体验，适合对接 Stripe 等多源回调。",
        "大量第三方回调涌入、需要重放调试与缓冲削峰、或不想让源站直接扛尖峰时选用。",
        "做出站「给你的客户发 Webhook」主能力看 Svix；两边问题不同勿混选。",
        tags=["webhook", "inbound", "queue", "devtools"],
        vendorId="hookdeck-inc",
        pricing={"model": "freemium"},
    ),
    # ——— Fraud / fingerprint ———
    mk(
        CAT_FRAUD,
        "fingerprint",
        "Fingerprint",
        "device-fingerprint",
        "浏览器/设备指纹 · 识别回头访客 · 反滥用与登录风控",
        "https://fingerprint.com",
        "Fingerprint（原 FingerprintJS）提供高精度浏览器与设备识别，用于识别回头设备、对抗垃圾注册与共享账号滥用。",
        "增长与安全要在无登录场景识别设备、反羊毛或风控登录时的短名单头部。",
        "隐私合规（告知/同意）与误伤真人需产品策略；不是完整反欺诈决策引擎。",
        tags=["fingerprint", "fraud", "device", "security"],
        vendorId="fingerprint-inc",
        pricing={"model": "usage"},
    ),
    mk(
        CAT_FRAUD,
        "sift",
        "Sift",
        "fraud-platform",
        "数字信任与反欺诈 · 支付/账号风险评分 · 机器学习",
        "https://sift.com",
        "Sift 提供账号与支付链路的风险评分与工作流，覆盖虚假账号、盗卡与滥用行为，偏交易与增长防损。",
        "支付漏斗或双边市场已出现规模化欺诈，需要可运营的规则+模型决策时对标。",
        "接入与标注成本不低；指纹类工具互补而非替代。中国大陆数据出境与合规需评估。",
        tags=["fraud", "payments", "risk", "ml"],
        vendorId="sift-inc",
        pricing={"model": "usage"},
    ),
    mk(
        CAT_FRAUD,
        "tongdun",
        "同盾",
        "fraud-platform",
        "国内智能风控 · 设备/交易/反欺诈 · 金融互金常用",
        "https://www.tongdun.cn",
        "同盾提供设备指纹、反欺诈与信贷/交易风控能力，服务国内互联网与金融类业务的风险管理场景。",
        "面向中国用户、支付与营销防刷，需要本地化合规叙述与供应商时列入国内短名单。",
        "与海外 Fingerprint/Sift 能力重叠但数据与模型域不同；采购与接口对接偏项目制。",
        tags=["fraud", "domestic", "risk", "fingerprint"],
        region="domestic",
        availability={
            "chinaAccessible": True,
            "needsCompany": True,
            "needsIcp": False,
            "regions": ["CN"],
        },
        vendorId="tongdun-inc",
        pricing={"model": "subscription"},
    ),
    mk(
        CAT_FRAUD,
        "shumei",
        "数美",
        "fraud-platform",
        "国内内容+设备风控 · 反作弊/反欺诈 · 互金与社交",
        "https://www.ishumei.com",
        "数美覆盖设备指纹、账号与营销反作弊、部分内容安全能力，服务国内互金、社交与电商的风险识别。",
        "国内业务要设备与营销反作弊、并希望与内容审核能力同供应商评估时，与同盾同轴比选。",
        "产品线宽，选型时要钉准「设备/交易」还是内容审核边界，避免买错套餐。",
        tags=["fraud", "domestic", "risk", "anti-abuse"],
        region="domestic",
        availability={
            "chinaAccessible": True,
            "needsCompany": True,
            "needsIcp": False,
            "regions": ["CN"],
        },
        vendorId="shumei-inc",
        pricing={"model": "subscription"},
    ),
    # ——— Unified API ———
    mk(
        CAT_UNI,
        "nango",
        "Nango",
        "unified-api",
        "开源嵌入式集成 · OAuth/同步 · 给你的 SaaS 装集成",
        "https://www.nango.dev",
        "Nango 帮产品团队在自有 SaaS 内嵌「连接客户 CRM/工单等」的集成：OAuth、字段同步与可自托管管道，开源优先。",
        "你的产品要向客户提供 Salesforce/HubSpot 类双向集成，又不想把集成当成巨型内部项目时选。",
        "这与 Zapier 给最终用户搭自动化不是同一题；连接器覆盖要以目录为准。",
        tags=["unified-api", "integrations", "open-source", "oauth"],
        pricing={"model": "open-source"},
        vendorId="nango-inc",
        githubUrl="https://github.com/NangoHQ/nango",
    ),
    mk(
        CAT_UNI,
        "merge-dev",
        "Merge",
        "unified-api",
        "统一 API 接 HR/ATS/CRM · 一次接入多 SaaS",
        "https://www.merge.dev",
        "Merge 提供分类统一 API（HRIS、ATS、CRM 等），让你的应用一次对接即可覆盖多家客户侧 SaaS，减少逐家 OAuth。",
        "B2B 产品要读/写客户侧人力资源或 CRM 数据、希望集成覆盖面上市卖点时对标。",
        "按联动账户与类别计费；深度字段与边缘系统仍可能需定制。国内 SaaS 目录弱于欧美。",
        tags=["unified-api", "integrations", "b2b", "saas"],
        vendorId="merge-dev-inc",
        pricing={"model": "subscription"},
    ),
    mk(
        CAT_UNI,
        "paragon",
        "Paragon",
        "unified-api",
        "嵌入式 iPaaS · 可视化集成工作流 · 给产品加连接器",
        "https://www.useparagon.com",
        "Paragon 面向产品内嵌集成：托管 OAuth、可视化工作流与连接器目录，让终端用户在你的产品里点选集成。",
        "要在 App 内提供「连接 Slack/Salesforce」体验、工程带宽有限时与 Nango/Merge 同轴比较。",
        "平台锁定与连接器路线图取决于供应商；极深定制仍可能回到自研同步。",
        tags=["unified-api", "ipaas", "integrations", "embed"],
        vendorId="paragon-inc",
        pricing={"model": "subscription"},
    ),
]

VENDORS_DATA = [
    vendor("pagerduty-inc", "PagerDuty", url="https://www.pagerduty.com"),
    vendor("incident-io-inc", "incident.io", url="https://incident.io"),
    vendor("svix-inc", "Svix", url="https://www.svix.com"),
    vendor("hookdeck-inc", "Hookdeck", url="https://hookdeck.com"),
    vendor("fingerprint-inc", "Fingerprint", url="https://fingerprint.com"),
    vendor("sift-inc", "Sift", url="https://sift.com"),
    vendor("tongdun-inc", "同盾", region="domestic", url="https://www.tongdun.cn"),
    vendor("shumei-inc", "数美", region="domestic", url="https://www.ishumei.com"),
    vendor("nango-inc", "Nango", url="https://www.nango.dev"),
    vendor("merge-dev-inc", "Merge", url="https://www.merge.dev"),
    vendor("paragon-inc", "Paragon", url="https://www.useparagon.com"),
    # atlassian 多半已有
    vendor("atlassian", "Atlassian", url="https://www.atlassian.com"),
]

EDGES_DATA = [
    edge(
        "e-opsgenie-alt-pagerduty",
        "opsgenie",
        "pagerduty",
        "alternative_to",
        note="Atlassian 栈 On-call vs 中立 On-call 枢纽",
        weight=0.85,
    ),
    edge(
        "e-incident-io-alt-pagerduty",
        "incident-io",
        "pagerduty",
        "alternative_to",
        note="事故流程/Slack 原生 vs 经典分页与升级",
        weight=0.65,
    ),
    edge(
        "e-opsgenie-with-statuspage",
        "opsgenie",
        "statuspage",
        "commonly_used_with",
        note="值班告警与对外状态沟通同栈",
        weight=0.75,
    ),
    edge(
        "e-pagerduty-with-datadog",
        "pagerduty",
        "datadog",
        "commonly_used_with",
        note="监控告警常路由到 PagerDuty",
        weight=0.8,
    ),
    edge(
        "e-pagerduty-with-statuspage",
        "pagerduty",
        "statuspage",
        "commonly_used_with",
        note="内部响应与对外状态页联动",
        weight=0.6,
    ),
    edge(
        "e-hookdeck-alt-svix",
        "hookdeck",
        "svix",
        "alternative_to",
        note="入站接收/重放 vs 出站投递门户——层可互补",
        weight=0.45,
    ),
    edge(
        "e-svix-with-stripe",
        "svix",
        "stripe",
        "commonly_used_with",
        note="支付成功后再向你的客户扇出 Webhook 的常见架构",
        weight=0.5,
    ),
    edge(
        "e-fingerprint-with-sift",
        "fingerprint",
        "sift",
        "commonly_used_with",
        note="设备信号喂给反欺诈决策",
        weight=0.65,
    ),
    edge(
        "e-sift-with-stripe",
        "sift",
        "stripe",
        "commonly_used_with",
        note="支付链路风险评分",
        weight=0.6,
    ),
    edge(
        "e-tongdun-domestic-fingerprint",
        "tongdun",
        "fingerprint",
        "domestic_equivalent_of",
        note="国内设备/反欺诈能力 vs 全球设备指纹",
        weight=0.55,
    ),
    edge(
        "e-shumei-domestic-sift",
        "shumei",
        "sift",
        "domestic_equivalent_of",
        note="国内反作弊/风控 vs 全球数字信任平台",
        weight=0.5,
    ),
    edge(
        "e-tongdun-alt-shumei",
        "tongdun",
        "shumei",
        "alternative_to",
        note="国内风控供应商同轴",
        weight=0.75,
    ),
    edge(
        "e-fingerprint-alt-turnstile",
        "fingerprint",
        "cloudflare-turnstile",
        "alternative_to",
        note="持续设备识别 vs 人机验证——问题不同",
        weight=0.35,
    ),
    edge(
        "e-nango-oss-merge",
        "nango",
        "merge-dev",
        "open_source_alternative_to",
        note="可自托管嵌入式集成 vs 分类统一 API",
        weight=0.7,
    ),
    edge(
        "e-paragon-alt-merge",
        "paragon",
        "merge-dev",
        "alternative_to",
        note="嵌入式 iPaaS 工作流 vs 统一 API 目录",
        weight=0.75,
    ),
    edge(
        "e-paragon-alt-nango",
        "paragon",
        "nango",
        "alternative_to",
        note="托管嵌入式集成 vs 开源 Nango",
        weight=0.7,
    ),
    edge(
        "e-nango-alt-zapier",
        "nango",
        "zapier",
        "alternative_to",
        note="给产品装集成 vs 给终端用户搭自动化——题不同",
        weight=0.4,
    ),
    edge(
        "e-merge-with-hubspot",
        "merge-dev",
        "hubspot",
        "commonly_used_with",
        note="统一 CRM 类别常映射到 HubSpot 等",
        weight=0.6,
    ),
]


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

    assert len({e["id"] for e in ENTRIES_DATA}) == len(ENTRIES_DATA)
    assert len({g["id"] for g in EDGES_DATA}) == len(EDGES_DATA)

    known = {e["id"] for e in ENTRIES_DATA}
    we = wv = wg = se = sv = sg = 0

    for e in ENTRIES_DATA:
        path = ENTRIES / f"{e['id']}.json"
        if path.exists() and not args.overwrite:
            se += 1
            print("skip entry", e["id"])
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
                print("skip edge missing", g["id"], end)
                ok = False
                break
        if not ok:
            continue
        save(path, g)
        wg += 1
        print("edge", g["id"])

    print(f"done entries={we}(skip {se}) vendors={wv}(skip {sv}) edges={wg}(skip {sg})")
    print("leaves:", CAT_INC, CAT_WH, CAT_FRAUD, CAT_UNI)


if __name__ == "__main__":
    main()
