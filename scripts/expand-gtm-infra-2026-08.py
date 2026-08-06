#!/usr/bin/env python3
"""上线侧 GTM / 运营基建补叶扩种（2026-08-06）。

遵守 content/README.md「扩种准入原则」：短名单级、最新可复核、各轴最佳，宁缺毋滥。

叶与锚点（每轴一位，非库存）：
- growth-social：Postiz / Mixpost（开源）+ Buffer + Typefully + Later + Publer + Ayrshare + Hootsuite
- growth-forms：Tally / Typeform / Fillout / Formbricks
- growth-feedback：Canny / Featurebase / Fider / Productboard
- growth-affiliate：Rewardful / Tolt / FirstPromoter / Dub
- cicd-automation：Zapier / Make / Activepieces / Pipedream（+ 迁 n8n）
- collab-scheduling：Cal.com / Calendly / SavvyCal
- msg-orchestration：Novu / Knock / Courier

用法:
  python3 scripts/expand-gtm-infra-2026-08.py
  python3 scripts/expand-gtm-infra-2026-08.py --overwrite
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
REVIEWED = "2026-08-06"

CAT_SOCIAL = "growth-social"
CAT_FORMS = "growth-forms"
CAT_FEEDBACK = "growth-feedback"
CAT_AFF = "growth-affiliate"
CAT_AUTO = "cicd-automation"
CAT_SCHED = "collab-scheduling"
CAT_ORCH = "msg-orchestration"


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
    # 批量装载后再统一 assert，方便一次列出全部长度问题
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


# ——— 社媒排期 ———
SOCIAL = [
    mk(
        CAT_SOCIAL,
        "postiz",
        "Postiz",
        "social-scheduler",
        "202x 开源社媒排期首选动量 · 30+ 平台 · Agent/API/n8n",
        "https://postiz.com",
        "Postiz 是当前开源社媒排期里动量最大的一档（AGPL）：可云可自托管，覆盖主流与新兴网络，提供日历、Public API、MCP/CLI 与 n8n 节点，方便用 Agent 或工作流起草后定时多发。",
        "要开源/自托管且跟 AI Agent 自动化同栈、或对照 Buffer/Hootsuite 找可自控替代时优先；若更想要经典 Buffer UI 与 Laravel 栈买断，对照 Mixpost。",
        "AGPL 与平台 OAuth 政策需团队评估；自托管要管账号绑定、密钥与升级，云套餐按团队规模计价。",
        vendorId="gitroom-inc",
        githubUrl="https://github.com/gitroomhq/postiz-app",
        pricing={"model": "open-source", "currency": "USD", "notes": "云版订阅；自托管免费但需运维"},
        tags=["social", "scheduling", "open-source", "self-hosted"],
        pitfalls=[
            "AGPL 许可对嵌入闭源产品有约束，商用分发前先看法务。",
            "各社交平台 API 政策与配额会变，连接器健康度要持续关注。",
        ],
    ),
    mk(
        CAT_SOCIAL,
        "mixpost",
        "Mixpost",
        "social-scheduler",
        "自托管 Buffer 体验 · Laravel 栈 · Lite 开源 / Pro 买断",
        "https://mixpost.app",
        "Mixpost 是自托管向的社媒排期控制台，界面与工作流接近经典 Buffer：队列、日历、多账号发布。Lite 开源可自用，Pro/Enterprise 一次买断高级渠道与能力，栈为 Laravel，适合要「自己的 Buffer」又不愿订阅云的团队。",
        "运维能接受 PHP/Laravel 自托管、想要成熟 Buffer 感而不是 Agent 向产品时与 Postiz 对照；要 AI Agent/MCP 与更广新平台优先 Postiz。",
        "Pro 渠道与功能在商业许可；自托管需管升级、存储与各平台 OAuth，Lite 渠道覆盖窄于 Pro。",
        vendorId="inovector-inc",
        githubUrl="https://github.com/inovector/mixpost",
        pricing={"model": "open-source", "currency": "USD", "notes": "Lite 开源；Pro/Enterprise 一次买断（以官网为准）"},
        tags=["social", "scheduling", "open-source", "self-hosted"],
        pitfalls=[
            "Lite 渠道较少，Instagram/TikTok 等常需 Pro。",
            "自托管运维与密钥轮换由团队自担。",
        ],
    ),
    mk(
        CAT_SOCIAL,
        "buffer",
        "Buffer",
        "social-scheduler",
        "经典轻量社媒排期默认 · 小团队零学习 · 不做重型套件",
        "https://buffer.com",
        "Buffer 是经典的社媒内容日历：把草稿排进队列、多账号定时发布，并附带基础互动与表现分析，界面克制，适合小团队建立固定发帖节奏。",
        "独立开发者或小运营组需要「够用、别太重」的排期工具时；企业级审批流、社群客服收件箱请看 Hootsuite 或专用社媒套件。",
        "深度社群互动与大型团队权限管理偏弱；高级分析与更多渠道在付费档。",
        vendorId="buffer-inc",
        pricing={"model": "freemium", "currency": "USD"},
        maturity="mature",
        tags=["social", "scheduling", "saas", "creators"],
        pitfalls=[
            "大型团队权限与审批能力弱于企业套件。",
            "进阶分析与部分渠道在更高付费档。",
        ],
    ),
    mk(
        CAT_SOCIAL,
        "typefully",
        "Typefully",
        "social-scheduler",
        "偏 X/LinkedIn 的写作台 · 线程排期强 · 创作者节奏向",
        "https://typefully.com",
        "Typefully 把长文线程写作、协作编辑与定时发布做在同一编辑器里，尤其擅长 X（Twitter）串文与 LinkedIn 节奏运营，带草稿协作与发布后表现回顾。",
        "以 X / LinkedIn 个人品牌或内容账号为主战场、写长线程多过管全网矩阵时优先；要 Instagram 视觉日历或 20+ 平台矩阵请看 Later / Postiz。",
        "渠道覆盖面窄于全能排期工具；高级协作与分析随档位放开。",
        vendorId="typefully-inc",
        pricing={"model": "freemium", "currency": "USD"},
        tags=["social", "twitter", "writing", "scheduling"],
        pitfalls=[
            "主打少数文字渠道，视觉向平台深度弱。",
            "团队席位与高级分析随订阅档位限制。",
        ],
    ),
    mk(
        CAT_SOCIAL,
        "publer",
        "Publer",
        "social-scheduler",
        "批量与内容库向 · 多账号日历 · 中小矩阵常用",
        "https://publer.com",
        "Publer 面向多账号矩阵运营：提供内容库、批量上传、可视化日历与基础回收分析，适合一个运营人同时管多品牌或多市场账号。",
        "小微团队账号数上来、需要批量重排与素材库复用时评估；开发者想用 API 灌内容可看 Ayrshare，开源自托管看 Postiz。",
        "企业级工作流与深度聆听弱于 Hootsuite 级套件；免费档渠道与席位紧。",
        vendorId="publer-inc",
        pricing={"model": "freemium", "currency": "USD"},
        tags=["social", "scheduling", "bulk", "saas"],
        pitfalls=[
            "企业级审批与社群收件箱能力有限。",
            "免费额度的账号数与历史数据偏紧。",
        ],
    ),
    mk(
        CAT_SOCIAL,
        "ayrshare",
        "Ayrshare",
        "social-api",
        "开发者向社媒发帖 API · 多平台一套接口 · 嵌产品内",
        "https://www.ayrshare.com",
        "Ayrshare 提供统一 REST API，让应用替用户绑定并发布到多个社交网络，覆盖排期、媒体上传与基础历史查询，定位是「嵌入你自己的产品」，不是运营人员用的日历 UI。",
        "SaaS / 白标要给客户「连接账号 → 发帖」能力、又不想逐家对接 OAuth 时采用；自用内容日历请用 Buffer / Postiz 一类产品。",
        "按消息与账号档位计费，峰值成本会随活跃客户上涨；各平台政策变更会影响可用能力。",
        vendorId="ayrshare-inc",
        pricing={"model": "subscription", "currency": "USD"},
        tags=["social", "api", "developer", "scheduling"],
        pitfalls=[
            "计费跟消息量与连接账号走，流量上来后要盯账单。",
            "不是给运营同学的日历产品，缺可视化内容库体验。",
        ],
    ),
    mk(
        CAT_SOCIAL,
        "hootsuite",
        "Hootsuite",
        "social-suite",
        "企业级社媒套件 · 收件箱/审批/报表重 · 采购周期长",
        "https://www.hootsuite.com",
        "Hootsuite 是面向中大型团队的社媒运营套件：统一收件箱、发布审批、权限分级与跨渠道报表，往往以组织采购与落地实施方式引入，而不是个人作者工具。",
        "多部门共管品牌账号、需要审批留痕、合规与培训支持时评估；Indie 个人号用它过重，优先 Buffer / Typefully / Postiz。",
        "价格与席位体系偏企业；上手与配置成本高于简洁排期工具。",
        vendorId="hootsuite-inc",
        pricing={"model": "subscription", "currency": "USD"},
        maturity="mature",
        tags=["social", "enterprise", "suite", "scheduling"],
        pitfalls=[
            "席位与模块打包报价，中小团队性价比通常不理想。",
            "配置与培训成本显著高于轻量排期工具。",
        ],
    ),
    mk(
        CAT_SOCIAL,
        "later-social",
        "Later",
        "social-scheduler",
        "视觉优先 IG/TikTok 日历 · 网红连结带货向",
        "https://later.com",
        "Later 以视觉内容日历著称，深度覆盖 Instagram、TikTok 等图像/短视频渠道，并延展到链路、创作者协作与基础电商导流，适合视觉营销团队按网格规划上线节奏。",
        "品牌或创作者以 IG / TikTok 视觉为主、需要「排版感」日历时评估；以 X 长线程或开发者 API 发布为主请换 Typefully / Ayrshare。",
        "偏视觉渠道，文字向平台深度一般；高档位功能与链接工具常需加购。",
        vendorId="later-inc",
        pricing={"model": "freemium", "currency": "USD"},
        tags=["social", "instagram", "tiktok", "scheduling"],
        pitfalls=[
            "文字向平台（如深度线程写作）体验不及专用工具。",
            "链接库与分析增强功能常在更高档位。",
        ],
    ),
    mk(
        CAT_SOCIAL,
        "metricool",
        "Metricool",
        "social-analytics",
        "分析+排期一体 · 多网络面板 · 中小品牌性价比向",
        "https://metricool.com",
        "Metricool 把多社交网络的表现分析与发布排期放在同一面板，并覆盖 Ads / 竞品粗看等运营视角，常见于中小品牌与代理用一套工具兼顾「发」与「看」。",
        "账号数量中等、既要发帖又要周报级复盘、预算有限时评估；只要极简排期用 Buffer，只要 API 灌内容用 Ayrshare。",
        "企业级治理与深社群客服弱；数据与 Ads 口径以各平台导出为准，跨工具对比需注意归因。",
        vendorId="metricool-inc",
        pricing={"model": "freemium", "currency": "EUR"},
        tags=["social", "analytics", "scheduling", "saas"],
        pitfalls=[
            "跨平台指标口径依赖各家官方数据，竞品估算别当精确 KPI。",
            "大型组织权限与审批能力仍弱于企业套件。",
        ],
    ),
]

# ——— 表单 / 问卷 ———
FORMS = [
    mk(
        CAT_FORMS,
        "typeform",
        "Typeform",
        "form-builder",
        "对话式表单体验强 · 品牌感好 · 转化页问卷向",
        "https://www.typeform.com",
        "Typeform 以一题一屏的对话式表单闻名，强调完成率与品牌呈现，适合调研、线索收集与轻量 quiz，生态连接 Zapier/CRM 成熟。",
        "对外品牌问卷、强调完成体验与分享传播的表单时采用；内部工具表单或要无限免费提交看 Tally，产品内嵌入调研也可评 Formbricks。",
        "免费/低档回复量有限；复杂条件逻辑与数据处理成本随规模上升。",
        vendorId="typeform-inc",
        pricing={"model": "freemium", "currency": "USD"},
        maturity="mature",
        tags=["forms", "survey", "lead-gen", "saas"],
        pitfalls=[
            "回复额度紧，活动高峰容易撞墙。",
            "复杂分支与导出能力随档位解锁。",
        ],
    ),
    mk(
        CAT_FORMS,
        "tally",
        "Tally",
        "form-builder",
        "Notion 感免费表单 · 逻辑块够用 · Indie 默认候选",
        "https://tally.so",
        "Tally 提供接近文档编辑的表单搭建体验，免费档对个人与小团队相当慷慨，支持条件逻辑、文件上传与常见通知集成，是 indie 收集 waitlist、反馈与报名表的常见默认项。",
        "需要快速上线名单表、不付费也能扛一定提交量时优先；要极致对话体验与企业品牌管控再评 Typeform。",
        "超大型合规审计与复杂工作流编排弱于企业表单套件；重度计算字段要实测。",
        vendorId="tally-inc",
        pricing={"model": "freemium", "currency": "USD"},
        tags=["forms", "survey", "indie", "saas"],
        pitfalls=[
            "企业级权限、审计与专属支持弱。",
            "极复杂评分/配额逻辑不如专用调研平台。",
        ],
    ),
    mk(
        CAT_FORMS,
        "fillout",
        "Fillout",
        "form-builder",
        "现代产品向表单 · 计算/支付/调度块强 · 嵌入友好",
        "https://www.fillout.com",
        "Fillout 定位为产品与运营可快速组装的现代表单：计算字段、支付、预约、PDF 映射与嵌入组件较齐全，适合把表单当成轻量「小应用」而不是静态问卷。",
        "表单里要收付款、预约或生成 PDF/报价这类多步流程时评估；只要简单 waitlist 用 Tally 更轻。",
        "功能面宽，模板与权限要自己克制，否则维护成本接近半个 internal app。",
        vendorId="fillout-inc",
        pricing={"model": "freemium", "currency": "USD"},
        tags=["forms", "workflow", "payments", "saas"],
        pitfalls=[
            "功能多，复杂表单会变成难维护的半成品应用。",
            "支付与高级集成多在付费档。",
        ],
    ),
    mk(
        CAT_FORMS,
        "formbricks",
        "Formbricks",
        "in-app-survey",
        "开源产品内调研 · 触发式问卷 · 可自托管隐私友好",
        "https://formbricks.com",
        "Formbricks 是开源的产品内调研与体验收集工具，可按事件/页面触发问卷，支持云托管与自托管，强调把反馈嵌进产品路径而不是外链问卷页。",
        "需要 NPS/PMF/功能反馈贴在产品会话里、并在意数据驻留时评估；对外营销落地页表单用 Tally/Typeform 更合适。",
        "外向品牌调研与视觉模板不如 Typeform；自托管仍要做更新与存储运维。",
        vendorId="formbricks-inc",
        githubUrl="https://github.com/formbricks/formbricks",
        pricing={"model": "open-source", "currency": "USD", "notes": "云托管订阅；自托管开源"},
        tags=["forms", "survey", "open-source", "product"],
        pitfalls=[
            "强项在产品内触发，不适合作为完整对外营销表单站。",
            "自托管需维护版本与用户隐私合规配置。",
        ],
    ),
]

# ——— 反馈 / 路线图 ———
FEEDBACK = [
    mk(
        CAT_FEEDBACK,
        "canny",
        "Canny",
        "feature-voting",
        "功能投票与路线图经典位 · 客户声音汇入 · 公开板",
        "https://canny.io",
        "Canny 把用户提交的功能请求做成可投票看板，并关联更新状态与 changelog，帮助产品团队把「客户声音 → 优先级 → 已上线公告」串在同一处。",
        "SaaS 需要公开/半公开路线图与投票、让客户参与优先级时评估；纯内部需求池也可以用，但会弱化社群感。",
        "深度产品管理（机会评分、目标树）不如 Productboard；进阶席位与多板块按订阅收费。",
        vendorId="canny-inc",
        pricing={"model": "subscription", "currency": "USD"},
        maturity="mature",
        tags=["feedback", "roadmap", "changelog", "saas"],
        pitfalls=[
            "投票会被活跃少数用户带偏，需人工二次判断优先级。",
            "企业级产品组合分析能力有限。",
        ],
    ),
    mk(
        CAT_FEEDBACK,
        "featurebase",
        "Featurebase",
        "feature-voting",
        "Canny 平替向 · 反馈/帮助中心/更新一体 · 价位亲民",
        "https://www.featurebase.app",
        "Featurebase 把功能投票、帮助中心与产品更新发布收敛到一套产品，常被当作 Canny 的轻量替代，覆盖从收集反馈、公示状态到教育用户「本周上了什么」的前半段旅程。",
        "中小团队要同时有反馈板、简易知识库与更新日志，又不想把 Canny + 帮助中心 + Changelog 三家拼在一起时评估。",
        "大型企业的工作流与分析深度仍有差距；若三块都浅用，不如拆回专用工具做深。",
        vendorId="featurebase-inc",
        pricing={"model": "freemium", "currency": "USD"},
        tags=["feedback", "roadmap", "changelog", "help-center"],
        pitfalls=[
            "大组织复杂权限与审批链不如专用产品管理平台。",
            "「三合一」容易堆功能，要克制范围避免半吊子。",
        ],
    ),
    mk(
        CAT_FEEDBACK,
        "fider",
        "Fider",
        "feature-voting",
        "开源功能投票板 · 可自托管 · 简链路反馈→状态",
        "https://fider.io",
        "Fider 是开源的功能请求与投票板：用户提交想法、投票排序，团队更新状态，数据可完全自托管。云托管与自建都支持，定位是干净的「客户声音墙」而不是完整 PM 套件。",
        "要开源/数据自持的公开路线图与投票、又不想上 Canny 级商业订阅时优先；要 Changelog+帮助中心一体化看 Featurebase，要 PM 洞察体看 Productboard。",
        "没有企业级产品组合与机会评分；高级品牌与 SSO 等多在商业托管档或需自研。",
        vendorId="fider-inc",
        githubUrl="https://github.com/getfider/fider",
        pricing={"model": "open-source", "currency": "USD", "notes": "自托管免费；官方云订阅"},
        tags=["feedback", "roadmap", "open-source", "self-hosted"],
        pitfalls=[
            "功能面聚焦投票板，缺少完整 PM 工作台。",
            "自托管需自管升级、邮件通知与反垃圾。",
        ],
    ),
    mk(
        CAT_FEEDBACK,
        "productboard",
        "Productboard",
        "product-management",
        "产品管理重镇 · 洞察到路线图 · 面向 PM 组织",
        "https://www.productboard.com",
        "Productboard 面向产品管理组织：沉淀客户洞察、机会与功能优先级，再落到路线图与发布沟通，常与工单、CRM、分析工具打通，属于 PM 工作台而非简单投票墙。",
        "有专职 PM、要「洞察—机会—交付」闭环与多产品线规划时评估；Indie 一人项目通常过重，用 Canny/Fider 即可。",
        "价格与实施成本显著；学习曲线陡，中小团队容易买而不用。",
        vendorId="productboard-inc",
        pricing={"model": "subscription", "currency": "USD"},
        maturity="mature",
        tags=["feedback", "roadmap", "product-management", "enterprise"],
        pitfalls=[
            "学习与配置成本高，一人团队不划算。",
            "订阅价格面向团队规模，扩张后账单跳升快。",
        ],
    ),
]

# ——— 联盟 / 短链 ———
AFF = [
    mk(
        CAT_AFF,
        "rewardful",
        "Rewardful",
        "affiliate",
        "Stripe 订阅联盟即装 · SaaS 推荐返佣 · 启用快",
        "https://www.getrewardful.com",
        "Rewardful 面向 Stripe 订阅型 SaaS：提供联盟链接、佣金规则与推荐人后台，把「推荐注册并付费 → 自动计佣」接到现有结账流，适合快速上线 affiliate。",
        "已用 Stripe Billing、想做推荐返佣且不想自建归因时优先；多支付通道或复杂 MLM 级规则请看更完整联盟平台。",
        "强绑定 Stripe 生态；非订阅/一次性商品与多 PSP 场景能力有限。",
        vendorId="rewardful-inc",
        pricing={"model": "subscription", "currency": "USD"},
        tags=["affiliate", "stripe", "saas", "referral"],
        pitfalls=[
            "基本假设是 Stripe 订阅，其他支付栈要自研桥接。",
            "复杂多级分销与税务合规仍需商务侧补齐。",
        ],
    ),
    mk(
        CAT_AFF,
        "firstpromoter",
        "FirstPromoter",
        "affiliate",
        "SaaS 联盟全功能 · 多集成 · 自动化营销触达",
        "https://firstpromoter.com",
        "FirstPromoter 是面向 SaaS 的联盟与推荐平台：跟踪链接/优惠码、佣金与 payout、推广者门户，并集成常见计费与营销工具，覆盖从线索到结佣的运营动作。",
        "需要比 Rewardful 更完整的联盟后台、多集成与 outbound 触达时评估；只要 Stripe 极速上线可先 Rewardful。",
        "配置面宽，规则设错会造成错佣；与支付/CRM 双重统计时要统一订单真相源。",
        vendorId="firstpromoter-inc",
        pricing={"model": "subscription", "currency": "USD"},
        tags=["affiliate", "referral", "saas", "marketing"],
        pitfalls=[
            "规则复杂时容易配错佣金，上线前用沙箱订单验收。",
            "与计费系统重复统计会打架，要钉死主数据源。",
        ],
    ),
    mk(
        CAT_AFF,
        "tolt",
        "Tolt",
        "affiliate",
        "新一代 Stripe 联盟 · 现代化 UI · SaaS 返佣向",
        "https://tolt.io",
        "Tolt 提供面向现代 SaaS 的联盟/推荐软件，深绑 Stripe 等收单，强调简洁设置、推广者体验与自动结佣，定位接近 Rewardful 一代工具的焕新替代。",
        "想用更新的界面与工作流做 Stripe 系推荐计划时对比 Rewardful；大型多货币多实体分佣要验证 payout 细节。",
        "生态年龄短于老牌，边缘集成与案例密度需自行 POC。",
        vendorId="tolt-inc",
        pricing={"model": "subscription", "currency": "USD"},
        tags=["affiliate", "stripe", "referral", "saas"],
        pitfalls=[
            "相对新，复杂企业场景案例少于 FirstPromoter 一类。",
            "仍受底层支付与税务合规约束，别当财务系统。",
        ],
    ),
    mk(
        CAT_AFF,
        "dub",
        "Dub",
        "link-management",
        "短链/归因/二维码 · 可自托管 · 联盟能力可选",
        "https://dub.co",
        "Dub 是面向增长团队的链接基础设施：自定义短链、点击分析、二维码与基础联盟/转化追踪，提供云版与开源自托管，常作为营销活动与多触点归因的链接层。",
        "需要品牌短链、活动 UTM 统一管理或自托管链接服务时评估；只做 Stripe 推荐佣金后台用 Rewardful 更垂直。",
        "链接层不替代完整广告归因；高级团队协作与 SSO 多在高档位。",
        vendorId="dub-inc",
        githubUrl="https://github.com/dubinc/dub",
        pricing={"model": "freemium", "currency": "USD"},
        tags=["links", "affiliate", "analytics", "open-source"],
        pitfalls=[
            "短链分析解决不了广告平台的跨设备归因。",
            "自托管要管域名、重定向可用性与反滥用。",
        ],
    ),
]

# ——— 业务自动化 ———
AUTO = [
    mk(
        CAT_AUTO,
        "zapier",
        "Zapier",
        "ipaas",
        "集成目录最广 · 无代码自动化标杆 · 按任务计费",
        "https://zapier.com",
        "Zapier 是业务自动化 iPaaS 的事实标准之一：海量 SaaS 连接器、无代码 Zaps，把表单、CRM、表格与通知串成事件驱动流程，适合运营与非工程角色自助集成。",
        "要在既有云端 SaaS 之间快速搭「如果 A 则 B」、连接器覆盖优先时采用；要自托管与代码级控制看 n8n / Activepieces，开发者 webhook/代码步骤看 Pipedream。",
        "任务量上来后账单陡增；复杂分支与数据转换能力弱于代码工作流。",
        vendorId="zapier-inc",
        pricing={"model": "freemium", "currency": "USD"},
        maturity="mature",
        tags=["automation", "ipaas", "nocode", "integration"],
        pitfalls=[
            "按任务计费，高频同步会迅速烧额度。",
            "复杂数据转换与错误重试不如代码工作流灵活。",
        ],
    ),
    mk(
        CAT_AUTO,
        "make-com",
        "Make",
        "ipaas",
        "可视化场景编排强 · 性价比常见平替 · 原 Integromat",
        "https://www.make.com",
        "Make（原 Integromat）用可视化场景画布编排多步自动化，路由器、聚合器与错误处理粒度细，同样是 Zapier 常见对照项，适合中等复杂度的 SaaS 间数据流。",
        "流程步骤多、需更细的分支与数据整形、又不想立即上代码时评估；连接器数量整体仍略逊 Zapier 头部目录。",
        "学习曲线高于「线性 Zap」；操作与数据量计费规则要细看。",
        vendorId="make-inc",
        pricing={"model": "freemium", "currency": "USD"},
        maturity="mature",
        tags=["automation", "ipaas", "nocode", "integration"],
        pitfalls=[
            "画布自由度高，场景容易搭成难维护的蜘蛛网。",
            "计费与操作包规则要按峰值流量测算。",
        ],
    ),
    mk(
        CAT_AUTO,
        "activepieces",
        "Activepieces",
        "ipaas",
        "开源 Zapier 替代 · 片段可扩展 · 可自托管",
        "https://www.activepieces.com",
        "Activepieces 是开源的业务自动化平台，提供流动画布与可扩展 pieces（连接器），可云可自托管，定位为 Zapier/Make 的可自掌控替代，方便团队按需写自定义片段。",
        "要数据驻留或二次开发连接器、又希望界面仍面向运营同学时评估；纯最广 SaaS 目录先 Zapier。",
        "连接器广度仍追头部；生产自托管要自己做高可用与密钥治理。",
        vendorId="activepieces-inc",
        githubUrl="https://github.com/activepieces/activepieces",
        pricing={"model": "open-source", "currency": "USD", "notes": "云版订阅；自托管开源"},
        tags=["automation", "open-source", "ipaas", "self-hosted"],
        pitfalls=[
            "连接器覆盖不及 Zapier，冷门 SaaS 要自己写 piece。",
            "自托管需运维队列、密钥与升级。",
        ],
    ),
    mk(
        CAT_AUTO,
        "pipedream",
        "Pipedream",
        "ipaas",
        "代码步骤优先 · 事件/ webhook 自动 · 开发者向",
        "https://pipedream.com",
        "Pipedream 面向开发者：用代码或低代码步骤处理 webhook、定时与 SaaS 事件，内置密钥管理与日志，适合「连接器 + 几行 JS/Python」而不是纯拖拽运营流。",
        "工程师要快速落地事件处理、原型集成或胶水逻辑、又不想自管服务器时采用；纯运营自助请用 Zapier/Make。",
        "平台运行额度与超时限制需设计幂等与重试；关键链路最终仍建议产品内服务化。",
        vendorId="pipedream-inc",
        pricing={"model": "freemium", "currency": "USD"},
        tags=["automation", "developer", "webhook", "ipaas"],
        pitfalls=[
            "执行时长与并发有平台上限，重任务要拆分。",
            "业务关键路径不宜长期停在胶水脚本层。",
        ],
    ),
]

# ——— 预约 ———
SCHED = [
    mk(
        CAT_SCHED,
        "cal-com",
        "Cal.com",
        "scheduling",
        "开源 Calendly 替代 · 可自托管 · 开发者可白标",
        "https://cal.com",
        "Cal.com 是开源的会议预约基础设施：链接选时、多日历冲突检测、团队活动类型与 webhook/API，可云可自托管，适合把预约嵌进产品或品牌域名。",
        "需要自托管/白标、或要把「约 demo」事件送进自己的 CRM/自动化时优先；只要个人约咨询且零运维用 Calendly 更快。",
        "日历提供商边界情况与时区规则要实测；自托管要维护邮件投递与可用时段同步。",
        vendorId="cal-com-inc",
        githubUrl="https://github.com/calcom/cal.com",
        pricing={"model": "open-source", "currency": "USD", "notes": "云版订阅；自托管开源"},
        tags=["scheduling", "calendar", "open-source", "self-hosted"],
        pitfalls=[
            "各日历服务商同步延迟与权限范围需实测。",
            "自托管要管邮件通知与反滥用。",
        ],
    ),
    mk(
        CAT_SCHED,
        "calendly",
        "Calendly",
        "scheduling",
        "预约链接事实标准 · 零运维 · 销售/成功团队普及",
        "https://calendly.com",
        "Calendly 让个人与团队共享可预约时段链接，自动避开冲突并写入日历、可挂视频会议与提醒，是销售演示、成功回访与候选人面试排程的常见默认。",
        "个人或小团队要最快上线「约 30 分钟」页、不关心自托管时优先；要深度白标与源码控制评 Cal.com。",
        "高级路由、集体可用性与 CRM 深集成在高价档；表单字段复杂时体验一般。",
        vendorId="calendly-inc",
        pricing={"model": "freemium", "currency": "USD"},
        maturity="mature",
        tags=["scheduling", "calendar", "sales", "saas"],
        pitfalls=[
            "团队路由与分析能力主要在付费档。",
            "品牌自定义与数据驻留选项有限。",
        ],
    ),
    mk(
        CAT_SCHED,
        "savvycal",
        "SavvyCal",
        "scheduling",
        "预约页 UX 标杆 · 对方日历叠加 · 顾问/招聘高质感",
        "https://savvycal.com",
        "SavvyCal 把预约体验做得很克制：邀请对象可在选时段时叠加查看自己的日历，减少来回改期；适合顾问、创始人与招聘等「对方时间很贵」的一对一约见。",
        "在意被约方体验、品牌调性，且团队不大时与 Calendly 对打；要销售路由/企业 CRM 深集成用 Calendly，要自托管/白标用 Cal.com。",
        "无慷慨免费档；企业级路由与 CRM 集成弱于 Calendly，大规模销售机队不是定位。",
        vendorId="savvycal-inc",
        pricing={"model": "subscription", "currency": "USD"},
        tags=["scheduling", "calendar", "ux", "saas"],
        pitfalls=[
            "缺少可长期使用的免费档，个人成本需接受订阅。",
            "销售团队复杂路由与 CRM 深度不如 Calendly。",
        ],
    ),
]

# ——— 通知编排 ———
ORCH = [
    mk(
        CAT_ORCH,
        "novu",
        "Novu",
        "notification-platform",
        "开源通知编排 · 多渠道模板 · 可自托管",
        "https://novu.co",
        "Novu 是开源通知基础设施：统一管理邮件/短信/推送/站内信等渠道模板与工作流，提供偏好管理与投递日志，可云可自托管，避免在业务代码里散落各家 SDK。",
        "产品通知类型变多、要可观测的多渠道编排与用户偏好中心时评估；只要事务邮件 API 用 Resend 即可。",
        "各供应商送达率仍取决于底层 ESP/SMS；自托管要管队列与密钥。",
        vendorId="novu-inc",
        githubUrl="https://github.com/novuhq/novu",
        pricing={"model": "open-source", "currency": "USD", "notes": "云版按量/订阅；自托管开源"},
        tags=["notifications", "orchestration", "open-source", "multichannel"],
        pitfalls=[
            "编排层不替代优质发信域名与短信签名资质。",
            "渠道一多，模板与变量约定需要严格规范。",
        ],
    ),
    mk(
        CAT_ORCH,
        "knock",
        "Knock",
        "notification-platform",
        "开发者向通知平台 · 批次与偏好 · 产品 inbox",
        "https://knock.app",
        "Knock 面向产品工程团队：用工作流定义通知、跨渠道发送、管理用户偏好与站内收件箱，强调类型安全集成与可观测，把「何时通知谁」从业务代码中抽离。",
        "B2B SaaS 通知规则复杂、需要统一偏好与 inbox 体验时评估；纯营销旅程编排请看 Customer.io / Braze。",
        "价格随事件量走；重度营销自动化不是定位。",
        vendorId="knock-inc",
        pricing={"model": "usage", "currency": "USD"},
        tags=["notifications", "orchestration", "developer", "inbox"],
        pitfalls=[
            "事件量大后费用需用采样与合并策略控制。",
            "不替代生命周期营销平台的分群旅程能力。",
        ],
    ),
    mk(
        CAT_ORCH,
        "courier",
        "Courier",
        "notification-platform",
        "设计器+API 通知平台 · 多渠道 · 模板中心向",
        "https://www.courier.com",
        "Courier 提供可视化模板与开发者 API 并行的通知平台，连接邮件、推送、聊天等多渠道，便于产品与运营共管模板内容，同时保留代码触发。",
        "需要非工程师也能改通知文案、又要统一投递与日志时评估；只要极简事务邮件或只要开源自托管分别看 Resend / Novu。",
        "模板治理与环境（dev/prod）流程要设计好，否则内容事故会放大。",
        vendorId="courier-inc",
        pricing={"model": "freemium", "currency": "USD"},
        tags=["notifications", "orchestration", "templates", "multichannel"],
        pitfalls=[
            "模板环境与权限治理不善会直接造成错发。",
            "底层渠道费用与限额仍要各供应商侧管理。",
        ],
    ),
]

ENTRIES_DATA = SOCIAL + FORMS + FEEDBACK + AFF + AUTO + SCHED + ORCH

VENDORS_DATA = [
    vendor("gitroom-inc", "Gitroom", url="https://postiz.com"),
    vendor("inovector-inc", "Inovector", url="https://mixpost.app"),
    vendor("buffer-inc", "Buffer", url="https://buffer.com"),
    vendor("typefully-inc", "Typefully", url="https://typefully.com"),
    vendor("publer-inc", "Publer", url="https://publer.com"),
    vendor("ayrshare-inc", "Ayrshare", url="https://www.ayrshare.com"),
    vendor("hootsuite-inc", "Hootsuite", url="https://www.hootsuite.com"),
    vendor("later-inc", "Later", url="https://later.com"),
    vendor("metricool-inc", "Metricool", url="https://metricool.com"),
    vendor("typeform-inc", "Typeform", url="https://www.typeform.com"),
    vendor("tally-inc", "Tally", url="https://tally.so"),
    vendor("fillout-inc", "Fillout", url="https://www.fillout.com"),
    vendor("formbricks-inc", "Formbricks", url="https://formbricks.com"),
    vendor("canny-inc", "Canny", url="https://canny.io"),
    vendor("featurebase-inc", "Featurebase", url="https://www.featurebase.app"),
    vendor("fider-inc", "Fider", url="https://fider.io"),
    vendor("productboard-inc", "Productboard", url="https://www.productboard.com"),
    vendor("rewardful-inc", "Rewardful", url="https://www.getrewardful.com"),
    vendor("firstpromoter-inc", "FirstPromoter", url="https://firstpromoter.com"),
    vendor("tolt-inc", "Tolt", url="https://tolt.io"),
    vendor("dub-inc", "Dub", url="https://dub.co"),
    vendor("zapier-inc", "Zapier", url="https://zapier.com"),
    vendor("make-inc", "Make", url="https://www.make.com"),
    vendor("activepieces-inc", "Activepieces", url="https://www.activepieces.com"),
    vendor("pipedream-inc", "Pipedream", url="https://pipedream.com"),
    vendor("cal-com-inc", "Cal.com", url="https://cal.com"),
    vendor("calendly-inc", "Calendly", url="https://calendly.com"),
    vendor("savvycal-inc", "SavvyCal", url="https://savvycal.com"),
    vendor("novu-inc", "Novu", url="https://novu.co"),
    vendor("knock-inc", "Knock", url="https://knock.app"),
    vendor("courier-inc", "Courier", url="https://www.courier.com"),
]

EDGES_DATA = [
    # social
    edge(
        "e-postiz-osalt-buffer",
        "postiz",
        "buffer",
        "open_source_alternative_to",
        note="开源可自托管 + API/Agent 向 vs 经典托管排期 SaaS",
    ),
    edge(
        "e-mixpost-osalt-buffer",
        "mixpost",
        "buffer",
        "open_source_alternative_to",
        note="自托管 Buffer 感控制台 vs 云端经典排期 SaaS",
    ),
    edge(
        "e-postiz-alt-mixpost",
        "postiz",
        "mixpost",
        "alternative_to",
        note="Agent/API/多平台动量 vs Laravel 栈 Buffer 感与买断 Pro",
        weight=0.75,
    ),
    edge(
        "e-postiz-osalt-hootsuite",
        "postiz",
        "hootsuite",
        "open_source_alternative_to",
        note="自托管/开源排期 vs 企业社媒套件",
        weight=0.6,
    ),
    edge(
        "e-postiz-with-n8n",
        "postiz",
        "n8n",
        "commonly_used_with",
        note="官方/社区常见：工作流生成内容后调用 Postiz API/节点发帖",
        weight=0.65,
    ),
    edge(
        "e-typefully-alt-buffer",
        "typefully",
        "buffer",
        "alternative_to",
        note="X/LinkedIn 写作台 vs 多渠道轻量日历",
    ),
    edge(
        "e-later-social-alt-buffer",
        "later-social",
        "buffer",
        "alternative_to",
        note="视觉向 IG/TikTok 日历 vs 通用轻量排期",
    ),
    edge(
        "e-publer-alt-buffer",
        "publer",
        "buffer",
        "alternative_to",
        note="批量/内容库与多账号矩阵 vs 极简队列",
    ),
    edge(
        "e-ayrshare-alt-buffer",
        "ayrshare",
        "buffer",
        "alternative_to",
        note="嵌入产品的发帖 API vs 运营用日历 UI",
        weight=0.55,
    ),
    edge(
        "e-metricool-alt-buffer",
        "metricool",
        "buffer",
        "alternative_to",
        note="分析+排期一体 vs 主打简洁发布",
    ),
    edge(
        "e-hootsuite-alt-buffer",
        "hootsuite",
        "buffer",
        "alternative_to",
        note="企业收件箱/审批/报表 vs 小团队轻量排期",
        weight=0.6,
    ),
    # forms
    edge(
        "e-tally-alt-typeform",
        "tally",
        "typeform",
        "alternative_to",
        note="慷慨免费、文档感搭建 vs 对话式完成率与品牌感",
    ),
    edge(
        "e-fillout-alt-typeform",
        "fillout",
        "typeform",
        "alternative_to",
        note="计算/支付/预约多块表单 vs 对话式调研体验",
    ),
    edge(
        "e-formbricks-osalt-typeform",
        "formbricks",
        "typeform",
        "open_source_alternative_to",
        note="开源产品内触发调研 vs 外向对话式表单 SaaS",
        weight=0.6,
    ),
    edge(
        "e-tally-with-zapier",
        "tally",
        "zapier",
        "commonly_used_with",
        note="表单提交事件驱动下游 CRM/通知自动化",
        weight=0.6,
    ),
    edge(
        "e-typeform-with-zapier",
        "typeform",
        "zapier",
        "commonly_used_with",
        note="完成问卷后进 CRM、表格或 Slack",
        weight=0.6,
    ),
    # feedback
    edge(
        "e-featurebase-alt-canny",
        "featurebase",
        "canny",
        "alternative_to",
        note="反馈+帮助中心+更新一体、价位更贴中小 vs 经典投票板",
    ),
    edge(
        "e-fider-osalt-canny",
        "fider",
        "canny",
        "open_source_alternative_to",
        note="开源可自托管投票板 vs 商业成熟反馈/路线图产品",
    ),
    edge(
        "e-productboard-alt-canny",
        "productboard",
        "canny",
        "alternative_to",
        note="PM 洞察—机会—路线图工作台 vs 客户投票墙",
        weight=0.6,
    ),
    edge(
        "e-canny-with-intercom",
        "canny",
        "intercom",
        "commonly_used_with",
        note="客服会话里的需求回流到投票与路线图",
        weight=0.5,
    ),
    # affiliate
    edge(
        "e-tolt-alt-rewardful",
        "tolt",
        "rewardful",
        "alternative_to",
        note="新一代 Stripe 联盟体验 vs 成熟即装联盟",
    ),
    edge(
        "e-firstpromoter-alt-rewardful",
        "firstpromoter",
        "rewardful",
        "alternative_to",
        note="更完整联盟运营后台 vs Stripe 极速上线",
    ),
    edge(
        "e-dub-with-rewardful",
        "dub",
        "rewardful",
        "commonly_used_with",
        note="短链/活动链接层 + 订阅联盟计佣层，按职责拆分",
        weight=0.5,
    ),
    edge(
        "e-rewardful-with-stripe",
        "rewardful",
        "stripe",
        "integrates_with",
        note="订阅与发票事件作为佣金触发源",
        weight=0.75,
    ),
    edge(
        "e-tolt-with-stripe",
        "tolt",
        "stripe",
        "integrates_with",
        note="深绑 Stripe 结账与订阅状态做归因",
        weight=0.75,
    ),
    # automation
    edge(
        "e-make-com-alt-zapier",
        "make-com",
        "zapier",
        "alternative_to",
        note="细粒度场景画布 vs 最广连接器与心智默认",
    ),
    edge(
        "e-activepieces-osalt-zapier",
        "activepieces",
        "zapier",
        "open_source_alternative_to",
        note="可自托管/扩展 pieces vs 托管 iPaaS 目录",
    ),
    edge(
        "e-n8n-osalt-zapier",
        "n8n",
        "zapier",
        "open_source_alternative_to",
        note="fair-code 自托管节点流 vs 无代码 SaaS 自动化",
    ),
    edge(
        "e-n8n-alt-make-com",
        "n8n",
        "make-com",
        "alternative_to",
        note="可自托管与代码节点 vs 托管可视化场景",
    ),
    edge(
        "e-pipedream-alt-zapier",
        "pipedream",
        "zapier",
        "alternative_to",
        note="开发者代码步骤与 webhook 优先 vs 运营向无代码",
        weight=0.6,
    ),
    edge(
        "e-activepieces-alt-n8n",
        "activepieces",
        "n8n",
        "alternative_to",
        note="更偏业务自动化 UI 的开源 iPaaS vs 运维/AI 混合流",
        weight=0.6,
    ),
    # scheduling
    edge(
        "e-cal-com-osalt-calendly",
        "cal-com",
        "calendly",
        "open_source_alternative_to",
        note="开源可自托管/白标 vs 托管预约默认项",
    ),
    edge(
        "e-savvycal-alt-calendly",
        "savvycal",
        "calendly",
        "alternative_to",
        note="被约方日历叠加的高质感一对一 vs 销售机队默认预约",
    ),
    edge(
        "e-cal-com-with-zapier",
        "cal-com",
        "zapier",
        "commonly_used_with",
        note="预约成功事件推进 CRM / 邮件 / Slack",
        weight=0.55,
    ),
    edge(
        "e-calendly-with-zapier",
        "calendly",
        "zapier",
        "commonly_used_with",
        note="预约成功后同步到 CRM、Slack 或邮件触达",
        weight=0.55,
    ),
    # orchestration
    edge(
        "e-novu-osalt-knock",
        "novu",
        "knock",
        "open_source_alternative_to",
        note="开源可自托管通知编排 vs 托管开发者通知平台",
    ),
    edge(
        "e-courier-alt-knock",
        "courier",
        "knock",
        "alternative_to",
        note="模板设计器+API 共管 vs 工作流/偏好开发者向",
    ),
    edge(
        "e-novu-with-resend",
        "novu",
        "resend",
        "commonly_used_with",
        note="编排层选渠道与模板，Resend 负责邮件投递",
        weight=0.65,
    ),
    edge(
        "e-knock-with-resend",
        "knock",
        "resend",
        "commonly_used_with",
        note="通知工作流把邮件渠道指到 Resend 等 ESP",
        weight=0.6,
    ),
    edge(
        "e-courier-with-twilio",
        "courier",
        "twilio",
        "commonly_used_with",
        note="短信/语音渠道常见走 Twilio 等 CPaaS",
        weight=0.55,
    ),
]


def migrate_n8n() -> None:
    """n8n 原挂在 ai-rag（工作流向被误归），迁入 cicd-automation。"""
    path = ENTRIES / "n8n.json"
    if not path.exists():
        print("warn: n8n.json missing, skip migrate")
        return
    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("category") == CAT_AUTO:
        print("n8n already on", CAT_AUTO)
        return
    old = data.get("category")
    data["category"] = CAT_AUTO
    data["subcategory"] = "ipaas"
    data["lastReviewed"] = REVIEWED
    if "workflow" not in data.get("tags", []) and "automation" not in data.get("tags", []):
        tags = list(data.get("tags") or [])
        for t in ("automation", "ipaas", "open-source", "self-hosted"):
            if t not in tags:
                tags.append(t)
        data["tags"] = tags[:5]
    save(path, data)
    print(f"migrated n8n {old} → {CAT_AUTO}")


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
    for g in EDGES_DATA:
        path = EDGES / f"{g['id']}.json"
        if path.exists() and not args.overwrite:
            skipped_g += 1
            continue
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

    migrate_n8n()

    print(
        f"done entries={wrote_e}(skip {skipped_e}) "
        f"vendors={wrote_v}(skip {skipped_v}) edges={wrote_g}(skip {skipped_g})"
    )
    print(
        f"new leaves covered: {CAT_SOCIAL} {CAT_FORMS} {CAT_FEEDBACK} "
        f"{CAT_AFF} {CAT_AUTO} {CAT_SCHED} {CAT_ORCH}"
    )


if __name__ == "__main__":
    main()
