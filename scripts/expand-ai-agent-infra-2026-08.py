#!/usr/bin/env python3
"""AI Agent 基建四叶扩种（2026-08）。

- ai-browser：浏览器自动化 / Computer Use（托管浏览器、Agent 浏览器、经典驱动）
- ai-search-api：联网检索 / 抓取 API（搜索 API、SERP 转发、抓取平台、代理池）
- ai-finetune：微调 / 训练框架（PEFT/TRL 底座、YAML/WebUI 上层、分布式、托管）
- ai-gpu-cloud：GPU 算力 / 训练平台（按小时租卡、Serverless、国内平台）

用法:
  python3 scripts/expand-ai-agent-infra-2026-08.py
  python3 scripts/expand-ai-agent-infra-2026-08.py --overwrite
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
REVIEWED = "2026-08-05"

CAT_BROWSER = "ai-browser"
CAT_SEARCH = "ai-search-api"
CAT_FINETUNE = "ai-finetune"
CAT_GPU = "ai-gpu-cloud"


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
        "tags": ["ai"],
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
    one = e["oneLiner"]
    assert 20 <= len(one) <= 58, (e["id"], len(one), one)
    desc_len = len(e.get("descriptionMd", ""))
    assert 160 <= desc_len <= 360, (e["id"], desc_len)
    assert 1 <= len(e.get("pitfalls") or []) <= 3, e["id"]
    assert e.get("subcategory"), e["id"]
    assert 3 <= len(e.get("tags") or []) <= 5, (e["id"], e.get("tags"))
    return e


def desc(what: str, when: str, caution: str) -> str:
    return f"{what}\n\n{when}\n\n{caution}\n"


def mk(cat, eid, name, sub, one, url, what, when, caution, **extra):
    pitfalls = extra.pop("pitfalls", None)
    kw = {
        "id": eid,
        "name": name,
        "category": cat,
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


GLOBAL = {
    "chinaAccessible": True,
    "needsCompany": False,
    "needsIcp": False,
    "regions": ["global"],
}

GLOBAL_ENTERPRISE = {
    "chinaAccessible": False,
    "needsCompany": True,
    "needsIcp": False,
    "regions": ["global"],
}

CARD_NEEDED = {
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

DOMESTIC_ENTERPRISE = {
    "chinaAccessible": True,
    "needsCompany": True,
    "needsIcp": False,
    "regions": ["CN"],
}


# ——————————————————————————————— ai-browser ———————————————————————————————

BROWSER_ENTRIES = [
    mk(
        CAT_BROWSER,
        "browserbase",
        "Browserbase",
        "hosted-browser",
        "托管无头浏览器会话 · 隐身代理/验证码/录屏 · 按会话时长计费",
        "https://www.browserbase.com",
        "Browserbase 把浏览器本身变成云服务：Agent 通过 API 拿到一个远端会话，代理出口、指纹隐身、会话录像与实时查看都由平台托管，本地只保留控制逻辑。",
        "当 Agent 需要长期稳定跑真实浏览器、但你不想自己维护容器与代理池时选它；它是运行层，上面的操作语义通常交给 Stagehand 或 Playwright 客户端表达。",
        "按会话时长计费，Agent 卡住不退出会持续烧钱；反爬对抗属灰色地带，抓取前需自查目标站条款。",
        vendorId="browserbase-inc",
        pricing={"model": "usage", "currency": "USD"},
        availability=CARD_NEEDED,
        tags=["ai", "browser", "automation", "cloud"],
    ),
    mk(
        CAT_BROWSER,
        "browser-use",
        "Browser Use",
        "agent-browser-oss",
        "开源 Python Agent 驱动浏览器 · 视觉+DOM 混合定位 · 可自托管",
        "https://browser-use.com",
        "Browser Use 是把浏览器交给 LLM 的开源 Python 库：它抽取页面可交互元素并配合截图让模型决定点哪里、填什么，再回放为真实操作，社区里常被当作「通用网页 Agent」的默认起点。",
        "适合任务描述模糊、页面结构无法预先写死的探索型自动化；若流程稳定且需要断言，写 Playwright 脚本更省钱也更快。",
        "每步都要喂截图与 DOM，token 成本高且延迟明显；长链路成功率不稳定，生产任务需自建重试与人工兜底。",
        vendorId="browser-use-inc",
        githubUrl="https://github.com/browser-use/browser-use",
        pricing={"model": "open-source"},
        maturity="beta",
        tags=["ai", "browser", "agent", "open-source"],
        sources=["https://browser-use.com", "https://github.com/browser-use/browser-use"],
    ),
    mk(
        CAT_BROWSER,
        "stagehand",
        "Stagehand",
        "agent-browser-oss",
        "在 Playwright 之上加自然语言动作 · AI 与代码混写 · TS 优先",
        "https://github.com/browserbase/stagehand",
        "Stagehand 由 Browserbase 开源，不另起炉灶而是包在 Playwright 外层：确定的步骤照常写代码，不确定的一步用一句自然语言描述，两种写法可在同一脚本里交替。",
        "适合已有 Playwright 资产、只想让少数易变环节由模型兜底的团队；全流程都交给模型自由发挥可看 Browser Use。",
        "自然语言步骤的结果不稳定，需要缓存动作或补断言；TypeScript 生态最完整，其他语言支持相对滞后。",
        vendorId="browserbase-inc",
        githubUrl="https://github.com/browserbase/stagehand",
        pricing={"model": "open-source"},
        maturity="beta",
        tags=["ai", "browser", "agent", "open-source"],
    ),
    mk(
        CAT_BROWSER,
        "steel-dev",
        "Steel",
        "hosted-browser",
        "开源浏览器 API · 自托管或用云端会话 · 规避单一厂商锁定",
        "https://steel.dev",
        "Steel 提供面向 Agent 的浏览器 API，同时开源了可自行部署的浏览器服务端，云端托管与私有部署共用同一套接口，属于这一层里少见的双轨形态。",
        "当数据不便出境、或想先用云端验证再迁回自有机房时优先评估；纯托管省心可看 Browserbase 与 Hyperbrowser。",
        "自托管要自己扛代理、指纹与扩容；云端配额与商业条款仍在调整期，长期方案需锁定版本。",
        vendorId="steel-inc",
        githubUrl="https://github.com/steel-dev/steel-browser",
        pricing={"model": "freemium", "currency": "USD"},
        maturity="beta",
        tags=["browser", "automation", "open-source", "self-hosted"],
        sources=["https://steel.dev", "https://github.com/steel-dev/steel-browser"],
    ),
    mk(
        CAT_BROWSER,
        "hyperbrowser",
        "Hyperbrowser",
        "hosted-browser",
        "云端浏览器池 · 并发会话/反检测/内置抓取端点 · Agent SDK",
        "https://www.hyperbrowser.ai",
        "Hyperbrowser 提供可批量并发的云端浏览器实例，除会话控制外还封装了抓取、结构化提取等现成端点，把「开浏览器」和「取数据」放进同一套 SDK。",
        "需要几十上百个会话同时跑、又不想分别接抓取 API 时评估；只要单会话精细操控，Browserbase 这类更纯粹。",
        "并发额度与套餐强绑定，超量成本上升快；平台较年轻，接口与文档变动频率高于老牌厂商。",
        vendorId="hyperbrowser-inc",
        pricing={"model": "usage", "currency": "USD"},
        availability=CARD_NEEDED,
        maturity="beta",
        tags=["ai", "browser", "automation", "cloud"],
    ),
    mk(
        CAT_BROWSER,
        "skyvern",
        "Skyvern",
        "workflow-agent",
        "视觉 LLM 跑表单流程 · 站点改版仍可执行 · 开源加云托管",
        "https://www.skyvern.com",
        "Skyvern 用视觉理解加 LLM 规划来完成登录、填表、下单这类多步网页工作流，强调不依赖写死的选择器，页面改版后仍能按目标继续推进。",
        "适合把重复的后台操作、批量申报与信息录入自动化；探索型浏览与研究类任务用通用 Agent 浏览器更顺手。",
        "涉及登录态与凭据托管，权限边界要提前设计；复杂流程仍需人工复核结果，不宜直接对接资金操作。",
        vendorId="skyvern-inc",
        githubUrl="https://github.com/Skyvern-AI/skyvern",
        pricing={"model": "freemium", "currency": "USD"},
        maturity="beta",
        tags=["ai", "browser", "agent", "rpa"],
        sources=["https://www.skyvern.com", "https://github.com/Skyvern-AI/skyvern"],
    ),
    mk(
        CAT_BROWSER,
        "puppeteer",
        "Puppeteer",
        "browser-driver",
        "Chrome DevTools 协议原生 · Node 单浏览器精控 · 生态成熟",
        "https://pptr.dev",
        "Puppeteer 是 Chrome 团队维护的 Node 浏览器控制库，直连 DevTools 协议，在性能采集、PDF 打印、拦截请求等底层控制上顺手，是很多抓取与截图服务的底座。",
        "只面向 Chromium、且以 Node 为主的场景可以继续用；要跨三种引擎并跑测试断言，Playwright 的工具链更完整。",
        "跨浏览器能力弱于后来者；等待与重试要自己写，页面异步复杂时容易出现偶发失败。",
        vendorId="google",
        githubUrl="https://github.com/puppeteer/puppeteer",
        pricing={"model": "open-source"},
        maturity="mature",
        tags=["browser", "automation", "nodejs", "open-source"],
    ),
    mk(
        CAT_BROWSER,
        "selenium",
        "Selenium",
        "browser-driver",
        "W3C WebDriver 老牌方案 · 多语言多浏览器 · Grid 分布式偏重",
        "https://www.selenium.dev",
        "Selenium 是浏览器自动化的元老，其 WebDriver 已成为 W3C 标准，覆盖 Java、Python、C# 等多语言绑定，并通过 Grid 支持大规模分布式执行。",
        "企业里已有大量历史用例、或团队栈是 Java/C# 时继续沿用最划算；新项目从零起步可直接看更现代的驱动。",
        "API 偏底层，显式等待与稳定性要自行打磨；Grid 运维成本高，调试体验落后于新一代工具。",
        vendorId=None,
        githubUrl="https://github.com/SeleniumHQ/selenium",
        pricing={"model": "open-source"},
        maturity="mature",
        tags=["browser", "automation", "testing", "open-source"],
    ),
    mk(
        CAT_BROWSER,
        "midscene",
        "Midscene.js",
        "agent-browser-oss",
        "字节开源 · 自然语言驱动 Web 与安卓 · 带可视化回放报告",
        "https://midscenejs.com",
        "Midscene.js 出自字节跳动 Web Infra 团队，用自然语言描述界面操作与断言，除浏览器外还支持安卓设备，并把每一步的模型判断生成可回放的可视化报告。",
        "国内团队做 UI 自动化或跨端验证、且希望调试过程可追溯时值得试；纯服务端抓取用无头方案更省资源。",
        "多模态模型调用带来额外费用与延迟；安卓侧对环境依赖较多，接入前先跑通设备链路。",
        vendorId="bytedance",
        githubUrl="https://github.com/web-infra-dev/midscene",
        pricing={"model": "open-source"},
        region="both",
        maturity="beta",
        tags=["ai", "browser", "testing", "open-source"],
        sources=["https://midscenejs.com", "https://github.com/web-infra-dev/midscene"],
    ),
]


# ————————————————————————————— ai-search-api —————————————————————————————

SEARCH_ENTRIES = [
    mk(
        CAT_SEARCH,
        "exa",
        "Exa",
        "neural-search",
        "自建神经索引 · 语义找页面并直接给正文 · 检索与取文分开计费",
        "https://exa.ai",
        "Exa 不转发通用搜索引擎结果，而是自建面向语义的网页索引：可以按「像这样的页面」检索，也能在一次调用里连正文一起返回，省去二次抓取。",
        "研究型检索、找相似公司或论文、给 RAG 喂长尾网页时表现突出；要的是新闻热词的实时排名，传统 SERP 更对口。",
        "索引覆盖与主流搜索引擎不同，时效性强的查询可能漏结果；检索次数与内容抓取分别计价，需分别测算。",
        vendorId="exa-labs",
        pricing={"model": "usage", "currency": "USD"},
        tags=["ai", "search", "api", "rag"],
    ),
    mk(
        CAT_SEARCH,
        "tavily",
        "Tavily",
        "agent-search",
        "为 Agent 调优的搜索 API · 直接给答案与引用片段 · 免费额度友好",
        "https://tavily.com",
        "Tavily 面向 LLM 场景重排与压缩搜索结果，返回的是可直接塞进上下文的摘要片段与来源链接，而不是让你自己去抓一堆网页再清洗。",
        "做联网问答、给 Agent 挂一个「先搜再答」工具时最省事；需要原始 SERP 排位或整站抓取则另选。",
        "结果经过平台裁剪，无法完全复现搜索引擎原貌；免费额度之外按次计费，高频轮询要设上限。",
        vendorId="tavily-inc",
        pricing={"model": "freemium", "currency": "USD"},
        tags=["ai", "search", "api", "agent"],
    ),
    mk(
        CAT_SEARCH,
        "serper",
        "Serper",
        "serp-api",
        "Google SERP 转 JSON · 低价高并发 · 只给链接摘要不含正文",
        "https://serper.dev",
        "Serper 把 Google 搜索结果页解析成结构化 JSON，主打低延迟与低单价，返回的是标题、链接与摘要，正文需要自己再抓。",
        "只需要「拿到一批相关链接」再交给抓取层处理时性价比高；要多引擎覆盖或法务背书，成熟 SERP 厂商更稳。",
        "结果依赖第三方对搜索页的解析，上游改版时可能短暂波动；不含正文，完整链路仍要配抓取工具。",
        vendorId="serper-inc",
        pricing={"model": "usage", "currency": "USD"},
        tags=["search", "api", "serp", "scraping"],
    ),
    mk(
        CAT_SEARCH,
        "serpapi",
        "SerpApi",
        "serp-api",
        "多引擎 SERP 结构化 · 谷歌/必应/地图/学术全覆盖 · 稳定性溢价",
        "https://serpapi.com",
        "SerpApi 是老牌搜索结果抓取服务，覆盖谷歌网页、图片、地图、购物、学术以及必应等多个引擎，字段解析细致且长期维护，文档与法务说明相对完备。",
        "需要地图、商品、学术等垂类 SERP，或企业对供应商合规资质有要求时选它；只要普通网页链接可用更便宜的方案。",
        "单价高于轻量竞品，大批量查询成本明显；不同引擎的字段结构差异大，切换时要重写解析。",
        vendorId="serpapi-inc",
        pricing={"model": "subscription", "currency": "USD"},
        maturity="mature",
        tags=["search", "api", "serp", "scraping"],
    ),
    mk(
        CAT_SEARCH,
        "apify",
        "Apify",
        "scrape-platform",
        "Actor 爬虫市集 · 现成抓取器开箱即跑 · 按算力与代理计费",
        "https://apify.com",
        "Apify 是爬虫托管平台，社区把针对具体站点的抓取器打包成 Actor 上架，用户既能直接调用别人写好的采集器，也能部署自己的爬虫并使用平台的代理与调度。",
        "目标站点明确且已有现成 Actor、或需要定时批量采集时最省开发；只想把任意 URL 转成干净文本，用抽取型 API 更直接。",
        "第三方 Actor 质量与维护状态参差，站点改版即失效；计费叠加算力、存储与代理，账单结构需要摸清。",
        vendorId="apify-inc",
        pricing={"model": "freemium", "currency": "USD"},
        maturity="mature",
        tags=["scraping", "api", "platform", "crawler"],
    ),
    mk(
        CAT_SEARCH,
        "bright-data",
        "Bright Data",
        "proxy-network",
        "大规模代理 IP 池 · 住宅与机房出口 · 企业合规但门槛偏高",
        "https://brightdata.com",
        "Bright Data 的核心资产是覆盖广泛的代理网络与配套的解锁、抓取产品，面向需要长期、大体量采集的企业客户，合规审查与账户尽调流程也更正式。",
        "当抓取规模大到必须自建 IP 策略、或行业要求供应商可审计时进入视野；小团队做几千次调用属于杀鸡用牛刀。",
        "住宅代理来源与用途争议长期存在，用途需自查合规；起步价与最低消费对小团队不友好。",
        vendorId="bright-data-inc",
        pricing={"model": "subscription", "currency": "USD"},
        availability=GLOBAL_ENTERPRISE,
        maturity="mature",
        tags=["scraping", "proxy", "enterprise", "data"],
    ),
    mk(
        CAT_SEARCH,
        "crawl4ai",
        "Crawl4AI",
        "web-scrape-llm",
        "开源抓取库 · 输出 LLM 友好 markdown · 自托管零调用费",
        "https://github.com/unclecode/crawl4ai",
        "Crawl4AI 是 Python 开源抓取框架，内置无头浏览器渲染、正文清洗与 markdown 输出，还支持按 schema 做结构化提取，定位就是给 RAG 与 Agent 供料。",
        "调用量大到 API 计费不划算、或语料不便经过第三方时自托管它；不想管代理与反爬运维则用托管服务省心。",
        "反爬对抗、代理与失败重试全要自己维护；抓取吞吐受本机资源限制，规模化需自建队列与调度。",
        vendorId=None,
        githubUrl="https://github.com/unclecode/crawl4ai",
        pricing={"model": "open-source"},
        maturity="beta",
        tags=["scraping", "rag", "open-source", "python"],
    ),
    mk(
        CAT_SEARCH,
        "scrapingbee",
        "ScrapingBee",
        "scrape-api",
        "抓取 API 代管代理与渲染 · 返回原始 HTML · 计费口径简单",
        "https://www.scrapingbee.com",
        "ScrapingBee 把代理轮换、JS 渲染与重试封装成一个请求参数化的 API，给一个 URL 返回渲染后的 HTML 或截图，解析与清洗留给调用方。",
        "已有成熟解析逻辑、只缺一个稳定出口时接入最快；要直接拿到干净 markdown 喂模型，抽取型服务更省一步。",
        "返回原始 HTML，正文清洗成本仍在自己这边；按请求计费，渲染类请求消耗更高需注意配置。",
        vendorId="scrapingbee-inc",
        pricing={"model": "subscription", "currency": "USD"},
        tags=["scraping", "api", "proxy", "html"],
    ),
    mk(
        CAT_SEARCH,
        "bocha-search",
        "博查搜索",
        "domestic-search",
        "国内联网检索 API · 中文网页与垂类语料 · 人民币计费无需出海",
        "https://bochaai.com",
        "博查（Bocha）面向国内开发者提供搜索与网页内容 API，覆盖中文网页及部分垂类内容，接口形态贴近给大模型做联网检索的用法。",
        "国内产品要给模型加联网能力、又受限于境外服务的支付与网络时，它是常见的第一选择；中文语料覆盖也比海外引擎更贴合。",
        "英文与海外站点覆盖不及国际引擎；配额与字段定义以控制台为准，跨境业务建议与海外搜索 API 双路兜底。",
        vendorId="bocha-ai",
        pricing={"model": "usage", "currency": "CNY"},
        availability=DOMESTIC,
        region="domestic",
        maturity="beta",
        tags=["search", "api", "domestic", "rag"],
    ),
]


# —————————————————————————————— ai-finetune ——————————————————————————————

FINETUNE_ENTRIES = [
    mk(
        CAT_FINETUNE,
        "unsloth",
        "Unsloth",
        "efficient-training",
        "单卡 LoRA 提速省显存 · 手写算子重写反传 · 消费级显卡也能跑",
        "https://unsloth.ai",
        "Unsloth 通过手写内核与重写反向传播，把常见开源模型的 LoRA/QLoRA 微调做得更省显存、更快，配套的 Colab 笔记本让单卡起步的门槛很低。",
        "手头只有一两张消费卡、想先把微调链路跑通时首选；多机多卡的大规模训练仍应回到分布式框架。",
        "深度优化意味着对模型架构适配有先后，新模型支持需等上游跟进；多卡与集群能力弱于通用训练框架。",
        vendorId="unsloth-ai",
        githubUrl="https://github.com/unslothai/unsloth",
        pricing={"model": "open-source"},
        tags=["ai", "finetune", "lora", "open-source"],
        sources=["https://unsloth.ai", "https://github.com/unslothai/unsloth"],
    ),
    mk(
        CAT_FINETUNE,
        "axolotl",
        "Axolotl",
        "training-framework",
        "YAML 配置驱动微调 · 全参/LoRA/QLoRA 齐备 · 多卡脚本成熟",
        "https://github.com/axolotl-ai-cloud/axolotl",
        "Axolotl 用一份 YAML 描述模型、数据集、训练策略与并行方式，把 Transformers 生态的训练细节收敛成可版本化的配置，社区里长期是复现实验的常用底座。",
        "需要把多组微调实验管起来、并在多卡环境反复跑时选它；只想在单卡上快速试一版，轻量方案上手更快。",
        "配置项繁多，参数组合错误往往到训练中段才暴露；环境依赖较重，升级时容易出现版本冲突。",
        vendorId="axolotl-ai",
        githubUrl="https://github.com/axolotl-ai-cloud/axolotl",
        pricing={"model": "open-source"},
        tags=["ai", "finetune", "training", "open-source"],
    ),
    mk(
        CAT_FINETUNE,
        "llama-factory",
        "LLaMA-Factory",
        "training-framework",
        "Web UI 点选微调 · 上百模型模板内置 · 中文社区文档厚",
        "https://github.com/hiyouga/LLaMA-Factory",
        "LLaMA-Factory 把主流开源模型的微调、对齐与评测收进统一框架，既能命令行跑也提供可视化界面，内置大量模型与数据集模板，中文资料尤其丰富。",
        "团队里有人不写训练代码、或需要快速覆盖多个国产与开源模型做对比时很合适；追求极致吞吐仍看底层框架。",
        "界面便利掩盖了超参细节，出问题需回到日志排查；模板众多但更新节奏不一，冷门模型分支质量参差。",
        vendorId=None,
        githubUrl="https://github.com/hiyouga/LLaMA-Factory",
        pricing={"model": "open-source"},
        region="both",
        tags=["ai", "finetune", "training", "open-source"],
    ),
    mk(
        CAT_FINETUNE,
        "hf-peft",
        "PEFT",
        "training-library",
        "参数高效微调库 · LoRA/QLoRA 等适配器统一接口 · 生态底座",
        "https://github.com/huggingface/peft",
        "PEFT 是 Hugging Face 的参数高效微调库，把 LoRA、QLoRA、前缀微调等方法收进一致的接口，只训练少量新增参数并单独保存适配器权重。",
        "自己写训练循环、或想弄清上层框架到底做了什么时直接用它；要开箱即用的完整流程，选上层封装更省事。",
        "只解决「怎么改模型」，数据处理与训练调度仍要自己搭；适配器合并与推理加载方式需按部署侧要求确认。",
        vendorId="huggingface",
        githubUrl="https://github.com/huggingface/peft",
        pricing={"model": "open-source"},
        maturity="mature",
        tags=["ai", "finetune", "lora", "open-source"],
    ),
    mk(
        CAT_FINETUNE,
        "hf-trl",
        "TRL",
        "training-library",
        "后训练算法库 · SFT/DPO/GRPO 一套 API · 对齐训练常用底座",
        "https://github.com/huggingface/trl",
        "TRL 提供监督微调与偏好对齐的训练器，把 SFT、DPO、GRPO 等后训练方法封装成一致用法，是 Transformers 生态里做对齐与强化学习实验的常用起点。",
        "要在指令微调之外再做偏好对齐、或复现论文里的对齐方法时用它；只做单纯的领域适配，参数高效微调就够。",
        "对齐训练对数据质量与超参极敏感，效果波动大；算法迭代快，示例代码常需跟随版本调整。",
        vendorId="huggingface",
        githubUrl="https://github.com/huggingface/trl",
        pricing={"model": "open-source"},
        tags=["ai", "finetune", "rlhf", "open-source"],
    ),
    mk(
        CAT_FINETUNE,
        "deepspeed",
        "DeepSpeed",
        "distributed-training",
        "ZeRO 分片省显存 · 支撑千卡级并行 · 偏底层需要调参经验",
        "https://www.deepspeed.ai",
        "DeepSpeed 由微软开源，核心是 ZeRO 系列显存优化：把优化器状态、梯度与参数在多卡间分片，再配合卸载与混合精度，让超出单卡容量的模型也能训练。",
        "参数量或批大小已经撑爆显存、需要多机扩展时引入；单卡小规模微调用它反而增加复杂度。",
        "配置文件与通信参数调优门槛高；卸载到内存或硬盘虽省显存，但吞吐下降需要实测权衡。",
        vendorId="microsoft",
        pricing={"model": "open-source"},
        maturity="mature",
        tags=["ai", "training", "distributed", "open-source"],
    ),
    mk(
        CAT_FINETUNE,
        "ms-swift",
        "ms-swift",
        "training-framework",
        "魔搭出品全流程 · 训练到部署一条命令 · 国产模型适配齐全",
        "https://github.com/modelscope/ms-swift",
        "ms-swift 是魔搭社区的大模型训练与部署框架，覆盖微调、对齐、量化到推理部署的完整链路，对国内开源模型与多模态模型的适配跟进较快。",
        "主力使用国产开源模型、或已在魔搭生态里管理模型与数据集时最顺；纯英文社区模型的资料仍以海外框架更多。",
        "功能面铺得广，单点深度不一定优于专精工具；版本迭代快，训练脚本需固定版本以保证可复现。",
        vendorId="modelscope",
        githubUrl="https://github.com/modelscope/ms-swift",
        pricing={"model": "open-source"},
        region="both",
        tags=["ai", "finetune", "domestic", "open-source"],
    ),
    mk(
        CAT_FINETUNE,
        "openpipe",
        "OpenPipe",
        "managed-finetune",
        "托管微调加数据回流 · 用生产日志蒸馏小模型 · 按用量计费",
        "https://openpipe.ai",
        "OpenPipe 把线上调用日志沉淀为训练集，再托管完成微调与部署，典型用法是用大模型的输出蒸馏出一个更便宜的小模型来接管稳定流量。",
        "已有大模型跑在生产、想把重复请求换成自训小模型省成本时评估；从零开始的研究性训练用开源框架更自由。",
        "训练数据来自生产日志，脱敏与合规要先做；模型与权重的可迁移性需在签约前确认，避免后续锁仓。",
        vendorId="openpipe-inc",
        pricing={"model": "usage", "currency": "USD"},
        availability=CARD_NEEDED,
        maturity="beta",
        tags=["ai", "finetune", "managed", "distillation"],
    ),
]


# —————————————————————————————— ai-gpu-cloud ——————————————————————————————

GPU_ENTRIES = [
    mk(
        CAT_GPU,
        "runpod",
        "RunPod",
        "gpu-rental",
        "按秒计费 GPU 容器 · Serverless 与常驻实例双形态 · 社区卡便宜",
        "https://www.runpod.io",
        "RunPod 以容器方式出租 GPU，既有开机即用的常驻实例，也有按请求扩缩的 Serverless 端点，并区分自营机房与社区节点两档价格与可靠性。",
        "个人和小团队做微调、批量推理或临时压测时上手最快；企业级 SLA 与长期容量承诺仍要看专业 GPU 云。",
        "社区节点可能随时被回收，重要任务需勤存检查点；镜像与网络存储另计费，长期挂载成本容易被忽略。",
        vendorId="runpod-inc",
        pricing={"model": "usage", "currency": "USD"},
        tags=["gpu", "cloud", "serverless", "training"],
    ),
    mk(
        CAT_GPU,
        "lambda-labs",
        "Lambda",
        "gpu-cloud",
        "AI 专用云 · 预装深度学习栈 · 按需实例与整柜集群并行",
        "https://lambda.ai",
        "Lambda 长期做深度学习工作站与服务器，云上延续同一套预装环境，从单卡按需实例到成规模的训练集群都提供，交付形态偏向研究与训练场景。",
        "需要稳定的多卡机器跑几天到几周的训练、且希望环境开箱可用时评估；短平快的弹性任务用按秒计费平台更灵活。",
        "热门型号常需排队或预留，临时扩容不一定拿得到；按需实例价格高于竞价市集，长期用应谈预留。",
        vendorId="lambda-labs-inc",
        pricing={"model": "usage", "currency": "USD"},
        availability=CARD_NEEDED,
        maturity="mature",
        tags=["gpu", "cloud", "training", "infra"],
    ),
    mk(
        CAT_GPU,
        "vast-ai",
        "Vast.ai",
        "gpu-marketplace",
        "GPU 竞价市集 · 散户机器价格极低 · 可靠性靠评分自行筛选",
        "https://vast.ai",
        "Vast.ai 是 GPU 算力的撮合市场，供给方既有数据中心也有个人机器，价格由竞价决定，平台用可靠性评分、带宽与硬件参数帮助买方筛选。",
        "预算敏感、任务可中断的实验与批处理最划算；对合规、网络与稳定性有硬要求的生产负载不适合。",
        "机器质量与网络差异极大，需按评分和实测挑选；竞价实例可能被抢占，务必自建检查点与重试。",
        vendorId="vast-ai-inc",
        pricing={"model": "usage", "currency": "USD"},
        availability=CARD_NEEDED,
        tags=["gpu", "cloud", "marketplace", "budget"],
    ),
    mk(
        CAT_GPU,
        "coreweave",
        "CoreWeave",
        "gpu-cloud",
        "企业级 GPU 云 · 大规模高速互联集群 · 面向长约容量交付",
        "https://www.coreweave.com",
        "CoreWeave 面向大模型训练与规模化推理提供专用 GPU 基础设施，强调高速互联、集群编排与容量规划，客户多为模型厂商与大型企业。",
        "训练规模到了需要成百上千张卡、并要谈长期容量与 SLA 时进入选型；十几张卡的实验用零售型平台更省事。",
        "以合同与预留容量为主，缺少即开即用的自助体验；起量门槛与承诺周期对中小团队不友好。",
        vendorId="coreweave-inc",
        pricing={"model": "usage", "currency": "USD"},
        availability=GLOBAL_ENTERPRISE,
        maturity="mature",
        tags=["gpu", "cloud", "enterprise", "training"],
    ),
    mk(
        CAT_GPU,
        "paperspace",
        "Paperspace",
        "gpu-rental",
        "Notebook 起步的 GPU 云 · 已并入 DigitalOcean · 上手门槛低",
        "https://www.paperspace.com",
        "Paperspace 提供托管 Notebook 与 GPU 虚拟机，界面友好、模板齐全，被 DigitalOcean 收购后逐步与其云产品线整合。",
        "教学、原型验证或希望在浏览器里直接开工时体验最好；追求最低单价或极致弹性的生产任务另择平台。",
        "GPU 型号与库存不如专业 GPU 云丰富；产品线整合期间入口与套餐仍在调整，长期方案需确认承接关系。",
        vendorId="paperspace-inc",
        pricing={"model": "freemium", "currency": "USD"},
        availability=CARD_NEEDED,
        tags=["gpu", "cloud", "notebook", "prototyping"],
    ),
    mk(
        CAT_GPU,
        "autodl",
        "AutoDL",
        "domestic-gpu",
        "国内按小时租卡 · 深度学习镜像齐备 · 无需海外支付与网络",
        "https://www.autodl.com",
        "AutoDL 是国内常见的 GPU 租用平台，按小时计费，提供预装框架的镜像与数据盘，学生与研究者用来跑训练和复现实验的比例很高。",
        "国内做微调、跑论文代码、临时借几张卡时最省事，支付与网络都不用绕路；企业级 SLA 与大规模集群不在其强项。",
        "热门卡型高峰期常无库存，需守候或换区；实例回收与数据盘计费规则要提前看清，避免作业中断。",
        vendorId="autodl-inc",
        pricing={"model": "usage", "currency": "CNY"},
        availability=DOMESTIC,
        region="domestic",
        tags=["gpu", "cloud", "domestic", "training"],
    ),
    mk(
        CAT_GPU,
        "gongji-suanli",
        "共绩算力",
        "domestic-gpu",
        "国内弹性算力平台 · 聚合闲时资源压价 · 容器与推理托管并行",
        "https://www.gongjiyun.com",
        "共绩算力把闲置与错峰的 GPU 资源聚合起来对外出租，支持容器化部署与模型推理托管，价格策略主打错峰低价，是国内这一层里较活跃的新玩家。",
        "国内团队做可中断的批量推理、临时训练或成本敏感的实验时值得比价；关键在线业务仍建议放在大厂云上。",
        "资源池由多方拼接，稳定性与可用区不如自建机房；长期作业需评估回收策略并做好检查点。",
        vendorId="gongji-tech",
        pricing={"model": "usage", "currency": "CNY"},
        availability=DOMESTIC,
        region="domestic",
        maturity="beta",
        tags=["gpu", "cloud", "domestic", "inference"],
    ),
    mk(
        CAT_GPU,
        "nebius",
        "Nebius",
        "gpu-cloud",
        "欧洲 AI 云 · 自建数据中心整机柜交付 · 偏长周期训练任务",
        "https://nebius.com",
        "Nebius 在欧洲自建数据中心提供 AI 专用云，围绕 GPU 集群配套存储、编排与托管服务，面向需要在欧盟境内完成训练与数据落地的客户。",
        "有数据驻留在欧洲的合规要求、或想在北美供给紧张时找替代产能时评估；小规模零散用卡不是它的主场。",
        "亚太区域延迟与可用区选择有限；合同与配额审批流程偏企业化，起步节奏慢于零售平台。",
        vendorId="nebius-inc",
        pricing={"model": "usage", "currency": "USD"},
        availability=GLOBAL_ENTERPRISE,
        tags=["gpu", "cloud", "europe", "training"],
    ),
    mk(
        CAT_GPU,
        "crusoe",
        "Crusoe",
        "gpu-cloud",
        "能源侧自建 AI 云 · 就地取电降碳降本 · 大规模训练容量导向",
        "https://crusoe.ai",
        "Crusoe 把算力部署在能源产地，用就地供电支撑 GPU 集群，主打成本与碳排放优势，产品形态是面向训练与推理的规模化 AI 云。",
        "长期大批量训练、电费在总成本里占比高、或需要向上游交代碳排指标的团队值得询价；临时借几张卡请用零售型平台。",
        "站点选址特殊，网络与区域覆盖不如超大规模云；以企业合同为主，自助开通体验有限，起量门槛偏高。",
        vendorId="crusoe-inc",
        pricing={"model": "usage", "currency": "USD"},
        availability=GLOBAL_ENTERPRISE,
        tags=["gpu", "cloud", "enterprise", "sustainability"],
    ),
    mk(
        CAT_GPU,
        "aliyun-pai",
        "阿里云 PAI",
        "domestic-platform",
        "阿里云一体化训练平台 · 数据到部署打通 · 走企业采购路径",
        "https://www.aliyun.com",
        "阿里云 PAI 是机器学习平台产品，把数据准备、交互式建模、分布式训练与在线服务串成一条流水线，并与阿里云的存储、网络与账号体系深度打通。",
        "企业已在阿里云上、需要合规可审计的训练与部署流水线时是自然选择；只想按小时借卡跑个实验会显得偏重。",
        "与阿里云生态耦合深，迁出成本高；计费维度多且需企业实名与配额申请，个人试水门槛偏高。",
        vendorId="aliyun",
        pricing={"model": "usage", "currency": "CNY"},
        availability=DOMESTIC_ENTERPRISE,
        region="domestic",
        maturity="mature",
        tags=["gpu", "cloud", "domestic", "mlops"],
    ),
]


ENTRIES_DATA: list[dict] = BROWSER_ENTRIES + SEARCH_ENTRIES + FINETUNE_ENTRIES + GPU_ENTRIES


VENDORS_DATA: list[dict] = [
    vendor("browserbase-inc", "Browserbase", url="https://www.browserbase.com"),
    vendor("browser-use-inc", "Browser Use", url="https://browser-use.com"),
    vendor("steel-inc", "Steel", url="https://steel.dev"),
    vendor("hyperbrowser-inc", "Hyperbrowser", url="https://www.hyperbrowser.ai"),
    vendor("skyvern-inc", "Skyvern", url="https://www.skyvern.com"),
    vendor("exa-labs", "Exa", url="https://exa.ai"),
    vendor("tavily-inc", "Tavily", url="https://tavily.com"),
    vendor("serper-inc", "Serper", url="https://serper.dev"),
    vendor("serpapi-inc", "SerpApi", url="https://serpapi.com"),
    vendor("apify-inc", "Apify", url="https://apify.com"),
    vendor("bright-data-inc", "Bright Data", url="https://brightdata.com"),
    vendor("scrapingbee-inc", "ScrapingBee", url="https://www.scrapingbee.com"),
    vendor("bocha-ai", "博查 AI", region="domestic", url="https://bochaai.com"),
    vendor("unsloth-ai", "Unsloth AI", url="https://unsloth.ai"),
    vendor("axolotl-ai", "Axolotl AI", url="https://axolotl.ai"),
    vendor("modelscope", "魔搭社区 ModelScope", region="domestic", url="https://modelscope.cn"),
    vendor("openpipe-inc", "OpenPipe", url="https://openpipe.ai"),
    vendor("runpod-inc", "RunPod", url="https://www.runpod.io"),
    vendor("lambda-labs-inc", "Lambda", url="https://lambda.ai"),
    vendor("vast-ai-inc", "Vast.ai", url="https://vast.ai"),
    vendor("coreweave-inc", "CoreWeave", url="https://www.coreweave.com"),
    vendor("paperspace-inc", "Paperspace", url="https://www.paperspace.com"),
    vendor("autodl-inc", "AutoDL", region="domestic", url="https://www.autodl.com"),
    vendor("gongji-tech", "共绩科技", region="domestic", url="https://www.gongjiyun.com"),
    vendor("nebius-inc", "Nebius", url="https://nebius.com"),
    vendor("crusoe-inc", "Crusoe", url="https://crusoe.ai"),
]


EDGES_DATA: list[dict] = [
    # ——— ai-browser 内部与跨叶 ———
    edge(
        "e-stagehand-built-playwright",
        "stagehand",
        "playwright",
        "built_on",
        weight=0.85,
        note="Stagehand 是 Playwright 的外层封装：原有 API 仍可用，自然语言步骤只是额外一层",
    ),
    edge(
        "e-browser-use-built-playwright",
        "browser-use",
        "playwright",
        "built_on",
        weight=0.8,
        note="底层用 Playwright 驱动真实浏览器，上层由 LLM 决定每一步动作",
    ),
    edge(
        "e-stagehand-cuw-browserbase",
        "stagehand",
        "browserbase",
        "commonly_used_with",
        weight=0.8,
        note="同一家出品：Stagehand 表达操作语义，Browserbase 提供托管会话与出口 IP",
    ),
    edge(
        "e-browser-use-alt-stagehand",
        "browser-use",
        "stagehand",
        "alternative_to",
        note="全流程交给模型自主决策 vs 保留 Playwright 代码、只在易变处插自然语言",
    ),
    edge(
        "e-steel-dev-osalt-browserbase",
        "steel-dev",
        "browserbase",
        "open_source_alternative_to",
        weight=0.75,
        note="Steel 的浏览器服务端可自托管，适合数据不便出境；Browserbase 只提供托管形态",
    ),
    edge(
        "e-hyperbrowser-alt-browserbase",
        "hyperbrowser",
        "browserbase",
        "alternative_to",
        note="偏高并发会话池并自带抓取端点 vs 偏单会话精细控制与观测",
    ),
    edge(
        "e-skyvern-alt-browser-use",
        "skyvern",
        "browser-use",
        "alternative_to",
        note="视觉驱动的固定业务流程（登录/填表/下单）vs 目标模糊的探索型网页 Agent",
    ),
    edge(
        "e-puppeteer-alt-selenium",
        "puppeteer",
        "selenium",
        "alternative_to",
        note="Node 单栈直连 DevTools 协议 vs 多语言绑定的 W3C WebDriver 标准实现",
    ),
    edge(
        "e-puppeteer-alt-playwright",
        "puppeteer",
        "playwright",
        "alternative_to",
        weight=0.8,
        note="只管 Chromium、偏底层控制 vs 三引擎覆盖并自带 auto-wait、trace 等测试工具链",
    ),
    edge(
        "e-midscene-alt-browser-use",
        "midscene",
        "browser-use",
        "alternative_to",
        note="字节开源、TS 生态且覆盖安卓并产出可视化报告 vs Python 生态的通用网页 Agent",
    ),
    edge(
        "e-midscene-igw-playwright",
        "midscene",
        "playwright",
        "integrates_with",
        weight=0.75,
        note="可接入既有 Playwright 用例，把难写的断言与定位换成自然语言描述",
    ),
    edge(
        "e-browser-use-cuw-langchain",
        "browser-use",
        "langchain",
        "commonly_used_with",
        weight=0.55,
        note="常被包成编排框架里的「浏览器工具」，由 LangChain 侧负责多工具调度",
    ),
    edge(
        "e-browserbase-cuw-firecrawl",
        "browserbase",
        "firecrawl",
        "commonly_used_with",
        weight=0.5,
        note="需要登录态与多步交互时用托管会话，只要把公开页转成正文时用抽取 API",
    ),
    edge(
        "e-browserbase-cuw-claude-code",
        "browserbase",
        "claude-code",
        "commonly_used_with",
        weight=0.45,
        note="通过 MCP 把远端浏览器会话挂给编码 Agent，用于联调与端到端验证",
    ),
    # ——— ai-search-api 内部与跨叶 ———
    edge(
        "e-exa-alt-tavily",
        "exa",
        "tavily",
        "alternative_to",
        note="自建语义索引、能连正文一起返回 vs 对结果做压缩重排、直接给可入上下文的片段",
    ),
    edge(
        "e-serper-alt-serpapi",
        "serper",
        "serpapi",
        "alternative_to",
        note="单引擎低价高并发 vs 多引擎垂类覆盖与更正式的合规说明，单价更高",
    ),
    edge(
        "e-serper-alt-exa",
        "serper",
        "exa",
        "alternative_to",
        weight=0.65,
        note="转发主流搜索引擎的排位结果 vs 自建索引按语义召回，两者覆盖面不同",
    ),
    edge(
        "e-crawl4ai-osalt-firecrawl",
        "crawl4ai",
        "firecrawl",
        "open_source_alternative_to",
        weight=0.85,
        note="同为 URL 转 markdown 供 RAG，自托管零调用费，但代理与反爬运维要自己扛",
    ),
    edge(
        "e-apify-alt-bright-data",
        "apify",
        "bright-data",
        "alternative_to",
        note="现成爬虫市集与托管调度 vs 以代理 IP 网络为核心的企业级采集基建",
    ),
    edge(
        "e-scrapingbee-alt-apify",
        "scrapingbee",
        "apify",
        "alternative_to",
        weight=0.65,
        note="单点抓取 API、计费简单 vs 平台化的 Actor 生态与定时调度",
    ),
    edge(
        "e-scrapingbee-alt-firecrawl",
        "scrapingbee",
        "firecrawl",
        "alternative_to",
        note="返回渲染后的原始 HTML 由你解析 vs 直接给清洗过的 markdown 与结构化字段",
    ),
    edge(
        "e-bocha-search-deq-tavily",
        "bocha-search",
        "tavily",
        "domestic_equivalent_of",
        weight=0.8,
        note="国内联网检索 API，中文覆盖更好、人民币计费，免去跨境支付与网络问题",
    ),
    edge(
        "e-tavily-igw-langchain",
        "tavily",
        "langchain",
        "integrates_with",
        weight=0.7,
        note="以现成检索工具的形式接入编排框架，是「先搜再答」链路的常见默认项",
    ),
    edge(
        "e-exa-igw-llamaindex",
        "exa",
        "llamaindex",
        "integrates_with",
        weight=0.65,
        note="作为外部检索源接入索引与查询管线，补足本地向量库覆盖不到的长尾网页",
    ),
    edge(
        "e-crawl4ai-igw-llamaindex",
        "crawl4ai",
        "llamaindex",
        "integrates_with",
        weight=0.6,
        note="抓取产出的 markdown 直接进切分与索引流程，负责 ingest 的最前一段",
    ),
    edge(
        "e-apify-igw-playwright",
        "apify",
        "playwright",
        "integrates_with",
        weight=0.6,
        note="平台的爬虫运行时支持 Playwright 编写采集器，本地脚本可迁到托管环境",
    ),
    edge(
        "e-tavily-cuw-firecrawl",
        "tavily",
        "firecrawl",
        "commonly_used_with",
        weight=0.6,
        note="搜索层负责找到候选链接，抓取层负责把选中的页面转成干净正文",
    ),
    edge(
        "e-exa-cuw-claude-code",
        "exa",
        "claude-code",
        "commonly_used_with",
        weight=0.45,
        note="通过 MCP 给编码 Agent 补一个联网检索工具，用于查文档与依赖变更",
    ),
    # ——— ai-finetune 内部与跨叶 ———
    edge(
        "e-unsloth-alt-axolotl",
        "unsloth",
        "axolotl",
        "alternative_to",
        note="单卡极致提速省显存 vs 配置化管理多组实验、多卡与全参训练更成熟",
    ),
    edge(
        "e-axolotl-alt-llama-factory",
        "axolotl",
        "llama-factory",
        "alternative_to",
        note="YAML 配置面向工程复现 vs Web UI 与模板降低门槛、中文资料更多",
    ),
    edge(
        "e-ms-swift-alt-llama-factory",
        "ms-swift",
        "llama-factory",
        "alternative_to",
        note="同为国内主力框架：ms-swift 打通训练到部署且贴魔搭生态，后者胜在上手与模板",
    ),
    edge(
        "e-unsloth-dep-hf-peft",
        "unsloth",
        "hf-peft",
        "depends_on",
        weight=0.75,
        note="沿用 PEFT 的适配器体系，产出的 LoRA 权重可在通用生态里加载",
    ),
    edge(
        "e-llama-factory-dep-hf-peft",
        "llama-factory",
        "hf-peft",
        "depends_on",
        weight=0.8,
        note="参数高效微调能力来自 PEFT，框架主要负责数据、模板与训练调度",
    ),
    edge(
        "e-axolotl-dep-hf-trl",
        "axolotl",
        "hf-trl",
        "depends_on",
        weight=0.75,
        note="SFT 与偏好对齐的训练器来自 TRL，Axolotl 用配置把它们串起来",
    ),
    edge(
        "e-hf-trl-cuw-hf-peft",
        "hf-trl",
        "hf-peft",
        "commonly_used_with",
        weight=0.85,
        note="同一生态的两层：TRL 决定用什么后训练算法，PEFT 决定改模型的哪部分参数",
    ),
    edge(
        "e-llama-factory-igw-deepspeed",
        "llama-factory",
        "deepspeed",
        "integrates_with",
        weight=0.7,
        note="多卡训练可切到 ZeRO 分片，显存不够时不必改训练代码",
    ),
    edge(
        "e-axolotl-igw-deepspeed",
        "axolotl",
        "deepspeed",
        "integrates_with",
        weight=0.7,
        note="并行策略在配置里声明即可启用，全参训练时常搭配使用",
    ),
    edge(
        "e-openpipe-alt-together-ai",
        "openpipe",
        "together-ai",
        "alternative_to",
        weight=0.6,
        note="围绕生产日志做蒸馏闭环 vs 开源模型托管厂商顺带提供的微调能力",
    ),
    edge(
        "e-unsloth-cuw-ollama",
        "unsloth",
        "ollama",
        "commonly_used_with",
        weight=0.6,
        note="训练与推理分工：微调产出的权重导出后交给本地推理端加载运行",
    ),
    edge(
        "e-llama-factory-cuw-vllm",
        "llama-factory",
        "vllm",
        "commonly_used_with",
        weight=0.65,
        note="训练侧产出权重、推理侧负责高吞吐 serving，两者不要放在同一层比较",
    ),
    edge(
        "e-hf-peft-cuw-huggingface-inference",
        "hf-peft",
        "huggingface-inference",
        "commonly_used_with",
        weight=0.55,
        note="同一生态的训练与推理两端：适配器权重推回 Hub 后可直接部署为端点",
    ),
    edge(
        "e-unsloth-cuw-runpod",
        "unsloth",
        "runpod",
        "commonly_used_with",
        weight=0.6,
        note="没有本地显卡时的常见组合：按小时租一张卡跑完微调即释放",
    ),
    # ——— ai-gpu-cloud 内部与跨叶 ———
    edge(
        "e-runpod-alt-vast-ai",
        "runpod",
        "vast-ai",
        "alternative_to",
        note="平台自营与社区节点分档、体验统一 vs 纯竞价市集、更便宜但需自行筛机器",
    ),
    edge(
        "e-paperspace-alt-runpod",
        "paperspace",
        "runpod",
        "alternative_to",
        note="Notebook 优先、适合教学与原型 vs 容器与 Serverless 优先、按秒计费更灵活",
    ),
    edge(
        "e-lambda-labs-alt-coreweave",
        "lambda-labs",
        "coreweave",
        "alternative_to",
        note="面向研究团队的预装环境与中等规模集群 vs 面向模型厂商的大规模长约容量",
    ),
    edge(
        "e-nebius-alt-coreweave",
        "nebius",
        "coreweave",
        "alternative_to",
        weight=0.65,
        note="欧洲自建机房、满足数据驻留要求 vs 北美为主的规模化 GPU 供给",
    ),
    edge(
        "e-crusoe-alt-coreweave",
        "crusoe",
        "coreweave",
        "alternative_to",
        weight=0.6,
        note="能源产地就地建站、主打电价与碳排 vs 以互联与集群规模为卖点",
    ),
    edge(
        "e-runpod-alt-modal",
        "runpod",
        "modal",
        "alternative_to",
        weight=0.7,
        note="租容器与实例、自己管进程 vs 把 Python 函数部署成按调用伸缩的 Serverless",
    ),
    edge(
        "e-runpod-alt-together-ai",
        "runpod",
        "together-ai",
        "alternative_to",
        weight=0.6,
        note="按小时租卡自建服务 vs 按 token 调现成 API：前者边际成本低、后者零运维",
    ),
    edge(
        "e-autodl-deq-vast-ai",
        "autodl",
        "vast-ai",
        "domestic_equivalent_of",
        weight=0.75,
        note="国内按小时租卡、镜像与支付本地化，无需跨境网络；规模与型号选择更有限",
    ),
    edge(
        "e-gongji-suanli-deq-runpod",
        "gongji-suanli",
        "runpod",
        "domestic_equivalent_of",
        weight=0.7,
        note="国内的容器化弹性算力与推理托管，靠错峰聚合压价，稳定性需自行兜底",
    ),
    edge(
        "e-aliyun-pai-deq-coreweave",
        "aliyun-pai",
        "coreweave",
        "domestic_equivalent_of",
        weight=0.55,
        note="国内企业级训练平台的对应位；PAI 额外打包数据与流水线，口径并非完全等同",
    ),
    edge(
        "e-runpod-cuw-vllm",
        "runpod",
        "vllm",
        "commonly_used_with",
        weight=0.7,
        note="自建推理的典型组合：在租来的卡上跑高吞吐 serving，成本按机时算",
    ),
]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--overwrite", action="store_true")
    args = ap.parse_args()

    ENTRIES.mkdir(parents=True, exist_ok=True)
    VENDORS.mkdir(parents=True, exist_ok=True)
    EDGES.mkdir(parents=True, exist_ok=True)

    ids = [e["id"] for e in ENTRIES_DATA]
    assert len(ids) == len(set(ids)), "duplicate entry id"
    gids = [g["id"] for g in EDGES_DATA]
    assert len(gids) == len(set(gids)), "duplicate edge id"

    wrote_e = wrote_v = wrote_g = 0
    skipped_e = skipped_g = 0
    per_cat: dict[str, int] = {}

    for e in ENTRIES_DATA:
        path = ENTRIES / f"{e['id']}.json"
        if path.exists() and not args.overwrite:
            skipped_e += 1
            print("skip entry exists", e["id"])
            continue
        save(path, e)
        wrote_e += 1
        per_cat[e["category"]] = per_cat.get(e["category"], 0) + 1
        print("entry", e["category"], e["id"])

    for v in VENDORS_DATA:
        path = VENDORS / f"{v['id']}.json"
        if path.exists() and not args.overwrite:
            continue
        save(path, v)
        wrote_v += 1
        print("vendor", v["id"])

    known_new = {x["id"] for x in ENTRIES_DATA}
    for g in EDGES_DATA:
        path = EDGES / f"{g['id']}.json"
        if path.exists() and not args.overwrite:
            skipped_g += 1
            continue
        frm_ok = (ENTRIES / f"{g['from']}.json").exists() or g["from"] in known_new
        to_ok = (ENTRIES / f"{g['to']}.json").exists() or g["to"] in known_new
        if not frm_ok:
            print("skip edge missing from", g["id"], g["from"])
            continue
        if not to_ok:
            print("skip edge missing to", g["id"], g["to"])
            continue
        save(path, g)
        wrote_g += 1
        print("edge", g["id"])

    print(f"done entries={wrote_e} (skipped {skipped_e}) vendors={wrote_v} edges={wrote_g} (skipped {skipped_g})")
    for k in (CAT_BROWSER, CAT_SEARCH, CAT_FINETUNE, CAT_GPU):
        print(f"  {k}: {per_cat.get(k, 0)}")


if __name__ == "__main__":
    main()
