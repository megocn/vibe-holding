#!/usr/bin/env python3
"""按 Arena.ai 全榜单回填/扩种（Text/Agent/WebDev/Vision/Document/Search/
Image/Image-Edit/T2V/I2V/Video-Edit 等）。

快照来源：https://arena.ai/leaderboard 概览（约 2026-07）。
用法：python3 scripts/expand-arena-all-2026-07.py
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


def save(path: Path, data) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def desc(what: str, when: str, caution: str) -> str:
    return f"{what}\n\n{when}\n\n{caution}\n"


def rk(
    system: str,
    *,
    rank: int | None = None,
    score: float | None = None,
    score_label: str | None = None,
    share: float | None = None,
    note: str,
    url: str,
) -> dict:
    r: dict = {
        "systemId": system,
        "period": PERIOD,
        "note": note,
        "sourceUrl": url,
        "asOf": ASOF,
    }
    if rank is not None:
        r["rank"] = rank
    if score is not None:
        r["score"] = score
    if share is not None:
        r["share"] = share
    if score_label:
        r["scoreLabel"] = score_label
    elif score is not None:
        r["scoreLabel"] = f"{int(score) if score == int(score) else score} Elo"
    return r


def ensure_ranking_systems() -> None:
    systems = load(RANKING)
    by_id = {s["id"]: s for s in systems}

    # fix text URL
    if "lmarena-text" in by_id:
        by_id["lmarena-text"]["url"] = "https://arena.ai/leaderboard/text"
        by_id["lmarena-text"]["description"] = (
            "众包盲测两两偏好 Elo；Text Arena Overall 是通用对话/推理的事实标准。"
        )

    extras = [
        {
            "id": "lmarena-agent",
            "name": "Arena AI Agent Leaderboard",
            "shortName": "Arena Agent",
            "categories": ["llm-line"],
            "metric": "mixed",
            "metricUnit": "%",
            "url": "https://arena.ai/leaderboard/agent",
            "description": "Agent 任务众包偏好胜率；长链路工具调用与异步任务选型参照。",
            "authority": "Arena AI（原 LMSYS）",
            "updateCadence": "weekly",
            "order": 3,
        },
        {
            "id": "lmarena-webdev",
            "name": "Arena AI WebDev Leaderboard",
            "shortName": "Arena WebDev",
            "categories": ["llm-line"],
            "metric": "mixed",
            "metricUnit": "Elo",
            "url": "https://arena.ai/leaderboard/code/webdev",
            "description": "Web 开发任务盲测 Elo；前端/全栈落地能力常用参照。",
            "authority": "Arena AI（原 LMSYS）",
            "updateCadence": "weekly",
            "order": 4,
        },
        {
            "id": "lmarena-vision",
            "name": "Arena AI Vision Leaderboard",
            "shortName": "Arena Vision",
            "categories": ["llm-line"],
            "metric": "mixed",
            "metricUnit": "Elo",
            "url": "https://arena.ai/leaderboard/vision",
            "description": "多模态视觉理解盲测 Elo；读图/图表/OCR 向选型参照。",
            "authority": "Arena AI（原 LMSYS）",
            "updateCadence": "weekly",
            "order": 5,
        },
        {
            "id": "lmarena-document",
            "name": "Arena AI Document Leaderboard",
            "shortName": "Arena Doc",
            "categories": ["llm-line"],
            "metric": "mixed",
            "metricUnit": "Elo",
            "url": "https://arena.ai/leaderboard/document",
            "description": "长文档理解与问答盲测 Elo。",
            "authority": "Arena AI（原 LMSYS）",
            "updateCadence": "weekly",
            "order": 6,
        },
        {
            "id": "lmarena-search",
            "name": "Arena AI Search Leaderboard",
            "shortName": "Arena Search",
            "categories": ["llm-line"],
            "metric": "mixed",
            "metricUnit": "Elo",
            "url": "https://arena.ai/leaderboard/search",
            "description": "带检索/联网的问答盲测 Elo；Search/Grounding 产品选型参照。",
            "authority": "Arena AI（原 LMSYS）",
            "updateCadence": "weekly",
            "order": 7,
        },
        {
            "id": "lmarena-image-edit",
            "name": "Arena AI Image Edit Leaderboard",
            "shortName": "Arena ImgEdit",
            "categories": ["design-ai-image"],
            "metric": "mixed",
            "metricUnit": "Elo",
            "url": "https://arena.ai/leaderboard/image-edit",
            "description": "单图编辑盲测 Elo；改图/局部编辑选型参照。",
            "authority": "Arena AI（原 LMSYS）",
            "updateCadence": "weekly",
            "order": 3,
        },
        {
            "id": "lmarena-t2v",
            "name": "Arena AI Text-to-Video Leaderboard",
            "shortName": "Arena T2V",
            "categories": ["design-ai-video"],
            "metric": "mixed",
            "metricUnit": "Elo",
            "url": "https://arena.ai/leaderboard/text-to-video",
            "description": "文生视频盲测 Elo；视频生成能力事实标准之一。",
            "authority": "Arena AI（原 LMSYS）",
            "updateCadence": "weekly",
            "order": 1,
        },
        {
            "id": "lmarena-i2v",
            "name": "Arena AI Image-to-Video Leaderboard",
            "shortName": "Arena I2V",
            "categories": ["design-ai-video"],
            "metric": "mixed",
            "metricUnit": "Elo",
            "url": "https://arena.ai/leaderboard/image-to-video",
            "description": "图生视频盲测 Elo。",
            "authority": "Arena AI（原 LMSYS）",
            "updateCadence": "weekly",
            "order": 2,
        },
        {
            "id": "lmarena-video-edit",
            "name": "Arena AI Video Edit Leaderboard",
            "shortName": "Arena VidEdit",
            "categories": ["design-ai-video"],
            "metric": "mixed",
            "metricUnit": "Elo",
            "url": "https://arena.ai/leaderboard/video-edit",
            "description": "视频编辑盲测 Elo。",
            "authority": "Arena AI（原 LMSYS）",
            "updateCadence": "weekly",
            "order": 3,
        },
    ]

    # bump product-hunt-design if still 2 and conflicting — leave as is
    added = 0
    for s in extras:
        if s["id"] not in by_id:
            # insert after lmarena-image / near other arena systems
            systems.append(s)
            added += 1
            print(f"+ ranking {s['id']}")
        else:
            # refresh metadata
            by_id[s["id"]].update({k: s[k] for k in s if k != "id"})
            print(f"= ranking {s['id']} refreshed")

    # rewrite from by_id + new appends already in systems list
    # Deduplicate by rebuilding
    seen = set()
    out = []
    for s in systems:
        if s["id"] in seen:
            continue
        seen.add(s["id"])
        # apply text url fix
        if s["id"] == "lmarena-text":
            s["url"] = "https://arena.ai/leaderboard/text"
        out.append(s)
    save(RANKING, out)
    print(f"ranking systems: {len(out)} (added {added})")


def ensure_vendor(vid: str, name: str, url: str, region: str = "overseas") -> None:
    path = VENDORS / f"{vid}.json"
    if path.exists():
        return
    save(path, {"id": vid, "name": name, "region": region, "url": url})
    print(f"+ vendor {vid}")


def write_entry(e: dict) -> None:
    assert len(e["oneLiner"]) <= 60, (e["id"], len(e["oneLiner"]), e["oneLiner"])
    assert len(e["descriptionMd"]) >= 120, e["id"]
    e.setdefault("updates", [])
    e["lastReviewed"] = REVIEWED
    path = ENTRIES / f"{e['id']}.json"
    exists = path.exists()
    save(path, e)
    print(f"{'~' if exists else '+'} entry {e['id']}")


def patch(eid: str, **updates) -> None:
    path = ENTRIES / f"{eid}.json"
    e = load(path)
    e.update(updates)
    e["lastReviewed"] = REVIEWED
    save(path, e)
    print(f"~ entry {eid}")


def write_edge(eid: str, frm: str, to: str, typ: str, weight: float = 0.7, note: str | None = None, confidence: str = "community") -> None:
    path = EDGES / f"{eid}.json"
    if path.exists():
        return
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
    save(path, e)
    print(f"+ edge {eid}")


U_TEXT = "https://arena.ai/leaderboard/text"
U_AGENT = "https://arena.ai/leaderboard/agent"
U_WEBDEV = "https://arena.ai/leaderboard/code/webdev"
U_VISION = "https://arena.ai/leaderboard/vision"
U_DOC = "https://arena.ai/leaderboard/document"
U_SEARCH = "https://arena.ai/leaderboard/search"
U_IMG = "https://arena.ai/leaderboard/text-to-image"
U_IMEDIT = "https://arena.ai/leaderboard/image-edit"
U_T2V = "https://arena.ai/leaderboard/text-to-video"
U_I2V = "https://arena.ai/leaderboard/image-to-video"
U_VEDIT = "https://arena.ai/leaderboard/video-edit"


def main() -> None:
    ensure_ranking_systems()
    ensure_vendor("alibaba-cloud", "阿里云", "https://www.aliyun.com/", "domestic")

    # —— 扩种：Claude Fable ——
    write_entry(
        {
            "id": "claude-fable",
            "name": "Claude Fable",
            "category": "llm-line",
            "subcategory": "line",
            "vendorId": "anthropic",
            "region": "overseas",
            "oneLiner": "Anthropic 顶档 · Fable 5 · Arena 多榜 #1",
            "officialUrl": "https://www.anthropic.com/claude/fable",
            "docsUrl": "https://platform.claude.com/docs/en/about-claude/models/overview",
            "currentVersion": "Fable 5",
            "pricing": {
                "model": "usage",
                "currency": "USD",
                "notes": "约 $10/M input · $50/M output；API `claude-fable-5`",
            },
            "availability": {
                "chinaAccessible": False,
                "needsCompany": False,
                "needsIcp": False,
                "regions": ["us", "eu", "global"],
            },
            "tags": ["llm", "reasoning", "code", "agentic", "flagship"],
            "maturity": "stable",
            "pitfalls": [
                "价高于 Opus；部分安全敏感域会降级到 Opus；国内不可直连",
                "曾因出口管制短暂下架，供应与政策风险需纳入采购",
            ],
            "updates": [
                {
                    "date": "2026-06-09",
                    "type": "release",
                    "version": "Fable 5",
                    "summary": "Anthropic 公开可用最强档；长链路 Agent/编码；API `claude-fable-5`",
                    "source": "https://www.anthropic.com/news/claude-fable-5-mythos-5",
                }
            ],
            "rankings": [
                rk("lmarena-text", rank=1, score=1507, note="claude-fable-5 · Text Overall", url=U_TEXT),
                rk("lmarena-agent", rank=1, share=12.72, score_label="12.72% win", note="Claude Fable 5 (High)", url=U_AGENT),
                rk("lmarena-vision", rank=1, score=1318, note="claude-fable-5", url=U_VISION),
                rk("lmarena-webdev", rank=2, score=1634, note="claude-fable-5", url=U_WEBDEV),
                rk("lmarena-document", rank=3, score=1505, note="claude-fable-5", url=U_DOC),
                rk("lmarena-search", rank=3, score=1237, note="claude-fable-5", url=U_SEARCH),
            ],
            "sources": [
                "https://www.anthropic.com/claude/fable",
                "https://www.anthropic.com/news/claude-fable-5-mythos-5",
                U_TEXT,
                U_AGENT,
                U_VISION,
            ],
            "descriptionMd": desc(
                "Claude Fable 是 Anthropic 公开可用的**最高能力选型档**（现 Fable 5），面向最长链路 Agent、复杂编码与知识工作；价位高于 Opus。Arena Text/Agent/Vision 等多榜居首。",
                "极难长任务、研究级 Agent 或需当前 Anthropic 最强公开模型时选用；常规企业编码默认仍可 Sonnet/Opus。",
                "价高；部分安全敏感域会路由到 Opus；国内不可直连；供应/政策波动需纳入采购。",
            ),
        }
    )

    # —— 扩种：Gemini Omni Flash（视频） ——
    write_entry(
        {
            "id": "gemini-omni-flash",
            "name": "Gemini Omni Flash",
            "category": "design-ai-video",
            "subcategory": "video-gen",
            "vendorId": "google",
            "region": "overseas",
            "oneLiner": "Google 视频 · Omni Flash · Arena T2V #1",
            "officialUrl": "https://gemini.google/",
            "currentVersion": "Omni Flash",
            "pricing": {"model": "freemium", "currency": "USD", "notes": "Gemini/Flow/API 配额"},
            "availability": {
                "chinaAccessible": False,
                "needsCompany": False,
                "needsIcp": False,
                "regions": ["global"],
            },
            "tags": ["ai", "video", "gemini", "audio-native"],
            "maturity": "stable",
            "pitfalls": [
                "与 Veo 企业线不同入口；国内不可用；配额与订阅档变化快",
            ],
            "updates": [
                {
                    "date": "2026-05-19",
                    "type": "release",
                    "version": "Omni Flash",
                    "summary": "Gemini 原生音画视频；Arena Text-to-Video 居首",
                    "source": "https://gemini.google/",
                }
            ],
            "rankings": [
                rk("lmarena-t2v", rank=1, score=1527, note="gemini-omni-flash", url=U_T2V),
                rk("lmarena-i2v", rank=2, score=1469, note="gemini-omni-flash", url=U_I2V),
                rk("lmarena-video-edit", rank=2, score=1347, note="gemini-omni-flash", url=U_VEDIT),
            ],
            "sources": ["https://gemini.google/", U_T2V, U_I2V, U_VEDIT],
            "descriptionMd": desc(
                "Gemini Omni Flash 是 Google 在 Gemini/Flow 侧的原生音画视频生成模型，Arena Text-to-Video 榜居首，图生视频与视频编辑亦处前列；与 Vertex Veo 企业线并行。",
                "消费级/创作者快速出片、或已在 Gemini 生态做 Nano Banana 静帧后延伸到视频时评估。",
                "与 Veo 不同入口；国内不可用；配额与订阅档变化快。",
            ),
        }
    )

    # —— 扩种：Meta Muse Video ——
    write_entry(
        {
            "id": "meta-muse-video",
            "name": "Muse Video",
            "category": "design-ai-video",
            "subcategory": "video-gen",
            "vendorId": "meta",
            "region": "overseas",
            "oneLiner": "Meta AI 视频 · Muse Video · Arena T2V 前三",
            "officialUrl": "https://ai.meta.com/blog/introducing-muse-image-muse-video-msl/",
            "currentVersion": "Muse Video",
            "pricing": {"model": "freemium", "currency": "USD"},
            "availability": {
                "chinaAccessible": False,
                "needsCompany": False,
                "needsIcp": False,
                "regions": ["global"],
            },
            "tags": ["ai", "video", "meta"],
            "maturity": "beta",
            "pitfalls": [
                "企业 API/商用条款与 Meta 消费入口变化快；国内不可用",
            ],
            "updates": [
                {
                    "date": "2026-07-07",
                    "type": "release",
                    "version": "Muse Video",
                    "summary": "与 Muse Image 同批；Arena Text-to-Video 进入前三",
                    "source": "https://ai.meta.com/blog/introducing-muse-image-muse-video-msl/",
                }
            ],
            "rankings": [
                rk("lmarena-t2v", rank=3, score=1459, note="muse-video", url=U_T2V),
            ],
            "sources": [
                "https://ai.meta.com/blog/introducing-muse-image-muse-video-msl/",
                U_T2V,
            ],
            "descriptionMd": desc(
                "Muse Video 是 Meta 2026-07 推出的 agentic 视频生成能力，经 Meta AI 等消费入口提供，与 Muse Image 同族；Arena Text-to-Video 约第 3。",
                "已在 Meta 生态做社交/创作者视频，或观察 agentic 视频工作流时纳入短名单。",
                "企业 API 与商用条款、产品入口变化快；国内不可用。",
            ),
        }
    )

    # —— 扩种：HappyHorse ——
    write_entry(
        {
            "id": "happyhorse",
            "name": "HappyHorse",
            "category": "design-ai-video",
            "subcategory": "video-gen",
            "vendorId": "alibaba-cloud",
            "region": "domestic",
            "oneLiner": "阿里 HappyHorse · 原生音画 · Arena 视频前列",
            "officialUrl": "https://www.aliyun.com/",
            "currentVersion": "HappyHorse 1.0",
            "pricing": {"model": "usage", "currency": "CNY", "notes": "公开 API/渠道仍在滚动开放"},
            "availability": {
                "chinaAccessible": True,
                "needsCompany": False,
                "needsIcp": False,
                "regions": ["CN", "global"],
            },
            "tags": ["ai", "video", "domestic", "audio-native"],
            "maturity": "beta",
            "pitfalls": [
                "公开 API/正式产品化进度需以阿里云公告为准；勿把榜单名次当成已可大规模采购",
            ],
            "updates": [
                {
                    "date": "2026-04-10",
                    "type": "release",
                    "version": "HappyHorse 1.0",
                    "summary": "原生音画视频；Arena T2V/I2V/Video Edit 前列",
                    "source": U_T2V,
                }
            ],
            "rankings": [
                rk("lmarena-t2v", rank=4, score=1430, note="happyhorse-1.0", url=U_T2V),
                rk("lmarena-i2v", rank=4, score=1444, note="happyhorse-1.0", url=U_I2V),
                rk("lmarena-video-edit", rank=3, score=1308, note="happyhorse-1.0", url=U_VEDIT),
            ],
            "sources": [U_T2V, U_I2V, U_VEDIT],
            "descriptionMd": desc(
                "HappyHorse 1.0 是阿里系（淘天未来生活实验室等叙事）原生音画视频模型，Arena Text-to-Video / Image-to-Video / Video Edit 均进入前列，强调音画同生与口型。",
                "关注国内/阿里云视频生成下一代能力、或做榜单对标 POC 时纳入；生产落地需等正式 API/套餐。",
                "公开渠道与企业采购进度变化快；勿仅凭榜单名次下单。",
            ),
        }
    )

    # —— LLM 回填 ——
    patch(
        "claude",
        oneLiner="Anthropic 族 · Fable/Opus/Sonnet/Haiku · Arena 多榜领先",
        descriptionMd=desc(
            "Claude 是 Anthropic 的大模型**产品族**。族下分 Fable（公开最强）、Opus / Sonnet / Haiku 等**选型档位**；具体版本写在对应档位条目上。",
            "选型时先定「用哪家」再定「哪一档」；Fable 用于极难长任务，Opus/Sonnet 覆盖多数企业编码与 Agent。",
            "Anthropic 系工具链协同好；采购与区域可用性是落地前提；国内不可直连 API。",
        ),
    )

    patch(
        "claude-opus",
        oneLiner="Anthropic 旗舰档 · Opus 4.8 · 企业 Agent 默认高档",
        descriptionMd=desc(
            "Anthropic Claude 产品族中的**旗舰企业选型档**（现 Opus 4.8）。复杂推理、长链路 Agent 与高质量编码协作；公开最强档见 Claude Fable。Arena Text 上 Opus 4.6/4.7 Thinking 仍处前三甲，Document/Search 亦强。",
            "企业复杂任务与编码 Agent 的默认高档；需当前 Anthropic 绝对顶档时升 Fable。",
            "价高；国内不可直连；长任务 token 消耗需留意。",
        ),
        rankings=[
            rk("lmarena-text", rank=2, score=1505, note="claude-opus-4-6-thinking（同族 Opus 最高可见档）", url=U_TEXT),
            rk("lmarena-agent", rank=3, share=9.75, score_label="9.75% win", note="Claude Opus 4.8 (Thinking)", url=U_AGENT),
            rk("lmarena-webdev", rank=5, score=1565, note="claude-opus-4-8-thinking", url=U_WEBDEV),
            rk("lmarena-vision", rank=2, score=1306, note="claude-opus-4-7-thinking", url=U_VISION),
            rk("lmarena-document", rank=1, score=1510, note="claude-opus-4-6", url=U_DOC),
            rk("lmarena-search", rank=1, score=1253, note="claude-opus-4-6-search", url=U_SEARCH),
            {
                "systemId": "artificial-analysis-index",
                "score": 61.4,
                "scoreLabel": "AAII 61.4",
                "period": PERIOD,
                "note": "Intelligence Index 前列",
                "sourceUrl": "https://artificialanalysis.ai/",
                "asOf": ASOF,
            },
        ],
        sources=[
            "https://www.anthropic.com/claude",
            "https://docs.anthropic.com",
            U_TEXT,
            U_AGENT,
            U_DOC,
        ],
    )

    patch(
        "claude-sonnet",
        rankings=[
            rk("lmarena-agent", rank=5, share=8.66, score_label="8.66% win", note="Claude Sonnet 5 (High)", url=U_AGENT),
            rk("lmarena-webdev", rank=9, score=1544, note="claude-sonnet-5-high", url=U_WEBDEV),
            rk("lmarena-document", rank=10, score=1471, note="claude-sonnet-5-high", url=U_DOC),
        ],
        sources=["https://www.anthropic.com/claude/sonnet", U_AGENT, U_WEBDEV],
    )

    patch(
        "gpt-4o",
        oneLiner="OpenAI 旗舰 · GPT-5.6 Sol · Arena Agent/WebDev 前列",
        rankings=[
            rk("lmarena-agent", rank=2, share=10.12, score_label="10.12% win", note="GPT 5.6 Sol (xHigh)", url=U_AGENT),
            rk("lmarena-webdev", rank=3, score=1630, note="gpt-5.6-sol-xhigh (codex-harness)", url=U_WEBDEV),
            rk("lmarena-vision", rank=9, score=1286, note="gpt-5.5", url=U_VISION),
            rk("lmarena-document", rank=6, score=1487, note="gpt-5.5-high", url=U_DOC),
            rk("lmarena-search", rank=2, score=1240, note="gpt-5.5-search", url=U_SEARCH),
            {
                "systemId": "lmarena-text",
                "tier": "Frontier",
                "period": PERIOD,
                "note": "Text Overall 名次随快照波动；Agent/WebDev 更稳居前列",
                "sourceUrl": U_TEXT,
                "asOf": ASOF,
            },
        ],
        sources=["https://openai.com/index/gpt-5-6/", U_AGENT, U_WEBDEV, U_SEARCH],
    )

    patch(
        "kimi-k3",
        oneLiner="月之暗面旗舰 · K3 · Arena WebDev #1",
        descriptionMd=desc(
            "月之暗面 Kimi 产品族的**旗舰选型档**。当前版本为 K3（约 2.8T MoE、百万级上下文、原生多模态等能力叙事，以官方为准）。Arena WebDev 居首，Agent/Text 亦处前列。",
            "与 Claude Fable/Opus、GPT Sol、Gemini Pro 同层对标；国内可达的开权重量级旗舰。",
            "旗舰调用需充值解锁；自托管门槛高；C 端高峰可能限流。",
        ),
        rankings=[
            rk("lmarena-webdev", rank=1, score=1678, note="kimi-k3", url=U_WEBDEV),
            rk("lmarena-agent", rank=4, share=9.71, score_label="9.71% win", note="Kimi K3", url=U_AGENT),
            rk("lmarena-text", rank=10, score=1486, note="kimi-k3", url=U_TEXT),
        ],
        sources=[
            "https://www.kimi.com/zh-cn/blog/kimi-k3",
            "https://platform.kimi.com/docs/guide/kimi-k3-quickstart",
            U_WEBDEV,
            U_AGENT,
            U_TEXT,
        ],
    )

    patch(
        "gemini-pro",
        rankings=[
            rk("lmarena-text", rank=8, score=1486, note="gemini-3.1-pro-preview", url=U_TEXT),
            rk("lmarena-vision", rank=7, score=1289, note="gemini-3-pro", url=U_VISION),
            rk("lmarena-search", rank=7, score=1212, note="gemini-3.1-pro-grounding", url=U_SEARCH),
        ],
        sources=[
            "https://ai.google.dev/gemini-api/docs/models",
            U_TEXT,
            U_VISION,
            U_SEARCH,
        ],
    )

    patch(
        "glm-flagship",
        rankings=[
            rk("lmarena-webdev", rank=4, score=1592, note="glm-5.2 (max)", url=U_WEBDEV),
            rk("lmarena-agent", rank=10, share=6.5, score_label="6.50% win", note="GLM 5.2 (Max)", url=U_AGENT),
            {
                "systemId": "lmarena-text",
                "tier": "CN frontier",
                "period": PERIOD,
                "note": "国产闭源旗舰；WebDev/Agent 榜更靠前",
                "sourceUrl": U_TEXT,
                "asOf": ASOF,
            },
        ],
        sources=["https://open.bigmodel.cn", U_WEBDEV, U_AGENT],
    )

    patch(
        "grok-flagship",
        rankings=[
            rk("lmarena-webdev", rank=7, score=1557, note="grok-4.5", url=U_WEBDEV),
        ],
        sources=["https://x.ai/news/grok-4-5", U_WEBDEV],
    )

    # —— 图像：补 Image Edit ——
    def merge_rankings(eid: str, extra: list[dict]) -> None:
        e = load(ENTRIES / f"{eid}.json")
        existing = {r["systemId"]: r for r in e.get("rankings", [])}
        for r in extra:
            existing[r["systemId"]] = r
        # keep stable order: prefer known systems order
        order = [
            "lmarena-image",
            "lmarena-image-edit",
            "aa-image-arena",
            "lmarena-t2v",
            "lmarena-i2v",
            "lmarena-video-edit",
            "lmarena-text",
            "lmarena-agent",
            "lmarena-webdev",
            "lmarena-vision",
            "lmarena-document",
            "lmarena-search",
            "artificial-analysis-index",
        ]
        merged = []
        seen = set()
        for sid in order:
            if sid in existing:
                merged.append(existing[sid])
                seen.add(sid)
        for sid, r in existing.items():
            if sid not in seen:
                merged.append(r)
        e["rankings"] = merged
        e["lastReviewed"] = REVIEWED
        srcs = list(dict.fromkeys((e.get("sources") or []) + [r.get("sourceUrl") for r in extra if r.get("sourceUrl")]))
        e["sources"] = [s for s in srcs if s]
        save(ENTRIES / f"{eid}.json", e)
        print(f"~ rankings {eid}")

    merge_rankings(
        "openai-gpt-image",
        [rk("lmarena-image-edit", rank=1, score=1465, note="gpt-image-2 (medium) · Single-Image Edit", url=U_IMEDIT)],
    )
    merge_rankings(
        "meta-muse-image",
        [rk("lmarena-image-edit", rank=2, score=1402, note="muse-image", url=U_IMEDIT)],
    )
    merge_rankings(
        "mai-image",
        [rk("lmarena-image-edit", rank=3, score=1401, note="mai-image-2.5", url=U_IMEDIT)],
    )
    merge_rankings(
        "jimeng",
        [rk("lmarena-image-edit", rank=4, score=1393, note="seedream-5.0-pro", url=U_IMEDIT)],
    )
    merge_rankings(
        "grok-imagine",
        [rk("lmarena-image-edit", rank=6, score=1389, note="grok-imagine-image-quality", url=U_IMEDIT)],
    )
    merge_rankings(
        "google-nano-banana",
        [
            rk("lmarena-image-edit", rank=7, score=1388, note="nano-banana-pro 2k", url=U_IMEDIT),
        ],
    )
    merge_rankings(
        "reve",
        [rk("lmarena-image-edit", rank=10, score=1383, note="reve-2.1", url=U_IMEDIT)],
    )

    # —— 视频回填 ——
    patch(
        "dreamina",
        currentVersion="Seedance 2.0",
        oneLiner="即梦视频 · Seedance 2.0 · Arena I2V/Edit #1",
        descriptionMd=desc(
            "即梦（海外 Dreamina）平台的**视频生成**能力，现以 Seedance 2.0 为代表。Arena Image-to-Video 与 Video Edit 居首，Text-to-Video 约第 2，是当前全球最热国内可达视频生成之一。",
            "已在即梦做图、需要同账号延伸到短视频/动态素材时优先；与 Omni Flash、Veo、Kling、Sora 同叶对比。",
            "商用与水印随套餐变；出海与海外 Dreamina 站点政策可能不同。",
        ),
        rankings=[
            rk("lmarena-t2v", rank=2, score=1482, note="dreamina-seedance-2.0-720p", url=U_T2V),
            rk("lmarena-i2v", rank=1, score=1474, note="dreamina-seedance-2.0-720p", url=U_I2V),
            rk("lmarena-video-edit", rank=1, score=1377, note="dreamina-seedance-2.0-720p", url=U_VEDIT),
        ],
        sources=["https://jimeng.jianying.com", U_T2V, U_I2V, U_VEDIT],
        updates=[
            {
                "date": "2026-01-01",
                "type": "release",
                "version": "Seedance 2.0",
                "summary": "即梦/Dreamina 视频旗舰；Arena I2V 与 Video Edit 居首",
                "source": U_I2V,
            }
        ],
    )

    patch(
        "google-veo",
        currentVersion="Veo 3.1",
        oneLiner="DeepMind Veo 3.1 · 原生音频 · Arena T2V 前十",
        rankings=[
            rk("lmarena-t2v", rank=6, score=1364, note="veo-3.1-audio-1080p", url=U_T2V),
            rk("lmarena-i2v", rank=7, score=1398, note="veo-3.1-audio", url=U_I2V),
        ],
        sources=["https://deepmind.google/models/veo/", U_T2V, U_I2V],
    )

    patch(
        "openai-sora",
        currentVersion="Sora 2 Pro",
        maturity="stable",
        oneLiner="OpenAI Sora 2 Pro · 高保真叙事 · Arena T2V #5",
        descriptionMd=desc(
            "Sora 是 OpenAI 的文生视频产品线（现 Sora 2 / Pro），强调高保真运动与叙事连贯；Arena Text-to-Video 约第 5（sora-2-pro）。",
            "已在 OpenAI 生态、需要旗舰级演示片时关注；批量生产仍常对照 Seedance / Omni Flash / Kling。",
            "可用性与区域政策变化快；成本高。",
        ),
        rankings=[
            rk("lmarena-t2v", rank=5, score=1366, note="sora-2-pro", url=U_T2V),
        ],
        sources=["https://openai.com/sora", U_T2V],
    )

    patch(
        "kling",
        currentVersion="Kling O3 / 2.x",
        oneLiner="快手可灵 · 文/图生视频 · Arena 视频中上",
        rankings=[
            rk("lmarena-t2v", rank=22, score=1219, note="kling-2.5-turbo-1080p（快照中上段）", url=U_T2V),
            rk("lmarena-video-edit", rank=5, score=1251, note="kling-o3-pro", url=U_VEDIT),
        ],
        sources=["https://klingai.com", U_T2V, U_VEDIT],
    )

    patch(
        "runway",
        currentVersion="Gen-4 Aleph",
        oneLiner="Runway Gen-4 · 影视 previs · Arena 视频编辑前列",
        rankings=[
            rk("lmarena-video-edit", rank=7, score=1194, note="runway-gen4-aleph", url=U_VEDIT),
        ],
        sources=["https://runwayml.com", U_VEDIT],
    )

    # grok imagine video — attach to grok-imagine entry as multimodal note + video rankings if category is image only
    # Better: patch grok-imagine description and add video rankings (systems allow design-ai-video only for t2v - can't put on image entry)
    # Add video ranks onto a note via new edge to video capability - or expand grok-imagine category? Keep separate by patching description only and creating thin video alias?
    # Simplest: add rankings to grok-imagine won't validate if system categories don't include design-ai-image.
    # So create no video ranking on image entry. Add note in description.
    gi = load(ENTRIES / "grok-imagine.json")
    gi["descriptionMd"] = desc(
        "Grok Imagine 是 xAI 的图像（及短视频）生成能力；静帧 `grok-imagine-image-quality` 在 Arena 文生图约第 12、改图约第 6；视频档 `grok-imagine-video` 在 T2V/I2V/Video Edit 亦处前列。",
        "已在 xAI/Grok 生态需要快速出图或短视频时选用；严肃品牌管线仍对照 GPT Image / Seedance / Omni Flash。",
        "区域与 API 成熟度变化快；企业合规与商用条款需核对。",
    )
    gi["oneLiner"] = "xAI 图/短视频 · Imagine · Arena 图改/视频前列"
    assert len(gi["oneLiner"]) <= 60
    gi["lastReviewed"] = REVIEWED
    save(ENTRIES / "grok-imagine.json", gi)
    print("~ entry grok-imagine (video note)")

    # —— 边 ——
    write_edge("e-fable-part-claude", "claude-fable", "claude", "part_of", 1.0, confidence="verified")
    write_edge("e-fable-alt-opus", "claude-fable", "claude-opus", "alternative_to", 0.9, "同族更高档 vs 企业默认旗舰")
    write_edge("e-fable-alt-gpt-sol", "claude-fable", "gpt-4o", "alternative_to", 0.85)
    write_edge("e-omni-flash-veo-related", "gemini-omni-flash", "google-veo", "commonly_used_with", 0.8, "同厂：Gemini 消费/创作者 vs Veo 企业线")
    write_edge("e-omni-flash-seedance-alt", "gemini-omni-flash", "dreamina", "alternative_to", 0.85)
    write_edge("e-muse-video-omni-alt", "meta-muse-video", "gemini-omni-flash", "alternative_to")
    write_edge("e-muse-video-image-related", "meta-muse-video", "meta-muse-image", "commonly_used_with", 0.9, "同批 Muse 图/视频")
    write_edge("e-happyhorse-seedance-alt", "happyhorse", "dreamina", "alternative_to", 0.8)
    write_edge("e-sora-omni-alt", "openai-sora", "gemini-omni-flash", "alternative_to")

    print("done")


if __name__ == "__main__":
    main()
