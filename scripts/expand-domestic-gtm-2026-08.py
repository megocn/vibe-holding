#!/usr/bin/env python3
"""近期 GTM 叶国内短名单补种（2026-08-07）。

仅补「有清晰国内外对标轴」的优质国内基建，遵守扩种准入原则；
弱赛道（无短名单级产品）宁缺。边用 domestic_equivalent_of → 海外锚点。

覆盖：
- net-media：七牛 / 又拍 / 腾讯云点播 / 火山 ImageX
- collab-crm：纷享销客 / 销售易 / 悟空 CRM
- collab-community：小鹅通 / 知识星球
- growth-forms：金数据 / 问卷星
- growth-feedback：兔小巢
- growth-social：新榜（微信内容运营轴，非欧美全网排期）
- cicd-automation：集简云 / 腾讯轻联 HiFlow
- collab-scheduling：飞书预约（边挂既有 feishu，不拆条）
- growth-affiliate / msg-orchestration / collab-async-capture /
  sec-privacy-legal：无足够优质独立短名单，本轮不硬凑

用法:
  python3 scripts/expand-domestic-gtm-2026-08.py
  python3 scripts/expand-domestic-gtm-2026-08.py --overwrite
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
        "availability": dict(DOMESTIC),
        "tags": [],
        "maturity": "stable",
        "pitfalls": [],
        "updates": [],
        "rankings": [],
        "sources": [],
        "lastReviewed": REVIEWED,
        "region": "domestic",
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


def edge(eid, frm, to, typ, weight=0.75, confidence="community", note=None):
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


def vendor(vid, name, region="domestic", url=None):
    v = {"id": vid, "name": name, "region": region}
    if url:
        v["url"] = url
    return v


ENTRIES_DATA: list[dict] = [
    # ——— 媒体 CDN ———
    mk(
        "net-media",
        "qiniu",
        "七牛云",
        "media-platform",
        "对象存储+图片视频处理 · 开发者向 · 国内媒体管道常用",
        "https://www.qiniu.com",
        "七牛云提供对象存储、CDN 与图片/音视频处理能力，API/SDK 面向开发者，常作为国内把上传、变换与投递串成一条媒体管道的默认底座之一。",
        "用户图片/短视频要落在国内节点、需要处理工作流与对象存储一体、对标 Cloudinary「开发者媒体底座」时评估。",
        "海外节点与全球品牌 DAM 深度弱于 Cloudinary；计费含存储、流量与处理，需拆账单对照。",
        vendorId="qiniu-inc",
        pricing={"model": "usage", "currency": "CNY"},
        maturity="mature",
        tags=["image", "video", "cdn", "storage", "domestic"],
        pitfalls=[
            "海外访问与全球 DAM 能力不及 Cloudinary。",
            "流量+处理叠加计费，要按峰值预估。",
        ],
    ),
    mk(
        "net-media",
        "upyun",
        "又拍云",
        "image-cdn",
        "存储+CDN+图片处理一体 · 中小站性价比 · 上手快",
        "https://www.upyun.com",
        "又拍云面向国内中小站与内容业务，把云存储、CDN 与图片处理放到同一控制台，强调易用与阶梯计价性价比，常见于图床、静态资源与轻量媒体交付而不是全球 DAM 套件。",
        "团队以国内流量为主、希望少组件拼装、对照七牛做价格与面板体验时评估；重度长视频流水线另看云厂商点播产品。",
        "大客户节点与定制能力因套餐而异；海外边缘与全球品牌体验弱于国际媒体 CDN。",
        vendorId="upyun-inc",
        pricing={"model": "usage", "currency": "CNY"},
        maturity="mature",
        tags=["image", "cdn", "storage", "domestic"],
        pitfalls=[
            "全球节点与企业定制深度通常弱于云巨头。",
            "视频长流业务能力需与点播产品对照。",
        ],
    ),
    mk(
        "net-media",
        "tencent-vod",
        "腾讯云点播",
        "video-api",
        "视频上传转码播放 · 腾讯云同栈 · 国内点播默认候选",
        "https://cloud.tencent.com/product/vod",
        "腾讯云点播（VOD）提供媒资上传、转码、自适应播放与分发，深度嵌入腾讯云账号体系与 CDN，定位国内「视频即服务」流水线，而不是全能图像 DAM 或通用对象存储。",
        "小程序/App 回放、课程与短视频要国内合规与节点、对照 Mux 开发者视频基建时评估；图变换请并行看 ImageX/七牛。",
        "与账号体系、备案与按量计费模型绑定；纯海外观众节点策略与账单结构要另评估。",
        vendorId="tencent",
        pricing={"model": "usage", "currency": "CNY"},
        maturity="mature",
        tags=["video", "streaming", "cloud", "domestic"],
        pitfalls=[
            "需腾讯云账号与国内合规流程（备案等场景相关）。",
            "不是图像 URL 变换主产品，图仍要 ImageX/七牛等。",
        ],
    ),
    mk(
        "net-media",
        "volcengine-imagex",
        "火山引擎 ImageX",
        "image-cdn",
        "字节系图片处理与分发 · 大流量图站向 · 与点播拆分",
        "https://www.volcengine.com/product/ImageX",
        "火山引擎 ImageX 面向海量图片的处理、存储与分发，强调处理能力与高并发投递，常与字节云数据分析等产品同栈，是国内「图 CDN + 实时处理」轴上的头部候选之一。",
        "图片量级大、已在火山/字节系技术栈或要与 DataTester 等同栈时评估；通用小站可先评估七牛或又拍。",
        "产品线学习曲线与计费项偏多；非字节生态集成与迁移成本要实测。",
        vendorId="bytedance",
        pricing={"model": "usage", "currency": "CNY"},
        tags=["image", "cdn", "transform", "domestic"],
        pitfalls=[
            "计费项与配置面较多，小流量场景可能过重。",
            "与非字节栈集成文档路径要预留联调。",
        ],
    ),
    # ——— CRM ———
    mk(
        "collab-crm",
        "fxiaoke",
        "纷享销客",
        "suite-crm",
        "连接型国产 CRM 头部 · 渠道/协同强 · 中大盘默认",
        "https://www.fxiaoke.com",
        "纷享销客是国产 CRM 第一梯队产品，强调连接型架构：销售、渠道、服务与协同，支持 SaaS 与私有化，服务网络覆盖国内多地，面向中大型组织复杂客户经营。",
        "国内中大型团队要本地化交付、渠道与上下游连接、对照 HubSpot「套件默认」轴时评估；轻量灵活对象可看海外 Attio 或悟空。",
        "采购与实施偏项目制，小团队易过重；价格随模块与私有化走。",
        vendorId="fxiaoke-inc",
        pricing={"model": "subscription", "currency": "CNY"},
        maturity="mature",
        tags=["crm", "enterprise", "domestic", "saas"],
        pitfalls=[
            "实施与模块组合使总拥有成本难一次看清。",
            "Indie 小团队通常过重，勿当轻量起盘默认。",
        ],
    ),
    mk(
        "collab-crm",
        "xiaoshouyi",
        "销售易",
        "pipeline-crm",
        "B2B 流程与 PaaS 定制 · 销售颗粒度细 · 中大型向",
        "https://www.xiaoshouyi.com",
        "销售易深耕 B2B 销售过程管理与 PaaS 定制：线索到回款链路颗粒度细，移动端与行业方案成熟，适合流程规范、要深度配置的中大型国内企业。",
        "项目型/长周期 B2B 销售、需要 PaaS 扩展时与纷享销客对照；要现代灵活对象小团队可看 Attio，开源自托管看悟空。",
        "定制能力强也意味着实施周期与顾问成本；小微线性管道可先 Pipedrive 类轻量。",
        vendorId="xiaoshouyi-inc",
        pricing={"model": "subscription", "currency": "CNY"},
        maturity="mature",
        tags=["crm", "b2b", "paas", "domestic"],
        pitfalls=[
            "PaaS 定制投入大，范围失控会拖实施。",
            "非国内交付网络的出海团队生态不如 Salesforce。",
        ],
    ),
    mk(
        "collab-crm",
        "wukong-crm",
        "悟空 CRM",
        "open-source-crm",
        "国产开源 CRM · 可私有化 · 中小团队成本敏感向",
        "https://www.5kcrm.com",
        "悟空 CRM 提供开源/可私有化的客户与销售管理能力，面向预算敏感与要数据驻留的中小团队，是国内开源 CRM 常见入口之一，对照 Twenty 的「开源 CRM」轴。",
        "要私有化、许可成本可控、功能以管道与客户档案为主时评估；企业级连接与行业方案仍看纷享/销售易。",
        "polish 与连接器广度弱于商业 SaaS；版本与社区/商业授权路径需分清。",
        vendorId="wukong-crm-inc",
        githubUrl="https://github.com/WuKongOpenSource/Wukong_OpenSource_CRM",
        pricing={"model": "open-source", "currency": "CNY", "notes": "开源版与商业版并存，以官网为准"},
        tags=["crm", "open-source", "self-hosted", "domestic"],
        pitfalls=[
            "开源与商业版边界、升级路径要进官网核实。",
            "企业集成与 polish 不及头部 SaaS。",
        ],
    ),
    # ——— 社区 ———
    mk(
        "collab-community",
        "xiaoe-tech",
        "小鹅通",
        "membership-community",
        "微信私域知识店铺 · 课程直播社群 · Circle 国内对位",
        "https://www.xiaoe-tech.com",
        "小鹅通是国内知识付费与私域经营 SaaS：课程、直播、训练营、店铺与社群（鹅圈子）装在同一产品里，深度挂接微信生态，服务创作者、讲师与教育机构做私域变现。",
        "要在微信侧卖课、跑训练营与会员、对照 Circle 托管会员社区时优先；纯付费问答型轻社群可看知识星球，可索引公开论坛看 Discourse。",
        "年费与支付通道费叠加；品牌与数据边界受微信平台规则强约束。",
        vendorId="xiaoe-inc",
        pricing={"model": "subscription", "currency": "CNY"},
        maturity="mature",
        tags=["community", "courses", "wechat", "domestic"],
        pitfalls=[
            "重度依赖微信生态规则与支付通道。",
            "功能包多，范围失控会变成重运营系统。",
        ],
    ),
    mk(
        "collab-community",
        "zsxq",
        "知识星球",
        "membership-community",
        "付费星友社群 · 低启动验证 · 内容沉淀强于课销",
        "https://www.zsxq.com",
        "知识星球主打付费会员社群：星主更新内容、问答互动、资料沉淀与续费关系，启动成本通常低于完整课程 SaaS，适合先用社群验证知识服务再扩课销体系。",
        "专家/创作者要轻量付费社群、对照小鹅通重课销与 Circle 会员空间时评估；要 SEO 友好的公开论坛请用 Discourse。",
        "以订单服务费/抽成为主；标准化课程直播与店铺经营能力明显弱于小鹅通。",
        vendorId="zsxq-inc",
        pricing={"model": "usage", "currency": "CNY", "notes": "平台服务费+通道费模式，以官网为准"},
        maturity="mature",
        tags=["community", "membership", "creators", "domestic"],
        pitfalls=[
            "课销与直播交付弱，做大课需另接系统。",
            "平台抽成与规则变化会影响利润测算。",
        ],
    ),
    # ——— 表单 ———
    mk(
        "growth-forms",
        "jinshuju",
        "金数据",
        "form-builder",
        "国内业务表单默认 · 报名收款预约 · 企微钉钉飞书集成",
        "https://www.jinshuju.net",
        "金数据面向国内团队做在线表单与业务数据收集：报名、问卷、预约、收款与对外查询页，并深度对接微信/企微/钉钉/飞书，定位业务表单而非纯学术考试系统。",
        "国内运营要可收款的报名与办公套件联动、对照 Tally/Typeform 时优先；海量考试测评与科研问卷可看问卷星。",
        "高级 API 与去品牌在更高档；跨境多语言与海外支付链路弱于国际产品。",
        vendorId="jinshuju-inc",
        pricing={"model": "freemium", "currency": "CNY"},
        maturity="mature",
        tags=["forms", "survey", "domestic", "saas"],
        pitfalls=[
            "企业 API 与品牌自定义多在付费档。",
            "出海多币种收款与合规模板需另评估。",
        ],
    ),
    mk(
        "growth-forms",
        "wenjuanxing",
        "问卷星",
        "form-builder",
        "问卷考试研究向头部 · 题型与样本生态 · 高校企业广覆盖",
        "https://www.wjx.cn",
        "问卷星以问卷调查、在线考试与测评见长，题型库与结果分析能力强，覆盖国内大多数高校与大量企业调研场景，也可承载报名表，但产品心智更偏「调研/考试」而非收款预约一体的业务表单。",
        "学术调研、培训结业考试、大规模问卷回收与需要题库能力时评估；偏业务收款、预约与对外查询闭环更常见选金数据。",
        "企业隐私、样本服务与数据出境相关条款要细读；复杂系统 webhook/API 集成弱于开发者向表单产品。",
        vendorId="ranxing-inc",
        pricing={"model": "freemium", "currency": "CNY"},
        maturity="mature",
        tags=["forms", "survey", "exam", "domestic"],
        pitfalls=[
            "业务收款/预约闭环不如金数据顺。",
            "样本与企业合规条款需按行业自查。",
        ],
    ),
    # ——— 反馈 ———
    mk(
        "growth-feedback",
        "tuxiaochao",
        "腾讯兔小巢",
        "feature-voting",
        "腾讯出品轻量反馈社区 · 嵌入快 · 微信回复触达",
        "https://txc.qq.com",
        "兔小巢是腾讯推出的用户意见反馈社区，可嵌入 App/H5/小程序/公众号，支持分类、回复与微信触达，定位轻量「用户声音墙」，非完整 PM 路线图套件。",
        "国产应用要快速挂反馈入口、微信侧触达用户、对照 Canny/Fider 轻量反馈轴时评估；完整投票路线图与 Changelog 一体仍看 Canny/Featurebase。",
        "已结束纯免费策略，需按套餐评估；企业级产品组合管理弱。",
        vendorId="tencent",
        pricing={"model": "subscription", "currency": "CNY", "notes": "曾长期免费，现已收费，以官网为准"},
        tags=["feedback", "community", "domestic", "wechat"],
        pitfalls=[
            "已商业化收费，免费心智不能再当默认。",
            "不是 Productboard 级洞察与路线图工作台。",
        ],
    ),
    # ——— 社媒 / 内容运营（国内轴，非 Buffer 全网排期）———
    mk(
        "growth-social",
        "newrank",
        "新榜",
        "content-ops",
        "微信等内容数据与榜单 · 运营决策向 · 非多平台一键排期",
        "https://www.newrank.cn",
        "新榜提供微信公众号等内容渠道的数据、榜单与运营分析，帮助团队做选题与账号诊断，主轴是「内容数据与行业对照」，而不是 Buffer 式多平台可视化排期日历。",
        "国内公号/内容团队要看账号数据与行业位置、找欧美排期工具的国内决策侧输入时评估；多平台一键发帖仍看 Postiz 等或各平台原生后台。",
        "勿与欧美社媒排期工具直接等价；数据源与指标口径受平台限制。",
        vendorId="newrank-inc",
        pricing={"model": "subscription", "currency": "CNY"},
        maturity="mature",
        tags=["social", "wechat", "analytics", "domestic"],
        pitfalls=[
            "不是多平台排期发帖工具，轴不同勿硬替 Buffer。",
            "第三方数据与平台官方后台口径可能不一致。",
        ],
    ),
    # ——— 自动化 ———
    mk(
        "cicd-automation",
        "jijyun",
        "集简云",
        "ipaas",
        "国内零代码 iPaaS · 钉钉飞书企微连接厚 · Zapier 对位",
        "https://www.jijyun.cn",
        "集简云是面向国内企业的零代码集成与自动化平台，连接钉钉、飞书、企微与大量本土 SaaS，用可视化流程做同步与触发，定位接近 Zapier 的国内业务自动化入口。",
        "流程在国内 SaaS 之间跑、对接人要求低、对照 Zapier/Make 时优先；开发者代码步骤可看 Pipedream，自托管 fair-code 看 n8n。",
        "复杂高并发与深度 API 治理弱于企业 iPaaS；连接器以本土应用为主。",
        vendorId="jijyun-inc",
        pricing={"model": "freemium", "currency": "CNY"},
        tags=["automation", "ipaas", "nocode", "domestic"],
        pitfalls=[
            "企业级吞吐与治理能力弱于重型 iPaaS。",
            "海外长尾 SaaS 连接器可能不如 Zapier 目录全。",
        ],
    ),
    mk(
        "cicd-automation",
        "tencent-hiflow",
        "腾讯轻联 HiFlow",
        "ipaas",
        "腾讯系场景连接器 · 与腾讯云/微信生态近 · 轻量自动化",
        "https://hiflow.tencent.com",
        "腾讯轻联（HiFlow）提供场景化连接与自动化，把腾讯系与常见应用事件串成流程，适合已在腾讯云/微信生态的团队做轻量集成，而不是全球连接器目录最长的 iPaaS。",
        "事件在腾讯系产品与国内 SaaS 之间流转、想少运维时评估；连接器广度优先仍可看集简云与 Zapier。",
        "生态偏向腾讯栈；复杂企业总线与私有协议要另上集成平台。",
        vendorId="tencent",
        pricing={"model": "freemium", "currency": "CNY"},
        tags=["automation", "ipaas", "tencent", "domestic"],
        pitfalls=[
            "非腾讯栈连接深度可能不足。",
            "勿当作全功能企业 ESB/iPaaS。",
        ],
    ),
]

VENDORS_DATA = [
    vendor("qiniu-inc", "七牛云", url="https://www.qiniu.com"),
    vendor("upyun-inc", "又拍云", url="https://www.upyun.com"),
    vendor("fxiaoke-inc", "纷享销客", url="https://www.fxiaoke.com"),
    vendor("xiaoshouyi-inc", "销售易", url="https://www.xiaoshouyi.com"),
    vendor("wukong-crm-inc", "悟空软件", url="https://www.5kcrm.com"),
    vendor("xiaoe-inc", "小鹅通", url="https://www.xiaoe-tech.com"),
    vendor("zsxq-inc", "知识星球", url="https://www.zsxq.com"),
    vendor("jinshuju-inc", "金数据", url="https://www.jinshuju.net"),
    vendor("ranxing-inc", "冉星信息（问卷星）", url="https://www.wjx.cn"),
    vendor("newrank-inc", "新榜", url="https://www.newrank.cn"),
    vendor("jijyun-inc", "集简云", url="https://www.jijyun.cn"),
]

EDGES_DATA = [
    # media
    edge(
        "e-qiniu-dom-cloudinary",
        "qiniu",
        "cloudinary",
        "domestic_equivalent_of",
        note="国内开发者媒体存储处理底座 vs 全球 Cloudinary 全栈媒体/DAM",
    ),
    edge(
        "e-upyun-dom-cloudinary",
        "upyun",
        "cloudinary",
        "domestic_equivalent_of",
        note="国内存储+图处理性价比一体 vs Cloudinary 全球能力",
        weight=0.65,
    ),
    edge(
        "e-upyun-alt-qiniu",
        "upyun",
        "qiniu",
        "alternative_to",
        note="面板与性价比向 vs 开发者媒体管道向",
        weight=0.7,
    ),
    edge(
        "e-tencent-vod-dom-mux",
        "tencent-vod",
        "mux",
        "domestic_equivalent_of",
        note="国内云点播转码播放 vs Mux 开发者视频基建",
    ),
    edge(
        "e-volcengine-imagex-dom-imgix",
        "volcengine-imagex",
        "imgix",
        "domestic_equivalent_of",
        note="字节系海量图处理分发 vs imgix URL 实时变换",
        weight=0.7,
    ),
    edge(
        "e-volcengine-imagex-alt-qiniu",
        "volcengine-imagex",
        "qiniu",
        "alternative_to",
        note="大流量图站/字节栈 vs 通用开发者媒体底座",
        weight=0.65,
    ),
    # crm
    edge(
        "e-fxiaoke-dom-hubspot",
        "fxiaoke",
        "hubspot",
        "domestic_equivalent_of",
        note="国产连接型 CRM 套件默认 vs HubSpot 增长套件默认",
    ),
    edge(
        "e-xiaoshouyi-dom-hubspot",
        "xiaoshouyi",
        "hubspot",
        "domestic_equivalent_of",
        note="B2B 流程+PaaS 国产 CRM vs HubSpot 营销销售套件",
        weight=0.7,
    ),
    edge(
        "e-xiaoshouyi-alt-fxiaoke",
        "xiaoshouyi",
        "fxiaoke",
        "alternative_to",
        note="流程颗粒与 PaaS vs 连接/渠道与协同",
        weight=0.75,
    ),
    edge(
        "e-wukong-crm-dom-twenty",
        "wukong-crm",
        "twenty",
        "domestic_equivalent_of",
        note="国产开源/可私有化 CRM vs Twenty 开源现代 CRM",
    ),
    edge(
        "e-wukong-crm-osalt-fxiaoke",
        "wukong-crm",
        "fxiaoke",
        "open_source_alternative_to",
        note="开源私有化成本敏感 vs 商业连接型 CRM",
        weight=0.65,
    ),
    # community
    edge(
        "e-xiaoe-tech-dom-circle-so",
        "xiaoe-tech",
        "circle-so",
        "domestic_equivalent_of",
        note="微信私域课程店铺+社群 vs Circle 托管会员社区",
    ),
    edge(
        "e-zsxq-dom-circle-so",
        "zsxq",
        "circle-so",
        "domestic_equivalent_of",
        note="轻量付费星友社群 vs Circle 会员空间（交付形态不同）",
        weight=0.65,
    ),
    edge(
        "e-zsxq-alt-xiaoe-tech",
        "zsxq",
        "xiaoe-tech",
        "alternative_to",
        note="低启动付费社群验证 vs 完整课销与训练营系统",
        weight=0.75,
    ),
    edge(
        "e-xiaoe-tech-alt-discourse",
        "xiaoe-tech",
        "discourse",
        "alternative_to",
        note="私域付费经营 vs 公开可索引论坛",
        weight=0.5,
    ),
    # forms
    edge(
        "e-jinshuju-dom-tally",
        "jinshuju",
        "tally",
        "domestic_equivalent_of",
        note="国内业务表单+办公套件集成 vs Tally 慷慨免费国际表单",
    ),
    edge(
        "e-jinshuju-dom-typeform",
        "jinshuju",
        "typeform",
        "domestic_equivalent_of",
        note="业务报名收款向 vs 对话式品牌问卷",
        weight=0.6,
    ),
    edge(
        "e-wenjuanxing-dom-typeform",
        "wenjuanxing",
        "typeform",
        "domestic_equivalent_of",
        note="国内问卷考试研究头部 vs Typeform 对话式体验",
        weight=0.65,
    ),
    edge(
        "e-wenjuanxing-alt-jinshuju",
        "wenjuanxing",
        "jinshuju",
        "alternative_to",
        note="调研考试分析强 vs 业务表单收款预约强",
        weight=0.75,
    ),
    # feedback
    edge(
        "e-tuxiaochao-dom-canny",
        "tuxiaochao",
        "canny",
        "domestic_equivalent_of",
        note="腾讯轻量反馈社区 vs Canny 投票/路线图产品",
        weight=0.65,
    ),
    edge(
        "e-tuxiaochao-dom-fider",
        "tuxiaochao",
        "fider",
        "domestic_equivalent_of",
        note="托管轻量反馈入口 vs Fider 开源投票板",
        weight=0.6,
    ),
    # social (axis caution)
    edge(
        "e-newrank-dom-buffer",
        "newrank",
        "buffer",
        "domestic_equivalent_of",
        note="微信等内容数据/运营决策（非一键排期）vs Buffer 多平台日历；轴不同需读 note",
        weight=0.45,
    ),
    # automation
    edge(
        "e-jijyun-dom-zapier",
        "jijyun",
        "zapier",
        "domestic_equivalent_of",
        note="国内零代码连接钉飞书企微等 vs Zapier 全球 iPaaS",
    ),
    edge(
        "e-tencent-hiflow-dom-zapier",
        "tencent-hiflow",
        "zapier",
        "domestic_equivalent_of",
        note="腾讯系场景连接器 vs Zapier 通用自动化",
        weight=0.65,
    ),
    edge(
        "e-tencent-hiflow-alt-jijyun",
        "tencent-hiflow",
        "jijyun",
        "alternative_to",
        note="腾讯生态轻量连接 vs 更广国内 SaaS 目录",
        weight=0.7,
    ),
    edge(
        "e-jijyun-alt-n8n",
        "jijyun",
        "n8n",
        "alternative_to",
        note="托管零代码国内连接 vs 可自托管节点工作流",
        weight=0.6,
    ),
    # scheduling: existing feishu
    edge(
        "e-feishu-dom-calendly",
        "feishu",
        "calendly",
        "domestic_equivalent_of",
        note="飞书日历一对一/轮流预约（套件能力）vs Calendly 独立预约页",
        weight=0.7,
    ),
    edge(
        "e-feishu-with-cal-com",
        "feishu",
        "cal-com",
        "alternative_to",
        note="套件内预约 vs 开源可自托管独立预约基建",
        weight=0.55,
    ),
    # soft multi-channel notify: existing getui
    edge(
        "e-getui-dom-knock",
        "getui",
        "knock",
        "domestic_equivalent_of",
        note="国内推送通道头部（渠道层）vs Knock 多渠道通知编排；层不同",
        weight=0.45,
    ),
    edge(
        "e-jpush-dom-novu",
        "jpush",
        "novu",
        "domestic_equivalent_of",
        note="极光推送通道 vs Novu 开源编排；通道≠编排中台",
        weight=0.45,
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
        except AssertionError as err:
            issues.append(str(err))
    if issues:
        for i in issues:
            print("INVALID", i)
        raise SystemExit(f"{len(issues)} failures")

    assert len({e["id"] for e in ENTRIES_DATA}) == len(ENTRIES_DATA)
    assert len({g["id"] for g in EDGES_DATA}) == len(EDGES_DATA)

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

    known = {x["id"] for x in ENTRIES_DATA}
    for g in EDGES_DATA:
        path = EDGES / f"{g['id']}.json"
        if path.exists() and not args.overwrite:
            sg += 1
            continue
        if not ((ENTRIES / f"{g['from']}.json").exists() or g["from"] in known):
            print("skip edge missing from", g["id"], g["from"])
            continue
        if not ((ENTRIES / f"{g['to']}.json").exists() or g["to"] in known):
            print("skip edge missing to", g["id"], g["to"])
            continue
        save(path, g)
        wg += 1
        print("edge", g["id"])

    print(f"done entries={we}(skip {se}) vendors={wv}(skip {sv}) edges={wg}(skip {sg})")


if __name__ == "__main__":
    main()
