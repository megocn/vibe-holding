#!/usr/bin/env python3
"""将 A–V 升为 section，按可比较单元拆 leaf；迁移条目与排行；补 Kimi K3 / Phosphor。"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "content"
ENTRIES = ROOT / "entries"
REVIEWED = "2026-07-23"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def save(path: Path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


# section_id -> list of (leaf_id, name, order, subcategory_keys | None)
# None subcategory_keys = default catch-all leaf for that section
LEAVES: dict[str, list[tuple[str, str, int, list[str] | None]]] = {
    "coding-agent": [
        ("coding-ide-agent", "IDE / 本机 Agent", 1, ["ide-agent", "ide", "extension"]),
        ("coding-cloud-builder", "云端 App Builder", 2, ["cloud-builder"]),
        ("coding-cli-agent", "终端 Agent", 3, ["cli"]),
    ],
    "llm": [
        ("llm-frontier", "通用旗舰模型", 1, None),
    ],
    "model-gateway": [
        ("gateway-router", "云端网关 / 路由", 1, None),
        ("gateway-local", "本地推理", 2, ["local"]),
    ],
    "language-runtime": [
        ("lang-language", "编程语言", 1, ["language"]),
        ("lang-runtime", "运行时", 2, ["runtime"]),
    ],
    "framework": [
        ("fw-fullstack", "全栈 / 元框架", 1, ["fullstack"]),
        ("fw-ui-lib", "UI 框架核心", 2, None),
    ],
    "ui-library": [
        ("ui-kits", "完整组件库", 1, None),  # default for antd/mantine/daisy
        ("ui-composable", "可组合 / 拷贝式", 2, ["composable"]),
        ("ui-primitives", "无样式原语", 3, ["primitives", "headless"]),
        ("ui-icons", "图标库", 4, ["icons"]),
    ],
    "cloud-deploy": [
        ("cloud-paas", "PaaS / 边缘托管", 1, None),
    ],
    "database-storage": [
        ("db-relational", "关系型 / Serverless SQL", 1, None),
        ("db-nosql", "文档 / NoSQL", 2, ["nosql"]),
        ("db-cache", "缓存 / KV", 3, ["cache", "serverless-data"]),
        ("db-object", "对象存储", 4, ["object-storage"]),
        ("db-sqlite-edge", "边缘 SQLite", 5, ["sqlite"]),
    ],
    "baas-auth": [
        ("baas-platform", "BaaS 平台", 1, None),
        ("baas-auth-only", "纯鉴权", 2, ["auth"]),
    ],
    "ai-infra": [
        ("ai-agent-fw", "Agent 编排框架", 1, ["agent-framework", "sdk"]),
        ("ai-rag", "RAG / 文档索引", 2, ["rag", "low-code"]),
        ("ai-vector", "向量库", 3, ["vector"]),
        ("ai-llm-obs", "LLM 可观测", 4, ["observability"]),
    ],
    "payment": [
        ("pay-processor", "支付处理商", 1, None),
        ("pay-mor", "Merchant of Record", 2, ["mor"]),
    ],
    "app-distribution": [
        ("dist-ios", "Apple 生态", 1, ["ios"]),
        ("dist-android", "Android 商店", 2, ["android"]),
        ("dist-extension", "浏览器扩展", 3, ["extension"]),
        ("dist-desktop", "桌面 / 直接分发", 4, ["desktop"]),
    ],
    "oss-ecosystem": [
        ("oss-toolchain", "构建与工具链", 1, None),
    ],
    "observability": [
        ("obs-errors", "错误与 APM", 1, ["errors", "apm"]),
        ("obs-product", "产品分析（观测向）", 2, ["product-analytics"]),
        ("obs-platform", "可观测平台 / 标准", 3, ["standards", "dashboards", "logs"]),
    ],
    "cicd-devops": [
        ("cicd-pipeline", "CI/CD 与容器", 1, None),
    ],
    "messaging": [
        ("msg-email", "邮件", 1, ["email"]),
        ("msg-sms", "短信 / 语音", 2, ["sms"]),
        ("msg-push", "推送", 3, ["push"]),
        ("msg-im", "IM / 机器人", 4, ["im"]),
    ],
    "analytics-growth": [
        ("growth-web", "网站分析", 1, ["web-analytics"]),
    ],
    "domain-dns-cdn": [
        ("net-cdn-dns", "CDN / DNS / 边缘", 1, ["cdn-dns", "cdn", "dns"]),
        ("net-domain", "域名注册", 2, ["domain"]),
    ],
    "security-compliance": [
        ("sec-secrets", "Secrets / 密钥管理", 1, ["secrets", "password-manager"]),
    ],
    "design-assets": [
        ("design-tools", "设计工具", 1, ["design"]),
        ("design-ai-image", "AI 图像生成", 2, ["ai-image"]),
        ("design-motion", "动效素材", 3, ["motion"]),
    ],
    "collaboration": [
        ("collab-pm", "项目管理", 1, ["pm"]),
        ("collab-docs", "文档 / Wiki", 2, ["docs"]),
        ("collab-suite", "协作套件", 3, ["suite"]),
    ],
    "globalization": [
        ("global-fx", "跨境收款 / 换汇", 1, ["fx", "collection"]),
        ("global-entity", "主体 / 公司路径", 2, ["entity"]),
        ("global-i18n", "国际化库", 3, ["i18n"]),
    ],
}

# entry id overrides when subcategory mapping is ambiguous
ENTRY_LEAF: dict[str, str] = {
    "shadcn-ui": "ui-composable",
    "radix-ui": "ui-primitives",
    "antd": "ui-kits",
    "mantine": "ui-kits",
    "daisyui": "ui-kits",
    "lucide": "ui-icons",  # move from design-assets → F/ui-icons
    "react": "fw-ui-lib",
    "vue": "fw-ui-lib",
    "nextjs": "fw-fullstack",
    "nuxt": "fw-fullstack",
    "remix": "fw-fullstack",
    "sveltekit": "fw-fullstack",
    "tanstack-start": "fw-fullstack",
    "postgresql": "db-relational",
    "neon": "db-relational",
    "planetscale": "db-relational",
    "mongodb-atlas": "db-nosql",
    "redis": "db-cache",
    "upstash": "db-cache",
    "cloudflare-r2": "db-object",
    "turso": "db-sqlite-edge",
    "supabase": "baas-platform",
    "firebase": "baas-platform",
    "appwrite": "baas-platform",
    "clerk": "baas-auth-only",
    "auth0": "baas-auth-only",
    "better-auth": "baas-auth-only",
    "stripe": "pay-processor",
    "alipay": "pay-processor",
    "wechat-pay": "pay-processor",
    "paddle": "pay-mor",
    "lemonsqueezy": "pay-mor",
    "creem": "pay-mor",
    "polar": "pay-mor",
    "vercel-ai-sdk": "ai-agent-fw",
    "mastra": "ai-agent-fw",
    "langgraph": "ai-agent-fw",
    "dify": "ai-rag",
    "llamaindex": "ai-rag",
    "openrouter": "gateway-router",
    "litellm": "gateway-router",
    "one-api": "gateway-router",
    "azure-openai": "gateway-router",
    "siliconflow": "gateway-router",
    "posthog": "obs-product",
    "sentry": "obs-errors",
}


def resolve_leaf(section: str, entry_id: str, subcategory: str | None) -> str:
    if entry_id in ENTRY_LEAF:
        return ENTRY_LEAF[entry_id]
    leaves = LEAVES[section]
    if subcategory:
        for lid, _name, _ord, keys in leaves:
            if keys and subcategory in keys:
                return lid
    # default = first leaf with keys is None, else first leaf
    for lid, _name, _ord, keys in leaves:
        if keys is None:
            return lid
    return leaves[0][0]


# ---------- categories.json ----------
old_cats = load(ROOT / "categories.json")
sections = []
for c in old_cats:
    sections.append(
        {
            "id": c["id"],
            "code": c["code"],
            "name": c["name"],
            "kind": "section",
            "order": c["order"],
        }
    )

all_cats = list(sections)
for section_id, leaf_list in LEAVES.items():
    for lid, name, order, _keys in leaf_list:
        all_cats.append(
            {
                "id": lid,
                "name": name,
                "kind": "leaf",
                "parent": section_id,
                "order": order,
            }
        )

save(ROOT / "categories.json", all_cats)
print(f"categories: {len(sections)} sections + {len(all_cats) - len(sections)} leaves")

# ---------- migrate entries ----------
section_ids = {c["id"] for c in sections}
moved = 0
for path in sorted(ENTRIES.glob("*.json")):
    e = load(path)
    old_cat = e["category"]
    if old_cat not in section_ids and old_cat not in {l[0] for ls in LEAVES.values() for l in ls}:
        # already a leaf? skip if parent exists in LEAVES values
        continue
    if old_cat not in section_ids:
        continue
    leaf = resolve_leaf(old_cat, e["id"], e.get("subcategory"))
    e["category"] = leaf
    # keep subcategory as hint tag-like field for now
    e["lastReviewed"] = REVIEWED
    save(path, e)
    moved += 1
print(f"entries remapped: {moved}")

# ---------- ranking systems: map section → leaves ----------
# Which leaves inherit rankings formerly on a section
SECTION_TO_RANK_LEAVES: dict[str, list[str]] = {
    "coding-agent": ["coding-ide-agent", "coding-cli-agent"],  # not cloud-builder
    "llm": ["llm-frontier"],
    "model-gateway": ["gateway-router", "gateway-local"],
    "language-runtime": ["lang-language", "lang-runtime"],
    "framework": ["fw-fullstack", "fw-ui-lib"],
    "ui-library": ["ui-kits", "ui-composable", "ui-primitives"],  # NOT ui-icons
    "cloud-deploy": ["cloud-paas"],
    "database-storage": ["db-relational", "db-nosql", "db-cache", "db-object", "db-sqlite-edge"],
    "baas-auth": ["baas-platform", "baas-auth-only"],
    "ai-infra": ["ai-agent-fw", "ai-rag", "ai-vector", "ai-llm-obs"],
    "payment": ["pay-processor", "pay-mor"],
    "app-distribution": ["dist-ios", "dist-android", "dist-extension", "dist-desktop"],
    "oss-ecosystem": ["oss-toolchain"],
    "observability": ["obs-errors", "obs-product", "obs-platform"],
    "cicd-devops": ["cicd-pipeline"],
    "messaging": ["msg-email", "msg-sms", "msg-push", "msg-im"],
    "analytics-growth": ["growth-web"],
    "domain-dns-cdn": ["net-cdn-dns", "net-domain"],
    "security-compliance": ["sec-secrets"],
    "design-assets": ["design-tools", "design-ai-image", "design-motion"],
    "collaboration": ["collab-pm", "collab-docs", "collab-suite"],
    "globalization": ["global-fx", "global-entity", "global-i18n"],
}

rankings = load(ROOT / "ranking-systems.json")
for sys in rankings:
    new_cats: list[str] = []
    for c in sys["categories"]:
        if c in SECTION_TO_RANK_LEAVES:
            new_cats.extend(SECTION_TO_RANK_LEAVES[c])
        else:
            new_cats.append(c)
    # dedupe preserve order
    seen = set()
    sys["categories"] = [x for x in new_cats if not (x in seen or seen.add(x))]

# dedicated icon ranking for ui-icons
rankings.append(
    {
        "id": "iconify-popularity",
        "name": "Iconify / 开源图标生态采用",
        "shortName": "Iconify",
        "categories": ["ui-icons"],
        "metric": "tier",
        "url": "https://iconify.design/",
        "description": "图标集在 Iconify 与前端生态中的采用广度；图标库不应与 Ant Design 等同榜。",
        "authority": "Iconify / community",
        "updateCadence": "ad-hoc",
        "order": 1,
    }
)
rankings.append(
    {
        "id": "github-icon-stars",
        "name": "GitHub Stars · Icon Sets",
        "shortName": "GH Icons",
        "categories": ["ui-icons"],
        "metric": "score",
        "url": "https://github.com/",
        "description": "主流开源图标集仓库星标，衡量开发者心智份额（非组件库可比）。",
        "authority": "GitHub",
        "updateCadence": "ad-hoc",
        "order": 2,
    }
)
save(ROOT / "ranking-systems.json", rankings)
print(f"ranking systems: {len(rankings)}")

# ---------- new entries: kimi-k3, phosphor, moonshot vendor ----------
vendors = load(ROOT / "vendors" / "seed.json")
if not any(v["id"] == "moonshot" for v in vendors):
    vendors.append(
        {
            "id": "moonshot",
            "name": "月之暗面 Moonshot AI",
            "region": "domestic",
            "url": "https://www.moonshot.cn",
        }
    )
if not any(v["id"] == "phosphor" for v in vendors):
    vendors.append(
        {
            "id": "phosphor",
            "name": "Phosphor Icons",
            "region": "overseas",
            "url": "https://phosphoricons.com",
        }
    )
save(ROOT / "vendors" / "seed.json", vendors)

kimi = {
    "id": "kimi-k3",
    "name": "Kimi K3",
    "category": "llm-frontier",
    "subcategory": "frontier",
    "vendorId": "moonshot",
    "region": "domestic",
    "oneLiner": "月之暗面 2.8T 开源旗舰模型",
    "descriptionMd": (
        "Kimi K3 是月之暗面 2026-07 发布的旗舰模型：约 2.8 万亿参数 MoE，"
        "原生多模态与 100 万 token 上下文，面向长程编程与知识工作。"
        "API 模型 id 为 `kimi-k3`；完整权重计划于 2026-07-27 前开源。"
    ),
    "officialUrl": "https://www.kimi.com",
    "docsUrl": "https://platform.kimi.com/docs/guide/kimi-k3-quickstart",
    "currentVersion": "K3",
    "pricing": {
        "model": "usage",
        "notes": "API：缓存命中输入约 $0.30/MTok，未命中约 $3/MTok，输出约 $15/MTok（以官方为准）",
        "currency": "USD",
    },
    "availability": {
        "chinaAccessible": True,
        "needsCompany": False,
        "needsIcp": False,
        "regions": ["CN", "global"],
    },
    "tags": ["llm", "domestic", "open-weights", "moe", "long-context", "multimodal", "coding"],
    "maturity": "stable",
    "pitfalls": [
        "旗舰调用需充值解锁；新用户代金券不可用于 K3",
        "自托管需大规模加速器集群，非消费级硬件可跑满血",
        "C 端高峰可能限流",
    ],
    "updates": [
        {
            "date": "2026-07-16",
            "type": "release",
            "version": "K3",
            "summary": "发布 Kimi K3：2.8T MoE、1M 上下文、原生视觉；API 上线",
            "source": "https://www.kimi.com/zh-cn/blog/kimi-k3",
        }
    ],
    "rankings": [
        {
            "systemId": "lmarena-text",
            "tier": "Open frontier",
            "period": "2026-07",
            "note": "开源/开权重量级旗舰；闭源顶尖仍可能领先",
            "sourceUrl": "https://www.kimi.com/zh-cn/blog/kimi-k3",
            "asOf": REVIEWED,
        }
    ],
    "sources": [
        "https://www.kimi.com/zh-cn/blog/kimi-k3",
        "https://platform.kimi.com/docs/guide/kimi-k3-quickstart",
    ],
    "lastReviewed": REVIEWED,
}
save(ENTRIES / "kimi-k3.json", kimi)

# older kimi entry as lineage optional - skip if too vague

phosphor = {
    "id": "phosphor-icons",
    "name": "Phosphor Icons",
    "category": "ui-icons",
    "subcategory": "icons",
    "vendorId": "phosphor",
    "region": "both",
    "oneLiner": "灵活权重的开源图标集",
    "descriptionMd": (
        "六种字重的 SVG/React/RN 图标库；VibeHolding 设计规范硬性采用。"
        "与 Ant Design 等完整组件库不可同榜对比。"
    ),
    "officialUrl": "https://phosphoricons.com",
    "docsUrl": "https://github.com/phosphor-icons/react",
    "pricing": {"model": "open-source"},
    "availability": {
        "chinaAccessible": True,
        "needsCompany": False,
        "needsIcp": False,
        "regions": ["global"],
    },
    "tags": ["icons", "svg", "react", "design-system"],
    "maturity": "mature",
    "pitfalls": ["与完整 UI 套件不是同一选型问题"],
    "updates": [],
    "rankings": [
        {
            "systemId": "iconify-popularity",
            "tier": "Widely adopted",
            "period": "2026",
            "asOf": REVIEWED,
        },
        {
            "systemId": "github-icon-stars",
            "tier": "Popular",
            "period": "2026",
            "asOf": REVIEWED,
        },
    ],
    "sources": ["https://phosphoricons.com"],
    "lastReviewed": REVIEWED,
}
save(ENTRIES / "phosphor-icons.json", phosphor)

# lucide rankings for icon leaf
lucide_path = ENTRIES / "lucide.json"
if lucide_path.exists():
    lucide = load(lucide_path)
    lucide["category"] = "ui-icons"
    lucide["rankings"] = [
        {
            "systemId": "iconify-popularity",
            "tier": "Widely adopted",
            "period": "2026",
            "asOf": REVIEWED,
        },
        {
            "systemId": "github-icon-stars",
            "tier": "Popular",
            "period": "2026",
            "note": "Feather 继任者生态",
            "asOf": REVIEWED,
        },
    ]
    lucide["lastReviewed"] = REVIEWED
    save(lucide_path, lucide)

# edges
edges = load(ROOT / "edges" / "seed.json")
edge_ids = {e["id"] for e in edges}


def add_edge(eid, frm, to, typ, weight=0.7, confidence="community", note=None):
    if eid in edge_ids:
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
    edge_ids.add(eid)


add_edge("e-kimi-k3-alt-claude", "kimi-k3", "claude-opus", "alternative_to", 0.65)
add_edge("e-kimi-k3-alt-deepseek", "kimi-k3", "deepseek-v3", "alternative_to", 0.7)
add_edge("e-kimi-k3-alt-glm", "kimi-k3", "glm", "alternative_to", 0.75)
add_edge("e-kimi-k3-alt-qwen", "kimi-k3", "qwen", "alternative_to", 0.7)
add_edge("e-openrouter-access-kimi", "openrouter", "kimi-k3", "provides_access_to", 0.5)
add_edge("e-phosphor-alt-lucide", "phosphor-icons", "lucide", "alternative_to", 0.8)
add_edge("e-lucide-with-shadcn", "lucide", "shadcn-ui", "commonly_used_with", 0.85)
add_edge(
    "e-phosphor-with-shadcn",
    "phosphor-icons",
    "shadcn-ui",
    "commonly_used_with",
    0.55,
    note="可替换 Lucide；本仓库设计规范采用 Phosphor",
)
save(ROOT / "edges" / "seed.json", edges)
print(f"edges total: {len(edges)}")
print("done")
