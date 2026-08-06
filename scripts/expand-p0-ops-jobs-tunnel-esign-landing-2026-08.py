#!/usr/bin/env python3
"""P0 上线路程五叶扩种（2026-08-07）。

遵守 content/README.md「扩种准入原则」：短名单级、最新可复核、各轴最佳，宁缺毋滥。

- ops-internal：Retool / Appsmith / Tooljet · 宜搭 / 简道云
- cloud-jobs：Temporal / BullMQ + 迁移 Inngest / Trigger.dev · 阿里云 Serverless 工作流
- net-tunnel：Tailscale / ngrok / Cloudflare Tunnel · frp
- sec-esign：DocuSign / Dropbox Sign · 法大大 / e签宝
- growth-landing：Webflow / Carrd + 迁移 Framer（国内无短名单级独立对标则不硬凑）

用法:
  python3 scripts/expand-p0-ops-jobs-tunnel-esign-landing-2026-08.py
  python3 scripts/expand-p0-ops-jobs-tunnel-esign-landing-2026-08.py --overwrite
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

CAT_OPS = "ops-internal"
CAT_JOBS = "cloud-jobs"
CAT_TUNNEL = "net-tunnel"
CAT_ESIGN = "sec-esign"
CAT_LAND = "growth-landing"

MIGRATE = {
    "inngest": CAT_JOBS,
    "trigger-dev": CAT_JOBS,
    "framer": CAT_LAND,
}

DOMESTIC_AVAIL = {
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
    assert 160 <= len(e["descriptionMd"]) <= 360, (e["id"], len(e["descriptionMd"]))
    assert 1 <= len(e["pitfalls"]) <= 3, e["id"]
    assert 3 <= len(e["tags"]) <= 5, e["id"]
    assert e.get("subcategory"), e["id"]
    assert e["id"] == e["id"].lower() and e["id"][0].isalpha(), e["id"]


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


# ——— 内部系统 / Admin ———
ENTRIES_DATA = [
    mk(
        CAT_OPS,
        "retool",
        "Retool",
        "internal-admin",
        "拖拽+JS 搭内部后台 · 连库/API 快 · 企服 admin 事实标准",
        "https://retool.com",
        "Retool 用可视化组件加少量 JS，快速搭建连接数据库与内部 API 的运营后台、审批与内部工具；权限、审计与资源权限对 B2B 企服内部系统友好。",
        "上线后要运营台、客服改数、财务导出、客户成功工具等「不可给公网的界面」，又不想从零写 React admin 时，它是事实标准短名单。",
        "按席位与资源定价随团队扩大变陡；交互特别深时仍会回到正式工程栈；中国大陆网络与采购路径需单独评估。",
        tags=["internal-tools", "low-code", "admin", "saas"],
        vendorId="retool-inc",
    ),
    mk(
        CAT_OPS,
        "appsmith",
        "Appsmith",
        "internal-admin",
        "开源 Retool 感内部应用 · 自托管许可友好 · 连任意 API",
        "https://www.appsmith.com",
        "Appsmith 是偏开源/可自托管的内部应用平台：拖拽 UI、绑定 SQL 与 REST/GraphQL，许可与数据驻留对不愿纯 SaaS 后台的团队友好。",
        "要自建运营后台、对接自有库表与内部 API，且预算或合规不愿上商业 Retool 时，与其同轴对标。",
        "复杂交互与精致视觉成本仍高；运维与版本升级需自担；云版与自托管功能差要对着文档核对。",
        tags=["internal-tools", "open-source", "admin", "self-host"],
        pricing={"model": "open-source"},
        vendorId="appsmith-inc",
        githubUrl="https://github.com/appsmithorg/appsmith",
    ),
    mk(
        CAT_OPS,
        "tooljet",
        "ToolJet",
        "internal-admin",
        "开源低代码内部工具 · 多数据源 · 工作流与权限",
        "https://www.tooljet.com",
        "ToolJet 面向工程与运营共建内部工具：可视化搭建、多数据源连接、简单审批流与 RBAC，社区版可自托管，商业版补协作与审计。",
        "需要比表格脚本更重、比自写完整 admin 更轻的中间层时，与 Appsmith/Retool 列入同一内部系统短名单。",
        "第三方集成与生态密度不及 Retool；超大团队对审计、SSO 与扩展的要求常把你推到企业版或自研。",
        tags=["internal-tools", "open-source", "admin", "low-code"],
        pricing={"model": "open-source"},
        vendorId="tooljet-inc",
        githubUrl="https://github.com/ToolJet/ToolJet",
    ),
    mk(
        CAT_OPS,
        "aliyun-yida",
        "宜搭",
        "internal-admin",
        "钉钉生态低代码应用 · 表单流程审批 · 国内内部系统常选",
        "https://www.aliyun.com/product/yida",
        "宜搭（钉钉/阿里云）以表单、流程与门户形式搭建内部应用，深度嵌钉钉组织、审批与消息，国内中小团队落地内部系统很快。",
        "组织已在钉钉，要考勤、采购、运营台账、轻审批而非纯代码 admin 时，是国内主选之一；选型时与简道云同轴比较。",
        "与欧美 Retool「连任意 SQL 写逻辑」轴不同；复杂界面与跨云身份集成碰到平台边界，迁出钉钉成本高。",
        tags=["internal-tools", "low-code", "dingtalk", "domestic"],
        region="domestic",
        availability=DOMESTIC_AVAIL,
        vendorId="alibaba-cloud",
        pitfalls=[
            "钉钉组织绑定深，迁出成本高",
            "复杂定制与非阿里数据源不如 Retool 灵活",
        ],
    ),
    mk(
        CAT_OPS,
        "jiandaoyun",
        "简道云",
        "internal-admin",
        "零代码业务应用 · 表单流水线 · 国内中小企业运维台",
        "https://www.jiandaoyun.com",
        "简道云以零/低代码表单与流程构建 CRM 轻模块、进销存、审批等业务系统，定位业务侧配置多于全职前端开发。",
        "国内中小团队技术人手不足、要快速上线业务台账与审批流时，与宜搭同级国内短名单；导入导出与消息通知较齐。",
        "复杂权限矩阵与深度 API 集成弱于工程级 low-code；业务膨胀后会逼近自研或 Retool 系。",
        tags=["internal-tools", "low-code", "forms", "domestic"],
        region="domestic",
        availability=DOMESTIC_AVAIL,
        vendorId="fanruan-jdy",
    ),
    # ——— 后台任务 ———
    mk(
        CAT_JOBS,
        "temporal",
        "Temporal",
        "durable-execution",
        "工作流 durable 执行 · 强一致重试/补偿 · 微服务长事务标杆",
        "https://temporal.io",
        "Temporal 以 durable execution 保证跨服务、长时间运行的工作流状态、重试与补偿语义，多语言 SDK 成熟，支持云与自托管。",
        "支付结算、多步审批、多微服务长事务，或需要严格可达性的 AI 多步编排时，它是应用侧 durable 底座的标杆。",
        "运维与概念门槛高于 Inngest/Trigger 类「几行函数」；纯短任务 cron 场景会过重。",
        tags=["jobs", "workflow", "durable", "open-source"],
        pricing={"model": "open-source"},
        vendorId="temporal-technologies",
        githubUrl="https://github.com/temporalio/temporal",
    ),
    mk(
        CAT_JOBS,
        "bullmq",
        "BullMQ",
        "queue-worker",
        "Redis 队列 Job · Node 生态默认 · 可观测/优先级/延迟任务",
        "https://docs.bullmq.io",
        "BullMQ 是基于 Redis 的 Node.js 任务队列：重试、延迟、优先级、流速与可观测组件生态成熟，是 Node 侧默认 worker 方案之一。",
        "已有 Redis，要跑邮件、转码、webhook 重试、批处理消费等进程内 worker，又不想引入完整 durable 平台时选用。",
        "可靠性边界取决于 Redis 与 worker 运维；跨语言协调与强一致长事务应看 Temporal 一类。",
        tags=["jobs", "queue", "redis", "node"],
        pricing={"model": "open-source"},
        vendorId="taskforce-sh",
        githubUrl="https://github.com/taskforcesh/bullmq",
    ),
    mk(
        CAT_JOBS,
        "aliyun-fnf",
        "阿里云 Serverless 工作流",
        "durable-execution",
        "云上编排函数/任务 · 长流程状态 · 国内云原生后台任务",
        "https://www.aliyun.com/product/fnf",
        "阿里云 Serverless 工作流（FnF）编排函数计算、消息与外部 HTTP 的有状态长流程，内置重试、可视化与云原生集成。",
        "业务已在阿里云，希望少管 Worker 完成支付后处理、媒体链路或多系统串联时，对标 Temporal/Inngest 的国内云选项。",
        "深度绑定阿里云账号与计费；跨云与复杂补偿建模表达力通常不如 Temporal。",
        tags=["jobs", "serverless", "workflow", "domestic"],
        region="domestic",
        availability={
            "chinaAccessible": True,
            "needsCompany": True,
            "needsIcp": False,
            "regions": ["CN"],
        },
        vendorId="alibaba-cloud",
        pricing={"model": "usage"},
    ),
    # ——— 隧道 / 零信任 ———
    mk(
        CAT_TUNNEL,
        "tailscale",
        "Tailscale",
        "zero-trust-vpn",
        "WireGuard mesh · 设备身份 · 零信任内网 · 开发机互联极快",
        "https://tailscale.com",
        "Tailscale 基于 WireGuard 组成零信任 mesh 网络：设备身份登录、ACL、出口节点，把分散的开发机与环境连成一张安全内网。",
        "多地开发机、家庭 lab、安全访问预发环境，又不想维护传统 VPN 中枢与证书地狱时，它是默认体验首选。",
        "规模与 IdP 集成会进企业档；中国大陆访问质量与企业合规策略需要实测与法务确认。",
        tags=["tunnel", "vpn", "zero-trust", "wireguard"],
        vendorId="tailscale-inc",
    ),
    mk(
        CAT_TUNNEL,
        "ngrok",
        "ngrok",
        "public-tunnel",
        "本地端口公网隧道 · webhook 调试 · 临时 HTTPS 演示利器",
        "https://ngrok.com",
        "ngrok 把本地端口暴露成公网 HTTPS 或 TCP 隧道，自带域名/鉴权与流量观测，是 webhook 调试与临时演示的事实工具。",
        "本地开发接第三方回调、真机访问、给客户短时演示内网服务时用；长期生产入口要另做架构。",
        "免费层域名与带宽限制明显；生产长期暴露应换稳定入口或 Cloudflare Tunnel 等可控方案。",
        tags=["tunnel", "webhook", "devtool", "https"],
        vendorId="ngrok-inc",
    ),
    mk(
        CAT_TUNNEL,
        "cloudflare-tunnel",
        "Cloudflare Tunnel",
        "public-tunnel",
        "出向连接入 CF 边缘 · 免开入站端口 · 接 Access 零信任",
        "https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/",
        "Cloudflare Tunnel（cloudflared）从内网主动连到 Cloudflare 边缘，无需公网 IP 或开入站端口，并可挂 Access 做身份访问控制。",
        "已有 Cloudflare 域名，要把家宽、机房或 K8s 服务安全挂到公网又不直接暴露源站时选用。",
        "深度依赖 Cloudflare 控制面；非 HTTP 与复杂四层流量要核对协议支持与定价。",
        tags=["tunnel", "cloudflare", "zero-trust", "edge"],
        vendorId="cloudflare-inc",
        pricing={"model": "freemium"},
    ),
    mk(
        CAT_TUNNEL,
        "frp",
        "frp",
        "public-tunnel",
        "开源自建内网穿透 · 国内工程常驻方案 · 要自备公网 VPS",
        "https://github.com/fatedier/frp",
        "frp 是客户端-服务端架构的开源内网穿透：HTTP/TCP/UDP 透出，你自备带公网 IP 的中继机即可运营，社区在国内很常用。",
        "国内工程要可控、低现金成本把内网服务暴露公网，并愿意自己运维中继与证书时，它是常见开源默认。",
        "安全加固、带宽与证书全靠自运维；没有商业 SaaS 的身份托管与 SLA，生产必须自己做监控。",
        tags=["tunnel", "open-source", "self-host", "domestic"],
        region="domestic",
        availability=DOMESTIC_AVAIL,
        pricing={"model": "open-source"},
        githubUrl="https://github.com/fatedier/frp",
        vendorId="fatedier-frp",
    ),
    # ——— 电子签 ———
    mk(
        CAT_ESIGN,
        "docusign",
        "DocuSign",
        "e-signature",
        "全球电子签名事实标准 · 模板/API/合规 · B2B 合同默认",
        "https://www.docusign.com",
        "DocuSign 覆盖模板签署、信封流程、开放 API 与多司法辖区合规证据链，是跨境外企电子签事实参考之一，生态集成与模板市场极广。",
        "出海 SaaS 要客户远程签 NDA、主协议或附件，法务要求审计与证据链时，作为主轴对标。",
        "席位与信封单价高；中国大陆法律效力与信创/国密场景应改看法大大、e签宝等；采购要算法务模板量。",
        tags=["esign", "contract", "compliance", "b2b"],
        vendorId="docusign-inc",
    ),
    mk(
        CAT_ESIGN,
        "dropbox-sign",
        "Dropbox Sign",
        "e-signature",
        "原 HelloSign · 简洁签署流 · 开发者 API 友好",
        "https://sign.dropbox.com",
        "Dropbox Sign（原 HelloSign）强调简洁的签署体验与嵌入式签约，API/SDK 对「产品内点签」集成友好，文档清晰。",
        "要在 App 内完成协议勾选签署、团队已用 Dropbox 生态、预算低于 DocuSign 企业套件时考虑。",
        "超大企业复杂多方法务流程、高级合规套件广度通常不及 DocuSign 全家桶。",
        tags=["esign", "api", "contract", "saas"],
        vendorId="dropbox-inc",
    ),
    mk(
        CAT_ESIGN,
        "fadada",
        "法大大",
        "e-signature",
        "国内电子签与合同 · 实名/司法 · B2B 签约主选之一",
        "https://www.fadada.com",
        "法大大提供实名认证、电子签章、合同生命周期管理与开放平台，服务国内商事主体电子签约，开放能力适合嵌入业务与销售流程。",
        "面向中国大陆客户签销售合同、劳务授权与隐私同意书，需要可核验实名与司法存证时列入国内核心短名单内。",
        "跨境多司法体系覆盖弱于 DocuSign；接入与认证链路套餐差大，采购前要跑通样例并看法务模板。",
        tags=["esign", "contract", "domestic", "compliance"],
        region="domestic",
        availability={
            "chinaAccessible": True,
            "needsCompany": True,
            "needsIcp": False,
            "regions": ["CN"],
        },
        vendorId="fadada-inc",
    ),
    mk(
        CAT_ESIGN,
        "esignbao",
        "e签宝",
        "e-signature",
        "国内电子签平台 · 公有云/混合 · 政企与互联网常用",
        "https://www.esign.cn",
        "e签宝覆盖个人与企业实名、签署、存证与开放 API，在政企与互联网合同电子化中渗透率高，产品线从公有云到专有部署都覆盖。",
        "国内合同电子化招标或供应商比选、与法大大同轴比较产品能力与价格时使用；法务常会同时看两家。",
        "公有云与专有云产品线多会拉长选型；默认跨境签约仍优先看 DocuSign 系与海外合规、证据链叙述。",
        tags=["esign", "contract", "domestic", "compliance"],
        region="domestic",
        availability={
            "chinaAccessible": True,
            "needsCompany": True,
            "needsIcp": False,
            "regions": ["CN"],
        },
        vendorId="esignbao-inc",
    ),
    # ——— 营销站 ———
    mk(
        CAT_LAND,
        "webflow",
        "Webflow",
        "marketing-site",
        "可视化设计+CMS+托管 · 营销站专业级 · 无代码上限高",
        "https://webflow.com",
        "Webflow 把版式设计、响应式、CMS 与托管合为一体，可到设计稿级精度发布营销与内容站，显著减少营销站前端开发工期。",
        "品牌官网、定价页、内容站需要设计师主导上线、又不想自建 Next 营销站时，它是专业级短名单头部首选。",
        "复杂产品逻辑与国内备案合规仍要工程补齐；席位与托管档位费用不低，协作与表单席位要算清楚。",
        tags=["marketing", "no-code", "cms", "website"],
        vendorId="webflow-inc",
    ),
    mk(
        CAT_LAND,
        "carrd",
        "Carrd",
        "marketing-site",
        "极简单页落地 · 定价低 · Solo/验证想法最快",
        "https://carrd.co",
        "Carrd 专注用极低学习成本搭单页或少页落地与简单表单，特别适合个人 Maker 与极早期产品快速验证上线。",
        "MVP 需要当天上线 waitlist、预告页或极简定价页、预算接近零时，它是最低摩擦选项之一。",
        "多页 CMS、协作与复杂动效远弱于 Webflow/Framer；品牌级官网很快顶到天花板，届时需迁移。",
        tags=["marketing", "landing", "no-code", "mvp"],
        vendorId="carrd-inc",
        pricing={"model": "subscription"},
    ),
]

# 厂商（alibaba-cloud 可能已存在，脚本幂等跳过）
VENDORS_DATA = [
    vendor("retool-inc", "Retool", url="https://retool.com"),
    vendor("appsmith-inc", "Appsmith", url="https://www.appsmith.com"),
    vendor("tooljet-inc", "ToolJet", url="https://www.tooljet.com"),
    vendor("fanruan-jdy", "帆软简道云", region="domestic", url="https://www.jiandaoyun.com"),
    vendor("temporal-technologies", "Temporal Technologies", url="https://temporal.io"),
    vendor("taskforce-sh", "Taskforce.sh", url="https://taskforce.sh"),
    vendor("tailscale-inc", "Tailscale", url="https://tailscale.com"),
    vendor("ngrok-inc", "ngrok", url="https://ngrok.com"),
    vendor("fatedier-frp", "frp", region="domestic", url="https://github.com/fatedier/frp"),
    vendor("docusign-inc", "DocuSign", url="https://www.docusign.com"),
    vendor("fadada-inc", "法大大", region="domestic", url="https://www.fadada.com"),
    vendor("esignbao-inc", "e签宝", region="domestic", url="https://www.esign.cn"),
    vendor("webflow-inc", "Webflow", url="https://webflow.com"),
    vendor("carrd-inc", "Carrd", url="https://carrd.co"),
    # alibaba-cloud / cloudflare-inc / dropbox-inc 多半已有
    vendor("alibaba-cloud", "阿里云", region="domestic", url="https://www.aliyun.com"),
    vendor("cloudflare-inc", "Cloudflare", url="https://www.cloudflare.com"),
    vendor("dropbox-inc", "Dropbox", url="https://www.dropbox.com"),
]

EDGES_DATA = [
    # ops
    edge(
        "e-appsmith-oss-retool",
        "appsmith",
        "retool",
        "open_source_alternative_to",
        note="可自托管开源内部工具 vs 商业 Retool",
        weight=0.8,
    ),
    edge(
        "e-tooljet-oss-retool",
        "tooljet",
        "retool",
        "open_source_alternative_to",
        note="另一开源内部工具短名单",
        weight=0.75,
    ),
    edge(
        "e-appsmith-alt-tooljet",
        "appsmith",
        "tooljet",
        "alternative_to",
        note="开源内部工具同轴",
        weight=0.75,
    ),
    edge(
        "e-yida-domestic-retool",
        "aliyun-yida",
        "retool",
        "domestic_equivalent_of",
        note="钉钉低代码内部应用 vs 工程向 Retool；可比场景有限",
        weight=0.55,
    ),
    edge(
        "e-jiandaoyun-domestic-retool",
        "jiandaoyun",
        "retool",
        "domestic_equivalent_of",
        note="表单零代码业务台 vs 开发者后台构建器",
        weight=0.5,
    ),
    edge(
        "e-yida-alt-jiandaoyun",
        "aliyun-yida",
        "jiandaoyun",
        "alternative_to",
        note="国内低代码内部系统同轴",
        weight=0.7,
    ),
    edge(
        "e-retool-with-postgres",
        "retool",
        "postgresql",
        "commonly_used_with",
        note="常直连业务 Postgres 做运营台",
        weight=0.65,
    ),
    # jobs
    edge(
        "e-inngest-alt-temporal",
        "inngest",
        "temporal",
        "alternative_to",
        note="事件 step 函数 vs 完整 durable workflow 引擎",
        weight=0.7,
    ),
    edge(
        "e-trigger-dev-alt-inngest",
        "trigger-dev",
        "inngest",
        "alternative_to",
        note="TS 后台 Job 平台同轴",
        weight=0.8,
    ),
    edge(
        "e-trigger-dev-alt-temporal",
        "trigger-dev",
        "temporal",
        "alternative_to",
        note="应用 Job 平台 vs 强一致工作流底座",
        weight=0.65,
    ),
    edge(
        "e-bullmq-alt-inngest",
        "bullmq",
        "inngest",
        "alternative_to",
        note="自管 Redis 队列 vs 托管 durable 函数",
        weight=0.7,
    ),
    edge(
        "e-bullmq-depends-redis",
        "bullmq",
        "redis",
        "depends_on",
        note="队列状态与后端在 Redis",
        weight=0.9,
    ),
    edge(
        "e-aliyun-fnf-domestic-temporal",
        "aliyun-fnf",
        "temporal",
        "domestic_equivalent_of",
        note="阿里云有状态工作流 vs Temporal 耐久执行",
        weight=0.55,
    ),
    # tunnel（Airflow↔Inngest 已有 e-apache-airflow-alt-inngest，不重复对称边）
    # tunnel
    edge(
        "e-ngrok-alt-cloudflare-tunnel",
        "ngrok",
        "cloudflare-tunnel",
        "alternative_to",
        note="本地公网隧道：SaaS DX vs CF 边缘出站",
        weight=0.75,
    ),
    edge(
        "e-tailscale-alt-ngrok",
        "tailscale",
        "ngrok",
        "alternative_to",
        note="私网 mesh 身份接入 vs 公网临时暴露；场景常不同",
        weight=0.45,
    ),
    edge(
        "e-frp-oss-ngrok",
        "frp",
        "ngrok",
        "open_source_alternative_to",
        note="自建穿透 vs 托管隧道",
        weight=0.7,
    ),
    edge(
        "e-frp-domestic-cloudflare-tunnel",
        "frp",
        "cloudflare-tunnel",
        "domestic_equivalent_of",
        note="自建中继穿透 vs CF Tunnel（非合规等价，工程路径相近）",
        weight=0.5,
    ),
    edge(
        "e-cloudflare-tunnel-with-cdn",
        "cloudflare-tunnel",
        "cloudflare-cdn",
        "commonly_used_with",
        note="Tunnel 源站常挂同一 CF zone",
        weight=0.7,
    ),
    # esign
    edge(
        "e-dropbox-sign-alt-docusign",
        "dropbox-sign",
        "docusign",
        "alternative_to",
        note="轻量签署 API vs 企业合同套件",
        weight=0.75,
    ),
    edge(
        "e-fadada-domestic-docusign",
        "fadada",
        "docusign",
        "domestic_equivalent_of",
        note="中国大陆电子签 vs 跨境 DocuSign",
        weight=0.7,
    ),
    edge(
        "e-esignbao-domestic-docusign",
        "esignbao",
        "docusign",
        "domestic_equivalent_of",
        note="国内电子签主选之一",
        weight=0.7,
    ),
    edge(
        "e-fadada-alt-esignbao",
        "fadada",
        "esignbao",
        "alternative_to",
        note="国内电子签同轴短名单",
        weight=0.8,
    ),
    # landing
    edge(
        "e-framer-alt-webflow",
        "framer",
        "webflow",
        "alternative_to",
        note="设计动画向营销站 vs CMS/设计系统向上限",
        weight=0.85,
    ),
    edge(
        "e-carrd-alt-webflow",
        "carrd",
        "webflow",
        "alternative_to",
        note="极简单页 vs 专业营销站平台",
        weight=0.6,
    ),
    edge(
        "e-carrd-alt-framer",
        "carrd",
        "framer",
        "alternative_to",
        note="低成本单页 vs 高定动画站点",
        weight=0.55,
    ),
]


def migrate_entries() -> None:
    for eid, cat in MIGRATE.items():
        path = ENTRIES / f"{eid}.json"
        if not path.exists():
            print("warn: missing migrate target", eid)
            continue
        data = json.loads(path.read_text(encoding="utf-8"))
        old = data.get("category")
        data["category"] = cat
        data["lastReviewed"] = REVIEWED
        if eid == "framer":
            data["subcategory"] = "marketing-site"
            tags = list(data.get("tags") or [])
            for t in ("design", "website", "marketing", "no-code"):
                if t not in tags:
                    tags.append(t)
            data["tags"] = tags[:5]
            if len(data["tags"]) < 3:
                data["tags"] = ["marketing", "website", "design"]
        elif eid in ("inngest", "trigger-dev"):
            data["subcategory"] = "durable-jobs"
        save(path, data)
        print(f"migrated {eid} {old} → {cat}")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--overwrite", action="store_true")
    args = ap.parse_args()

    ENTRIES.mkdir(parents=True, exist_ok=True)
    VENDORS.mkdir(parents=True, exist_ok=True)
    EDGES.mkdir(parents=True, exist_ok=True)

    issues: list[str] = []
    for e in ENTRIES_DATA:
        try:
            validate_entry(e)
        except AssertionError as err:
            issues.append(str(err))
    if issues:
        for i in issues:
            print("INVALID", i)
        raise SystemExit(f"{len(issues)} entry validation failures")

    ids = [e["id"] for e in ENTRIES_DATA]
    assert len(ids) == len(set(ids)), "duplicate entry id"
    gids = [g["id"] for g in EDGES_DATA]
    assert len(gids) == len(set(gids)), "duplicate edge id"

    wrote_e = wrote_v = wrote_g = 0
    skipped_e = skipped_v = skipped_g = 0
    for e in ENTRIES_DATA:
        path = ENTRIES / f"{e['id']}.json"
        if path.exists() and not args.overwrite:
            skipped_e += 1
            print("skip entry exists", e["id"])
            continue
        save(path, e)
        wrote_e += 1
        print("entry", e["category"], e["id"])

    for v in VENDORS_DATA:
        path = VENDORS / f"{v['id']}.json"
        if path.exists() and not args.overwrite:
            skipped_v += 1
            continue
        save(path, v)
        wrote_v += 1
        print("vendor", v["id"])

    known_new = {x["id"] for x in ENTRIES_DATA}
    # also known via migrate
    known_new |= set(MIGRATE.keys())
    for g in EDGES_DATA:
        path = EDGES / f"{g['id']}.json"
        if path.exists() and not args.overwrite:
            skipped_g += 1
            continue
        # avoid dual alt with existing e-apache-airflow-alt-inngest → inngest-alt-airflow same pair?
        # e-inngest-alt-airflow-jobs is reverse of existing - SKIP if would create symmetric dupe
        frm_ok = (ENTRIES / f"{g['from']}.json").exists() or g["from"] in known_new
        to_ok = (ENTRIES / f"{g['to']}.json").exists() or g["to"] in known_new
        if not frm_ok:
            print("skip edge missing from", g["id"], g["from"])
            continue
        if not to_ok:
            print("skip edge missing to", g["id"], g["to"])
            continue
        save(path, g)
        wrote_g += 1
        print("edge", g["id"])

    migrate_entries()

    print(
        f"done entries={wrote_e}(skip {skipped_e}) "
        f"vendors={wrote_v}(skip {skipped_v}) edges={wrote_g}(skip {skipped_g})"
    )
    print(
        f"leaves: {CAT_OPS} {CAT_JOBS} {CAT_TUNNEL} {CAT_ESIGN} {CAT_LAND}; "
        f"migrate {list(MIGRATE.keys())}"
    )


if __name__ == "__main__":
    main()
