#!/usr/bin/env python3
"""LLM 粒度重整：family（产品族）/ line（选型档位）；版本只写 currentVersion。"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "content"
ENTRIES = ROOT / "entries"
REVIEWED = "2026-07-23"


def load(p: Path):
    return json.loads(p.read_text(encoding="utf-8"))


def save(p: Path, data):
    p.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


# ---------- categories: replace llm-frontier ----------
cats = load(ROOT / "categories.json")
cats = [c for c in cats if c["id"] != "llm-frontier"]
cats.append(
    {
        "id": "llm-family",
        "name": "产品族 / 品牌",
        "kind": "leaf",
        "parent": "llm",
        "order": 1,
    }
)
cats.append(
    {
        "id": "llm-line",
        "name": "选型档位",
        "kind": "leaf",
        "parent": "llm",
        "order": 2,
    }
)
save(ROOT / "categories.json", cats)

# ---------- ranking: llm-frontier → llm-line ----------
ranks = load(ROOT / "ranking-systems.json")
for sys in ranks:
    sys["categories"] = [
        "llm-line" if c == "llm-frontier" else c for c in sys["categories"]
    ]
save(ROOT / "ranking-systems.json", ranks)


def entry(**kw):
    e = {
        "pricing": {"model": "usage"},
        "availability": {
            "chinaAccessible": True,
            "needsCompany": False,
            "needsIcp": False,
            "regions": ["global"],
        },
        "tags": ["llm"],
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
    return e


# ---------- families ----------
families = [
    entry(
        id="claude",
        name="Claude",
        category="llm-family",
        vendorId="anthropic",
        region="overseas",
        oneLiner="Anthropic 大模型产品族",
        descriptionMd=(
            "Claude 产品族下分 Opus / Sonnet / Haiku 等**选型档位**；"
            "具体版本（如 Opus 4.8）写在档位条目的 `currentVersion`，不单独与档位并列比较。"
        ),
        officialUrl="https://www.anthropic.com/claude",
        docsUrl="https://docs.anthropic.com",
        availability={
            "chinaAccessible": False,
            "needsCompany": False,
            "needsIcp": False,
            "regions": ["us", "eu"],
        },
        tags=["llm", "family", "anthropic"],
        maturity="mature",
        pitfalls=["中国大陆不可直接访问 API"],
    ),
    entry(
        id="gpt",
        name="GPT",
        category="llm-family",
        vendorId="openai",
        region="overseas",
        oneLiner="OpenAI GPT 产品族",
        descriptionMd="OpenAI 对话/多模态模型族；旗舰档与 mini 档为选型单元，具体版本见档位 `currentVersion`。",
        officialUrl="https://openai.com",
        availability={
            "chinaAccessible": False,
            "needsCompany": False,
            "needsIcp": False,
            "regions": ["global"],
        },
        tags=["llm", "family", "openai"],
        maturity="mature",
    ),
    entry(
        id="gemini",
        name="Gemini",
        category="llm-family",
        vendorId="google",
        region="overseas",
        oneLiner="Google DeepMind Gemini 产品族",
        descriptionMd="Gemini 下有 Pro / Flash 等档位；长上下文与多模态是族级能力叙事。",
        officialUrl="https://deepmind.google/technologies/gemini/",
        availability={
            "chinaAccessible": False,
            "needsCompany": False,
            "needsIcp": False,
            "regions": ["global"],
        },
        tags=["llm", "family", "google"],
    ),
    entry(
        id="kimi",
        name="Kimi",
        category="llm-family",
        vendorId="moonshot",
        region="domestic",
        oneLiner="月之暗面 Kimi 产品族",
        descriptionMd=(
            "Kimi 为月之暗面面向 C 端与 API 的产品族。"
            "**K3** 是旗舰档的当前版本，不是与「Claude Opus 档位」同级的独立品牌。"
        ),
        officialUrl="https://www.kimi.com",
        docsUrl="https://platform.kimi.com",
        tags=["llm", "family", "domestic", "moonshot"],
        maturity="stable",
    ),
]

# qwen / glm become families (rewrite in place)
qwen = load(ENTRIES / "qwen.json")
qwen.update(
    {
        "category": "llm-family",
        "subcategory": "family",
        "name": "通义千问",
        "oneLiner": "阿里云通义大模型产品族",
        "descriptionMd": (
            "通义千问是阿里云大模型**产品族**（含 Max / Plus / Turbo 等档位与开源权重线）。"
            "选型对比请用下属「选型档位」条目（如 Qwen-Max），勿与具体版本或他族档位混为一谈。"
        ),
        "rankings": [],  # 排行挂在 line
        "tags": ["llm", "family", "domestic", "aliyun"],
        "lastReviewed": REVIEWED,
        "pitfalls": ["产品线名称多易混淆——先选档位再看版本"],
    }
)
save(ENTRIES / "qwen.json", qwen)

glm = load(ENTRIES / "glm.json")
glm_rankings = glm.get("rankings", [])
glm.update(
    {
        "category": "llm-family",
        "subcategory": "family",
        "name": "智谱 GLM",
        "oneLiner": "智谱 AI 大模型产品族",
        "descriptionMd": (
            "智谱 GLM 为国产大模型**产品族**；具体旗舰档与版本见下属选型档位。"
        ),
        "rankings": [],
        "tags": ["llm", "family", "domestic", "code"],
        "lastReviewed": REVIEWED,
    }
)
save(ENTRIES / "glm.json", glm)

deepseek_family = entry(
    id="deepseek",
    name="DeepSeek",
    category="llm-family",
    vendorId="deepseek",
    region="domestic",
    oneLiner="深度求索大模型产品族",
    descriptionMd="DeepSeek 产品族；V3 / R1 等为版本或特化线，旗舰对话档见 DeepSeek 旗舰。",
    officialUrl="https://www.deepseek.com",
    tags=["llm", "family", "domestic", "value"],
)
for f in families + [deepseek_family]:
    save(ENTRIES / f"{f['id']}.json", f)

# ---------- lines (rewrite existing) ----------
# claude-opus stays line
opus = load(ENTRIES / "claude-opus.json")
opus["category"] = "llm-line"
opus["subcategory"] = "line"
opus["oneLiner"] = "Claude 旗舰档（Opus）"
opus["descriptionMd"] = (
    "Anthropic Claude 产品族中的**旗舰选型档位**。"
    f"当前版本：{opus.get('currentVersion', 'Opus')}（API 等细节见 updates）；"
    "与「Kimi 产品族」或「通义千问产品族」不是同一粒度——应与其他族的旗舰档对比。"
)
opus["lastReviewed"] = REVIEWED
save(ENTRIES / "claude-opus.json", opus)

# gpt-4o → GPT 旗舰档（保留 id 稳边）
gpt = load(ENTRIES / "gpt-4o.json")
gpt.update(
    {
        "category": "llm-line",
        "subcategory": "line",
        "name": "GPT 旗舰",
        "oneLiner": "OpenAI GPT 旗舰选型档",
        "descriptionMd": (
            "OpenAI GPT 产品族的旗舰档。历史以 GPT-4o 为代表；"
            "当前版本以 `currentVersion` / updates 为准（勿把版本名当成产品族）。"
        ),
        "currentVersion": gpt.get("currentVersion") or "GPT-4o",
        "lastReviewed": REVIEWED,
        "tags": ["llm", "line", "multimodal", "openai", "flagship"],
    }
)
save(ENTRIES / "gpt-4o.json", gpt)

# gemini-pro
gem = load(ENTRIES / "gemini-pro.json")
gem["category"] = "llm-line"
gem["subcategory"] = "line"
gem["oneLiner"] = "Gemini 旗舰/主力档（Pro）"
gem["descriptionMd"] = (
    "Google Gemini 产品族中的 Pro 选型档；具体版本见 currentVersion。"
    "与 Flash 等轻量档区分。"
)
gem["lastReviewed"] = REVIEWED
save(ENTRIES / "gemini-pro.json", gem)

# deepseek-v3 → 旗舰档叙事
ds = load(ENTRIES / "deepseek-v3.json")
ds.update(
    {
        "category": "llm-line",
        "subcategory": "line",
        "name": "DeepSeek 旗舰",
        "oneLiner": "DeepSeek 高性价比旗舰档",
        "descriptionMd": (
            "DeepSeek 产品族的旗舰对话/代码档。"
            "**V3** 为当前版本标签（见 currentVersion），不是与「通义千问产品族」同级的节点。"
        ),
        "currentVersion": "V3",
        "lastReviewed": REVIEWED,
        "tags": ["llm", "line", "domestic", "code", "value", "flagship"],
    }
)
save(ENTRIES / "deepseek-v3.json", ds)

# kimi-k3 → Kimi 旗舰档（保留 id）
kimi_line = load(ENTRIES / "kimi-k3.json")
kimi_line.update(
    {
        "category": "llm-line",
        "subcategory": "line",
        "name": "Kimi 旗舰",
        "oneLiner": "Kimi 产品族旗舰选型档",
        "descriptionMd": (
            "月之暗面 Kimi 产品族的**旗舰档**。"
            "当前版本为 **K3**（约 2.8T MoE、1M 上下文、原生多模态）；"
            "API model id `kimi-k3`。与 Claude Opus、Qwen-Max 同属「档位」粒度，"
            "不应与「通义千问」产品族条目直接同列对比。"
        ),
        "currentVersion": "K3",
        "lastReviewed": REVIEWED,
        "tags": [
            "llm",
            "line",
            "domestic",
            "open-weights",
            "moe",
            "long-context",
            "flagship",
        ],
    }
)
save(ENTRIES / "kimi-k3.json", kimi_line)

# new lines under qwen / glm
qwen_max = entry(
    id="qwen-max",
    name="Qwen-Max",
    category="llm-line",
    subcategory="line",
    vendorId="alibaba-cloud",
    region="domestic",
    oneLiner="通义千问旗舰选型档",
    descriptionMd=(
        "通义千问产品族的旗舰档（Max）。具体子版本/API 名以阿里云百炼控制台为准，"
        "写在 currentVersion / updates。"
    ),
    officialUrl="https://tongyi.aliyun.com",
    currentVersion="Max",
    pricing={"model": "usage", "currency": "CNY"},
    tags=["llm", "line", "domestic", "aliyun", "flagship"],
    pitfalls=["与 Plus/Turbo 档位能力与价格不同，勿混用"],
    rankings=[
        {
            "systemId": "lmarena-text",
            "tier": "CN flagship",
            "period": "2026-07",
            "note": "通义旗舰档；开源线另见 Qwen 开源权重",
            "asOf": REVIEWED,
        },
        {
            "systemId": "artificial-analysis-index",
            "tier": "Competitive",
            "period": "2026-07",
            "asOf": REVIEWED,
        },
    ],
)
# move old qwen rankings already cleared; use above
save(ENTRIES / "qwen-max.json", qwen_max)

glm_flag = entry(
    id="glm-flagship",
    name="GLM 旗舰",
    category="llm-line",
    subcategory="line",
    vendorId="zhipu-ai",
    region="domestic",
    oneLiner="智谱 GLM 旗舰选型档",
    descriptionMd="智谱 GLM 产品族旗舰档；版本见 currentVersion（如 GLM-4.x）。",
    officialUrl="https://bigmodel.cn",
    currentVersion="GLM-4",
    pricing={"model": "usage", "currency": "CNY"},
    tags=["llm", "line", "domestic", "code", "flagship"],
    pitfalls=["需实名认证"],
    rankings=glm_rankings
    or [
        {
            "systemId": "lmarena-text",
            "tier": "CN frontier",
            "period": "2026-07",
            "asOf": REVIEWED,
        }
    ],
)
save(ENTRIES / "glm-flagship.json", glm_flag)

# ---------- edges ----------
edges = load(ROOT / "edges" / "seed.json")
ids = {e["id"] for e in edges}


def add(eid, frm, to, typ, weight=0.85, confidence="verified", note=None):
    if eid in ids:
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
    edges.append(e)
    ids.add(eid)


def retarget(old: str, new: str):
    for e in edges:
        if e["from"] == old:
            e["from"] = new
        if e["to"] == old:
            e["to"] = new


# part_of: line → family
add("e-opus-part-claude", "claude-opus", "claude", "part_of", 1.0)
add("e-gpt4o-part-gpt", "gpt-4o", "gpt", "part_of", 1.0, note="旗舰档归属 GPT 族")
add("e-gempro-part-gemini", "gemini-pro", "gemini", "part_of", 1.0)
add("e-kimiline-part-kimi", "kimi-k3", "kimi", "part_of", 1.0, note="Kimi 旗舰档；版本 K3")
add("e-ds-part-deepseek", "deepseek-v3", "deepseek", "part_of", 1.0)
add("e-qwenmax-part-qwen", "qwen-max", "qwen", "part_of", 1.0)
add("e-glmflag-part-glm", "glm-flagship", "glm", "part_of", 1.0)

# retarget edges that used family-as-model
# glm domestic/alt → glm-flagship where comparing to lines
for e in edges:
    # kimi-k3-alt-glm pointed to glm family — point to glm-flagship
    if e["id"] == "e-kimi-k3-alt-glm":
        e["to"] = "glm-flagship"
    if e["id"] == "e-kimi-k3-alt-qwen":
        e["to"] = "qwen-max"
    # glm → claude domestic: was glm family to opus; use flagship
    if e["id"] == "e-glm-domestic-claude":
        e["from"] = "glm-flagship"
    # qwen → gemini domestic
    if e["id"] == "e-qwen-domestic-gemini":
        e["from"] = "qwen-max"
    # trae/siliconflow/one-api cuw with qwen → qwen-max
    if e["to"] == "qwen" and e["type"] == "commonly_used_with":
        e["to"] = "qwen-max"
    if e["from"] == "glm" and e["type"] == "commonly_used_with":
        e["from"] = "glm-flagship"

# line-level alternatives (flagship peers)
add("e-kimiline-alt-opus", "kimi-k3", "claude-opus", "alternative_to", 0.7, "community")
add("e-qwenmax-alt-opus", "qwen-max", "claude-opus", "alternative_to", 0.65, "community")
add("e-glmflag-alt-opus", "glm-flagship", "claude-opus", "alternative_to", 0.7, "community")
add("e-qwenmax-alt-kimiline", "qwen-max", "kimi-k3", "alternative_to", 0.75, "community")

# family-level soft alternatives (optional navigation)
add(
    "e-kimi-fam-alt-claude-fam",
    "kimi",
    "claude",
    "alternative_to",
    0.5,
    "community",
    "产品族级对照，细选看旗舰档",
)
add(
    "e-qwen-fam-alt-gpt-fam",
    "qwen",
    "gpt",
    "alternative_to",
    0.45,
    "community",
    "产品族级对照",
)

save(ROOT / "edges" / "seed.json", edges)

# recipes: qwen → qwen-max for llm layer
for rpath in (ROOT / "recipes").glob("*.json"):
    r = load(rpath)
    if r.get("layers", {}).get("llm") == "qwen":
        r["layers"]["llm"] = "qwen-max"
        save(rpath, r)
        print(f"recipe llm → qwen-max: {r['id']}")

print("LLM grain migration done")
