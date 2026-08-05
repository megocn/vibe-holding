#!/usr/bin/env python3
"""增长三叶扩种（growth-seo / growth-experiment / growth-lifecycle）。

- SEO / 关键词：Moz / Screaming Frog / Similarweb / Ubersuggest / Bing 站长工具
  / 百度搜索资源平台 / 5118 / 爱站网
- Feature Flag / 实验：LaunchDarkly / Statsig / GrowthBook / Unleash / Flagsmith
  / ConfigCat / Optimizely / OpenFeature / 火山引擎 DataTester
- 邮件营销 / 生命周期：Mailchimp / Loops / Customer.io / Kit / Klaviyo / beehiiv
  / Substack / Buttondown / Braze

用法:
  python3 scripts/expand-growth-2026-08.py
  python3 scripts/expand-growth-2026-08.py --overwrite
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

CAT_SEO = "growth-seo"
CAT_EXP = "growth-experiment"
CAT_LIFE = "growth-lifecycle"


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
        "tags": ["growth"],
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
    assert 160 <= len(e["descriptionMd"]) <= 360, (e["id"], len(e["descriptionMd"]))
    assert 1 <= len(e["pitfalls"]) <= 3, e["id"]
    assert 3 <= len(e["tags"]) <= 5, e["id"]
    assert e.get("subcategory"), e["id"]
    assert e["id"] == e["id"].lower() and e["id"][0].isalpha(), e["id"]
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


def seo(eid, name, sub, one, url, what, when, caution, **extra):
    return mk(CAT_SEO, eid, name, sub, one, url, what, when, caution, **extra)


def exp(eid, name, sub, one, url, what, when, caution, **extra):
    return mk(CAT_EXP, eid, name, sub, one, url, what, when, caution, **extra)


def life(eid, name, sub, one, url, what, when, caution, **extra):
    return mk(CAT_LIFE, eid, name, sub, one, url, what, when, caution, **extra)


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

DOMESTIC = {
    "chinaAccessible": True,
    "needsCompany": False,
    "needsIcp": False,
    "regions": ["CN"],
}

DOMESTIC_ICP = {
    "chinaAccessible": True,
    "needsCompany": False,
    "needsIcp": True,
    "regions": ["CN"],
}


SEO_ENTRIES: list[dict] = [
    seo(
        "moz",
        "Moz",
        "seo-suite",
        "DA/PA 权威度口径起家 · 关键词与站点爬取一体 · 教程体系厚",
        "https://moz.com",
        "Moz 是老牌 SEO 工具套件，提供关键词研究、站点爬取诊断、外链查询与 Domain Authority（DA）等指标，其 DA/PA 口径被行业长期当作站点权威度的通用参照。",
        "把 SEO 当长期渠道、需要一套「指标口径 + 教程体系」帮团队对齐认知时评估；外链深度情报仍是 Ahrefs 的强项，竞品流量画像看 Similarweb。",
        "索引库与外链覆盖不及头部两家；DA 是第三方估算值，不同工具之间口径不可比。",
        vendorId="moz-inc",
        pricing={"model": "subscription", "currency": "USD"},
        maturity="mature",
        tags=["seo", "keyword", "backlink", "saas"],
        pitfalls=[
            "DA 是第三方估算值，勿当成搜索引擎的真实排名依据。",
            "外链索引覆盖不及头部竞品，跨工具数据难直接对齐。",
        ],
    ),
    seo(
        "screaming-frog",
        "Screaming Frog SEO Spider",
        "site-audit",
        "本机桌面爬虫 · 技术 SEO 体检与批量抓取 · 按年授权、数据留本地",
        "https://www.screamingfrog.co.uk",
        "Screaming Frog SEO Spider 是运行在本机的网站爬虫，抓完站点后输出标题、状态码、重定向链、canonical 与结构化数据等技术体检结果，可与搜索表现数据联合排查。",
        "站点改版迁移前后做全量比对、批量排查死链与重复元信息，或要求抓取结果留在本机不上传第三方云时优先。",
        "只做技术审计，不提供关键词研究与长期排名跟踪；大站抓取吃内存，需切换数据库存储模式并预留磁盘。",
        vendorId="screaming-frog-ltd",
        pricing={"model": "freemium", "currency": "GBP", "notes": "免费版限抓取 URL 数，完整功能按年授权"},
        maturity="mature",
        tags=["seo", "crawler", "audit", "desktop"],
        pitfalls=[
            "大站抓取吃内存，需切数据库存储模式并预留磁盘。",
            "不做关键词研究与排名跟踪，需另配云端套件。",
        ],
    ),
    seo(
        "similarweb",
        "Similarweb",
        "traffic-intelligence",
        "第三方流量与渠道构成估算 · 竞品行业面板 · 看别人家不看自家",
        "https://www.similarweb.com",
        "Similarweb 用第三方数据估算网站与 App 的访问规模、流量来源构成、受众重合与竞品排名，属于「看别人家」的市场情报工具，而不是部署在自己站点上的分析埋点。",
        "做竞品调研、渠道结构判断或行业选型输入时使用；自家站点真实数据请用 GA4/Plausible 一类分析工具，搜索表现回到 Search Console。",
        "数据是模型估算，长尾小站误差尤其大；企业套餐门槛高，免费额度只能看粗粒度概览。",
        vendorId="similarweb-inc",
        pricing={"model": "freemium", "currency": "USD"},
        maturity="mature",
        tags=["seo", "market-intel", "competitor", "analytics"],
        pitfalls=[
            "估算数据对长尾小站误差大，勿当精确口径引用。",
            "深度报表价格高，免费额度只够看概览。",
        ],
    ),
    seo(
        "ubersuggest",
        "Ubersuggest",
        "seo-suite",
        "轻量关键词与站点体检 · 低价订阅或买断 · 个人站入门够用",
        "https://neilpatel.com/ubersuggest/",
        "Ubersuggest 由 Neil Patel 团队运营，把关键词建议、内容创意、站点体检与基础排名跟踪打包成低价工具，界面简单、上手门槛低，定位是 SEO 套件里的入门档。",
        "个人站、独立开发者或早期项目只需要判断「有没有搜索量、页面有没有明显毛病」，又不愿承担头部套件订阅时评估。",
        "数据深度与更新频率明显弱于头部套件；站内营销内容较重，别把它的估算值当作唯一决策依据。",
        vendorId="neil-patel-digital",
        pricing={"model": "freemium", "currency": "USD"},
        tags=["seo", "keyword", "budget", "starter"],
        pitfalls=[
            "关键词与外链数据深度弱于头部套件，适合粗筛不适合深挖。",
            "估算值波动较大，建议与第二数据源交叉验证。",
        ],
    ),
    seo(
        "bing-webmaster-tools",
        "Bing 网站管理员工具",
        "search-console",
        "Bing 官方索引与搜索表现 · 支持 IndexNow 主动推送 · 完全免费",
        "https://www.bing.com/webmasters",
        "Bing 网站管理员工具是微软提供的官方搜索表现面板：提交站点地图、查看抓取与索引状态、观察关键词展现与点击，并支持 IndexNow 协议把新增或更新的 URL 主动推给搜索侧。",
        "面向英文市场、或希望内容被 Bing 及其驱动的问答类入口收录时，与 Google Search Console 并行接入，成本只是多做一次域名验证。",
        "只反映 Bing 自身数据，流量盘子远小于 Google；不要用它的指标替代 GSC 判断整体搜索表现。",
        vendorId="microsoft",
        pricing={"model": "free"},
        maturity="mature",
        tags=["seo", "search-console", "free", "microsoft"],
        pitfalls=[
            "数据仅覆盖 Bing 自身，不能代表整体搜索表现。",
            "IndexNow 推送不等于收录，仍受内容质量判定影响。",
        ],
    ),
    seo(
        "baidu-search-console",
        "百度搜索资源平台",
        "search-console",
        "百度官方索引与抓取诊断 · 站点验证与链接提交 · 中文站必接",
        "https://ziyuan.baidu.com",
        "百度搜索资源平台是百度官方的站长工具：站点验证、Sitemap 与链接主动推送、抓取诊断、索引量与搜索关键词展现，是中文站点与百度搜索之间的官方通道。",
        "面向国内用户、内容以中文为主并希望被百度收录时必接；面向海外市场的站点主看 Google Search Console，两边的指标与判定规则不通用。",
        "多数功能要求站点完成验证、部分权益与备案主体挂钩；收录判定不透明，提交成功不等于会被收录。",
        vendorId="baidu",
        region="domestic",
        availability=DOMESTIC_ICP,
        pricing={"model": "free", "currency": "CNY"},
        maturity="mature",
        tags=["seo", "search-console", "domestic", "baidu"],
        pitfalls=[
            "提交链接不等于收录，判定规则不公开。",
            "部分功能与备案主体、站点验证状态强绑定。",
        ],
    ),
    seo(
        "wu5118",
        "5118",
        "keyword-research",
        "中文关键词与长尾词挖掘 · 竞品词库与收录监控 · 套餐分级明显",
        "https://www.5118.com",
        "5118 是国内老牌 SEO 数据平台，提供中文关键词与长尾词挖掘、竞品站点词库、收录与排名监控等能力，词库与语料以中文搜索场景为主，适合做规模化选题输入。",
        "做中文内容选题、需要成规模的长尾词库，或想监控国内竞品站点表现时评估；官方索引提交与抓取诊断仍要回到百度搜索资源平台。",
        "数据为第三方估算，权重类指标不是搜索引擎口径；高级功能与导出条数按套餐分级，采购前核对配额。",
        vendorId="wu5118-inc",
        region="domestic",
        availability=DOMESTIC,
        pricing={"model": "subscription", "currency": "CNY"},
        tags=["seo", "keyword", "domestic", "chinese"],
        pitfalls=[
            "权重与流量为平台自定义估算口径，跨平台不可比。",
            "导出条数与高级功能按套餐分级，容易低估采购成本。",
        ],
    ),
    seo(
        "aizhan",
        "爱站网",
        "seo-suite",
        "中文站长查询工具集 · 收录/排名/备案一站查 · 含本地工具包",
        "https://www.aizhan.com",
        "爱站网是国内常用的站长查询工具集：域名收录、关键词排名、外链与备案信息查询，并提供可下载的本地工具包，用于批量核对站点与竞品域名的基础状况。",
        "需要快速体检中文站点的基础指标、批量核对竞品域名，或作为 5118 之外的第二数据源做交叉验证时使用。",
        "权重是平台自定义估算口径，不同站长工具之间不可比；免费查询有频次限制，深度功能需付费。",
        vendorId="aizhan-inc",
        region="domestic",
        availability=DOMESTIC,
        pricing={"model": "freemium", "currency": "CNY"},
        tags=["seo", "domestic", "webmaster", "chinese"],
        pitfalls=[
            "平台权重非搜索引擎口径，勿写进对外指标。",
            "免费查询有频次限制，批量核对需付费或用本地工具包。",
        ],
    ),
]


EXP_ENTRIES: list[dict] = [
    exp(
        "launchdarkly",
        "LaunchDarkly",
        "feature-flag",
        "企业级开关标杆 · 权限审批与审计齐 · 按席位与上下文计价",
        "https://launchdarkly.com",
        "LaunchDarkly 是功能开关领域的企业级代表：多环境标志管理、目标人群规则、审批与审计流、多语言 SDK 与边缘投递，核心主张是把「部署」和「上线」拆成两件事。",
        "团队规模大、开关数量多且需要权限分级与合规审计，或要把灰度发布纳入正式发布流程时评估；只需要几个简单开关的小团队用它偏贵。",
        "价格随席位与上下文规模增长很快；规则模型有锁定成本，接入时最好在应用侧再包一层自己的开关抽象。",
        vendorId="launchdarkly-inc",
        pricing={"model": "subscription", "currency": "USD"},
        maturity="mature",
        tags=["feature-flag", "experiment", "enterprise", "sdk"],
        pitfalls=[
            "按席位与上下文计价，规模上来后成本抬升明显。",
            "规则模型与 SDK 有锁定成本，建议自建一层开关抽象。",
        ],
    ),
    exp(
        "statsig",
        "Statsig",
        "experimentation",
        "开关与实验同栈 · 自带指标与统计引擎 · 按事件量计价",
        "https://statsig.com",
        "Statsig 把功能开关、A/B 实验与产品指标放在同一套系统里：开关发布后直接复用同一份事件流做实验读数，内置统计引擎与自动化的实验结果分析。",
        "希望「灰度 → 实验 → 指标」闭环少接一套分析工具，并愿意把事件送进同一平台时评估；只要开关、不做实验的团队可以选更轻的方案。",
        "事件量是计价主轴，埋点膨胀会直接推高成本；实验结论依赖埋点口径，接入前先把指标定义统一。",
        vendorId="statsig-inc",
        pricing={"model": "usage", "currency": "USD"},
        tags=["feature-flag", "experiment", "analytics", "sdk"],
        pitfalls=[
            "按事件量计价，埋点膨胀会直接推高账单。",
            "实验结论强依赖埋点口径，指标定义不统一会得出错误结论。",
        ],
    ),
    exp(
        "growthbook",
        "GrowthBook",
        "experimentation",
        "开源实验平台 · 直接在自有数仓上跑分析 · 可自托管、事件不外传",
        "https://www.growthbook.io",
        "GrowthBook 是开源的功能开关与 A/B 实验平台，特点是不要求把事件送进厂商云，而是直接连到你已有的数据仓库上执行实验查询，把标志下发与实验分析解耦。",
        "已有数仓与埋点体系、希望实验分析复用现成数据并规避事件外传，或因合规要求必须私有化部署时优先。",
        "实验结论的质量取决于自家数仓的数据质量与查询成本；自托管要自己承担升级、备份与可用性运维。",
        vendorId="growthbook-inc",
        githubUrl="https://github.com/growthbook/growthbook",
        pricing={"model": "open-source"},
        tags=["feature-flag", "experiment", "open-source", "self-host"],
        pitfalls=[
            "实验结论质量取决于自有数仓的数据口径与查询成本。",
            "自托管需自担升级与高可用运维。",
        ],
    ),
    exp(
        "unleash",
        "Unleash",
        "feature-flag",
        "开源开关服务端 · 私有化与边缘代理 · 专注开关不做实验分析",
        "https://www.getunleash.io",
        "Unleash 是开源的功能开关服务，提供服务端 API、多语言 SDK 与 Edge/Proxy 组件，强调标志求值发生在自己这一侧，企业版补充权限、审计与合规相关能力。",
        "把开关当基础设施来建、要求私有化部署或数据不出网，而实验分析另有体系时优先；要开箱即用的实验读数请看 GrowthBook 或 Statsig。",
        "实验与指标能力弱，需要自己拼接分析链路；开源版与企业版功能分层明显，选型前核对所需特性落在哪一档。",
        vendorId="unleash-inc",
        githubUrl="https://github.com/Unleash/unleash",
        pricing={"model": "open-source"},
        tags=["feature-flag", "open-source", "self-host", "sdk"],
        pitfalls=[
            "不含实验统计能力，需另配分析体系。",
            "开源版与企业版功能分层明显，容易在采购时才发现缺特性。",
        ],
    ),
    exp(
        "flagsmith",
        "Flagsmith",
        "feature-flag",
        "开源开关与远程配置 · 托管自建两条路 · 移动端配置下发友好",
        "https://www.flagsmith.com",
        "Flagsmith 提供开源的功能开关与远程配置服务，支持自托管与官方托管两种形态；除布尔开关外也常被用来下发多变体配置，前端与移动端 SDK 覆盖较全。",
        "既要功能开关也要远程配置、并希望保留「先用托管、后转自建」退路的团队适合评估。",
        "实验统计能力有限，A/B 结论仍需外部分析；自托管版本的规模化与高可用要自己压测和运维。",
        vendorId="flagsmith-inc",
        githubUrl="https://github.com/Flagsmith/flagsmith",
        pricing={"model": "open-source"},
        tags=["feature-flag", "open-source", "remote-config", "self-host"],
        pitfalls=[
            "实验统计能力有限，A/B 结论需借助外部分析。",
            "自托管的高可用与扩容需自行压测。",
        ],
    ),
    exp(
        "configcat",
        "ConfigCat",
        "feature-flag",
        "轻量托管开关 · 计价与终端用户量脱钩 · 功能面刻意克制",
        "https://configcat.com",
        "ConfigCat 是定位轻量的托管功能开关服务，主打接入简单、SDK 体积小，按配置数与席位而不是终端用户量计价，功能面刻意保持克制，不往实验平台方向堆。",
        "只需要稳定的开关下发与基础人群定向、不打算为实验平台付费，或月活很大但开关很少、按用户量计价不划算时评估。",
        "没有完整的实验与指标体系；复杂人群规则和企业级治理需求超出后仍要换更重的平台。",
        vendorId="configcat-inc",
        pricing={"model": "freemium", "currency": "USD"},
        tags=["feature-flag", "saas", "lightweight", "sdk"],
        pitfalls=[
            "不提供实验统计，只解决开关下发。",
            "复杂人群规则与治理需求增长后需要迁移。",
        ],
    ),
    exp(
        "optimizely",
        "Optimizely",
        "experimentation",
        "老牌实验平台并入 DXP · 偏营销与内容试验 · 企业采购路径",
        "https://www.optimizely.com",
        "Optimizely 从网页 A/B 测试起家，如今是包含内容管理、个性化与实验的数字体验平台，试验形态覆盖页面改版、内容位与功能开关，面向营销与内容团队的比重更高。",
        "营销或内容团队要做页面级试验并与 CMS、个性化能力同栈，或企业已在其体系内时评估；纯工程侧的开关治理看 LaunchDarkly 一类更合适。",
        "产品线经多次并购整合，模块边界与命名变化较大；采购与实施偏企业项目制，小团队的成本与复杂度都高。",
        vendorId="optimizely-inc",
        pricing={"model": "subscription", "currency": "USD"},
        maturity="mature",
        tags=["experiment", "dxp", "enterprise", "marketing"],
        pitfalls=[
            "并购整合后模块命名与边界变化大，查文档需确认版本。",
            "企业项目制采购，小团队投入产出比低。",
        ],
    ),
    exp(
        "openfeature",
        "OpenFeature",
        "flag-standard",
        "CNCF 开关开放标准 · 统一 SDK 接口换后端 · 自身不提供托管",
        "https://openfeature.dev",
        "OpenFeature 是 CNCF 旗下的功能开关开放标准，定义统一的 SDK 接口与 Provider 机制，让应用代码与具体开关厂商解耦，后端可以在不同开关服务之间替换而不改调用处。",
        "担心开关厂商锁定，或多个团队各用不同后端、需要统一接入口径时，先按它写好封装层再去选具体供应商。",
        "它是规范与 SDK，不提供标志存储与管理界面，仍需搭配一个 Provider；各家 Provider 的成熟度与特性覆盖并不一致。",
        vendorId="cncf",
        githubUrl="https://github.com/open-feature/spec",
        pricing={"model": "open-source"},
        tags=["feature-flag", "standard", "open-source", "cncf"],
        pitfalls=[
            "只是规范与 SDK，仍需搭配具体 Provider 才能用。",
            "各家 Provider 特性覆盖不一致，换后端未必零成本。",
        ],
    ),
    exp(
        "datatester",
        "火山引擎 DataTester",
        "experimentation",
        "火山系 A/B 实验 · 承接字节内部方法论 · 与国内数据栈同云",
        "https://www.volcengine.com/product/datatester",
        "DataTester 是火山引擎提供的 A/B 实验平台，沿用字节跳动内部沉淀的实验方法论，覆盖流量分层、实验分流、指标看板与开关式发布，常与火山引擎的数据与增长产品同栈使用。",
        "团队在国内、数据与业务已经落在火山或字节云体系，且需要中文文档与本地化实施支持时评估。",
        "与火山账号及其数据产品绑定较深，跨云迁移成本高；计费与功能分档以控制台为准，勿按海外同类产品的价格心智估算。",
        vendorId="volcengine",
        region="domestic",
        availability=DOMESTIC,
        pricing={"model": "usage", "currency": "CNY"},
        tags=["experiment", "ab-test", "domestic", "volcengine"],
        pitfalls=[
            "与火山账号及数据产品绑定深，跨云迁移成本高。",
            "功能分档与计价随控制台调整，需以官方为准。",
        ],
    ),
]


LIFE_ENTRIES: list[dict] = [
    life(
        "mailchimp",
        "Mailchimp",
        "email-marketing",
        "老牌营销邮件一体机 · 模板名单自动化齐 · 按联系人阶梯计价",
        "https://mailchimp.com",
        "Mailchimp 是历史最长的邮件营销平台之一：可视化模板编辑、名单与分群管理、自动化旅程、落地页与表单打包提供，面向不写代码的市场与运营角色。",
        "中小企业或内容团队需要一套开箱即用的营销邮件与名单工具，并由非技术同事日常操作时评估。",
        "按联系人规模阶梯涨价，长期不清理的僵尸订阅者会持续吃成本；验证码、账单一类事务邮件请走专门的发信 API，不要混在营销账号里。",
        vendorId="intuit",
        pricing={"model": "freemium", "currency": "USD"},
        maturity="mature",
        tags=["email", "marketing", "automation", "crm"],
        pitfalls=[
            "按联系人数阶梯计价，不清理名单会持续吃成本。",
            "勿用营销账号发事务邮件，信誉与到达率会互相拖累。",
        ],
    ),
    life(
        "loops-so",
        "Loops",
        "lifecycle-automation",
        "面向 SaaS 的轻量邮件旅程 · 事件触发友好 · 界面克制易上手",
        "https://loops.so",
        "Loops 是面向现代 SaaS 的邮件平台，把订阅名单、生命周期旅程与产品内触发邮件放在同一处，界面简洁，API 与事件触发对开发者友好。",
        "独立开发者或小型 SaaS 想用一套工具同时管好欢迎序列、留存触达与产品更新通知，又不愿配置传统营销平台那套复杂旅程时评估。",
        "深度分群与多渠道编排能力不及企业级平台；高频验证码类邮件仍建议走专用事务通道，避免拖累营销域名信誉。",
        vendorId="loops-inc",
        pricing={"model": "freemium", "currency": "USD"},
        tags=["email", "saas", "lifecycle", "developer"],
        pitfalls=[
            "分群与多渠道编排能力弱于企业级平台。",
            "验证码类高频事务邮件建议另走专用通道。",
        ],
    ),
    life(
        "customer-io",
        "Customer.io",
        "lifecycle-automation",
        "事件驱动旅程编排 · 邮件推送短信多渠道 · 依赖上游埋点质量",
        "https://customer.io",
        "Customer.io 以用户事件与属性为核心做生命周期消息编排：可视化旅程画布支持分支与等待条件，除邮件外还能发 App 推送、短信与站内消息。",
        "产品行为数据比较完整、需要按「做了什么/没做什么」触发精细的激活与留存流程时评估；只发周报通讯用它偏重。",
        "效果高度依赖上游埋点质量，数据没接好旅程就是空转；按可触达用户与消息量计价，规模化前先测算成本。",
        vendorId="customerio-inc",
        pricing={"model": "subscription", "currency": "USD"},
        tags=["email", "lifecycle", "automation", "multichannel"],
        pitfalls=[
            "旅程效果依赖埋点质量，数据不全等于空转。",
            "按可触达用户与消息量计价，规模化成本需提前测算。",
        ],
    ),
    life(
        "kit-convertkit",
        "Kit（原 ConvertKit）",
        "newsletter",
        "创作者订阅通讯 · 标签式分群与序列 · 纯文本风格转化好",
        "https://kit.com",
        "Kit（原 ConvertKit）面向创作者与独立作者，用标签与序列而不是传统名单来管理订阅者，内置落地页、表单与付费订阅能力，邮件模板偏纯文本风格。",
        "以个人品牌、课程或知识内容变现为主，需要把订阅者沉淀在自己手上并做长期序列培育时评估。",
        "电商场景与复杂事件编排能力弱；品牌改名后新旧文档、社区教程混杂，检索资料时注意分辨版本。",
        vendorId="kit-inc",
        pricing={"model": "freemium", "currency": "USD"},
        tags=["email", "newsletter", "creator", "automation"],
        pitfalls=[
            "电商与复杂事件编排能力弱于专业生命周期平台。",
            "改名后新旧资料混杂，查文档需确认是 Kit 还是 ConvertKit 时期。",
        ],
    ),
    life(
        "klaviyo",
        "Klaviyo",
        "email-marketing",
        "电商生命周期专精 · 深绑店铺订单数据 · 邮件短信同台",
        "https://www.klaviyo.com",
        "Klaviyo 面向电商做生命周期营销：直接对接店铺的订单、购物车与商品数据，按购买行为分群，并触发弃购挽回、复购提醒等邮件与短信流程。",
        "主营 DTC 或电商、销售额与邮件渠道强相关，且已经在成熟电商平台上运营时优先。",
        "非电商场景下大量模板与指标用不上，性价比偏低；与店铺数据模型绑定较深，迁出时旅程与分群基本要重建。",
        vendorId="klaviyo-inc",
        pricing={"model": "subscription", "currency": "USD"},
        tags=["email", "ecommerce", "lifecycle", "sms"],
        pitfalls=[
            "非电商场景性价比低，大量电商指标闲置。",
            "与店铺数据模型绑定深，迁出需重建旅程与分群。",
        ],
    ),
    life(
        "beehiiv",
        "beehiiv",
        "newsletter",
        "通讯增长与广告变现一体 · 推荐计划与站点托管 · 媒体化运营向",
        "https://www.beehiiv.com",
        "beehiiv 是面向新闻通讯的发布平台，除发信外还提供订阅站点托管、推荐计划、广告位撮合与增长看板，把通讯当成一门可以运营的媒体业务来做。",
        "打算把通讯做成独立媒体、关注订阅增长与广告或付费变现，而不只是给产品用户发更新时评估。",
        "偏内容媒体而非产品触达，缺少基于产品事件的旅程编排；变现能力与订阅规模强相关，早期不必为高档位付费。",
        vendorId="beehiiv-inc",
        pricing={"model": "freemium", "currency": "USD"},
        tags=["newsletter", "publishing", "growth", "monetization"],
        pitfalls=[
            "缺少基于产品事件的旅程编排，不适合做应用内生命周期触达。",
            "变现功能与订阅规模强相关，早期升档意义不大。",
        ],
    ),
    life(
        "substack",
        "Substack",
        "newsletter",
        "写作与付费订阅托管 · 平台自带发现流量 · 按订阅收入抽成",
        "https://substack.com",
        "Substack 提供从写作、发信到付费订阅的一站式托管，内置阅读器与推荐网络能带来平台内的自然曝光，商业模式是按付费订阅收入抽成而非收工具订阅费。",
        "个人作者想零配置开始写作、并顺手验证付费订阅，且愿意用部分收入换取平台生态曝光时选它。",
        "站点形态与品牌自定义受限，增长较依赖平台推荐；名单可导出，但读者关系与支付链路留在平台侧，转向独立站需要重建。",
        vendorId="substack-inc",
        pricing={"model": "freemium", "currency": "USD", "notes": "免费发信，付费订阅按比例抽成"},
        tags=["newsletter", "publishing", "subscription", "creator"],
        pitfalls=[
            "品牌与站点自定义受限，增长依赖平台推荐位。",
            "支付与读者关系在平台侧，转独立站需重建链路。",
        ],
    ),
    life(
        "buttondown",
        "Buttondown",
        "newsletter",
        "极简通讯工具 · Markdown 写作与完整 API · 数据可随时导出",
        "https://buttondown.com",
        "Buttondown 是由小团队维护的极简新闻通讯工具，用 Markdown 写作、界面克制，提供完整 API 与导入导出能力，刻意不堆砌营销功能。",
        "个人或小团队只想稳定地把文章发给订阅者，重视写作体验与数据可迁出，且不需要复杂自动化时评估。",
        "自动化、分群与团队协作能力有限；由小团队维护，选型时要接受相应的支持响应节奏与功能演进速度。",
        vendorId="buttondown-inc",
        pricing={"model": "freemium", "currency": "USD"},
        tags=["newsletter", "minimal", "markdown", "indie"],
        pitfalls=[
            "自动化与分群能力有限，复杂旅程做不了。",
            "小团队维护，支持响应与功能演进节奏偏慢。",
        ],
    ),
    life(
        "braze",
        "Braze",
        "crm-messaging",
        "企业级跨渠道触达编排 · 推送短信站内齐 · 项目制实施",
        "https://www.braze.com",
        "Braze 是面向中大型企业的客户互动平台，围绕用户档案与实时事件编排邮件、App 推送、短信与站内消息等多渠道旅程，并配套试验与内容个性化能力。",
        "以 App 为主、用户量级大且需要多渠道统一编排与团队协作治理时评估；只做邮件通讯用它明显过重。",
        "采购与实施偏企业项目制，接入成本高、周期长；数据模型与旅程配置迁移困难，选型前要想清楚长期归属。",
        vendorId="braze-inc",
        pricing={"model": "subscription", "currency": "USD"},
        maturity="mature",
        tags=["lifecycle", "multichannel", "enterprise", "push"],
        pitfalls=[
            "企业项目制实施，接入周期长、成本高。",
            "旅程与数据模型迁移困难，切换供应商代价大。",
        ],
    ),
]


ENTRIES_DATA: list[dict] = SEO_ENTRIES + EXP_ENTRIES + LIFE_ENTRIES


VENDORS_DATA: list[dict] = [
    vendor("moz-inc", "Moz", url="https://moz.com"),
    vendor("screaming-frog-ltd", "Screaming Frog", url="https://www.screamingfrog.co.uk"),
    vendor("similarweb-inc", "Similarweb", url="https://www.similarweb.com"),
    vendor("neil-patel-digital", "Neil Patel Digital", url="https://neilpatel.com"),
    vendor("wu5118-inc", "5118", region="domestic", url="https://www.5118.com"),
    vendor("aizhan-inc", "爱站网", region="domestic", url="https://www.aizhan.com"),
    vendor("launchdarkly-inc", "LaunchDarkly", url="https://launchdarkly.com"),
    vendor("statsig-inc", "Statsig", url="https://statsig.com"),
    vendor("growthbook-inc", "GrowthBook", url="https://www.growthbook.io"),
    vendor("unleash-inc", "Unleash", url="https://www.getunleash.io"),
    vendor("flagsmith-inc", "Flagsmith", url="https://www.flagsmith.com"),
    vendor("configcat-inc", "ConfigCat", url="https://configcat.com"),
    vendor("optimizely-inc", "Optimizely", url="https://www.optimizely.com"),
    vendor("cncf", "Cloud Native Computing Foundation", url="https://www.cncf.io"),
    vendor("intuit", "Intuit", url="https://www.intuit.com"),
    vendor("loops-inc", "Loops", url="https://loops.so"),
    vendor("customerio-inc", "Customer.io", url="https://customer.io"),
    vendor("kit-inc", "Kit", url="https://kit.com"),
    vendor("klaviyo-inc", "Klaviyo", url="https://www.klaviyo.com"),
    vendor("beehiiv-inc", "beehiiv", url="https://www.beehiiv.com"),
    vendor("substack-inc", "Substack", url="https://substack.com"),
    vendor("buttondown-inc", "Buttondown", url="https://buttondown.com"),
    vendor("braze-inc", "Braze", url="https://www.braze.com"),
]


EDGES_DATA: list[dict] = [
    # ——— SEO：同层互比 ———
    edge(
        "e-moz-alt-ahrefs",
        "moz",
        "ahrefs",
        "alternative_to",
        note="DA 口径与教程体系 vs 外链索引深度；两边权威度指标不可直接换算",
    ),
    edge(
        "e-ubersuggest-alt-semrush",
        "ubersuggest",
        "semrush",
        "alternative_to",
        note="低价入门档粗筛关键词 vs 全渠道营销套件；数据深度差一个量级",
    ),
    edge(
        "e-screaming-frog-alt-semrush",
        "screaming-frog",
        "semrush",
        "alternative_to",
        note="本机一次性技术抓取 vs 云端定期站点审计；前者数据不出本机",
        weight=0.6,
    ),
    edge(
        "e-screaming-frog-with-google-search-console",
        "screaming-frog",
        "google-search-console",
        "commonly_used_with",
        note="本机抓取查结构问题 + 官方索引数据看实际收录，联合定位掉量原因",
    ),
    edge(
        "e-similarweb-alt-semrush",
        "similarweb",
        "semrush",
        "alternative_to",
        note="第三方流量与受众估算 vs 关键词/广告为主的营销套件",
        weight=0.6,
    ),
    edge(
        "e-similarweb-with-ga4",
        "similarweb",
        "ga4",
        "commonly_used_with",
        note="看竞品的估算数据 vs 看自家的真实埋点数据，两者不可互相替代",
        weight=0.5,
    ),
    edge(
        "e-bing-webmaster-tools-alt-google-search-console",
        "bing-webmaster-tools",
        "google-search-console",
        "alternative_to",
        note="Bing 官方面板 vs Google 官方面板；建议并行接入而非二选一",
    ),
    edge(
        "e-baidu-search-console-cn-google-search-console",
        "baidu-search-console",
        "google-search-console",
        "domestic_equivalent_of",
        note="百度官方站长通道对应 GSC；收录判定与指标口径互不通用",
        weight=0.85,
    ),
    edge(
        "e-wu5118-cn-semrush",
        "wu5118",
        "semrush",
        "domestic_equivalent_of",
        note="中文长尾词库与国内竞品监控，对应海外关键词套件的位置",
        weight=0.75,
    ),
    edge(
        "e-aizhan-cn-moz",
        "aizhan",
        "moz",
        "domestic_equivalent_of",
        note="中文站长查询与自定义权重口径，对应 Moz 的站点权威度心智",
        weight=0.65,
    ),
    edge(
        "e-aizhan-alt-wu5118",
        "aizhan",
        "wu5118",
        "alternative_to",
        note="两家中文 SEO 数据源，权重口径不同，建议交叉验证而非只信一家",
    ),
    edge(
        "e-wu5118-with-baidu-search-console",
        "wu5118",
        "baidu-search-console",
        "commonly_used_with",
        note="第三方词库挖掘选题 + 百度官方通道提交与看收录，前者不替代后者",
        weight=0.75,
    ),
    # ——— Feature Flag / 实验 ———
    edge(
        "e-statsig-alt-launchdarkly",
        "statsig",
        "launchdarkly",
        "alternative_to",
        note="开关+实验+指标一体（按事件量） vs 开关治理专精（按席位）",
    ),
    edge(
        "e-configcat-alt-launchdarkly",
        "configcat",
        "launchdarkly",
        "alternative_to",
        note="轻量托管、计价与终端用户量脱钩 vs 企业级权限审批与审计",
    ),
    edge(
        "e-growthbook-osalt-launchdarkly",
        "growthbook",
        "launchdarkly",
        "open_source_alternative_to",
        note="开源可自托管、实验读自有数仓 vs 商业托管的开关治理平台",
    ),
    edge(
        "e-unleash-osalt-launchdarkly",
        "unleash",
        "launchdarkly",
        "open_source_alternative_to",
        note="开源开关服务端，标志求值留在自己一侧；企业治理特性在商业版",
    ),
    edge(
        "e-flagsmith-osalt-launchdarkly",
        "flagsmith",
        "launchdarkly",
        "open_source_alternative_to",
        note="开源开关+远程配置，可托管可自建；实验统计能力弱于商业方案",
    ),
    edge(
        "e-growthbook-osalt-statsig",
        "growthbook",
        "statsig",
        "open_source_alternative_to",
        note="实验分析在自有数仓执行 vs 事件送进厂商云按量计费",
        weight=0.65,
    ),
    edge(
        "e-unleash-alt-flagsmith",
        "unleash",
        "flagsmith",
        "alternative_to",
        note="专注开关基础设施 vs 开关叠远程配置、移动端下发更顺",
    ),
    edge(
        "e-unleash-int-openfeature",
        "unleash",
        "openfeature",
        "integrates_with",
        note="提供 OpenFeature Provider，应用侧可按标准接口接入",
        weight=0.75,
    ),
    edge(
        "e-flagsmith-int-openfeature",
        "flagsmith",
        "openfeature",
        "integrates_with",
        note="提供 OpenFeature Provider，便于日后更换开关后端",
        weight=0.75,
    ),
    edge(
        "e-growthbook-int-openfeature",
        "growthbook",
        "openfeature",
        "integrates_with",
        note="可通过 OpenFeature 接口接入，降低对单一开关平台的耦合",
        weight=0.7,
    ),
    edge(
        "e-posthog-alt-launchdarkly",
        "posthog",
        "launchdarkly",
        "alternative_to",
        note="分析平台自带 feature flag 的一体化省事 vs 专业化开关平台的权限、审计与规则深度",
    ),
    edge(
        "e-posthog-alt-statsig",
        "posthog",
        "statsig",
        "alternative_to",
        note="一体化：分析与开关同库；专业化：实验统计与指标引擎更完备，事件量计价",
    ),
    edge(
        "e-statsig-int-nextjs",
        "statsig",
        "nextjs",
        "integrates_with",
        note="前端/边缘侧开关求值，配合 Next.js 渲染分流做灰度",
        weight=0.55,
    ),
    edge(
        "e-datatester-cn-optimizely",
        "datatester",
        "optimizely",
        "domestic_equivalent_of",
        note="火山系 A/B 实验平台对应老牌商业实验平台；生态与计价完全不同",
        weight=0.7,
    ),
    edge(
        "e-datatester-with-sensorsdata",
        "datatester",
        "sensorsdata",
        "commonly_used_with",
        note="实验分流与读数 + 行为分析埋点；指标口径需先对齐再看实验结论",
        weight=0.55,
    ),
    # ——— 生命周期 / 邮件营销 ———
    edge(
        "e-loops-so-alt-mailchimp",
        "loops-so",
        "mailchimp",
        "alternative_to",
        note="SaaS 向轻量旅程、事件触发友好 vs 老牌营销一体机、面向运营岗",
    ),
    edge(
        "e-kit-convertkit-alt-mailchimp",
        "kit-convertkit",
        "mailchimp",
        "alternative_to",
        note="创作者标签+序列模型 vs 传统名单+模板模型",
    ),
    edge(
        "e-klaviyo-alt-mailchimp",
        "klaviyo",
        "mailchimp",
        "alternative_to",
        note="电商深绑订单与购物车数据 vs 通用营销名单工具",
    ),
    edge(
        "e-mailchimp-alt-brevo",
        "mailchimp",
        "brevo",
        "alternative_to",
        note="纯营销一体机 vs 营销与事务发信合一的欧洲平台",
        weight=0.6,
    ),
    edge(
        "e-customer-io-alt-braze",
        "customer-io",
        "braze",
        "alternative_to",
        note="事件驱动、中量级可自助接入 vs 企业级多渠道、项目制实施",
    ),
    edge(
        "e-beehiiv-alt-substack",
        "beehiiv",
        "substack",
        "alternative_to",
        note="自有站点与广告/推荐增长工具箱 vs 平台托管、按订阅收入抽成",
    ),
    edge(
        "e-buttondown-alt-beehiiv",
        "buttondown",
        "beehiiv",
        "alternative_to",
        note="极简写作与数据可迁出 vs 媒体化增长与变现工具箱",
    ),
    edge(
        "e-substack-alt-kit-convertkit",
        "substack",
        "kit-convertkit",
        "alternative_to",
        note="平台托管带发现流量 vs 名单与付费关系握在自己手里",
    ),
    edge(
        "e-loops-so-with-resend",
        "loops-so",
        "resend",
        "commonly_used_with",
        note="营销/生命周期名单与旅程 vs 事务邮件发信 API；两类邮件分账号分域名，别混选",
        weight=0.6,
    ),
    edge(
        "e-mailchimp-alt-sendgrid",
        "mailchimp",
        "sendgrid",
        "alternative_to",
        note="营销邮件（名单、模板、自动化） vs 事务邮件 API（验证码、账单）；同属发信但选型口径不同",
        weight=0.55,
    ),
    edge(
        "e-braze-with-segment",
        "braze",
        "segment",
        "commonly_used_with",
        note="CDP 统一用户档案与事件 → 触达平台负责多渠道编排",
        weight=0.7,
    ),
    edge(
        "e-customer-io-with-segment",
        "customer-io",
        "segment",
        "commonly_used_with",
        note="埋点与身份统一在 CDP，旅程条件直接引用同一份事件口径",
        weight=0.7,
    ),
    edge(
        "e-customer-io-with-posthog",
        "customer-io",
        "posthog",
        "commonly_used_with",
        note="产品分析定义人群与留存指标 → 生命周期平台执行触达",
        weight=0.55,
    ),
    edge(
        "e-loops-so-with-stripe",
        "loops-so",
        "stripe",
        "commonly_used_with",
        note="订阅与支付事件触发续费提醒、失败挽回等生命周期邮件",
        weight=0.55,
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

    print(
        f"done entries={wrote_e}(skip {skipped_e}) "
        f"vendors={wrote_v}(skip {skipped_v}) edges={wrote_g}(skip {skipped_g})"
    )


if __name__ == "__main__":
    main()
