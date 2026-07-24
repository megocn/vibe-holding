#!/usr/bin/env python3
"""素材站点扩种：图库/灵感板/字体叶 + Pinterest 等发散补种。

- 新叶：design-stock / design-inspiration / design-fonts
- 迁移：unsplash、pexels、undraw → design-stock
- 幂等写入 entries/vendors/edges

用法:
  python3 scripts/expand-design-assets-2026-07.py
  python3 scripts/expand-design-assets-2026-07.py --overwrite
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
REVIEWED = "2026-07-24"


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
    assert len(e["oneLiner"]) <= 60, (e["id"], len(e["oneLiner"]), e["oneLiner"])
    assert len(e.get("descriptionMd", "")) >= 120, (e["id"], len(e.get("descriptionMd", "")))
    assert e.get("pitfalls"), e["id"]
    assert e.get("subcategory"), e["id"]
    return e


def desc(what: str, when: str, caution: str) -> str:
    return f"{what}\n\n{when}\n\n{caution}\n"


def mk(eid, name, cat, sub, one, url, what, when, caution, **extra):
    pitfalls = extra.pop("pitfalls", None)
    kw = {
        "id": eid,
        "name": name,
        "category": cat,
        "subcategory": sub,
        "oneLiner": one,
        "officialUrl": url,
        "descriptionMd": desc(what, when, caution),
        "pitfalls": pitfalls or [caution[:80]],
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


CN = {
    "chinaAccessible": True,
    "needsCompany": False,
    "needsIcp": False,
    "regions": ["CN"],
}
US_BLOCKED = {
    "chinaAccessible": False,
    "needsCompany": False,
    "needsIcp": False,
    "regions": ["global"],
}

ENTRIES_DATA: list[dict] = [
    # ========== design-stock · 图库 / 素材市场 ==========
    mk(
        "pinterest",
        "Pinterest",
        "design-inspiration",
        "moodboard",
        "视觉灵感板 · 拼贴收藏 · 营销/品牌 mood",
        "https://www.pinterest.com",
        "Pinterest 以图片拼贴与主题板（board）组织视觉灵感，设计师与运营常用作 moodboard、竞品视觉与趋势收集，而非传统「按授权下载商用图库」。",
        "需要发散视觉方向、收集参考拼贴、或运营做内容灵感库时优先；真正可商用下载请转到 Unsplash/Freepik/Adobe Stock。",
        "图片版权复杂，钉图≠可商用；国内访问与账号策略不稳定，团队应另备素材源。",
        vendorId="pinterest-inc",
        tags=["inspiration", "moodboard", "social"],
        pricing={"model": "freemium"},
        maturity="mature",
    ),
    mk(
        "pixabay",
        "Pixabay",
        "design-stock",
        "stock",
        "免费图/视频/插画/音乐 · 一站式",
        "https://pixabay.com",
        "Pixabay 提供免费照片、插画、矢量、视频与音乐等多媒体素材，许可相对宽松，适合 indie 与内容站快速配图配乐。",
        "需要「不只照片」的一站式免费素材、或与 Unsplash/Pexels 做备份源时选用。",
        "热门图同质化明显；商用前仍须读清 Pixabay License 与人物/商标限制。",
        vendorId="canva-inc",
        tags=["stock", "photos", "video", "free"],
        pricing={"model": "free"},
        maturity="mature",
    ),
    mk(
        "freepik",
        "Freepik",
        "design-stock",
        "stock-market",
        "海量矢量/模板/图库 · 订阅向素材市场",
        "https://www.freepik.com",
        "Freepik（现亦以 Magnific 叙事扩展 AI 创作）提供照片、矢量、图标、模板、Mockup 等超大库存，是营销与演示设计常用的付费/免费分层素材市场。",
        "需要海报、演示、社媒模板与矢量包、可接受订阅换无归因时评估；与 Envato/Adobe Stock 同层。",
        "免费层常需署名；品牌项目注意素材「模板感」与授权范围；站点品牌更名期间入口以官网为准。",
        vendorId="freepik-inc",
        tags=["stock", "vectors", "templates", "subscription"],
        pricing={"model": "subscription", "currency": "USD"},
        maturity="mature",
    ),
    mk(
        "envato-elements",
        "Envato Elements",
        "design-stock",
        "stock-market",
        "订阅制全能素材 · 模板/主题/音视频",
        "https://elements.envato.com",
        "Envato Elements 以月费解锁海量模板、主题、照片、图形、音效与视频素材，Web/演示/营销团队「一订阅多用」场景常见。",
        "同时需要 WordPress/演示模板、UI kit 与音视频素材、希望统一授权账单时优先。",
        "单次用量低时不如按需图库划算；授权条款（席位、最终产品）必须读清。",
        vendorId="envato",
        tags=["stock", "templates", "subscription", "audio"],
        pricing={"model": "subscription", "currency": "USD"},
        maturity="mature",
    ),
    mk(
        "adobe-stock",
        "Adobe Stock",
        "design-stock",
        "stock-market",
        "Adobe 生态图库 · CC 内嵌检索",
        "https://stock.adobe.com",
        "Adobe Stock 与 Creative Cloud 深度集成，在 Ps/Ai/Xd 内直接检索授权素材，企业与设计团队统一采购常见。",
        "团队已买 Adobe CC、需要工作流内嵌搜图与合规授权时优先。",
        "单价/积分偏高；独立开发者常更看 Unsplash + Freepik 组合。",
        vendorId="adobe",
        tags=["stock", "adobe", "enterprise"],
        pricing={"model": "subscription", "currency": "USD"},
        maturity="mature",
    ),
    mk(
        "shutterstock",
        "Shutterstock",
        "design-stock",
        "stock-market",
        "老牌商用图库 · 企业授权清晰",
        "https://www.shutterstock.com",
        "Shutterstock 是全球大型商用图库，覆盖照片、矢量、视频与音乐，企业采购与清晰授权路径成熟。",
        "品牌/广告需要可审计商用授权、法务友好条款时评估；与 Getty/Adobe Stock 同层。",
        "成本高于免费图库；「网红图」过度使用会显模板感。",
        vendorId="shutterstock-inc",
        tags=["stock", "enterprise", "photos"],
        pricing={"model": "subscription", "currency": "USD"},
        maturity="mature",
    ),
    mk(
        "flaticon",
        "Flaticon",
        "design-stock",
        "icons-pack",
        "海量图标包下载 · Freepik 生态",
        "https://www.flaticon.com",
        "Flaticon 提供海量可下载图标与贴纸（SVG/PNG 等），偏设计师打包下载与演示配图，与开发者图标库（Lucide/Iconify）定位不同。",
        "演示稿、落地页、运营物料需要成套图标风格时评估；产品 UI 组件库仍优先 Lucide/Phosphor 等代码图标。",
        "免费常需署名；与 UI 叶 `ui-icons` 条目勿混比——一个是素材站，一个是工程依赖。",
        vendorId="freepik-inc",
        tags=["icons", "stock", "download"],
        pricing={"model": "freemium"},
        maturity="mature",
    ),
    mk(
        "icons8",
        "Icons8",
        "design-stock",
        "icons-pack",
        "图标+插画+照片 · 风格统一商店",
        "https://icons8.com",
        "Icons8 提供风格较统一的图标、插画、照片与音乐等，强调成套视觉一致性，适合快速拼出统一风格的营销页与演示。",
        "需要「一套风格走天下」的图标+插画组合、可付费去署名时评估。",
        "免费限制多；产品内嵌图标仍建议工程图标库以便 tree-shake 与主题化。",
        vendorId="icons8-inc",
        tags=["icons", "illustration", "stock"],
        pricing={"model": "subscription", "currency": "USD"},
    ),
    mk(
        "noun-project",
        "The Noun Project",
        "design-stock",
        "icons-pack",
        "极简图标集市 · 语义化符号",
        "https://thenounproject.com",
        "The Noun Project 聚合大量极简、语义清晰的图标，设计师按概念检索符号，适合信息图与中性 UI 隐喻。",
        "需要概念符号（而非产品 icon set）、信息图配图时评估。",
        "免费需署名；风格混杂，成套一致性不如单一 icon set。",
        vendorId="noun-project-inc",
        tags=["icons", "symbols"],
        pricing={"model": "freemium"},
        maturity="mature",
    ),
    mk(
        "vecteezy",
        "Vecteezy",
        "design-stock",
        "vectors",
        "矢量/插画下载站 · 免费+Pro",
        "https://www.vecteezy.com",
        "Vecteezy 专注矢量图、插画与部分照片视频，提供免费与 Pro 分层，适合海报、印刷与社媒向的可编辑矢量素材采购。",
        "需要可编辑矢量插画、或与 Freepik 做备选素材市场时评估；印刷前注意出血与色彩模式。",
        "免费许可与署名规则需核对；质量参差，品牌项目要人工筛选。",
        vendorId="vecteezy-inc",
        tags=["vectors", "illustration", "stock"],
        pricing={"model": "freemium"},
    ),
    mk(
        "coverr",
        "Coverr",
        "design-stock",
        "video-stock",
        "免费网站英雄视频 · 竖横屏",
        "https://coverr.co",
        "Coverr 提供面向网站英雄区与背景的免费库存视频，强调可商用短镜头与多比例，适合落地页氛围视频。",
        "营销页需要轻量 b-roll/背景视频、预算为零时选用；长片与电影级素材看付费库。",
        "片库规模相对有限；商用条款与内嵌音乐轨授权要分开确认，必要时换无声轨。",
        vendorId="coverr-inc",
        tags=["video", "stock", "free", "landing"],
        pricing={"model": "free"},
    ),
    mk(
        "mixkit",
        "Mixkit",
        "design-stock",
        "video-stock",
        "免费视频/音乐素材 · Envato 旗下",
        "https://mixkit.co",
        "Mixkit（Envato）提供免费视频片段与音乐等，许可相对清晰，适合内容创作、教程与社媒短视频快速配素材。",
        "需要免费可商用视频/音乐、与 Envato 生态邻近时评估。",
        "高端定制与稀缺镜头仍不足；音乐与画面授权条目要分别阅读，避免混用过期许可。",
        vendorId="envato",
        tags=["video", "music", "stock", "free"],
        pricing={"model": "free"},
    ),
    mk(
        "storyset",
        "Storyset",
        "design-stock",
        "illustration",
        "可定制 SVG 插画 · 动画可选",
        "https://storyset.com",
        "Storyset（Freepik 生态）提供可改色、可加简单动画的情境插画，适合 onboarding、空状态与功能说明页。",
        "需要比 unDraw 更强定制/动效、又要快速出插画时评估。",
        "风格辨识度高，多用易显模板站；商用与署名看套餐。",
        vendorId="freepik-inc",
        tags=["illustration", "svg", "onboarding"],
        pricing={"model": "freemium"},
    ),
    mk(
        "humaaans",
        "Humaaans",
        "design-stock",
        "illustration",
        "可拼装人物插画 · Mix & Match",
        "https://www.humaaans.com",
        "Humaaans 提供可自由组合的扁平人物插画部件，适合产品说明、多样角色展示与多样性表达，社区衍生资源多。",
        "需要多样人物姿态、快速拼角色插画时选用；与 Open Peeps/unDraw 对照。",
        "风格单一；复杂场景仍需定制插画或 AI 生成。",
        tags=["illustration", "characters", "free"],
        pricing={"model": "free"},
    ),
    mk(
        "open-peeps",
        "Open Peeps",
        "design-stock",
        "illustration",
        "手绘风人物组件 · CC0",
        "https://www.openpeeps.com",
        "Open Peeps 是手绘风、可组合的人物插画库，许可宽松（CC0 叙事），适合友好、轻松语气的产品与社区插画。",
        "品牌语气偏亲切、需要可商用人物插画组件且想免署名纠纷时评估；可与 Humaaans 对照风格。",
        "风格固定；与企业严谨视觉可能不搭。",
        tags=["illustration", "characters", "cc0"],
        pricing={"model": "free"},
    ),
    mk(
        "bao-tu-wang",
        "包图网",
        "design-stock",
        "stock-market",
        "国内商用素材站 · 模板/摄影/视频",
        "https://ibaotu.com",
        "包图网是国内常用的商用素材平台，覆盖摄影图、设计模板、视频与各类设计元素，面向电商与营销设计采购。",
        "国内团队需要中文检索、人民币结算与国内版权叙事时评估；与千图/摄图对照。",
        "授权范围（个人/企业/多端）必须核对；质量与「网感」参差需人工筛选。",
        vendorId="bao-tu",
        region="domestic",
        tags=["stock", "domestic", "templates"],
        pricing={"model": "subscription", "currency": "CNY"},
        availability=CN,
    ),
    mk(
        "zcool-assets",
        "站酷海洛",
        "design-stock",
        "stock-market",
        "站酷系商用图库 · 国内设计师向",
        "https://www.hellorf.com",
        "站酷海洛（Hellorf）提供面向国内的正版摄影图库与设计素材，与站酷社区设计师生态邻近，适合品牌与广告采购。",
        "需要国内正版图、设计师工作流熟悉站酷时评估。",
        "价格与套餐需测算；国际大片种丰富度对照 Shutterstock/Getty。",
        vendorId="zcool-inc",
        region="domestic",
        tags=["stock", "domestic"],
        pricing={"model": "subscription", "currency": "CNY"},
        availability=CN,
        officialUrl="https://www.hellorf.com",
    ),
    # ========== design-inspiration · 灵感 / 作品集 ==========
    mk(
        "dribbble",
        "Dribbble",
        "design-inspiration",
        "portfolio",
        "UI/视觉作品集社区 · 趋势灵感",
        "https://dribbble.com",
        "Dribbble 是设计师展示 UI、品牌与动效作品的社区，产品与设计团队常用作视觉趋势与招聘作品集入口。",
        "需要 UI/视觉灵感、找设计师作品集或追踪风格趋势时优先；落地实现仍要回到设计系统约束。",
        "Shot 多为概念稿，直接落地成本高；国内访问与招聘转化因团队而异。",
        vendorId="dribbble-inc",
        tags=["inspiration", "ui", "portfolio"],
        pricing={"model": "freemium"},
        maturity="mature",
    ),
    mk(
        "behance",
        "Behance",
        "design-inspiration",
        "portfolio",
        "Adobe 作品集 · 长案例叙事",
        "https://www.behance.net",
        "Behance（Adobe）适合展示完整设计案例与项目叙事，品牌、影视与综合设计作品集常见，与 Dribbble 的短 shot 互补。",
        "需要看完整案例流程、品牌视觉体系或招聘综合设计师时评估。",
        "信息密度高、检索偏作品集而非可下载素材；商用素材请走 Adobe Stock。",
        vendorId="adobe",
        tags=["inspiration", "portfolio", "adobe"],
        pricing={"model": "free"},
        maturity="mature",
    ),
    mk(
        "mobbin",
        "Mobbin",
        "design-inspiration",
        "ui-patterns",
        "移动/Web UI 截图库 · 模式检索",
        "https://mobbin.com",
        "Mobbin 收录真实 App/Web 界面截图，可按流程与 UI 模式检索，产品设计师做竞品与交互参考时高频使用。",
        "需要真实产品界面模式（登录/支付/列表），而非概念 shot 时优先。",
        "订阅制；截图仅供参考，实现与无研仍要自己做。",
        vendorId="mobbin-inc",
        tags=["inspiration", "ui", "patterns", "mobile"],
        pricing={"model": "subscription", "currency": "USD"},
    ),
    mk(
        "godly",
        "Godly",
        "design-inspiration",
        "landing",
        "精选落地页画廊 · Web 美学",
        "https://godly.website",
        "Godly 精选高质量营销落地页案例，强调当代 Web 视觉、排版与动效，适合找 landing / 品牌站灵感。",
        "做官网/活动页需要高水平视觉参考时浏览；落地实现时注意性能预算与无障碍，勿盲目堆动效。",
        "非素材下载站；案例可能过时，需核对是否仍上线。",
        tags=["inspiration", "landing", "web"],
        pricing={"model": "free"},
    ),
    mk(
        "landingfolio",
        "Landingfolio",
        "design-inspiration",
        "landing",
        "落地页分区组件灵感 · 可筛选",
        "https://www.landingfolio.com",
        "Landingfolio 按落地页区块（Hero、定价、FAQ 等）整理灵感与部分组件资源，方便对照信息结构而非整页抄袭。",
        "搭建营销页信息架构、需要分区级参考或组件灵感时评估；付费资源注意代码与设计授权边界。",
        "部分资源收费；注意版权与代码授权。",
        vendorId="landingfolio-inc",
        tags=["inspiration", "landing", "sections"],
        pricing={"model": "freemium"},
    ),
    mk(
        "awwwards",
        "Awwwards",
        "design-inspiration",
        "web-awards",
        "网页设计奖项与画廊 · 前沿美学",
        "https://www.awwwards.com",
        "Awwwards 评选并展示前沿网页设计与动效作品，适合寻找实验性交互、创意叙事与品牌站灵感。",
        "品牌站、活动站需要冲击力视觉与交互参考时浏览；也可作年度设计趋势观察入口。",
        "获奖站常偏实验向，直接照搬易损害性能与可达性；灵感要克制落地并做预算评估。",
        vendorId="awwwards-inc",
        tags=["inspiration", "web", "awards"],
        pricing={"model": "freemium"},
        maturity="mature",
    ),
    mk(
        "zcool",
        "站酷",
        "design-inspiration",
        "portfolio",
        "国内设计师社区 · 作品/招聘/学习",
        "https://www.zcool.com.cn",
        "站酷是国内设计作品与交流社区，覆盖平面、UI、三维等，设计师求职与品牌方找灵感/外包常见入口。",
        "国内团队需要中文作品集生态、或对接国内设计师时优先；国际向可并行 Dribbble/Behance。",
        "作品版权与商用需直接联系作者；平台内容质量参差。",
        vendorId="zcool-inc",
        region="domestic",
        tags=["inspiration", "portfolio", "domestic"],
        pricing={"model": "freemium"},
        availability=CN,
        maturity="mature",
    ),
    mk(
        "huaban",
        "花瓣",
        "design-inspiration",
        "moodboard",
        "国内灵感采集 · 类似 Pinterest",
        "https://huaban.com",
        "花瓣网提供图片采集与画板组织，国内设计与运营常用作中文语境下的视觉灵感与素材线索收集。",
        "需要国内可访问的 moodboard、中文标签检索时评估；可与 Pinterest 对照。",
        "采集图版权不清，不能当商用下载源；画质与源站稳定性因内容而异。",
        vendorId="huaban-inc",
        region="domestic",
        tags=["inspiration", "moodboard", "domestic"],
        pricing={"model": "freemium"},
        availability=CN,
    ),
    # ========== design-fonts · 字体 ==========
    mk(
        "google-fonts",
        "Google Fonts",
        "design-fonts",
        "web-fonts",
        "Web 字体事实标准 · 免费 CDN/自托管",
        "https://fonts.google.com",
        "Google Fonts 提供大量免费可商用 Web 字体与易用嵌入方式，是站点与产品选型字体的默认起点之一。",
        "需要快速上线 Web 字体、开源许可清晰时优先；注重隐私/国内可达可自托管或子集化。",
        "国内 CDN 可达性与隐私合规需方案；中文字体选择少于西文，常需中文字体源。",
        vendorId="google",
        tags=["fonts", "web", "free"],
        pricing={"model": "free"},
        maturity="mature",
    ),
    mk(
        "fontshare",
        "Fontshare",
        "design-fonts",
        "web-fonts",
        "高质量免费字体 · Indian Type Foundry",
        "https://www.fontshare.com",
        "Fontshare 由 Indian Type Foundry 提供一批设计感强的免费可商用字体，常作风格化品牌站的 Google Fonts 补充。",
        "需要比默认无衬线更有性格、又要免费商用的拉丁字体时评估。",
        "中文覆盖几乎无；家族数量少于 Google Fonts。",
        vendorId="itf",
        tags=["fonts", "free", "display"],
        pricing={"model": "free"},
    ),
    mk(
        "adobe-fonts",
        "Adobe Fonts",
        "design-fonts",
        "subscription-fonts",
        "CC 订阅字体库 · 桌面+Web",
        "https://fonts.adobe.com",
        "Adobe Fonts（原 Typekit）随 Creative Cloud 提供海量授权字体，设计工具内一键激活，适合已购 CC 的团队。",
        "团队已有 Adobe 订阅、需要正版西文/部分 CJK 字体工作流时优先。",
        "无 CC 则成本高；Web 项目要确认套餐的 pageview 限制。",
        vendorId="adobe",
        tags=["fonts", "adobe", "subscription"],
        pricing={"model": "subscription", "currency": "USD"},
        maturity="mature",
    ),
    mk(
        "alibaba-puhuiti",
        "阿里巴巴普惠体",
        "design-fonts",
        "cjk-fonts",
        "免费商用中文字体 · 品牌/电商常用",
        "https://www.alibabafonts.com/#/font",
        "阿里巴巴普惠体是面向中文场景的免费可商用字体家族，电商、活动页与国内产品常用，补齐 Google Fonts 中文不足。",
        "国内 Web/App 需要清晰中文 UI/标题字体且许可友好时评估；可与思源黑体对照。",
        "字重与场景要做渲染测试；与西文混排需选搭配字体。",
        vendorId="alibaba",
        region="domestic",
        tags=["fonts", "chinese", "free", "cjk"],
        pricing={"model": "free"},
        availability=CN,
    ),
    mk(
        "source-han-sans",
        "思源黑体",
        "design-fonts",
        "cjk-fonts",
        "Adobe+Google 开源 CJK · Noto Sans CJK",
        "https://github.com/adobe-fonts/source-han-sans",
        "思源黑体（Source Han Sans / Noto Sans CJK）是覆盖中日韩的开源字体家族，桌面与 Web 自托管常见，许可友好。",
        "需要开源中文字体、多语言 CJK 产品或与 Noto 西文统一时优先。",
        "完整字库体积大，Web 必须子集化/按需加载，否则首屏很重。",
        vendorId="adobe",
        region="both",
        tags=["fonts", "chinese", "open-source", "cjk"],
        pricing={"model": "open-source"},
        githubUrl="https://github.com/adobe-fonts/source-han-sans",
        maturity="mature",
    ),
]

VENDORS_DATA: list[dict] = [
    vendor("pinterest-inc", "Pinterest", url="https://www.pinterest.com"),
    vendor("freepik-inc", "Freepik Company", url="https://www.freepik.com"),
    vendor("envato", "Envato", url="https://envato.com"),
    vendor("shutterstock-inc", "Shutterstock", url="https://www.shutterstock.com"),
    vendor("icons8-inc", "Icons8", url="https://icons8.com"),
    vendor("noun-project-inc", "The Noun Project", url="https://thenounproject.com"),
    vendor("vecteezy-inc", "Vecteezy", url="https://www.vecteezy.com"),
    vendor("coverr-inc", "Coverr", url="https://coverr.co"),
    vendor("dribbble-inc", "Dribbble", url="https://dribbble.com"),
    vendor("mobbin-inc", "Mobbin", url="https://mobbin.com"),
    vendor("landingfolio-inc", "Landingfolio", url="https://www.landingfolio.com"),
    vendor("awwwards-inc", "Awwwards", url="https://www.awwwards.com"),
    vendor("zcool-inc", "站酷", region="domestic", url="https://www.zcool.com.cn"),
    vendor("huaban-inc", "花瓣", region="domestic", url="https://huaban.com"),
    vendor("bao-tu", "包图网", region="domestic", url="https://ibaotu.com"),
    vendor("itf", "Indian Type Foundry", url="https://www.fontshare.com"),
]

EDGES_DATA: list[dict] = [
    # stock
    edge("edge-pixabay-unsplash-alt", "pixabay", "unsplash", "alternative_to"),
    edge("edge-pixabay-pexels-alt", "pixabay", "pexels", "alternative_to"),
    edge("edge-freepik-unsplash-alt", "freepik", "unsplash", "alternative_to", weight=0.5, note="付费市场 vs 免费摄影"),
    edge("edge-envato-freepik-alt", "envato-elements", "freepik", "alternative_to"),
    edge("edge-adobe-stock-shutterstock-alt", "adobe-stock", "shutterstock", "alternative_to"),
    edge("edge-adobe-stock-unsplash-alt", "adobe-stock", "unsplash", "alternative_to", weight=0.45),
    edge("edge-flaticon-icons8-alt", "flaticon", "icons8", "alternative_to"),
    edge("edge-flaticon-noun-alt", "flaticon", "noun-project", "alternative_to"),
    edge("edge-flaticon-lucide-related", "flaticon", "lucide", "alternative_to", weight=0.35, note="素材站图标包 vs 工程图标库，弱替代"),
    edge("edge-vecteezy-freepik-alt", "vecteezy", "freepik", "alternative_to"),
    edge("edge-coverr-mixkit-alt", "coverr", "mixkit", "alternative_to"),
    edge("edge-mixkit-envato-with", "mixkit", "envato-elements", "commonly_used_with", note="同属 Envato 生态"),
    edge("edge-storyset-undraw-alt", "storyset", "undraw", "alternative_to"),
    edge("edge-humaaans-openpeeps-alt", "humaaans", "open-peeps", "alternative_to"),
    edge("edge-humaaans-undraw-alt", "humaaans", "undraw", "alternative_to", weight=0.55),
    edge("edge-baotu-freepik-dom", "bao-tu-wang", "freepik", "domestic_equivalent_of"),
    edge("edge-hellorf-shutterstock-dom", "zcool-assets", "shutterstock", "domestic_equivalent_of"),
    edge("edge-flaticon-freepik-with", "flaticon", "freepik", "commonly_used_with", note="同公司生态"),
    edge("edge-storyset-freepik-with", "storyset", "freepik", "commonly_used_with"),
    # inspiration
    edge("edge-pinterest-huaban-dom", "huaban", "pinterest", "domestic_equivalent_of"),
    edge("edge-dribbble-behance-alt", "dribbble", "behance", "alternative_to", note="短 shot vs 长案例"),
    edge("edge-dribbble-zcool-dom", "zcool", "dribbble", "domestic_equivalent_of"),
    edge("edge-mobbin-dribbble-alt", "mobbin", "dribbble", "alternative_to", weight=0.5, note="真实产品截图 vs 概念稿"),
    edge("edge-godly-landingfolio-alt", "godly", "landingfolio", "alternative_to"),
    edge("edge-awwwards-godly-with", "awwwards", "godly", "commonly_used_with"),
    edge("edge-pinterest-dribbble-with", "pinterest", "dribbble", "commonly_used_with", note="mood + UI 灵感"),
    edge("edge-zcool-hellorf-with", "zcool", "zcool-assets", "commonly_used_with", note="社区 + 海洛图库"),
    # fonts
    edge("edge-fontshare-google-fonts-alt", "fontshare", "google-fonts", "alternative_to", weight=0.55),
    edge("edge-adobe-fonts-google-alt", "adobe-fonts", "google-fonts", "alternative_to", weight=0.5),
    edge("edge-puhuiti-google-fonts-with", "alibaba-puhuiti", "google-fonts", "commonly_used_with", note="中文 + 西文搭配"),
    edge("edge-sourcehan-puhuiti-alt", "source-han-sans", "alibaba-puhuiti", "alternative_to"),
    edge("edge-sourcehan-google-with", "source-han-sans", "google-fonts", "commonly_used_with"),
]


def write_item(dir_path: Path, item: dict, overwrite: bool) -> bool:
    path = dir_path / f"{item['id']}.json"
    if path.exists() and not overwrite:
        return False
    save(path, item)
    return True


def migrate_existing() -> None:
    moves = {
        "unsplash": ("design-stock", "stock"),
        "pexels": ("design-stock", "stock"),
        "undraw": ("design-stock", "illustration"),
    }
    for eid, (cat, sub) in moves.items():
        path = ENTRIES / f"{eid}.json"
        if not path.exists():
            print(f"migrate skip: {eid}")
            continue
        e = json.loads(path.read_text(encoding="utf-8"))
        changed = e.get("category") != cat or e.get("subcategory") != sub
        e["category"] = cat
        e["subcategory"] = sub
        e["lastReviewed"] = REVIEWED
        if changed:
            save(path, e)
            print(f"migrate: {eid} → {cat}/{sub}")
        else:
            print(f"migrate: {eid} already on {cat}")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--overwrite", action="store_true")
    args = ap.parse_args()

    migrate_existing()

    ea = va = eda = 0
    for e in ENTRIES_DATA:
        if write_item(ENTRIES, e, args.overwrite):
            ea += 1
    for v in VENDORS_DATA:
        if write_item(VENDORS, v, args.overwrite):
            va += 1
    for ed in EDGES_DATA:
        if write_item(EDGES, ed, args.overwrite):
            eda += 1

    print(
        f"done: +entries={ea} +vendors={va} +edges={eda} "
        f"total_entries={len(list(ENTRIES.glob('*.json')))} "
        f"total_edges={len(list(EDGES.glob('*.json')))} "
        f"total_vendors={len(list(VENDORS.glob('*.json')))}"
    )


if __name__ == "__main__":
    main()
