#!/usr/bin/env python3
"""2026-07 联网调研扩种：增量写入 entries/edges/vendors/concepts/recipes，不覆盖已有条目（除显式更新）。"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "content"
ENTRIES = ROOT / "entries"
RECIPES = ROOT / "recipes"
EDGES = ROOT / "edges" / "seed.json"
VENDORS = ROOT / "vendors" / "seed.json"
CONCEPTS = ROOT / "concepts" / "seed.json"
REVIEWED = "2026-07-23"


def entry(**kw):
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
    return e


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


def write_entry(e: dict, overwrite: bool = False) -> bool:
    path = ENTRIES / f"{e['id']}.json"
    if path.exists() and not overwrite:
        return False
    path.write_text(json.dumps(e, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return True


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def save_json(path: Path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def merge_by_id(existing: list, new_items: list) -> int:
    ids = {x["id"] for x in existing}
    added = 0
    for item in new_items:
        if item["id"] not in ids:
            existing.append(item)
            ids.add(item["id"])
            added += 1
    return added


# ---------- entries ----------
new_entries: list[dict] = []

# D language-runtime
new_entries += [
    entry(
        id="typescript",
        name="TypeScript",
        category="language-runtime",
        subcategory="language",
        region="both",
        oneLiner="带类型的 JavaScript 超集",
        descriptionMd="微软主导的静态类型语言，Vibe Coding / 全栈 Web 的事实标准。",
        officialUrl="https://www.typescriptlang.org",
        docsUrl="https://www.typescriptlang.org/docs/",
        pricing={"model": "open-source"},
        tags=["language", "web", "vibe-friendly"],
        maturity="mature",
        rankings=[{"systemId": "tiobe-index", "tier": "Top tier", "period": "2026", "asOf": REVIEWED, "note": "长期高人气"}],
    ),
    entry(
        id="nodejs",
        name="Node.js",
        category="language-runtime",
        subcategory="runtime",
        region="both",
        oneLiner="最主流的 JS/TS 服务端运行时",
        descriptionMd="基于 V8 的 JavaScript 运行时，npm 生态中心。",
        officialUrl="https://nodejs.org",
        docsUrl="https://nodejs.org/docs/",
        pricing={"model": "open-source"},
        tags=["runtime", "javascript"],
        maturity="mature",
    ),
    entry(
        id="bun",
        name="Bun",
        category="language-runtime",
        subcategory="runtime",
        oneLiner="高速 all-in-one JS 运行时与工具链",
        descriptionMd="兼容 Node 的运行时，内置打包、测试与包管理，偏 DX。",
        officialUrl="https://bun.sh",
        docsUrl="https://bun.sh/docs",
        pricing={"model": "open-source"},
        tags=["runtime", "javascript", "dx"],
        pitfalls=["部分 Node 原生模块兼容仍有缺口"],
    ),
    entry(
        id="python",
        name="Python",
        category="language-runtime",
        subcategory="language",
        region="both",
        oneLiner="AI / 数据与脚本的通用语言",
        descriptionMd="AI Agent 框架与数据科学默认语言；后端与自动化亦常用。",
        officialUrl="https://www.python.org",
        pricing={"model": "open-source"},
        tags=["language", "ai", "scripting"],
        maturity="mature",
        rankings=[{"systemId": "tiobe-index", "rank": 1, "period": "2026", "asOf": REVIEWED}],
    ),
    entry(
        id="go",
        name="Go",
        category="language-runtime",
        subcategory="language",
        region="both",
        oneLiner="简洁高并发的系统与云原生语言",
        descriptionMd="Google 开源，适合 CLI、网关、基础设施与高并发服务。",
        officialUrl="https://go.dev",
        pricing={"model": "open-source"},
        tags=["language", "cloud-native"],
        maturity="mature",
    ),
    entry(
        id="rust",
        name="Rust",
        category="language-runtime",
        subcategory="language",
        region="both",
        oneLiner="内存安全的系统级语言",
        descriptionMd="无 GC 的高性能语言；Tauri、部分运行时与工具链底层常用。",
        officialUrl="https://www.rust-lang.org",
        pricing={"model": "open-source"},
        tags=["language", "systems"],
        maturity="mature",
        pitfalls=["学习曲线陡，Vibe 生成后仍需人工审内存/生命周期"],
    ),
    entry(
        id="deno",
        name="Deno",
        category="language-runtime",
        subcategory="runtime",
        oneLiner="安全优先的 TS-first 运行时",
        descriptionMd="默认权限沙箱、原生 TypeScript；Deno Deploy 边缘部署。",
        officialUrl="https://deno.com",
        pricing={"model": "open-source"},
        tags=["runtime", "typescript", "edge"],
        pitfalls=["npm 兼容相对 Bun/Node 仍需验证"],
    ),
]

# J ai-infra
new_entries += [
    entry(
        id="vercel-ai-sdk",
        name="Vercel AI SDK",
        category="ai-infra",
        subcategory="sdk",
        vendorId="vercel-inc",
        oneLiner="TS 流式 AI 应用原语库",
        descriptionMd="统一多模型流式输出、工具调用与 UI 钩子；Mastra 等常建其上。",
        officialUrl="https://sdk.vercel.ai",
        docsUrl="https://sdk.vercel.ai/docs",
        pricing={"model": "open-source"},
        tags=["typescript", "streaming", "vibe-friendly"],
    ),
    entry(
        id="mastra",
        name="Mastra",
        category="ai-infra",
        subcategory="agent-framework",
        oneLiner="TypeScript 全栈 Agent 框架",
        descriptionMd="agents、工作流、memory、RAG、evals 一体；面向 TS 生产 Agent。",
        officialUrl="https://mastra.ai",
        docsUrl="https://mastra.ai/docs",
        pricing={"model": "open-source"},
        tags=["typescript", "agent", "rag"],
        pitfalls=["生态相对 LangChain 年轻，集成面在快速变化"],
    ),
    entry(
        id="langgraph",
        name="LangGraph",
        category="ai-infra",
        subcategory="agent-framework",
        oneLiner="有状态 Agent 图编排（Python 强）",
        descriptionMd="LangChain 生态的图工作流，适合复杂分支、人机回路与持久化。",
        officialUrl="https://www.langchain.com/langgraph",
        pricing={"model": "open-source"},
        tags=["python", "agent", "workflow"],
    ),
    entry(
        id="llamaindex",
        name="LlamaIndex",
        category="ai-infra",
        subcategory="rag",
        oneLiner="文档 RAG 与数据代理框架",
        descriptionMd="专注索引、检索与文档增强生成；Python/TS 均有。",
        officialUrl="https://www.llamaindex.ai",
        pricing={"model": "open-source"},
        tags=["rag", "documents"],
    ),
    entry(
        id="dify",
        name="Dify",
        category="ai-infra",
        subcategory="low-code",
        region="both",
        oneLiner="开源 LLM 应用可视化平台",
        descriptionMd="工作流、RAG、Agent 可视化编排；国内团队采用多，可自托管。",
        officialUrl="https://dify.ai",
        pricing={"model": "open-source"},
        tags=["low-code", "rag", "self-host"],
        pitfalls=["重度定制时仍可能要跳出可视化层写代码"],
    ),
    entry(
        id="pgvector",
        name="pgvector",
        category="ai-infra",
        subcategory="vector",
        oneLiner="Postgres 向量扩展",
        descriptionMd="在现有 Postgres/Supabase/Neon 上做向量检索，Indie RAG 首选。",
        officialUrl="https://github.com/pgvector/pgvector",
        pricing={"model": "open-source"},
        tags=["vector", "postgres", "rag"],
        rankings=[{"systemId": "db-engines-vector", "tier": "Extension", "period": "2026", "asOf": REVIEWED}],
    ),
    entry(
        id="qdrant",
        name="Qdrant",
        category="ai-infra",
        subcategory="vector",
        oneLiner="高性能开源向量数据库",
        descriptionMd="过滤+向量检索优秀；可云可自托管。",
        officialUrl="https://qdrant.tech",
        pricing={"model": "freemium"},
        tags=["vector", "search"],
        rankings=[{"systemId": "db-engines-vector", "tier": "Popular", "period": "2026", "asOf": REVIEWED}],
    ),
    entry(
        id="langfuse",
        name="Langfuse",
        category="ai-infra",
        subcategory="observability",
        oneLiner="开源 LLM 可观测与评测",
        descriptionMd="追踪、评分、数据集与 Prompt 管理；可自托管。",
        officialUrl="https://langfuse.com",
        pricing={"model": "open-source"},
        tags=["observability", "evals", "self-host"],
    ),
]

# L app-distribution
new_entries += [
    entry(
        id="apple-app-store",
        name="Apple App Store",
        category="app-distribution",
        subcategory="ios",
        oneLiner="iOS/macOS 官方应用商店",
        descriptionMd="苹果生态分发主渠道；需开发者账号、审核与隐私合规。",
        officialUrl="https://developer.apple.com/app-store/",
        pricing={"model": "subscription", "notes": "开发者账号约 $99/年；分成 15%/30%", "currency": "USD"},
        availability={"chinaAccessible": True, "needsCompany": False, "needsIcp": False, "regions": ["global"]},
        tags=["ios", "macos", "store"],
        pitfalls=["审核周期与拒审理由多变", "国内主体上架另有资质要求"],
        maturity="mature",
    ),
    entry(
        id="google-play",
        name="Google Play",
        category="app-distribution",
        subcategory="android",
        oneLiner="全球 Android 主应用商店",
        descriptionMd="Google 官方商店；国内访问与收款路径需单独规划。",
        officialUrl="https://play.google.com/console",
        pricing={"model": "subscription", "notes": "一次性注册费；分成政策以官方为准", "currency": "USD"},
        tags=["android", "store"],
        pitfalls=["中国大陆用户需国内安卓市场并行", "收款常绑万里汇/Airwallex 等"],
        maturity="mature",
    ),
    entry(
        id="chrome-web-store",
        name="Chrome Web Store",
        category="app-distribution",
        subcategory="extension",
        oneLiner="Chrome/Chromium 扩展商店",
        descriptionMd="浏览器扩展分发；Manifest V3 与权限审核是关键约束。",
        officialUrl="https://chrome.google.com/webstore",
        pricing={"model": "freemium"},
        tags=["extension", "browser"],
        pitfalls=["权限与隐私政策审核严格"],
        maturity="mature",
    ),
    entry(
        id="github-releases",
        name="GitHub Releases",
        category="app-distribution",
        subcategory="desktop",
        oneLiner="开源/桌面应用直接分发渠道",
        descriptionMd="通过 GitHub Releases 分发二进制；常配合自动更新（Tauri/Sparkle）。",
        officialUrl="https://docs.github.com/en/repositories/releasing-projects-on-github",
        pricing={"model": "freemium"},
        tags=["desktop", "opensource", "distribution"],
        maturity="mature",
    ),
    entry(
        id="testflight",
        name="TestFlight",
        category="app-distribution",
        subcategory="ios",
        oneLiner="Apple 官方 Beta 测试分发",
        descriptionMd="App Store Connect 内测通道，上架前验证与小范围灰度。",
        officialUrl="https://developer.apple.com/testflight/",
        pricing={"model": "free"},
        tags=["ios", "beta"],
        maturity="mature",
    ),
    entry(
        id="huawei-appgallery",
        name="华为应用市场",
        category="app-distribution",
        subcategory="android",
        region="domestic",
        oneLiner="国内安卓重要分发渠道",
        descriptionMd="华为 AppGallery；国内安卓多市场之一，常需软著/资质。",
        officialUrl="https://developer.huawei.com/consumer/cn/appgallery/",
        pricing={"model": "freemium"},
        availability={"chinaAccessible": True, "needsCompany": True, "needsIcp": False, "regions": ["CN"]},
        tags=["android", "domestic", "store"],
        pitfalls=["多市场重复打包与审核成本高"],
        maturity="mature",
    ),
]

# A cloud-builder + ide-agent deepen
new_entries += [
    entry(
        id="lovable",
        name="Lovable",
        category="coding-agent",
        subcategory="cloud-builder",
        oneLiner="提示即全栈应用的云端 Builder",
        descriptionMd="浏览器内从描述到部署；默认 React/Supabase 等意见栈，锁仓风险需注意。",
        officialUrl="https://lovable.dev",
        pricing={"model": "subscription", "currency": "USD"},
        tags=["vibe-friendly", "cloud-builder", "runtime:vendor-cloud"],
        pitfalls=["厂商 runtime 锁仓，毕业到自有栈成本高", "不适合持有真实生产凭据的长期项目"],
    ),
    entry(
        id="bolt-new",
        name="Bolt.new",
        category="coding-agent",
        subcategory="cloud-builder",
        oneLiner="StackBlitz 的浏览器全栈原型工具",
        descriptionMd="偏营销页与快速原型；WebContainers 本机感，部署仍偏平台。",
        officialUrl="https://bolt.new",
        pricing={"model": "freemium", "currency": "USD"},
        tags=["vibe-friendly", "cloud-builder", "prototype"],
        pitfalls=["超出原型阶段需迁移到可移植仓库"],
    ),
    entry(
        id="v0",
        name="v0",
        category="coding-agent",
        subcategory="cloud-builder",
        vendorId="vercel-inc",
        oneLiner="Vercel 的 UI 生成原语",
        descriptionMd="从描述/设计生成 React+Tailwind 组件；常嵌入其他 vibe 工作流。",
        officialUrl="https://v0.dev",
        pricing={"model": "freemium", "currency": "USD"},
        tags=["ui", "react", "cloud-builder"],
        pitfalls=["偏单次 UI 生成，不是完整工程 Agent"],
    ),
    entry(
        id="replit-agent",
        name="Replit Agent",
        category="coding-agent",
        subcategory="cloud-builder",
        oneLiner="Replit 内的云端编程 Agent",
        descriptionMd="在 Replit IDE/运行时内完成与部署；「接着写完」体验强，锁 Replit runtime。",
        officialUrl="https://replit.com",
        pricing={"model": "subscription", "currency": "USD"},
        tags=["cloud-builder", "runtime:vendor-cloud"],
        pitfalls=["迁移出 Replit 成本高"],
    ),
    entry(
        id="github-copilot",
        name="GitHub Copilot",
        category="coding-agent",
        subcategory="ide-agent",
        oneLiner="多 IDE 的企业友好 AI 结对",
        descriptionMd="VS Code/JetBrains 等广泛集成；企业可预测计费与合规叙事强。",
        officialUrl="https://github.com/features/copilot",
        pricing={"model": "subscription", "currency": "USD"},
        tags=["ide", "enterprise", "ide-agent"],
        pitfalls=["多文件自治深度通常弱于 Cursor/Claude Code"],
    ),
    entry(
        id="openai-codex",
        name="OpenAI Codex",
        category="coding-agent",
        subcategory="ide-agent",
        vendorId="openai",
        oneLiner="OpenAI 异步云端编码 Agent",
        descriptionMd="CLI/Web/移动跨面状态保持；沙箱执行，适合并行异步任务。",
        officialUrl="https://openai.com/codex/",
        pricing={"model": "usage", "currency": "USD"},
        tags=["agent", "async", "ide-agent"],
    ),
]

# M oss-ecosystem
new_entries += [
    entry(id="vite", name="Vite", category="oss-ecosystem", subcategory="bundler", oneLiner="下一代前端构建工具", descriptionMd="基于 ESM 的极速开发服务器与打包；Vue/React 生态默认。", officialUrl="https://vite.dev", pricing={"model": "open-source"}, tags=["bundler", "frontend"], maturity="mature"),
    entry(id="pnpm", name="pnpm", category="oss-ecosystem", subcategory="package-manager", oneLiner="高效磁盘的包管理器", descriptionMd="内容寻址存储与严格依赖；Monorepo 友好。", officialUrl="https://pnpm.io", pricing={"model": "open-source"}, tags=["monorepo", "dx"], maturity="mature"),
    entry(id="biome", name="Biome", category="oss-ecosystem", subcategory="lint-format", oneLiner="统一的 lint+format 工具链", descriptionMd="Rust 实现，替代 ESLint+Prettier 组合的常见选择。", officialUrl="https://biomejs.dev", pricing={"model": "open-source"}, tags=["lint", "format"], maturity="stable"),
    entry(id="zod", name="Zod", category="oss-ecosystem", subcategory="validation", oneLiner="TS 优先的运行时 Schema", descriptionMd="校验+类型推导一体；API/表单/配置的事实标准之一。", officialUrl="https://zod.dev", pricing={"model": "open-source"}, tags=["schema", "typescript"], maturity="mature"),
    entry(id="drizzle", name="Drizzle ORM", category="oss-ecosystem", subcategory="orm", oneLiner="轻量 SQL-first TypeScript ORM", descriptionMd="贴近 SQL 的类型安全 ORM；与 Neon/Turso/Postgres 搭配多。", officialUrl="https://orm.drizzle.team", pricing={"model": "open-source"}, tags=["orm", "sql"], maturity="stable"),
    entry(id="tanstack-query", name="TanStack Query", category="oss-ecosystem", subcategory="data-fetching", oneLiner="异步状态与缓存库", descriptionMd="服务端状态管理；React/Vue 等前端数据层主流。", officialUrl="https://tanstack.com/query", pricing={"model": "open-source"}, tags=["react", "cache"], maturity="mature"),
    entry(id="trpc", name="tRPC", category="oss-ecosystem", subcategory="api", oneLiner="端到端类型安全 RPC", descriptionMd="共享 TS 类型的客户端-服务端调用；常与 Next/Monorepo 同用。", officialUrl="https://trpc.io", pricing={"model": "open-source"}, tags=["typescript", "api"], maturity="stable"),
]

# N observability
new_entries += [
    entry(id="sentry", name="Sentry", category="observability", subcategory="errors", oneLiner="错误与性能监控平台", descriptionMd="异常聚合、性能与 Session Replay；前后端广泛 SDK。", officialUrl="https://sentry.io", pricing={"model": "freemium", "currency": "USD"}, tags=["errors", "apm"], maturity="mature"),
    entry(id="posthog", name="PostHog", category="observability", subcategory="product-analytics", oneLiner="开源产品分析与功能旗标", descriptionMd="事件分析、Session、Feature flags；可云可自托管。亦常归入增长类。", officialUrl="https://posthog.com", pricing={"model": "freemium", "currency": "USD"}, tags=["analytics", "self-host", "flags"], maturity="stable"),
    entry(id="opentelemetry", name="OpenTelemetry", category="observability", subcategory="standards", oneLiner="可观测性开放标准", descriptionMd="Traces/Metrics/Logs 统一采集规范；对接多家后端。", officialUrl="https://opentelemetry.io", pricing={"model": "open-source"}, tags=["otel", "standards"], maturity="mature"),
    entry(id="grafana", name="Grafana", category="observability", subcategory="dashboards", oneLiner="开源可观测可视化", descriptionMd="仪表盘与告警；常与 Prometheus/Loki 组合。", officialUrl="https://grafana.com", pricing={"model": "freemium"}, tags=["dashboards", "self-host"], maturity="mature"),
    entry(id="axiom", name="Axiom", category="observability", subcategory="logs", oneLiner="面向开发者的日志与事件平台", descriptionMd="高基数事件查询；Serverless/边缘场景友好。", officialUrl="https://axiom.co", pricing={"model": "freemium", "currency": "USD"}, tags=["logs", "events"], maturity="stable"),
]

# O cicd
new_entries += [
    entry(id="github-actions", name="GitHub Actions", category="cicd-devops", subcategory="ci", oneLiner="GitHub 原生 CI/CD", descriptionMd="YAML 工作流；与 PR/Release 深度集成，Indie 默认选择。", officialUrl="https://github.com/features/actions", pricing={"model": "freemium"}, tags=["ci", "cd"], maturity="mature"),
    entry(id="docker", name="Docker", category="cicd-devops", subcategory="containers", oneLiner="容器化事实标准", descriptionMd="镜像构建与运行；本地到云的一致性交付基础。", officialUrl="https://www.docker.com", pricing={"model": "freemium"}, tags=["containers"], maturity="mature"),
    entry(id="pulumi", name="Pulumi", category="cicd-devops", subcategory="iac", oneLiner="用通用语言写的 IaC", descriptionMd="TS/Python 等写基础设施；相对 HCL 对前端更友好。", officialUrl="https://www.pulumi.com", pricing={"model": "freemium", "currency": "USD"}, tags=["iac", "cloud"], maturity="stable"),
]

# P messaging
new_entries += [
    entry(id="resend", name="Resend", category="messaging", subcategory="email", oneLiner="开发者友好的事务邮件 API", descriptionMd="现代 DX 的邮件发送；与 React Email 生态配套。", officialUrl="https://resend.com", pricing={"model": "freemium", "currency": "USD"}, tags=["email", "transactional"], maturity="stable"),
    entry(id="twilio", name="Twilio", category="messaging", subcategory="sms", oneLiner="全球短信/语音 API", descriptionMd="SMS、Voice、Verify；出海通知常用。", officialUrl="https://www.twilio.com", pricing={"model": "usage", "currency": "USD"}, tags=["sms", "voice"], maturity="mature", pitfalls=["国内短信常另选阿里云/腾讯云"]),
    entry(id="firebase-fcm", name="Firebase Cloud Messaging", category="messaging", subcategory="push", vendorId="firebase-inc", oneLiner="跨平台推送服务", descriptionMd="Android/iOS/Web 推送；Firebase 生态一部分。", officialUrl="https://firebase.google.com/products/cloud-messaging", pricing={"model": "free"}, tags=["push", "mobile"], maturity="mature"),
    entry(id="feishu-bot", name="飞书机器人", category="messaging", subcategory="im", region="domestic", oneLiner="飞书群机器人与开放平台", descriptionMd="国内团队通知与审批流常用入口。", officialUrl="https://open.feishu.cn", pricing={"model": "freemium"}, tags=["im", "domestic"], maturity="mature"),
    entry(id="wecom", name="企业微信", category="messaging", subcategory="im", region="domestic", vendorId="tencent", oneLiner="企微消息与客户联系", descriptionMd="国内 B2B 触达与内部通知；与微信生态打通。", officialUrl="https://work.weixin.qq.com", pricing={"model": "freemium"}, tags=["im", "domestic"], maturity="mature"),
]

# Q growth
new_entries += [
    entry(id="plausible", name="Plausible", category="analytics-growth", subcategory="web-analytics", oneLiner="隐私友好的轻量分析", descriptionMd="无 Cookie 墙叙事的网站分析；可自托管。", officialUrl="https://plausible.io", pricing={"model": "subscription", "currency": "USD"}, tags=["privacy", "analytics"], maturity="stable"),
    entry(id="umami", name="Umami", category="analytics-growth", subcategory="web-analytics", oneLiner="开源简单网站分析", descriptionMd="自托管优先的轻量统计，替代 GA 的常见选择。", officialUrl="https://umami.is", pricing={"model": "open-source"}, tags=["self-host", "analytics"], maturity="stable"),
    entry(id="ga4", name="Google Analytics 4", category="analytics-growth", subcategory="web-analytics", vendorId="google", oneLiner="谷歌网站与应用分析", descriptionMd="事件模型的主流分析；隐私合规与国内可用性需评估。", officialUrl="https://analytics.google.com", pricing={"model": "free"}, tags=["analytics", "google"], maturity="mature", pitfalls=["国内访问与合规成本", "Cookie/同意管理负担"]),
]

# R network — avoid id collision with vendor `cloudflare`
new_entries += [
    entry(id="cloudflare-cdn", name="Cloudflare", category="domain-dns-cdn", subcategory="cdn-dns", vendorId="cloudflare", oneLiner="DNS / CDN / 安全一体网络", descriptionMd="域名、DNS、CDN、WAF 与 Workers 边缘；Indie 零成本出海常用底座。", officialUrl="https://www.cloudflare.com", pricing={"model": "freemium"}, tags=["cdn", "dns", "edge"], maturity="mature"),
    entry(id="aliyun-wanwang", name="阿里云万网", category="domain-dns-cdn", subcategory="domain", region="domestic", vendorId="alibaba-cloud", oneLiner="国内域名注册主渠道", descriptionMd="域名注册与国内备案流程常经阿里云。", officialUrl="https://wanwang.aliyun.com", pricing={"model": "usage"}, availability={"chinaAccessible": True, "needsCompany": False, "needsIcp": False, "regions": ["CN"]}, tags=["domain", "domestic"], maturity="mature"),
    entry(id="dnspod", name="DNSPod", category="domain-dns-cdn", subcategory="dns", region="domestic", vendorId="tencent", oneLiner="腾讯云 DNS 解析", descriptionMd="国内常用权威 DNS；与腾讯云产品联动。", officialUrl="https://www.dnspod.cn", pricing={"model": "freemium"}, tags=["dns", "domestic"], maturity="mature"),
    entry(id="edgeone", name="EdgeOne", category="domain-dns-cdn", subcategory="cdn", region="domestic", vendorId="tencent", oneLiner="腾讯边缘安全加速", descriptionMd="国内 CDN/边缘安全产品，对标 Cloudflare 部分能力。", officialUrl="https://edgeone.ai", pricing={"model": "usage"}, tags=["cdn", "edge", "domestic"], maturity="stable"),
]

# S security
new_entries += [
    entry(id="infisical", name="Infisical", category="security-compliance", subcategory="secrets", oneLiner="开源开发者 Secrets 平台", descriptionMd="项目/环境组织密钥；CLI `infisical run` 注入；可自托管。", officialUrl="https://infisical.com", pricing={"model": "open-source"}, tags=["secrets", "cli", "self-host"], maturity="stable"),
    entry(id="doppler", name="Doppler", category="security-compliance", subcategory="secrets", oneLiner="托管型开发者 Secrets", descriptionMd="按项目/环境同步密钥；`doppler run` 注入子进程。", officialUrl="https://www.doppler.com", pricing={"model": "freemium", "currency": "USD"}, tags=["secrets", "cli"], maturity="stable", pitfalls=["云端托管，无自托管选项"]),
    entry(id="onepassword", name="1Password", category="security-compliance", subcategory="password-manager", oneLiner="密码库与开发者 Secrets 自动化", descriptionMd="个人/团队密码管理；CLI `op run` 与 Shell Plugin 注入。", officialUrl="https://1password.com", pricing={"model": "subscription", "currency": "USD"}, tags=["secrets", "password"], maturity="mature"),
    entry(id="hashicorp-vault", name="HashiCorp Vault", category="security-compliance", subcategory="secrets", oneLiner="企业级密钥与动态机密", descriptionMd="动态密钥、加密即服务；运维成本高，偏中大型团队。", officialUrl="https://www.vaultproject.io", pricing={"model": "freemium"}, tags=["secrets", "enterprise"], maturity="mature", pitfalls=["学习与运维成本显著高于 Doppler/Infisical"]),
]

# T design
new_entries += [
    entry(id="figma", name="Figma", category="design-assets", subcategory="design", oneLiner="协作式界面设计工具", descriptionMd="设计与原型协作标准；Dev Mode / 变量对接工程。", officialUrl="https://www.figma.com", pricing={"model": "freemium", "currency": "USD"}, tags=["design", "ui"], maturity="mature"),
    entry(id="lottiefiles", name="LottieFiles", category="design-assets", subcategory="motion", oneLiner="Lottie 动效资源与工具", descriptionMd="轻量矢量动效格式生态；Web/移动端常用。", officialUrl="https://lottiefiles.com", pricing={"model": "freemium"}, tags=["motion", "lottie"], maturity="stable"),
    entry(id="lucide", name="Lucide", category="design-assets", subcategory="icons", oneLiner="开源图标集", descriptionMd="基于 Feather 的清晰图标；React/多框架封装。", officialUrl="https://lucide.dev", pricing={"model": "open-source"}, tags=["icons"], maturity="mature"),
    entry(id="jimeng", name="即梦", category="design-assets", subcategory="ai-image", region="domestic", vendorId="bytedance", oneLiner="字节系 AI 图像生成", descriptionMd="国内可用的文生图/设计辅助；合规与商用条款需核对。", officialUrl="https://jimeng.jianying.com", pricing={"model": "freemium"}, tags=["ai", "image", "domestic"], maturity="stable"),
    entry(id="midjourney", name="Midjourney", category="design-assets", subcategory="ai-image", oneLiner="高质量文生图", descriptionMd="Discord/Web 驱动的图像生成；品牌与营销视觉常用。", officialUrl="https://www.midjourney.com", pricing={"model": "subscription", "currency": "USD"}, tags=["ai", "image"], maturity="stable", pitfalls=["商用授权与账号区域政策需核对"]),
]

# U collab
new_entries += [
    entry(id="linear", name="Linear", category="collaboration", subcategory="pm", oneLiner="工程师友好的项目管理", descriptionMd="高速 issue 追踪；与 GitHub/Agent 工作流契合。", officialUrl="https://linear.app", pricing={"model": "freemium", "currency": "USD"}, tags=["pm", "issues"], maturity="stable"),
    entry(id="notion", name="Notion", category="collaboration", subcategory="docs", oneLiner="万能文档与知识库", descriptionMd="文档/数据库/Wiki；团队知识沉淀常用。", officialUrl="https://www.notion.so", pricing={"model": "freemium", "currency": "USD"}, tags=["docs", "wiki"], maturity="mature"),
    entry(id="feishu", name="飞书", category="collaboration", subcategory="suite", region="domestic", oneLiner="国内一站式协作套件", descriptionMd="文档、日历、IM、审批；国内团队默认协作面。", officialUrl="https://www.feishu.cn", pricing={"model": "freemium"}, tags=["suite", "domestic"], maturity="mature"),
    entry(id="github-projects", name="GitHub Projects", category="collaboration", subcategory="pm", oneLiner="仓库内嵌项目管理", descriptionMd="Issues + Projects 看板；与 PR/Actions 同仓。", officialUrl="https://docs.github.com/en/issues/planning-and-tracking-with-projects", pricing={"model": "freemium"}, tags=["pm", "github"], maturity="stable"),
]

# V globalization
new_entries += [
    entry(id="wise", name="Wise", category="globalization", subcategory="fx", oneLiner="多币种账户与低成本换汇", descriptionMd="跨境收款/付款与多币种余额；Indie 常用中转。", officialUrl="https://wise.com", pricing={"model": "usage"}, tags=["fx", "banking"], maturity="mature"),
    entry(id="worldfirst", name="万里汇 WorldFirst", category="globalization", subcategory="collection", region="domestic", oneLiner="应用商店与广告跨境收款", descriptionMd="蚂蚁国际旗下；支持商店/广告场景结汇，个人开发者友好叙事。", officialUrl="https://www.worldfirst.com.cn", pricing={"model": "usage"}, tags=["collection", "domestic", "store"], pitfalls=["费率与活动常变，以后台为准"], maturity="stable"),
    entry(id="airwallex", name="Airwallex 空中云汇", category="globalization", subcategory="collection", region="both", oneLiner="多币种全球账户与收款", descriptionMd="虚拟卡与多主体账户；适合多平台收款。", officialUrl="https://www.airwallex.com", pricing={"model": "usage"}, tags=["collection", "multi-currency"], maturity="stable"),
    entry(id="pingpong", name="PingPong", category="globalization", subcategory="collection", region="domestic", oneLiner="跨境收款平台", descriptionMd="电商与部分开发者场景收款；大额风控需注意。", officialUrl="https://www.pingpongx.com", pricing={"model": "usage"}, tags=["collection", "domestic"], maturity="stable"),
    entry(id="stripe-atlas", name="Stripe Atlas", category="globalization", subcategory="entity", vendorId="stripe-inc", oneLiner="一站式美国公司+Stripe 路径", descriptionMd="帮创业者注册美企并开通 Stripe；成本与银行侧（Mercury/EIN）近年变难。", officialUrl="https://stripe.com/atlas", pricing={"model": "usage", "notes": "一次性费用+年审量级见官方", "currency": "USD"}, tags=["entity", "stripe"], pitfalls=["大陆开发者仍须海外主体", "银行开户与 EIN 周期拉长"], maturity="stable"),
    entry(id="next-intl", name="next-intl", category="globalization", subcategory="i18n", oneLiner="Next.js 国际化库", descriptionMd="App Router 友好的 i18n；类型安全消息。", officialUrl="https://next-intl.dev", pricing={"model": "open-source"}, tags=["i18n", "nextjs"], maturity="stable"),
]

# deepen existing categories
new_entries += [
    entry(id="ollama", name="Ollama", category="model-gateway", subcategory="local", oneLiner="本机一键跑开源模型", descriptionMd="本地拉取与服务 LLM；隐私与离线场景。", officialUrl="https://ollama.com", pricing={"model": "open-source"}, tags=["local", "privacy"], maturity="stable"),
    entry(id="lm-studio", name="LM Studio", category="model-gateway", subcategory="local", oneLiner="图形化本地模型工作台", descriptionMd="桌面端管理与对话本地模型；适合非 CLI 用户。", officialUrl="https://lmstudio.ai", pricing={"model": "free"}, tags=["local", "desktop"], maturity="stable"),
    entry(id="better-auth", name="Better Auth", category="baas-auth", subcategory="auth", oneLiner="TS 优先的开源鉴权框架", descriptionMd="Email/OAuth/组织/2FA 等；自托管、框架无关，Indie starter 高频。", officialUrl="https://www.better-auth.com", pricing={"model": "open-source"}, tags=["auth", "typescript", "self-host"], maturity="stable"),
    entry(id="turso", name="Turso", category="database-storage", subcategory="sqlite", oneLiner="边缘 SQLite（libSQL）", descriptionMd="分布式 SQLite；与 Cloudflare/边缘部署搭配。", officialUrl="https://turso.tech", pricing={"model": "freemium", "currency": "USD"}, tags=["sqlite", "edge"], maturity="stable"),
    entry(id="cloudflare-r2", name="Cloudflare R2", category="database-storage", subcategory="object-storage", vendorId="cloudflare", oneLiner="无出口费的对象存储", descriptionMd="S3 兼容；与 Workers/Pages 同生态。", officialUrl="https://www.cloudflare.com/developer-platform/r2/", pricing={"model": "usage", "currency": "USD"}, tags=["storage", "s3"], maturity="stable"),
    entry(id="upstash", name="Upstash", category="database-storage", subcategory="serverless-data", oneLiner="Serverless Redis/队列等", descriptionMd="按请求计费的 Redis、QStash 等；边缘友好。", officialUrl="https://upstash.com", pricing={"model": "freemium", "currency": "USD"}, tags=["redis", "serverless"], maturity="stable"),
    entry(id="creem", name="Creem", category="payment", subcategory="mor", oneLiner="新兴 MoR 支付", descriptionMd="面向独立开发者的 Merchant of Record；常作 LS/Paddle 备选。", officialUrl="https://www.creem.io", pricing={"model": "usage", "currency": "USD"}, tags=["mor", "payment"], maturity="beta", pitfalls=["相对 Stripe/Paddle 生态更年轻"]),
    entry(id="polar", name="Polar", category="payment", subcategory="mor", oneLiner="开源友好的 MoR / 变现", descriptionMd="开源项目与数字产品变现；MoR 税务托管叙事。", officialUrl="https://polar.sh", pricing={"model": "usage", "currency": "USD"}, tags=["mor", "opensource", "payment"], maturity="stable"),
    entry(id="tanstack-start", name="TanStack Start", category="framework", subcategory="fullstack", oneLiner="TanStack 全栈框架", descriptionMd="Router/Query/Form 一体的全栈起步；可部署 Cloudflare 等。", officialUrl="https://tanstack.com/start", pricing={"model": "open-source"}, tags=["react", "fullstack"], maturity="beta"),
]

# strip None vendorId
for e in new_entries:
    if e.get("vendorId") is None:
        e.pop("vendorId", None)

added_n = 0
for e in new_entries:
    if write_entry(e):
        added_n += 1
print(f"entries added: {added_n} / attempted {len(new_entries)}")

# ---------- update lemonsqueezy ----------
ls_path = ENTRIES / "lemonsqueezy.json"
ls = load_json(ls_path)
ls["pitfalls"] = [
    "已被 Stripe 收购；产品路线可能并入 Stripe 生态",
    "2026 起对新大陆独立开发者申请收紧，新项目慎选",
    "品类限制仍在；费率相对自建 Stripe 偏高",
]
ls["descriptionMd"] = (
    "Merchant of Record，曾适合卖数字商品与订阅。"
    "被 Stripe 收购后，存量账户可继续；**新大陆独立开发者**更建议评估 Paddle / Polar / Creem。"
)
ls["updates"] = [
    {
        "date": "2024-07-01",
        "type": "policy",
        "summary": "Stripe 宣布收购 Lemon Squeezy",
        "source": "https://stripe.com/blog",
    },
    {
        "date": "2026-01-01",
        "type": "policy",
        "summary": "大陆新独立开发者开通难度上升（社区观测）；优先考虑其他 MoR",
        "source": "https://chdh.me/reports/stripe-china-guide-2026/",
    },
]
ls["lastReviewed"] = REVIEWED
ls["tags"] = list(dict.fromkeys([*ls.get("tags", []), "mor", "legacy-caution"]))
save_json(ls_path, ls)
print("updated lemonsqueezy")

# optional: mark existing agents ide-agent
for aid in ["cursor", "claude-code", "windsurf", "continue", "aider", "trae"]:
    p = ENTRIES / f"{aid}.json"
    if p.exists():
        data = load_json(p)
        if data.get("subcategory") in (None, "ide"):
            data["subcategory"] = "ide-agent"
            data["lastReviewed"] = REVIEWED
            save_json(p, data)
print("patched A subcategory ide-agent")

# ---------- vendors ----------
vendors = load_json(VENDORS)
new_vendors = [
    {"id": "mistral", "name": "Mistral AI", "region": "overseas", "url": "https://mistral.ai"},
    {"id": "replit-inc", "name": "Replit", "region": "overseas", "url": "https://replit.com"},
    {"id": "stackblitz", "name": "StackBlitz", "region": "overseas", "url": "https://stackblitz.com"},
    {"id": "lovable-inc", "name": "Lovable", "region": "overseas", "url": "https://lovable.dev"},
    {"id": "qdrant-inc", "name": "Qdrant", "region": "overseas", "url": "https://qdrant.tech"},
    {"id": "langfuse-inc", "name": "Langfuse", "region": "overseas", "url": "https://langfuse.com"},
    {"id": "mastra-inc", "name": "Mastra", "region": "overseas", "url": "https://mastra.ai"},
    {"id": "dify-inc", "name": "Dify", "region": "both", "url": "https://dify.ai"},
    {"id": "apple", "name": "Apple", "region": "overseas", "url": "https://www.apple.com"},
    {"id": "huawei", "name": "华为", "region": "domestic", "url": "https://www.huawei.com"},
    {"id": "posthog-inc", "name": "PostHog", "region": "overseas", "url": "https://posthog.com"},
    {"id": "sentry-inc", "name": "Sentry", "region": "overseas", "url": "https://sentry.io"},
    {"id": "resend-inc", "name": "Resend", "region": "overseas", "url": "https://resend.com"},
    {"id": "twilio-inc", "name": "Twilio", "region": "overseas", "url": "https://www.twilio.com"},
    {"id": "infisical-inc", "name": "Infisical", "region": "overseas", "url": "https://infisical.com"},
    {"id": "doppler-inc", "name": "Doppler", "region": "overseas", "url": "https://www.doppler.com"},
    {"id": "1password-inc", "name": "1Password", "region": "overseas", "url": "https://1password.com"},
    {"id": "hashicorp", "name": "HashiCorp", "region": "overseas", "url": "https://www.hashicorp.com"},
    {"id": "figma-inc", "name": "Figma", "region": "overseas", "url": "https://www.figma.com"},
    {"id": "linear-inc", "name": "Linear", "region": "overseas", "url": "https://linear.app"},
    {"id": "notion-inc", "name": "Notion", "region": "overseas", "url": "https://www.notion.so"},
    {"id": "wise-inc", "name": "Wise", "region": "overseas", "url": "https://wise.com"},
    {"id": "worldfirst-inc", "name": "万里汇", "region": "domestic", "url": "https://www.worldfirst.com.cn"},
    {"id": "airwallex-inc", "name": "Airwallex", "region": "both", "url": "https://www.airwallex.com"},
    {"id": "pingpong-inc", "name": "PingPong", "region": "domestic", "url": "https://www.pingpongx.com"},
    {"id": "polar-inc", "name": "Polar", "region": "overseas", "url": "https://polar.sh"},
    {"id": "creem-inc", "name": "Creem", "region": "overseas", "url": "https://www.creem.io"},
    {"id": "turso-inc", "name": "Turso", "region": "overseas", "url": "https://turso.tech"},
    {"id": "upstash-inc", "name": "Upstash", "region": "overseas", "url": "https://upstash.com"},
    {"id": "better-auth-inc", "name": "Better Auth", "region": "overseas", "url": "https://www.better-auth.com"},
]
print(f"vendors added: {merge_by_id(vendors, new_vendors)}")
save_json(VENDORS, vendors)

# ---------- concepts ----------
concepts = load_json(CONCEPTS)
new_concepts = [
    {"id": "oauth", "name": "OAuth", "summaryMd": "委托授权协议，第三方登录与 API 授权的基础。", "aliases": ["OAuth 2.0"]},
    {"id": "mor", "name": "Merchant of Record (MoR)", "summaryMd": "由平台作为法定商家代收并处理税务/合规，降低卖家主体负担。", "aliases": ["MoR", "Merchant of Record"]},
    {"id": "icp", "name": "ICP 备案", "summaryMd": "中国大陆网站托管需完成的工信部备案要求。", "aliases": ["备案"]},
    {"id": "function-calling", "name": "Function / Tool Calling", "summaryMd": "模型按 schema 调用外部工具/函数的能力。", "aliases": ["Tool Calling", "Tools"]},
    {"id": "e2ee", "name": "End-to-End Encryption", "summaryMd": "端到端加密：服务端仅存密文，无法解密用户数据。", "aliases": ["E2EE", "零知识"]},
]
print(f"concepts added: {merge_by_id(concepts, new_concepts)}")
save_json(CONCEPTS, concepts)

# ---------- edges ----------
edges = load_json(EDGES)
new_edges = [
    # D
    edge("e-ts-with-next", "typescript", "nextjs", "commonly_used_with", 0.95, "verified"),
    edge("e-bun-alt-node", "bun", "nodejs", "alternative_to", 0.75),
    edge("e-deno-alt-node", "deno", "nodejs", "alternative_to", 0.65),
    edge("e-python-with-langgraph", "python", "langgraph", "commonly_used_with", 0.85),
    edge("e-ts-with-mastra", "typescript", "mastra", "commonly_used_with", 0.8),
    # J
    edge("e-mastra-built-ai-sdk", "mastra", "vercel-ai-sdk", "built_on", 0.7),
    edge("e-ai-sdk-with-next", "vercel-ai-sdk", "nextjs", "integrates_with", 0.85, "verified"),
    edge("e-llamaindex-uses-rag", "llamaindex", "rag", "uses_concept", 0.95, "verified"),
    edge("e-pgvector-int-pg", "pgvector", "postgresql", "integrates_with", 0.95, "verified"),
    edge("e-pgvector-with-supabase", "pgvector", "supabase", "commonly_used_with", 0.85),
    edge("e-qdrant-alt-pgvector", "qdrant", "pgvector", "alternative_to", 0.6),
    edge("e-dify-uses-rag", "dify", "rag", "uses_concept", 0.8),
    edge("e-langfuse-with-mastra", "langfuse", "mastra", "commonly_used_with", 0.55),
    # L
    edge("e-testflight-part-apple", "testflight", "apple-app-store", "part_of", 0.9, "verified"),
    edge("e-huawei-dom-gplay", "huawei-appgallery", "google-play", "domestic_equivalent_of", 0.7),
    edge("e-gh-releases-with-github-actions", "github-releases", "github-actions", "commonly_used_with", 0.75),
    # A
    edge("e-lovable-with-supabase", "lovable", "supabase", "commonly_used_with", 0.85),
    edge("e-v0-owned-vercel", "v0", "vercel-inc", "owned_by", 0.95, "verified"),
    edge("e-bolt-alt-lovable", "bolt-new", "lovable", "alternative_to", 0.7),
    edge("e-replit-alt-lovable", "replit-agent", "lovable", "alternative_to", 0.6),
    edge("e-copilot-alt-cursor", "github-copilot", "cursor", "alternative_to", 0.75),
    edge("e-codex-alt-claude-code", "openai-codex", "claude-code", "alternative_to", 0.7),
    edge("e-codex-powered-openai", "openai-codex", "gpt-4o", "powered_by", 0.7),
    # K LS migration
    edge("e-ls-migrate-paddle", "lemonsqueezy", "paddle", "migration_path_to", 0.8, "community", "MoR 迁移候选"),
    edge("e-ls-migrate-creem", "lemonsqueezy", "creem", "migration_path_to", 0.65, "community"),
    edge("e-ls-migrate-polar", "lemonsqueezy", "polar", "migration_path_to", 0.7, "community"),
    edge("e-creem-alt-paddle", "creem", "paddle", "alternative_to", 0.7),
    edge("e-polar-alt-paddle", "polar", "paddle", "alternative_to", 0.75),
    edge("e-paddle-uses-mor", "paddle", "mor", "uses_concept", 0.9, "verified"),
    edge("e-creem-uses-mor", "creem", "mor", "uses_concept", 0.85),
    edge("e-polar-uses-mor", "polar", "mor", "uses_concept", 0.85),
    edge("e-ls-uses-mor", "lemonsqueezy", "mor", "uses_concept", 0.9, "verified"),
    # deepen
    edge("e-ollama-alt-openrouter", "ollama", "openrouter", "alternative_to", 0.5, "community", "本地 vs 云路由"),
    edge("e-lmstudio-alt-ollama", "lm-studio", "ollama", "alternative_to", 0.7),
    edge("e-better-auth-oss-clerk", "better-auth", "clerk", "open_source_alternative_to", 0.75),
    edge("e-better-auth-alt-auth0", "better-auth", "auth0", "alternative_to", 0.65),
    edge("e-turso-alt-neon", "turso", "neon", "alternative_to", 0.55),
    edge("e-r2-alt-s3-narrative", "cloudflare-r2", "cloudflare-pages", "commonly_used_with", 0.8),
    edge("e-upstash-alt-redis", "upstash", "redis", "alternative_to", 0.7),
    edge("e-tanstack-start-alt-next", "tanstack-start", "nextjs", "alternative_to", 0.65),
    edge("e-tanstack-start-depends-react", "tanstack-start", "react", "depends_on", 0.95, "verified"),
    # M
    edge("e-biome-oss-eslint-prettier", "biome", "vite", "commonly_used_with", 0.6),
    edge("e-drizzle-with-neon", "drizzle", "neon", "commonly_used_with", 0.8),
    edge("e-drizzle-with-turso", "drizzle", "turso", "commonly_used_with", 0.75),
    edge("e-trpc-with-next", "trpc", "nextjs", "commonly_used_with", 0.8),
    edge("e-zod-with-trpc", "zod", "trpc", "commonly_used_with", 0.85),
    edge("e-pnpm-with-vite", "pnpm", "vite", "commonly_used_with", 0.7),
    edge("e-tq-with-react", "tanstack-query", "react", "commonly_used_with", 0.9, "verified"),
    # N/Q
    edge("e-posthog-with-next", "posthog", "nextjs", "commonly_used_with", 0.75),
    edge("e-umami-oss-ga4", "umami", "ga4", "open_source_alternative_to", 0.7),
    edge("e-plausible-alt-ga4", "plausible", "ga4", "alternative_to", 0.75),
    edge("e-sentry-with-next", "sentry", "nextjs", "integrates_with", 0.8),
    edge("e-otel-with-grafana", "opentelemetry", "grafana", "commonly_used_with", 0.7),
    # O
    edge("e-gha-with-docker", "github-actions", "docker", "commonly_used_with", 0.75),
    edge("e-gha-with-vercel", "github-actions", "vercel", "commonly_used_with", 0.7),
    # P
    edge("e-resend-with-next", "resend", "nextjs", "commonly_used_with", 0.8),
    edge("e-feishu-bot-part-feishu", "feishu-bot", "feishu", "part_of", 0.85),
    # R
    edge("e-edgeone-dom-cf", "edgeone", "cloudflare-cdn", "domestic_equivalent_of", 0.65),
    edge("e-cf-cdn-with-pages", "cloudflare-cdn", "cloudflare-pages", "commonly_used_with", 0.9, "verified"),
    edge("e-cf-cdn-with-r2", "cloudflare-cdn", "cloudflare-r2", "commonly_used_with", 0.85),
    # S — contrast with VH positioning (knowledge only)
    edge("e-infisical-oss-doppler", "infisical", "doppler", "open_source_alternative_to", 0.8),
    edge("e-infisical-alt-vault", "infisical", "hashicorp-vault", "alternative_to", 0.55),
    edge("e-1p-alt-doppler", "onepassword", "doppler", "alternative_to", 0.5),
    # T/U/V
    edge("e-lucide-with-shadcn", "lucide", "shadcn-ui", "commonly_used_with", 0.85),
    edge("e-jimeng-dom-mj", "jimeng", "midjourney", "domestic_equivalent_of", 0.6),
    edge("e-feishu-dom-notion", "feishu", "notion", "domestic_equivalent_of", 0.55),
    edge("e-linear-alt-gh-projects", "linear", "github-projects", "alternative_to", 0.65),
    edge("e-next-intl-with-next", "next-intl", "nextjs", "integrates_with", 0.9, "verified"),
    edge("e-worldfirst-with-gplay", "worldfirst", "google-play", "commonly_used_with", 0.7),
    edge("e-atlas-with-stripe", "stripe-atlas", "stripe", "commonly_used_with", 0.95, "verified"),
    edge("e-clerk-uses-oauth", "clerk", "oauth", "uses_concept", 0.85),
    edge("e-better-auth-uses-oauth", "better-auth", "oauth", "uses_concept", 0.85),
    edge("e-ai-sdk-uses-fc", "vercel-ai-sdk", "function-calling", "uses_concept", 0.8),
]
print(f"edges added: {merge_by_id(edges, new_edges)}")
save_json(EDGES, edges)

# ---------- recipes ----------
recipes = [
    {
        "id": "ai-rag-app",
        "name": "AI RAG 应用版",
        "target": "快速上线可检索私有知识的 AI Web 应用",
        "layers": {
            "coding-agent": "cursor",
            "llm": "claude-opus",
            "framework": "nextjs",
            "ui": "shadcn-ui",
            "ai-sdk": "vercel-ai-sdk",
            "vector": "pgvector",
            "baas": "supabase",
            "deploy": "vercel",
            "observability": "langfuse",
        },
        "rationaleMd": "TS 全链路：Cursor + Claude 写代码，AI SDK 流式，pgvector 顺 Postgres/Supabase，Langfuse 看链路。",
        "estimatedCost": "月成本约 $20–60 起（视模型用量）",
        "caveats": ["向量与 chunk 策略决定效果", "生产需配额与密钥轮换"],
    },
    {
        "id": "cf-zero-cost-oversea",
        "name": "Cloudflare 零成本出海版",
        "target": "尽量压低固定成本的出海 Web MVP",
        "layers": {
            "coding-agent": "cursor",
            "framework": "tanstack-start",
            "ui": "shadcn-ui",
            "auth": "better-auth",
            "db": "turso",
            "storage": "cloudflare-r2",
            "deploy": "cloudflare-pages",
            "network": "cloudflare-cdn",
            "email": "resend",
            "payment": "polar",
        },
        "rationaleMd": "Workers/Pages + R2 + Turso 压低固定成本；Better Auth 自托管鉴权；Polar 作 MoR 收款。",
        "estimatedCost": "固定成本可接近 $0，邮件与 MoR 按量",
        "caveats": ["边缘运行时限制需提前验证", "复杂后台或许可仍可能要另外部署"],
    },
    {
        "id": "domestic-wechat-dual",
        "name": "国内双端+微信生态版",
        "target": "面向国内用户、接入微信登录与支付的应用",
        "layers": {
            "coding-agent": "trae",
            "llm": "qwen",
            "framework": "nextjs",
            "ui": "antd",
            "baas": "supabase",
            "deploy": "aliyun-fc",
            "payment": "wechat-pay",
            "alt-pay": "alipay",
            "messaging": "wecom",
            "domain": "aliyun-wanwang",
        },
        "rationaleMd": "国内 Agent/模型 + 阿里云函数 + 微信/支付宝收款；域名走万网便于备案叙事。",
        "estimatedCost": "视云与支付费率；需主体与资质",
        "caveats": ["微信支付/登录需企业主体与认证", "小程序另需独立分发路径", "ICP 备案（概念 icp）"],
    },
]
for r in recipes:
    p = RECIPES / f"{r['id']}.json"
    if not p.exists():
        save_json(p, r)
        print(f"recipe created: {r['id']}")
    else:
        print(f"recipe skip: {r['id']}")

print("done")
