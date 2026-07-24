#!/usr/bin/env python3
"""非 Arena 权威榜回填：AA Intelligence / Coding Agent / Video / Speech、
OpenRouter 用量、SWE-bench Pro 等。

用法：python3 scripts/expand-non-arena-2026-07.py
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

AA = "https://artificialanalysis.ai/leaderboards/models"
AA_CODING = "https://artificialanalysis.ai/"
AA_VIDEO = "https://artificialanalysis.ai/video/leaderboard/text-to-video"
AA_SPEECH = "https://artificialanalysis.ai/text-to-speech/leaderboard/provider-voice"
AA_IMAGE = "https://artificialanalysis.ai/image/leaderboard/text-to-image"
OR = "https://openrouter.ai/rankings"
SWE = "https://www.swebench.com/"


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
    tier: str | None = None,
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
    if tier:
        r["tier"] = tier
    if score_label:
        r["scoreLabel"] = score_label
    elif score is not None:
        if system == "artificial-analysis-index":
            r["scoreLabel"] = f"AAII {score}"
        elif system == "aa-coding-agent":
            r["scoreLabel"] = f"AA Coding {score}"
        elif system in ("swe-bench-pro", "swe-bench-verified"):
            r["scoreLabel"] = f"{score}%"
        else:
            r["scoreLabel"] = f"{int(score) if float(score) == int(float(score)) else score} Elo"
    return r


def merge_rankings(eid: str, extra: list[dict], **fields) -> None:
    path = ENTRIES / f"{eid}.json"
    e = load(path)
    existing = {r["systemId"]: r for r in e.get("rankings", [])}
    for r in extra:
        existing[r["systemId"]] = r
    order = [
        "lmarena-text",
        "lmarena-agent",
        "lmarena-webdev",
        "lmarena-vision",
        "lmarena-document",
        "lmarena-search",
        "artificial-analysis-index",
        "aa-coding-agent",
        "openrouter-popularity",
        "swe-bench-pro",
        "lmarena-image",
        "lmarena-image-edit",
        "aa-image-arena",
        "lmarena-t2v",
        "lmarena-i2v",
        "lmarena-video-edit",
        "aa-video-arena",
        "aa-speech-arena",
        "swe-bench-verified",
        "jetbrains-ai-tools",
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
    for k, v in fields.items():
        e[k] = v
    srcs = list(
        dict.fromkeys(
            (e.get("sources") or [])
            + [r.get("sourceUrl") for r in extra if r.get("sourceUrl")]
        )
    )
    e["sources"] = [s for s in srcs if s]
    save(path, e)
    print(f"~ {eid}")


def ensure_vendor(vid: str, name: str, url: str, region: str = "overseas") -> None:
    path = VENDORS / f"{vid}.json"
    if path.exists():
        return
    save(path, {"id": vid, "name": name, "region": region, "url": url})
    print(f"+ vendor {vid}")


def write_entry(e: dict) -> None:
    assert len(e["oneLiner"]) <= 60, (e["id"], e["oneLiner"], len(e["oneLiner"]))
    assert len(e["descriptionMd"]) >= 120, e["id"]
    e.setdefault("updates", [])
    e["lastReviewed"] = REVIEWED
    path = ENTRIES / f"{e['id']}.json"
    exists = path.exists()
    save(path, e)
    print(f"{'~' if exists else '+'} entry {e['id']}")


def write_edge(eid: str, frm: str, to: str, typ: str, weight: float = 0.7, note: str | None = None) -> None:
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


def ensure_systems() -> None:
    systems = load(RANKING)
    by_id = {s["id"]: i for i, s in enumerate(systems)}

    def upsert(s: dict) -> None:
        if s["id"] in by_id:
            systems[by_id[s["id"]]].update(s)
            print(f"= ranking {s['id']}")
        else:
            systems.append(s)
            by_id[s["id"]] = len(systems) - 1
            print(f"+ ranking {s['id']}")

    # OpenRouter：挂到 llm-line 作为用量热度（非能力榜）
    if "openrouter-popularity" in by_id:
        s = systems[by_id["openrouter-popularity"]]
        cats = list(dict.fromkeys(s.get("categories", []) + ["llm-line"]))
        s["categories"] = cats
        s["description"] = (
            "统一网关上的真实请求份额与热度；反映路由层选用偏好，不等于能力上限。"
        )
        s["order"] = 8  # llm-line 上靠后，避免压过 Arena/AA
        print("= openrouter → llm-line")

    upsert(
        {
            "id": "aa-coding-agent",
            "name": "Artificial Analysis · Coding Agent Index",
            "shortName": "AA Coding",
            "categories": ["coding-cli-agent", "coding-ide-agent"],
            "metric": "score",
            "url": "https://artificialanalysis.ai/",
            "description": "编码 Agent 脚手架×模型组合的综合指数；对照 Codex / Claude Code 等真实工作流。",
            "authority": "Artificial Analysis",
            "updateCadence": "weekly",
            "order": 1,
        }
    )
    # swe-bench 改为 order 2，避免双主榜告警过重——仍保留
    if "swe-bench-verified" in by_id:
        systems[by_id["swe-bench-verified"]]["order"] = 2

    upsert(
        {
            "id": "aa-video-arena",
            "name": "Artificial Analysis · Text-to-Video Arena",
            "shortName": "AA Video",
            "categories": ["design-ai-video"],
            "metric": "mixed",
            "metricUnit": "Elo",
            "url": AA_VIDEO,
            "description": "文生视频盲测 Elo（含音画）；与 Arena T2V 交叉验证。",
            "authority": "Artificial Analysis",
            "updateCadence": "weekly",
            "order": 4,
        }
    )

    upsert(
        {
            "id": "swe-bench-pro",
            "name": "SWE-bench Pro",
            "shortName": "SWE-bench Pro",
            "categories": ["llm-line"],
            "metric": "score",
            "metricUnit": "%",
            "url": SWE,
            "description": "更难的软件工程 Agent 基准 % Resolved；模型档位编码能力交叉验证（非产品脚手架榜）。",
            "authority": "SWE-bench / community",
            "updateCadence": "ad-hoc",
            "order": 9,
        }
    )

    save(RANKING, systems)


def aa_index(rank: int, score: float, note: str) -> dict:
    return rk(
        "artificial-analysis-index",
        rank=rank,
        score=score,
        score_label=f"AAII {score}",
        note=note,
        url=AA,
    )


def main() -> None:
    ensure_systems()
    ensure_vendor("xiaomi", "小米", "https://www.mi.com/", "domestic")
    ensure_vendor("meta", "Meta", "https://meta.com/")

    # —— 扩种 ——
    write_entry(
        {
            "id": "meta-muse-spark",
            "name": "Muse Spark",
            "category": "llm-line",
            "subcategory": "line",
            "vendorId": "meta",
            "region": "overseas",
            "oneLiner": "Meta 旗舰 LLM · Spark 1.1 · AA Index 前列",
            "officialUrl": "https://ai.meta.com/",
            "currentVersion": "Muse Spark 1.1",
            "pricing": {"model": "usage", "currency": "USD"},
            "availability": {
                "chinaAccessible": False,
                "needsCompany": False,
                "needsIcp": False,
                "regions": ["global"],
            },
            "tags": ["llm", "line", "meta", "flagship"],
            "maturity": "stable",
            "pitfalls": [
                "国内不可用；产品入口与 API 渠道仍在滚动；与 Muse Image/Video 同厂不同模态",
            ],
            "updates": [
                {
                    "date": "2026-07-10",
                    "type": "release",
                    "version": "Muse Spark 1.1",
                    "summary": "Meta 旗舰文本模型；AA Intelligence Index 进入 50+ 前沿档",
                    "source": AA,
                }
            ],
            "rankings": [
                aa_index(14, 51, "Muse Spark 1.1 (xhigh)"),
                rk(
                    "lmarena-text",
                    rank=5,
                    score=1495,
                    note="muse-spark-1.1（Arena Text 快照）",
                    url="https://arena.ai/leaderboard/text",
                ),
            ],
            "sources": ["https://ai.meta.com/", AA],
            "descriptionMd": desc(
                "Muse Spark 是 Meta 的旗舰文本大模型线（现 1.1），2026-07 进入 Artificial Analysis Intelligence Index 50+ 前沿档，Arena Text 亦处前列；与 Muse Image/Video 同属 Meta AI 叙事。",
                "已在 Meta/Llama 生态需要闭源旗舰对话能力、或做六强前沿实验室对标时评估。",
                "国内不可用；API/产品入口变化快；勿与开源 Llama 线混为一谈。",
            ),
        }
    )

    write_entry(
        {
            "id": "wan-video",
            "name": "通义万相 · 视频",
            "category": "design-ai-video",
            "subcategory": "video-gen",
            "vendorId": "alibaba-cloud",
            "region": "domestic",
            "oneLiner": "阿里 Wan 2.7 · 文/图生视频 · AA Video 前三",
            "officialUrl": "https://tongyi.aliyun.com/",
            "currentVersion": "Wan 2.7",
            "pricing": {"model": "usage", "currency": "CNY"},
            "availability": {
                "chinaAccessible": True,
                "needsCompany": False,
                "needsIcp": False,
                "regions": ["CN", "global"],
            },
            "tags": ["ai", "video", "domestic", "wan"],
            "maturity": "stable",
            "pitfalls": [
                "与通义万相静帧/图像线分列选型；模型 id 与计费以百炼文档为准",
            ],
            "updates": [
                {
                    "date": "2026-06-01",
                    "type": "release",
                    "version": "Wan 2.7",
                    "summary": "文生视频旗舰档；AA Text-to-Video（含音）进入全球前三",
                    "source": AA_VIDEO,
                }
            ],
            "rankings": [
                rk(
                    "aa-video-arena",
                    rank=3,
                    score=1164,
                    score_label="1164 Elo",
                    note="Wan2.7-260612 · with audio",
                    url=AA_VIDEO,
                ),
                rk(
                    "lmarena-i2v",
                    rank=5,
                    score=1434,
                    note="wan2.7-i2v（Arena I2V）",
                    url="https://arena.ai/leaderboard/image-to-video",
                ),
            ],
            "sources": ["https://tongyi.aliyun.com/", AA_VIDEO],
            "descriptionMd": desc(
                "通义 Wan 是阿里云/通义系视频生成线（现 Wan 2.7），支持文生/图生视频；AA Text-to-Video（含音）约第 3，Arena Image-to-Video 亦处前列，是国内云栈高频选项。",
                "已用阿里云百炼、需要国内合规视频生成时评估；与即梦 Seedance、可灵、HappyHorse 对照。",
                "与万相静帧分列；模型 id 与计费以百炼为准；内容安全审核需适配。",
            ),
        }
    )

    write_entry(
        {
            "id": "mimo",
            "name": "MiMo",
            "category": "llm-line",
            "subcategory": "line",
            "vendorId": "xiaomi",
            "region": "domestic",
            "oneLiner": "小米 MiMo · V2.5 · OpenRouter 用量顶尖",
            "officialUrl": "https://github.com/XiaomiMiMo",
            "currentVersion": "MiMo-V2.5",
            "pricing": {"model": "usage", "currency": "CNY", "notes": "开源权重 + 托管 API 渠道"},
            "availability": {
                "chinaAccessible": True,
                "needsCompany": False,
                "needsIcp": False,
                "regions": ["CN", "global"],
            },
            "tags": ["llm", "line", "domestic", "open-weights"],
            "maturity": "stable",
            "pitfalls": [
                "官方企业 SLA 与文档成熟度仍在扩张；生产需锁定权重/托管商版本",
            ],
            "updates": [
                {
                    "date": "2026-06-01",
                    "type": "release",
                    "version": "MiMo-V2.5",
                    "summary": "开源/托管高用量线；OpenRouter 周用量常居前列",
                    "source": OR,
                }
            ],
            "rankings": [
                rk(
                    "openrouter-popularity",
                    rank=1,
                    tier="Top usage",
                    note="MiMo-V2.5 · OpenRouter 周用量常居前列（快照波动）",
                    url=OR,
                ),
                rk(
                    "artificial-analysis-index",
                    score=37,
                    score_label="AAII 37",
                    note="MiMo-V2.5；用量热度远高于智力指数位次",
                    url=AA,
                ),
            ],
            "sources": ["https://github.com/XiaomiMiMo", OR, AA],
            "descriptionMd": desc(
                "MiMo 是小米开源/托管大模型线（现 V2.5 / Pro），在 OpenRouter 等统一网关上以极高 token 用量著称，偏高性价比路由与 Agent 兜底。",
                "成本敏感、需要开源权重或网关热门国产线时评估；智力上限对照 Kimi/DeepSeek/Qwen 旗舰。",
                "企业 SLA 与文档仍在扩张；生产锁定版本；勿把用量榜当成能力榜。",
            ),
        }
    )

    # —— AA Intelligence Index ——
    merge_rankings(
        "claude-fable",
        [
            aa_index(1, 60, "Claude Fable 5 (with fallback)"),
            rk(
                "swe-bench-pro",
                rank=1,
                score=80.3,
                score_label="80.3%",
                note="SWE-bench Pro 公开报道前列",
                url=SWE,
            ),
        ],
    )
    merge_rankings(
        "gpt-4o",
        [
            aa_index(2, 59, "GPT-5.6 Sol (max)"),
            rk(
                "swe-bench-pro",
                score=64.6,
                score_label="64.6%",
                note="SWE-bench Pro（Sol 档公开报道）",
                url=SWE,
            ),
        ],
    )
    merge_rankings(
        "kimi-k3",
        [
            aa_index(3, 57, "Kimi K3"),
            rk(
                "openrouter-popularity",
                rank=11,
                tier="Rising usage",
                note="K3 上线后 OpenRouter 用量快速爬升",
                url=OR,
            ),
        ],
    )
    merge_rankings(
        "claude-opus",
        [
            aa_index(6, 56, "Claude Opus 4.8 (max)"),
            rk(
                "openrouter-popularity",
                rank=8,
                tier="High usage",
                note="Claude Opus 4.8 · OpenRouter 周用量前列",
                url=OR,
            ),
            rk(
                "swe-bench-pro",
                score=69.2,
                score_label="69.2%",
                note="SWE-bench Pro（Opus 4.8 公开报道）",
                url=SWE,
            ),
        ],
    )
    merge_rankings(
        "grok-flagship",
        [aa_index(8, 54, "Grok 4.5 (high)")],
    )
    merge_rankings(
        "claude-sonnet",
        [aa_index(10, 53, "Claude Sonnet 5 (max)")],
    )
    merge_rankings(
        "gpt-mini",
        [aa_index(12, 51, "GPT-5.6 Luna (max)")],
        oneLiner="OpenAI 成本档 · Luna · AA Index 51 前沿边缘",
    )
    merge_rankings(
        "glm-flagship",
        [
            aa_index(13, 51, "GLM-5.2 (max)"),
            rk(
                "openrouter-popularity",
                rank=4,
                tier="Top usage",
                note="GLM-5.2 · OpenRouter 周用量顶尖",
                url=OR,
            ),
        ],
    )
    merge_rankings(
        "gemini-flash",
        [aa_index(15, 50, "Gemini 3.6 Flash")],
    )
    merge_rankings(
        "gemini-pro",
        [aa_index(20, 46, "Gemini 3.1 Pro Preview")],
    )
    merge_rankings(
        "qwen-max",
        [aa_index(22, 46, "Qwen3.7 Max")],
        currentVersion="3.7-Max",
    )
    merge_rankings(
        "deepseek-v3",
        [
            aa_index(26, 44, "DeepSeek V4 Pro (max)"),
            rk(
                "openrouter-popularity",
                rank=2,
                tier="Top usage",
                note="V4 Flash/Pro 合计常居 OpenRouter 用量顶部",
                url=OR,
            ),
        ],
        oneLiner="国产性价比旗舰 · V4 · AA/OpenRouter 双强",
    )
    merge_rankings(
        "minimax-flagship",
        [
            aa_index(25, 44, "MiniMax-M3"),
            rk(
                "openrouter-popularity",
                rank=7,
                tier="High usage",
                note="MiniMax M3 · OpenRouter 高用量",
                url=OR,
            ),
        ],
    )
    merge_rankings(
        "hunyuan-pro",
        [
            rk(
                "openrouter-popularity",
                rank=3,
                tier="Top usage",
                note="Hy3 · OpenRouter 周用量顶尖（快照）",
                url=OR,
            ),
            rk(
                "artificial-analysis-index",
                score=41,
                score_label="AAII 41",
                note="Hy3",
                url=AA,
            ),
        ],
        oneLiner="腾讯混元旗舰 · Hy3 · OpenRouter 用量顶尖",
    )
    merge_rankings(
        "step-2",
        [
            rk(
                "openrouter-popularity",
                rank=6,
                tier="High usage",
                note="Step 3.7 Flash · OpenRouter 高用量",
                url=OR,
            ),
            rk(
                "artificial-analysis-index",
                score=30,
                score_label="AAII 30",
                note="Step 3.7 Flash",
                url=AA,
            ),
        ],
    )

    # —— AA Coding Agent ——
    merge_rankings(
        "openai-codex",
        [
            rk(
                "aa-coding-agent",
                rank=1,
                score=80,
                score_label="AA Coding 80",
                note="GPT-5.6 Sol (max) × Codex",
                url=AA_CODING,
            ),
            rk(
                "swe-bench-verified",
                tier="Top scaffold",
                note="与 Sol 旗舰组合在 AA Coding Agent Index 居首",
                url=SWE,
            ),
        ],
        oneLiner="OpenAI Codex · AA Coding Agent #1 · CLI/IDE",
        maturity="stable",
    )
    merge_rankings(
        "claude-code",
        [
            rk(
                "aa-coding-agent",
                rank=3,
                score=77,
                score_label="AA Coding 77",
                note="Claude Fable 5 × Claude Code",
                url=AA_CODING,
            ),
        ],
        oneLiner="Anthropic 终端 Agent · AA Coding 前列 · 仓库编排",
        currentVersion="Claude Code",
    )

    # —— AA Video ——
    merge_rankings(
        "gemini-omni-flash",
        [
            rk(
                "aa-video-arena",
                rank=1,
                score=1245,
                score_label="1245 Elo",
                note="with audio",
                url=AA_VIDEO,
            ),
        ],
    )
    merge_rankings(
        "dreamina",
        [
            rk(
                "aa-video-arena",
                rank=2,
                score=1227,
                score_label="1227 Elo",
                note="Seedance 2.0 720p · with audio",
                url=AA_VIDEO,
            ),
        ],
    )
    merge_rankings(
        "happyhorse",
        [
            rk(
                "aa-video-arena",
                rank=4,
                score=1149,
                score_label="1149 Elo",
                note="HappyHorse-1.1 · with audio",
                url=AA_VIDEO,
            ),
        ],
        currentVersion="HappyHorse 1.1",
    )
    merge_rankings(
        "kling",
        [
            rk(
                "aa-video-arena",
                rank=6,
                score=1111,
                score_label="1111 Elo",
                note="Kling 3.0 1080p Pro · with audio",
                url=AA_VIDEO,
            ),
        ],
        currentVersion="Kling 3.0",
        oneLiner="快手可灵 3.0 · 文/图生视频 · AA/Arena 前列",
    )
    merge_rankings(
        "google-veo",
        [
            rk(
                "aa-video-arena",
                rank=11,
                score=1095,
                score_label="1095 Elo",
                note="Veo 3.1 · with audio",
                url=AA_VIDEO,
            ),
        ],
    )
    merge_rankings(
        "vidu",
        [
            rk(
                "aa-video-arena",
                rank=15,
                score=1083,
                score_label="1083 Elo",
                note="Vidu Q3 Pro · with audio",
                url=AA_VIDEO,
            ),
        ],
        currentVersion="Vidu Q3 Pro",
    )
    merge_rankings(
        "pixverse",
        [
            rk(
                "aa-video-arena",
                rank=16,
                score=1073,
                score_label="1073 Elo",
                note="PixVerse V6 · with audio",
                url=AA_VIDEO,
            ),
        ],
        currentVersion="V6",
    )
    merge_rankings(
        "ltx-video",
        [
            rk(
                "aa-video-arena",
                rank=21,
                score=975,
                score_label="975 Elo",
                note="LTX-2.3 Fast · open weights · with audio",
                url=AA_VIDEO,
            ),
        ],
        currentVersion="LTX-2.3",
        oneLiner="Lightricks LTX-2.3 · 开源视频 · AA 开权重量前列",
    )

    # —— AA Speech ——
    merge_rankings(
        "qwen-audio-tts",
        [
            rk(
                "aa-speech-arena",
                rank=1,
                score=1234,
                score_label="1234 Elo",
                note="Qwen-Audio-3.0-TTS-Plus",
                url=AA_SPEECH,
            ),
        ],
        oneLiner="通义 Audio TTS · AA Speech #1 · 3.0 Plus",
    )
    merge_rankings(
        "cartesia",
        [
            rk(
                "aa-speech-arena",
                rank=4,
                score=1208,
                score_label="1208 Elo",
                note="Sonic 3.5",
                url=AA_SPEECH,
            ),
        ],
        currentVersion="Sonic 3.5",
        oneLiner="Cartesia Sonic 3.5 · 低延迟 TTS · AA Speech 前五",
    )
    merge_rankings(
        "minimax-speech",
        [
            rk(
                "aa-speech-arena",
                rank=10,
                score=1178,
                score_label="1178 Elo",
                note="Speech 2.8 HD",
                url=AA_SPEECH,
            ),
        ],
        currentVersion="Speech 2.8 HD",
        oneLiner="MiniMax Speech 2.8 · 中文音色 · AA Speech 前十",
    )
    merge_rankings(
        "elevenlabs",
        [
            rk(
                "aa-speech-arena",
                rank=11,
                score=1175,
                score_label="1175 Elo",
                note="Eleven v3",
                url=AA_SPEECH,
            ),
        ],
        currentVersion="Eleven v3",
        oneLiner="ElevenLabs v3 · 表达力 TTS · AA Speech 前十二",
    )
    merge_rankings(
        "fish-audio",
        [
            rk(
                "aa-speech-arena",
                rank=17,
                score=1138,
                score_label="1138 Elo",
                note="Fish Audio S2.1 Pro",
                url=AA_SPEECH,
            ),
        ],
        currentVersion="S2.1 Pro",
    )
    merge_rankings(
        "openai-tts",
        [
            rk(
                "aa-speech-arena",
                rank=27,
                score=1103,
                score_label="1103 Elo",
                note="TTS-1 HD",
                url=AA_SPEECH,
            ),
        ],
    )

    # —— 边 ——
    write_edge("e-muse-spark-part-meta", "meta-muse-spark", "meta-muse-image", "commonly_used_with", 0.6, "同厂文本 vs 图像")
    write_edge("e-muse-spark-alt-fable", "meta-muse-spark", "claude-fable", "alternative_to", 0.7)
    write_edge("e-wan-seedance-alt", "wan-video", "dreamina", "alternative_to", 0.85)
    write_edge("e-wan-wanxiang-related", "wan-video", "tongyi-wanxiang", "commonly_used_with", 0.8, "通义图/视频同栈")
    write_edge("e-mimo-alt-deepseek", "mimo", "deepseek-v3", "alternative_to", 0.75, "开源高用量对标")
    write_edge("e-codex-alt-claude-code", "openai-codex", "claude-code", "alternative_to", 0.9)

    print("done")


if __name__ == "__main__":
    main()
