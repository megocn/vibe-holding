#!/usr/bin/env python3
"""可观测日志 / 可用性监控 / 实时通信三叶扩种（2026-08）。

- obs-logs：Graylog / Vector / Fluent Bit / Logstash / OpenObserve / Sumo Logic / 阿里云 SLS / 腾讯云 CLS
- obs-uptime：UptimeRobot / Checkly / Cronitor / Healthchecks.io / Pingdom / Statuspage / Instatus / OpenStatus
- msg-realtime：Pusher / Ably / Liveblocks / PartyKit / Socket.IO / Centrifugo / Yjs / 声网 / 即构 / 腾讯云 TRTC

用法:
  python3 scripts/expand-obs-realtime-2026-08.py
  python3 scripts/expand-obs-realtime-2026-08.py --overwrite
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
REVIEWED = "2026-08-05"

CAT_LOGS = "obs-logs"
CAT_UPTIME = "obs-uptime"
CAT_REALTIME = "msg-realtime"


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
    one = e["oneLiner"]
    assert 20 <= len(one) <= 58, (e["id"], len(one), one)
    dlen = len(e.get("descriptionMd", ""))
    assert 160 <= dlen <= 360, (e["id"], dlen)
    assert e.get("pitfalls"), e["id"]
    assert e.get("subcategory"), e["id"]
    assert 3 <= len(e.get("tags") or []) <= 5, (e["id"], e.get("tags"))
    assert e["pricing"]["model"] in {"free", "freemium", "subscription", "usage", "open-source"}, e["id"]
    assert e["maturity"] in {"experimental", "beta", "stable", "mature"}, e["id"]
    assert e["region"] in {"overseas", "domestic", "both"}, e["id"]
    return e


def desc(what: str, when: str, caution: str) -> str:
    return f"{what}\n\n{when}\n\n{caution}\n"


def mk(cat, eid, name, sub, one, url, what, when, caution, **extra):
    pitfalls = extra.pop("pitfalls", None)
    kw = {
        "id": eid,
        "name": name,
        "category": cat,
        "subcategory": sub,
        "oneLiner": one,
        "officialUrl": url,
        "descriptionMd": desc(what, when, caution),
        "pitfalls": pitfalls or [caution[:90]],
    }
    kw.update(extra)
    return entry(**kw)


def edge(eid, frm, to, typ, weight=0.7, confidence="community", note=None, sources=None):
    assert typ in {
        "alternative_to",
        "open_source_alternative_to",
        "domestic_equivalent_of",
        "commonly_used_with",
        "integrates_with",
        "depends_on",
        "built_on",
        "part_of",
        "migration_path_to",
        "conflicts_with",
        "succeeds",
    }, (eid, typ)
    e = {
        "id": eid,
        "from": frm,
        "to": to,
        "type": typ,
        "weight": weight,
        "confidence": confidence,
        "sources": sources or [],
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


GLOBAL = {
    "chinaAccessible": True,
    "needsCompany": False,
    "needsIcp": False,
    "regions": ["global"],
}

DOMESTIC = {
    "chinaAccessible": True,
    "needsCompany": False,
    "needsIcp": False,
    "regions": ["CN"],
}

BOTH = {
    "chinaAccessible": True,
    "needsCompany": False,
    "needsIcp": False,
    "regions": ["CN", "global"],
}


# ————————————————————————— obs-logs —————————————————————————

LOGS: list[dict] = [
    mk(
        CAT_LOGS,
        "graylog",
        "Graylog",
        "log-management",
        "自托管日志门面 · 输入/流分发/权限告警齐全 · 依赖搜索引擎存储",
        "https://graylog.org",
        "Graylog 是自托管的日志管理平台：统一接收 Syslog、GELF、Beats 等输入，按流做分发与留存策略，再叠加检索、仪表盘、告警与角色权限。Open 版免费自建，企业与安全模块另行授权。",
        "已经或愿意维护 Elasticsearch / OpenSearch 集群、需要一套带账号权限与审计视角的日志门面时评估；只想低成本把日志聚起来看，先比 Loki 这类只索引标签的方案。",
        "存储层的容量与运维仍归自己；开源版与商业版在归档、审计、安全分析上的边界要在选型时逐项核对，别按官网总览页想当然。",
        vendorId="graylog-inc",
        githubUrl="https://github.com/Graylog2/graylog2-server",
        pricing={"model": "open-source", "notes": "Open 版免费自托管；Enterprise / Security 按数据量商业授权"},
        maturity="mature",
        tags=["logging", "self-host", "open-source", "siem"],
        pitfalls=[
            "存储层（ES/OpenSearch）的扩容与调优成本仍在自己身上",
            "开源版与企业版的归档、审计、安全模块边界需逐项核对",
        ],
    ),
    mk(
        CAT_LOGS,
        "vector-dev",
        "Vector",
        "log-pipeline",
        "Rust 高性能可观测数据管道 · 日志/指标统一转换 · Datadog 开源",
        "https://vector.dev",
        "Vector 是 Datadog 开源的可观测数据管道，用 Rust 写成，把日志、指标、事件从各类来源采集后经 VRL 变换脚本清洗、采样、脱敏，再分发到多个下游后端，可作 Agent 也可作聚合层。",
        "需要在采集端就做裁剪降本、或要同时向多个后端双写以便平滑迁移供应商时评估；栈中它站在应用与日志存储之间，替代或前置于 Fluent Bit、Logstash。",
        "VRL 变换脚本属于新的一套语法，团队要额外学习与测试；作为聚合层部署时它本身也需要高可用与背压容量规划。",
        vendorId="datadog-inc",
        githubUrl="https://github.com/vectordotdev/vector",
        pricing={"model": "open-source"},
        maturity="stable",
        tags=["logging", "pipeline", "open-source", "observability"],
        pitfalls=[
            "VRL 变换脚本是独立语法，需要单独学习与回归测试",
            "作聚合层时自身要做高可用与磁盘缓冲容量规划",
        ],
    ),
    mk(
        CAT_LOGS,
        "fluent-bit",
        "Fluent Bit",
        "log-pipeline",
        "轻量 C 语言采集器 · K8s DaemonSet 事实标准 · 内存占用极低",
        "https://fluentbit.io",
        "Fluent Bit 是 CNCF 旗下的轻量日志与指标采集器，用 C 实现，内存占用只有几十 MB，插件覆盖主流输入与输出，几乎是 Kubernetes 集群里日志边车与 DaemonSet 的默认选择。",
        "在容器与边缘节点上要一个足够省资源的采集端时首选；它负责收与转，落地存储与检索交给 Loki、Elasticsearch、对象存储或各家云日志服务。",
        "复杂的解析与富化能力弱于 Logstash 与 Vector；配置以文件段落为主，多环境差异容易漂移，建议纳入配置管理统一下发。",
        githubUrl="https://github.com/fluent/fluent-bit",
        pricing={"model": "open-source"},
        maturity="mature",
        tags=["logging", "pipeline", "kubernetes", "open-source"],
        pitfalls=[
            "复杂解析与富化能力弱于 Logstash / Vector",
            "多环境配置容易漂移，需纳入统一配置管理",
        ],
    ),
    mk(
        CAT_LOGS,
        "logstash",
        "Logstash",
        "log-pipeline",
        "ELK 经典管道 · 插件与 Grok 解析最全 · JVM 资源开销偏重",
        "https://www.elastic.co/logstash",
        "Logstash 是 Elastic 官方的日志收集与处理管道，凭 Grok、Mutate 等成熟过滤器与庞大的插件生态，长期承担 ELK 栈里的解析与富化环节，也能对接非 Elastic 的下游。",
        "已在 Elastic 栈内、且日志格式杂乱需要重解析时最划算；纯转发场景用 Elastic Agent、Fluent Bit 或 Vector 更省资源。",
        "基于 JVM，单实例内存与启动开销明显高于 C/Rust 系采集器；授权与版本节奏跟随 Elastic 主线，跨大版本升级要连同下游一起验证。",
        vendorId="elastic",
        githubUrl="https://github.com/elastic/logstash",
        pricing={"model": "open-source", "notes": "随 Elastic Stack 发行，遵循其授权条款"},
        maturity="mature",
        tags=["logging", "pipeline", "elastic", "open-source"],
        pitfalls=[
            "JVM 内存与启动开销高于 C/Rust 系采集器",
            "版本与授权跟随 Elastic 主线，跨大版本升级需连同下游验证",
        ],
    ),
    mk(
        CAT_LOGS,
        "openobserve",
        "OpenObserve",
        "log-store",
        "Rust 写的一体化可观测后端 · 直接落对象存储 · 号称极省存储",
        "https://openobserve.ai",
        "OpenObserve 用 Rust 实现，把日志、指标与链路收在同一后端，数据以列式格式直接落在 S3 等对象存储上，自带查询界面与告警，部署形态比 Elasticsearch 一类集群轻得多。",
        "想自托管一套统一的可观测后端、又不愿养搜索引擎集群时评估；它可以接在 Fluent Bit、Vector 或 OpenTelemetry Collector 后面，替代 Loki 加 Elasticsearch 的组合。",
        "项目相对年轻，大规模高基数场景下的查询表现需自行压测；开源版与云版在多租户、权限上的差异要提前确认。",
        vendorId="openobserve-inc",
        githubUrl="https://github.com/openobserve/openobserve",
        pricing={"model": "open-source", "notes": "开源自托管免费；官方云版按摄入量计费"},
        maturity="beta",
        tags=["logging", "observability", "open-source", "self-host"],
        pitfalls=[
            "项目较年轻，高基数与大规模查询表现需自行压测",
            "开源版与云版在多租户与权限上的差异需提前确认",
        ],
    ),
    mk(
        CAT_LOGS,
        "sumo-logic",
        "Sumo Logic",
        "log-management",
        "老牌托管日志分析 SaaS · 偏安全与合规审计 · 按摄入量计费",
        "https://www.sumologic.com",
        "Sumo Logic 是较早的一批云端日志分析服务，主打机器数据的集中检索、仪表盘与告警，并在安全运营与合规审计方向做了不少打包能力，属于完全托管、不需自建存储的形态。",
        "企业侧要求日志长期留存、审计线索与安全分析，又不想自己养集群时评估；轻量应用日志上云看 Axiom，自建省钱看 Loki 或 OpenObserve。",
        "按摄入与留存计费，噪声日志会直接变成账单，接入前先做采样与裁剪；数据出境与留存地域需与合规团队确认。",
        vendorId="sumo-logic-inc",
        pricing={"model": "usage", "currency": "USD", "notes": "按摄入数据量与留存时长计费"},
        maturity="mature",
        availability=GLOBAL,
        tags=["logging", "saas", "security", "compliance"],
        pitfalls=[
            "按摄入量计费，噪声日志会直接推高账单",
            "数据出境与留存地域需与合规团队确认",
        ],
    ),
    mk(
        CAT_LOGS,
        "aliyun-sls",
        "阿里云日志服务 SLS",
        "cloud-logs",
        "阿里云一站式日志 · 采集/加工/投递闭环 · 与云内产品打通深",
        "https://www.aliyun.com/product/sls",
        "阿里云日志服务 SLS 覆盖日志的采集、存储、加工、检索与投递全链路，自带 Logtail 采集端与查询分析语法，并与云内的计算、存储、告警产品打通，是国内公有云日志侧最完整的一套。",
        "主体资源已在阿里云、希望日志与云监控告警同栈闭环时优先；跨云或混合部署再评估 Loki、OpenObserve 这类可自托管方案。",
        "计费维度较多（写入、索引、存储、投递分开算），索引字段开多了成本上升明显；重度使用后迁出成本高，采集端尽量保留标准协议出口。",
        vendorId="aliyun",
        region="domestic",
        availability=DOMESTIC,
        pricing={"model": "usage", "currency": "CNY", "notes": "写入、索引、存储与投递分项计费"},
        maturity="mature",
        tags=["logging", "cloud", "domestic", "aliyun"],
        sources=["https://www.aliyun.com/product/sls", "https://www.aliyun.com"],
        pitfalls=[
            "写入、索引、存储分项计费，索引字段开多成本明显上升",
            "深度使用后迁出成本高，采集端建议保留标准协议出口",
        ],
    ),
    mk(
        CAT_LOGS,
        "tencent-cls",
        "腾讯云日志服务 CLS",
        "cloud-logs",
        "腾讯云托管日志 · 检索分析与投递一体 · 与云内告警同栈",
        "https://cloud.tencent.com/product/cls",
        "腾讯云日志服务 CLS 提供日志采集、结构化存储、检索分析、告警与投递能力，支持 LogListener 与主流开源采集端接入，常与腾讯云上的容器、网关、数据库日志一起使用。",
        "业务主体在腾讯云、希望日志与云上告警与对象存储链路打通时优先；国内跨云或要自控存储成本，再看自托管管道加对象存储的组合。",
        "索引与留存策略直接决定账单，接入前先按日志级别分流；控制台能力与开放接口更新较快，自动化脚本要跟随版本回归。",
        vendorId="tencent-cloud",
        region="domestic",
        availability=DOMESTIC,
        pricing={"model": "usage", "currency": "CNY", "notes": "按写入流量、索引与存储时长计费"},
        maturity="mature",
        tags=["logging", "cloud", "domestic", "tencent"],
        sources=["https://cloud.tencent.com/product/cls", "https://cloud.tencent.com"],
        pitfalls=[
            "索引与留存策略直接决定账单，需按日志级别分流",
            "控制台与开放接口迭代较快，自动化脚本需跟随回归",
        ],
    ),
]


# ———————————————————————— obs-uptime ————————————————————————

UPTIME: list[dict] = [
    mk(
        CAT_UPTIME,
        "uptimerobot",
        "UptimeRobot",
        "uptime-check",
        "老牌拨测入门款 · 免费额度大 · 监控项与状态页一站配齐",
        "https://uptimerobot.com",
        "UptimeRobot 是最常见的外部拨测服务：HTTP、端口、关键字与心跳几类检查加上多渠道通知，免费档就能覆盖几十个监控项，配置界面简单，也提供基础的对外状态页。",
        "个人项目与中小团队要第一层「网站还活着吗」的监控时最省事；需要浏览器级流程校验看 Checkly，需要自托管与数据自持看 OpenStatus。",
        "只从外部看可用性，定位不到内部原因，需与日志和 APM 搭配；免费档的检查频率与节点数量有限，误报与漏报都要留出容忍窗口。",
        vendorId="uptimerobot-inc",
        pricing={"model": "freemium", "currency": "USD", "notes": "免费档覆盖基础监控项，付费档提升频率与功能"},
        maturity="mature",
        availability=GLOBAL,
        tags=["uptime", "monitoring", "status-page", "saas"],
        pitfalls=[
            "只看外部可用性，定位不到内部原因，需与日志/APM 搭配",
            "免费档检查频率与探测节点有限，需容忍误报窗口",
        ],
    ),
    mk(
        CAT_UPTIME,
        "checkly",
        "Checkly",
        "synthetic-monitoring",
        "Playwright 写的合成监控 · 监控即代码 · 面向前端关键流程",
        "https://www.checklyhq.com",
        "Checkly 把可用性监控写成代码：用 Playwright 脚本跑真实浏览器流程，用 API 检查校验接口契约，配合命令行与基础设施即代码方式纳入版本库，随部署一起发布。",
        "登录、下单这类多步关键流程需要持续验证，或团队已习惯把监控放进仓库管理时选它；只要「域名是否可达」用 UptimeRobot 更划算。",
        "浏览器检查按运行次数计费，脚本写得频繁又冗长会明显推高成本；脚本本身也是需要维护的代码，页面改版后容易连环误报。",
        vendorId="checkly-inc",
        pricing={"model": "freemium", "currency": "USD", "notes": "按检查运行次数计费，含免费额度"},
        maturity="stable",
        availability=GLOBAL,
        tags=["uptime", "synthetic", "playwright", "monitoring"],
        pitfalls=[
            "浏览器检查按运行次数计费，高频脚本成本上升快",
            "监控脚本本身需维护，页面改版易引发连环误报",
        ],
    ),
    mk(
        CAT_UPTIME,
        "cronitor",
        "Cronitor",
        "cron-heartbeat",
        "定时任务心跳起家 · 兼顾拨测与状态页 · 面向后台作业",
        "https://cronitor.io",
        "Cronitor 从定时任务监控起家：作业开始与结束时上报心跳，超时、失败或干脆没跑都会告警，后来又补上了站点拨测与状态页，形成一套围绕后台作业的可用性视图。",
        "关心的是「夜里那个批处理有没有跑成功」而不只是首页能否打开时选它；纯网站拨测用 UptimeRobot，自托管心跳看 Healthchecks.io。",
        "心跳类监控要求业务侧改代码埋点，接入面比外部拨测大；多产品线合并计费，监控项一多要重新算单价。",
        vendorId="cronitor-inc",
        pricing={"model": "freemium", "currency": "USD", "notes": "按监控项数量分档订阅"},
        maturity="stable",
        availability=GLOBAL,
        tags=["uptime", "cron", "heartbeat", "monitoring"],
        pitfalls=[
            "心跳监控需要业务侧改代码埋点，接入面大于外部拨测",
            "监控项增多后按项计费的单价需重新测算",
        ],
    ),
    mk(
        CAT_UPTIME,
        "healthchecks-io",
        "Healthchecks.io",
        "cron-heartbeat",
        "开源 cron 心跳 · 一个 URL 即接入 · 可完全自托管",
        "https://healthchecks.io",
        "Healthchecks.io 是专注定时任务心跳的开源项目：给每个作业分配一个 URL，脚本跑完 curl 一下即可，逾期未报到就触发通知，托管版与自托管版功能基本一致。",
        "运维脚本、备份任务与数据管道需要「没跑就告警」的兜底时接入成本最低；要一并管理网站拨测与状态页，再叠 UptimeRobot 或 Cronitor。",
        "只覆盖心跳这一件事，不做浏览器流程与深层探测；自托管版本需要自己保证告警通道与数据库可用，否则监控系统自身成了盲区。",
        vendorId="healthchecks-io-inc",
        githubUrl="https://github.com/healthchecks/healthchecks",
        pricing={"model": "freemium", "currency": "USD", "notes": "自托管免费开源；官方托管版按项目档位订阅"},
        maturity="stable",
        availability=GLOBAL,
        tags=["uptime", "cron", "open-source", "self-host"],
        pitfalls=[
            "只覆盖心跳，不做浏览器流程与深层探测",
            "自托管时需保证告警通道可用，否则监控自身成盲区",
        ],
    ),
    mk(
        CAT_UPTIME,
        "pingdom",
        "Pingdom",
        "uptime-check",
        "SolarWinds 旗下老牌拨测 · 全球节点多 · 偏企业采购",
        "https://www.pingdom.com",
        "Pingdom 是历史悠久的站点可用性与性能监控服务，现属 SolarWinds，提供全球分布的探测节点、页面速度分析与真实用户监控，报表与告警形态偏向企业运维。",
        "需要覆盖面广的全球拨测节点、且已在 SolarWinds 体系内采购运维工具时评估；轻量项目用 UptimeRobot，流程校验用 Checkly。",
        "价格与套餐面向企业，个人项目性价比低；产品迭代节奏偏稳健，新特性不如新兴同类活跃。",
        vendorId="solarwinds",
        pricing={"model": "subscription", "currency": "USD", "notes": "按监控项与真实用户监控量分档"},
        maturity="mature",
        availability=GLOBAL,
        tags=["uptime", "monitoring", "enterprise", "saas"],
        pitfalls=[
            "套餐面向企业，个人与小团队性价比偏低",
            "迭代节奏稳健，新特性不如新兴同类活跃",
        ],
    ),
    mk(
        CAT_UPTIME,
        "statuspage",
        "Atlassian Statuspage",
        "status-page",
        "对外事故沟通标准件 · 与 Jira/Opsgenie 同栈 · 订阅者通知全",
        "https://www.atlassian.com/software/statuspage",
        "Statuspage 是 Atlassian 的对外状态页产品，负责事故公告、组件状态、维护窗口与订阅者通知，本身不做探测，而是把内部告警与人工判断翻译成客户能看懂的对外口径。",
        "面向外部客户、需要一套规范的事故沟通与订阅通知机制时选它，尤其是已经在用 Jira 与 Opsgenie 的团队；探测能力仍需 UptimeRobot、Checkly 等提供。",
        "不含拨测能力，得与监控工具搭配才完整；按订阅者规模计费，用户量大时成本上升，轻量场景可看 Instatus 或 OpenStatus。",
        vendorId="atlassian",
        pricing={"model": "subscription", "currency": "USD", "notes": "按状态页数量与订阅者规模分档"},
        maturity="mature",
        availability=GLOBAL,
        tags=["status-page", "incident", "atlassian", "saas"],
        pitfalls=[
            "自身不含拨测能力，需与监控工具搭配",
            "按订阅者规模计费，用户量大时成本上升明显",
        ],
    ),
    mk(
        CAT_UPTIME,
        "instatus",
        "Instatus",
        "status-page",
        "轻快状态页 · 一次性买断式定价友好 · 自定义域名与主题",
        "https://instatus.com",
        "Instatus 是主打轻快与好看的状态页服务，页面为静态托管、加载快，支持自定义域名、主题与订阅通知，并能从常见监控工具接收事件自动更新组件状态。",
        "需要一张体面的对外状态页、又不想为订阅者规模持续付高价时评估；企业级事故流程与工单联动仍是 Statuspage 更完整。",
        "定位在状态页本身，事故管理与值班排班能力有限；自动更新依赖上游监控的集成质量，接入前先验证事件映射关系。",
        vendorId="instatus-inc",
        pricing={"model": "freemium", "currency": "USD", "notes": "免费档可用基础状态页，付费档解锁自定义域名等"},
        maturity="stable",
        availability=GLOBAL,
        tags=["status-page", "incident", "saas", "monitoring"],
        pitfalls=[
            "事故管理与值班排班能力有限，偏纯状态页",
            "自动更新依赖上游监控集成质量，需先验证事件映射",
        ],
    ),
    mk(
        CAT_UPTIME,
        "openstatus",
        "OpenStatus",
        "uptime-check",
        "开源拨测加状态页 · 可自托管数据自持 · 现代前端栈实现",
        "https://www.openstatus.dev",
        "OpenStatus 是开源的可用性监控与状态页项目，把合成拨测、延迟分布与对外状态页放在一起，既提供官方托管版，也可以完整自托管，数据留在自己手里。",
        "既要拨测又要状态页、且倾向开源与自持数据的团队值得一试；要成熟的企业事故流程仍看 Statuspage，要省心免维护看 UptimeRobot。",
        "项目仍在快速演进，自托管需要跟随上游升级；探测节点与告警通道数量不及成熟商业服务，关键业务建议双份监控。",
        vendorId="openstatus-inc",
        githubUrl="https://github.com/openstatusHQ/openstatus",
        pricing={"model": "open-source", "notes": "开源自托管免费；官方云版按监控项分档"},
        maturity="beta",
        availability=GLOBAL,
        tags=["uptime", "status-page", "open-source", "self-host"],
        pitfalls=[
            "项目演进快，自托管需要持续跟随上游升级",
            "探测节点与告警通道少于成熟商业服务，关键业务建议双份监控",
        ],
    ),
]


# ——————————————————————— msg-realtime ———————————————————————

REALTIME: list[dict] = [
    mk(
        CAT_REALTIME,
        "pusher",
        "Pusher",
        "hosted-pubsub",
        "托管 WebSocket 频道 · 接入最省事 · 按连接与消息数计费",
        "https://pusher.com",
        "Pusher Channels 提供托管的发布订阅通道：客户端订阅频道、服务端触发事件，SDK 覆盖主流语言与前端框架，开发者不必自建长连接集群就能做通知、在线状态与实时看板。",
        "只需要把服务端事件推到浏览器、且不想承担连接层运维时最快；要严格的消息有序与历史回放看 Ably，要自托管省钱看 Centrifugo。",
        "按并发连接与消息条数计费，广播型场景增长很快；托管服务的连接上限与区域节点决定体验，国内用户的跨境时延需实测。",
        vendorId="pusher-inc",
        pricing={"model": "freemium", "currency": "USD", "notes": "按并发连接数与日消息量分档"},
        maturity="mature",
        availability=GLOBAL,
        tags=["realtime", "websocket", "pubsub", "saas"],
        pitfalls=[
            "按并发连接与消息量计费，广播型场景成本增长快",
            "国内访问的跨境时延需实测，无本地节点保障",
        ],
    ),
    mk(
        CAT_REALTIME,
        "ably",
        "Ably",
        "hosted-pubsub",
        "带交付保证的实时消息云 · 有序与历史回放 · 多协议接入",
        "https://ably.com",
        "Ably 是面向实时消息的托管平台，强调消息有序、精确一次的交付语义、断线续传与历史回放，除 WebSocket 外还支持 MQTT、SSE 等多种协议，并提供跨区域的边缘网络。",
        "金融行情、体育比分、协同状态同步等对丢消息零容忍的场景优先；只做简单通知推送，Pusher 接入更轻，自托管看 Centrifugo。",
        "能力越全定价维度越复杂，消息数、连接数与通道数分别计量；把交付保证的假设写进业务逻辑后，迁移到简单方案的代价会变大。",
        vendorId="ably-inc",
        pricing={"model": "freemium", "currency": "USD", "notes": "按消息数、并发连接与通道数计量"},
        maturity="mature",
        availability=GLOBAL,
        tags=["realtime", "websocket", "pubsub", "saas"],
        pitfalls=[
            "计费维度多（消息/连接/通道），需按峰值建模测算",
            "交付保证一旦写进业务假设，迁移到简单方案代价大",
        ],
    ),
    mk(
        CAT_REALTIME,
        "liveblocks",
        "Liveblocks",
        "collaboration",
        "多人协同现成积木 · 光标/评论/通知开箱 · 前端框架优先",
        "https://liveblocks.io",
        "Liveblocks 提供多人协同的上层能力：在线状态与光标、共享存储、评论与通知等做成了现成组件与 Hook，同时可以承载 Yjs 文档，让协同编辑不必从连接层自己搭起。",
        "要在 React 一类前端里快速做出「像 Figma 那样多人在场」的体验时最省时间；只要底层同步算法用 Yjs，只要消息通道用 Pusher 或 Ably。",
        "上层抽象越省事，越绑定其数据模型与房间概念，替换需要重写协同层；按月活协同用户计费，规模上来后要重新测算。",
        vendorId="liveblocks-inc",
        pricing={"model": "freemium", "currency": "USD", "notes": "按月活协同用户与房间数分档"},
        maturity="stable",
        availability=GLOBAL,
        tags=["realtime", "collaboration", "crdt", "saas"],
        pitfalls=[
            "上层抽象绑定其房间与数据模型，替换需重写协同层",
            "按月活协同用户计费，规模扩大后成本需重新测算",
        ],
    ),
    mk(
        CAT_REALTIME,
        "partykit",
        "PartyKit",
        "edge-realtime",
        "边缘有状态房间 · 一段服务端代码即一个房间 · Cloudflare 系",
        "https://www.partykit.io",
        "PartyKit 把实时应用抽象成「房间」：每个房间是一段跑在边缘的有状态服务端代码，天然处理连接、广播与持久状态，底座是 Cloudflare 的 Durable Objects 与 Workers。",
        "做多人游戏、协同白板或 AI 应用的实时会话，且愿意把逻辑写在边缘运行时里时评估；纯消息分发用 Pusher，协同组件用 Liveblocks。",
        "运行时受边缘平台约束，长连接时长、内存与依赖都有限制；项目已并入 Cloudflare 体系，长期形态可能随之调整，重要项目留好迁移预案。",
        vendorId="partykit-inc",
        githubUrl="https://github.com/partykit/partykit",
        pricing={"model": "freemium", "currency": "USD", "notes": "开源框架免费；托管运行随底层边缘平台计费"},
        maturity="beta",
        availability=GLOBAL,
        tags=["realtime", "edge", "websocket", "open-source"],
        pitfalls=[
            "受边缘运行时约束：连接时长、内存与依赖都有限制",
            "已并入 Cloudflare 体系，长期产品形态可能调整",
        ],
    ),
    mk(
        CAT_REALTIME,
        "socket-io",
        "Socket.IO",
        "websocket-lib",
        "经典实时通信库 · 自动重连与房间广播 · 需自建服务端",
        "https://socket.io",
        "Socket.IO 是历史最久、生态最厚的实时通信库，在 WebSocket 之上补齐自动重连、心跳、房间与命名空间等约定，服务端以 Node.js 为主，各语言都有社区实现的客户端。",
        "自建服务端、想要一套久经检验的连接层抽象时选它；多实例部署需要配合适配器共享状态，不想运维连接层则用 Pusher、Ably。",
        "协议是私有约定，客户端必须用配套 SDK，与原生 WebSocket 不互通；水平扩展要引入适配器与粘性会话，运维复杂度都在自己这边。",
        githubUrl="https://github.com/socketio/socket.io",
        pricing={"model": "open-source"},
        maturity="mature",
        availability=GLOBAL,
        tags=["realtime", "websocket", "open-source", "nodejs"],
        pitfalls=[
            "私有协议，客户端必须使用配套 SDK，与原生 WebSocket 不互通",
            "水平扩展需引入适配器与粘性会话，运维成本自担",
        ],
    ),
    mk(
        CAT_REALTIME,
        "centrifugo",
        "Centrifugo",
        "self-hosted-pubsub",
        "自托管实时消息服务器 · 语言无关 · 靠 Redis 横向扩展",
        "https://centrifugal.dev",
        "Centrifugo 是用 Go 写的独立实时消息服务器，与业务语言解耦：后端通过 HTTP 或 gRPC 发布，前端用其 SDK 订阅频道，支持在线状态、历史消息与频道权限，多节点靠 Redis 一类代理打通。",
        "后端不是 Node.js、又想自建长连接层省下托管费用时是常见选择；不愿运维连接层就用 Pusher 或 Ably，需要协同数据结构则叠 Yjs。",
        "连接层的容量规划、灰度与故障演练都要自己做；鉴权采用签名令牌模式，接入时要把密钥轮换与过期策略一并设计好。",
        githubUrl="https://github.com/centrifugal/centrifugo",
        pricing={"model": "open-source", "notes": "开源自托管；另有商业版扩展"},
        maturity="stable",
        availability=GLOBAL,
        tags=["realtime", "websocket", "open-source", "self-host"],
        pitfalls=[
            "连接层容量规划、灰度与故障演练需自行承担",
            "令牌鉴权需自行设计密钥轮换与过期策略",
        ],
    ),
    mk(
        CAT_REALTIME,
        "yjs",
        "Yjs",
        "crdt",
        "协同编辑的 CRDT 内核 · 传输层可插拔 · 编辑器适配最全",
        "https://yjs.dev",
        "Yjs 是高性能的 CRDT 实现，负责多端并发修改后的自动合并与离线同步，本身不含服务器，传输可以走 WebSocket、WebRTC 或任意通道，并为主流富文本与代码编辑器提供了成熟绑定。",
        "自建协同文档、白板或代码编辑器时作为数据同步内核；想连服务端一起省掉，就选 Liveblocks 或 PartyKit 这类把 Yjs 托管起来的方案。",
        "只解决数据合并，鉴权、持久化与历史版本都得自建；CRDT 文档会随编辑历史增长，需要设计快照与垃圾回收策略。",
        githubUrl="https://github.com/yjs/yjs",
        pricing={"model": "open-source"},
        maturity="stable",
        availability=GLOBAL,
        tags=["realtime", "crdt", "collaboration", "open-source"],
        pitfalls=[
            "只解决数据合并，鉴权、持久化与版本历史需自建",
            "文档随编辑历史增长，需设计快照与垃圾回收策略",
        ],
    ),
    mk(
        CAT_REALTIME,
        "agora",
        "声网 Agora",
        "rtc",
        "自建实时网络的音视频云 · 弱网表现稳 · 国内外双区可用",
        "https://www.agora.io",
        "声网 Agora 是以软件定义实时网络为底座的音视频云，提供互动直播、语音通话、实时消息与信令 SDK，覆盖移动端、Web 与小程序，在弱网抗性与全球加速上投入较多。",
        "出海产品或国内互动场景需要成熟的 RTC 能力、且希望一套 SDK 兼顾双区时评估；愿意自托管则看 LiveKit，纯消息通道用 Ably 或 Pusher。",
        "按分钟数计费，音视频分辨率与并发规模会显著放大账单；国内与海外为不同区域，账号、合规与接入域名需分别规划。",
        vendorId="agora-inc",
        region="both",
        availability=BOTH,
        pricing={"model": "usage", "currency": "CNY", "notes": "按音视频通话分钟数计费，分辨率越高单价越高"},
        maturity="mature",
        tags=["realtime", "rtc", "webrtc", "video"],
        pitfalls=[
            "按分钟计费，高分辨率与大并发会显著放大账单",
            "国内与海外属不同区域，账号与合规需分别规划",
        ],
    ),
    mk(
        CAT_REALTIME,
        "zego",
        "即构 ZEGO",
        "rtc",
        "音视频加上层场景组件 · 语聊房/直播模板全 · 出海双区支持",
        "https://www.zego.im",
        "即构科技提供实时音视频、实时语音与互动直播的 SDK，除底层通话能力外还打包了语聊房、直播间、K 歌等上层场景组件，可以少写不少业务侧的连麦与麦位逻辑。",
        "社交娱乐、语聊房与秀场直播这类场景要快速成型时优势明显；只要纯粹的会议或对话式 AI 通道，声网与 LiveKit 的对照更直接。",
        "上层场景组件用得越深，业务与其 SDK 的耦合越紧；按分钟计费，海外区域覆盖与国内不完全一致，出海前先确认目标地区节点。",
        vendorId="zego-inc",
        region="both",
        availability=BOTH,
        pricing={"model": "usage", "currency": "CNY", "notes": "按音视频通话分钟数计费，按场景包另行报价"},
        maturity="mature",
        tags=["realtime", "rtc", "webrtc", "domestic"],
        pitfalls=[
            "上层场景组件用得越深，业务与其 SDK 耦合越紧",
            "海外节点覆盖与国内不完全一致，出海前需确认目标地区",
        ],
    ),
    mk(
        CAT_REALTIME,
        "tencent-trtc",
        "腾讯云 TRTC",
        "rtc",
        "腾讯云实时音视频 · 与直播/点播/IM 同栈 · 国内节点密",
        "https://cloud.tencent.com/product/trtc",
        "腾讯云 TRTC 是云上的实时音视频服务，提供多人通话、互动连麦与低延时观看，并与腾讯云的直播、点播、即时通信等产品同栈，接入侧有较完整的 UI 组件与 Demo。",
        "业务已在腾讯云、需要 RTC 与直播链路自然衔接的国内团队优先；跨云或要自托管控制成本，则评估 LiveKit 这类开源方案。",
        "按通话分钟与套餐包计费，连麦人数与分辨率是主要成本变量；能力与云内其他产品耦合较紧，迁移到自建方案需重做信令与转推链路。",
        vendorId="tencent-cloud",
        region="domestic",
        availability=DOMESTIC,
        pricing={"model": "usage", "currency": "CNY", "notes": "按通话分钟数与套餐包计费"},
        maturity="mature",
        tags=["realtime", "rtc", "cloud", "domestic"],
        sources=["https://cloud.tencent.com/product/trtc", "https://cloud.tencent.com"],
        pitfalls=[
            "按分钟与套餐包计费，连麦人数与分辨率是主要成本变量",
            "与云内其他产品耦合紧，迁自建需重做信令与转推链路",
        ],
    ),
]


ENTRIES_DATA: list[dict] = LOGS + UPTIME + REALTIME


VENDORS_DATA: list[dict] = [
    vendor("graylog-inc", "Graylog", url="https://graylog.org"),
    vendor("openobserve-inc", "OpenObserve", url="https://openobserve.ai"),
    vendor("sumo-logic-inc", "Sumo Logic", url="https://www.sumologic.com"),
    vendor("uptimerobot-inc", "UptimeRobot", url="https://uptimerobot.com"),
    vendor("checkly-inc", "Checkly", url="https://www.checklyhq.com"),
    vendor("cronitor-inc", "Cronitor", url="https://cronitor.io"),
    vendor("healthchecks-io-inc", "Healthchecks.io", url="https://healthchecks.io"),
    vendor("solarwinds", "SolarWinds", url="https://www.solarwinds.com"),
    vendor("instatus-inc", "Instatus", url="https://instatus.com"),
    vendor("openstatus-inc", "OpenStatus", url="https://www.openstatus.dev"),
    vendor("pusher-inc", "Pusher", url="https://pusher.com"),
    vendor("ably-inc", "Ably", url="https://ably.com"),
    vendor("liveblocks-inc", "Liveblocks", url="https://liveblocks.io"),
    vendor("partykit-inc", "PartyKit", url="https://www.partykit.io"),
    vendor("zego-inc", "即构科技 ZEGO", region="domestic", url="https://www.zego.im"),
]


EDGES_DATA: list[dict] = [
    # ——— obs-logs 同层对照 ———
    edge(
        "e-graylog-osalt-sumo-logic",
        "graylog",
        "sumo-logic",
        "open_source_alternative_to",
        note="自托管日志门面 vs 全托管日志分析 SaaS：省订阅费但要自养存储与集群",
        weight=0.7,
    ),
    edge(
        "e-openobserve-osalt-datadog",
        "openobserve",
        "datadog",
        "open_source_alternative_to",
        note="对象存储直写的自托管可观测后端 vs 商业全家桶：省摄入费，换来自运维",
        weight=0.6,
    ),
    edge(
        "e-openobserve-osalt-axiom",
        "openobserve",
        "axiom",
        "open_source_alternative_to",
        note="同为列式低成本日志后端；OpenObserve 可自托管，Axiom 是托管 Serverless 形态",
        weight=0.65,
    ),
    edge(
        "e-openobserve-alt-loki",
        "openobserve",
        "loki",
        "alternative_to",
        note="一体化后端（日志+指标+链路）vs 只索引标签、依赖 Grafana 做界面",
        weight=0.7,
    ),
    edge(
        "e-graylog-alt-openobserve",
        "graylog",
        "openobserve",
        "alternative_to",
        note="成熟权限与告警体系 vs 更轻的存储形态与更新的实现",
        weight=0.6,
    ),
    edge(
        "e-vector-dev-alt-fluent-bit",
        "vector-dev",
        "fluent-bit",
        "alternative_to",
        note="Rust 管道，变换与多路分发更强 vs C 采集器，资源占用更低",
        weight=0.8,
    ),
    edge(
        "e-fluent-bit-alt-logstash",
        "fluent-bit",
        "logstash",
        "alternative_to",
        note="轻量转发首选 vs JVM 重解析：Grok 富化强但资源开销大",
        weight=0.75,
    ),
    edge(
        "e-vector-dev-cuw-loki",
        "vector-dev",
        "loki",
        "commonly_used_with",
        note="Vector 采集与裁剪，Loki 承担存储与检索，是常见的低成本日志栈",
        weight=0.7,
    ),
    edge(
        "e-fluent-bit-cuw-opentelemetry",
        "fluent-bit",
        "opentelemetry",
        "commonly_used_with",
        note="Fluent Bit 支持 OTLP 收发，常与 OTel Collector 混编在同一采集链路",
        weight=0.7,
    ),
    edge(
        "e-vector-dev-iw-prometheus",
        "vector-dev",
        "prometheus",
        "integrates_with",
        note="Vector 可抓取并导出 Prometheus 指标，把日志与指标收在同一管道",
        weight=0.6,
    ),
    edge(
        "e-logstash-cuw-elasticsearch",
        "logstash",
        "elasticsearch",
        "commonly_used_with",
        note="ELK 经典组合：Logstash 解析富化，Elasticsearch 承担索引与检索",
        weight=0.85,
    ),
    edge(
        "e-graylog-dep-elasticsearch",
        "graylog",
        "elasticsearch",
        "depends_on",
        note="Graylog 的检索层依赖 Elasticsearch / OpenSearch，存储运维成本随之而来",
        weight=0.8,
    ),
    edge(
        "e-sumo-logic-alt-datadog",
        "sumo-logic",
        "datadog",
        "alternative_to",
        note="偏日志与安全审计的托管服务 vs 指标链路日志全覆盖的可观测平台",
        weight=0.7,
    ),
    edge(
        "e-aliyun-sls-part-of-aliyun",
        "aliyun-sls",
        "aliyun",
        "part_of",
        note="SLS 是阿里云的日志服务组件，计费与权限走云账号体系",
        weight=0.9,
    ),
    edge(
        "e-tencent-cls-part-of-tencent-cloud",
        "tencent-cls",
        "tencent-cloud",
        "part_of",
        note="CLS 是腾讯云的日志服务组件，与云内告警和对象存储同栈",
        weight=0.9,
    ),
    edge(
        "e-aliyun-sls-deq-sumo-logic",
        "aliyun-sls",
        "sumo-logic",
        "domestic_equivalent_of",
        note="国内公有云托管日志的对标：SLS 与云内产品打通更深，出境合规更省心",
        weight=0.65,
    ),
    edge(
        "e-tencent-cls-deq-sumo-logic",
        "tencent-cls",
        "sumo-logic",
        "domestic_equivalent_of",
        note="同为托管日志检索与告警；CLS 计费与控制台在国内，安全分析能力弱于 Sumo",
        weight=0.6,
    ),
    edge(
        "e-tencent-cls-alt-aliyun-sls",
        "tencent-cls",
        "aliyun-sls",
        "alternative_to",
        note="国内两朵云的日志服务对照：跟随主体资源所在云选，跨云使用不划算",
        weight=0.8,
    ),
    edge(
        "e-aliyun-sls-cuw-opentelemetry",
        "aliyun-sls",
        "opentelemetry",
        "commonly_used_with",
        note="以 OTel 协议接入可降低锁仓，采集端保留标准出口便于日后迁移",
        weight=0.55,
    ),
    # ——— obs-uptime 同层对照 ———
    edge(
        "e-openstatus-osalt-uptimerobot",
        "openstatus",
        "uptimerobot",
        "open_source_alternative_to",
        note="开源可自托管、数据自持 vs 免费额度大但托管封闭",
        weight=0.75,
    ),
    edge(
        "e-healthchecks-io-osalt-cronitor",
        "healthchecks-io",
        "cronitor",
        "open_source_alternative_to",
        note="同做定时任务心跳；Healthchecks 可自托管，Cronitor 另有拨测与状态页",
        weight=0.75,
    ),
    edge(
        "e-uptimerobot-alt-pingdom",
        "uptimerobot",
        "pingdom",
        "alternative_to",
        note="轻量免费档起步 vs 企业采购与全球节点覆盖",
        weight=0.7,
    ),
    edge(
        "e-checkly-alt-uptimerobot",
        "checkly",
        "uptimerobot",
        "alternative_to",
        note="浏览器级流程校验、监控即代码 vs 简单可达性拨测，成本与心智都更轻",
        weight=0.7,
    ),
    edge(
        "e-betterstack-alt-uptimerobot",
        "betterstack",
        "uptimerobot",
        "alternative_to",
        note="日志、告警与值班一体 vs 只做拨测与基础状态页",
        weight=0.7,
    ),
    edge(
        "e-instatus-alt-statuspage",
        "instatus",
        "statuspage",
        "alternative_to",
        note="轻快状态页、定价对订阅者规模更友好 vs Atlassian 生态与完整事故流程",
        weight=0.75,
    ),
    edge(
        "e-openstatus-alt-instatus",
        "openstatus",
        "instatus",
        "alternative_to",
        note="拨测与状态页合一且可自托管 vs 专注状态页、托管开箱即用",
        weight=0.65,
    ),
    edge(
        "e-uptimerobot-cuw-statuspage",
        "uptimerobot",
        "statuspage",
        "commonly_used_with",
        note="拨测负责发现，状态页负责对外沟通，两者分工不重叠",
        weight=0.6,
    ),
    edge(
        "e-checkly-iw-vercel",
        "checkly",
        "vercel",
        "integrates_with",
        note="常在 Vercel 部署后触发合成检查，把关键流程校验挂进发布流程",
        weight=0.6,
    ),
    edge(
        "e-checkly-iw-opentelemetry",
        "checkly",
        "opentelemetry",
        "integrates_with",
        note="合成检查可关联 OTel 链路，把外部失败下钻到内部调用",
        weight=0.55,
    ),
    edge(
        "e-checkly-cuw-sentry",
        "checkly",
        "sentry",
        "commonly_used_with",
        note="外部拨测发现「打不开」，Sentry 解释「为什么报错」，互为补充",
        weight=0.55,
    ),
    edge(
        "e-openstatus-bo-nextjs",
        "openstatus",
        "nextjs",
        "built_on",
        note="仪表盘与状态页以 Next.js 实现，自托管时需具备该栈的部署能力",
        weight=0.55,
    ),
    edge(
        "e-betterstack-cuw-grafana",
        "betterstack",
        "grafana",
        "commonly_used_with",
        note="托管告警与值班 vs 自建可视化中枢；常见做法是拨测告警外接、图表留在 Grafana",
        weight=0.5,
    ),
    # ——— msg-realtime 同层对照 ———
    edge(
        "e-ably-alt-pusher",
        "ably",
        "pusher",
        "alternative_to",
        note="交付保证与历史回放更强 vs 接入更简单、心智更轻",
        weight=0.8,
    ),
    edge(
        "e-centrifugo-osalt-pusher",
        "centrifugo",
        "pusher",
        "open_source_alternative_to",
        note="自托管实时消息服务器，省下按连接计费，代价是连接层运维",
        weight=0.75,
    ),
    edge(
        "e-socket-io-osalt-pusher",
        "socket-io",
        "pusher",
        "open_source_alternative_to",
        note="自建 Node.js 连接层 vs 托管频道服务；扩容与粘性会话需自理",
        weight=0.7,
    ),
    edge(
        "e-socket-io-alt-centrifugo",
        "socket-io",
        "centrifugo",
        "alternative_to",
        note="嵌入 Node 应用的库 vs 语言无关的独立服务器，后者更适合非 Node 后端",
        weight=0.7,
    ),
    edge(
        "e-liveblocks-alt-partykit",
        "liveblocks",
        "partykit",
        "alternative_to",
        note="现成协同组件与托管数据模型 vs 自己写边缘房间逻辑，自由度更高",
        weight=0.7,
    ),
    edge(
        "e-liveblocks-iw-yjs",
        "liveblocks",
        "yjs",
        "integrates_with",
        note="Liveblocks 可承载 Yjs 文档，把 CRDT 的服务端与持久化托管起来",
        weight=0.75,
    ),
    edge(
        "e-partykit-iw-yjs",
        "partykit",
        "yjs",
        "integrates_with",
        note="边缘房间常作为 Yjs 的同步服务端，适合自建协同白板与文档",
        weight=0.7,
    ),
    edge(
        "e-liveblocks-iw-nextjs",
        "liveblocks",
        "nextjs",
        "integrates_with",
        note="以 React Hook 与服务端鉴权接入 Next.js，是最常见的落地组合",
        weight=0.65,
    ),
    edge(
        "e-partykit-bo-cloudflare-workers",
        "partykit",
        "cloudflare-workers",
        "built_on",
        note="房间的有状态运行时建立在 Workers 与 Durable Objects 之上",
        weight=0.85,
    ),
    edge(
        "e-socket-io-iw-redis",
        "socket-io",
        "redis",
        "integrates_with",
        note="多实例部署靠 Redis 适配器广播事件，否则房间消息跨节点不通",
        weight=0.7,
    ),
    edge(
        "e-centrifugo-dep-redis",
        "centrifugo",
        "redis",
        "depends_on",
        note="多节点横向扩展与在线状态依赖 Redis 一类代理，单机模式可不用",
        weight=0.7,
    ),
    edge(
        "e-agora-alt-livekit",
        "agora",
        "livekit",
        "alternative_to",
        note="成熟商业 RTC 云、弱网与全球加速自带 vs 开源可自托管、成本与可控性更好",
        weight=0.8,
    ),
    edge(
        "e-agora-conversational-ai-po-agora",
        "agora-conversational-ai",
        "agora",
        "part_of",
        note="对话式 AI 能力是声网 RTC 之上的扩展，底层仍是同一套实时网络",
        weight=0.9,
    ),
    edge(
        "e-zego-alt-agora",
        "zego",
        "agora",
        "alternative_to",
        note="国内 RTC 双雄：即构上层场景组件更全，声网底层网络与出海口碑更久",
        weight=0.8,
    ),
    edge(
        "e-tencent-trtc-alt-agora",
        "tencent-trtc",
        "agora",
        "alternative_to",
        note="云内一体（直播/点播/IM 同栈）vs 独立厂商、跨云中立",
        weight=0.75,
    ),
    edge(
        "e-zego-deq-livekit",
        "zego",
        "livekit",
        "domestic_equivalent_of",
        note="国内 RTC SDK 与场景组件 vs 海外开源自托管方案，交付形态与计费完全不同",
        weight=0.6,
    ),
    edge(
        "e-tencent-trtc-deq-livekit",
        "tencent-trtc",
        "livekit",
        "domestic_equivalent_of",
        note="国内云托管 RTC vs 海外开源 RTC；国内节点与合规更省事，自控性更弱",
        weight=0.6,
    ),
    edge(
        "e-tencent-trtc-part-of-tencent-cloud",
        "tencent-trtc",
        "tencent-cloud",
        "part_of",
        note="TRTC 是腾讯云的实时音视频组件，与直播、点播、IM 共用云账号体系",
        weight=0.9,
    ),
    edge(
        "e-ably-cuw-nextjs",
        "ably",
        "nextjs",
        "commonly_used_with",
        note="前端订阅频道、服务端路由发布事件，是 Next.js 里加实时能力的常见做法",
        weight=0.5,
    ),
]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--overwrite", action="store_true")
    args = ap.parse_args()

    ENTRIES.mkdir(parents=True, exist_ok=True)
    VENDORS.mkdir(parents=True, exist_ok=True)
    EDGES.mkdir(parents=True, exist_ok=True)

    ids = [e["id"] for e in ENTRIES_DATA]
    assert len(ids) == len(set(ids)), "duplicate entry id"
    gids = [g["id"] for g in EDGES_DATA]
    assert len(gids) == len(set(gids)), "duplicate edge id"

    wrote_e = wrote_v = wrote_g = 0
    skipped_e = skipped_g = 0
    for e in ENTRIES_DATA:
        path = ENTRIES / f"{e['id']}.json"
        if path.exists() and not args.overwrite:
            skipped_e += 1
            print("skip entry exists", e["id"])
            continue
        save(path, e)
        wrote_e += 1
        print("entry", e["id"])

    for v in VENDORS_DATA:
        path = VENDORS / f"{v['id']}.json"
        if path.exists() and not args.overwrite:
            continue
        save(path, v)
        wrote_v += 1
        print("vendor", v["id"])

    known_new = set(ids)
    for g in EDGES_DATA:
        path = EDGES / f"{g['id']}.json"
        if path.exists() and not args.overwrite:
            continue
        frm_ok = (ENTRIES / f"{g['from']}.json").exists() or g["from"] in known_new
        to_ok = (ENTRIES / f"{g['to']}.json").exists() or g["to"] in known_new
        if not frm_ok:
            skipped_g += 1
            print("skip edge missing from", g["id"], g["from"])
            continue
        if not to_ok:
            skipped_g += 1
            print("skip edge missing to", g["id"], g["to"])
            continue
        save(path, g)
        wrote_g += 1
        print("edge", g["id"])

    print(
        f"done entries={wrote_e} (skipped {skipped_e}) "
        f"vendors={wrote_v} edges={wrote_g} (skipped {skipped_g})"
    )


if __name__ == "__main__":
    main()
