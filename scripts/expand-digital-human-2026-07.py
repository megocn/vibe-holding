#!/usr/bin/env python3
"""数字人 / 口播形象扩种（按用途叶 design-digital-human）。

- 口播成片：HeyGen / Synthesia / D-ID / Hedra / Colossyan / 腾讯智影 / 讯飞智作 / 商汤如影 / 火山引擎
- 实时对话数字人：Tavus / Anam / 硅基 DUIX
- 开源说话头：LivePortrait / SadTalker / HeyGem

用法:
  python3 scripts/expand-digital-human-2026-07.py
  python3 scripts/expand-digital-human-2026-07.py --overwrite
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
REVIEWED = "2026-07-29"
CAT = "design-digital-human"


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
        "tags": ["ai", "avatar", "digital-human"],
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


def mk(eid, name, sub, one, url, what, when, caution, **extra):
    pitfalls = extra.pop("pitfalls", None)
    kw = {
        "id": eid,
        "name": name,
        "category": CAT,
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


US_BLOCKED = {
    "chinaAccessible": False,
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

ENTRIES_DATA: list[dict] = [
    # ——— 海外口播成片 ———
    mk(
        "d-id",
        "D-ID",
        "avatar-video",
        "照片驱动说话头 · API 轻量入门 · 短片向",
        "https://www.d-id.com",
        "D-ID 把静图/肖像驱动成说话头视频，提供 Studio 与开发者 API，强调快速生成短口播与会说话肖像，是 HeyGen/Synthesia 之外常见的轻量对照。",
        "只要「一张照片 + 文稿/音频」快速出短片、或要嵌入产品做说话肖像 POC 时评估；不要与文生镜头类工具混比。",
        "成片质量与全身表演弱于头部玩家；形象授权与 deepfake 合规同样严格。",
        vendorId="d-id-inc",
        pricing={"model": "subscription", "currency": "USD"},
        availability=US_BLOCKED,
        tags=["ai", "avatar", "api", "talking-head"],
    ),
    mk(
        "hedra",
        "Hedra",
        "avatar-video",
        "表情向角色视频 · 音乐/角色表演 · 风格化",
        "https://www.hedra.com",
        "Hedra 偏表情与角色表演的 AI 视频/数字人生成，适合音乐短片、风格化角色口播等「不像企业培训片」的创意向用法，与写实企业数字人平台定位不同。",
        "需要角色表情张力、音乐视频感或非写实说话角色时评估；企业培训模板流优先看 Synthesia/HeyGen。",
        "企业合规与多语本地化弱于培训向平台；产品形态与套餐变化快，POC 前锁定能力边界。",
        vendorId="hedra-inc",
        pricing={"model": "freemium", "currency": "USD"},
        availability=US_BLOCKED,
        tags=["ai", "avatar", "creative", "character"],
    ),
    mk(
        "colossyan",
        "Colossyan",
        "avatar-video",
        "互动培训数字人 · L&D 向 · 情景片",
        "https://www.colossyan.com",
        "Colossyan 面向学习与发展（L&D）场景的 AI 数字人视频，强调培训情景、分支互动与团队协作成片，是 Synthesia 在互动培训赛道的常见对照。",
        "需要可交互培训视频、情景演练或多角色讲解而非纯营销口播时评估。",
        "创意营销镜头弱；按席位/分钟计费需测算规模，勿与实时对话数字人混选。",
        vendorId="colossyan-inc",
        pricing={"model": "subscription", "currency": "USD"},
        availability=US_BLOCKED,
        tags=["ai", "avatar", "enterprise", "training"],
    ),
    # ——— 实时对话数字人 ———
    mk(
        "tavus",
        "Tavus",
        "realtime-avatar",
        "实时对话数字人 · CVI · 销售/客服向",
        "https://www.tavus.io",
        "Tavus 做 Conversational Video Interface：低时延、可对话的数字人，面向销售页、互动演示与客服/陪练等「面对面」场景，与批量脚本口播成片是不同产品形态。",
        "需要用户与数字人实时对话、个性化 1:1 视频交互时优先；批量培训/营销口播片请看 HeyGen/Synthesia。",
        "不是批量成片工具；成本与并发按会话计，需评估 LLM/TTS 联调与合规（形象克隆授权）。",
        vendorId="tavus-inc",
        pricing={"model": "usage", "currency": "USD"},
        availability=US_BLOCKED,
        tags=["ai", "avatar", "realtime", "api"],
    ),
    mk(
        "anam",
        "Anam",
        "realtime-avatar",
        "低时延交互数字人 API · 客服/Agent 向",
        "https://www.anam.ai",
        "Anam 提供实时交互式 AI Avatar API，强调低时延对话视频代理，面向客服、培训与销售中的 Conversational Video Agent 嵌入场景。",
        "要在自有产品里嵌「会说话的视频 Agent」、且关注端到端时延时评估；批量口播成片另选。",
        "形象/音色额度与并发上限按套餐变化；合规与克隆授权需产品侧自建流程。",
        vendorId="anam-inc",
        pricing={"model": "usage", "currency": "USD"},
        availability=US_BLOCKED,
        tags=["ai", "avatar", "realtime", "api"],
    ),
    # ——— 国内平台 ———
    mk(
        "tencent-zhiying",
        "腾讯智影",
        "domestic-suite",
        "腾讯系数字人口播 · 剪辑/配音一体 · 短视频向",
        "https://zenvideo.qq.com",
        "腾讯智影是腾讯云端智能视频创作平台，集成数字人口播、形象/声音克隆、文本配音与文章转视频等能力，常用于国内短视频、企业宣传与内容工业化生产。",
        "国内团队要快速出数字人口播、且希望与腾讯生态（账号/素材/分发）同栈时评估。",
        "能力与套餐以控制台为准；出海多语与海外分发需另测，勿默认等同 HeyGen。",
        vendorId="tencent",
        pricing={"model": "freemium", "currency": "CNY"},
        availability=DOMESTIC,
        region="domestic",
        tags=["ai", "avatar", "domestic", "video"],
    ),
    mk(
        "senseavatar",
        "商汤如影",
        "domestic-suite",
        "商汤数字人 · 口播/直播复刻 · 营销向",
        "https://www.sensetime.com",
        "商汤如影（SenseAvatar）隶属日日新大模型体系，提供数字人视频生成、形象定制与直播间复刻等能力，面向短视频营销、品牌 IP 与数字人直播。",
        "国内要高拟真数字人成片或直播运营、且可接受企业采购路径时评估。",
        "企业采购与试用门槛偏高；产品入口与套餐常随商汤站改版，签约前锁定具体 SKU。",
        vendorId="sensetime",
        pricing={"model": "subscription", "currency": "CNY"},
        availability=DOMESTIC,
        region="domestic",
        tags=["ai", "avatar", "domestic", "livestream"],
        sources=["https://www.sensetime.com", "https://www.sensetime.com/cn"],
    ),
    mk(
        "guiji-duix",
        "硅基智能 · DUIX",
        "realtime-avatar",
        "国内交互数字人 · 直播/SDK · 端侧可部署",
        "https://website.guiji.ai",
        "硅基智能（勿与「硅基流动」混淆）提供数字人交互与直播相关能力，DUIX 等 SDK/开源线支持 Web/端侧部署说话与互动数字人，常见于国内直播与客服交互场景。",
        "国内要数字人直播、H5/App 嵌入交互形象，或评估端侧开源方案时纳入；推理 API 网关请看硅基流动。",
        "商用授权与开源协议需分清；品牌名易与 SiliconFlow 混淆，选型文档务必写全称。",
        vendorId="guiji-inc",
        pricing={"model": "freemium", "currency": "CNY"},
        availability=DOMESTIC,
        region="domestic",
        tags=["ai", "avatar", "domestic", "sdk", "realtime"],
    ),
    mk(
        "iflytek-zhizuo",
        "讯飞智作",
        "domestic-suite",
        "讯飞数字人成片 · 配音强 · 教育/口播向",
        "https://www.xfzhizuo.cn",
        "讯飞智作依托科大讯飞语音与星火能力，提供数字人定制与口播视频生成，强调配音质量与教育/知识输出等中文场景。",
        "课程讲解、知识口播、国内中文音色要求高时评估；可与讯飞开放平台语音能力对照。",
        "海外语种与创意镜头弱于国际营销向工具；套餐与定制交付路径以官网为准。",
        vendorId="iflytek",
        pricing={"model": "freemium", "currency": "CNY"},
        availability=DOMESTIC,
        region="domestic",
        tags=["ai", "avatar", "domestic", "tts"],
    ),
    mk(
        "volcengine-avatar",
        "火山引擎智能数字人",
        "domestic-suite",
        "字节云数字人 · 企业定制 · 营销/互动",
        "https://www.volcengine.com/product/avatar",
        "火山引擎智能数字人面向企业级虚拟人解决方案，覆盖形象生成、驱动与业务集成，常与字节云、豆包语音等能力同栈落地品牌营销与互动场景。",
        "已用火山/字节云、需要国内企业级数字人定制或 API 集成时评估。",
        "偏企业采购与项目制；个人创作者轻量成片可优先看智影/智作等自助产品。",
        vendorId="volcengine",
        pricing={"model": "usage", "currency": "CNY"},
        availability=DOMESTIC,
        region="domestic",
        tags=["ai", "avatar", "domestic", "cloud"],
    ),
    # ——— 开源说话头 / 本地 ———
    mk(
        "liveportrait",
        "LivePortrait",
        "talking-head-oss",
        "开源人像驱动 · 高效表情迁移 · 研究/自建",
        "https://github.com/KwaiVGI/LivePortrait",
        "LivePortrait（快手视觉团队开源）用驱动视频高效迁移表情与头部运动到目标人像，是自建说话头/写真动画管线的常用开源组件，而非完整 SaaS 数字人平台。",
        "有 GPU、要自建口型/表情驱动或研究管线时评估；要开箱成片请用商业数字人平台。",
        "需自备推理与合规审核；商用授权以仓库协议与上游声明为准，非一键营销成片工具。",
        vendorId=None,
        pricing={"model": "open-source"},
        maturity="beta",
        tags=["ai", "avatar", "open-source", "talking-head"],
        region="overseas",
    ),
    mk(
        "sadtalker",
        "SadTalker",
        "talking-head-oss",
        "开源音频驱动说话头 · 经典管线 · 自托管",
        "https://github.com/OpenTalker/SadTalker",
        "SadTalker 是广为使用的开源音频驱动说话头方案：输入肖像与音频生成口型同步视频，适合自托管实验与低成本 POC，质量与稳定性依赖环境与后处理。",
        "要本地/私有化验证「照片+音频→说话视频」、可接受工程投入时评估。",
        "效果与商业 SaaS 有差距；依赖与 CUDA 环境维护成本高，生产需自建审核与运维。",
        vendorId=None,
        pricing={"model": "open-source"},
        maturity="stable",
        tags=["ai", "avatar", "open-source", "talking-head"],
        region="overseas",
    ),
    mk(
        "heygem",
        "HeyGem",
        "talking-head-oss",
        "硅基开源本地数字人 · 实时交互试验",
        "https://github.com/GuijiAI/HeyGem.ai",
        "HeyGem 是硅基智能开源的本地/实时数字人相关项目，社区常与 DUIX 一并讨论，用于端侧或自托管交互数字人试验，不等同于硅基商业 SaaS 全功能。",
        "要评估开源本地数字人推理、或与硅基生态对照时纳入；商用成片与直播交付看硅基商业产品。",
        "仓库与协议可能分叉迁移；星标热度≠生产就绪，上线前核对授权与模型权重来源。",
        vendorId="guiji-inc",
        pricing={"model": "open-source"},
        maturity="beta",
        availability=DOMESTIC,
        region="domestic",
        tags=["ai", "avatar", "open-source", "realtime"],
    ),
]

VENDORS_DATA: list[dict] = [
    vendor("d-id-inc", "D-ID", url="https://www.d-id.com"),
    vendor("hedra-inc", "Hedra", url="https://www.hedra.com"),
    vendor("colossyan-inc", "Colossyan", url="https://www.colossyan.com"),
    vendor("tavus-inc", "Tavus", url="https://www.tavus.io"),
    vendor("anam-inc", "Anam", url="https://www.anam.ai"),
    vendor("sensetime", "商汤科技", region="domestic", url="https://www.sensetime.com"),
    vendor("guiji-inc", "硅基智能", region="domestic", url="https://website.guiji.ai"),
]

EDGES_DATA: list[dict] = [
    edge(
        "edge-heygen-did-alt",
        "heygen",
        "d-id",
        "alternative_to",
        note="全身多语口播成片 vs 轻量照片说话头",
    ),
    edge(
        "edge-synthesia-colossyan-alt",
        "synthesia",
        "colossyan",
        "alternative_to",
        note="企业培训口播 vs 互动 L&D 情景",
    ),
    edge(
        "edge-heygen-hedra-related",
        "heygen",
        "hedra",
        "commonly_used_with",
        note="写实营销口播 vs 表情/角色表演向",
        weight=0.55,
    ),
    edge(
        "edge-tavus-anam-alt",
        "tavus",
        "anam",
        "alternative_to",
        note="实时对话数字人 API 对照",
    ),
    edge(
        "edge-tavus-heygen-related",
        "tavus",
        "heygen",
        "commonly_used_with",
        note="实时对话 vs 批量口播成片，勿混比",
        weight=0.5,
    ),
    edge(
        "edge-zhiying-heygen-alt",
        "tencent-zhiying",
        "heygen",
        "alternative_to",
        note="国内智影生态 vs 海外营销数字人",
    ),
    edge(
        "edge-senseavatar-zhiying-alt",
        "senseavatar",
        "tencent-zhiying",
        "alternative_to",
        note="商汤如影 vs 腾讯智影（国内数字人）",
    ),
    edge(
        "edge-zhizuo-zhiying-alt",
        "iflytek-zhizuo",
        "tencent-zhiying",
        "alternative_to",
        note="讯飞配音强 vs 腾讯短视频创作一体",
    ),
    edge(
        "edge-volc-avatar-zhiying-related",
        "volcengine-avatar",
        "tencent-zhiying",
        "commonly_used_with",
        note="企业定制云数字人 vs 自助成片工具",
        weight=0.55,
    ),
    edge(
        "edge-guiji-tavus-related",
        "guiji-duix",
        "tavus",
        "commonly_used_with",
        note="国内交互/直播数字人 vs 海外 CVI",
        weight=0.5,
    ),
    edge(
        "edge-guiji-siliconflow-related",
        "guiji-duix",
        "siliconflow",
        "commonly_used_with",
        note="同名易混：数字人公司 vs 推理聚合；能力不同层",
        weight=0.35,
    ),
    edge(
        "edge-heygem-guiji-related",
        "heygem",
        "guiji-duix",
        "commonly_used_with",
        note="开源试验线 vs 硅基商业/SDK 产品",
        weight=0.75,
    ),
    edge(
        "edge-liveportrait-sadtalker-alt",
        "liveportrait",
        "sadtalker",
        "alternative_to",
        note="开源人像驱动对照",
    ),
    edge(
        "edge-liveportrait-did-related",
        "liveportrait",
        "d-id",
        "commonly_used_with",
        note="开源自建管线 vs 商业说话头 API",
        weight=0.55,
    ),
    edge(
        "edge-zhizuo-iflytek-speech-related",
        "iflytek-zhizuo",
        "iflytek-speech",
        "commonly_used_with",
        note="数字人成片产品 vs 讯飞开放平台语音 API",
        weight=0.65,
    ),
]


MIGRATE_IDS = ("heygen", "synthesia")


def migrate_existing() -> int:
    n = 0
    for eid in MIGRATE_IDS:
        path = ENTRIES / f"{eid}.json"
        if not path.exists():
            continue
        data = load(path)
        if data.get("category") == CAT:
            continue
        data["category"] = CAT
        data["subcategory"] = data.get("subcategory") or "avatar-video"
        data["lastReviewed"] = REVIEWED
        tags = list(data.get("tags") or [])
        if "digital-human" not in tags:
            tags.append("digital-human")
            data["tags"] = tags
        save(path, data)
        n += 1
        print("migrate", eid)
    return n


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--overwrite", action="store_true")
    args = ap.parse_args()

    ENTRIES.mkdir(parents=True, exist_ok=True)
    VENDORS.mkdir(parents=True, exist_ok=True)
    EDGES.mkdir(parents=True, exist_ok=True)

    migrated = migrate_existing()

    wrote_e = wrote_v = wrote_g = 0
    for e in ENTRIES_DATA:
        path = ENTRIES / f"{e['id']}.json"
        if path.exists() and not args.overwrite:
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

    known_new = {x["id"] for x in ENTRIES_DATA} | set(MIGRATE_IDS)
    for g in EDGES_DATA:
        path = EDGES / f"{g['id']}.json"
        if path.exists() and not args.overwrite:
            continue
        frm_ok = (ENTRIES / f"{g['from']}.json").exists() or g["from"] in known_new
        to_ok = (ENTRIES / f"{g['to']}.json").exists() or g["to"] in known_new
        if not frm_ok:
            print("skip edge missing from", g["id"])
            continue
        if not to_ok:
            print("skip edge missing to", g["id"], g["to"])
            continue
        save(path, g)
        wrote_g += 1
        print("edge", g["id"])

    print(f"done migrate={migrated} entries={wrote_e} vendors={wrote_v} edges={wrote_g}")


if __name__ == "__main__":
    main()
