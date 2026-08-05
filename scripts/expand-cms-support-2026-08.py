#!/usr/bin/env python3
"""内容管理 / CMS（collab-cms）与 客服 / 工单（collab-support）扩种。

- collab-cms：Contentful / Sanity / Payload / Storyblok / Hygraph（SaaS 与自托管 Headless）
  + TinaCMS / Decap / Keystatic（Git 存内容）+ WordPress / Ghost / Wagtail（传统建站）
- collab-support：Intercom / Zendesk / Freshdesk / Help Scout / Plain / Crisp / Tawk.to
  + Chatwoot（开源）+ 美洽 / 网易七鱼（国内）

用法:
  python3 scripts/expand-cms-support-2026-08.py
  python3 scripts/expand-cms-support-2026-08.py --overwrite
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
CAT_CMS = "collab-cms"
CAT_SUPPORT = "collab-support"


def save(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def entry(**kw) -> dict:
    e = {
        "pricing": {"model": "freemium"},
        "availability": {
            "chinaAccessible": True,
            "needsCompany": False,
            "needsIcp": False,
            "regions": ["global"],
        },
        "tags": ["cms"],
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
    assert 20 <= len(e["oneLiner"]) <= 58, (e["id"], len(e["oneLiner"]), e["oneLiner"])
    assert 160 <= len(e.get("descriptionMd", "")) <= 360, (e["id"], len(e.get("descriptionMd", "")))
    assert 1 <= len(e.get("pitfalls") or []) <= 3, e["id"]
    assert e.get("subcategory"), e["id"]
    assert 3 <= len(e.get("tags") or []) <= 5, e["id"]
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


def cms(eid, name, sub, one, url, what, when, caution, **extra):
    return mk(CAT_CMS, eid, name, sub, one, url, what, when, caution, **extra)


def support(eid, name, sub, one, url, what, when, caution, **extra):
    return mk(CAT_SUPPORT, eid, name, sub, one, url, what, when, caution, **extra)


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


GLOBAL = {
    "chinaAccessible": True,
    "needsCompany": False,
    "needsIcp": False,
    "regions": ["global"],
}

# 自建站点若落地国内服务器需 ICP 备案
SELF_HOST_SITE = {
    "chinaAccessible": True,
    "needsCompany": False,
    "needsIcp": True,
    "regions": ["global"],
}

DOMESTIC = {
    "chinaAccessible": True,
    "needsCompany": False,
    "needsIcp": False,
    "regions": ["CN"],
}

DOMESTIC_B2B = {
    "chinaAccessible": True,
    "needsCompany": True,
    "needsIcp": False,
    "regions": ["CN"],
}


CMS_ENTRIES: list[dict] = [
    # ——— SaaS Headless ———
    cms(
        "contentful",
        "Contentful",
        "headless-cms",
        "API-first 老牌 Headless · 空间与环境分层严 · 企业治理向",
        "https://www.contentful.com",
        "Contentful 是 API 优先的托管型 Headless CMS：内容类型与条目走空间与环境分层，配交付/管理两套接口、Webhook 与多语言，编辑后台与前端完全解耦。",
        "多品牌多站点共用一份内容、需要发布流程与权限审计、且愿意把内容托管交给厂商时评估；前端多与 Next.js、Nuxt 等框架同栈。",
        "按内容条目、语言与 API 调用计费，规模上来后成本抬升快；导出迁移可行但建模习惯有厂商烙印。",
        vendorId="contentful-inc",
        pricing={"model": "freemium", "currency": "USD", "notes": "免费档有条目与用户上限；企业档按空间/用量报价"},
        availability=GLOBAL,
        maturity="mature",
        tags=["cms", "headless", "saas", "api"],
        docsUrl="https://www.contentful.com/developers/docs/",
        pitfalls=[
            "按条目/语言/调用计费，内容规模膨胀后成本不易预测。",
            "免费与低档位有较硬的条目和角色上限，团队扩张需提前测算。",
        ],
    ),
    cms(
        "sanity",
        "Sanity",
        "headless-cms",
        "内容湖 + GROQ 查询 · Studio 可代码定制 · 实时协作强",
        "https://www.sanity.io",
        "Sanity 把内容存为托管的结构化文档，用 GROQ 查询取数；编辑后台 Studio 是可自行编码与部署的 React 应用，支持实时协作与自定义输入控件。",
        "内容模型复杂、需要把编辑器改造成业务专用工作台，或看重实时协作与富文本可移植性时评估；常与 Next.js、Vercel 同栈。",
        "GROQ 与可移植富文本是自有口径，前端需要适配层；Studio 定制能力强也意味着要自己维护这份代码。",
        vendorId="sanity-inc",
        pricing={"model": "freemium", "currency": "USD", "notes": "免费档含一定用量；按席位与 API/带宽用量升档"},
        availability=GLOBAL,
        tags=["cms", "headless", "saas", "graphql"],
        docsUrl="https://www.sanity.io/docs",
        pitfalls=[
            "GROQ 与 Portable Text 属自有口径，跨 CMS 迁移需重写取数与渲染层。",
            "Studio 深度定制后即成为需长期维护的前端项目。",
        ],
    ),
    cms(
        "storyblok",
        "Storyblok",
        "headless-cms",
        "可视化编辑器 + 组件化 Block 建模 · 市场团队友好",
        "https://www.storyblok.com",
        "Storyblok 是带可视化编辑器的 Headless CMS：页面由可复用 Block 组件拼装，编辑者在真实预览里点选修改，开发者仍通过接口取结构化内容。",
        "营销站点需要非技术同事自助改版、又不想退回传统整站 CMS 时评估；与 Nuxt、Next.js 等框架的预览桥接是常见落点。",
        "可视化预览要前端配合埋桥接代码，改造成本落在开发侧；组件粒度设计不当会让 Block 库迅速膨胀难维护。",
        vendorId="storyblok-gmbh",
        pricing={"model": "freemium", "currency": "USD", "notes": "免费社区档；按席位与流量升档"},
        availability=GLOBAL,
        tags=["cms", "headless", "saas", "visual-editor"],
        docsUrl="https://www.storyblok.com/docs",
        pitfalls=[
            "可视化预览需前端接入桥接脚本，非纯后端接管。",
            "Block 组件缺乏规范时会快速膨胀，后期治理成本高。",
        ],
    ),
    cms(
        "hygraph",
        "Hygraph",
        "headless-cms",
        "GraphQL 原生 Headless · 可联邦聚合外部数据源",
        "https://hygraph.com",
        "Hygraph（原 GraphCMS）以 GraphQL 为一等接口，内容建模与查询都围绕 Schema 展开，并提供把外部服务数据联邦进同一张查询图的能力。",
        "前端已全面 GraphQL、希望内容与商品/用户等外部数据一次查询取回时评估；纯 REST 团队收益有限。",
        "GraphQL 是主路径，团队缺少相关经验时上手更慢；联邦聚合会把外部服务的可用性与限流一并带进内容接口。",
        vendorId="hygraph-gmbh",
        pricing={"model": "freemium", "currency": "USD", "notes": "免费档有用量上限；按项目与用量升档"},
        availability=GLOBAL,
        tags=["cms", "headless", "graphql", "saas"],
        docsUrl="https://hygraph.com/docs",
        pitfalls=[
            "以 GraphQL 为主路径，REST 心智的团队迁移成本更高。",
            "内容联邦把外部接口的限流与故障引入内容交付链路。",
        ],
    ),
    cms(
        "payload-cms",
        "Payload CMS",
        "headless-cms",
        "TypeScript 配置即模型 · 跑在 Next.js 内 · 自托管开源",
        "https://payloadcms.com",
        "Payload 是 TypeScript 原生的开源 Headless CMS，内容模型用代码声明，后台与接口可直接跑在 Next.js 应用内部，数据落在自己的 Postgres 或 MongoDB。",
        "已用 Next.js、希望内容后台与业务代码同仓同部署、且要求数据自持时评估；与 Strapi、Directus 属同层的自托管选项。",
        "运维与升级由自己承担；模型改动走代码与迁移而非后台点选，非技术同事无法自助加字段。",
        vendorId="payload-inc",
        pricing={"model": "open-source", "notes": "自托管免费；官方云托管另计"},
        availability=GLOBAL,
        githubUrl="https://github.com/payloadcms/payload",
        tags=["cms", "headless", "open-source", "typescript"],
        docsUrl="https://payloadcms.com/docs",
        pitfalls=[
            "内容模型改动需改代码并做迁移，运营侧无法自助扩字段。",
            "自托管意味着数据库、备份与升级全部自担。",
        ],
    ),
    # ——— Git 存内容 ———
    cms(
        "tina-cms",
        "TinaCMS",
        "git-based-cms",
        "内容存 Git · Markdown 可视化编辑 · Next.js 生态最顺",
        "https://tina.io",
        "TinaCMS 把 Markdown/MDX 等文件仍留在 Git 仓库，另提供可视化编辑界面与内容 Schema，编辑动作最终落成仓库提交，可选官方云做协作与索引。",
        "文档站、博客与营销站已用静态生成、希望非技术同事在页面上直接改文案又不引入数据库时评估。",
        "内容量大或需要复杂关联查询时 Git 方案会吃力；实时协作与权限粒度弱于托管型 CMS。",
        vendorId="tina-inc",
        pricing={"model": "open-source", "notes": "开源自托管免费；Tina Cloud 按团队计费"},
        availability=GLOBAL,
        githubUrl="https://github.com/tinacms/tinacms",
        tags=["cms", "git-based", "open-source", "markdown"],
        docsUrl="https://tina.io/docs",
        pitfalls=[
            "内容规模变大后 Git 读写与构建时间明显变慢。",
            "多人同时编辑的冲突处理与权限粒度弱于托管型 CMS。",
        ],
    ),
    cms(
        "decap-cms",
        "Decap CMS",
        "git-based-cms",
        "纯 Git 的开源静态站后台 · 无数据库 · 配置即建模",
        "https://decapcms.org",
        "Decap CMS（原 Netlify CMS）是运行在浏览器里的静态站内容后台：用一份配置描述集合与字段，编辑结果通过 Git 提供方的接口直接提交回仓库，不需要自建数据库与服务端。",
        "Hugo、Astro、Jekyll 等静态站要给编辑者一个最简后台、且希望内容随代码一起版本化时评估。",
        "依赖 Git 托管方的鉴权与提交接口，需要一层认证服务；媒体管理与富文本体验偏基础。",
        pricing={"model": "open-source"},
        availability=GLOBAL,
        githubUrl="https://github.com/decaporg/decap-cms",
        tags=["cms", "git-based", "open-source", "static-site"],
        docsUrl="https://decapcms.org/docs/",
        pitfalls=[
            "需要额外的 OAuth 认证服务才能对接 Git 托管方。",
            "媒体库与富文本能力基础，重内容站点容易触顶。",
        ],
    ),
    cms(
        "keystatic",
        "Keystatic",
        "git-based-cms",
        "内容写回仓库 · Astro/Next 内嵌后台 · 本地模式可离线",
        "https://keystatic.com",
        "Keystatic 由 Thinkmill 开源，内容以 Markdoc/MDX/JSON 存在仓库中，后台可作为路由内嵌进 Astro、Next.js 等应用，本地模式直接读写工作区文件。",
        "小型内容站想要轻量后台、又不愿引入托管服务与数据库时评估；与 Decap、TinaCMS 属同层的 Git 方案。",
        "生态与插件数量少于老牌方案；内容体量与协作规模上去后仍需转向托管型 CMS。",
        vendorId="thinkmill",
        pricing={"model": "open-source"},
        availability=GLOBAL,
        maturity="beta",
        githubUrl="https://github.com/Thinkmill/keystatic",
        tags=["cms", "git-based", "open-source", "astro"],
        docsUrl="https://keystatic.com/docs",
        pitfalls=[
            "项目较新，生态与第三方字段类型少于老牌方案。",
            "面向中小内容量，重协作场景仍需托管型 CMS。",
        ],
    ),
    # ——— 传统整站 CMS ———
    cms(
        "wordpress",
        "WordPress",
        "traditional-cms",
        "PHP 插件生态最大 · 整站建站主力 · 自托管可控但需运维",
        "https://wordpress.org",
        "WordPress 是自托管的开源整站 CMS，主题负责前台呈现、插件承载功能扩展，块编辑器统一了内容与版式编辑，也可只当内容源走接口给前端。",
        "企业官网、内容站与外包交付要求生态成熟、可招到人维护时仍是稳妥选择；纯 App 供稿则优先看 Headless 方案。",
        "插件叠加带来安全与性能债，升级需回归测试；站点落地国内服务器须完成 ICP 备案。",
        vendorId="automattic",
        pricing={"model": "open-source", "notes": "软件开源免费；主机、主题与插件另计"},
        availability=SELF_HOST_SITE,
        maturity="mature",
        region="both",
        tags=["cms", "php", "open-source", "website"],
        githubUrl="https://github.com/WordPress/WordPress",
        pitfalls=[
            "插件生态庞杂，安全补丁与版本兼容需持续跟进。",
            "国内服务器托管站点须完成 ICP 备案。",
        ],
    ),
    cms(
        "ghost",
        "Ghost",
        "traditional-cms",
        "内容订阅与邮件通讯一体 · Node 开源 · 托管自托管皆可",
        "https://ghost.org",
        "Ghost 是面向出版与订阅的开源 Node 内容平台：写作后台克制，内置会员、付费墙与邮件通讯，也可关掉自带前台只作内容接口使用。",
        "个人或小团队做付费专栏、品牌博客与邮件通讯，希望内容与订阅收费在一套系统里闭环时评估。",
        "扩展性远不如插件生态型 CMS，复杂业务页面需自写主题或前端；自托管要自行处理升级与邮件送达。",
        vendorId="ghost-foundation",
        pricing={"model": "open-source", "notes": "自托管免费；Ghost(Pro) 官方托管按订阅计费"},
        availability=SELF_HOST_SITE,
        maturity="mature",
        githubUrl="https://github.com/TryGhost/Ghost",
        tags=["cms", "publishing", "open-source", "newsletter"],
        docsUrl="https://ghost.org/docs/",
        pitfalls=[
            "无插件市场，复杂功能需改主题或自建前端。",
            "自托管需自理版本升级与邮件送达率。",
        ],
    ),
    cms(
        "wagtail",
        "Wagtail",
        "traditional-cms",
        "Django 系开源 CMS · 页面树与审校流 · 政企内容站常用",
        "https://wagtail.org",
        "Wagtail 是构建在 Django 之上的开源 CMS，以页面树组织站点、模型用 Python 声明，内置版本、审校与工作流，天然与既有 Django 业务共用一套模型与权限。",
        "团队已是 Python/Django 栈、站点信息架构层级深、且对无障碍与审校流程有要求时评估。",
        "对非 Python 团队门槛高；改页面结构要写模型与迁移，运营无法自助扩字段。",
        vendorId="torchbox",
        pricing={"model": "open-source"},
        availability=GLOBAL,
        maturity="mature",
        githubUrl="https://github.com/wagtail/wagtail",
        tags=["cms", "python", "django", "open-source"],
        docsUrl="https://docs.wagtail.org",
        pitfalls=[
            "绑定 Django 技术栈，非 Python 团队维护成本高。",
            "页面模型改动需写迁移，运营侧无法自助调整结构。",
        ],
    ),
]


SUPPORT_ENTRIES: list[dict] = [
    # ——— 海外对话式 / 工单套件 ———
    support(
        "intercom",
        "Intercom",
        "conversational-support",
        "站内对话式支持 + AI 客服 · 生态深 · 计价随解决量走",
        "https://www.intercom.com",
        "Intercom 以站内消息气泡起家，把在线对话、帮助中心、产品引导与 AI 应答收进一套工作台，客服工单与主动触达共用同一份用户档案。",
        "SaaS 产品要在应用内做售前答疑与留存运营、且愿意为一体化体验付费时评估；纯邮件工单场景性价比不高。",
        "按席位叠加 AI 解决量计费，用量波动会直接反映在账单上；深度绑定后帮助中心与自动化流程迁移成本高。",
        vendorId="intercom-inc",
        pricing={"model": "subscription", "currency": "USD", "notes": "按席位订阅，AI 应答按解决次数另计"},
        availability=GLOBAL,
        maturity="mature",
        tags=["support", "livechat", "saas", "ai"],
        docsUrl="https://developers.intercom.com",
        pitfalls=[
            "AI 应答按解决量计费，高峰期账单波动明显。",
            "国内站点加载气泡脚本延迟较高，需评估首屏影响。",
        ],
    ),
    support(
        "zendesk",
        "Zendesk",
        "ticketing-suite",
        "企业级工单与知识库 · 流程报表完备 · 实施与配置偏重",
        "https://www.zendesk.com",
        "Zendesk 是工单起家的客户服务套件：多渠道汇聚成工单、配 SLA、分派规则、知识库与报表，另有面向大型组织的权限与审计能力。",
        "客服团队规模化、需要 SLA 考核与跨部门流转、并对报表和合规有硬要求时评估；小团队会觉得配置负担重。",
        "功能按模块与档位拆分，报价与实施周期都不轻；自动化规则堆积后维护复杂，换供应商时历史工单迁移量大。",
        vendorId="zendesk-inc",
        pricing={"model": "subscription", "currency": "USD", "notes": "按席位分档订阅，AI 与高级功能常需加购"},
        availability=GLOBAL,
        maturity="mature",
        tags=["support", "ticketing", "saas", "enterprise"],
        docsUrl="https://developer.zendesk.com",
        pitfalls=[
            "高级能力散落在加购模块，实际单价常高于标称档位。",
            "自动化规则长期堆积后难以审计与重构。",
        ],
    ),
    support(
        "freshdesk",
        "Freshdesk",
        "ticketing-suite",
        "工单起家的性价比套件 · Freshworks 生态 · 中小团队向",
        "https://freshdesk.com",
        "Freshdesk 是 Freshworks 旗下的客服工单产品，覆盖邮件与多渠道工单、自动分派、知识库与基础报表，并与同厂的销售、IT 服务台产品共用生态。",
        "预算敏感、又需要正规工单流程与知识库的中小团队评估；已用 Freshworks 其他产品时协同更划算。",
        "深度定制与企业级治理弱于头部套件；跨产品数据打通程度需按实际模块核实，勿默认全通。",
        vendorId="freshworks",
        pricing={"model": "freemium", "currency": "USD", "notes": "有免费入门档；按席位分档订阅"},
        availability=GLOBAL,
        tags=["support", "ticketing", "saas", "helpdesk"],
        pitfalls=[
            "企业级权限、审计与定制深度弱于头部套件。",
            "同厂产品的数据打通需逐模块核实，勿默认全通。",
        ],
    ),
    support(
        "helpscout",
        "Help Scout",
        "shared-inbox",
        "邮件为主的共享收件箱 · 对客无工单感 · 帮助中心自带",
        "https://www.helpscout.com",
        "Help Scout 以共享收件箱为核心：客户收到的是普通邮件而非带编号的工单通知，团队侧有分派、协作备注、帮助中心与轻量站内气泡。",
        "希望支持体验保持人情味、对话量中等、不想让客户面对工单系统的团队评估；重流程 SLA 场景仍需正式工单台。",
        "复杂路由、SLA 与报表能力有限；随着团队扩张常需迁移到更重的工单套件。",
        vendorId="helpscout-inc",
        pricing={"model": "subscription", "currency": "USD", "notes": "按席位订阅，含帮助中心与站内气泡"},
        availability=GLOBAL,
        tags=["support", "shared-inbox", "email", "saas"],
        docsUrl="https://developer.helpscout.com",
        pitfalls=[
            "SLA、分级路由与报表能力有限，规模化后易触顶。",
            "以邮件为主线，实时聊天与自动化弱于对话式平台。",
        ],
    ),
    support(
        "plain-com",
        "Plain",
        "b2b-support",
        "面向 B2B SaaS 的支持台 · Slack 原生 · API 与工作流优先",
        "https://www.plain.com",
        "Plain 是面向 B2B SaaS 的客户支持工具：把 Slack 共享频道、邮件与站内求助收进统一线程，并强调用接口把客户上下文与工程侧问题单串起来。",
        "客户是企业账号、日常支持发生在 Slack 共享频道、且希望支持与研发工单联动时评估；面向海量消费者的场景不匹配。",
        "定位窄，缺少大众客服套件的呼叫中心与复杂知识库；团队与生态较年轻，能力边界需 POC 验证。",
        vendorId="plain-inc",
        pricing={"model": "subscription", "currency": "USD", "notes": "按席位订阅"},
        availability=GLOBAL,
        tags=["support", "b2b", "slack", "saas"],
        docsUrl="https://www.plain.com/docs",
        pitfalls=[
            "面向 B2B 窄场景，消费级海量会话与呼叫中心能力缺位。",
            "产品较年轻，复杂需求需 POC 验证能力边界。",
        ],
    ),
    support(
        "crisp",
        "Crisp",
        "livechat",
        "轻量共享收件箱 · 渠道插件多 · 小团队价格友好",
        "https://crisp.chat",
        "Crisp 提供网站聊天气泡、共享收件箱与多渠道插件，把邮件、社交与即时通讯消息汇进一个界面，另带机器人、知识库与共享浏览等实用件。",
        "初创或中小团队要快速上一个能用的在线客服、渠道杂而预算有限时评估；重工单流程与合规审计场景不合适。",
        "企业级权限、报表与 SLA 偏弱；能力散在插件中，不同档位可用范围差别大，选档前需逐项核对。",
        vendorId="crisp-im",
        pricing={"model": "freemium", "currency": "USD", "notes": "免费档基础聊天；插件与高级能力随档位开放"},
        availability=GLOBAL,
        tags=["support", "livechat", "saas", "smb"],
        docsUrl="https://docs.crisp.chat",
        pitfalls=[
            "企业级权限、SLA 与报表能力偏弱。",
            "关键能力分散在插件里，需按档位逐项核对可用范围。",
        ],
    ),
    support(
        "tawk-to",
        "Tawk.to",
        "livechat",
        "基础聊天长期免费 · 去品牌与人力代管另付费 · 嵌入极轻",
        "https://www.tawk.to",
        "Tawk.to 提供免费的网站在线聊天与访客实时监控，坐席与会话量不设限，另带基础知识库与预设回复，靠移除品牌标识、代运营坐席等增值服务盈利。",
        "个人站、外包交付或早期产品只想先有一个能收消息的入口、预算接近零、也不打算把客服流程正规化时评估；有合规与报表要求的团队直接看付费方案。",
        "免费的代价是品牌露出与相对基础的能力；数据合规、报表与自动化都弱，业务正规化后通常需要替换。",
        vendorId="tawk-inc",
        pricing={"model": "free", "currency": "USD", "notes": "核心功能免费；去品牌与代管坐席为付费项"},
        availability=GLOBAL,
        tags=["support", "livechat", "free", "smb"],
        pitfalls=[
            "免费档带品牌露出，去除需按月付费。",
            "报表、自动化与合规能力基础，规模化后需替换。",
        ],
    ),
    # ——— 开源 ———
    support(
        "chatwoot",
        "Chatwoot",
        "open-source-support",
        "开源全渠道客服 · 可自托管数据自持 · Rails 栈需运维",
        "https://www.chatwoot.com",
        "Chatwoot 是开源的客户互动平台：网站聊天、邮件与主流社交渠道汇进共享收件箱，带团队分派、自动化与知识库，可自托管也可用官方云。",
        "对客服会话数据落地有要求、或想避开按席位长期付费的团队评估；愿意承担 Rails 与依赖服务的运维成本时收益最大。",
        "自托管要自理升级、存储与消息渠道凭据；部分高级能力属商业版授权，社区版能力边界需先核对。",
        vendorId="chatwoot-inc",
        pricing={"model": "open-source", "notes": "社区版自托管免费；云版与企业功能按席位计费"},
        availability=GLOBAL,
        githubUrl="https://github.com/chatwoot/chatwoot",
        tags=["support", "open-source", "self-hosted", "omnichannel"],
        docsUrl="https://www.chatwoot.com/docs",
        pitfalls=[
            "自托管需自理升级、附件存储与各渠道凭据轮换。",
            "部分能力属商业版授权，社区版边界需提前核对。",
        ],
    ),
    # ——— 国内 ———
    support(
        "meiqia",
        "美洽",
        "domestic-support",
        "国内多渠道在线客服 · 微信小程序接入顺 · 中小团队向",
        "https://meiqia.com",
        "美洽是国内的在线客服 SaaS，覆盖网页与 App 咨询、微信公众号与小程序等渠道接入，配工单、客服机器人与会话质检等常规能力。",
        "国内产品要快速接入在线客服、主要流量来自微信生态与自有网站、且希望开通与结算都走本地渠道时评估；出海多语与全球节点需另选方案。",
        "海外访问与多语言支持有限；渠道能力与并发坐席按套餐差异大，签约前需按实际渠道逐项确认。",
        vendorId="meiqia-inc",
        pricing={"model": "freemium", "currency": "CNY", "notes": "按坐席数与功能档订阅"},
        availability=DOMESTIC,
        region="domestic",
        tags=["support", "livechat", "domestic", "wechat"],
        pitfalls=[
            "面向国内场景，海外访问与多语言能力有限。",
            "渠道与坐席能力按套餐分层，签约前需逐项确认。",
        ],
    ),
    support(
        "qiyu",
        "网易七鱼",
        "domestic-support",
        "网易系客服云 · 工单与智能机器人齐备 · 偏企业采购",
        "https://qiyukf.com",
        "网易七鱼是网易旗下的智能客服云，提供在线客服、工单系统、呼叫中心与客服机器人，渠道覆盖网页、App、微信与企业微信等国内入口。",
        "国内中大型团队需要工单流转、质检报表与呼叫中心一体，且倾向选择有资质与本地服务的厂商时评估。",
        "开通与计费偏企业采购路径，个人与小团队门槛偏高；能力按模块拆分，报价前需明确所需模块与坐席数。",
        vendorId="netease",
        pricing={"model": "subscription", "currency": "CNY", "notes": "按坐席与模块分档，企业采购为主"},
        availability=DOMESTIC_B2B,
        region="domestic",
        tags=["support", "ticketing", "domestic", "callcenter"],
        pitfalls=[
            "以企业采购为主，个人与小团队开通门槛偏高。",
            "呼叫中心等模块需单独开通，整体报价随模块叠加。",
        ],
    ),
]


ENTRIES_DATA: list[dict] = CMS_ENTRIES + SUPPORT_ENTRIES

VENDORS_DATA: list[dict] = [
    vendor("contentful-inc", "Contentful", url="https://www.contentful.com"),
    vendor("sanity-inc", "Sanity", url="https://www.sanity.io"),
    vendor("storyblok-gmbh", "Storyblok", url="https://www.storyblok.com"),
    vendor("hygraph-gmbh", "Hygraph", url="https://hygraph.com"),
    vendor("payload-inc", "Payload", url="https://payloadcms.com"),
    vendor("tina-inc", "Tina", url="https://tina.io"),
    vendor("thinkmill", "Thinkmill", url="https://www.thinkmill.com.au"),
    vendor("automattic", "Automattic", url="https://automattic.com"),
    vendor("ghost-foundation", "Ghost Foundation", url="https://ghost.org"),
    vendor("torchbox", "Torchbox", url="https://torchbox.com"),
    vendor("intercom-inc", "Intercom", url="https://www.intercom.com"),
    vendor("zendesk-inc", "Zendesk", url="https://www.zendesk.com"),
    vendor("freshworks", "Freshworks", url="https://www.freshworks.com"),
    vendor("helpscout-inc", "Help Scout", url="https://www.helpscout.com"),
    vendor("plain-inc", "Plain", url="https://www.plain.com"),
    vendor("crisp-im", "Crisp IM", url="https://crisp.chat"),
    vendor("tawk-inc", "tawk.to", url="https://www.tawk.to"),
    vendor("chatwoot-inc", "Chatwoot", url="https://www.chatwoot.com"),
    vendor("meiqia-inc", "美洽", region="domestic", url="https://meiqia.com"),
    vendor("netease", "网易", region="domestic", url="https://www.163.com"),
]


EDGES_DATA: list[dict] = [
    # ——— CMS：同层横比 ———
    edge(
        "e-contentful-alt-sanity",
        "contentful",
        "sanity",
        "alternative_to",
        note="托管 Headless 双雄：Contentful 偏空间/环境治理与企业流程，Sanity 偏可编码 Studio 与实时协作",
        weight=0.8,
    ),
    edge(
        "e-storyblok-alt-contentful",
        "storyblok",
        "contentful",
        "alternative_to",
        note="Storyblok 主打可视化 Block 编辑，Contentful 主打纯结构化接口与治理",
        weight=0.75,
    ),
    edge(
        "e-hygraph-alt-contentful",
        "hygraph",
        "contentful",
        "alternative_to",
        note="Hygraph 以 GraphQL 与内容联邦为主路径，Contentful 以 REST/GraphQL 双接口与空间模型为主",
        weight=0.7,
    ),
    edge(
        "e-payload-cms-osalt-contentful",
        "payload-cms",
        "contentful",
        "open_source_alternative_to",
        note="用自托管代码建模换取数据自持，代价是运维与非技术同事自助能力",
        weight=0.75,
    ),
    edge(
        "e-strapi-osalt-contentful",
        "strapi",
        "contentful",
        "open_source_alternative_to",
        note="Strapi 后台可点选建模，更接近 Contentful 的运营体验；托管与扩容自理",
        weight=0.75,
    ),
    edge(
        "e-strapi-alt-payload-cms",
        "strapi",
        "payload-cms",
        "alternative_to",
        note="同为自托管 Node CMS：Strapi 后台点选建模，Payload 以 TypeScript 代码声明模型",
        weight=0.8,
    ),
    edge(
        "e-directus-alt-payload-cms",
        "directus",
        "payload-cms",
        "alternative_to",
        note="Directus 直接包裹既有数据库表，Payload 由代码定义模型再生成存储",
        weight=0.7,
    ),
    edge(
        "e-tina-cms-alt-decap-cms",
        "tina-cms",
        "decap-cms",
        "alternative_to",
        note="同为 Git 存内容：TinaCMS 有可视化实时编辑与可选云端，Decap 纯前端配置更轻",
        weight=0.75,
    ),
    edge(
        "e-keystatic-alt-decap-cms",
        "keystatic",
        "decap-cms",
        "alternative_to",
        note="Keystatic 后台内嵌进应用路由并支持本地文件模式，Decap 为独立后台页面",
        weight=0.7,
    ),
    edge(
        "e-tina-cms-osalt-storyblok",
        "tina-cms",
        "storyblok",
        "open_source_alternative_to",
        note="可视化编辑的开源方向：内容留在 Git，换掉托管服务与按席位计费",
        weight=0.6,
    ),
    edge(
        "e-ghost-alt-wordpress",
        "ghost",
        "wordpress",
        "alternative_to",
        note="Ghost 聚焦出版与订阅收费，WordPress 靠插件生态覆盖任意站点形态",
        weight=0.75,
    ),
    edge(
        "e-wagtail-alt-wordpress",
        "wagtail",
        "wordpress",
        "alternative_to",
        note="Wagtail 走 Django 模型与审校流，WordPress 走 PHP 主题插件生态",
        weight=0.7,
    ),
    edge(
        "e-wordpress-mig-ghost",
        "wordpress",
        "ghost",
        "migration_path_to",
        note="内容站转做付费订阅/邮件通讯时的常见迁移方向；插件类功能需另找替代",
        weight=0.6,
    ),
    edge(
        "e-decap-cms-alt-strapi",
        "decap-cms",
        "strapi",
        "alternative_to",
        note="静态站给编辑者最简后台 vs 需要数据库与接口的完整内容服务",
        weight=0.55,
    ),
    # ——— CMS：跨叶组合 ———
    edge(
        "e-payload-cms-built-nextjs",
        "payload-cms",
        "nextjs",
        "built_on",
        note="后台与接口以 Next.js 应用形态运行，与业务前端同仓同部署",
        weight=0.85,
    ),
    edge(
        "e-wagtail-built-django",
        "wagtail",
        "django",
        "built_on",
        note="页面模型、权限与后台均建立在 Django 之上，可与既有业务模型共存",
        weight=0.9,
    ),
    edge(
        "e-contentful-cuw-nextjs",
        "contentful",
        "nextjs",
        "commonly_used_with",
        note="内容走接口取回、页面在构建期或增量再生成，是营销站常见组合",
        weight=0.7,
    ),
    edge(
        "e-sanity-cuw-nextjs",
        "sanity",
        "nextjs",
        "commonly_used_with",
        note="Studio 可与前端同仓部署，配合草稿预览做实时预览",
        weight=0.75,
    ),
    edge(
        "e-sanity-cuw-vercel",
        "sanity",
        "vercel",
        "commonly_used_with",
        note="内容更新触发部署或按需再生成，Studio 亦常托管在同一平台",
        weight=0.65,
    ),
    edge(
        "e-storyblok-cuw-nuxt",
        "storyblok",
        "nuxt",
        "commonly_used_with",
        note="可视化编辑需要前端接入桥接层，Nuxt 生态的对接示例较完整",
        weight=0.65,
    ),
    edge(
        "e-keystatic-cuw-astro",
        "keystatic",
        "astro",
        "commonly_used_with",
        note="后台以路由形式内嵌进 Astro 站点，内容文件与代码同仓",
        weight=0.7,
    ),
    edge(
        "e-tina-cms-cuw-nextjs",
        "tina-cms",
        "nextjs",
        "commonly_used_with",
        note="面向 Next.js 的可视化编辑与预览支持最完整",
        weight=0.7,
    ),
    edge(
        "e-decap-cms-cuw-cloudflare-pages",
        "decap-cms",
        "cloudflare-pages",
        "commonly_used_with",
        note="静态站托管 + Git 提交式后台：提交回仓库即触发重新构建",
        weight=0.6,
    ),
    edge(
        "e-ghost-cuw-astro",
        "ghost",
        "astro",
        "commonly_used_with",
        note="关掉自带前台只用内容接口，由 Astro 生成静态前端",
        weight=0.55,
    ),
    edge(
        "e-payload-cms-cuw-postgresql",
        "payload-cms",
        "postgresql",
        "commonly_used_with",
        note="常用 Postgres 适配器落库（亦支持 MongoDB），数据留在自有实例",
        weight=0.7,
    ),
    edge(
        "e-wagtail-cuw-postgresql",
        "wagtail",
        "postgresql",
        "commonly_used_with",
        note="生产部署的常规数据库选择，全文检索与并发表现更稳",
        weight=0.65,
    ),
    # ——— 客服：同层横比与镜像 ———
    edge(
        "e-zendesk-alt-intercom",
        "zendesk",
        "intercom",
        "alternative_to",
        note="Zendesk 从工单与流程出发，Intercom 从站内对话与增长运营出发",
        weight=0.8,
    ),
    edge(
        "e-crisp-alt-intercom",
        "crisp",
        "intercom",
        "alternative_to",
        note="同为站内聊天形态，Crisp 价格与功能都更轻，缺企业级治理",
        weight=0.7,
    ),
    edge(
        "e-helpscout-alt-intercom",
        "helpscout",
        "intercom",
        "alternative_to",
        note="Help Scout 以邮件共享收件箱为主线，对客不暴露工单编号",
        weight=0.7,
    ),
    edge(
        "e-plain-com-alt-intercom",
        "plain-com",
        "intercom",
        "alternative_to",
        note="Plain 面向 B2B 企业客户与 Slack 共享频道，Intercom 面向海量终端用户",
        weight=0.6,
    ),
    edge(
        "e-freshdesk-alt-zendesk",
        "freshdesk",
        "zendesk",
        "alternative_to",
        note="同为工单套件，Freshdesk 价格与上手更友好，企业级定制弱一档",
        weight=0.75,
    ),
    edge(
        "e-tawk-to-alt-crisp",
        "tawk-to",
        "crisp",
        "alternative_to",
        note="Tawk.to 核心功能免费但带品牌露出，Crisp 付费换更完整的插件与体验",
        weight=0.65,
    ),
    edge(
        "e-chatwoot-osalt-intercom",
        "chatwoot",
        "intercom",
        "open_source_alternative_to",
        note="自托管换数据自持与去席位计费，代价是运维与 AI 能力差距",
        weight=0.8,
    ),
    edge(
        "e-chatwoot-osalt-zendesk",
        "chatwoot",
        "zendesk",
        "open_source_alternative_to",
        note="覆盖多渠道收件箱与基础工单，SLA、报表与合规审计仍弱一档",
        weight=0.65,
    ),
    edge(
        "e-meiqia-de-intercom",
        "meiqia",
        "intercom",
        "domestic_equivalent_of",
        note="国内在线客服镜像：微信生态接入顺，AI 与全球节点弱于 Intercom",
        weight=0.7,
    ),
    edge(
        "e-qiyu-de-zendesk",
        "qiyu",
        "zendesk",
        "domestic_equivalent_of",
        note="国内工单/呼叫中心镜像：本地化与资质合规更省事，生态开放度低一档",
        weight=0.7,
    ),
    edge(
        "e-meiqia-alt-qiyu",
        "meiqia",
        "qiyu",
        "alternative_to",
        note="国内同层：美洽偏中小团队自助开通，七鱼偏企业采购与呼叫中心",
        weight=0.75,
    ),
    # ——— 客服：跨叶集成 ———
    edge(
        "e-intercom-int-slack",
        "intercom",
        "slack",
        "integrates_with",
        note="会话与提醒同步到频道，团队可在 Slack 内响应与协作",
        weight=0.7,
    ),
    edge(
        "e-zendesk-int-slack",
        "zendesk",
        "slack",
        "integrates_with",
        note="工单通知与创建可在频道内完成，减少来回切换",
        weight=0.65,
    ),
    edge(
        "e-chatwoot-int-slack",
        "chatwoot",
        "slack",
        "integrates_with",
        note="官方集成把会话转发到频道并支持直接回复",
        weight=0.7,
    ),
    edge(
        "e-crisp-int-slack",
        "crisp",
        "slack",
        "integrates_with",
        note="插件形式把收件箱消息接进频道，适合无专职客服的小团队",
        weight=0.65,
        sources=["https://crisp.chat/en/integrations/"],
    ),
    edge(
        "e-crisp-int-discord",
        "crisp",
        "discord",
        "integrates_with",
        note="官方 Discord 插件可在频道内收发会话，社区型产品常用",
        weight=0.6,
        sources=["https://crisp.chat/en/integrations/"],
    ),
    edge(
        "e-plain-com-int-slack",
        "plain-com",
        "slack",
        "integrates_with",
        note="以 Slack 共享频道为一等入口，客户消息直接汇入支持线程",
        weight=0.8,
    ),
    edge(
        "e-plain-com-int-linear",
        "plain-com",
        "linear",
        "integrates_with",
        note="支持会话可转成研发问题单并回写状态，闭合客户反馈环",
        weight=0.65,
    ),
    edge(
        "e-meiqia-int-wecom",
        "meiqia",
        "wecom",
        "integrates_with",
        note="把企业微信作为会话接入渠道之一，与公众号、小程序并列",
        weight=0.6,
    ),
    edge(
        "e-qiyu-int-wecom",
        "qiyu",
        "wecom",
        "integrates_with",
        note="企业微信渠道接入后统一进工单与坐席分派",
        weight=0.6,
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
    assert len(ids) == len(set(ids)), "entry id 重复"
    gids = [g["id"] for g in EDGES_DATA]
    assert len(gids) == len(set(gids)), "edge id 重复"

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
        print("entry", e["id"])

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
            print("skip edge exists", g["id"])
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

    cms_n = sum(1 for e in ENTRIES_DATA if e["category"] == CAT_CMS)
    sup_n = sum(1 for e in ENTRIES_DATA if e["category"] == CAT_SUPPORT)
    print(
        f"done entries={wrote_e}(skip {skipped_e}) "
        f"[{CAT_CMS}={cms_n} {CAT_SUPPORT}={sup_n}] "
        f"vendors={wrote_v}(skip {skipped_v}) edges={wrote_g}(skip {skipped_g})"
    )


if __name__ == "__main__":
    main()
