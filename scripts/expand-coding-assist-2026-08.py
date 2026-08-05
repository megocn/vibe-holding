#!/usr/bin/env python3
"""编码助手扩种（两个叶类：coding-completion / coding-review）。

- 补全插件 / 代码助手：Sourcegraph Cody / Qodo Gen / Refact.ai / Tabby / Fitten Code /
  aiXcoder / CodeFuse / CodeGPT
- 代码审查 / PR Agent：CodeRabbit / Greptile / Graphite / Codacy / DeepSource /
  Sourcery / Ellipsis / CodeScene

定位口径：
- coding-completion 收「插进现有 IDE 的补全与内联助手」，独立 IDE（cursor / windsurf / trae）留在 coding-ide-agent。
- coding-review 收「在 PR/MR 上评审、给意见或门禁」的工具，安全扫描（Semgrep/Snyk 类）归 sec-appsec。

用法:
  python3 scripts/expand-coding-assist-2026-08.py
  python3 scripts/expand-coding-assist-2026-08.py --overwrite
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
CAT_COMPLETION = "coding-completion"
CAT_REVIEW = "coding-review"


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
        "tags": ["ai", "coding"],
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
    body = len(e["descriptionMd"].replace("\n", ""))
    assert 160 <= body <= 360, (e["id"], body)
    assert e.get("pitfalls"), e["id"]
    assert e.get("subcategory"), e["id"]
    assert 3 <= len(e["tags"]) <= 5, (e["id"], e["tags"])
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

DOMESTIC = {
    "chinaAccessible": True,
    "needsCompany": False,
    "needsIcp": False,
    "regions": ["CN"],
}


ENTRIES_DATA: list[dict] = [
    # ═══ leaf: coding-completion —— 插进现有 IDE 的补全与内联助手 ═══
    mk(
        CAT_COMPLETION,
        "cody",
        "Sourcegraph Cody",
        "enterprise-context",
        "靠 Sourcegraph 检索取上下文 · 跨仓问答/补全 · 企业档为主",
        "https://sourcegraph.com",
        "Cody 是 Sourcegraph 的编辑器内 AI 助手：装在 VS Code / JetBrains 里，靠自家代码检索把跨仓库的实现与调用喂给补全和问答，而不是另起一个 IDE。",
        "团队仓库多、日常要「跨服务先找到实现再改」的检索型上下文时评估；单仓键入补全用 Copilot 一类即可，独立 Agent 编辑器另看 Cursor 系。",
        "Sourcegraph 的主线已转向 Amp，Cody 的个人档形态几经收敛，选型前确认当前可购档位与部署方式（云实例 / 自托管）。",
        pitfalls=[
            "个人档形态几经调整，长期押注前先确认当前可购买档位",
            "上下文质量取决于 Sourcegraph 实例索引了哪些仓库",
        ],
        vendorId="sourcegraph",
        pricing={"model": "subscription", "currency": "USD"},
        availability=GLOBAL,
        tags=["ai", "code-completion", "code-search", "enterprise"],
    ),
    mk(
        CAT_COMPLETION,
        "qodo-gen",
        "Qodo Gen",
        "test-and-quality",
        "前身 CodiumAI · 强项是生成测试与边界用例 · 编辑器插件形态",
        "https://www.qodo.ai",
        "Qodo Gen（原 CodiumAI）是装进 VS Code / JetBrains 的助手，围绕「先补测试再改代码」组织能力：读函数生成用例、提示边界情况，顺带给补全与解释。",
        "在意回归安全网、希望提交前先有测试与自查的团队，可在纯补全插件之上叠这一层；只求键入速度则看 Supermaven / Copilot。",
        "生成的用例需人工筛选，别直接当验收标准；同厂的 PR 评审线是另一形态，别把两者当同一产品比价。",
        pitfalls=[
            "生成用例需人工筛选，勿直接当验收标准",
            "同厂 PR 评审线是另一形态，别混作同一产品比价",
        ],
        vendorId="qodo",
        pricing={"model": "freemium", "currency": "USD"},
        availability=GLOBAL,
        tags=["ai", "code-completion", "testing", "code-review"],
    ),
    mk(
        CAT_COMPLETION,
        "refact-ai",
        "Refact.ai",
        "self-hosted-oss",
        "开源可自托管 · 补全/聊天/Agent 同一插件 · 支持自有模型",
        "https://refact.ai",
        "Refact.ai 是开源的编辑器内 AI 栈：补全、聊天与 Agent 收在同一个插件里，服务端可以自托管，也支持接自有模型、在私有代码上做适配。",
        "代码不能出内网、又想要一套较完整的插件体验时评估；只要最省事的托管补全则用 Copilot 一类，纯补全后端可对照 Tabby。",
        "自托管要自备 GPU 与运维；开源版与云端付费档能力边界不同，商用前核对协议与档位。",
        pitfalls=[
            "自托管需自备 GPU 与日常运维",
            "开源版与云端档能力不等价，商用前核对协议",
        ],
        vendorId="refact-ai-inc",
        githubUrl="https://github.com/smallcloudai/refact",
        pricing={"model": "open-source"},
        availability=GLOBAL,
        tags=["ai", "code-completion", "open-source", "self-hosted"],
    ),
    mk(
        CAT_COMPLETION,
        "tabby",
        "Tabby（TabbyML）",
        "self-hosted-oss",
        "自托管补全服务 · 单机 GPU 即可起 · 主打代码不外传",
        "https://www.tabbyml.com",
        "Tabby 是自托管的代码补全服务：一台带 GPU 的机器起服务，编辑器只装轻量插件连过去，提示与代码不出自有网络，也可挂仓库索引补上下文。",
        "把「代码不出内网」当硬约束、又不想走企业采购流程时的第一批候选；要开箱即用的多模型体验仍看托管产品。",
        "补全手感取决于所选开源模型与显卡预算，别照 Copilot 预期；集群化与权限治理要自建。",
        pitfalls=[
            "同名产品多（终端工具 Tabby 等），检索与文档需带 TabbyML 限定",
            "补全质量随开源模型与显卡预算浮动",
        ],
        vendorId="tabbyml",
        githubUrl="https://github.com/TabbyML/tabby",
        pricing={"model": "open-source"},
        availability=GLOBAL,
        tags=["ai", "code-completion", "open-source", "self-hosted"],
    ),
    mk(
        CAT_COMPLETION,
        "fitten-code",
        "Fitten Code",
        "domestic-plugin",
        "国内免费补全插件 · 中文交互顺 · 覆盖 VS Code/JetBrains",
        "https://www.fittentech.com",
        "Fitten Code 是非十科技的编辑器补全与对话插件，主打国内网络下的低延迟响应，对中文提示与注释友好，个人使用长期保留免费档。",
        "国内开发者想要一个零门槛、不依赖外网也能用的补全插件时可以先试，和通义灵码、CodeGeeX 属同层比较；企业私有化与合规采购需另谈方案。",
        "复杂重构与长链路改造别过度依赖；免费档的数据使用范围以官网条款为准，敏感仓库先内部评估。",
        pitfalls=[
            "复杂重构能力有限，别当主力 Agent 用",
            "免费档数据使用范围以条款为准，敏感仓库先评估",
        ],
        vendorId="fitten-tech",
        pricing={"model": "freemium", "currency": "CNY"},
        availability=DOMESTIC,
        region="domestic",
        tags=["ai", "code-completion", "domestic", "free"],
    ),
    mk(
        CAT_COMPLETION,
        "aixcoder",
        "aiXcoder",
        "domestic-plugin",
        "重心在私有化部署 · 面向金融/运营商合规 · 补全加代码检索",
        "https://www.aixcoder.com",
        "aiXcoder 提供代码补全与生成插件，产品重心是私有化部署：模型与服务落到客户机房，再结合团队代码库做适配，常见于金融、运营商等合规要求高的组织。",
        "国内企业要「模型进机房、过程可审计」的补全能力时纳入候选；个人轻量使用可先看免费插件。",
        "以项目制交付为主，个人档能力相对有限；效果依赖本地算力与代码库适配投入，建议先做小范围试点。",
        pitfalls=[
            "项目制交付为主，评估周期与投入不低",
            "效果依赖本地算力与代码库适配，需先试点",
        ],
        vendorId="aixcoder-inc",
        pricing={"model": "subscription", "currency": "CNY"},
        availability=DOMESTIC,
        region="domestic",
        tags=["ai", "code-completion", "domestic", "self-hosted"],
    ),
    mk(
        CAT_COMPLETION,
        "codefuse",
        "CodeFuse",
        "domestic-plugin",
        "蚂蚁开源代码智能线 · 模型加工具集 · 偏自建拼装",
        "https://codefuse.ai",
        "CodeFuse 是蚂蚁集团的代码智能线，对外以开源模型与工具集为主，覆盖补全、代码解释与仓库级理解，可自行拼装成组织内部的编码助手。",
        "想在国内自建代码助手、愿意基于开源模型与组件搭一套时评估；要开箱可用的商业插件请看通义灵码、Fitten 一类。",
        "开源仓库分散、版本节奏快，需要持续的工程集成投入；对外仓库与蚂蚁内部完整能力不等同，别据此推断全部效果。",
        pitfalls=[
            "仓库分散、集成成本高，不是开箱即用插件",
            "对外开源能力≠内部完整版，勿据此推断效果",
        ],
        vendorId="ant-group",
        pricing={"model": "open-source"},
        availability=DOMESTIC,
        region="domestic",
        sources=["https://codefuse.ai", "https://github.com/codefuse-ai"],
        tags=["ai", "code-completion", "open-source", "domestic"],
    ),
    mk(
        CAT_COMPLETION,
        "codegpt",
        "CodeGPT",
        "multi-model-plugin",
        "模型自选的薄插件 · 可挂自有 Key 或本机模型 · 多编辑器",
        "https://codegpt.co",
        "CodeGPT 是主打「模型自选」的编辑器插件：在 VS Code、JetBrains 里接不同厂商的模型或本机模型，做补全、解释与局部小改，把选模型的权力交回用户。",
        "已有自己的 API Key 或本地模型、只需要一层薄外壳时评估；要深度 Agent 与多文件改造仍看独立 IDE 或 CLI Agent。",
        "同名项目不少（社区版 JetBrains 插件等），落地前确认是哪条产品线；体验随所接模型波动，token 账单由自有 Key 承担。",
        pitfalls=[
            "同名项目多，确认是哪条产品线再采购",
            "体验随所接模型波动，账单走自有 Key",
        ],
        vendorId="codegpt-inc",
        pricing={"model": "freemium", "currency": "USD"},
        availability=GLOBAL,
        tags=["ai", "code-completion", "multi-model", "plugin"],
    ),
    # ═══ leaf: coding-review —— PR/MR 上的评审、意见与门禁 ═══
    mk(
        CAT_REVIEW,
        "coderabbit",
        "CodeRabbit",
        "pr-review-agent",
        "PR 逐行评审加变更摘要 · GitHub/GitLab App 接入 · 上手最快",
        "https://www.coderabbit.ai",
        "CodeRabbit 以 GitHub/GitLab App 的形式挂在 PR 上：自动给变更摘要、逐行评论与可追问的对话，也能把团队约定写进配置来约束评审口径。",
        "团队想先用「自动第二双眼睛」补上评审人力缺口时的默认起点；架构级问题仍需人来评。",
        "评论量容易过多，需要调阈值与路径过滤，否则真问题被噪声淹没；按贡献者计费，团队规模上去要先测算。",
        pitfalls=[
            "默认评论偏多，需调阈值与路径过滤",
            "按贡献者计费，规模上去成本增长明显",
        ],
        vendorId="coderabbit-inc",
        pricing={"model": "subscription", "currency": "USD"},
        availability=GLOBAL,
        tags=["ai", "code-review", "pull-request", "ci"],
    ),
    mk(
        CAT_REVIEW,
        "greptile",
        "Greptile",
        "pr-review-agent",
        "先索引整仓再评审 · 抓跨文件影响面 · 检索能力也开放 API",
        "https://www.greptile.com",
        "Greptile 先给代码库建索引，再用整仓上下文做 PR 评审，强项是指出「这一改会牵动别处」的跨文件问题；同一套检索能力也以 API 形式对外提供。",
        "老仓库耦合重、最担心一次改动引发连带故障时优先，可与 CodeRabbit 对照试跑同一批 PR；只需要风格与规范类意见，轻量评审工具就够。",
        "索引需要读全仓权限，合规审批要提前走；大仓的首次索引与增量维护都有成本。",
        pitfalls=[
            "需授权读取全仓，合规审批要提前安排",
            "大仓索引与增量维护有额外成本",
        ],
        vendorId="greptile-inc",
        pricing={"model": "subscription", "currency": "USD"},
        availability=GLOBAL,
        tags=["ai", "code-review", "codebase-index", "pull-request"],
    ),
    mk(
        CAT_REVIEW,
        "graphite",
        "Graphite",
        "pr-workflow",
        "堆叠 PR 工作流为主 · 顺带 AI 评审 · 合并队列与 CLI",
        "https://graphite.dev",
        "Graphite 的底子是 stacked PR 工作流：用 CLI 把大改拆成一串小 PR，配合合并队列与看板推进，近年在此之上叠了 AI 评审给即时反馈。",
        "团队愿意调整协作习惯、追求小步快评的评审节奏时评估；只想加评审意见而不动流程，选纯评审 Agent 更省事。",
        "堆叠流程要全员一致才有收益，个别人不用就会打断链路；生态以 GitHub 为主，其他平台支持需先确认。",
        pitfalls=[
            "堆叠工作流需全员一致，半数人不用则收益打折",
            "生态以 GitHub 为主，其他平台支持先确认",
        ],
        vendorId="graphite-dev",
        pricing={"model": "freemium", "currency": "USD"},
        availability=GLOBAL,
        tags=["code-review", "pull-request", "workflow", "ai"],
    ),
    mk(
        CAT_REVIEW,
        "codacy",
        "Codacy",
        "quality-gate",
        "多语静态分析聚合 · 质量门禁与阈值 · 团队治理面板",
        "https://www.codacy.com",
        "Codacy 把多语言的静态分析、重复度与覆盖率结果聚到一处，给 PR 打门禁、给团队看趋势，属于流程里的质量闸门，而非会对话的评审 Agent。",
        "组织需要统一的质量标准与可汇报指标时纳入；要针对业务逻辑的语义化意见，则另配 AI 评审工具。",
        "规则集过严会拖慢合并，落地要先定基线再逐步收紧；与安全扫描职责不同，别指望它替代 SAST。",
        pitfalls=[
            "规则集过严会拖慢合并，先定基线再收紧",
            "职责与安全扫描不同，不能替代 SAST",
        ],
        vendorId="codacy-inc",
        pricing={"model": "subscription", "currency": "USD"},
        availability=GLOBAL,
        tags=["code-review", "static-analysis", "quality-gate", "ci"],
    ),
    mk(
        CAT_REVIEW,
        "deepsource",
        "DeepSource",
        "quality-gate",
        "持续静态分析 · 部分规则可自动出修复 PR · 多语覆盖",
        "https://deepsource.com",
        "DeepSource 在仓库上持续跑静态分析，把问题按类型收敛成可处理的列表，并能对部分规则直接生成修复提交，减少「只报不修」的负担。",
        "存量代码坏味道多、想用自动化逐步偿还技术债时合适；一次性的架构评审仍要靠人或评审 Agent。",
        "自动修复要 review 后再合，别开全自动；各语言的规则覆盖差异较大，选型前按主力语言核对。",
        pitfalls=[
            "自动修复需人工 review 后再合并",
            "各语言规则覆盖差异大，按主力语言核对",
        ],
        vendorId="deepsource-inc",
        pricing={"model": "freemium", "currency": "USD"},
        availability=GLOBAL,
        tags=["code-review", "static-analysis", "autofix", "ci"],
    ),
    mk(
        CAT_REVIEW,
        "sourcery",
        "Sourcery",
        "refactor-advice",
        "重构建议起家（Python 最熟） · 兼做 PR 评审 · 可本机跑",
        "https://sourcery.ai",
        "Sourcery 以「给可读性与重构建议」为特色，早期在 Python 生态中最为人熟知，既能装进编辑器边写边提示，也能作为评审工具在 PR 上留意见。",
        "主力语言是 Python、在意惯用写法与可读性时性价比高；多语言大仓要统一门禁则看 Codacy 一类。",
        "语言覆盖不如通用平台均衡，非 Python 栈需先试；建议偏局部写法，架构层问题不在射程内。",
        pitfalls=[
            "非 Python 栈覆盖较弱，需先小范围验证",
            "建议偏局部写法，架构问题不在射程内",
        ],
        vendorId="sourcery-ai",
        pricing={"model": "freemium", "currency": "USD"},
        availability=GLOBAL,
        tags=["code-review", "refactoring", "python", "pull-request"],
    ),
    mk(
        CAT_REVIEW,
        "ellipsis",
        "Ellipsis",
        "pr-review-agent",
        "评审之外还能直接改 · 按评论产出提交 · 以 GitHub 为主",
        "https://www.ellipsis.dev",
        "Ellipsis 是 PR 上的 AI 评审 Agent：除了留意见，还能按评论直接改代码并推送提交，把「指出问题」与「顺手修掉」放进同一个循环。",
        "小改动希望机器直接收尾、减少评审来回时评估，与只留意见的 CodeRabbit 是同层的两种取向；要求严格人工把关的仓库应限制其写权限。",
        "让 Agent 直接提交需配分支保护与必需审查，避免自动改动绕过流程；复杂改造仍要人接手。",
        pitfalls=[
            "Agent 直接提交需配分支保护与必需审查",
            "复杂改造仍需人接手，勿全权托付",
        ],
        vendorId="ellipsis-dev",
        pricing={"model": "subscription", "currency": "USD"},
        availability=GLOBAL,
        tags=["ai", "code-review", "pull-request", "agent"],
    ),
    mk(
        CAT_REVIEW,
        "codescene",
        "CodeScene",
        "code-health",
        "行为代码分析 · 热点与技术债、团队耦合 · 偏管理视角",
        "https://codescene.com",
        "CodeScene 从版本历史出发做行为代码分析：结合改动频率与复杂度找出热点文件、量化代码健康度，也能看出团队与模块之间的耦合关系。",
        "要给重构排优先级、或向管理层解释技术债集中在哪时最有用，可与 Codacy 这类规则门禁互补；单个 PR 的逐行意见不是它的强项。",
        "结论依赖较长的提交历史，新仓或刚迁移的仓意义有限；指标需结合上下文解读，别直接当 KPI 考核。",
        pitfalls=[
            "依赖较长提交历史，新仓结论意义有限",
            "指标别直接当 KPI 考核，需结合上下文",
        ],
        vendorId="codescene-ab",
        pricing={"model": "subscription", "currency": "USD"},
        availability=GLOBAL,
        tags=["code-review", "code-health", "tech-debt", "analytics"],
    ),
]

VENDORS_DATA: list[dict] = [
    vendor("qodo", "Qodo", url="https://www.qodo.ai"),
    vendor("refact-ai-inc", "Refact.ai", url="https://refact.ai"),
    vendor("tabbyml", "TabbyML", url="https://www.tabbyml.com"),
    vendor("fitten-tech", "非十科技", region="domestic", url="https://www.fittentech.com"),
    vendor("aixcoder-inc", "aiXcoder", region="domestic", url="https://www.aixcoder.com"),
    vendor("codegpt-inc", "CodeGPT", url="https://codegpt.co"),
    vendor("coderabbit-inc", "CodeRabbit", url="https://www.coderabbit.ai"),
    vendor("greptile-inc", "Greptile", url="https://www.greptile.com"),
    vendor("graphite-dev", "Graphite", url="https://graphite.dev"),
    vendor("codacy-inc", "Codacy", url="https://www.codacy.com"),
    vendor("deepsource-inc", "DeepSource", url="https://deepsource.com"),
    vendor("sourcery-ai", "Sourcery", url="https://sourcery.ai"),
    vendor("ellipsis-dev", "Ellipsis", url="https://www.ellipsis.dev"),
    vendor("codescene-ab", "CodeScene", url="https://codescene.com"),
]

EDGES_DATA: list[dict] = [
    # ——— 叶内：补全插件互比 ———
    edge(
        "e-tabby-osalt-github-copilot",
        "tabby",
        "github-copilot",
        "open_source_alternative_to",
        weight=0.8,
        note="自托管补全服务，代码不出内网；手感换算力预算",
    ),
    edge(
        "e-refact-ai-osalt-github-copilot",
        "refact-ai",
        "github-copilot",
        "open_source_alternative_to",
        weight=0.75,
        note="开源插件把补全/聊天/Agent 收在一起，服务端可自托管",
    ),
    edge(
        "e-refact-ai-alt-tabby",
        "refact-ai",
        "tabby",
        "alternative_to",
        note="两条自托管开源线：Refact 带 Agent 与模型适配，Tabby 更轻更易起",
    ),
    edge(
        "e-cody-alt-github-copilot",
        "cody",
        "github-copilot",
        "alternative_to",
        note="跨仓检索型上下文 vs 深度绑定 GitHub 生态",
    ),
    edge(
        "e-cody-alt-qodo-gen",
        "cody",
        "qodo-gen",
        "alternative_to",
        weight=0.6,
        note="代码库检索问答 vs 测试生成与提交前自查",
    ),
    edge(
        "e-codegpt-alt-continue",
        "codegpt",
        "continue",
        "alternative_to",
        note="多模型薄插件：CodeGPT 偏托管产品化，Continue 偏开源可配",
    ),
    edge(
        "e-sourcegraph-amp-succ-cody",
        "sourcegraph-amp",
        "cody",
        "succeeds",
        weight=0.8,
        note="Amp 接棒 Sourcegraph 的 AI 主线，Cody 收敛到企业上下文档",
    ),
    edge(
        "e-tabby-cuw-continue",
        "tabby",
        "continue",
        "commonly_used_with",
        weight=0.6,
        note="自托管补全后端配开源插件前端，凑一套内网可用组合",
    ),
    # ——— 国内 ↔ 海外镜像 ———
    edge(
        "e-aixcoder-domeq-tabnine",
        "aixcoder",
        "tabnine",
        "domestic_equivalent_of",
        note="都以私有化部署与合规为卖点，aiXcoder 走国内项目制交付",
    ),
    edge(
        "e-fitten-code-domeq-github-copilot",
        "fitten-code",
        "github-copilot",
        "domestic_equivalent_of",
        note="国内网络直连、个人免费档；能力上限低于 Copilot",
    ),
    edge(
        "e-codefuse-domeq-cody",
        "codefuse",
        "cody",
        "domestic_equivalent_of",
        weight=0.6,
        note="同走仓库级理解路线，CodeFuse 以开源组件自建替代商业托管",
    ),
    edge(
        "e-codefuse-alt-codegeex",
        "codefuse",
        "codegeex",
        "alternative_to",
        note="国内开源代码模型两条线：CodeFuse 偏工具集自建，CodeGeeX 偏成品插件",
    ),
    # ——— 叶内：评审工具互比 ———
    edge(
        "e-coderabbit-alt-greptile",
        "coderabbit",
        "greptile",
        "alternative_to",
        weight=0.8,
        note="逐行评论加摘要、上手快 vs 整仓索引、专抓跨文件影响",
    ),
    edge(
        "e-ellipsis-alt-coderabbit",
        "ellipsis",
        "coderabbit",
        "alternative_to",
        note="能按评论直接改代码提交 vs 以评审意见为主",
    ),
    edge(
        "e-sourcery-alt-coderabbit",
        "sourcery",
        "coderabbit",
        "alternative_to",
        weight=0.6,
        note="Python 向重构建议 vs 通用多语 PR 评审",
    ),
    edge(
        "e-deepsource-alt-codacy",
        "deepsource",
        "codacy",
        "alternative_to",
        weight=0.8,
        note="偏问题收敛与自动修复 vs 偏多语聚合与治理面板",
    ),
    edge(
        "e-codescene-alt-codacy",
        "codescene",
        "codacy",
        "alternative_to",
        weight=0.6,
        note="用提交历史看热点与技术债 vs 用规则集做门禁",
    ),
    edge(
        "e-graphite-cuw-coderabbit",
        "graphite",
        "coderabbit",
        "commonly_used_with",
        weight=0.6,
        note="堆叠 PR 管流程，AI 评审补意见；两者关注点不重叠",
    ),
    # ——— 跨叶：挂进现有图谱 ———
    edge(
        "e-qodo-gen-cuw-coderabbit",
        "qodo-gen",
        "coderabbit",
        "commonly_used_with",
        weight=0.6,
        note="提交前在编辑器补测试，提交后在 PR 上自动评审",
    ),
    edge(
        "e-coderabbit-integ-github-actions",
        "coderabbit",
        "github-actions",
        "integrates_with",
        weight=0.7,
        note="以 App 与检查项形式并入 CI，可作合并前门禁",
    ),
    edge(
        "e-deepsource-integ-github-actions",
        "deepsource",
        "github-actions",
        "integrates_with",
        weight=0.7,
        note="分析结果回写为检查项，配质量阈值卡合并",
    ),
    edge(
        "e-codacy-integ-gitlab-ci",
        "codacy",
        "gitlab-ci",
        "integrates_with",
        weight=0.7,
        note="接 MR 流水线做质量阈值与覆盖率门禁",
    ),
    edge(
        "e-coderabbit-cuw-cursor",
        "coderabbit",
        "cursor",
        "commonly_used_with",
        weight=0.6,
        note="本机 Agent 快速改完，PR 侧再要一双独立的眼睛",
    ),
    edge(
        "e-greptile-cuw-claude-code",
        "greptile",
        "claude-code",
        "commonly_used_with",
        weight=0.55,
        note="整仓检索型评审 vs 终端里动手改码，常同栈搭配",
    ),
]


def check_dupes() -> None:
    ids = [e["id"] for e in ENTRIES_DATA]
    assert len(ids) == len(set(ids)), "duplicate entry id"
    gids = [g["id"] for g in EDGES_DATA]
    assert len(gids) == len(set(gids)), "duplicate edge id"
    pairs: dict[tuple[str, str], str] = {}
    for g in EDGES_DATA:
        key = tuple(sorted((g["from"], g["to"])))
        assert key not in pairs or pairs[key] == g["type"], ("pair conflict", key)
        pairs[key] = g["type"]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--overwrite", action="store_true")
    args = ap.parse_args()

    check_dupes()

    ENTRIES.mkdir(parents=True, exist_ok=True)
    VENDORS.mkdir(parents=True, exist_ok=True)
    EDGES.mkdir(parents=True, exist_ok=True)

    wrote_e = wrote_v = wrote_g = 0
    for e in ENTRIES_DATA:
        path = ENTRIES / f"{e['id']}.json"
        if path.exists() and not args.overwrite:
            print("skip entry exists", e["id"])
            continue
        save(path, e)
        wrote_e += 1
        print("entry", e["id"], e["category"])

    for v in VENDORS_DATA:
        path = VENDORS / f"{v['id']}.json"
        if path.exists() and not args.overwrite:
            print("skip vendor exists", v["id"])
            continue
        save(path, v)
        wrote_v += 1
        print("vendor", v["id"])

    known_new = {x["id"] for x in ENTRIES_DATA}
    for g in EDGES_DATA:
        path = EDGES / f"{g['id']}.json"
        if path.exists() and not args.overwrite:
            print("skip edge exists", g["id"])
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

    print(f"done entries={wrote_e} vendors={wrote_v} edges={wrote_g}")


if __name__ == "__main__":
    main()
