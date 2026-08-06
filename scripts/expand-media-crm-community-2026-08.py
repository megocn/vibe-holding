#!/usr/bin/env python3
"""GTM 侧五域扩叶扩种（2026-08-06）。

遵守 content/README.md「扩种准入原则」：短名单级、最新可复核、各轴最佳，宁缺毋滥。

- net-media：Cloudinary / Mux / imgix / ImageKit
- collab-crm：Attio / HubSpot / Pipedrive / Twenty
- collab-community：Discourse / Circle / Flarum（+ 边连既有 discord）
- sec-privacy-legal：迁移 termly / iubenda / cookiebot / onetrust（不重造）
- collab-async-capture：Loom / Marker / Jam（不吞 session replay）

用法:
  python3 scripts/expand-media-crm-community-2026-08.py
  python3 scripts/expand-media-crm-community-2026-08.py --overwrite
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

CAT_MEDIA = "net-media"
CAT_CRM = "collab-crm"
CAT_COMM = "collab-community"
CAT_PRIV = "sec-privacy-legal"
CAT_ASYNC = "collab-async-capture"

PRIVACY_MIGRATE = ("termly", "iubenda", "cookiebot", "onetrust")


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


# ——— 媒体处理 CDN ———
MEDIA = [
    mk(
        CAT_MEDIA,
        "cloudinary",
        "Cloudinary",
        "media-platform",
        "图像+视频变换/DAM 一体 · AI 变换深 · 全栈默认但账单陡",
        "https://cloudinary.com",
        "Cloudinary 是全栈媒体平台：上传、存储、URL/API 实时变换、优化投递与 DAM，覆盖图与视频，并提供生成式裁切、去背等 AI 能力，常被当作媒体管道的默认采购位。",
        "产品需要智能裁切、叠加层、多格式自适应与统一资产库，愿意接受 credit/用量型计价时评估；只要视频流水线看 Mux，只要廉价图优化看 ImageKit/imgix。",
        "变换与带宽 credit 模型易在流量上来后跳涨；功能面宽，误用会把简单交付做成重平台。",
        vendorId="cloudinary-inc",
        pricing={"model": "freemium", "currency": "USD"},
        maturity="mature",
        tags=["image", "video", "cdn", "dam", "transform"],
        pitfalls=[
            "credit/用量模型下带宽与变换叠加会账单陡升。",
            "能力过多，团队缺规范时易把交付做成重 DAM。",
        ],
    ),
    mk(
        CAT_MEDIA,
        "mux",
        "Mux",
        "video-api",
        "开发者视频基础设施 · 上传转码播放 API · 不兼 DAM",
        "https://www.mux.com",
        "Mux 面向开发者提供视频上传、转码、自适应播放与数据分析 API/SDK，定位是「把视频当基础设施接入」，而不是通用图像变换或营销 DAM。",
        "用户生成视频、课程回放、产品内嵌播放器需要可靠转码与播放数据时优先；图站与多格式静态资源请用 Cloudinary/imgix/ImageKit。",
        "视频分钟与 CDN 出站按量计费，热门内容要预算；不覆盖图库/DAM 全流程。",
        vendorId="mux-inc",
        pricing={"model": "usage", "currency": "USD"},
        tags=["video", "streaming", "api", "developer"],
        pitfalls=[
            "按编码分钟与观众分钟计费，爆款时要控清晰度与缓存。",
            "不是图像 CDN，图与 DAM 仍要另选。",
        ],
    ),
    mk(
        CAT_MEDIA,
        "imgix",
        "imgix",
        "image-cdn",
        "URL 实时图像变换标杆 · 接已有对象存储 · 媒体站向",
        "https://www.imgix.com",
        "imgix 以 URL 参数驱动的实时图像渲染与全球投递见长，可挂在自有 S3/GCS 等源站之上，强调色彩与渲染品质，常见于内容与电商图站而非全能 DAM。",
        "已有对象存储、只要高质量点选裁切与格式协商、且流量规模值得专业图 CDN 时评估；要一体化上传+AI 工作流看 Cloudinary。",
        "入门带宽档偏贵；长视频不是主场，完整视频流水线另看 Mux。",
        vendorId="imgix-inc",
        pricing={"model": "usage", "currency": "USD"},
        maturity="mature",
        tags=["image", "cdn", "transform", "performance"],
        pitfalls=[
            "带宽起价与最低消费对小站不友好。",
            "视频与 DAM 深度不及 Cloudinary / Mux。",
        ],
    ),
    mk(
        CAT_MEDIA,
        "imagekit",
        "ImageKit",
        "image-cdn",
        "开发者图视频 CDN · 性价比 Cloudinary 对照 · DAM 可选",
        "https://imagekit.io",
        "ImageKit 提供实时变换、优化投递与可选 DAM，API 面接近 imgix/Cloudinary 路径，计价往往以带宽为主，常被当作 Cloudinary 的中档对照与 imgix 风格 drop-in。",
        "需要 URL 变换与中等流量账单可预期、又想可选资产库时评估；极端 AI 生成式变换与企业 DAM 流程仍是 Cloudinary 强项。",
        "AI/生成式能力与生态插件深度不及头部；选型前按真实变换矩阵压测。",
        vendorId="imagekit-inc",
        pricing={"model": "freemium", "currency": "USD"},
        tags=["image", "video", "cdn", "transform"],
        pitfalls=[
            "复杂 AI 变换与企业 DAM 深度弱于 Cloudinary。",
            "视频长流媒体仍建议专用视频栈对照 Mux。",
        ],
    ),
]

# ——— CRM ———
CRM = [
    mk(
        CAT_CRM,
        "attio",
        "Attio",
        "modern-crm",
        "灵活对象模型 + AI · 202x B2B 现代 CRM · 三席免费档",
        "https://attio.com",
        "Attio 是面向现代 B2B 团队的 CRM：自定义对象与关系、邮件日历同步、enrichment 与 AI 问询，强调用你的数据模型运转，而不是塞进固定销售漏斗模板。",
        "种子到成长期 SaaS 要可塑对象、关系洞察与 AI 辅助跟进、又不想一上来上营销套件时优先；纯视觉管道可看 Pipedrive，要营销+销售一体看 HubSpot。",
        "高阶自动化与呼叫智能多在付费档；超大销售机队与强合规采购仍可能走 Salesforce 路线。",
        vendorId="attio-inc",
        pricing={"model": "freemium", "currency": "USD"},
        tags=["crm", "b2b", "ai", "saas"],
        pitfalls=[
            "高级序列与通话智能能力随档位解锁，报价要按席位+功能核。",
            "超大企业采购与行业合规模板不如老牌全栈。",
        ],
    ),
    mk(
        CAT_CRM,
        "hubspot",
        "HubSpot",
        "suite-crm",
        "营销销售客服套件锚点 · 免费 CRM 起盘 · 席位升级账单高",
        "https://www.hubspot.com",
        "HubSpot 以免费 CRM 起盘，向上打包 Marketing/Sales/Service Hub，把线索、管道、邮件、落地页与客服放在同一套件——是增长团队的套件默认项，而不是「极简轻 CRM」新锐。",
        "同时要 inbound 内容、营销自动化与销售管道、可接受套件绑定与席位单价时评估；只想灵活对象模型优先 Attio，只要看板管道优先 Pipedrive。",
        "报告、自动化与多 Hub 功能升级后费用跳升快；套件锁定迁移成本高。",
        vendorId="hubspot-inc",
        pricing={"model": "freemium", "currency": "USD"},
        maturity="mature",
        tags=["crm", "marketing", "suite", "saas"],
        pitfalls=[
            "进阶自动化与报告往往要跨 Hub 付费，总账易失控。",
            "数据与流程深度绑套件后迁移贵。",
        ],
    ),
    mk(
        CAT_CRM,
        "pipedrive",
        "Pipedrive",
        "pipeline-crm",
        "视觉交易管道极简 · 销售自管向 · 少对象建模",
        "https://www.pipedrive.com",
        "Pipedrive 围绕「交易从左到右过管道」设计：可视化看板、活动提醒与销售报告，配置面刻意窄，适合流程线性的销售个人或小团队。",
        "outbound 为主、只要清晰交易阶段与活动节奏、不要复杂自定义对象时采用；要关系图谱与对象自由用 Attio，要营销漏斗一体用 HubSpot。",
        "无慷慨长期免费档；自定义对象与跨团队工作流弱于现代灵活 CRM。",
        vendorId="pipedrive-inc",
        pricing={"model": "subscription", "currency": "USD"},
        maturity="mature",
        tags=["crm", "sales", "pipeline", "saas"],
        pitfalls=[
            "复杂多产品线与非交易型关系建模吃力。",
            "高级自动化与报告常在更高席位档。",
        ],
    ),
    mk(
        CAT_CRM,
        "twenty",
        "Twenty",
        "open-source-crm",
        "开源现代 CRM · 可自托管 · GraphQL/React 栈",
        "https://twenty.com",
        "Twenty 是开源的现代 CRM：React + GraphQL，支持云托管与自托管，界面与数据模型朝现代 B2B 工作台演进，适合要数据驻留或可二次开发的团队。",
        "必须自托管/开源、或要在 CRM 上二次开发、且能承受运维时评估；要开箱营销套件仍是 HubSpot，要托管 AI 灵活对象可先 Attio。",
        "生态集成与 polish 仍追商业 SaaS；生产自托管要管权限、备份与升级。",
        vendorId="twenty-inc",
        githubUrl="https://github.com/twentyhq/twenty",
        pricing={"model": "open-source", "currency": "USD", "notes": "云订阅；自托管开源"},
        tags=["crm", "open-source", "self-hosted", "developer"],
        pitfalls=[
            "连接器广度与 polish 弱于商业头部。",
            "自托管需运维身份、邮件同步与备份。",
        ],
    ),
]

# ——— 社区 ———
COMM = [
    mk(
        CAT_COMM,
        "discourse",
        "Discourse",
        "forum",
        "开源论坛标杆 · SEO 友好长帖 · 可自托管可托管",
        "https://www.discourse.org",
        "Discourse 是开源论坛平台：主题式讨论、信任等级、搜索与 SEO 友好的永久链接，可官方托管也可自托管，是「可被搜索的社区知识库」常见选型。",
        "要公开/半公开问答、文档站并行、可自持数据与主题定制时优先；会员付费圈与课程社群可看 Circle，实时语音聊天看 Discord。",
        "运维与主题定制成本高于闭源 SaaS；实时语音与轻聊不是强项。",
        vendorId="discourse-inc",
        githubUrl="https://github.com/discourse/discourse",
        pricing={"model": "open-source", "currency": "USD", "notes": "托管订阅；自托管开源"},
        maturity="mature",
        tags=["community", "forum", "open-source", "self-hosted"],
        pitfalls=[
            "自托管主题、邮件与反垃圾需持续投入。",
            "实时语音与轻社交节奏弱于 Discord 类。",
        ],
    ),
    mk(
        CAT_COMM,
        "circle-so",
        "Circle",
        "membership-community",
        "托管会员社区 · 课程/空间/活动一体 · 创作者变现向",
        "https://circle.so",
        "Circle 是托管社区 SaaS：空间、课程、活动、直播与会员订阅放在同一产品，强调运营与变现工具，而不是开源论坛源码。",
        "课程/付费会员/创作者要一站式空间与支付、零运维时评估；要 SEO 长尾知识库与自托管用 Discourse，工程/游戏实时社区常见配 Discord。",
        "成员与功能档位订阅；数据与定制深度受 SaaS 约束，迁出成本存在。",
        vendorId="circle-so-inc",
        pricing={"model": "subscription", "currency": "USD"},
        tags=["community", "membership", "courses", "saas"],
        pitfalls=[
            "成员规模上来后按档计费，功能包要克制开通。",
            "数据驻留与白标能力不如自托管论坛。",
        ],
    ),
    mk(
        CAT_COMM,
        "flarum",
        "Flarum",
        "forum",
        "轻量开源论坛 · 扩展生态 · 部署与心智比 Discourse 轻",
        "https://flarum.org",
        "Flarum 是轻量 PHP 开源论坛：现代化 UI、扩展市场，部署与默认心智比 Discourse 更轻，适合中小站「先跑起来」的社区，而不是企业级信任体系论坛。",
        "要可自托管的简洁论坛、团队运维预算有限时评估；大规模信任等级、官方托管 SLA 与重度 SEO 运维更常见选 Discourse。",
        "企业支持与托管选项弱于 Discourse；扩展质量参差，升级需测兼容。",
        vendorId="flarum-inc",
        githubUrl="https://github.com/flarum/flarum",
        pricing={"model": "open-source", "currency": "USD"},
        tags=["community", "forum", "open-source", "self-hosted"],
        pitfalls=[
            "企业级支持与托管 SLA 弱。",
            "扩展升级兼容要回归测试。",
        ],
    ),
]

# ——— 异步录屏 / 标注 ———
ASYNC = [
    mk(
        CAT_ASYNC,
        "loom",
        "Loom",
        "async-video",
        "异步录屏沟通默认 · 链接即播 · 非 session 回放产品分析",
        "https://www.loom.com",
        "Loom 让人快速录制屏幕与摄像头说明，生成可分享链接，定位是团队异步沟通与支持讲解，而不是网站访客行为回放或缺陷批注工具。",
        "跨时区讲解需求、产品演示与支持话术需要可暂停回看的短视频时优先；访客 session 回放看 LogRocket/Hotjar 叶，页面上钉缺陷看 Marker。",
        "席位与观看/AI 功能按档；敏感屏幕需流程规范，避免泄密录屏外发。",
        vendorId="loom-inc",
        pricing={"model": "freemium", "currency": "USD"},
        maturity="mature",
        tags=["async-video", "screen-recording", "collaboration", "saas"],
        pitfalls=[
            "不是产品分析用的访客会话回放。",
            "企业数据驻留与权限策略要单独配置。",
        ],
    ),
    mk(
        CAT_ASYNC,
        "marker-io",
        "Marker",
        "visual-bug-feedback",
        "页面可视缺陷标注 · 一键进工单 · 设计/QA 反馈向",
        "https://marker.io",
        "Marker 让干系人在真实页面上圈注问题并附截图/录制元数据，把反馈一键送进 issue 工具，定位是视觉验收与缺陷沟通，而非异步人声讲解或访客分析。",
        "设计/产品/客户要在预发环境「指哪里改哪里」、且进 Linear/Jira 时评估；工程复现会话用 Jam 或 session replay，只讲概念用 Loom。",
        "按席位/项目计费；落地页 SDK 与权限要配白名单，避免扫到生产敏感数据。",
        vendorId="marker-io-inc",
        pricing={"model": "subscription", "currency": "USD"},
        tags=["bug-reporting", "qa", "feedback", "annotation"],
        pitfalls=[
            "环境白名单与 PII 遮罩未配好会录到敏感信息。",
            "不能替代正式测试用例与自动化。",
        ],
    ),
    mk(
        CAT_ASYNC,
        "jam-dev",
        "Jam",
        "dev-bug-capture",
        "录屏+控制台/网络元数据 · 开发者缺陷包 · 对标 Marker",
        "https://jam.dev",
        "Jam 把屏幕录制与浏览器控制台、网络请求等开发者上下文打成一条缺陷报告，方便前端复现，介于「给人看的 Loom」与「圈 UI 的 Marker」之间的工程向捕获。",
        "工程团队要减少「本地复现不了」来回、把技术上下文塞进 ticket 时评估；纯设计批注用 Marker，纯产品讲解用 Loom。",
        "隐私与网络日志要规范；重度分析向会话回放仍看 LogRocket 一类。",
        vendorId="jam-dev-inc",
        pricing={"model": "freemium", "currency": "USD"},
        tags=["bug-reporting", "devtools", "screen-recording", "developer"],
        pitfalls=[
            "会捕获网络与控制台，密钥出现在请求里时有泄露风险。",
            "不替代系统化 APM 与错误聚合。",
        ],
    ),
]

ENTRIES_DATA = MEDIA + CRM + COMM + ASYNC

VENDORS_DATA = [
    vendor("cloudinary-inc", "Cloudinary", url="https://cloudinary.com"),
    vendor("mux-inc", "Mux", url="https://www.mux.com"),
    vendor("imgix-inc", "imgix", url="https://www.imgix.com"),
    vendor("imagekit-inc", "ImageKit", url="https://imagekit.io"),
    vendor("attio-inc", "Attio", url="https://attio.com"),
    vendor("hubspot-inc", "HubSpot", url="https://www.hubspot.com"),
    vendor("pipedrive-inc", "Pipedrive", url="https://www.pipedrive.com"),
    vendor("twenty-inc", "Twenty", url="https://twenty.com"),
    vendor("discourse-inc", "Discourse", url="https://www.discourse.org"),
    vendor("circle-so-inc", "Circle", url="https://circle.so"),
    vendor("flarum-inc", "Flarum", url="https://flarum.org"),
    vendor("loom-inc", "Loom", url="https://www.loom.com"),
    vendor("marker-io-inc", "Marker", url="https://marker.io"),
    vendor("jam-dev-inc", "Jam", url="https://jam.dev"),
]

EDGES_DATA = [
    # media
    edge(
        "e-imagekit-alt-cloudinary",
        "imagekit",
        "cloudinary",
        "alternative_to",
        note="带宽向计价、中档变换 vs 全栈 AI/DAM 默认但 credit 更重",
    ),
    edge(
        "e-imgix-alt-cloudinary",
        "imgix",
        "cloudinary",
        "alternative_to",
        note="源站旁路 URL 变换、图品质向 vs 上传+DAM+AI 一体",
    ),
    edge(
        "e-mux-alt-cloudinary",
        "mux",
        "cloudinary",
        "alternative_to",
        note="开发者视频流水线 vs 图视频全能媒体平台（视频维对打）",
        weight=0.6,
    ),
    edge(
        "e-imagekit-alt-imgix",
        "imagekit",
        "imgix",
        "alternative_to",
        note="性价比图 CDN + 可选 DAM vs 高端渲染/媒体站图 CDN",
        weight=0.65,
    ),
    edge(
        "e-cloudinary-with-nextjs",
        "cloudinary",
        "nextjs",
        "commonly_used_with",
        note="next/image loader 或官方 SDK 做响应式投递",
        weight=0.55,
    ),
    edge(
        "e-imgix-with-aws-s3",
        "imgix",
        "aws-s3",
        "commonly_used_with",
        note="S3/源站出图 + imgix 边缘渲染，不强制迁库到媒体云",
        weight=0.65,
    ),
    edge(
        "e-cloudinary-alt-bunny-cdn",
        "cloudinary",
        "bunny-cdn",
        "alternative_to",
        note="媒体变换/DAM 层 vs 通用低价 CDN（层不同，勿等同比较）",
        weight=0.45,
    ),
    # crm
    edge(
        "e-attio-alt-hubspot",
        "attio",
        "hubspot",
        "alternative_to",
        note="灵活对象+AI 现代 CRM vs 营销销售套件起盘默认",
    ),
    edge(
        "e-pipedrive-alt-hubspot",
        "pipedrive",
        "hubspot",
        "alternative_to",
        note="纯交易管道极简 vs 套件化增长 CRM",
    ),
    edge(
        "e-pipedrive-alt-attio",
        "pipedrive",
        "attio",
        "alternative_to",
        note="线性看板销售 vs 可塑对象与关系图谱",
        weight=0.65,
    ),
    edge(
        "e-twenty-osalt-hubspot",
        "twenty",
        "hubspot",
        "open_source_alternative_to",
        note="开源可自托管现代 CRM vs 托管增长套件",
    ),
    edge(
        "e-twenty-alt-attio",
        "twenty",
        "attio",
        "alternative_to",
        note="开源自托管 vs 托管 AI 现代 CRM",
        weight=0.65,
    ),
    # community
    edge(
        "e-discourse-osalt-circle-so",
        "discourse",
        "circle-so",
        "open_source_alternative_to",
        note="开源长帖论坛/SEO vs 托管会员课程社区",
    ),
    edge(
        "e-flarum-alt-discourse",
        "flarum",
        "discourse",
        "alternative_to",
        note="更轻部署与 UI vs 信任等级与托管生态更成熟",
    ),
    edge(
        "e-discourse-alt-discord",
        "discourse",
        "discord",
        "alternative_to",
        note="可索引长帖知识社区 vs 实时频道/语音 IM 社区",
        weight=0.6,
    ),
    edge(
        "e-circle-so-alt-discord",
        "circle-so",
        "discord",
        "alternative_to",
        note="付费会员空间与课程 vs 免费实时聊天室枢纽",
        weight=0.55,
    ),
    edge(
        "e-circle-so-with-stripe",
        "circle-so",
        "stripe",
        "commonly_used_with",
        note="会员订阅与付费空间常接 Stripe 收款",
        weight=0.55,
    ),
    # privacy migrate edges (reinforce; termly↔iubenda 已有 e-iubenda-alt-termly，勿镜像)
    edge(
        "e-cookiebot-alt-iubenda",
        "cookiebot",
        "iubenda",
        "alternative_to",
        note="Cookie 扫描分类/同意日志专长 vs 政策生成+同意一体",
        weight=0.65,
    ),
    edge(
        "e-termly-alt-cookiebot",
        "termly",
        "cookiebot",
        "alternative_to",
        note="政策生成器主战场 vs 欧盟 CMP/扫描老牌",
        weight=0.6,
    ),
    edge(
        "e-onetrust-alt-cookiebot",
        "onetrust",
        "cookiebot",
        "alternative_to",
        note="企业隐私治理/数据地图全套 vs 站点级 Cookie 同意",
        weight=0.6,
    ),
    # async capture
    edge(
        "e-jam-dev-alt-loom",
        "jam-dev",
        "loom",
        "alternative_to",
        note="带控制台/网络的缺陷包 vs 人声异步讲解录屏",
        weight=0.6,
    ),
    edge(
        "e-marker-io-alt-jam-dev",
        "marker-io",
        "jam-dev",
        "alternative_to",
        note="业务方页面圈注验收 vs 工程元数据缺陷捕获",
        weight=0.65,
    ),
    edge(
        "e-marker-io-with-linear",
        "marker-io",
        "linear",
        "commonly_used_with",
        note="圈注反馈一键落 Linear issue",
        weight=0.65,
    ),
    edge(
        "e-marker-io-with-jira",
        "marker-io",
        "jira",
        "commonly_used_with",
        note="企业工单流常见回写 Jira",
        weight=0.6,
    ),
    edge(
        "e-jam-dev-with-linear",
        "jam-dev",
        "linear",
        "commonly_used_with",
        note="缺陷包连同复现上下文进 Linear",
        weight=0.6,
    ),
    edge(
        "e-loom-alt-logrocket",
        "loom",
        "logrocket",
        "alternative_to",
        note="人对人异步讲解 vs 访客会话工程回放（勿混选型）",
        weight=0.4,
    ),
]


def migrate_privacy() -> None:
    for eid in PRIVACY_MIGRATE:
        path = ENTRIES / f"{eid}.json"
        if not path.exists():
            print("warn: missing privacy entry", eid)
            continue
        data = json.loads(path.read_text(encoding="utf-8"))
        old = data.get("category")
        if old == CAT_PRIV:
            print("privacy already on", eid, CAT_PRIV)
            continue
        data["category"] = CAT_PRIV
        data["lastReviewed"] = REVIEWED
        if not data.get("subcategory"):
            data["subcategory"] = "privacy-consent"
        save(path, data)
        print(f"migrated {eid} {old} → {CAT_PRIV}")


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

    migrate_privacy()

    print(
        f"done entries={wrote_e}(skip {skipped_e}) "
        f"vendors={wrote_v}(skip {skipped_v}) edges={wrote_g}(skip {skipped_g})"
    )
    print(
        f"leaves: {CAT_MEDIA} {CAT_CRM} {CAT_COMM} {CAT_PRIV} {CAT_ASYNC}; "
        f"privacy migrate {PRIVACY_MIGRATE}"
    )


if __name__ == "__main__":
    main()
