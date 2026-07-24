#!/usr/bin/env python3
"""一次性扩充种子内容（T-CORE-9）。可重复执行：覆盖 entries/vendors/concepts/edges。"""
from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "content"
ENTRIES = ROOT / "entries"


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
        "sources": [],
        "lastReviewed": "2026-07-20",
        "region": "overseas",
    }
    e.update(kw)
    if "officialUrl" in e and not e["sources"]:
        e["sources"] = [e["officialUrl"]]
    if e.get("vendorId") is None:
        e.pop("vendorId", None)
    assert len(e["oneLiner"]) <= 60, (e["id"], len(e["oneLiner"]), e["oneLiner"])
    return e


def edge(eid, frm, to, typ, weight=0.7, confidence="community", note=None):
    e = {
        "id": eid,
        "from": frm,
        "to": to,
        "type": typ,
        "weight": weight,
        "confidence": confidence,
        "sources": [],
        "createdAt": "2026-07-23",
    }
    if note:
        e["note"] = note
    return e


vendors = [
    {"id": "anysphere", "name": "Anysphere", "region": "overseas", "url": "https://anysphere.inc"},
    {"id": "anthropic", "name": "Anthropic", "region": "overseas", "url": "https://anthropic.com"},
    {"id": "zhipu-ai", "name": "智谱 AI", "region": "domestic", "url": "https://zhipuai.cn"},
    {"id": "vercel-inc", "name": "Vercel", "region": "overseas", "url": "https://vercel.com"},
    {"id": "supabase-inc", "name": "Supabase", "region": "overseas", "url": "https://supabase.com"},
    {"id": "stripe-inc", "name": "Stripe", "region": "overseas", "url": "https://stripe.com"},
    {"id": "tencent", "name": "腾讯", "region": "domestic", "url": "https://tencent.com"},
    {"id": "openai", "name": "OpenAI", "region": "overseas", "url": "https://openai.com"},
    {"id": "google", "name": "Google", "region": "overseas", "url": "https://google.com"},
    {"id": "deepseek", "name": "深度求索", "region": "domestic", "url": "https://www.deepseek.com"},
    {"id": "alibaba-cloud", "name": "阿里云", "region": "domestic", "url": "https://aliyun.com"},
    {"id": "bytedance", "name": "字节跳动", "region": "domestic", "url": "https://www.bytedance.com"},
    {"id": "codeium", "name": "Codeium", "region": "overseas", "url": "https://codeium.com"},
    {"id": "continue-dev", "name": "Continue", "region": "overseas", "url": "https://continue.dev"},
    {"id": "netlify-inc", "name": "Netlify", "region": "overseas", "url": "https://netlify.com"},
    {"id": "cloudflare", "name": "Cloudflare", "region": "overseas", "url": "https://cloudflare.com"},
    {"id": "railway-inc", "name": "Railway", "region": "overseas", "url": "https://railway.app"},
    {"id": "fly-io-inc", "name": "Fly.io", "region": "overseas", "url": "https://fly.io"},
    {"id": "firebase-inc", "name": "Firebase", "region": "overseas", "url": "https://firebase.google.com"},
    {"id": "clerk-inc", "name": "Clerk", "region": "overseas", "url": "https://clerk.com"},
    {"id": "auth0-inc", "name": "Auth0", "region": "overseas", "url": "https://auth0.com"},
    {"id": "appwrite-inc", "name": "Appwrite", "region": "overseas", "url": "https://appwrite.io"},
    {"id": "ant-group", "name": "蚂蚁集团", "region": "domestic", "url": "https://antgroup.com"},
    {"id": "paddle-inc", "name": "Paddle", "region": "overseas", "url": "https://paddle.com"},
    {"id": "lemon-squeezy", "name": "Lemon Squeezy", "region": "overseas", "url": "https://lemonsqueezy.com"},
    {"id": "neon-inc", "name": "Neon", "region": "overseas", "url": "https://neon.tech"},
    {"id": "planetscale-inc", "name": "PlanetScale", "region": "overseas", "url": "https://planetscale.com"},
    {"id": "mongodb", "name": "MongoDB", "region": "overseas", "url": "https://mongodb.com"},
    {"id": "redis-ltd", "name": "Redis Ltd.", "region": "overseas", "url": "https://redis.io"},
    {"id": "siliconflow-inc", "name": "硅基流动", "region": "domestic", "url": "https://siliconflow.cn"},
    {"id": "meta", "name": "Meta", "region": "overseas", "url": "https://meta.com"},
]

entries: list[dict] = []


def add(e: dict) -> None:
    entries.append(e)


# ---- coding-agent ----
add(
    entry(
        id="cursor",
        name="Cursor",
        category="coding-agent",
        subcategory="ide",
        vendorId="anysphere",
        oneLiner="AI 原生代码编辑器",
        descriptionMd="基于 VS Code 的 AI 原生编辑器，内置 Agent、多文件编辑与 MCP。",
        officialUrl="https://cursor.com",
        docsUrl="https://docs.cursor.com",
        pricing={"model": "subscription", "notes": "Pro $20/月起", "currency": "USD"},
        tags=["ai", "ide", "mcp", "vibe-friendly"],
        pitfalls=["额度用尽后变慢", "注意 Privacy Mode"],
        updates=[
            {
                "date": "2026-07-10",
                "type": "feature",
                "summary": "增强 Agent 多步任务能力",
                "source": "https://cursor.com/changelog",
            }
        ],
    )
)
add(
    entry(
        id="windsurf",
        name="Windsurf",
        category="coding-agent",
        subcategory="ide",
        vendorId="codeium",
        oneLiner="Codeium 出品的 Agent 编辑器",
        descriptionMd="面向 Agent 工作流的 IDE，强调级联编辑与上下文感知。",
        officialUrl="https://codeium.com/windsurf",
        tags=["ai", "ide", "agent"],
        maturity="beta",
        pitfalls=["生态仍在快速变化"],
    )
)
add(
    entry(
        id="claude-code",
        name="Claude Code",
        category="coding-agent",
        subcategory="cli",
        vendorId="anthropic",
        oneLiner="Anthropic 官方终端编程 Agent",
        descriptionMd="在终端中调用 Claude 完成多文件改动、命令执行与仓库理解。",
        officialUrl="https://docs.anthropic.com/en/docs/claude-code",
        pricing={"model": "usage", "currency": "USD"},
        availability={
            "chinaAccessible": False,
            "needsCompany": False,
            "needsIcp": False,
            "regions": ["us", "eu"],
        },
        tags=["cli", "agent", "anthropic"],
        maturity="beta",
        pitfalls=["需 Anthropic API", "中国大陆需中转"],
    )
)
add(
    entry(
        id="trae",
        name="Trae",
        category="coding-agent",
        subcategory="ide",
        vendorId="bytedance",
        region="domestic",
        oneLiner="字节跳动推出的 AI IDE",
        descriptionMd="面向中文开发者的 AI 编程环境，强调国内可访问与协作。",
        officialUrl="https://www.trae.ai",
        tags=["ai", "ide", "domestic"],
        maturity="beta",
        pitfalls=["海外生态对接仍弱"],
    )
)
add(
    entry(
        id="continue",
        name="Continue",
        category="coding-agent",
        subcategory="extension",
        vendorId="continue-dev",
        oneLiner="开源 IDE 扩展，可接任意模型",
        descriptionMd="VS Code / JetBrains 扩展，支持自托管模型与自定义 Agent。",
        officialUrl="https://continue.dev",
        pricing={"model": "open-source"},
        tags=["oss", "extension", "bring-your-model"],
        pitfalls=["体验依赖所选模型质量"],
    )
)
add(
    entry(
        id="aider",
        name="Aider",
        category="coding-agent",
        subcategory="cli",
        oneLiner="Git 友好的终端结对编程工具",
        descriptionMd="基于 Git 的命令行 AI 结对编程，自动提交与仓库感知。",
        officialUrl="https://aider.chat",
        pricing={"model": "open-source"},
        tags=["cli", "git", "oss"],
        pitfalls=["需自备模型 API Key"],
    )
)

# ---- llm ----
add(
    entry(
        id="claude-opus",
        name="Claude Opus",
        category="llm",
        vendorId="anthropic",
        oneLiner="Anthropic 旗舰级大模型",
        descriptionMd="擅长复杂推理与代码，支持长上下文与工具调用。",
        officialUrl="https://www.anthropic.com/claude",
        docsUrl="https://docs.anthropic.com",
        pricing={"model": "usage", "notes": "按 token 计费", "currency": "USD"},
        availability={
            "chinaAccessible": False,
            "needsCompany": False,
            "needsIcp": False,
            "regions": ["us", "eu"],
        },
        tags=["llm", "reasoning", "code"],
        maturity="mature",
        pitfalls=["中国大陆不可直接访问", "输出 token 价格较高"],
        updates=[
            {
                "date": "2026-07-12",
                "type": "feature",
                "summary": "长上下文与工具调用改进",
                "source": "https://www.anthropic.com/news",
            }
        ],
    )
)
add(
    entry(
        id="glm",
        name="GLM",
        category="llm",
        vendorId="zhipu-ai",
        region="domestic",
        oneLiner="智谱国产大模型系列",
        descriptionMd="国内可直连的大模型，覆盖对话、代码与工具调用场景。",
        officialUrl="https://bigmodel.cn",
        pricing={"model": "usage", "currency": "CNY"},
        tags=["llm", "domestic", "code"],
        pitfalls=["部分能力与国外旗舰仍有差距", "需实名认证"],
        updates=[
            {
                "date": "2026-06-01",
                "type": "feature",
                "summary": "Coding 场景模型能力升级",
                "source": "https://bigmodel.cn",
            }
        ],
    )
)
add(
    entry(
        id="gpt-4o",
        name="GPT-4o",
        category="llm",
        vendorId="openai",
        oneLiner="OpenAI 多模态旗舰模型",
        descriptionMd="文本/图像多模态，生态工具与 SDK 最完善之一。",
        officialUrl="https://openai.com/gpt-4o",
        pricing={"model": "usage", "currency": "USD"},
        availability={
            "chinaAccessible": False,
            "needsCompany": False,
            "needsIcp": False,
            "regions": ["global"],
        },
        tags=["llm", "multimodal", "openai"],
        maturity="mature",
        pitfalls=["国内访问受限", "政策与额度变化频繁"],
    )
)
add(
    entry(
        id="gemini-pro",
        name="Gemini Pro",
        category="llm",
        vendorId="google",
        oneLiner="Google 多模态大模型",
        descriptionMd="与 Google Cloud / AI Studio 深度集成，长上下文表现突出。",
        officialUrl="https://deepmind.google/technologies/gemini/",
        pricing={"model": "usage", "currency": "USD"},
        availability={
            "chinaAccessible": False,
            "needsCompany": False,
            "needsIcp": False,
            "regions": ["global"],
        },
        tags=["llm", "google", "multimodal"],
        pitfalls=["国内不可直连", "配额与区域限制"],
    )
)
add(
    entry(
        id="deepseek-v3",
        name="DeepSeek V3",
        category="llm",
        vendorId="deepseek",
        region="domestic",
        oneLiner="高性价比国产推理/代码模型",
        descriptionMd="在代码与推理任务上性价比突出，国内可直连 API。",
        officialUrl="https://www.deepseek.com",
        pricing={"model": "usage", "currency": "CNY"},
        tags=["llm", "domestic", "code", "value"],
        pitfalls=["高峰期偶发排队", "文档英文较少"],
    )
)
add(
    entry(
        id="qwen",
        name="通义千问",
        category="llm",
        vendorId="alibaba-cloud",
        region="domestic",
        oneLiner="阿里云通义大模型系列",
        descriptionMd="覆盖通用对话与代码，与阿里云百炼/函数计算集成紧密。",
        officialUrl="https://tongyi.aliyun.com",
        pricing={"model": "usage", "currency": "CNY"},
        tags=["llm", "domestic", "aliyun"],
        pitfalls=["产品线名称多易混淆"],
    )
)

# ---- model-gateway ----
add(
    entry(
        id="openrouter",
        name="OpenRouter",
        category="model-gateway",
        oneLiner="多模型统一路由与计费网关",
        descriptionMd="一个 API Key 访问多家模型，适合快速切换与比价。",
        officialUrl="https://openrouter.ai",
        pricing={"model": "usage", "currency": "USD"},
        tags=["gateway", "routing"],
        pitfalls=["部分模型有区域限制", "需预充值"],
        updates=[
            {
                "date": "2026-07-08",
                "type": "pricing",
                "summary": "多模型路由费率表更新",
                "source": "https://openrouter.ai/docs",
            }
        ],
    )
)
add(
    entry(
        id="siliconflow",
        name="SiliconFlow",
        category="model-gateway",
        vendorId="siliconflow-inc",
        region="domestic",
        oneLiner="国内模型推理加速与聚合平台",
        descriptionMd="聚合开源/国产模型推理，适合国内低延迟调用。",
        officialUrl="https://siliconflow.cn",
        pricing={"model": "usage", "currency": "CNY"},
        tags=["gateway", "domestic", "inference"],
        pitfalls=["模型清单变化快"],
    )
)
add(
    entry(
        id="litellm",
        name="LiteLLM",
        category="model-gateway",
        oneLiner="开源多厂商 LLM 代理",
        descriptionMd="统一 OpenAI 兼容接口代理上百种模型，可自托管。",
        officialUrl="https://www.litellm.ai",
        pricing={"model": "open-source"},
        tags=["gateway", "oss", "proxy"],
        pitfalls=["自托管需运维", "配置项多"],
    )
)
add(
    entry(
        id="one-api",
        name="New API / One API",
        category="model-gateway",
        region="domestic",
        oneLiner="可自建的令牌分发与渠道网关",
        descriptionMd="国内社区常用的渠道聚合与令牌管理系统，可私有部署。",
        officialUrl="https://github.com/QuantumNous/new-api",
        pricing={"model": "open-source"},
        tags=["gateway", "oss", "self-host", "domestic"],
        pitfalls=["需自行维护渠道稳定性"],
    )
)
add(
    entry(
        id="azure-openai",
        name="Azure OpenAI",
        category="model-gateway",
        oneLiner="企业级 OpenAI 模型托管",
        descriptionMd="在 Azure 上托管 OpenAI 模型，强调合规与企业合同。",
        officialUrl="https://azure.microsoft.com/products/ai-services/openai-service",
        pricing={"model": "usage", "currency": "USD"},
        availability={
            "chinaAccessible": False,
            "needsCompany": True,
            "needsIcp": False,
            "regions": ["global"],
        },
        tags=["gateway", "enterprise", "openai"],
        maturity="mature",
        pitfalls=["开通与配额流程长", "需企业主体"],
    )
)

# ---- framework ----
add(
    entry(
        id="react",
        name="React",
        category="framework",
        vendorId="meta",
        oneLiner="声明式 UI 库，前端事实标准",
        descriptionMd="组件化 UI 库，生态庞大，是多数全栈框架的基础。",
        officialUrl="https://react.dev",
        pricing={"model": "open-source"},
        tags=["frontend", "ui", "library"],
        maturity="mature",
        pitfalls=["自身不含路由/数据方案，需自行组合"],
        lastReviewed="2026-07-15",
    )
)
add(
    entry(
        id="nextjs",
        name="Next.js",
        category="framework",
        subcategory="fullstack",
        vendorId="vercel-inc",
        oneLiner="React 全栈元框架",
        descriptionMd="基于 React 的全栈框架，支持 SSR/SSG/RSC，与 Vercel 深度集成。",
        officialUrl="https://nextjs.org",
        docsUrl="https://nextjs.org/docs",
        pricing={"model": "open-source"},
        tags=["react", "fullstack", "ssr", "vibe-friendly"],
        maturity="mature",
        pitfalls=["App Router 心智成本高", "非 Vercel 部署需额外配置"],
        updates=[
            {
                "date": "2026-06-15",
                "type": "feature",
                "summary": "Turbopack 稳定化",
                "source": "https://nextjs.org/blog",
            }
        ],
    )
)
add(
    entry(
        id="vue",
        name="Vue",
        category="framework",
        oneLiner="渐进式前端框架",
        descriptionMd="易上手的渐进式框架，中文生态与文档友好。",
        officialUrl="https://vuejs.org",
        pricing={"model": "open-source"},
        tags=["frontend", "progressive"],
        maturity="mature",
        pitfalls=["大型企业生态相对 React 偏少"],
    )
)
add(
    entry(
        id="nuxt",
        name="Nuxt",
        category="framework",
        subcategory="fullstack",
        oneLiner="Vue 全栈元框架",
        descriptionMd="基于 Vue 的全栈框架，支持 SSR 与文件路由。",
        officialUrl="https://nuxt.com",
        pricing={"model": "open-source"},
        tags=["vue", "fullstack", "ssr"],
        maturity="mature",
        pitfalls=["部分模块版本兼容需留意"],
    )
)
add(
    entry(
        id="remix",
        name="Remix",
        category="framework",
        subcategory="fullstack",
        oneLiner="注重 Web 标准的 React 框架",
        descriptionMd="强调嵌套路由、表单与渐进增强，可部署多端。",
        officialUrl="https://remix.run",
        pricing={"model": "open-source"},
        tags=["react", "fullstack", "web-standards"],
        pitfalls=["与 Next 生态心智不同"],
    )
)
add(
    entry(
        id="sveltekit",
        name="SvelteKit",
        category="framework",
        subcategory="fullstack",
        oneLiner="Svelte 全栈框架",
        descriptionMd="编译期优化的 Svelte 应用框架，包体小、性能好。",
        officialUrl="https://kit.svelte.dev",
        pricing={"model": "open-source"},
        tags=["svelte", "fullstack"],
        pitfalls=["招聘与组件生态小于 React"],
    )
)

# ---- ui-library ----
add(
    entry(
        id="shadcn-ui",
        name="shadcn/ui",
        category="ui-library",
        oneLiner="可复制的 Radix+Tailwind 组件集",
        descriptionMd="不是传统 npm 包，而是复制到项目中的高质量组件代码。",
        officialUrl="https://ui.shadcn.com",
        pricing={"model": "open-source"},
        tags=["ui", "react", "tailwind", "vibe-friendly"],
        pitfalls=["升级需手动同步"],
        updates=[
            {
                "date": "2026-05-30",
                "type": "feature",
                "summary": "新增表单与图表组件块",
                "source": "https://ui.shadcn.com",
            }
        ],
    )
)
add(
    entry(
        id="antd",
        name="Ant Design",
        category="ui-library",
        oneLiner="企业级 React UI 组件库",
        descriptionMd="蚂蚁开源的企业级组件库，中文文档与国内生态成熟。",
        officialUrl="https://ant.design",
        pricing={"model": "open-source"},
        tags=["ui", "react", "enterprise", "domestic-friendly"],
        maturity="mature",
        pitfalls=["默认风格偏后台", "包体积偏大"],
    )
)
add(
    entry(
        id="mantine",
        name="Mantine",
        category="ui-library",
        oneLiner="功能丰富的 React 组件与 hooks",
        descriptionMd="自带主题、表单与 hooks，适合快速搭后台与 SaaS。",
        officialUrl="https://mantine.dev",
        pricing={"model": "open-source"},
        tags=["ui", "react", "hooks"],
        pitfalls=["定制深度不如自研设计系统"],
    )
)
add(
    entry(
        id="radix-ui",
        name="Radix UI",
        category="ui-library",
        oneLiner="无样式无障碍基础原语",
        descriptionMd="提供可访问性优先的无样式组件原语，常作设计系统底座。",
        officialUrl="https://www.radix-ui.com",
        pricing={"model": "open-source"},
        tags=["ui", "a11y", "primitives"],
        maturity="mature",
        pitfalls=["需自行补齐样式体系"],
    )
)
add(
    entry(
        id="daisyui",
        name="DaisyUI",
        category="ui-library",
        oneLiner="Tailwind 组件类插件",
        descriptionMd="基于 Tailwind 的语义化组件类，适合快速出界面。",
        officialUrl="https://daisyui.com",
        pricing={"model": "open-source"},
        tags=["ui", "tailwind"],
        pitfalls=["复杂交互仍需手写"],
    )
)

# ---- cloud-deploy ----
add(
    entry(
        id="vercel",
        name="Vercel",
        category="cloud-deploy",
        vendorId="vercel-inc",
        oneLiner="前端与 Serverless 部署平台",
        descriptionMd="与 Next.js 一等集成，预览部署与边缘网络成熟。",
        officialUrl="https://vercel.com",
        pricing={"model": "freemium", "currency": "USD"},
        tags=["deploy", "serverless", "vibe-friendly"],
        maturity="mature",
        pitfalls=["超额计费需关注", "国内访问不稳定"],
        updates=[
            {
                "date": "2026-07-01",
                "type": "pricing",
                "summary": "Hobby 额度调整",
                "source": "https://vercel.com/pricing",
            }
        ],
    )
)
add(
    entry(
        id="netlify",
        name="Netlify",
        category="cloud-deploy",
        vendorId="netlify-inc",
        oneLiner="Jamstack 部署与边缘函数平台",
        descriptionMd="静态站与边缘函数友好，表单/身份等插件丰富。",
        officialUrl="https://www.netlify.com",
        pricing={"model": "freemium", "currency": "USD"},
        tags=["deploy", "jamstack"],
        maturity="mature",
        pitfalls=["与 Vercel 功能高度重叠"],
    )
)
add(
    entry(
        id="cloudflare-pages",
        name="Cloudflare Pages",
        category="cloud-deploy",
        vendorId="cloudflare",
        oneLiner="全球 CDN 上的静态/SSR 托管",
        descriptionMd="依托 Cloudflare 网络，Workers 集成紧密，性价比高。",
        officialUrl="https://pages.cloudflare.com",
        pricing={"model": "freemium", "currency": "USD"},
        tags=["deploy", "cdn", "workers"],
        pitfalls=["部分 Node API 兼容需适配"],
    )
)
add(
    entry(
        id="railway",
        name="Railway",
        category="cloud-deploy",
        vendorId="railway-inc",
        oneLiner="从仓库到数据库的一站式 PaaS",
        descriptionMd="适合快速部署全栈与数据库，开发体验友好。",
        officialUrl="https://railway.app",
        pricing={"model": "usage", "currency": "USD"},
        tags=["deploy", "paas", "database"],
        pitfalls=["成本随用量上升快"],
    )
)
add(
    entry(
        id="fly-io",
        name="Fly.io",
        category="cloud-deploy",
        vendorId="fly-io-inc",
        oneLiner="靠近用户的容器托管",
        descriptionMd="全球多区域跑 Docker，适合需要靠近用户的后端。",
        officialUrl="https://fly.io",
        pricing={"model": "usage", "currency": "USD"},
        tags=["deploy", "containers", "edge"],
        pitfalls=["运维心智高于纯 Serverless"],
    )
)
add(
    entry(
        id="aliyun-fc",
        name="阿里云函数计算",
        category="cloud-deploy",
        vendorId="alibaba-cloud",
        region="domestic",
        oneLiner="国内 Serverless 函数计算",
        descriptionMd="按量计费的事件驱动计算，适合国内合规与低延迟。",
        officialUrl="https://www.aliyun.com/product/fc",
        pricing={"model": "usage", "currency": "CNY"},
        availability={
            "chinaAccessible": True,
            "needsCompany": False,
            "needsIcp": False,
            "regions": ["cn"],
        },
        tags=["deploy", "serverless", "domestic"],
        maturity="mature",
        pitfalls=["厂商锁定", "控制台复杂度高"],
    )
)

# ---- baas-auth ----
add(
    entry(
        id="supabase",
        name="Supabase",
        category="baas-auth",
        vendorId="supabase-inc",
        oneLiner="开源 Firebase 替代（Postgres）",
        descriptionMd="Postgres + Auth + Storage + Realtime，适合快速做后端。",
        officialUrl="https://supabase.com",
        pricing={"model": "freemium", "currency": "USD"},
        tags=["baas", "postgres", "auth", "vibe-friendly"],
        pitfalls=["闲置项目可能暂停", "RLS 上手有门槛"],
        updates=[
            {
                "date": "2026-06-28",
                "type": "feature",
                "summary": "向量检索与 Auth Hook 增强",
                "source": "https://supabase.com/changelog",
            }
        ],
    )
)
add(
    entry(
        id="firebase",
        name="Firebase",
        category="baas-auth",
        vendorId="firebase-inc",
        oneLiner="Google 移动/Web 后端套件",
        descriptionMd="Auth、Firestore、Hosting 一体化，移动端生态强。",
        officialUrl="https://firebase.google.com",
        pricing={"model": "freemium", "currency": "USD"},
        availability={
            "chinaAccessible": False,
            "needsCompany": False,
            "needsIcp": False,
            "regions": ["global"],
        },
        tags=["baas", "google", "mobile"],
        maturity="mature",
        pitfalls=["国内不可用", "厂商锁定深"],
    )
)
add(
    entry(
        id="clerk",
        name="Clerk",
        category="baas-auth",
        vendorId="clerk-inc",
        oneLiner="面向前端的认证与用户管理",
        descriptionMd="开箱即用的登录组件与组织/多租户能力，Next.js 友好。",
        officialUrl="https://clerk.com",
        pricing={"model": "freemium", "currency": "USD"},
        tags=["auth", "saas", "nextjs"],
        pitfalls=["免费额度后涨价明显"],
    )
)
add(
    entry(
        id="auth0",
        name="Auth0",
        category="baas-auth",
        vendorId="auth0-inc",
        oneLiner="企业级身份认证平台",
        descriptionMd="成熟的 IDaaS，协议与合规能力强，适合 B2B。",
        officialUrl="https://auth0.com",
        pricing={"model": "subscription", "currency": "USD"},
        tags=["auth", "enterprise"],
        maturity="mature",
        pitfalls=["定价高", "配置复杂"],
    )
)
add(
    entry(
        id="appwrite",
        name="Appwrite",
        category="baas-auth",
        vendorId="appwrite-inc",
        oneLiner="可自托管的开源 BaaS",
        descriptionMd="Auth、数据库、存储与函数，可云可自建。",
        officialUrl="https://appwrite.io",
        tags=["baas", "oss", "self-host"],
        pitfalls=["自托管运维成本"],
    )
)

# ---- payment ----
add(
    entry(
        id="stripe",
        name="Stripe",
        category="payment",
        vendorId="stripe-inc",
        oneLiner="全球在线支付与订阅基础设施",
        descriptionMd="开发者体验优秀的支付平台，订阅与账单能力完善。",
        officialUrl="https://stripe.com",
        pricing={"model": "usage", "currency": "USD"},
        availability={
            "chinaAccessible": True,
            "needsCompany": True,
            "needsIcp": False,
            "regions": ["global"],
        },
        tags=["payment", "subscription"],
        maturity="mature",
        pitfalls=["需海外主体", "风控严格"],
        updates=[
            {
                "date": "2026-07-05",
                "type": "policy",
                "summary": "部分地区 KYC 更新",
                "source": "https://stripe.com/docs",
            }
        ],
    )
)
add(
    entry(
        id="wechat-pay",
        name="微信支付",
        category="payment",
        vendorId="tencent",
        region="domestic",
        oneLiner="国内主流移动支付",
        descriptionMd="覆盖公众号/小程序/APP 支付，国内用户覆盖广。",
        officialUrl="https://pay.weixin.qq.com",
        pricing={"model": "usage", "currency": "CNY"},
        availability={
            "chinaAccessible": True,
            "needsCompany": True,
            "needsIcp": False,
            "regions": ["cn"],
        },
        tags=["payment", "domestic"],
        maturity="mature",
        pitfalls=["需商户号与资质", "对接文档分散"],
    )
)
add(
    entry(
        id="alipay",
        name="支付宝",
        category="payment",
        vendorId="ant-group",
        region="domestic",
        oneLiner="国内主流综合支付",
        descriptionMd="网页/APP/小程序支付与商家服务完善。",
        officialUrl="https://open.alipay.com",
        pricing={"model": "usage", "currency": "CNY"},
        availability={
            "chinaAccessible": True,
            "needsCompany": True,
            "needsIcp": False,
            "regions": ["cn"],
        },
        tags=["payment", "domestic"],
        maturity="mature",
        pitfalls=["企业资质要求高"],
    )
)
add(
    entry(
        id="paddle",
        name="Paddle",
        category="payment",
        vendorId="paddle-inc",
        oneLiner="面向 SaaS 的 Merchant of Record",
        descriptionMd="代收税与全球合规，适合独立开发者卖软件。",
        officialUrl="https://www.paddle.com",
        pricing={"model": "usage", "currency": "USD"},
        tags=["payment", "saas", "mor"],
        pitfalls=["费率高于 Stripe", "审核周期"],
    )
)
add(
    entry(
        id="lemonsqueezy",
        name="Lemon Squeezy",
        category="payment",
        vendorId="lemon-squeezy",
        oneLiner="面向创作者的支付与税务托管",
        descriptionMd="Merchant of Record，适合卖数字商品与订阅。",
        officialUrl="https://www.lemonsqueezy.com",
        pricing={"model": "usage", "currency": "USD"},
        tags=["payment", "creator", "mor"],
        pitfalls=["品类限制", "费率不低"],
    )
)

# ---- database-storage ----
add(
    entry(
        id="postgresql",
        name="PostgreSQL",
        category="database-storage",
        oneLiner="功能强大的开源关系型数据库",
        descriptionMd="扩展丰富（含向量），是多数 BaaS 与云库的底座。",
        officialUrl="https://www.postgresql.org",
        pricing={"model": "open-source"},
        tags=["database", "sql", "oss"],
        maturity="mature",
        pitfalls=["自托管运维门槛"],
    )
)
add(
    entry(
        id="neon",
        name="Neon",
        category="database-storage",
        vendorId="neon-inc",
        oneLiner="Serverless Postgres",
        descriptionMd="分支数据库与自动休眠，适合 Serverless 应用。",
        officialUrl="https://neon.tech",
        pricing={"model": "freemium", "currency": "USD"},
        tags=["database", "postgres", "serverless"],
        pitfalls=["冷启动延迟", "厂商锁定"],
    )
)
add(
    entry(
        id="planetscale",
        name="PlanetScale",
        category="database-storage",
        vendorId="planetscale-inc",
        oneLiner="基于 Vitess 的 Serverless MySQL",
        descriptionMd="分支工作流与无感扩缩，适合高并发 MySQL 场景。",
        officialUrl="https://planetscale.com",
        pricing={"model": "freemium", "currency": "USD"},
        tags=["database", "mysql", "serverless"],
        pitfalls=["免费档变更过", "部分 SQL 限制"],
    )
)
add(
    entry(
        id="redis",
        name="Redis",
        category="database-storage",
        vendorId="redis-ltd",
        oneLiner="内存数据结构存储",
        descriptionMd="缓存、会话、队列与实时排行榜的常用底座。",
        officialUrl="https://redis.io",
        pricing={"model": "open-source"},
        tags=["cache", "kv", "oss"],
        maturity="mature",
        pitfalls=["内存成本", "持久化策略需设计"],
    )
)
add(
    entry(
        id="mongodb-atlas",
        name="MongoDB Atlas",
        category="database-storage",
        vendorId="mongodb",
        oneLiner="托管文档数据库",
        descriptionMd="灵活 schema 的文档库云服务，与 Node 生态契合。",
        officialUrl="https://www.mongodb.com/atlas",
        pricing={"model": "freemium", "currency": "USD"},
        tags=["database", "document", "cloud"],
        maturity="mature",
        pitfalls=["复杂事务不如关系库", "成本需监控"],
    )
)

# ---- edges ----
edges: list[dict] = []


def E(*args, **kwargs):
    edges.append(edge(*args, **kwargs))


# verified / structural
E("e-cursor-powered-claude", "cursor", "claude-opus", "powered_by", 0.9, "verified")
E("e-cursor-impl-mcp", "cursor", "mcp", "implements", 0.8, "verified")
E("e-claude-code-powered-claude", "claude-code", "claude-opus", "powered_by", 0.95, "verified")
E("e-openrouter-access-claude", "openrouter", "claude-opus", "provides_access_to", 0.7, "verified")
E("e-openrouter-access-gpt", "openrouter", "gpt-4o", "provides_access_to", 0.7, "verified")
E("e-azure-access-gpt", "azure-openai", "gpt-4o", "provides_access_to", 0.9, "verified")
E("e-nextjs-depends-react", "nextjs", "react", "depends_on", 1.0, "verified")
E("e-remix-depends-react", "remix", "react", "depends_on", 1.0, "verified")
E("e-nuxt-depends-vue", "nuxt", "vue", "depends_on", 1.0, "verified")
E("e-shadcn-built-react", "shadcn-ui", "react", "built_on", 0.9, "verified")
E("e-shadcn-built-radix", "shadcn-ui", "radix-ui", "built_on", 0.85, "verified")
E("e-antd-built-react", "antd", "react", "built_on", 0.9, "verified")
E("e-mantine-built-react", "mantine", "react", "built_on", 0.9, "verified")
E("e-vercel-hosts-nextjs", "vercel", "nextjs", "hosts", 0.95, "verified")
E("e-neon-built-pg", "neon", "postgresql", "built_on", 0.95, "verified")
E("e-supabase-built-pg", "supabase", "postgresql", "built_on", 0.9, "verified")

# domestic equivalents
E("e-glm-domestic-claude", "glm", "claude-opus", "domestic_equivalent_of", 0.6)
E("e-deepseek-domestic-gpt", "deepseek-v3", "gpt-4o", "domestic_equivalent_of", 0.65)
E("e-qwen-domestic-gemini", "qwen", "gemini-pro", "domestic_equivalent_of", 0.55)
E("e-trae-domestic-cursor", "trae", "cursor", "domestic_equivalent_of", 0.55)
E("e-wechatpay-domestic-stripe", "wechat-pay", "stripe", "domestic_equivalent_of", 0.7)
E("e-alipay-domestic-stripe", "alipay", "stripe", "domestic_equivalent_of", 0.65)
E("e-aliyunfc-domestic-vercel", "aliyun-fc", "vercel", "domestic_equivalent_of", 0.5)
E("e-siliconflow-domestic-openrouter", "siliconflow", "openrouter", "domestic_equivalent_of", 0.6)

# alternatives
E("e-cursor-alt-windsurf", "cursor", "windsurf", "alternative_to", 0.8, "community")
E("e-cursor-alt-continue", "cursor", "continue", "alternative_to", 0.55)
E("e-cursor-alt-claude-code", "cursor", "claude-code", "alternative_to", 0.5)
E("e-windsurf-alt-trae", "windsurf", "trae", "alternative_to", 0.45)
E("e-claude-alt-gpt", "claude-opus", "gpt-4o", "alternative_to", 0.75)
E("e-claude-alt-gemini", "claude-opus", "gemini-pro", "alternative_to", 0.65)
E("e-gpt-alt-deepseek", "gpt-4o", "deepseek-v3", "alternative_to", 0.55)
E("e-nextjs-alt-remix", "nextjs", "remix", "alternative_to", 0.7)
E("e-nextjs-alt-nuxt", "nextjs", "nuxt", "alternative_to", 0.5)
E("e-nextjs-alt-sveltekit", "nextjs", "sveltekit", "alternative_to", 0.45)
E("e-vue-alt-react", "vue", "react", "alternative_to", 0.7)
E("e-shadcn-alt-antd", "shadcn-ui", "antd", "alternative_to", 0.55)
E("e-shadcn-alt-mantine", "shadcn-ui", "mantine", "alternative_to", 0.6)
E("e-antd-alt-mantine", "antd", "mantine", "alternative_to", 0.5)
E("e-vercel-alt-netlify", "vercel", "netlify", "alternative_to", 0.75)
E("e-vercel-alt-cf", "vercel", "cloudflare-pages", "alternative_to", 0.7)
E("e-vercel-alt-railway", "vercel", "railway", "alternative_to", 0.55)
E("e-netlify-alt-cf", "netlify", "cloudflare-pages", "alternative_to", 0.65)
E("e-railway-alt-fly", "railway", "fly-io", "alternative_to", 0.7)
E("e-supabase-alt-firebase", "supabase", "firebase", "alternative_to", 0.75)
E("e-supabase-alt-appwrite", "supabase", "appwrite", "alternative_to", 0.65)
E("e-clerk-alt-auth0", "clerk", "auth0", "alternative_to", 0.7)
E("e-clerk-alt-supabase", "clerk", "supabase", "alternative_to", 0.45)
E("e-stripe-alt-paddle", "stripe", "paddle", "alternative_to", 0.65)
E("e-stripe-alt-lemon", "stripe", "lemonsqueezy", "alternative_to", 0.6)
E("e-paddle-alt-lemon", "paddle", "lemonsqueezy", "alternative_to", 0.7)
E("e-wechat-alt-alipay", "wechat-pay", "alipay", "alternative_to", 0.85)
E("e-neon-alt-planetscale", "neon", "planetscale", "alternative_to", 0.55)
E("e-neon-alt-supabase", "neon", "supabase", "alternative_to", 0.4)
E("e-openrouter-alt-litellm", "openrouter", "litellm", "alternative_to", 0.6)
E("e-openrouter-alt-oneapi", "openrouter", "one-api", "alternative_to", 0.5)
E("e-litellm-alt-oneapi", "litellm", "one-api", "alternative_to", 0.55)

# conflicts
E("e-vercel-conflicts-netlify", "vercel", "netlify", "conflicts_with", 0.4, "community", "同栈通常二选一")

# commonly_used_with / compatible
pairs_cuw = [
    ("cursor", "nextjs", 0.75),
    ("cursor", "claude-opus", 0.8),
    ("cursor", "shadcn-ui", 0.65),
    ("windsurf", "nextjs", 0.55),
    ("continue", "openrouter", 0.7),
    ("continue", "litellm", 0.65),
    ("aider", "gpt-4o", 0.6),
    ("aider", "claude-opus", 0.65),
    ("trae", "qwen", 0.55),
    ("trae", "deepseek-v3", 0.6),
    ("nextjs", "shadcn-ui", 0.85),
    ("nextjs", "supabase", 0.8),
    ("nextjs", "vercel", 0.9),
    ("nextjs", "clerk", 0.75),
    ("nextjs", "stripe", 0.7),
    ("nextjs", "neon", 0.65),
    ("remix", "fly-io", 0.55),
    ("nuxt", "cloudflare-pages", 0.5),
    ("vue", "daisyui", 0.45),
    ("supabase", "stripe", 0.65),
    ("supabase", "vercel", 0.7),
    ("clerk", "stripe", 0.55),
    ("vercel", "stripe", 0.6),
    ("railway", "postgresql", 0.7),
    ("railway", "redis", 0.55),
    ("fly-io", "redis", 0.5),
    ("openrouter", "cursor", 0.55),
    ("siliconflow", "trae", 0.5),
    ("siliconflow", "deepseek-v3", 0.7),
    ("siliconflow", "qwen", 0.65),
    ("glm", "trae", 0.5),
    ("appwrite", "cloudflare-pages", 0.4),
    ("firebase", "cloudflare-pages", 0.35),
    ("shadcn-ui", "radix-ui", 0.8),
    ("mantine", "nextjs", 0.55),
    ("antd", "nextjs", 0.5),
    ("planetscale", "nextjs", 0.55),
    ("mongodb-atlas", "railway", 0.45),
    ("paddle", "nextjs", 0.45),
    ("lemonsqueezy", "nextjs", 0.4),
    ("wechat-pay", "aliyun-fc", 0.5),
    ("alipay", "aliyun-fc", 0.5),
    ("one-api", "deepseek-v3", 0.55),
    ("one-api", "qwen", 0.55),
    ("litellm", "gpt-4o", 0.6),
    ("litellm", "claude-opus", 0.6),
    ("azure-openai", "nextjs", 0.4),
    ("auth0", "nextjs", 0.5),
    ("netlify", "supabase", 0.45),
    ("cloudflare-pages", "neon", 0.4),
    ("sveltekit", "vercel", 0.45),
    ("daisyui", "sveltekit", 0.35),
]

for a, b, w in pairs_cuw:
    E(f"e-cuw-{a}-{b}", a, b, "commonly_used_with", w)

compat = [
    ("nextjs", "vercel", 0.95),
    ("nextjs", "netlify", 0.7),
    ("nextjs", "cloudflare-pages", 0.75),
    ("supabase", "nextjs", 0.85),
    ("clerk", "nextjs", 0.9),
    ("stripe", "nextjs", 0.85),
    ("neon", "vercel", 0.7),
    ("redis", "railway", 0.7),
]
for a, b, w in compat:
    E(f"e-compat-{a}-{b}", a, b, "compatible_with", w)

# concept links
E("e-supabase-uses-rls", "supabase", "rls", "uses_concept", 0.8, "verified")
E("e-vercel-uses-serverless", "vercel", "serverless", "uses_concept", 0.7)
E("e-aliyunfc-uses-serverless", "aliyun-fc", "serverless", "uses_concept", 0.8)
E("e-cursor-uses-mcp", "cursor", "mcp", "uses_concept", 0.7)

# write files
for p in ENTRIES.glob("*.json"):
    p.unlink()

seen: set[str] = set()
for e in entries:
    assert e["id"] not in seen, e["id"]
    seen.add(e["id"])
    (ENTRIES / f"{e['id']}.json").write_text(json.dumps(e, ensure_ascii=False, indent=2) + "\n")

(ROOT / "vendors" / "seed.json").write_text(json.dumps(vendors, ensure_ascii=False, indent=2) + "\n")

concepts = [
    {
        "id": "mcp",
        "name": "Model Context Protocol (MCP)",
        "summaryMd": "模型与工具/数据源之间的标准化连接协议。",
        "aliases": ["Model Context Protocol"],
    },
    {
        "id": "rag",
        "name": "RAG",
        "summaryMd": "检索增强生成：用外部知识库提升回答准确性。",
        "aliases": ["Retrieval-Augmented Generation"],
    },
    {
        "id": "serverless",
        "name": "Serverless",
        "summaryMd": "按需计费、免运维服务器的计算范式。",
        "aliases": [],
    },
    {
        "id": "rls",
        "name": "Row Level Security",
        "summaryMd": "数据库行级安全策略，常见于 Postgres/Supabase。",
        "aliases": ["RLS"],
    },
]
(ROOT / "concepts" / "seed.json").write_text(json.dumps(concepts, ensure_ascii=False, indent=2) + "\n")

# dedupe edge ids
edge_ids = set()
unique_edges = []
for e in edges:
    if e["id"] in edge_ids:
        continue
    edge_ids.add(e["id"])
    unique_edges.append(e)
(ROOT / "edges" / "seed.json").write_text(json.dumps(unique_edges, ensure_ascii=False, indent=2) + "\n")

# second recipe
recipe_domestic = {
    "id": "domestic-miniapp-fast",
    "name": "国内小程序极速版",
    "target": "个人/小团队快速上线国内可支付的 Web/小程序后端",
    "layers": {
        "coding-agent": "trae",
        "llm": "deepseek-v3",
        "framework": "nextjs",
        "ui": "antd",
        "baas": "supabase",
        "deploy": "aliyun-fc",
        "payment": "wechat-pay",
    },
    "rationaleMd": "优先国内可访问模型与支付；部署用阿里云函数计算，收款用微信支付。",
    "estimatedCost": "月成本约 ¥50–200（视调用量）",
    "caveats": ["微信支付需商户资质", "Supabase 国内延迟需评估，可换自建 Postgres"],
}
(ROOT / "recipes" / "domestic-miniapp-fast.json").write_text(
    json.dumps(recipe_domestic, ensure_ascii=False, indent=2) + "\n"
)

print("entries", len(entries))
print(dict(sorted(Counter(e["category"] for e in entries).items())))
print("vendors", len(vendors))
print("edges", len(unique_edges))
print("concepts", len(concepts))
print("recipes", len(list((ROOT / "recipes").glob("*.json"))))
