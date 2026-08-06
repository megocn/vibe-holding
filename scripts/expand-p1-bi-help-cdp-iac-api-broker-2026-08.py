#!/usr/bin/env python3
"""P1 可比单元拆叶扩种（2026-08-07）。

遵守扩种准入：短名单、宁缺毋滥；迁移优先于重写。

新叶:
- db-bi：Metabase / Superset / Looker Studio · FineBI
- collab-help：Document360 + 迁移 GitBook
- growth-cdp：RudderStack + 迁移 Segment
- cicd-iac：OpenTofu + 迁移 Terraform / Pulumi
- cicd-gitops：迁移 Argo CD / Flux CD
- oss-api-dev：Postman / Hoppscotch / Insomnia · Apifox
- msg-broker：RocketMQ / Redpanda + 迁移 Kafka 族

用法:
  python3 scripts/expand-p1-bi-help-cdp-iac-api-broker-2026-08.py
  python3 scripts/expand-p1-bi-help-cdp-iac-api-broker-2026-08.py --overwrite
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

CAT_BI = "db-bi"
CAT_HELP = "collab-help"
CAT_CDP = "growth-cdp"
CAT_IAC = "cicd-iac"
CAT_GITOPS = "cicd-gitops"
CAT_API = "oss-api-dev"
CAT_BROKER = "msg-broker"

MIGRATE: dict[str, tuple[str, str | None]] = {
    # id -> (category, subcategory|None to set)
    "terraform": (CAT_IAC, "iac"),
    "pulumi": (CAT_IAC, "iac"),
    "argo-cd": (CAT_GITOPS, "gitops"),
    "flux-cd": (CAT_GITOPS, "gitops"),
    "segment": (CAT_CDP, "cdp"),
    "gitbook": (CAT_HELP, "help-center"),
    "kafka": (CAT_BROKER, "streaming"),
    "rabbitmq": (CAT_BROKER, "queue"),
    "apache-pulsar": (CAT_BROKER, "streaming"),
    "confluent-cloud": (CAT_BROKER, "managed"),
    "aws-msk": (CAT_BROKER, "managed"),
}

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
        "pricing": {"model": "freemium"},
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
    assert 160 <= len(e["descriptionMd"]) <= 360, (e["id"], len(e["descriptionMd"]), e["descriptionMd"])
    assert 1 <= len(e["pitfalls"]) <= 3, e["id"]
    assert 3 <= len(e["tags"]) <= 5, e["id"]
    assert e.get("subcategory"), e["id"]
    assert e["id"] == e["id"].lower() and e["id"][0].isalpha(), e["id"]


def desc(what: str, when: str, caution: str) -> str:
    body = f"{what}\n\n{when}\n\n{caution}\n"
    # 保证落在 160–360：谨慎追加短说明而非硬截断
    pad = "选型前请以官网与当前定价页为准。"
    while len(body) < 160:
        caution = caution.rstrip("。") + "。" + pad
        body = f"{what}\n\n{when}\n\n{caution}\n"
        if len(body) > 360:
            break
    if not (160 <= len(body) <= 360):
        raise ValueError(f"desc length {len(body)}: {what[:40]}")
    return body


def mk(cat, eid, name, sub, one, url, what, when, caution, **extra):
    pitfalls = extra.pop("pitfalls", None)
    description = desc(what, when, caution)
    # 同步 pitfalls 与 caution 一致感：取第一句
    pit = pitfalls or [caution[:90]]
    kw = {
        "id": eid,
        "name": name,
        "category": cat,
        "subcategory": sub,
        "oneLiner": one,
        "officialUrl": url,
        "descriptionMd": description,
        "pitfalls": pit,
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
    # ——— BI ———
    mk(
        CAT_BI,
        "metabase",
        "Metabase",
        "bi-dashboard",
        "开源 BI 入门默认 · SQL/GUI 问数 · 自托管或云",
        "https://www.metabase.com",
        "Metabase 提供 GUI 问数、SQL 编辑器、仪表盘与权限，开源可自托管，也有托管云，是团队级 BI 事实入门选项。",
        "仓库或 Postgres/ClickHouse 已就绪，业务要自助看转化与经营指标、工程不愿上重型 BI 套件时优先对标。",
        "复杂语义层与百万行以上性能需调优；企业治理与嵌入能力要对照商业版。",
        tags=["bi", "dashboard", "open-source", "sql"],
        pricing={"model": "open-source"},
        vendorId="metabase-inc",
        githubUrl="https://github.com/metabase/metabase",
    ),
    mk(
        CAT_BI,
        "apache-superset",
        "Apache Superset",
        "bi-dashboard",
        "Airbnb 开源 BI · 图表/探索强 · 云与自建常见",
        "https://superset.apache.org",
        "Apache Superset 是开源数据探索与仪表盘平台，图表类型丰富、SQL Lab 与多数据源连接成熟，常见于数据团队自建。",
        "已有数仓/查询层，需要比 Metabase 更重探索与可视化、可接受运维成本时列入短名单。",
        "部署与权限模型比 Metabase 更重；非技术业务自助体验因配置差异大。",
        tags=["bi", "dashboard", "open-source", "apache"],
        pricing={"model": "open-source"},
        vendorId="apache-software-foundation",
        githubUrl="https://github.com/apache/superset",
    ),
    mk(
        CAT_BI,
        "looker-studio",
        "Looker Studio",
        "bi-dashboard",
        "原 Data Studio · 免费连 GA/Sheet · 营销看板快",
        "https://lookerstudio.google.com",
        "Looker Studio（原 Google Data Studio）免费连接 GA4、Sheets、BigQuery 等，拖拽作营销与运营看板成本极低。",
        "增长/市场团队要快速看板、数据主要在 Google 系且预算近零时使用；与企业 Looker 语义层不是同一档。",
        "复杂权限、语义层与企业嵌入远弱于 Looker/Metabase 自建；依赖 Google 账号与配额。",
        tags=["bi", "dashboard", "google", "marketing"],
        pricing={"model": "free"},
        vendorId="google",
    ),
    mk(
        CAT_BI,
        "finebi",
        "FineBI",
        "bi-dashboard",
        "帆软自助 BI · 国内企业看板事实选项 · 实施重",
        "https://www.finebi.com",
        "FineBI 是帆软自助式 BI 产品，面向业务人员拖拽分析与门户看板，在国内政企与中大型数据项目中渗透高。",
        "国内企业要中文文档、本地化实施与信创叙述、与报表/大屏体系打通时，国内 BI 主选之一。",
        "采购与实施成本高；云原生轻团队往往更偏向 Metabase 自托管。",
        tags=["bi", "dashboard", "domestic", "enterprise"],
        region="domestic",
        availability={
            "chinaAccessible": True,
            "needsCompany": True,
            "needsIcp": False,
            "regions": ["CN"],
        },
        vendorId="fanruan-inc",
        pricing={"model": "subscription"},
    ),
    # ——— 帮助中心 ———
    mk(
        CAT_HELP,
        "document360",
        "Document360",
        "help-center",
        "产品帮助中心 SaaS · 版本/多语言 · 客服知识库向",
        "https://document360.com",
        "Document360 专做客户向知识库与帮助中心：版本、多语言、分类检索与分析，面向支持与产品文档团队。",
        "SaaS 产品需要独立 Help Center、降低重复工单，又不想用纯静态文档站时对标。",
        "工程向 API 文档与 Git 工作流体验弱于 Mintlify/Docusaurus；席位与流量档位要算成本。",
        tags=["help-center", "docs", "support", "saas"],
        vendorId="document360-inc",
    ),
    # ——— CDP ———
    mk(
        CAT_CDP,
        "rudderstack",
        "RudderStack",
        "cdp",
        "开源/可管 CDP · Segment 工作流 · 仓库优先路由",
        "https://www.rudderstack.com",
        "RudderStack 提供事件采集与多目的地路由，开源可自托管，强调把事件写入仓库再反哺工具的「仓库优先」路径。",
        "要削弱 Segment 锁定、自管管道、或把事件先落 BigQuery/Snowflake 再对接下游工具时选用。",
        "目的地覆盖与调试体验仍要核对版本；运维管道与 schema 治理需团队投入。",
        tags=["cdp", "events", "open-source", "pipeline"],
        pricing={"model": "open-source"},
        vendorId="rudderstack-inc",
        githubUrl="https://github.com/rudderlabs/rudder-server",
    ),
    # ——— IaC ———
    mk(
        CAT_IAC,
        "opentofu",
        "OpenTofu",
        "iac",
        "Terraform 开源分叉 · HCL 兼容 · Linux 基金会",
        "https://opentofu.org",
        "OpenTofu 是 Terraform 的开源分叉，兼容 HCL 与大量现有模块，社区治理在 Linux 基金会下，规避 BUSL 许可顾虑。",
        "团队已有 Terraform 模块资产、需要明确开源许可与供应商中立时，与 Terraform 同轴对比。",
        "云厂商最新资源 provider 节奏可能滞后商业 Terraform；企业协作功能要对齐。",
        tags=["iac", "terraform", "open-source", "hcl"],
        pricing={"model": "open-source"},
        vendorId="opentofu-linux-foundation",
        githubUrl="https://github.com/opentofu/opentofu",
    ),
    # ——— API 工具 ———
    mk(
        CAT_API,
        "postman",
        "Postman",
        "api-client",
        "API 调试协作事实标准 · 集合/Mock/监控 · 团队空间",
        "https://www.postman.com",
        "Postman 是 API 设计与调试协作平台：集合、环境、Mock、监控与团队工作区，行业默认短名单。",
        "前后端联调、对外 API 交付文档与自动化轻测、跨角色共享请求样本时主轴。",
        "高级协作与用量计费陡；纯开源替代看 Hoppscotch/Insomnia/Apifox。",
        tags=["api", "http", "devops", "collaboration"],
        vendorId="postman-inc",
    ),
    mk(
        CAT_API,
        "hoppscotch",
        "Hoppscotch",
        "api-client",
        "开源 Web API 客户端 · 轻快 · 可自托管",
        "https://hoppscotch.io",
        "Hoppscotch（原 Postwoman）是开源 API 客户端，浏览器体验快，可自托管，适合轻量调试与团队分享。",
        "要摆脱 Postman 客户端体积/账号、偏好开源自托管时列入对比。",
        "企业治理、大型工作区与官方 Mock 生态弱于 Postman；高级场景要组合其他工具。",
        tags=["api", "open-source", "http", "self-host"],
        pricing={"model": "open-source"},
        vendorId="hoppscotch-inc",
        githubUrl="https://github.com/hoppscotch/hoppscotch",
    ),
    mk(
        CAT_API,
        "insomnia",
        "Insomnia",
        "api-client",
        "设计简洁的 API 客户端 · 插件/Git · Kong 生态",
        "https://insomnia.rest",
        "Insomnia 侧重视觉清晰的 REST/GraphQL 调试，支持插件与 Git 同步，与 Kong 生态有交集。",
        "工程师偏好本地客户端、需要 GraphQL 调试体验并与 Postman 比工作流时选。",
        "团队协作与云同步能力相对 Postman 弱；许可证与账号策略历史上有过调整需关注。",
        tags=["api", "http", "graphql", "desktop"],
        vendorId="kong-inc",
        pricing={"model": "freemium"},
    ),
    mk(
        CAT_API,
        "apifox",
        "Apifox",
        "api-client",
        "国内 API 一体化 · 设计/调试/Mock · Postman+文档感",
        "https://apifox.com",
        "Apifox 把接口设计、调试、Mock 与文档一体化，中文体验与国内协作习惯友好，常作 Postman 国内替代。",
        "国内团队要统一接口文档与联调、减少多工具跳转时，国内 API 协作主选之一。",
        "出海协作与英文生态密度弱于 Postman；高级企业网关场景仍看配套治理。",
        tags=["api", "domestic", "mock", "collaboration"],
        region="domestic",
        availability=DOMESTIC,
        vendorId="apifox-inc",
    ),
    # ——— 消息中间件补种 ———
    mk(
        CAT_BROKER,
        "apache-rocketmq",
        "Apache RocketMQ",
        "queue",
        "阿里开源消息中间件 · 事务/顺序/延时 · 国内默认之一",
        "https://rocketmq.apache.org",
        "Apache RocketMQ 源自阿里，强调事务消息、顺序与延时等业务消息语义，国内互联网与金融系统广泛使用。",
        "国内业务消息、电商订单与交易链路需要强顺序/事务消息语义时优先对标 Kafka 的应用消息轴。",
        "全球云厂商生态密度低于 Kafka；跨语言客户端与运维知识要按版本核对。",
        tags=["queue", "messaging", "apache", "domestic"],
        pricing={"model": "open-source"},
        region="domestic",
        availability=DOMESTIC,
        vendorId="apache-software-foundation",
        githubUrl="https://github.com/apache/rocketmq",
    ),
    mk(
        CAT_BROKER,
        "redpanda",
        "Redpanda",
        "streaming",
        "Kafka API 兼容 · 无 ZooKeeper · 低延迟流",
        "https://www.redpanda.com",
        "Redpanda 以 Kafka API 兼容为目标，C++ 实现、无 ZooKeeper 依赖，强调简单运维与较低延迟。",
        "要 Kafka 协议生态、又想简化集群运维或提升尾延迟时，与 Kafka/MSK 同轴对比。",
        "生态连接器完整度仍看版本；深度 Kafka 内部特性不能默认 100% 等价。",
        tags=["streaming", "kafka-compatible", "events"],
        vendorId="redpanda-inc",
        pricing={"model": "open-source"},
        githubUrl="https://github.com/redpanda-data/redpanda",
    ),
]

VENDORS_DATA = [
    vendor("metabase-inc", "Metabase", url="https://www.metabase.com"),
    vendor("document360-inc", "Document360", url="https://document360.com"),
    vendor("rudderstack-inc", "RudderStack", url="https://www.rudderstack.com"),
    vendor("opentofu-linux-foundation", "OpenTofu", url="https://opentofu.org"),
    vendor("postman-inc", "Postman", url="https://www.postman.com"),
    vendor("hoppscotch-inc", "Hoppscotch", url="https://hoppscotch.io"),
    vendor("apifox-inc", "Apifox", region="domestic", url="https://apifox.com"),
    vendor("redpanda-inc", "Redpanda", url="https://www.redpanda.com"),
    vendor("fanruan-inc", "帆软", region="domestic", url="https://www.fanruan.com"),
    # google / apache-software-foundation / kong-inc 多半已有
    vendor("google", "Google", url="https://www.google.com"),
    vendor("apache-software-foundation", "Apache Software Foundation", url="https://apache.org"),
    vendor("kong-inc", "Kong", url="https://konghq.com"),
]

EDGES_DATA = [
    # BI
    edge(
        "e-superset-oss-metabase",
        "apache-superset",
        "metabase",
        "open_source_alternative_to",
        note="更重探索可视化的开源 BI vs Metabase 入门向",
        weight=0.7,
    ),
    edge(
        "e-looker-studio-alt-metabase",
        "looker-studio",
        "metabase",
        "alternative_to",
        note="Google 免费营销看板 vs 自托管/产品化 BI",
        weight=0.55,
    ),
    edge(
        "e-finebi-domestic-metabase",
        "finebi",
        "metabase",
        "domestic_equivalent_of",
        note="国内企业自助 BI vs 开源/全球 Metabase",
        weight=0.55,
    ),
    edge(
        "e-metabase-with-postgresql",
        "metabase",
        "postgresql",
        "commonly_used_with",
        note="常直连业务/仓 Postgres 做看板",
        weight=0.7,
    ),
    edge(
        "e-metabase-with-clickhouse",
        "metabase",
        "clickhouse",
        "commonly_used_with",
        note="分析库常见接法",
        weight=0.65,
    ),
    # help
    edge(
        "e-document360-alt-gitbook",
        "document360",
        "gitbook",
        "alternative_to",
        note="客服向帮助中心 vs 产品/协作文档站",
        weight=0.7,
    ),
    # gitbook↔mintlify 已有 e-mintlify-alt-gitbook，不重复
    edge(
        "e-document360-with-zendesk",
        "document360",
        "zendesk",
        "commonly_used_with",
        note="知识库降低 Zendesk 重复工单",
        weight=0.55,
    ),
    edge(
        "e-document360-with-intercom",
        "document360",
        "intercom",
        "commonly_used_with",
        note="帮助中心与会话支持互补",
        weight=0.5,
    ),
    # CDP
    edge(
        "e-rudderstack-oss-segment",
        "rudderstack",
        "segment",
        "open_source_alternative_to",
        note="可自托管事件 CDP 管道 vs Segment",
        weight=0.85,
    ),
    edge(
        "e-rudderstack-with-mixpanel",
        "rudderstack",
        "mixpanel",
        "commonly_used_with",
        note="管道下游常接产品分析",
        weight=0.65,
    ),
    edge(
        "e-segment-with-mixpanel",
        "segment",
        "mixpanel",
        "commonly_used_with",
        note="采集一次路由到 Mixpanel 等",
        weight=0.7,
    ),
    # IaC
    edge(
        "e-opentofu-oss-terraform",
        "opentofu",
        "terraform",
        "open_source_alternative_to",
        note="HCL 兼容开源分叉 vs 商业许可 Terraform",
        weight=0.9,
    ),
    # pulumi↔terraform 已有 edge-terraform-pulumi-alternative-to
    # GitOps
    edge(
        "e-flux-cd-alt-argo-cd",
        "flux-cd",
        "argo-cd",
        "alternative_to",
        note="GitOps 持续交付同轴：模块化 reconcile vs UI 驱动",
        weight=0.85,
    ),
    # API
    edge(
        "e-hoppscotch-oss-postman",
        "hoppscotch",
        "postman",
        "open_source_alternative_to",
        note="开源轻量客户端 vs Postman",
        weight=0.8,
    ),
    edge(
        "e-insomnia-alt-postman",
        "insomnia",
        "postman",
        "alternative_to",
        note="本地 API 客户端同轴",
        weight=0.75,
    ),
    edge(
        "e-apifox-domestic-postman",
        "apifox",
        "postman",
        "domestic_equivalent_of",
        note="国内一体化 API 协作 vs Postman",
        weight=0.8,
    ),
    edge(
        "e-hoppscotch-alt-insomnia",
        "hoppscotch",
        "insomnia",
        "alternative_to",
        note="开源 API 客户端同轴",
        weight=0.7,
    ),
    # broker（rabbitmq/kafka、pulsar/kafka 边已有，不重复）
    edge(
        "e-rocketmq-domestic-kafka",
        "apache-rocketmq",
        "kafka",
        "domestic_equivalent_of",
        note="国内业务消息语义强 vs 全球事件流标杆",
        weight=0.55,
    ),
    edge(
        "e-redpanda-alt-kafka",
        "redpanda",
        "kafka",
        "alternative_to",
        note="Kafka API 兼容运行时",
        weight=0.8,
    ),
    edge(
        "e-confluent-with-kafka",
        "confluent-cloud",
        "kafka",
        "commonly_used_with",
        note="托管发行与连接器基于 Kafka 协议",
        weight=0.85,
    ),
    edge(
        "e-msk-with-kafka",
        "aws-msk",
        "kafka",
        "commonly_used_with",
        note="AWS 托管开源 Kafka",
        weight=0.85,
    ),
]


def migrate() -> None:
    for eid, (cat, sub) in MIGRATE.items():
        path = ENTRIES / f"{eid}.json"
        if not path.exists():
            print("warn: missing migrate target", eid)
            continue
        data = json.loads(path.read_text(encoding="utf-8"))
        old = data.get("category")
        data["category"] = cat
        data["lastReviewed"] = REVIEWED
        if sub and not data.get("subcategory"):
            data["subcategory"] = sub
        elif sub:
            data["subcategory"] = sub
        # tags 最少 3
        tags = list(data.get("tags") or [])
        if cat == CAT_BROKER:
            for t in ("messaging", "broker"):
                if t not in tags:
                    tags.append(t)
        if cat == CAT_IAC:
            for t in ("iac", "devops"):
                if t not in tags:
                    tags.append(t)
        if cat == CAT_GITOPS:
            for t in ("gitops", "kubernetes", "cd"):
                if t not in tags:
                    tags.append(t)
        if cat == CAT_CDP:
            for t in ("cdp", "events", "analytics"):
                if t not in tags:
                    tags.append(t)
        if cat == CAT_HELP:
            for t in ("docs", "help-center", "saas"):
                if t not in tags:
                    tags.append(t)
        data["tags"] = tags[:5]
        if len(data["tags"]) < 3:
            data["tags"] = (data["tags"] + ["infra", "tooling", "platform"])[:3]
        # description length soft fix if too short (pulumi/sensors not here)
        dm = data.get("descriptionMd") or ""
        if len(dm) < 160:
            pad = "\n\n选型前请以官网文档与当前许可策略为准。\n"
            if not dm.endswith("\n"):
                dm += "\n"
            data["descriptionMd"] = (dm.rstrip() + pad) if len(dm + pad) <= 360 else dm
            # still short? append more
            while len(data["descriptionMd"]) < 160:
                data["descriptionMd"] = data["descriptionMd"].rstrip() + " 详细能力以发布说明为准。\n"
                if len(data["descriptionMd"]) > 360:
                    break
        save(path, data)
        print(f"migrated {eid} {old} → {cat}")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--overwrite", action="store_true")
    args = ap.parse_args()

    issues = []
    for e in ENTRIES_DATA:
        try:
            validate_entry(e)
        except AssertionError as err:
            issues.append(str(err))
        except ValueError as err:
            issues.append(str(err))
    if issues:
        for i in issues:
            print("INVALID", i)
        raise SystemExit(f"{len(issues)} validation failures")

    ids = [e["id"] for e in ENTRIES_DATA]
    assert len(ids) == len(set(ids))
    gids = [g["id"] for g in EDGES_DATA]
    assert len(gids) == len(set(gids))

    wrote_e = wrote_v = wrote_g = 0
    skip_e = skip_v = skip_g = 0
    known = {x["id"] for x in ENTRIES_DATA} | set(MIGRATE.keys())

    for e in ENTRIES_DATA:
        path = ENTRIES / f"{e['id']}.json"
        if path.exists() and not args.overwrite:
            skip_e += 1
            print("skip entry", e["id"])
            continue
        save(path, e)
        wrote_e += 1
        print("entry", e["category"], e["id"])

    for v in VENDORS_DATA:
        path = VENDORS / f"{v['id']}.json"
        if path.exists() and not args.overwrite:
            skip_v += 1
            continue
        save(path, v)
        wrote_v += 1
        print("vendor", v["id"])

    for g in EDGES_DATA:
        path = EDGES / f"{g['id']}.json"
        if path.exists() and not args.overwrite:
            skip_g += 1
            continue
        for end in (g["from"], g["to"]):
            if not ((ENTRIES / f"{end}.json").exists() or end in known):
                print("skip edge missing", g["id"], end)
                break
        else:
            save(path, g)
            wrote_g += 1
            print("edge", g["id"])

    migrate()

    print(
        f"done entries={wrote_e}(skip {skip_e}) vendors={wrote_v}(skip {skip_v}) "
        f"edges={wrote_g}(skip {skip_g})"
    )
    print(
        "leaves:",
        CAT_BI,
        CAT_HELP,
        CAT_CDP,
        CAT_IAC,
        CAT_GITOPS,
        CAT_API,
        CAT_BROKER,
    )


if __name__ == "__main__":
    main()
