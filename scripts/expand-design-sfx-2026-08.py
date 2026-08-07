#!/usr/bin/env python3
"""新建 design-sfx 叶 + AI 时代音效基建短名单（2026-08-07）。

叶职责：UI / 影视 / 游戏 **音效（SFX）** 检索、直链下载、API、程序化合成、文本生音效。
与 design-ai-music（配乐）/ ai-speech（TTS·ASR）分离。

轴与条目：
- 免费可商用直链图库：Mixkit（自 design-stock 迁入并重写）
- 社区 + API：Freesound
- 大体量免费站（署名层）：ZapSplat
- 国内 CC/版权双轨：爱给网
- 文本生音效 SaaS：ElevenLabs Sound Effects
- 开源文本生音效：Meta AudioGen（AudioCraft）
- 程序化 UI/小品：jsfxr

用法:
  python3 scripts/expand-design-sfx-2026-08.py
  python3 scripts/expand-design-sfx-2026-08.py --overwrite
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ENTRIES_DIR = ROOT / "content" / "entries"
VENDORS_DIR = ROOT / "content" / "vendors"
EDGES_DIR = ROOT / "content" / "edges"
CATS_PATH = ROOT / "content" / "categories.json"
ICONS_PATH = ROOT / "packages" / "ui" / "src" / "icons.ts"
REVIEWED = "2026-08-07"
LEAF = "design-sfx"


def save(path: Path, data: dict | list) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def ensure_leaf() -> None:
    cats = load(CATS_PATH)
    if any(c.get("id") == LEAF for c in cats):
        print(f"leaf {LEAF} exists")
        return
    leaf = {
        "id": LEAF,
        "name": "音效 / SFX",
        "kind": "leaf",
        "parent": "design-assets",
        "order": 13,
        "usageMd": (
            "片子、产品 UI、Agent 演示要打击/环境/反馈音时。\n\n"
            "音效库（可直链/API）与文本生 SFX；配乐走 AI 音乐叶，人声走语音叶。\n\n"
            "先冻结许可与格式，进时间线前自托管 CDN；别热链第三方不稳定地址。"
        ),
    }
    idx = next((i for i, c in enumerate(cats) if c.get("id") == "design-fonts"), None)
    if idx is None:
        cats.append(leaf)
    else:
        cats.insert(idx + 1, leaf)
    save(CATS_PATH, cats)
    print(f"leaf {LEAF} inserted")


def ensure_icon() -> None:
    text = ICONS_PATH.read_text(encoding="utf-8")
    if f"'{LEAF}'" in text:
        print("icon mapping exists")
        return
    needle = "  'design-fonts': 'TextT',\n"
    if needle not in text:
        raise SystemExit("icons.ts: design-fonts anchor not found")
    ICONS_PATH.write_text(text.replace(needle, needle + f"  '{LEAF}': 'Waveform',\n"), encoding="utf-8")
    print("icon design-sfx → Waveform")


def entry(**kw) -> dict:
    e: dict = {
        "pricing": {"model": "free"},
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
        "category": LEAF,
        "subcategory": "sfx",
    }
    e.update(kw)
    if "officialUrl" in e and not e["sources"]:
        e["sources"] = [e["officialUrl"]]
    for k in ("vendorId", "githubUrl", "docsUrl", "pricingUrl"):
        if e.get(k) is None:
            e.pop(k, None)
    return e


def validate_entry(e: dict) -> None:
    assert 18 <= len(e["oneLiner"]) <= 80, (e["id"], len(e["oneLiner"]), e["oneLiner"])
    assert 120 <= len(e["descriptionMd"]) <= 400, (e["id"], len(e["descriptionMd"]))
    assert 1 <= len(e["pitfalls"]) <= 4, e["id"]
    assert 3 <= len(e["tags"]) <= 7, e["id"]


def edge(
    eid: str,
    frm: str,
    to: str,
    typ: str,
    weight: float = 0.75,
    confidence: str = "community",
    note: str | None = None,
) -> dict:
    d: dict = {
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
        d["note"] = note
    return d


VENDOR_DATA = [
    {
        "id": "freesound-project",
        "name": "Freesound",
        "region": "overseas",
        "url": "https://freesound.org",
    },
    {
        "id": "zapsplat-inc",
        "name": "ZapSplat",
        "region": "overseas",
        "url": "https://www.zapsplat.com",
    },
    {
        "id": "aigei-inc",
        "name": "爱给网",
        "region": "domestic",
        "url": "https://www.aigei.com",
    },
]

MIXKIT = entry(
    id="mixkit",
    name="Mixkit",
    vendorId="envato",
    oneLiner="免登录可商用 SFX/视频/配乐 · 统一站方许可",
    officialUrl="https://mixkit.co/free-sound-effects/",
    sources=[
        "https://mixkit.co/free-sound-effects/",
        "https://mixkit.co/license/",
        "https://mixkit.co/llm-info/",
    ],
    pricing={"model": "free", "notes": "Sound Effects Free License 等分品类；勿整站转售"},
    maturity="mature",
    tags=["sfx", "stock", "video", "music", "free", "cdn"],
    pitfalls=[
        "视频/音乐/音效分属不同 Mixkit License 文本，混用素材时要分别核对版本。",
        "禁止把素材文件再做成可下载的竞品库存库；嵌入最终作品是正道。",
        "库深不及专业 foley 站；高端定制仍走 Envato Elements 或生成式。",
    ],
    descriptionMd=(
        "Mixkit（Envato）提供 **免费音效、库存视频、配乐与模板**，音效页明确可商用、"
        "免署名可选、无需注册即可下载，适合剪辑流水线与产品内容快速配音效。"
        "素材托管在站方 CDN，许可相对统一，比「逐条 CC 社区库」更省法务心智。\n\n"
        "需要可直接下载的免登录 SFX、或与 Envato 订阅高级库成对选型时优先；"
        "Agent 管线若要可编程检索与相似音，再叠 Freesound API。\n\n"
        "生产建议下载后自托管，勿长期热链第三方 URL；许可以 mixkit.co/license 当期页为准。\n"
    ),
)

ENTRY_DATA = [
    entry(
        id="freesound",
        name="Freesound",
        vendorId="freesound-project",
        oneLiner="社区音效库 · APIv2 检索/预览 · 单条 CC 许可",
        officialUrl="https://freesound.org",
        docsUrl="https://freesound.org/docs/api/",
        sources=[
            "https://freesound.org",
            "https://freesound.org/docs/api/overview.html",
        ],
        pricing={"model": "free", "notes": "站点与 API 免费；单条多为 CC0/CC-BY/CC-BY-NC 等"},
        maturity="mature",
        tags=["sfx", "api", "open-data", "cc", "foley"],
        pitfalls=[
            "许可按**单条**文件而定（含 BY-NC），Agent 下载前必须读 license 字段，禁止假定整库可商用。",
            "原格式全量下载需 OAuth2；仅 token 常只能拿预览/受限质量链路。",
            "内容质量与标签噪声大，语义检索要做后过滤与人工试听。",
        ],
        descriptionMd=(
            "Freesound 是最大的社区贡献音效库之一，覆盖 foley、环境、实验音色，"
            "提供 **APIv2** 检索、相似音、分析特征与预览 URL，适合工具链与 AI Agent 程序化挑音。\n\n"
            "需要「可搜 + API + 开放许可样本」、或科研/内容分析与草稿 foley 时优先；"
            "与 Mixkit 等「站方统一免费许可」库对照：API 与长尾更强，授权一致性更弱。\n\n"
            "产品发布管线应只入库 CC0/明确允许商用条目；预览链勿当生产 CDN 长期热链。\n"
        ),
    ),
    entry(
        id="zapsplat",
        name="ZapSplat",
        vendorId="zapsplat-inc",
        oneLiner="大体量免费 SFX · 注册下载 · 免费层需署名",
        officialUrl="https://www.zapsplat.com",
        sources=["https://www.zapsplat.com", "https://www.zapsplat.com/license-type/standard-license/"],
        pricing={
            "model": "freemium",
            "notes": "Basic 免费 MP3+限速+署名；Gold 解锁 WAV/去署名",
            "currency": "GBP",
        },
        maturity="mature",
        tags=["sfx", "stock", "freemium", "foley"],
        pitfalls=[
            "免费 Basic：商用可做但须按协议署名，且 MP3/下载速率有限制。",
            "实物商品/发声玩具等可能需单独 merchandising 许可。",
            "非稳定直链开放平台；自动化爬取下载易踩 ToS。",
        ],
        descriptionMd=(
            "ZapSplat 提供大体量专业向音效（及部分配乐）在线库，每日更新。"
            "Standard License 下 Basic 账号可在影视/游戏/App/社媒等嵌入使用（含 monetize），"
            "条件包括署名与格式/速率限制；Gold 去掉署名并放 WAV。\n\n"
            "需要「比 Mixkit 更深的专业 foley 库」、可接受账号与署名层时评估；"
            "Agent 流水线更看 Freesound API 或统一许可图库。\n\n"
            "商用前读当期 Standard License；禁用「拆出 SFX 再当素材库转售」。\n"
        ),
    ),
    entry(
        id="aigei",
        name="爱给网",
        vendorId="aigei-inc",
        region="domestic",
        oneLiner="国内音效素材站 · CC 免费区 + 版权单购 · UI/游戏向",
        officialUrl="https://www.aigei.com/sound/",
        sources=["https://www.aigei.com/sound/", "https://www.aigei.com/sound/cc/"],
        pricing={
            "model": "freemium",
            "notes": "CC0/CC 可免费商用（按条目）；另售版权音效/配乐",
            "currency": "CNY",
        },
        maturity="stable",
        availability={
            "chinaAccessible": True,
            "needsCompany": False,
            "needsIcp": False,
            "regions": ["CN"],
        },
        tags=["sfx", "domestic", "cc", "stock", "ui"],
        pitfalls=[
            "站内免费与付费、CC 与「版权音效」并存，必须按条目协议下载，禁止整站默认可商用。",
            "部分素材镜像/转载来源杂，二次上架产品要留存授权截图与来源。",
            "无稳定、文档化的公开全球 API；不适合直接当生产直链源。",
        ],
        descriptionMd=(
            "爱给网是国内常用的音效/配乐/部分 3D 与视频素材站，UI 提示、游戏与短视频向类目齐全，"
            "并设 **CC 协议免费商用专区**；另有低价版权音效与配乐单购、以及 AI 配音等周边能力。\n\n"
            "国内团队要中文界面可检索 SFX、对接本地内容生产链路时评估；"
            "与 Mixkit/ZapSplat 构成国内外「下载型图库」对照轴。\n\n"
            "Agent 或批量入库应先筛 CC0/明确 BY 条目；企业项目关键成片优先版权单购路径。\n"
        ),
    ),
    entry(
        id="elevenlabs-sfx",
        name="ElevenLabs Sound Effects",
        vendorId="elevenlabs-inc",
        oneLiner="文本生音效 API · 按分钟 · 付费档方可商用",
        officialUrl="https://elevenlabs.io/sound-effects",
        docsUrl="https://elevenlabs.io/docs/api-reference/text-to-sound-effects/convert",
        pricingUrl="https://elevenlabs.io/pricing/api",
        sources=[
            "https://elevenlabs.io/sound-effects",
            "https://elevenlabs.io/docs/api-reference/text-to-sound-effects/convert",
        ],
        pricing={
            "model": "usage",
            "notes": "API 按生成分钟计费（约 $0.12/min 量级，以官价为准）；免费档商用受限",
            "currency": "USD",
        },
        maturity="stable",
        tags=["sfx", "ai", "text-to-audio", "api", "elevenlabs"],
        pitfalls=[
            "免费用户通常仅非商用；商用需付费订阅并遵守 ToS（禁止卖竞品服务等）。",
            "长场景/对白仍弱于专用配乐与 TTS——SFX 与音乐/语音要分轨选型。",
            "国内直连与支付可能受限；成本随生成秒数线性涨。",
        ],
        descriptionMd=(
            "ElevenLabs Sound Effects 提供 **text → SFX** 生成（API `/v1/sound-generation`），"
            "用自然语言描述谁什、材质与场景即可出环境/打击/过渡等片段，面向视频、游戏与 Agent 内容管线。"
            "与同厂 TTS/克隆分列计费与产品面，但账号体系统一。\n\n"
            "库存图库搜不到的「一次性定制音」、或流水线内按脚本动态配音效时优先；"
            "固定 UI 点击声与可复用 foley 仍常先查 Mixkit/Freesound。\n\n"
            "生成结果要本地固化版本与许可快照；勿把瞬时 URL 当永久热链。\n"
        ),
    ),
    entry(
        id="meta-audiogen",
        name="Meta AudioGen",
        vendorId="meta",
        oneLiner="开源文本生环境音 · AudioCraft · 可自托管",
        officialUrl="https://ai.meta.com/resources/models-and-libraries/audiocraft/",
        githubUrl="https://github.com/facebookresearch/audiocraft",
        docsUrl="https://facebookresearch.github.io/audiocraft/docs/AUDIOGEN.html",
        sources=[
            "https://github.com/facebookresearch/audiocraft",
            "https://facebookresearch.github.io/audiocraft/docs/AUDIOGEN.html",
            "https://ai.meta.com/blog/audiocraft-musicgen-audiogen-encodec-generative-ai-audio/",
        ],
        pricing={"model": "open-source", "notes": "代码 MIT 居多；权重/商用务必核 Hugging Face 模型卡与使用政策"},
        maturity="stable",
        tags=["sfx", "ai", "text-to-audio", "open-source", "self-host"],
        pitfalls=[
            "预训练权重常带研究/非商业限制，上线产品前必须读模型卡与责任政策，不可默认 OFL 级自由商用。",
            "需 GPU 推理；延迟与运维成本显著高于直链图库。",
            "环境音/场景描述强，与精修 UI 点击声、高制作 foley 库不是同一体验层。",
        ],
        descriptionMd=(
            "AudioGen 是 Meta AudioCraft 中的 **text-to-sound** 模型，面向环境音与效果音描述生成，"
            "与 MusicGen（配乐）分工。开源代码与训练/推理脚本便于研究与自托管实验，"
            "是「生成式 SFX 基建」开源参照系。\n\n"
            "需要本地生成、可再训练/可控采样、或作为 ElevenLabs 等 SaaS 的开源对照时评估；"
            "不急深度自建则优先托管 API。\n\n"
            "生产商用路径要单独做法务与安全评估；输出需听感 QC 与响度标准化。\n"
        ),
    ),
    entry(
        id="jsfxr",
        name="jsfxr",
        oneLiner="浏览器/库内 8-bit 合成 · Unlicense · 游戏 UI 反馈",
        officialUrl="https://sfxr.me",
        githubUrl="https://github.com/chr15m/jsfxr",
        sources=["https://sfxr.me", "https://github.com/chr15m/jsfxr"],
        pricing={"model": "open-source", "notes": "核心 Unlicense；sfxr.me Pro 另售打包功能"},
        maturity="mature",
        tags=["sfx", "procedural", "game", "ui", "open-source"],
        pitfalls=[
            "气质固定 8-bit/retro，品牌写实产品 UI 可能违和。",
            "Pro 云存档/zip 打包为增值；免费层已够导出 wav 做原型。",
        ],
        descriptionMd=(
            "jsfxr 是经典 sfxr 的 Web/JavaScript 移植：在浏览器里调合成器参数，"
            "或用 npm 库在游戏运行时生成 pickup/laser/click 等短音效，许可极宽松（Unlicense）。"
            "可即时出 wav，无需依赖外链 CDN。\n\n"
            "Game Jam、产品微交互占位音、离线可复现的程序化 SFX 时优先；"
            "电影感 foley 与自然语言描述音走图库或 ElevenLabs/AudioGen。\n\n"
            "上线前统一响度与采样率；避免每个环境现场随机合成导致音画不一致。\n"
        ),
    ),
]

EDGE_DATA = [
    edge(
        "e-mixkit-alt-freesound",
        "mixkit",
        "freesound",
        "alternative_to",
        0.75,
        note="统一许可下载站 vs 社区 API 库",
    ),
    edge("e-mixkit-alt-zapsplat", "mixkit", "zapsplat", "alternative_to", 0.7),
    edge(
        "e-aigei-dom-mixkit",
        "aigei",
        "mixkit",
        "domestic_equivalent_of",
        0.7,
        note="国内音效素材站 vs 国外统一免费许可图库",
    ),
    edge("e-aigei-alt-zapsplat", "aigei", "zapsplat", "alternative_to", 0.65),
    edge(
        "e-elevenlabs-sfx-alt-mixkit",
        "elevenlabs-sfx",
        "mixkit",
        "alternative_to",
        0.7,
        note="文本生成 vs 库存下载",
    ),
    edge(
        "e-elevenlabs-sfx-cuw-elevenlabs",
        "elevenlabs-sfx",
        "elevenlabs",
        "commonly_used_with",
        0.85,
        "verified",
        note="同账号语音 + 音效层",
    ),
    edge(
        "e-meta-audiogen-oss-elevenlabs-sfx",
        "meta-audiogen",
        "elevenlabs-sfx",
        "open_source_alternative_to",
        0.75,
    ),
    edge(
        "e-jsfxr-alt-mixkit",
        "jsfxr",
        "mixkit",
        "alternative_to",
        0.55,
        note="程序化 8-bit vs 实录/库音",
    ),
    edge(
        "e-freesound-cuw-kenney",
        "freesound",
        "kenney",
        "commonly_used_with",
        0.55,
        note="游戏原型：社区 foley + CC0 包",
    ),
    edge(
        "e-pixabay-cuw-mixkit",
        "pixabay",
        "mixkit",
        "commonly_used_with",
        0.6,
        note="同属免费多媒体；Pixabay 亦含音效/音乐",
    ),
    edge(
        "e-stable-audio-cuw-elevenlabs-sfx",
        "stable-audio",
        "elevenlabs-sfx",
        "commonly_used_with",
        0.5,
        note="生成式音频管线：配乐 + SFX 分轨",
    ),
]


def write_entries(overwrite: bool) -> None:
    validate_entry(MIXKIT)
    mp = ENTRIES_DIR / "mixkit.json"
    if mp.exists() and not overwrite:
        cur = load(mp)
        if cur.get("category") != LEAF or "SFX" not in cur.get("oneLiner", ""):
            save(mp, MIXKIT)
            print("rewrite+migrate mixkit → design-sfx")
        else:
            print("skip mixkit")
    else:
        save(mp, MIXKIT)
        print("write mixkit")

    for e in ENTRY_DATA:
        validate_entry(e)
        p = ENTRIES_DIR / f"{e['id']}.json"
        if p.exists() and not overwrite:
            print(f"skip entry {e['id']}")
            continue
        save(p, e)
        print(f"entry {e['id']} · ol={len(e['oneLiner'])} d={len(e['descriptionMd'])}")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--overwrite", action="store_true")
    args = ap.parse_args()

    ensure_leaf()
    ensure_icon()

    for v in VENDOR_DATA:
        p = VENDORS_DIR / f"{v['id']}.json"
        if p.exists() and not args.overwrite:
            print(f"skip vendor {v['id']}")
            continue
        save(p, v)
        print(f"vendor {v['id']}")

    write_entries(args.overwrite)

    for ed in EDGE_DATA:
        p = EDGES_DIR / f"{ed['id']}.json"
        if p.exists() and not args.overwrite:
            print(f"skip edge {ed['id']}")
            continue
        save(p, ed)
        print(f"edge {ed['id']}")


if __name__ == "__main__":
    main()
