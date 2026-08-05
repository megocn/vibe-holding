#!/usr/bin/env python3
"""AI 应用侧「四件套」扩种：评测、护栏、记忆、沙箱。

这四层过去散落在 ai-rag / ai-agent-fw / ai-llm-obs 里，导致「拿什么评」「怎么兜底」
「记忆放哪」「Agent 在哪跑代码」四个不同问题被塞进同一份榜单。本批按叶归位并补齐。

用法:
  python3 scripts/expand-ai-guard-2026-08.py
  python3 scripts/expand-ai-guard-2026-08.py --overwrite
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


def save(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def entry(**kw) -> dict:
    e = {
        "pricing": {"model": "open-source"},
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
    assert 20 <= len(e["oneLiner"]) <= 58, (e["id"], len(e["oneLiner"]))
    assert 155 <= len(e["descriptionMd"]) <= 380, (e["id"], len(e["descriptionMd"]))
    assert e["pitfalls"], e["id"]
    assert e.get("subcategory"), e["id"]
    return e


def mk(eid, name, cat, sub, one, url, what, when, caution, **extra):
    pitfalls = extra.pop("pitfalls", None)
    kw = {
        "id": eid,
        "name": name,
        "category": cat,
        "subcategory": sub,
        "oneLiner": one,
        "officialUrl": url,
        "descriptionMd": f"{what}\n\n{when}\n\n{caution}\n",
        "pitfalls": pitfalls or [caution[:90]],
    }
    kw.update(extra)
    return entry(**kw)


def edge(eid, frm, to, typ, weight=0.7, confidence="community", note=None):
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
    return e


def vendor(vid, name, region="overseas", url=None):
    v = {"id": vid, "name": name, "region": region}
    if url:
        v["url"] = url
    return v


OSS = {"model": "open-source"}
SAAS = {"model": "freemium", "currency": "USD"}
USAGE = {"model": "usage", "currency": "USD"}

ENTRIES_DATA: list[dict] = [
    # ——————— ai-eval 评测 / Prompt 实验 ———————
    mk(
        "promptfoo", "Promptfoo", "ai-eval", "cli-eval",
        "本地 CLI 跑评测集 · 配置即用例；可进 CI 当回归门",
        "https://promptfoo.dev",
        "Promptfoo 用 YAML 描述用例与断言，在本地或 CI 里批量跑 prompt 与模型对照，输出可视化对比表，也支持红队式越狱探测。",
        "想把「换个 prompt 到底变好还是变坏」变成可回归的门禁，而不是靠人肉试几条时优先；与 Vitest、GitHub Actions 一类工程栈天然合拍。",
        "断言质量决定评测价值，LLM-as-judge 本身也会漂；评测集不随业务更新就会很快失真，需要有人长期维护。",
        pricing=OSS, tags=["ai", "eval", "open-source", "cli"],
        pitfalls=["LLM-as-judge 自身会漂，需定期抽样人工校准", "评测集不更新会迅速失真"],
    ),
    mk(
        "ragas", "Ragas", "ai-eval", "rag-eval",
        "RAG 专用指标 · 忠实度/相关性打分；依赖裁判模型",
        "https://github.com/explodinggradients/ragas",
        "Ragas 是面向检索增强生成的评测库，围绕忠实度、答案相关性、上下文精确率与召回率等指标给 RAG 链路打分，可无参考答案运行。",
        "已经搭起 RAG、要判断「是检索差还是生成差」时用它做分层归因；常与 LlamaIndex、LangChain 的评测流水线搭配。",
        "指标依赖裁判模型，换模型会让分数不可比；只覆盖 RAG 语义质量，端到端业务效果仍要另测。",
        pricing=OSS, tags=["ai", "eval", "rag", "open-source"],
        pitfalls=["换裁判模型后历史分数不可横比", "只评 RAG 语义质量，不等于业务效果"],
    ),
    mk(
        "deepeval", "DeepEval", "ai-eval", "unit-test-eval",
        "pytest 风格写 LLM 断言 · 单测心智；托管面在 Confident",
        "https://github.com/confident-ai/deepeval",
        "DeepEval 把 LLM 评测写成 pytest 用例：像断言函数一样断言幻觉率、相关性与自定义指标，配套 Confident AI 提供托管看板与数据集管理。",
        "团队已有 Python 测试习惯、希望评测和单测跑在同一条流水线上时优先。",
        "开源库与托管平台的能力边界要先分清，别在 POC 后才发现关键功能在云端；指标同样依赖裁判模型。",
        pricing=SAAS, tags=["ai", "eval", "testing", "python"],
        pitfalls=["开源库与托管平台功能边界需先确认", "指标依赖裁判模型，成本随用例数上涨"],
    ),
    mk(
        "opik", "Opik", "ai-eval", "eval-tracing",
        "评测与追踪一体 · Comet 开源；可自托管",
        "https://github.com/comet-ml/opik",
        "Opik 是 Comet 开源的 LLM 评测与追踪工具，既能记录线上调用轨迹，也能对数据集批量跑评测指标，支持自托管部署。",
        "希望「线上追踪」和「离线评测」共用一套数据与界面、又要能私有化部署时评估；与 Langfuse 属同层可直接横比。",
        "两头都做意味着两头都不如专精工具深；自托管版本的运维与升级成本要计入，托管版则要评估数据出境。",
        pricing=SAAS, tags=["ai", "eval", "observability", "open-source"],
        pitfalls=["评测与追踪兼顾，单项深度不及专精工具", "自托管需自担运维与升级"],
    ),
    mk(
        "langwatch", "LangWatch", "ai-eval", "eval-platform",
        "评测 + 优化闭环 · 面向非工程角色的实验台",
        "https://langwatch.ai",
        "LangWatch 把质量监控、评测集与 prompt 优化放在一个平台里，界面友好到产品与运营也能参与调优，同时提供 SDK 接入线上流量。",
        "团队里做 prompt 调优的不只是工程师、需要一个共同看板讨论质量时评估。",
        "平台化意味着数据要出本地，合规敏感场景需先确认部署形态；与已有可观测工具容易职责重叠。",
        pricing=SAAS, tags=["ai", "eval", "platform", "collaboration"],
        pitfalls=["数据出本地，合规敏感场景需先确认部署形态", "与已有 LLM 可观测工具职责易重叠"],
    ),
    mk(
        "evidently", "Evidently", "ai-eval", "ml-monitoring",
        "从 ML 监控延伸到 LLM 评测 · 报告丰富；偏数据科学心智",
        "https://www.evidentlyai.com",
        "Evidently 起家于表格模型的数据漂移与质量监控，如今把同一套报告体系延伸到 LLM 与 RAG 评测，开源库可直接生成可视化报告。",
        "团队里已有传统机器学习模型、希望 LLM 与它们共用一套质量报告口径时评估。",
        "心智偏数据科学而非应用工程，接入成本对纯应用团队略高；LLM 侧能力仍晚于专做评测的工具。",
        pricing=SAAS, tags=["ai", "eval", "monitoring", "open-source"],
        pitfalls=["偏数据科学心智，应用团队接入成本略高", "LLM 侧能力起步晚于专做评测的工具"],
    ),
    mk(
        "patronus-ai", "Patronus AI", "ai-eval", "managed-eval",
        "托管评测与幻觉检测 · 自带评判模型；闭源为主",
        "https://www.patronus.ai",
        "Patronus AI 提供托管式 LLM 评测服务，主打幻觉与不安全输出的自动检测，附带自研评判模型与行业基准，面向企业交付。",
        "企业要一份「第三方出具」的质量评估、且不愿自己维护裁判模型与评测集时评估；与自建评测栈是买与造的关系。",
        "闭源托管意味着评判逻辑不完全可审计；按调用计费，大规模回归评测成本需先测算，敏感数据也要过合规。",
        pricing=USAGE, tags=["ai", "eval", "managed", "enterprise"],
        pitfalls=["评判逻辑不完全可审计", "按调用计费，大规模回归成本需测算"],
    ),
    mk(
        "humanloop", "Humanloop", "ai-eval", "prompt-management",
        "Prompt 版本管理 + 评测 · 非工程可改；偏企业协作",
        "https://humanloop.com",
        "Humanloop 把 prompt 当作可版本化的资产管理：产品与领域专家在界面里改写并评估，工程侧通过 SDK 拉取指定版本，形成协作闭环。",
        "prompt 频繁被非工程角色调整、需要版本与评测留痕时评估。",
        "把 prompt 托管到外部平台会引入运行期依赖，需要设计好降级路径；企业方案价格不透明，需商务沟通。",
        pricing=SAAS, tags=["ai", "eval", "prompt", "enterprise"],
        pitfalls=["prompt 托管在外部引入运行期依赖，需设计降级", "企业定价不透明，需商务沟通"],
    ),
    # ——————— ai-guardrail 护栏 / 内容安全 ———————
    mk(
        "guardrails-ai", "Guardrails AI", "ai-guardrail", "output-validation",
        "输出结构与内容校验 · 校验器可插拔；社区版为主",
        "https://www.guardrailsai.com",
        "Guardrails AI 用可插拔的校验器约束模型输出：结构是否合法、有无有害内容、是否偏题，校验失败可重试或降级，配套 Hub 提供社区校验器。",
        "输出要直接进下游系统、不能出现结构错误或越界内容时，在应用与模型之间加这一层做兜底。",
        "每次校验都额外增加一轮时延与成本；Hub 上的社区校验器质量参差，上线前需自建回归用例逐个验证。",
        pricing=OSS, tags=["ai", "guardrail", "validation", "open-source"],
        pitfalls=["每次校验增加时延与成本", "社区校验器质量参差，需自建回归验证"],
    ),
    mk(
        "nemo-guardrails", "NeMo Guardrails", "ai-guardrail", "dialog-rails",
        "对话流护栏 · Colang 描述可走路径；NVIDIA 生态",
        "https://github.com/NVIDIA/NeMo-Guardrails",
        "NeMo Guardrails 用 Colang 这门专用语言描述对话可以走与不可以走的路径，把话题边界、事实核查与越狱防护做成可编排的轨道。",
        "做客服、陪练这类多轮对话产品，需要明确写死「这个机器人不谈什么、越界了怎么接」时评估。",
        "要额外学一门 Colang，规则一复杂维护成本就上来了；护栏本身也走模型调用，会给每轮对话叠加时延。",
        pricing=OSS, tags=["ai", "guardrail", "dialog", "open-source"],
        pitfalls=["需额外学习 Colang，规则复杂后难维护", "护栏自身走模型调用，叠加时延"],
    ),
    mk(
        "llm-guard", "LLM Guard", "ai-guardrail", "input-output-scan",
        "输入输出双向扫描 · 提示注入/PII 检测；自托管",
        "https://github.com/protectai/llm-guard",
        "LLM Guard 在请求进入模型前与响应返回前各扫一遍，覆盖提示注入、越狱、敏感信息泄露、有害语言与代码注入等常见风险项。",
        "自建 LLM 网关、需要一层完全可自托管的安全扫描而不愿把用户内容送到第三方时评估。",
        "扫描器基于模型与规则，误杀与漏判都会发生，阈值需按业务反复调；同步串在链路上会明显拉长首字时延。",
        pricing=OSS, tags=["ai", "guardrail", "security", "open-source"],
        pitfalls=["误杀与漏判并存，阈值需按业务调", "串在链路上明显影响首字时延"],
    ),
    mk(
        "lakera", "Lakera", "ai-guardrail", "prompt-security",
        "提示注入防护 SaaS · 攻击情报持续更新；数据需出本地",
        "https://www.lakera.ai",
        "Lakera 专注 AI 应用的提示注入与越狱防护，以 API 形式提供实时判定，并靠持续更新的攻击样本库跟进新出现的绕过手法。",
        "面向公众开放的 AI 产品，把安全判定外包给专业团队比自己天天追新攻击面更划算时评估。",
        "判定要把用户内容发往第三方，合规敏感场景需先过审；按调用计费，高流量下的成本要先测算。",
        pricing=USAGE, tags=["ai", "guardrail", "security", "saas"],
        pitfalls=["内容需发往第三方，合规敏感场景先过审", "按调用计费，高流量下成本可观"],
    ),
    mk(
        "rebuff", "Rebuff", "ai-guardrail", "prompt-injection",
        "提示注入多层检测 · 含金丝雀词；项目偏轻量",
        "https://github.com/protectai/rebuff",
        "Rebuff 用启发式规则、模型判定、向量相似比对与金丝雀词四层手段检测提示注入，其中金丝雀词能反过来确认系统提示是否已被泄露出去。",
        "想低成本给现有链路先加一道注入检测、或用它来研究注入攻防机制、做安全基线时评估。",
        "项目体量与维护节奏都不及商业方案，不建议当作唯一防线；检测层开得越多，时延与成本叠加越明显。",
        pricing=OSS, maturity="beta", tags=["ai", "guardrail", "security", "open-source"],
        pitfalls=["维护节奏一般，不宜作唯一防线", "多层检测叠加时延与成本"],
    ),
    mk(
        "presidio", "Microsoft Presidio", "ai-guardrail", "pii-redaction",
        "PII 识别与脱敏 · 支持文本/图像；需按语种调词典",
        "https://github.com/microsoft/presidio",
        "Presidio 是微软开源的隐私数据识别与脱敏框架，内置多种实体识别器并可自定义规则，支持文本与图像，常被放在数据进模型之前。",
        "要在把用户数据喂给模型或送往第三方之前先做一遍脱敏、且要求整条链路可自托管时优先。",
        "中文等非英语场景的识别效果需要自行补词典与规则才够用；脱敏后若还原逻辑设计不当，反而会引入新的泄露面。",
        pricing=OSS, tags=["ai", "guardrail", "privacy", "open-source"],
        pitfalls=["中文场景识别需自补词典与规则", "还原逻辑设计不当会引入新泄露面"],
    ),
    mk(
        "azure-content-safety", "Azure AI Content Safety", "ai-guardrail", "cloud-moderation",
        "云侧内容审核 API · 多模态分级；与 Azure 生态绑定",
        "https://azure.microsoft.com",
        "Azure AI Content Safety 提供文本与图像的有害内容分级判定，以及针对提示攻击与「越权输出」的检测能力，是 Azure 上模型服务的常见配套。",
        "已在 Azure 生态、要给 Azure OpenAI 之类服务补一层官方审核时优先。",
        "与 Azure 账号和区域强绑定，跨云使用不经济；类目与阈值口径是平台定义的，不一定贴合你的业务红线。",
        vendorId="microsoft", pricing=USAGE,
        tags=["ai", "guardrail", "moderation", "cloud"],
        pitfalls=["与 Azure 账号区域强绑定，跨云不经济", "审核类目由平台定义，未必贴合业务红线"],
    ),
    mk(
        "aliyun-content-safety", "阿里云内容安全", "ai-guardrail", "domestic-moderation",
        "国内合规审核主力 · 覆盖图文音视频；按调用计费",
        "https://www.aliyun.com",
        "阿里云内容安全提供文本、图片、音视频的机器审核能力，规则与类目对齐国内监管要求，是面向国内用户的产品做合规兜底的常规选择。",
        "产品在国内上线、需要留存审核记录并应对监管抽查时基本是必选项；常与生成式模型输出侧串联。",
        "机审无法百分之百兜底，重点场景仍要配人工复核队列；类目口径会随监管调整，接入后需持续跟进变更公告。",
        vendorId="alibaba", pricing={"model": "usage", "currency": "CNY"},
        availability={"chinaAccessible": True, "needsCompany": True, "needsIcp": False, "regions": ["CN"]},
        region="domestic",
        tags=["ai", "guardrail", "moderation", "domestic"],
        pitfalls=["机审不能完全兜底，重点场景需人工复核", "监管口径变化后需跟进规则调整"],
    ),
    # ——————— ai-memory Agent 记忆 ———————
    mk(
        "zep", "Zep", "ai-memory", "temporal-memory",
        "时序知识图谱记忆 · 记事实也记变化；有托管与开源",
        "https://www.getzep.com",
        "Zep 把对话历史提炼成带时间维度的知识图谱，既保留事实也保留事实何时发生变化，检索时按相关性与时效一并排序。",
        "做长期陪伴、客服或销售类 Agent，需要「记得用户三个月前说过什么、后来又改口了」这类记忆时评估。",
        "图谱构建要额外的模型调用，写入成本与时延都高于简单向量存储；开源版与托管版能力有差别，选型前先对齐。",
        pricing=SAAS, tags=["ai", "memory", "graph", "agent"],
        pitfalls=["图谱构建带来额外调用成本与写入时延", "开源版与托管版能力有差异"],
    ),
    mk(
        "graphiti", "Graphiti", "ai-memory", "memory-framework",
        "时序图谱记忆框架 · Zep 内核开源；需自备图库",
        "https://github.com/getzep/graphiti",
        "Graphiti 是 Zep 开源出来的时序知识图谱框架，把对话与事件增量写入图中并维护事实的有效期，可独立集成到自己的 Agent 里。",
        "想要 Zep 那套时序记忆但坚持全自托管、或要在自有图数据库上做二次开发时选它。",
        "需要自备并长期运维一套图数据库；增量更新与事实冲突消解的调参不轻松，小项目上很容易得不偿失。",
        pricing=OSS, tags=["ai", "memory", "graph", "open-source"],
        pitfalls=["需自备并运维图数据库", "增量更新与冲突消解调参成本高"],
    ),
    mk(
        "cognee", "Cognee", "ai-memory", "memory-pipeline",
        "记忆即管道 · 图谱与向量并用；仍在快速演进",
        "https://www.cognee.ai",
        "Cognee 把记忆构建当作一条数据管道来做：抽取实体与关系写入图谱，同时保留向量索引，让 Agent 既能语义召回、也能沿关系做多跳推理。",
        "记忆里既有大量非结构文本、又有明确实体与关系，单纯向量检索答不好多跳问题时评估。",
        "接口与抽象仍在快速演进，跨版本升级可能不兼容；管道跑得越重，每条记忆的写入成本与时延就越高。",
        pricing=OSS, maturity="beta", tags=["ai", "memory", "graph", "open-source"],
        pitfalls=["接口仍在演进，升级可能不兼容", "管道越重写入成本越高"],
    ),
    mk(
        "memobase", "Memobase", "ai-memory", "user-profile",
        "以用户画像为中心的记忆 · 结构化档案；官网已下线",
        "https://docs.memobase.io/introduction",
        "Memobase 侧重把对话沉淀成结构化的用户画像，用可读的档案字段而非纯向量记录偏好与状态，便于在提示里直接引用与人工核对，服务端可自托管。",
        "做面向个人用户的长期产品、需要一份「这个用户是谁」的可解释画像而非黑盒向量时评估，自托管一份即可跑通。",
        "画像字段设计是主要工作量，抽取不准会长期误导下游生成；官网主站已下线、只剩文档与开源仓库，长期依赖前先看提交活跃度。",
        pricing=OSS, maturity="beta",
        tags=["ai", "memory", "profile", "agent", "open-source"],
        githubUrl="https://github.com/memodb-io/memobase",
        docsUrl="https://docs.memobase.io",
        sources=["https://github.com/memodb-io/memobase", "https://docs.memobase.io/introduction"],
        pitfalls=[
            "画像字段设计是主要工作量，抽取不准会长期误导下游",
            "官网主站已下线，只剩文档与仓库，商业化前景不明",
        ],
    ),
    mk(
        "supermemory", "Supermemory", "ai-memory", "memory-api",
        "记忆 API 与个人知识层 · 接入快；深度定制空间小",
        "https://supermemory.ai",
        "Supermemory 提供开箱即用的记忆 API 与个人知识层，把网页、笔记与对话统一收纳、按语义召回，几行代码即可接入。",
        "想尽快给应用加上「记得住上下文」的能力、暂时不打算自建检索与图谱管线时评估。",
        "托管形态决定了深度定制空间有限，记忆的切分与召回策略基本由平台决定；数据要出本地，合规敏感场景需先评估。",
        pricing=SAAS, maturity="beta", tags=["ai", "memory", "api", "saas"],
        pitfalls=["记忆策略由平台决定，定制空间有限", "数据出本地需评估合规"],
    ),
    # ——————— ai-sandbox 代码沙箱 / Agent 运行时 ———————
    mk(
        "e2b", "E2B", "ai-sandbox", "code-interpreter",
        "Agent 专用代码沙箱 · 秒级冷启动；按运行时长计费",
        "https://e2b.dev",
        "E2B 提供给 AI Agent 用的隔离云沙箱，秒级启动一个可跑 Python/Node 的环境，支持文件读写、联网与长任务保活，SDK 直接嵌进 Agent 循环。",
        "Agent 需要真正执行代码、装依赖或处理用户上传文件，而你不愿让它碰生产机器时优先。",
        "按沙箱运行时长计费，长时任务成本要盯；沙箱内网络与依赖安装策略需按安全要求收紧。",
        pricing=USAGE, tags=["ai", "sandbox", "agent", "runtime"],
        pitfalls=["按运行时长计费，长任务成本需监控", "沙箱出网策略需按安全要求收紧"],
    ),
    mk(
        "daytona", "Daytona", "ai-sandbox", "dev-environment",
        "标准化开发环境 · 从人用转向 Agent 用；需自建镜像规范",
        "https://www.daytona.io",
        "Daytona 做标准化的按需开发环境，近年重心转向为 AI Agent 提供可编程的隔离运行环境，支持自托管与多种基础设施后端。",
        "既要给人开一致的开发环境、又要给 Agent 提供同规格沙箱，希望两者共用一套定义时评估。",
        "环境镜像与依赖规范要团队自己立，否则一致性收益打折；自托管形态的运维成本别低估。",
        pricing=SAAS, tags=["ai", "sandbox", "devenv", "open-source"],
        pitfalls=["镜像与依赖规范需团队自建", "自托管形态运维成本不低"],
    ),
    mk(
        "riza", "Riza", "ai-sandbox", "code-execution-api",
        "代码执行 API · WASM 隔离轻量；不适合重依赖任务",
        "https://riza.io",
        "Riza 提供面向 LLM 工具调用的代码执行 API，用 WebAssembly 沙箱跑不受信任的代码片段，启动极快、隔离边界清晰。",
        "只需要让模型跑一小段计算或数据处理、并不需要完整操作系统时，它比整机沙箱轻得多。",
        "WASM 隔离意味着系统调用与三方原生依赖都受限，重依赖任务跑不动；没有长驻状态，会话保持需自行设计。",
        pricing=USAGE, maturity="beta", tags=["ai", "sandbox", "wasm", "api"],
        pitfalls=["WASM 环境不支持重原生依赖", "无长驻状态，需自行设计会话保持"],
    ),
    mk(
        "codesandbox-sdk", "CodeSandbox SDK", "ai-sandbox", "vm-sandbox",
        "可分叉的持久化微型 VM · 带内存快照；偏 Web 栈",
        "https://codesandbox.io",
        "CodeSandbox SDK 把其在线 IDE 背后的微型虚拟机开放出来：环境可分叉、可快照恢复，让 Agent 在有状态的环境里连续工作。",
        "Agent 需要反复回到同一环境继续改代码、或要为每个用户会话分叉一份环境时评估。",
        "生态与镜像偏 Web/Node 栈，异构语言支持要先验证；持久化环境的存储与保活成本需要盯。",
        pricing=SAAS, tags=["ai", "sandbox", "vm", "web"],
        pitfalls=["镜像与生态偏 Web/Node 栈", "持久环境的存储与保活成本需监控"],
    ),
    mk(
        "webcontainers", "WebContainers", "ai-sandbox", "browser-runtime",
        "浏览器内跑 Node · 零服务器成本；受浏览器能力限制",
        "https://webcontainers.io",
        "WebContainers 是 StackBlitz 的浏览器内运行时，直接在用户标签页里跑 Node 与包管理器，无需后端沙箱即可预览与执行前端项目。",
        "做在线教程、可交互文档或 Web 应用预览，希望执行成本落在用户端时优先。",
        "只覆盖 Node/Web 生态，原生依赖与后端语言跑不了；受浏览器隔离策略限制，对跨源与性能有约束。",
        pricing=SAAS, tags=["ai", "sandbox", "browser", "node"],
        pitfalls=["仅覆盖 Node/Web 生态", "受浏览器隔离与性能限制，重任务不适用"],
    ),
    mk(
        "judge0", "Judge0", "ai-sandbox", "code-judge",
        "多语言代码判题引擎 · 六十余种语言；面向短程序",
        "https://judge0.com",
        "Judge0 是开源的在线代码执行与判题引擎，支持数十种语言的编译与运行，可自托管也有托管 API，长期用于教育与面试平台。",
        "需要批量跑短程序并拿到标准输出、退出码与耗时，例如判题、代码题评测或模型代码能力测评时评估。",
        "面向一次性短程序，不适合长驻服务或复杂依赖工程；自托管时资源隔离与配额必须自己配好。",
        pricing=SAAS, tags=["ai", "sandbox", "judge", "open-source"],
        pitfalls=["面向短程序，不适合长驻或重依赖工程", "自托管需自行配置资源隔离与配额"],
    ),
    mk(
        "gvisor", "gVisor", "ai-sandbox", "kernel-sandbox",
        "用户态内核隔离 · 比容器强的边界；有系统调用兼容代价",
        "https://gvisor.dev",
        "gVisor 是 Google 开源的应用内核，在用户态实现一层系统调用拦截，让不受信任的容器获得接近虚拟机的隔离强度，是多家沙箱产品的底层。",
        "自建执行沙箱、要在容器成本与虚拟机隔离之间取平衡时，作为基础设施层评估。",
        "部分系统调用不完全兼容，重 I/O 与特殊内核特性场景需实测；它是基础组件，不含调度与计费等平台能力。",
        pricing=OSS, tags=["ai", "sandbox", "security", "open-source"],
        pitfalls=["系统调用兼容性需按负载实测", "只是隔离层，不含调度与计费等平台能力"],
    ),
]

VENDORS_DATA: list[dict] = [
    vendor("confident-ai", "Confident AI", url="https://confident-ai.com"),
    vendor("zep-inc", "Zep", url="https://www.getzep.com"),
    vendor("e2b-inc", "E2B", url="https://e2b.dev"),
]

EDGES_DATA: list[dict] = [
    # 评测叶内互比 + 与观测分层
    edge("e-promptfoo-alt-braintrust", "promptfoo", "braintrust", "alternative_to",
         note="本地 CLI 与 CI 门禁 vs 托管评测平台", weight=0.8),
    edge("e-promptfoo-alt-deepeval", "promptfoo", "deepeval", "alternative_to",
         note="YAML 配置用例 vs pytest 断言心智", weight=0.75),
    edge("e-ragas-alt-deepeval", "ragas", "deepeval", "alternative_to",
         note="RAG 专用指标 vs 通用 LLM 断言框架", weight=0.7),
    edge("e-ragas-cuw-llamaindex", "ragas", "llamaindex", "commonly_used_with",
         note="搭好 RAG 之后用它做检索/生成分层归因", weight=0.75),
    edge("e-opik-alt-langfuse", "opik", "langfuse", "alternative_to",
         note="评测与追踪一体 vs 专做线上追踪；都可自托管", weight=0.7),
    edge("e-promptfoo-cuw-langfuse", "promptfoo", "langfuse", "commonly_used_with",
         note="离线评测 vs 线上观测，是互补的两层而非二选一", weight=0.7),
    edge("e-langwatch-alt-humanloop", "langwatch", "humanloop", "alternative_to",
         note="质量看板取向 vs prompt 资产管理取向", weight=0.65),
    edge("e-patronus-ai-alt-braintrust", "patronus-ai", "braintrust", "alternative_to",
         note="自带评判模型的托管服务 vs 自建评测集的平台", weight=0.6),
    edge("e-evidently-alt-ragas", "evidently", "ragas", "alternative_to",
         note="从 ML 监控延伸 vs RAG 原生指标", weight=0.6),
    # 护栏叶
    edge("e-llm-guard-alt-guardrails-ai", "llm-guard", "guardrails-ai", "alternative_to",
         note="安全扫描取向 vs 输出结构校验取向", weight=0.8),
    edge("e-llm-guard-oss-lakera", "llm-guard", "lakera", "open_source_alternative_to",
         note="自托管扫描换取内容不出本地", weight=0.75),
    edge("e-rebuff-alt-llm-guard", "rebuff", "llm-guard", "alternative_to",
         note="专攻提示注入 vs 覆盖面更全的双向扫描", weight=0.7),
    edge("e-nemo-guardrails-alt-guardrails-ai", "nemo-guardrails", "guardrails-ai", "alternative_to",
         note="对话流轨道 vs 单次输出校验", weight=0.7),
    edge("e-presidio-cuw-llm-guard", "presidio", "llm-guard", "commonly_used_with",
         note="PII 脱敏与安全扫描常串在同一入口层", weight=0.65),
    edge("e-aliyun-content-safety-dom-azure-content-safety",
         "aliyun-content-safety", "azure-content-safety", "domestic_equivalent_of",
         note="国内合规审核对应云侧内容审核 API 的位置", weight=0.75),
    edge("e-guardrails-ai-cuw-langchain", "guardrails-ai", "langchain", "commonly_used_with",
         note="在链路输出侧加一层校验", weight=0.6),
    # 记忆叶
    edge("e-zep-alt-mem0", "zep", "mem0", "alternative_to",
         note="时序知识图谱 vs 轻量记忆层；写入成本与可解释性取舍不同", weight=0.85),
    edge("e-graphiti-part-of-zep", "graphiti", "zep", "part_of",
         note="Zep 开源出来的时序图谱内核", weight=0.9, confidence="verified"),
    edge("e-cognee-alt-zep", "cognee", "zep", "alternative_to",
         note="通用记忆管道 vs 面向对话的时序图谱", weight=0.7),
    edge("e-memobase-alt-mem0", "memobase", "mem0", "alternative_to",
         note="结构化用户画像 vs 通用记忆条目", weight=0.7),
    edge("e-supermemory-alt-mem0", "supermemory", "mem0", "alternative_to",
         note="开箱托管 API vs 可自托管的记忆层", weight=0.65),
    edge("e-mem0-cuw-qdrant", "mem0", "qdrant", "commonly_used_with",
         note="记忆层通常仍要落到一个向量库上", weight=0.6),
    edge("e-zep-cuw-neo4j", "zep", "neo4j", "commonly_used_with",
         note="时序记忆图谱常以图数据库为后端", weight=0.6),
    # 沙箱叶
    edge("e-daytona-alt-e2b", "daytona", "e2b", "alternative_to",
         note="标准化开发环境延伸而来 vs 原生为 Agent 设计的沙箱", weight=0.8),
    edge("e-riza-alt-e2b", "riza", "e2b", "alternative_to",
         note="WASM 轻量执行 vs 完整环境沙箱", weight=0.75),
    edge("e-codesandbox-sdk-alt-e2b", "codesandbox-sdk", "e2b", "alternative_to",
         note="可分叉的有状态微型 VM vs 一次性沙箱", weight=0.7),
    edge("e-webcontainers-alt-codesandbox-sdk", "webcontainers", "codesandbox-sdk", "alternative_to",
         note="执行落在浏览器 vs 落在云端 VM", weight=0.7),
    edge("e-judge0-alt-riza", "judge0", "riza", "alternative_to",
         note="多语言判题引擎 vs 面向工具调用的执行 API", weight=0.6),
    edge("e-e2b-built-on-gvisor", "e2b", "gvisor", "built_on",
         note="Agent 沙箱普遍依赖用户态内核这类隔离底座", weight=0.5,
         confidence="inferred"),
    edge("e-e2b-cuw-claude-code", "e2b", "claude-code", "commonly_used_with",
         note="终端 Agent 跑不可信代码时挂一层隔离环境", weight=0.55),
    edge("e-e2b-cuw-langchain", "e2b", "langchain", "commonly_used_with",
         note="作为代码解释器工具接进 Agent 链路", weight=0.65),
]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--overwrite", action="store_true")
    args = ap.parse_args()

    new_ids = {e["id"] for e in ENTRIES_DATA}

    def exists(nid: str) -> bool:
        return (ENTRIES / f"{nid}.json").exists() or nid in new_ids

    wrote_e = wrote_v = wrote_g = 0
    for v in VENDORS_DATA:
        path = VENDORS / f"{v['id']}.json"
        if path.exists() and not args.overwrite:
            continue
        save(path, v)
        wrote_v += 1

    for e in ENTRIES_DATA:
        path = ENTRIES / f"{e['id']}.json"
        if path.exists() and not args.overwrite:
            print("skip entry", e["id"])
            continue
        save(path, e)
        wrote_e += 1

    skipped = []
    for g in EDGES_DATA:
        path = EDGES / f"{g['id']}.json"
        if path.exists() and not args.overwrite:
            continue
        if not exists(g["from"]) or not exists(g["to"]):
            skipped.append(f"{g['from']}->{g['to']}")
            continue
        save(path, g)
        wrote_g += 1

    print(f"done entries={wrote_e} vendors={wrote_v} edges={wrote_g}")
    if skipped:
        print(f"skipped edges ({len(skipped)}): {', '.join(skipped)}")


if __name__ == "__main__":
    main()
