#!/usr/bin/env python3
"""3D 生成 / Live2D·骨骼动效 / 游戏与 3D 素材站扩种。

- design-ai-3d：Meshy / Tripo / Rodin 等文生 3D
- design-character-rig：Live2D Cubism / nizima / Spine
- design-game-assets：Sketchfab / OpenGameArt / Kenney / Poly Haven / Fab

用法:
  python3 scripts/expand-3d-live2d-assets-2026-07.py
  python3 scripts/expand-3d-live2d-assets-2026-07.py --overwrite
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
REVIEWED = "2026-07-28"


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
    # typ: alternative_to | commonly_used_with | ...
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

ENTRIES_DATA: list[dict] = [
    # ========== design-ai-image · 文生 3D ==========
    mk(
        "meshy",
        "Meshy",
        "design-ai-3d",
        "ai-3d",
        "文/图生 3D · 绑骨与动画管线 · 游戏/原型常用",
        "https://www.meshy.ai",
        "Meshy 提供文本/图像生成 3D 网格，并支持重拓扑、贴图、绑骨与基础动画导出（如 GLB），面向游戏原型、角色样板与营销 3D 资产快速试错。",
        "需要从概念图快速落到可预览/可挂动画的 3D 角色或道具、且接受 AI 拓扑质量时评估；可与 Tripo、Rodin 同层对比。",
        "商用授权与积分套餐变化快；高模体积大，上线前需压面/换装自研骨骼或公告板。",
        tags=["ai", "3d", "game-art"],
        vendorId="meshy-ai",
        pricing={"model": "subscription"},
        pitfalls=[
            "商用授权与积分套餐变化快，导出前核对许可。",
            "高模体积大，Web/移动端需压面或改公告板。",
        ],
    ),
    mk(
        "tripo",
        "Tripo",
        "design-ai-3d",
        "ai-3d",
        "文/图生 3D · 多格式导出 · 偏产品与游戏样板",
        "https://www.tripo3d.ai",
        "Tripo（VAST）提供 AI 文生/图生 3D，强调较快出模与多格式导出，适合产品可视化、游戏概念体与电商 3D 试制。",
        "需要与 Meshy 对照的第二家文生 3D、或特定导出格式/速度偏好时纳入短名单。",
        "拓扑与 UV 质量因任务波动；角色绑骨与面部细节通常仍需 DCC 或人工。",
        tags=["ai", "3d"],
        vendorId="tripo-ai",
        pricing={"model": "freemium"},
        pitfalls=[
            "拓扑/UV 不稳定，量产角色仍常回 DCC。",
            "积分与商用条款以官网为准，注意区域可用性。",
        ],
    ),
    mk(
        "rodin",
        "Rodin",
        "design-ai-3d",
        "ai-3d",
        "Hyper3D 文生 3D · 偏高质量网格与材质",
        "https://hyper3d.ai",
        "Rodin（Hyper3D）面向高质量 AI 3D 生成，强调网格完整性与材质表现，常见于数字人、道具与影视概念资产试验。",
        "对网格观感要求高于「能预览就行」、可接受更高单价或排队时评估；与 Meshy/Tripo 对照。",
        "价格与额度策略偏专业向；动画/绑骨能力弱于部分竞品，需另接管线。",
        tags=["ai", "3d"],
        vendorId="hyper3d",
        pricing={"model": "subscription"},
        pitfalls=[
            "绑骨/动画管线不如 Meshy 一体；需另接工具。",
            "成本与额度适合样板，不适合无预算量产。",
        ],
    ),
    mk(
        "csm-ai",
        "CSM",
        "design-ai-3d",
        "ai-3d",
        "图像/视频转 3D · 偏扫描重建与产品捕捉",
        "https://www.csm.ai",
        "CSM 侧重从图像或视频序列重建 3D，接近「轻量扫描/捕捉」叙事，适合实物产品、场景片段进入数字资产库。",
        "已有多视角照片或短视频、希望进引擎做产品 3D 时评估；与纯文生 3D（Meshy）互补。",
        "拍摄规范影响成败；角色绑定与游戏动画仍需下游工具。",
        tags=["ai", "3d", "scan"],
        vendorId="csm-inc",
        pricing={"model": "freemium"},
        pitfalls=[
            "输入照片质量与角度覆盖决定结果上限。",
            "不是角色表演级绑骨方案。",
        ],
    ),
    # ========== design-motion · Live2D / Spine ==========
    mk(
        "live2d-cubism",
        "Live2D Cubism",
        "design-character-rig",
        "live2d",
        "2.5D 角色网格绑定 · Editor+SDK · moc3 行业标准",
        "https://www.live2d.com",
        "Live2D Cubism 用网格变形让 2D 立绘「活」起来，产出 moc3 等运行时格式，是虚拟主播、日式 RPG UI/立绘战斗的常见标准；含 Editor 与多端 SDK。",
        "需要眨眼/口型/摆动级角色表演、且愿意投入绑定与授权时选用；与 Spine、Rive、自研分件木偶对照。",
        "Editor/SDK 按主体规模收费；moc3 无法从单张立绘自动可靠生成，需分层 PSD+绑定。",
        tags=["animation", "live2d", "character"],
        vendorId="live2d-inc",
        pricing={"model": "subscription"},
        pitfalls=[
            "中大型企业 SDK/Editor 授权成本高，需对照官方价目。",
            "单张立绘不能自动变成可用 moc3，必须分层与绑定。",
        ],
        docsUrl="https://docs.live2d.com",
    ),
    mk(
        "nizima",
        "nizima",
        "design-character-rig",
        "live2d",
        "Live2D 官方向素材市场 · 买现成模型与部件",
        "https://nizima.com",
        "nizima 是 Live2D 生态常见的模型与部件交易市场，可购买或获取免费/付费 moc 相关资产，缩短从零绑定的时间。",
        "需要现成 Live2D 角色做原型、虚拟形象或学习参考，而不自建全套绑定时评估。",
        "每套素材许可不同（改作/商用/再分发）；品牌定制形象仍难直接买到。",
        tags=["animation", "live2d", "stock"],
        vendorId="live2d-inc",
        pricing={"model": "freemium"},
        pitfalls=[
            "许可因商品而异，上线前逐条核对。",
            "与自有 IP 门派形象通常对不上，只能做管线验证。",
        ],
    ),
    mk(
        "spine",
        "Spine",
        "design-character-rig",
        "skeletal-2d",
        "2D 骨骼动画编辑器 · skel/atlas · 游戏角色主流",
        "https://esotericsoftware.com",
        "Spine（Esoteric）是游戏业常用的 2D 骨骼动画工具，导出 skel/json + atlas，runtime 覆盖多数引擎；适合平台动作、格斗与 UI 骨骼角色。",
        "需要比 Live2D 更「游戏动作向」的剪影/换装骨骼、且团队熟悉 Spine 工作流时优先。",
        "Editor 许可证与 runtime 分发规则需严格合规；无许可证不可把官方 runtime 打进产品。",
        tags=["animation", "spine", "game-art"],
        vendorId="esoteric-software",
        pricing={"model": "subscription"},
        pitfalls=[
            "产品内嵌官方 runtime 需持有对应 Editor 许可。",
            "从单张立绘自动出 skel 无成熟商用 SaaS。",
        ],
    ),
    # ========== design-stock · 3D/游戏素材站 ==========
    mk(
        "sketchfab",
        "Sketchfab",
        "design-game-assets",
        "3d-stock",
        "在线 3D 模型库与浏览 · 下载授权分层",
        "https://sketchfab.com",
        "Sketchfab 提供海量可在线预览的 3D 模型，含免费与付费授权分层，覆盖游戏、建筑可视化与 AR 试用资产。",
        "需要快速找参考模、免费 CC 模或购买现成道具进引擎时评估；与 Poly Haven、Fab 对照。",
        "免费层许可混杂（CC0/CC-BY 等）；下载与 API 限额、部分地区访问需自备网络策略。",
        tags=["stock", "3d", "game-art"],
        vendorId="sketchfab-inc",
        pricing={"model": "freemium"},
        availability=US_BLOCKED,
        pitfalls=[
            "许可与是否可商用/改作必须逐模型核对。",
            "国内访问不稳定时需备用镜像或本地缓存。",
        ],
    ),
    mk(
        "opengameart",
        "OpenGameArt",
        "design-game-assets",
        "game-stock",
        "开源游戏素材社区 · CC0/CC-BY 常见",
        "https://opengameart.org",
        "OpenGameArt 聚集免费/开源游戏贴图、精灵、音效与部分 3D，许可以 CC0、CC-BY 等为主，适合原型与独立游戏起步。",
        "需要可商用免费素材、能接受风格不统一与质量参差时作为第一站检索。",
        "视觉风格混杂；商用项目仍要逐条确认许可与署名要求。",
        tags=["stock", "game-art", "free"],
        pricing={"model": "free"},
        pitfalls=[
            "质量与风格极不统一，品牌向项目需精筛。",
            "署名与衍生协议因上传者而异。",
        ],
    ),
    mk(
        "kenney",
        "Kenney",
        "design-game-assets",
        "game-stock",
        "CC0 游戏素材包 · 像素/低模/UI 原型友好",
        "https://kenney.nl/assets",
        "Kenney 提供大量 CC0 游戏资产包（2D/3D/音频/UI），几乎无署名压力，是 Game Jam 与玩法原型的默认素材源之一。",
        "需要快速可商用占位美术、像素或低模风格、希望授权最省心时优先。",
        "风格辨识度高，成品上线常被认出「Kenney 味」，正式品牌向需替换。",
        tags=["stock", "game-art", "free", "cc0"],
        pricing={"model": "free"},
        pitfalls=[
            "视觉辨识度高，正式产品建议换装。",
            "不覆盖写实武侠/旗舰角色需求。",
        ],
    ),
    mk(
        "polyhaven",
        "Poly Haven",
        "design-game-assets",
        "3d-stock",
        "CC0 HDRI/贴图/模型 · 3D 场景光照友好",
        "https://polyhaven.com",
        "Poly Haven 提供 CC0 的 HDRI、PBR 贴图与部分模型，适合 Blender/引擎里搭真实感光照与环境。",
        "需要免费可商用环境光与材质、做产品渲染或场景铺底时评估。",
        "角色/动画资产极少；偏环境与材质，不解决 Live2D/角色绑定。",
        tags=["stock", "3d", "cc0", "hdri"],
        pricing={"model": "free"},
        pitfalls=[
            "几乎无角色表演资产。",
            "高分辨率 HDRI 体积大，Web 实时需降采样。",
        ],
    ),
    mk(
        "fab",
        "Fab",
        "design-game-assets",
        "3d-stock",
        "Epic 数字资产商店 · 原 Marketplace/Quixel 整合向",
        "https://www.fab.com",
        "Fab 是 Epic 侧数字内容商店方向（整合原 Marketplace / Quixel 等叙事），提供游戏与影视向 3D、材质、特效等资产交易与部分免费内容。",
        "Unreal/Epic 生态内采购场景资产、或需要影院级扫描材质时评估；与 Sketchfab 互补。",
        "引擎绑定与授权条款复杂；免费资产亦有使用限制，导出到非 UE 管线前要读许可。",
        tags=["stock", "3d", "game-art", "unreal"],
        vendorId="epic-games",
        pricing={"model": "freemium"},
        availability=US_BLOCKED,
        pitfalls=[
            "许可与引擎绑定需逐项核对。",
            "国内访问与支付可能受阻。",
        ],
    ),
    mk(
        "craftpix",
        "Craftpix",
        "design-game-assets",
        "game-stock",
        "2D 游戏素材站 · 免费包+付费包 · 精灵/UI 常见",
        "https://craftpix.net",
        "Craftpix 提供 2D 游戏精灵、UI、背景等免费与付费包，偏休闲与平台跳跃原型，许可按包说明。",
        "需要成套 2D 关卡/UI 素材、快速拼出可玩 Demo 时评估；与 Kenney、OpenGameArt 对照。",
        "免费包常有署名或非独占限制；风格偏欧美卡通，难直接用于水墨武侠。",
        tags=["stock", "game-art", "2d"],
        pricing={"model": "freemium"},
        pitfalls=[
            "免费与付费许可不同，注意署名与再分发。",
            "美术风格与国风/武侠项目匹配度低。",
        ],
    ),
]

VENDORS_DATA = [
    vendor("meshy-ai", "Meshy", url="https://www.meshy.ai"),
    vendor("tripo-ai", "VAST / Tripo", url="https://www.tripo3d.ai"),
    vendor("hyper3d", "Hyper3D", url="https://hyper3d.ai"),
    vendor("csm-inc", "CSM", url="https://www.csm.ai"),
    vendor("live2d-inc", "Live2D Inc.", url="https://www.live2d.com"),
    vendor("esoteric-software", "Esoteric Software", url="https://esotericsoftware.com"),
    vendor("sketchfab-inc", "Sketchfab", url="https://sketchfab.com"),
    vendor("epic-games", "Epic Games", url="https://www.epicgames.com"),
]

EDGES_DATA = [
    edge(
        "edge-meshy-tripo-alternative",
        "meshy",
        "tripo",
        "alternative_to",
        note="文生 3D 同层竞品",
    ),
    edge(
        "edge-meshy-rodin-alternative",
        "meshy",
        "rodin",
        "alternative_to",
        note="文生 3D：速度/一体管线 vs 网格观感",
    ),
    edge(
        "edge-meshy-csm-related",
        "meshy",
        "csm-ai",
        "commonly_used_with",
        note="文生概念模 vs 照片/视频重建",
        weight=0.55,
    ),
    edge(
        "edge-live2d-nizima-related",
        "live2d-cubism",
        "nizima",
        "commonly_used_with",
        note="工具链 vs 模型素材市场",
        weight=0.8,
    ),
    edge(
        "edge-live2d-spine-alternative",
        "live2d-cubism",
        "spine",
        "alternative_to",
        note="2.5D 网格表演 vs 游戏 2D 骨骼",
    ),
    edge(
        "edge-live2d-rive-related",
        "live2d-cubism",
        "rive",
        "commonly_used_with",
        note="角色表演 vs 交互 UI/状态机动效",
        weight=0.55,
    ),
    edge(
        "edge-spine-rive-related",
        "spine",
        "rive",
        "commonly_used_with",
        note="游戏骨骼 vs 产品交互动效",
        weight=0.5,
    ),
    edge(
        "edge-sketchfab-polyhaven-related",
        "sketchfab",
        "polyhaven",
        "commonly_used_with",
        note="模型市场 vs CC0 环境/HDRI",
        weight=0.6,
    ),
    edge(
        "edge-opengameart-kenney-related",
        "opengameart",
        "kenney",
        "commonly_used_with",
        note="开源社区素材 vs CC0 成套包",
        weight=0.75,
    ),
    edge(
        "edge-kenney-craftpix-alternative",
        "kenney",
        "craftpix",
        "alternative_to",
        note="CC0 原型包 vs 免费/付费 2D 游戏包",
    ),
    edge(
        "edge-fab-sketchfab-alternative",
        "fab",
        "sketchfab",
        "alternative_to",
        note="Epic 生态资产店 vs 通用 3D 浏览下载",
    ),
    edge(
        "edge-meshy-spline-related",
        "meshy",
        "spline",
        "commonly_used_with",
        note="生成网格资产 vs Web 内建 3D 场景编辑",
        weight=0.45,
    ),
    edge(
        "edge-live2d-lottiefiles-related",
        "live2d-cubism",
        "lottiefiles",
        "commonly_used_with",
        note="角色网格 vs 营销矢量微动效，不同层",
        weight=0.35,
    ),
]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--overwrite", action="store_true")
    args = ap.parse_args()

    ENTRIES.mkdir(parents=True, exist_ok=True)
    VENDORS.mkdir(parents=True, exist_ok=True)
    EDGES.mkdir(parents=True, exist_ok=True)

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

    for g in EDGES_DATA:
        path = EDGES / f"{g['id']}.json"
        if path.exists() and not args.overwrite:
            continue
        # skip edge if endpoint missing
        if not (ENTRIES / f"{g['from']}.json").exists() and g["from"] not in {x["id"] for x in ENTRIES_DATA}:
            print("skip edge missing from", g["id"])
            continue
        if not (ENTRIES / f"{g['to']}.json").exists() and g["to"] not in {x["id"] for x in ENTRIES_DATA}:
            # allow existing catalog targets
            if not (ENTRIES / f"{g['to']}.json").exists():
                print("skip edge missing to", g["id"], g["to"])
                continue
        save(path, g)
        wrote_g += 1
        print("edge", g["id"])

    print(f"done entries={wrote_e} vendors={wrote_v} edges={wrote_g}")


if __name__ == "__main__":
    main()
