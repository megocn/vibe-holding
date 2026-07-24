#!/usr/bin/env python3
"""按 Arena / Artificial Analysis 文生图榜回填与扩种 design-ai-image。

用法:
  python3 scripts/expand-image-arena-2026-07.py
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTENT = ROOT / "content"
ENTRIES = CONTENT / "entries"
VENDORS = CONTENT / "vendors"
EDGES = CONTENT / "edges"
RANKING = CONTENT / "ranking-systems.json"
REVIEWED = "2026-07-24"
ASOF = "2026-07-24"
PERIOD = "2026-07"
ARENA = "https://arena.ai/leaderboard/text-to-image"
AA = "https://artificialanalysis.ai/image/leaderboard/text-to-image"


def save(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def arena(rank: int, score: int, note: str) -> dict:
    return {
        "systemId": "lmarena-image",
        "rank": rank,
        "score": score,
        "scoreLabel": f"{score} Elo",
        "period": PERIOD,
        "note": note,
        "sourceUrl": ARENA,
        "asOf": ASOF,
    }


def aa(rank: int, score: int, note: str) -> dict:
    return {
        "systemId": "aa-image-arena",
        "rank": rank,
        "score": score,
        "scoreLabel": f"{score} Elo",
        "period": PERIOD,
        "note": note,
        "sourceUrl": AA,
        "asOf": ASOF,
    }


def desc(what: str, when: str, caution: str) -> str:
    return f"{what}\n\n{when}\n\n{caution}\n"


def ensure_vendor(vid: str, name: str, url: str, region: str = "overseas") -> None:
    path = VENDORS / f"{vid}.json"
    if path.exists():
        return
    save(path, {"id": vid, "name": name, "region": region, "url": url})
    print(f"+ vendor {vid}")


def write_entry(e: dict) -> None:
    assert len(e["oneLiner"]) <= 60, (e["id"], len(e["oneLiner"]), e["oneLiner"])
    assert len(e["descriptionMd"]) >= 120, e["id"]
    path = ENTRIES / f"{e['id']}.json"
    save(path, e)
    print(f"{'~' if path.exists() else '+'} entry {e['id']}")


def write_edge(eid: str, frm: str, to: str, typ: str = "alternative_to", weight: float = 0.7, note: str | None = None) -> None:
    path = EDGES / f"{eid}.json"
    if path.exists():
        return
    e = {
        "id": eid,
        "from": frm,
        "to": to,
        "type": typ,
        "weight": weight,
        "confidence": "community",
        "sources": [],
        "createdAt": REVIEWED,
    }
    if note:
        e["note"] = note
    save(path, e)
    print(f"+ edge {eid}")


def patch_existing(eid: str, **updates) -> None:
    path = ENTRIES / f"{eid}.json"
    e = load(path)
    e.update(updates)
    e["lastReviewed"] = REVIEWED
    save(path, e)
    print(f"~ entry {eid}")


def ensure_ranking_systems() -> None:
    systems = load(RANKING)
    ids = {s["id"] for s in systems}
    if "aa-image-arena" not in ids:
        # insert after lmarena-image
        idx = next(i for i, s in enumerate(systems) if s["id"] == "lmarena-image")
        systems.insert(
            idx + 1,
            {
                "id": "aa-image-arena",
                "name": "Artificial Analysis · Text-to-Image Arena",
                "shortName": "AA Image",
                "categories": ["design-ai-image"],
                "metric": "mixed",
                "metricUnit": "Elo",
                "url": AA,
                "description": "独立第三方文生图盲测 Elo，常与 Arena 交叉验证；含开源权重与 API 价参考。",
                "authority": "Artificial Analysis",
                "updateCadence": "weekly",
                "order": 2,
            },
        )
        # product-hunt-design already order 2 → bump to 3 for design-ai-image secondary
        for s in systems:
            if s["id"] == "product-hunt-design":
                s["order"] = 3
        save(RANKING, systems)
        print("+ ranking aa-image-arena")
    else:
        print("= ranking aa-image-arena exists")


def main() -> None:
    ensure_ranking_systems()

    # —— 新厂商 ——
    ensure_vendor("reve-inc", "Reve", "https://www.reve.com/")
    ensure_vendor("hidream-ai", "HiDream.ai", "https://hidream.ai/")
    ensure_vendor("krea-ai", "Krea", "https://www.krea.ai/")
    ensure_vendor("microsoft-ai", "Microsoft AI", "https://microsoft.ai/")

    # —— 扩种：Arena/AA 前列缺失 ——
    new_entries = [
        {
            "id": "reve",
            "name": "Reve",
            "category": "design-ai-image",
            "subcategory": "image-gen",
            "oneLiner": "Layout-first 4K 文生图 · Arena #2 · 构图可编",
            "officialUrl": "https://www.reve.com/",
            "docsUrl": "https://www.reve.com/",
            "vendorId": "reve-inc",
            "region": "overseas",
            "pricing": {"model": "usage", "currency": "USD"},
            "availability": {
                "chinaAccessible": False,
                "needsCompany": False,
                "needsIcp": False,
                "regions": ["global"],
            },
            "tags": ["ai", "image"],
            "maturity": "stable",
            "currentVersion": "Reve 2.1",
            "updates": [
                {
                    "date": "2026-07-09",
                    "type": "release",
                    "version": "Reve 2.1",
                    "summary": "原生 4K、layout-first 规划层；Arena/AA 文生图榜紧随 GPT Image 2",
                    "source": "https://www.reve.com/",
                }
            ],
            "rankings": [
                arena(2, 1302, "Text-to-Image · reve-2.1"),
                aa(2, 1306, "Reve 2.1"),
            ],
            "sources": [ARENA, AA, "https://www.reve.com/"],
            "pitfalls": [
                "新旗舰投票样本仍在积累（Arena Preliminary）；国内直连与企业采购路径需核对",
            ],
            "descriptionMd": desc(
                "Reve（现旗舰 Reve 2.1）以 layout-first 规划层再渲染，强调原生 4K、构图可控与文字/细节一致性，是 2026 中 Arena 与 AA 文生图榜上仅次于 GPT Image 2 的闭源选手。",
                "需要 4K 营销静帧、精确排版构图或可编辑中间表示时评估；与 GPT Image 2、Ideogram 4 对照。",
                "新旗舰投票样本仍在积累；国内直连与企业采购路径需核对。",
            ),
        },
        {
            "id": "google-nano-banana",
            "name": "Nano Banana",
            "category": "design-ai-image",
            "subcategory": "image-gen",
            "oneLiner": "Gemini 文生图/改图 · Nano Banana 2 · 消费级热",
            "officialUrl": "https://gemini.google/overview/image-generation/",
            "vendorId": "google",
            "region": "overseas",
            "pricing": {"model": "freemium", "currency": "USD", "notes": "Gemini 订阅档；API 按量"},
            "availability": {
                "chinaAccessible": False,
                "needsCompany": False,
                "needsIcp": False,
                "regions": ["global"],
            },
            "tags": ["ai", "image", "gemini"],
            "maturity": "stable",
            "currentVersion": "Nano Banana 2",
            "updates": [
                {
                    "date": "2026-02-01",
                    "type": "release",
                    "version": "Nano Banana 2",
                    "summary": "Gemini 3.1 Flash Image 线；消费级出图/改图主力，Arena 前列",
                    "source": "https://gemini.google/overview/image-generation/",
                }
            ],
            "rankings": [
                arena(5, 1261, "gemini-3.1-flash-image · nano-banana-2"),
                aa(7, 1253, "Nano Banana 2 (Gemini 3.1 Flash Image)"),
            ],
            "sources": [
                "https://gemini.google/overview/image-generation/",
                ARENA,
                AA,
            ],
            "pitfalls": [
                "与 Vertex Imagen 企业线不同入口；国内不可用；Pro/Lite 档位与拒图策略需对照文档",
            ],
            "descriptionMd": desc(
                "Nano Banana 是 Google Gemini 侧的文生图/改图产品线（现 Nano Banana 2 / Pro / Lite），强调世界知识、推理式改图与消费级速度，与 ChatGPT 出图并列最热入口之一。",
                "已在 Gemini App/AI Studio 做创意出图、快速改图或品牌试稿时默认评估；企业合同与合规出图另看 Imagen（Vertex）。",
                "与 Imagen 企业线不同入口；国内不可用；档位与拒图策略需对照文档。",
            ),
        },
        {
            "id": "mai-image",
            "name": "MAI Image",
            "category": "design-ai-image",
            "subcategory": "image-gen",
            "oneLiner": "Microsoft AI 文生图 · 2.5 旗舰 · 品牌设计向",
            "officialUrl": "https://microsoft.ai/models/mai-image-2-5/",
            "vendorId": "microsoft-ai",
            "region": "overseas",
            "pricing": {"model": "usage", "currency": "USD"},
            "availability": {
                "chinaAccessible": False,
                "needsCompany": False,
                "needsIcp": False,
                "regions": ["global"],
            },
            "tags": ["ai", "image", "microsoft"],
            "maturity": "stable",
            "currentVersion": "MAI-Image-2.5",
            "updates": [
                {
                    "date": "2026-06-01",
                    "type": "release",
                    "version": "MAI-Image-2.5",
                    "summary": "设计感知/商业视觉向旗舰；AA 文生图榜前列，Arena 同步进入头部",
                    "source": "https://microsoft.ai/models/mai-image-2-5/",
                }
            ],
            "rankings": [
                arena(6, 1257, "mai-image-2.5"),
                aa(3, 1265, "MAI-Image-2.5"),
            ],
            "sources": [
                "https://microsoft.ai/models/mai-image-2-5/",
                ARENA,
                AA,
            ],
            "pitfalls": [
                "国内直连与 Azure 区域可用性需核对；品牌安全与内容策略随 Microsoft AI 政策变化",
            ],
            "descriptionMd": desc(
                "MAI Image 是 Microsoft AI 的文生图族（现旗舰 MAI-Image-2.5，另有 Flash/Efficient 档），面向写实与品牌/商业设计可控编辑，在 AA 与 Arena 文生图榜均处头部。",
                "已在 Microsoft/Azure 生态、需要商业视觉与精确改图时评估；可与 GPT Image、Nano Banana 对照。",
                "国内直连与区域可用性需核对；品牌安全与内容策略随政策变化。",
            ),
        },
        {
            "id": "meta-muse-image",
            "name": "Muse Image",
            "category": "design-ai-image",
            "subcategory": "image-gen",
            "oneLiner": "Meta AI 文生图 · agentic · Arena 前列",
            "officialUrl": "https://ai.meta.com/blog/introducing-muse-image-muse-video-msl/",
            "vendorId": "meta",
            "region": "overseas",
            "pricing": {"model": "freemium", "currency": "USD"},
            "availability": {
                "chinaAccessible": False,
                "needsCompany": False,
                "needsIcp": False,
                "regions": ["global"],
            },
            "tags": ["ai", "image", "meta"],
            "maturity": "beta",
            "currentVersion": "Muse Image",
            "updates": [
                {
                    "date": "2026-07-07",
                    "type": "release",
                    "version": "Muse Image",
                    "summary": "Meta AI / IG 侧 agentic 图像生成；Arena Text-to-Image 进入前三档",
                    "source": "https://ai.meta.com/blog/introducing-muse-image-muse-video-msl/",
                }
            ],
            "rankings": [
                arena(3, 1280, "muse-image · Preliminary"),
            ],
            "sources": [
                "https://ai.meta.com/blog/introducing-muse-image-muse-video-msl/",
                ARENA,
            ],
            "pitfalls": [
                "Arena 样本仍为 Preliminary；企业 API/商用条款与 Meta 产品入口变化快",
            ],
            "descriptionMd": desc(
                "Muse Image 是 Meta 2026-07 推出的 agentic 文生图能力，经 Meta AI / Instagram 等消费入口提供，强调工具调用与自迭代生成，Arena 文生图榜迅速冲到前列。",
                "已在 Meta 生态做社交/创作者出图，或观察 agentic 图像工作流时纳入短名单。",
                "投票样本仍在积累；企业 API 与商用条款、产品入口变化快。",
            ),
        },
        {
            "id": "hidream",
            "name": "HiDream",
            "category": "design-ai-image",
            "subcategory": "image-gen",
            "oneLiner": "HiDream-O1 · 开源统一生成 · AA 前列",
            "officialUrl": "https://hidream.ai/",
            "githubUrl": "https://github.com/HiDream-ai/HiDream-O1-Image",
            "vendorId": "hidream-ai",
            "region": "overseas",
            "pricing": {"model": "freemium", "currency": "USD", "notes": "开源权重 MIT；托管 API 另计"},
            "availability": {
                "chinaAccessible": True,
                "needsCompany": False,
                "needsIcp": False,
                "regions": ["global"],
            },
            "tags": ["ai", "image", "open-source"],
            "maturity": "stable",
            "currentVersion": "HiDream-O1-Image 1.5",
            "updates": [
                {
                    "date": "2026-05-08",
                    "type": "release",
                    "version": "HiDream-O1-Image",
                    "summary": "像素级统一 Transformer；文生图/编辑/个性化；开源权重",
                    "source": "https://github.com/HiDream-ai/HiDream-O1-Image",
                }
            ],
            "rankings": [
                arena(37, 1118, "hidream-o1-image"),
                aa(4, 1262, "HiDream-O1-Image-1.5"),
            ],
            "sources": [
                "https://hidream.ai/",
                "https://github.com/HiDream-ai/HiDream-O1-Image",
                AA,
                ARENA,
            ],
            "pitfalls": [
                "自托管显存与工程成本不低；商业托管价与开源许可分开核对",
            ],
            "descriptionMd": desc(
                "HiDream-O1-Image 是 HiDream.ai 的统一图像生成基础模型（开源），像素级 Unified Transformer，覆盖文生图、指令编辑与主体个性化；AA 文生图榜上闭源/开源变体均处前列。",
                "需要开源可控、ComfyUI/自托管或与闭源旗舰对照的研究/产品管线时评估。",
                "自托管显存与工程成本不低；商业托管价与开源许可分开核对。",
            ),
        },
        {
            "id": "krea",
            "name": "Krea",
            "category": "design-ai-image",
            "subcategory": "image-gen",
            "oneLiner": "Krea 2 · 实时创意图 · AA/Arena 中上",
            "officialUrl": "https://www.krea.ai/",
            "vendorId": "krea-ai",
            "region": "overseas",
            "pricing": {"model": "freemium", "currency": "USD"},
            "availability": {
                "chinaAccessible": True,
                "needsCompany": False,
                "needsIcp": False,
                "regions": ["global"],
            },
            "tags": ["ai", "image"],
            "maturity": "stable",
            "currentVersion": "Krea 2",
            "updates": [
                {
                    "date": "2026-05-01",
                    "type": "release",
                    "version": "Krea 2",
                    "summary": "Medium/Large/Turbo 分档；独立实验室模型，AA 文生图榜中上",
                    "source": "https://www.krea.ai/",
                }
            ],
            "rankings": [
                arena(36, 1120, "krea-2-medium"),
                aa(15, 1197, "Krea 2 Medium"),
            ],
            "sources": ["https://www.krea.ai/", ARENA, AA],
            "pitfalls": [
                "实时画布体验与纯 API 管线能力不同；商用许可与开源档分开核对",
            ],
            "descriptionMd": desc(
                "Krea 以实时创意图画布与自研 Krea 2 模型族（Medium/Large/Turbo）著称，在 AA 与 Arena 文生图榜处于中上，适合设计师边画边出图。",
                "需要交互式探索、风格实验或独立于大厂闭源栈的创意图时试用。",
                "画布体验与纯 API 管线能力不同；商用许可与开源档分开核对。",
            ),
        },
        {
            "id": "luma-uni",
            "name": "Luma UNI",
            "category": "design-ai-image",
            "subcategory": "image-gen",
            "oneLiner": "Luma 文生图 · UNI 1.1 Max · 与视频同栈",
            "officialUrl": "https://lumalabs.ai/api",
            "vendorId": "luma-labs",
            "region": "overseas",
            "pricing": {"model": "usage", "currency": "USD"},
            "availability": {
                "chinaAccessible": False,
                "needsCompany": False,
                "needsIcp": False,
                "regions": ["global"],
            },
            "tags": ["ai", "image", "luma"],
            "maturity": "stable",
            "currentVersion": "UNI 1.1 Max",
            "updates": [
                {
                    "date": "2026-05-01",
                    "type": "release",
                    "version": "UNI 1.1",
                    "summary": "Luma 文生图旗舰线；Arena/AA 进入前三十档",
                    "source": "https://lumalabs.ai/api",
                }
            ],
            "rankings": [
                arena(15, 1188, "uni-1.1-max"),
                aa(27, 1170, "Luma UNI 1 Max"),
            ],
            "sources": ["https://lumalabs.ai/api", ARENA, AA],
            "pitfalls": [
                "与 Dream Machine 视频是同厂不同模态；按量成本与商用条款需核对",
            ],
            "descriptionMd": desc(
                "Luma UNI 是 Luma AI 的文生图线（现 UNI 1.1 / Max），与 Dream Machine 视频同生态，强调创意静帧与 API 接入，Arena/AA 文生图榜处于第一梯队中后段。",
                "已在 Luma 做视频、需要同厂静帧资产或 API 批量出图时评估；与 Flux、Recraft 对照。",
                "与视频能力分列选型；按量成本与商用条款需核对。",
            ),
        },
    ]

    for e in new_entries:
        e["lastReviewed"] = REVIEWED
        if "updates" not in e:
            e["updates"] = []
        write_entry(e)

    # —— 回填已有条目 ——
    patch_existing(
        "openai-gpt-image",
        rankings=[
            arena(1, 1385, "gpt-image-2 (medium)"),
            aa(1, 1337, "GPT Image 2 (high)"),
        ],
        sources=[
            "https://platform.openai.com/docs/guides/images",
            "https://developers.openai.com/api/docs/models/gpt-image-2",
            ARENA,
            AA,
        ],
    )

    patch_existing(
        "flux-ai",
        name="Flux",
        currentVersion="FLUX.2",
        oneLiner="BFL FLUX.2 · API/开源分档 · 自托管首选",
        descriptionMd=desc(
            "Flux（Black Forest Labs）现以 FLUX.2 族（max/pro/flex/dev/klein）为主力，质量与速度分档清晰，API 与 ComfyUI/开源权重生态成熟，是自托管与开放管线的默认海外选项。",
            "需要 Midjourney 级可控美学之外的 API/自托管、或开源权重进产品 pipeline 时评估 FLUX.2。",
            "pro/max licensing 与 NSFW 政策需遵守；算力成本随分辨率上升。",
        ),
        pitfalls=["pro/max licensing 与 NSFW 政策需遵守；算力成本随分辨率上升。"],
        rankings=[
            arena(20, 1162, "flux-2-max"),
            aa(17, 1192, "FLUX.2 [max]"),
        ],
        sources=["https://blackforestlabs.ai", "https://bfl.ai/models/flux-2", ARENA, AA],
        updates=[
            {
                "date": "2025-11-01",
                "type": "release",
                "version": "FLUX.2",
                "summary": "max/pro/flex/dev 等分档接档 FLUX.1；写实与光学细节增强",
                "source": "https://bfl.ai/models/flux-2",
            }
        ],
    )

    patch_existing(
        "ideogram",
        currentVersion="Ideogram 4.0",
        oneLiner="Ideogram 4 · 图内文字强 · 开源权重可选",
        descriptionMd=desc(
            "Ideogram 以图内可读文字与排版见长；现旗舰 Ideogram 4.0（Quality 等档，部分开源权重）在 Arena/AA 文生图榜进入前十五至三十档，适合海报、logo 与社交文案落地。",
            "营销图需内嵌 slogan/标题且少后期 PS 文字时优先试用；与 GPT Image、Reve 对照文字渲染。",
            "艺术风格上限因场景而异；API batch 与开源许可查最新。",
        ),
        pitfalls=["艺术风格上限因场景而异；API batch 与开源许可查最新。"],
        rankings=[
            arena(13, 1207, "ideogram-4.0-quality"),
            aa(29, 1169, "Ideogram 4.0 Quality"),
        ],
        sources=["https://ideogram.ai", "https://ideogram.ai/blog/4.0/", ARENA, AA],
        updates=[
            {
                "date": "2026-06-01",
                "type": "release",
                "version": "Ideogram 4.0",
                "summary": "文字/布局增强；Quality 档进入 Arena 前列，部分开源权重",
                "source": "https://ideogram.ai/blog/4.0/",
            }
        ],
    )

    patch_existing(
        "recraft",
        currentVersion="Recraft V4.1",
        oneLiner="Recraft V4.1 · 品牌矢量/设计语言 · Utility Pro",
        descriptionMd=desc(
            "Recraft 专注品牌一致的矢量插画、icon 与设计语言生成；现 V4.1（含 Utility Pro）在 Arena/AA 文生图榜进入前二十，适合 UI 资产与品牌视觉批量。",
            "设计系统需要统一插画风格、导出 SVG 或品牌资产时评估；与 Ideogram、GPT Image 对照。",
            "照片级 realism 非最强项；商业 license 条款需读清。",
        ),
        pitfalls=["照片级 realism 非最强项；商业 license 条款需读清。"],
        rankings=[
            arena(19, 1169, "recraft-v4.1-utility-pro"),
            aa(11, 1207, "Recraft V4.1 Utility Pro"),
        ],
        sources=["https://www.recraft.ai", ARENA, AA],
        updates=[
            {
                "date": "2026-05-01",
                "type": "release",
                "version": "Recraft V4.1",
                "summary": "Utility Pro 等档；设计向盲测偏好上升",
                "source": "https://www.recraft.ai/blog/recraft-v4-1-more-beautiful-by-nature",
            }
        ],
    )

    patch_existing(
        "grok-imagine",
        maturity="stable",
        currentVersion="Grok Imagine Quality",
        oneLiner="xAI 文生图 · Imagine Quality · Arena 前十二",
        descriptionMd=desc(
            "Grok Imagine 是 xAI 的图像生成能力（含 quality/pro 等档），与 Grok 对话生态绑定；`grok-imagine-image-quality` 在 Arena 文生图榜约第 12、AA 约第 14。",
            "已在 xAI/Grok 生态需要快速出图或创意视觉时选用；严肃品牌管线仍对照 GPT Image / Flux / Midjourney。",
            "区域与 API 成熟度变化快；企业合规与商用条款需核对。",
        ),
        rankings=[
            arena(12, 1229, "grok-imagine-image-quality"),
            aa(14, 1200, "grok-imagine-image-quality"),
        ],
        sources=["https://x.ai", "https://docs.x.ai/developers/models/grok-imagine-image-quality", ARENA, AA],
    )

    patch_existing(
        "jimeng",
        currentVersion="Seedream 5.0 Pro",
        oneLiner="即梦图像 · Seedream 5.0 Pro · 国内榜前列",
        descriptionMd=desc(
            "即梦（海外 Dreamina）是字节剪映团队的一站式 AIGC 平台；图像侧现以 Seedream 5.0 Pro 等档为代表，在 Arena/AA 文生图榜进入前十五，是国内可达的高热度选项。",
            "国内营销图、电商主图、创意草稿且要剪映/抖音工作流时优先；视频能力见「即梦 · 视频」。",
            "活动视觉需过品牌与广告法审核；积分与会员跨图/视频共用时注意配额。",
        ),
        rankings=[
            arena(11, 1231, "seedream-5.0-pro"),
            aa(8, 1229, "Seedream 5.0 Pro"),
        ],
        sources=["https://jimeng.jianying.com", ARENA, AA],
        updates=[
            {
                "date": "2026-02-01",
                "type": "release",
                "version": "Seedream 5.0 Pro",
                "summary": "即梦/Seed 图像旗舰档；Arena/AA 进入全球前十五",
                "source": "https://seed.bytedance.com/en/seedream5_0_pro",
            }
        ],
    )

    patch_existing(
        "google-imagen",
        currentVersion="Imagen 4 Ultra",
        oneLiner="Google Imagen 4 · Vertex 企业文生图",
        descriptionMd=desc(
            "Imagen 是 Google Cloud / Vertex 侧的企业文生图族（现 Imagen 4 Ultra/Standard/Fast），强调合同、安全过滤与 GCP 计费集成；Arena 上 Ultra 约第 27，AA 约第 28。消费级热度见同厂 Nano Banana。",
            "已在 GCP、需要企业级图像生成与统一计费时评估；创意消费入口优先 Nano Banana。",
            "国内访问受限；与 Gemini Nano Banana 产品线勿混淆。",
        ),
        pitfalls=["国内访问受限；与 Gemini Nano Banana 产品线勿混淆。"],
        rankings=[
            arena(27, 1148, "imagen-ultra-4.0"),
            aa(28, 1169, "Imagen 4 Ultra"),
        ],
        sources=[
            "https://deepmind.google/technologies/imagen/",
            ARENA,
            AA,
        ],
        updates=[
            {
                "date": "2025-06-01",
                "type": "release",
                "version": "Imagen 4",
                "summary": "Ultra/Standard/Fast 分档；Vertex 企业文生图主力",
                "source": "https://deepmind.google/technologies/imagen/",
            }
        ],
    )

    patch_existing(
        "hunyuan-image",
        currentVersion="混元生图 3.0",
        oneLiner="腾讯混元生图 3.0 · 国内云 · Arena 中上",
        descriptionMd=desc(
            "混元生图是腾讯混元多模态中的文生图能力，现以 3.0 为代表；Arena 文生图榜约第 26（1151 Elo），AA 开源变体亦在中段，可与混元视频及腾讯云业务同生态落地。",
            "腾讯云/微信生态应用需要国内文生图时评估；与即梦、通义万相、可图对照。",
            "艺术社区热度因场景而异；内容安全审核策略需适配产品。",
        ),
        rankings=[
            arena(26, 1151, "hunyuan-image-3.0"),
            aa(57, 1120, "HunyuanImage 3.0"),
        ],
        sources=["https://hunyuan.tencent.com", "https://hunyuan.tencent.com/image/en?tabIndex=0", ARENA, AA],
        updates=[
            {
                "date": "2025-09-01",
                "type": "release",
                "version": "混元生图 3.0",
                "summary": "写实与中文场景增强；Arena 进入全球前三十",
                "source": "https://hunyuan.tencent.com/image/en?tabIndex=0",
            }
        ],
    )

    patch_existing(
        "tongyi-wanxiang",
        currentVersion="Qwen-Image 2.0 Pro",
        oneLiner="通义万相 / Qwen-Image · 国内云文生图",
        descriptionMd=desc(
            "通义万相是阿里云通义系文生图产品；模型侧现与 Qwen-Image 2.0 Pro 等档对齐，Arena 约第 14、AA 约第 26，面向国内开发者与电商/营销素材。",
            "国内电商主图、活动视觉且已用阿里云时优先；与即梦、混元对照。",
            "API 字段与计费以阿里云文档为准；注意内容安全审核。",
        ),
        pitfalls=["API 字段与计费以阿里云文档为准；注意内容安全审核。"],
        rankings=[
            arena(14, 1193, "qwen-image-2.0-pro"),
            aa(26, 1171, "Qwen Image 2.0 Pro"),
        ],
        sources=["https://tongyi.aliyun.com/wanxiang/", ARENA, AA],
        updates=[
            {
                "date": "2026-04-22",
                "type": "release",
                "version": "Qwen-Image 2.0 Pro",
                "summary": "通义/Qwen 图像旗舰档；Arena 进入全球前十五",
                "source": "https://bailian.console.alibabacloud.com/",
            }
        ],
    )

    patch_existing(
        "midjourney",
        currentVersion="Midjourney V7+",
        oneLiner="审美/艺术向标杆 · 订阅制 · 盲测非 Arena 顶流",
        descriptionMd=desc(
            "Midjourney 仍以审美与艺术方向著称，品牌/营销视觉与社群工作流成熟（Discord/Web 订阅制）。在 Arena/AA 盲测总榜上已非头部（AA 可见 v7 Alpha 约第 90），选型应区分「好看」与「盲测偏好/文字渲染」。",
            "需要强风格艺术向、品牌视觉探索时仍常用；写实/文字/API 管线优先对照 GPT Image、Flux、Reve。",
            "商用授权与账号区域政策需核对；无官方开放 API。",
        ),
        pitfalls=["商用授权与账号区域政策需核对；无官方开放 API。"],
        rankings=[
            aa(90, 1064, "Midjourney v7 Alpha（AA 快照；非 Arena 顶流）"),
        ],
        sources=["https://www.midjourney.com", AA],
    )

    patch_existing(
        "stable-diffusion",
        currentVersion="SD 3.5 Large",
        oneLiner="开源可本地 · SD 3.5 · LoRA 生态",
        descriptionMd=desc(
            "Stable Diffusion 开源文生图/图生图家族，现常见 SD 3.5 Large 等档；Arena 上约第 73，AA 开源权重中段。优势在本地/私有化与 LoRA 生态，而非盲测总分。",
            "需要可控成本批量素材、或私有化不宜上传商业机密 prompt 时自托管。",
            "模型版权与生成内容合规需法务评估；硬件 GPU 成本不低。",
        ),
        rankings=[
            arena(73, 938, "stable-diffusion-v35-large"),
            aa(111, 1020, "Stable Diffusion 3.5 Large"),
        ],
        sources=["https://stability.ai/stable-diffusion", ARENA, AA],
    )

    patch_existing(
        "leonardo-ai",
        currentVersion="Lucid Origin",
        oneLiner="Leonardo · Lucid Origin · 游戏/创意资产",
        descriptionMd=desc(
            "Leonardo 提供 fine-tune、sprite 与创意资产管线；现以 Lucid Origin 等模型参与榜单，Arena 约第 66、AA Lucid Origin Ultra 约第 59，偏游戏与创意 asset 批量。",
            "需要 consistent character、game asset 或平台工作流时试用。",
            "免费额度有限；commercial license 需确认 plan。",
        ),
        pitfalls=["免费额度有限；commercial license 需确认 plan。"],
        rankings=[
            arena(66, 1013, "lucid-origin"),
            aa(59, 1118, "Lucid Origin Ultra"),
        ],
        sources=["https://leonardo.ai", ARENA, AA],
    )

    patch_existing(
        "kolors",
        currentVersion="Kolors 2.1",
        oneLiner="快手可图 · Kolors 2.1 · 开源/平台",
        descriptionMd=desc(
            "可图（Kolors）是快手系文生图模型，平台与开源权重并存；AA 上 Kolors 2.1 约第 55，常与可灵视频同生态出现在国内创意生产链路。",
            "国内需要文生图且可能与可灵视频串联、或希望自托管开源权重时评估。",
            "产品入口与品牌叙事可能随可灵平台整合变化；商用与开源许可分开核对。",
        ),
        rankings=[
            aa(55, 1125, "Kolors 2.1"),
        ],
        sources=["https://github.com/Kwai-Kolors/Kolors", AA],
    )

    # —— 边 ——
    write_edge("edge-reve-gpt-image-alt", "reve", "openai-gpt-image", note="Arena/AA 文生图榜相邻旗舰")
    write_edge("edge-nano-banana-gpt-image-alt", "google-nano-banana", "openai-gpt-image", note="消费级出图双热门")
    write_edge("edge-nano-banana-imagen-related", "google-nano-banana", "google-imagen", "commonly_used_with", 0.8, "同厂：Gemini 消费级 vs Vertex 企业线")
    write_edge("edge-mai-image-gpt-image-alt", "mai-image", "openai-gpt-image")
    write_edge("edge-muse-image-gpt-image-alt", "meta-muse-image", "openai-gpt-image")
    write_edge("edge-hidream-flux-os", "hidream", "flux-ai", "open_source_alternative_to", 0.75, "开源统一生成 vs BFL 开源/API 分档")
    write_edge("edge-krea-flux-alt", "krea", "flux-ai")
    write_edge("edge-luma-uni-flux-alt", "luma-uni", "flux-ai")
    write_edge("edge-reve-ideogram-alt", "reve", "ideogram", note="文字/排版向对照")
    write_edge("edge-jimeng-seedream-gpt-alt", "jimeng", "openai-gpt-image", note="国内 Seedream 对照海外旗舰")

    print("done")


if __name__ == "__main__":
    main()
