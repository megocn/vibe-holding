#!/usr/bin/env python3
"""VibeHolding Wave 1 (A–F + J) knowledge base expansion."""
from __future__ import annotations

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
    e.pop("vendorId", None) if e.get("vendorId") is None else None
    assert len(e["oneLiner"]) <= 60, (e["id"], e["oneLiner"])
    assert len(e.get("descriptionMd", "")) >= 120, (e["id"], len(e.get("descriptionMd", "")))
    assert e.get("pitfalls"), e["id"]
    assert e.get("subcategory"), e["id"]
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


def desc(what: str, when: str, caution: str) -> str:
    return f"{what}\n\n{when}\n\n{caution}\n"


def mk(
    eid: str,
    name: str,
    cat: str,
    sub: str,
    one: str,
    url: str,
    what: str,
    when: str,
    caution: str,
    *,
    region: str = "overseas",
    vendor: str | None = None,
    pricing: str = "freemium",
    maturity: str = "stable",
    tags: list[str] | None = None,
    pitfalls: list[str] | None = None,
    china: bool = True,
    docs: str | None = None,
    **extra,
) -> dict:
    kw: dict = {
        "id": eid,
        "name": name,
        "category": cat,
        "subcategory": sub,
        "oneLiner": one,
        "officialUrl": url,
        "descriptionMd": desc(what, when, caution),
        "region": region,
        "pricing": {"model": pricing},
        "maturity": maturity,
        "tags": tags or [],
        "pitfalls": pitfalls or [caution],
        "availability": {
            "chinaAccessible": china,
            "needsCompany": False,
            "needsIcp": False,
            "regions": ["global"],
        },
    }
    if vendor:
        kw["vendorId"] = vendor
    if docs:
        kw["docsUrl"] = docs
    kw.update(extra)
    return entry(**kw)


def llm_family(
    eid: str,
    name: str,
    vendor: str,
    url: str,
    one: str,
    what: str,
    when: str,
    caution: str,
    *,
    region: str = "overseas",
    china: bool = True,
    pricing: str = "usage",
    **extra,
) -> dict:
    return mk(
        eid, name, "llm-family", "family", one, url, what, when, caution,
        region=region, vendor=vendor, pricing=pricing, china=china,
        tags=["llm", "family"], **extra,
    )


def llm_line(
    eid: str,
    name: str,
    vendor: str,
    url: str,
    one: str,
    what: str,
    when: str,
    caution: str,
    *,
    region: str = "overseas",
    china: bool = True,
    pricing: str = "usage",
    flagship: bool = False,
    **extra,
) -> dict:
    tags = ["llm", "line"]
    if flagship:
        tags.append("flagship")
    return mk(
        eid, name, "llm-line", "line", one, url, what, when, caution,
        region=region, vendor=vendor, pricing=pricing, china=china,
        tags=tags, **extra,
    )


_entries: list[dict] = []
_edges: list[dict] = []


def add(e: dict) -> None:
    _entries.append(e)


def link(eid: str, frm: str, to: str, typ: str, **kw) -> None:
    _edges.append(edge(eid, frm, to, typ, **kw))



_VENDORS = [
    {"id": "01-ai", "name": "零一万物", "region": "domestic", "url": "https://www.lingyiwanwu.com"},
    {"id": "actix-team", "name": "Actix", "region": "overseas", "url": "https://actix.rs"},
    {"id": "adobe-react-aria", "name": "Adobe", "region": "overseas", "url": "https://react-spectrum.adobe.com/react-aria"},
    {"id": "adonisjs", "name": "AdonisJS", "region": "overseas", "url": "https://adonisjs.com"},
    {"id": "agno-ai", "name": "Agno", "region": "overseas", "url": "https://www.agno.com"},
    {"id": "amazon", "name": "Amazon", "region": "overseas", "url": "https://aws.amazon.com"},
    {"id": "angular-team", "name": "Google", "region": "overseas", "url": "https://angular.dev"},
    {"id": "anthropic", "name": "Anthropic", "region": "overseas", "url": "https://www.anthropic.com"},
    {"id": "anyscale-inc", "name": "Anyscale", "region": "overseas", "url": "https://www.anyscale.com"},
    {"id": "apple-swift", "name": "Apple", "region": "overseas", "url": "https://swift.org"},
    {"id": "arize-ai", "name": "Arize AI", "region": "overseas", "url": "https://arize.com"},
    {"id": "astro-inc", "name": "Astro", "region": "overseas", "url": "https://astro.build"},
    {"id": "augment-code", "name": "Augment Code", "region": "overseas", "url": "https://www.augmentcode.com"},
    {"id": "autogen-ms", "name": "Microsoft", "region": "overseas", "url": "https://microsoft.github.io/autogen"},
    {"id": "baichuan-inc", "name": "百川智能", "region": "domestic", "url": "https://www.baichuan-ai.com"},
    {"id": "baidu", "name": "百度", "region": "domestic", "url": "https://www.baidu.com"},
    {"id": "baidu-comate", "name": "百度", "region": "domestic", "url": "https://comate.baidu.com"},
    {"id": "base44-inc", "name": "Base44", "region": "overseas", "url": "https://base44.com"},
    {"id": "baseten-inc", "name": "Baseten", "region": "overseas", "url": "https://www.baseten.co"},
    {"id": "blackbox-ai", "name": "Blackbox AI", "region": "overseas", "url": "https://www.blackbox.ai"},
    {"id": "blink-new", "name": "Blink", "region": "overseas", "url": "https://blink.new"},
    {"id": "braintrust-data", "name": "Braintrust", "region": "overseas", "url": "https://www.braintrust.dev"},
    {"id": "bytedance-marscode", "name": "字节跳动", "region": "domestic", "url": "https://www.marscode.com"},
    {"id": "cerebras", "name": "Cerebras", "region": "overseas", "url": "https://cerebras.ai"},
    {"id": "chakra-ark", "name": "Chakra UI", "region": "overseas", "url": "https://ark-ui.com"},
    {"id": "chakra-ui-inc", "name": "Chakra UI", "region": "overseas", "url": "https://chakra-ui.com"},
    {"id": "chroma-inc", "name": "Chroma", "region": "overseas", "url": "https://www.trychroma.com"},
    {"id": "cline-inc", "name": "Cline", "region": "overseas", "url": "https://cline.bot"},
    {"id": "cloudflare-inc", "name": "Cloudflare", "region": "overseas", "url": "https://www.cloudflare.com"},
    {"id": "cohere", "name": "Cohere", "region": "overseas", "url": "https://cohere.com"},
    {"id": "coze", "name": "扣子 Coze", "region": "both", "url": "https://www.coze.com"},
    {"id": "create-xyz", "name": "Create", "region": "overseas", "url": "https://www.create.xyz"},
    {"id": "crewai-inc", "name": "CrewAI", "region": "overseas", "url": "https://www.crewai.com"},
    {"id": "databutton", "name": "Databutton", "region": "overseas", "url": "https://databutton.com"},
    {"id": "deepinfra-inc", "name": "DeepInfra", "region": "overseas", "url": "https://deepinfra.com"},
    {"id": "deepset", "name": "deepset", "region": "overseas", "url": "https://www.deepset.ai"},
    {"id": "django-software", "name": "Django Software Foundation", "region": "overseas", "url": "https://www.djangoproject.com"},
    {"id": "dotnet-foundation", "name": ".NET Foundation", "region": "overseas", "url": "https://dotnet.microsoft.com"},
    {"id": "electronjs", "name": "Electron", "region": "overseas", "url": "https://www.electronjs.org"},
    {"id": "element-plus", "name": "Element Plus", "region": "overseas", "url": "https://element-plus.org"},
    {"id": "elixir-lang", "name": "Elixir", "region": "overseas", "url": "https://elixir-lang.org"},
    {"id": "emergent-labs", "name": "Emergent", "region": "overseas", "url": "https://emergent.sh"},
    {"id": "expo-dev", "name": "Expo", "region": "overseas", "url": "https://expo.dev"},
    {"id": "expressjs", "name": "OpenJS Foundation", "region": "overseas", "url": "https://expressjs.com"},
    {"id": "factory-ai", "name": "Factory", "region": "overseas", "url": "https://factory.ai"},
    {"id": "fastapi-tiangolo", "name": "FastAPI", "region": "overseas", "url": "https://fastapi.tiangolo.com"},
    {"id": "fastify-team", "name": "Fastify", "region": "overseas", "url": "https://fastify.dev"},
    {"id": "firecrawl-dev", "name": "Firecrawl", "region": "overseas", "url": "https://www.firecrawl.dev"},
    {"id": "fireworks-ai", "name": "Fireworks AI", "region": "overseas", "url": "https://fireworks.ai"},
    {"id": "flowise-ai", "name": "FlowiseAI", "region": "overseas", "url": "https://flowiseai.com"},
    {"id": "flutter-dev", "name": "Flutter", "region": "overseas", "url": "https://flutter.dev"},
    {"id": "fontawesome", "name": "Font Awesome", "region": "overseas", "url": "https://fontawesome.com"},
    {"id": "framer", "name": "Framer", "region": "overseas", "url": "https://www.framer.com"},
    {"id": "ggml-org", "name": "ggml", "region": "overseas", "url": "https://github.com/ggerganov/llama.cpp"},
    {"id": "gin-gonic", "name": "Gin", "region": "overseas", "url": "https://gin-gonic.com"},
    {"id": "gluestack", "name": "gluestack", "region": "overseas", "url": "https://gluestack.io"},
    {"id": "google-dart", "name": "Google", "region": "overseas", "url": "https://dart.dev"},
    {"id": "google-deepmind", "name": "Google DeepMind", "region": "overseas", "url": "https://deepmind.google"},
    {"id": "google-gemma", "name": "Google", "region": "overseas", "url": "https://ai.google.dev/gemma"},
    {"id": "google-vertex", "name": "Google Cloud", "region": "overseas", "url": "https://cloud.google.com/vertex-ai"},
    {"id": "goose-ai", "name": "Block", "region": "overseas", "url": "https://block.github.io/goose"},
    {"id": "groq-inc", "name": "Groq", "region": "overseas", "url": "https://groq.com"},
    {"id": "helicone-ai", "name": "Helicone", "region": "overseas", "url": "https://www.helicone.ai"},
    {"id": "heroui", "name": "HeroUI", "region": "overseas", "url": "https://www.heroui.com"},
    {"id": "hono-dev", "name": "Hono", "region": "overseas", "url": "https://hono.dev"},
    {"id": "huggingface", "name": "Hugging Face", "region": "overseas", "url": "https://huggingface.co"},
    {"id": "iconify", "name": "Iconify", "region": "overseas", "url": "https://iconify.design"},
    {"id": "instructor-ai", "name": "Instructor", "region": "overseas", "url": "https://python.useinstructor.com"},
    {"id": "ionic-team", "name": "Ionic", "region": "overseas", "url": "https://ionic.io"},
    {"id": "jetbrains", "name": "JetBrains", "region": "overseas", "url": "https://jetbrains.com"},
    {"id": "jina-ai", "name": "Jina AI", "region": "overseas", "url": "https://jina.ai"},
    {"id": "kotlin-foundation", "name": "Kotlin Foundation", "region": "overseas", "url": "https://kotlinlang.org"},
    {"id": "lancedb", "name": "LanceDB", "region": "overseas", "url": "https://lancedb.com"},
    {"id": "langchain-inc", "name": "LangChain", "region": "overseas", "url": "https://www.langchain.com"},
    {"id": "laravel", "name": "Laravel", "region": "overseas", "url": "https://laravel.com"},
    {"id": "letta-ai", "name": "Letta", "region": "overseas", "url": "https://www.letta.com"},
    {"id": "mem0-ai", "name": "Mem0", "region": "overseas", "url": "https://mem0.ai"},
    {"id": "meta-llama", "name": "Meta Llama", "region": "overseas", "url": "https://llama.meta.com"},
    {"id": "microsoft", "name": "Microsoft", "region": "overseas", "url": "https://microsoft.com"},
    {"id": "minimax", "name": "MiniMax", "region": "domestic", "url": "https://www.minimaxi.com"},
    {"id": "mistral-ai", "name": "Mistral AI", "region": "overseas", "url": "https://mistral.ai"},
    {"id": "modal-labs", "name": "Modal", "region": "overseas", "url": "https://modal.com"},
    {"id": "moonshot-ai", "name": "Moonshot AI", "region": "domestic", "url": "https://www.moonshot.cn"},
    {"id": "morph-llm", "name": "Morph", "region": "overseas", "url": "https://morphllm.com"},
    {"id": "mui", "name": "MUI", "region": "overseas", "url": "https://mui.com"},
    {"id": "n8n-io", "name": "n8n", "region": "overseas", "url": "https://n8n.io"},
    {"id": "naive-ui", "name": "Naive UI", "region": "overseas", "url": "https://www.naiveui.com"},
    {"id": "nestjs", "name": "NestJS", "region": "overseas", "url": "https://nestjs.com"},
    {"id": "novita-ai", "name": "Novita AI", "region": "overseas", "url": "https://novita.ai"},
    {"id": "openai", "name": "OpenAI", "region": "overseas", "url": "https://openai.com"},
    {"id": "openhands-ai", "name": "OpenHands", "region": "overseas", "url": "https://www.all-hands.dev"},
    {"id": "oracle-java", "name": "Oracle", "region": "overseas", "url": "https://www.oracle.com/java"},
    {"id": "phind-inc", "name": "Phind", "region": "overseas", "url": "https://phind.com"},
    {"id": "phoenix-framework", "name": "Phoenix", "region": "overseas", "url": "https://www.phoenixframework.org"},
    {"id": "php-foundation", "name": "The PHP Foundation", "region": "overseas", "url": "https://www.php.net"},
    {"id": "pieces-app", "name": "Pieces", "region": "overseas", "url": "https://pieces.app"},
    {"id": "pinecone-io", "name": "Pinecone", "region": "overseas", "url": "https://www.pinecone.io"},
    {"id": "poolside-ai", "name": "poolside", "region": "overseas", "url": "https://poolside.ai"},
    {"id": "portkey-ai", "name": "Portkey", "region": "overseas", "url": "https://portkey.ai"},
    {"id": "primefaces", "name": "PrimeTek", "region": "overseas", "url": "https://www.primefaces.org"},
    {"id": "promptlayer", "name": "PromptLayer", "region": "overseas", "url": "https://promptlayer.com"},
    {"id": "pydantic", "name": "Pydantic", "region": "overseas", "url": "https://pydantic.dev"},
    {"id": "quasar-team", "name": "Quasar", "region": "overseas", "url": "https://quasar.dev"},
    {"id": "qwik-dev", "name": "Qwik", "region": "overseas", "url": "https://qwik.dev"},
    {"id": "rails-core", "name": "Rails Core Team", "region": "overseas", "url": "https://rubyonrails.org"},
    {"id": "redwoodjs", "name": "RedwoodJS", "region": "overseas", "url": "https://redwoodjs.com"},
    {"id": "replicate-inc", "name": "Replicate", "region": "overseas", "url": "https://replicate.com"},
    {"id": "roo-code-inc", "name": "Roo Code", "region": "overseas", "url": "https://roocode.com"},
    {"id": "ruby-central", "name": "Ruby Central", "region": "overseas", "url": "https://ruby-lang.org"},
    {"id": "sambanova", "name": "SambaNova", "region": "overseas", "url": "https://sambanova.ai"},
    {"id": "same-new", "name": "Same.new", "region": "overseas", "url": "https://same.new"},
    {"id": "scala-lang", "name": "Scala", "region": "overseas", "url": "https://www.scala-lang.org"},
    {"id": "shanghai-ai-lab", "name": "上海 AI Lab", "region": "domestic", "url": "https://www.shlab.org.cn"},
    {"id": "softgen-ai", "name": "Softgen", "region": "overseas", "url": "https://softgen.ai"},
    {"id": "solidjs", "name": "SolidJS", "region": "overseas", "url": "https://www.solidjs.com"},
    {"id": "sourcegraph", "name": "Sourcegraph", "region": "overseas", "url": "https://sourcegraph.com"},
    {"id": "stepfun", "name": "阶跃星辰", "region": "domestic", "url": "https://www.stepfun.com"},
    {"id": "steve-donovan", "name": "Steve Schoger", "region": "overseas", "url": "https://heroicons.com"},
    {"id": "supermaven", "name": "Supermaven", "region": "overseas", "url": "https://supermaven.com"},
    {"id": "svelte-team", "name": "Svelte", "region": "overseas", "url": "https://svelte.dev"},
    {"id": "sweep-ai", "name": "Sweep", "region": "overseas", "url": "https://sweep.dev"},
    {"id": "tabler", "name": "Tabler", "region": "overseas", "url": "https://tabler.io"},
    {"id": "tabnine-inc", "name": "Tabnine", "region": "overseas", "url": "https://www.tabnine.com"},
    {"id": "tailwind-labs", "name": "Tailwind Labs", "region": "overseas", "url": "https://tailwindcss.com"},
    {"id": "tamagui", "name": "Tamagui", "region": "overseas", "url": "https://tamagui.dev"},
    {"id": "tauri-apps", "name": "Tauri", "region": "overseas", "url": "https://tauri.app"},
    {"id": "tempolabs", "name": "Tempo Labs", "region": "overseas", "url": "https://tempolabs.ai"},
    {"id": "tencent-cloud", "name": "腾讯云", "region": "domestic", "url": "https://cloud.tencent.com"},
    {"id": "tencent-codebuddy", "name": "腾讯", "region": "domestic", "url": "https://copilot.tencent.com"},
    {"id": "tencent-hunyuan", "name": "腾讯", "region": "domestic", "url": "https://cloud.tencent.com/product/hunyuan"},
    {"id": "tii-falcon", "name": "Technology Innovation Institute", "region": "overseas", "url": "https://falconllm.tii.ae"},
    {"id": "together-ai-inc", "name": "Together AI", "region": "overseas", "url": "https://www.together.ai"},
    {"id": "tokio-axum", "name": "Tokio", "region": "overseas", "url": "https://github.com/tokio-rs/axum"},
    {"id": "tongyi", "name": "通义", "region": "domestic", "url": "https://tongyi.aliyun.com"},
    {"id": "turbopuffer", "name": "Turbopuffer", "region": "overseas", "url": "https://turbopuffer.com"},
    {"id": "unstructured-io", "name": "Unstructured", "region": "overseas", "url": "https://unstructured.io"},
    {"id": "upstage", "name": "Upstage", "region": "overseas", "url": "https://upstage.ai"},
    {"id": "vercel-inc", "name": "Vercel", "region": "overseas", "url": "https://vercel.com"},
    {"id": "vespa-ai", "name": "Vespa", "region": "overseas", "url": "https://vespa.ai"},
    {"id": "vllm-inc", "name": "vLLM", "region": "overseas", "url": "https://vllm.ai"},
    {"id": "vmware-spring", "name": "VMware Tanzu", "region": "overseas", "url": "https://spring.io"},
    {"id": "void-editor", "name": "Void", "region": "overseas", "url": "https://voideditor.com"},
    {"id": "volcengine", "name": "火山引擎", "region": "domestic", "url": "https://www.volcengine.com"},
    {"id": "vuetify-team", "name": "Vuetify", "region": "overseas", "url": "https://vuetifyjs.com"},
    {"id": "warp-dev", "name": "Warp", "region": "overseas", "url": "https://www.warp.dev"},
    {"id": "weaviate-io", "name": "Weaviate", "region": "overseas", "url": "https://weaviate.io"},
    {"id": "xai", "name": "xAI", "region": "overseas", "url": "https://x.ai"},
    {"id": "zed-industries", "name": "Zed Industries", "region": "overseas", "url": "https://zed.dev"},
    {"id": "zhipu", "name": "智谱", "region": "domestic", "url": "https://zhipuai.cn"},
    {"id": "zhipu-codegeex", "name": "智谱", "region": "domestic", "url": "https://codegeex.cn"},
    {"id": "zig-lang", "name": "Zig Software Foundation", "region": "overseas", "url": "https://ziglang.org"},
    {"id": "zilliz", "name": "Zilliz", "region": "both", "url": "https://zilliz.com"},
]

add(mk("cline", "Cline", "coding-ide-agent", "ide-extension", "VS Code 开源自主编码 Agent 扩展", "https://cline.bot",
    "Cline 是 VS Code 上的开源 AI 编码助手，可在编辑器内自主读写文件、运行终端并规划多步任务，支持接入 Claude/GPT 等模型 API。", "希望在 VS Code 内获得接近 Cursor 的 Agent 体验、又需完全掌控模型与数据流向的团队，适合作为 Cursor 的开源替代试点。", "自主模式可能误改多文件；务必启用 Git 快照并限制 shell 权限，生产仓库建议人工 review 每一批 diff。",
    region="overseas", vendor="cline-inc", pricing="freemium",
    pitfalls=["自主模式可能误改多文件；务必启用 Git 快照并限制 shell 权限，生产仓库…"]))
link("cline-e0", "cline", "cursor", "open_source_alternative_to")
add(mk("zed", "Zed", "coding-ide-agent", "native-ide", "Rust 原生高性能协作 IDE", "https://zed.dev",
    "Zed 是用 Rust 编写的原生 IDE，内置多人协作、低延迟编辑与 AI 补全，强调极致性能与现代 UX，支持 LSP 与远程开发。", "追求编辑器响应速度与轻量体验、且愿意尝试非 VS Code 生态的开发者；与 Rust/TS 项目搭配体验突出。", "插件生态仍小于 VS Code；团队若深度依赖特定 JetBrains 插件需评估迁移成本。",
    region="overseas", vendor="zed-industries", pricing="freemium",
    pitfalls=["插件生态仍小于 VS Code；团队若深度依赖特定 JetBrains 插件需评…"]))
link("zed-e0", "zed", "cursor", "alternative_to")
add(mk("gemini-cli", "Gemini CLI", "coding-cli-agent", "terminal-agent", "Google 终端 Gemini 编码助手", "https://github.com/google-gemini/gemini-cli",
    "Gemini CLI 是 Google 推出的终端 AI 编码工具，可在命令行中对话、读写项目文件并执行 shell，深度集成 Gemini 模型能力。", "偏好终端工作流、已使用 Google Cloud/Gemini API 的开发者；适合脚本化与 CI Adjacent 的编码任务。", "终端 Agent 权限过大时可能执行破坏性命令；建议沙箱环境试用并限制 API key 权限范围。",
    region="overseas", vendor="google-deepmind", pricing="freemium",
    pitfalls=["终端 Agent 权限过大时可能执行破坏性命令；建议沙箱环境试用并限制 API …"]))
link("gemini-cli-e0", "gemini-cli", "claude-code", "alternative_to")
add(mk("tongyi-lingma", "通义灵码", "coding-ide-agent", "ide-extension", "阿里云通义系 IDE 智能编码助手", "https://tongyi.aliyun.com/lingma",
    "通义灵码是阿里云推出的 AI 编程助手，支持 VS Code/JetBrains 插件，提供代码补全、单元测试生成与仓库级问答，模型基于通义系列。", "国内团队使用阿里云生态、需要合规本地化模型与中文代码理解时首选；与 Java/前端混合栈兼容良好。", "企业版与公有云 API 配额需提前规划；复杂跨仓库重构能力仍弱于 Cursor Agent 模式。",
    region="domestic", vendor="tongyi", pricing="freemium",
    pitfalls=["企业版与公有云 API 配额需提前规划；复杂跨仓库重构能力仍弱于 Cursor …"]))
link("tongyi-lingma-e0", "tongyi-lingma", "github-copilot", "domestic_equivalent_of")
add(mk("codegeex", "CodeGeeX", "coding-ide-agent", "ide-extension", "智谱开源多语言代码大模型助手", "https://codegeex.cn",
    "CodeGeeX 由智谱 AI 维护，提供 IDE 插件与 API，覆盖 100+ 语言代码补全、解释与生成，支持私有化部署选项。", "需要中文友好、可本地或私有化部署的 Copilot 替代方案时考虑；教育科研场景使用广泛。", "最新模型能力与 GPT-4o/Claude 仍有差距；复杂架构设计任务需人工校验输出。",
    region="domestic", vendor="zhipu-codegeex", pricing="freemium",
    pitfalls=["最新模型能力与 GPT-4o/Claude 仍有差距；复杂架构设计任务需人工校验…"]))
link("codegeex-e0", "codegeex", "github-copilot", "domestic_equivalent_of")
add(mk("comate", "Comate", "coding-ide-agent", "ide-extension", "百度文心驱动的智能编程助手", "https://comate.baidu.com",
    "Comate 是百度基于文心大模型推出的 IDE 插件，支持代码补全、注释生成、单测与智能调试，深度集成百度开发者生态。", "国内 Java/前端团队、已采购百度云或偏好国产模型合规路线时可评估；对个人开发者有免费额度。", "插件仅支持主流 IDE；Agent 多文件编排能力仍在快速迭代，生产环境需 code review。",
    region="domestic", vendor="baidu-comate", pricing="freemium",
    pitfalls=["插件仅支持主流 IDE；Agent 多文件编排能力仍在快速迭代，生产环境需 co…"]))
link("comate-e0", "comate", "github-copilot", "domestic_equivalent_of")
add(mk("base44", "Base44", "coding-cloud-builder", "ai-app-builder", "自然语言生成全栈 Web 应用", "https://base44.com",
    "Base44 是 AI 驱动的应用构建平台，用户用自然语言描述需求即可生成前后端代码与部署，面向非工程师与快速原型场景。", "产品经理或创始人需要在数小时内验证 SaaS 想法、且可接受后续手工 refine 代码时使用。", "生成代码质量与可维护性参差；上线前必须安全审计、替换硬编码密钥并接入正规 CI。",
    region="overseas", vendor="base44-inc", pricing="subscription",
    pitfalls=["生成代码质量与可维护性参差；上线前必须安全审计、替换硬编码密钥并接入正规 CI。"]))
link("base44-e0", "base44", "lovable", "alternative_to")
add(mk("amazon-q", "Amazon Q Developer", "coding-ide-agent", "cloud-copilot", "AWS 官方 AI 开发助手", "https://aws.amazon.com/q/developer",
    "Amazon Q Developer 集成于 JetBrains/VS Code 与 AWS 控制台，提供代码补全、安全扫描与基础设施代码建议，深度理解 AWS API。", "重度 AWS 用户、需要在 IaC 与应用代码间获得上下文感知建议的云端团队优先考虑。", "非 AWS 技术栈收益有限；企业合规需确认数据是否用于模型训练及区域可用性。",
    region="overseas", vendor="amazon", pricing="freemium",
    pitfalls=["非 AWS 技术栈收益有限；企业合规需确认数据是否用于模型训练及区域可用性。"]))
link("amazon-q-e0", "amazon-q", "github-copilot", "alternative_to")
add(mk("tabnine", "Tabnine", "coding-ide-agent", "ide-extension", "企业级隐私优先 AI 代码补全", "https://www.tabnine.com",
    "Tabnine 提供 IDE 内 AI 补全，强调企业私有化与零数据留存选项，支持多种本地与云端模型后端。", "金融/医疗等对代码外泄敏感、需要 on-prem 或 VPC 部署 Copilot 能力的组织适合评估。", "Agent 与多文件编辑能力弱于 Cursor/Cline；更多定位补全而非自主编程。",
    region="overseas", vendor="tabnine-inc", pricing="subscription",
    pitfalls=["Agent 与多文件编辑能力弱于 Cursor/Cline；更多定位补全而非自主…"]))
link("tabnine-e0", "tabnine", "github-copilot", "alternative_to")
add(mk("jetbrains-ai", "JetBrains AI Assistant", "coding-ide-agent", "native-ide", "JetBrains IDE 内置 AI 助手", "https://www.jetbrains.com/ai",
    "JetBrains AI Assistant 深度集成 IntelliJ/PyCharm/WebStorm 等 IDE，提供聊天、补全、提交信息生成与上下文感知重构建议。", "已全面使用 JetBrains 系 IDE 的 Java/Kotlin/Python 团队，希望避免额外安装 VS Code 插件时自然选用。", "按 IDE 席位计费成本需测算；与 Cursor 等跨编辑器 Agent 相比多文件任务编排能力有限。",
    region="overseas", vendor="jetbrains", pricing="subscription",
    pitfalls=["按 IDE 席位计费成本需测算；与 Cursor 等跨编辑器 Agent 相比多…"]))
link("jetbrains-ai-e0", "jetbrains-ai", "github-copilot", "alternative_to")
add(mk("sourcegraph-amp", "Sourcegraph Amp", "coding-ide-agent", "agent-platform", "面向大型代码库的 AI 编码 Agent", "https://sourcegraph.com/amp",
    "Sourcegraph Amp 基于 Sourcegraph 代码搜索与上下文引擎，提供跨仓库 AI Agent，擅长理解巨型 monorepo 与生成精准变更。", "拥有超大规模代码库、需要跨服务理解业务逻辑的企业工程团队；与 Cody 历史能力一脉相承。", "部署与索引成本高；小团队可能用 Cursor + 良好文档即可覆盖需求。",
    region="overseas", vendor="sourcegraph", pricing="subscription",
    pitfalls=["部署与索引成本高；小团队可能用 Cursor + 良好文档即可覆盖需求。"]))
link("sourcegraph-amp-e0", "sourcegraph-amp", "cursor", "alternative_to")
add(mk("roo-code", "Roo Code", "coding-ide-agent", "ide-extension", "VS Code 多模式 AI 编码 Agent", "https://roocode.com",
    "Roo Code 是 VS Code 扩展，提供 Architect/Code/Debug 等多角色 Agent 模式，支持 MCP 与多种 LLM 后端。", "已在 VS Code 工作且希望比 Cline 更结构化角色分工的开发者；适合实验 MCP 工具链集成。", "模式过多可能增加认知负担；复杂任务仍需人工拆分验收标准。",
    region="overseas", vendor="roo-code-inc", pricing="freemium",
    pitfalls=["模式过多可能增加认知负担；复杂任务仍需人工拆分验收标准。"]))
link("roo-code-e0", "roo-code", "cline", "alternative_to")
add(mk("void-editor", "Void", "coding-ide-agent", "native-ide", "开源 Cursor 风格 AI IDE", "https://voideditor.com",
    "Void 是基于 VS Code 开源分支的 AI 原生 IDE，强调隐私、本地模型支持与 Cursor 类似的 Agent 交互体验。", "关注数据主权、希望本地 Ollama/LM Studio 驱动编码 Agent 的个人开发者可试用。", "项目较新，稳定性与扩展兼容需持续跟踪；企业 SLA 支持有限。",
    region="overseas", vendor="void-editor", pricing="open-source",
    pitfalls=["项目较新，稳定性与扩展兼容需持续跟踪；企业 SLA 支持有限。"]))
link("void-editor-e0", "void-editor", "cursor", "open_source_alternative_to")
add(mk("augment-code", "Augment Code", "coding-ide-agent", "ide-extension", "企业代码库上下文 AI 助手", "https://www.augmentcode.com",
    "Augment Code 面向企业工程团队，索引私有代码库并提供高上下文补全与 Agent，强调安全合规与大型 monorepo 理解。", "数百人工程组织需要比通用 Copilot 更懂内部框架与 API 的助手时可 POC。", "索引构建耗时；权限模型配置不当可能泄露敏感模块。",
    region="overseas", vendor="augment-code", pricing="subscription",
    pitfalls=["索引构建耗时；权限模型配置不当可能泄露敏感模块。"]))
link("augment-code-e0", "augment-code", "cursor", "alternative_to")
add(mk("supermaven", "Supermaven", "coding-ide-agent", "ide-extension", "超快上下文窗口代码补全", "https://supermaven.com",
    "Supermaven 以超大上下文补全著称，在 VS Code/JetBrains 中提供低延迟 inline 建议，后被 Cursor 团队技术关注。", "需要极长文件内连贯补全、写作大量样板代码的开发者；适合与更强 Agent 工具并用。", "已被 Cursor 部分吸收，独立产品路线图需关注；Agent 能力非其核心。",
    region="overseas", vendor="supermaven", pricing="subscription",
    pitfalls=["已被 Cursor 部分吸收，独立产品路线图需关注；Agent 能力非其核心。"]))
link("supermaven-e0", "supermaven", "github-copilot", "alternative_to")
add(mk("warp", "Warp", "coding-cli-agent", "terminal-ide", "AI 原生 Rust 终端", "https://www.warp.dev",
    "Warp 是用 Rust 重写的现代终端，内置 AI 命令搜索、工作流块与协作功能，将 shell 体验产品化。", "CLI 重度用户希望减少记忆命令、用自然语言生成 pipeline 时可日常替换 iTerm/Windows Terminal。", "AI 功能需联网账户；团队脚本 secret 可能误入 prompt，需教育红线条款。",
    region="overseas", vendor="warp-dev", pricing="freemium",
    pitfalls=["AI 功能需联网账户；团队脚本 secret 可能误入 prompt，需教育红线…"]))
link("warp-e0", "warp", "gemini-cli", "alternative_to")
add(mk("openhands", "OpenHands", "coding-cli-agent", "open-agent", "开源自主软件工程 Agent", "https://www.all-hands.dev",
    "OpenHands 是开源 AI 软件工程师 Agent，可自主浏览代码、运行测试并提交 PR，支持 Docker 沙箱隔离。", "研究型团队或希望自托管 Devin 类 Agent、完全掌控模型与环境的组织适合部署试验。", "沙箱逃逸与误操作风险需运维关注；生产自动 merge 必须禁用或严格门禁。",
    region="overseas", vendor="openhands-ai", pricing="open-source",
    pitfalls=["沙箱逃逸与误操作风险需运维关注；生产自动 merge 必须禁用或严格门禁。"]))
link("openhands-e0", "openhands", "cursor", "open_source_alternative_to")
add(mk("phind", "Phind", "coding-cli-agent", "search-agent", "面向开发者的 AI 搜索引擎", "https://phind.com",
    "Phind 结合搜索与 LLM，为编程问题提供带引用来源的答案，支持追问与代码片段生成，定位开发者专属 Perplexity。", "调试陌生 API、快速理解报错栈或调研技术选型时作为 Google/StackOverflow 补充。", "答案可能过时或幻觉；关键决策仍需查阅官方文档与源码。",
    region="overseas", vendor="phind-inc", pricing="freemium",
    pitfalls=["答案可能过时或幻觉；关键决策仍需查阅官方文档与源码。"]))
link("phind-e0", "phind", "gpt", "commonly_used_with")
add(mk("factory", "Factory", "coding-cloud-builder", "ai-dev-platform", "Droids 驱动的企业 AI 工程平台", "https://factory.ai",
    "Factory 提供「Droids」自主 Agent 完成 ticket、修 bug 与 feature 开发，面向企业 SDLC 集成与 GitHub/GitLab 工作流。", "工程经理希望 AI 直接消费 Linear/Jira ticket 并开 PR 的自动化实验阶段可试点。", "自动 PR 质量参差；需严格 CI、测试覆盖与人审才能 merge 到 main。",
    region="overseas", vendor="factory-ai", pricing="subscription",
    pitfalls=["自动 PR 质量参差；需严格 CI、测试覆盖与人审才能 merge 到 main…"]))
link("factory-e0", "factory", "github-actions", "integrates_with")
add(mk("sweep", "Sweep", "coding-ide-agent", "github-bot", "GitHub Issue 转 PR 的 AI Junior Dev", "https://sweep.dev",
    "Sweep 监听 GitHub Issue 与评论，自主生成代码变更并开 PR，适合处理明确、范围受限的 bugfix 与小 feature。", "开源项目或中小团队希望 offload 简单 maintenance task、维护者时间有限时使用。", "复杂架构变更容易失败；Issue 描述必须足够精确并附带测试期望。",
    region="overseas", vendor="sweep-ai", pricing="freemium",
    pitfalls=["复杂架构变更容易失败；Issue 描述必须足够精确并附带测试期望。"]))
link("sweep-e0", "sweep", "github-actions", "integrates_with")
add(mk("poolside", "poolside", "coding-ide-agent", "enterprise-copilot", "企业自托管代码大模型平台", "https://poolside.ai",
    "poolside 训练面向软件的专用基础模型并交付企业私有化 Copilot，强调安全隔离与大型代码语料微调。", "超大型金融机构或国防相关项目需要完全内网代码 AI 且预算充足时可接触销售评估。", "公开信息较少、采购周期长；中小团队不适合作为首选 Copilot。",
    region="overseas", vendor="poolside-ai", pricing="subscription",
    pitfalls=["公开信息较少、采购周期长；中小团队不适合作为首选 Copilot。"]))
link("poolside-e0", "poolside", "github-copilot", "alternative_to")
add(mk("create-xyz", "Create", "coding-cloud-builder", "mobile-web-builder", "AI 生成 React Native/Web 应用", "https://www.create.xyz",
    "Create 允许用户用 prompt 生成可运行的移动端与 Web 应用原型，集成常见后端与 UI 模板，面向 indie hacker。", "独立开发者快速验证 App 想法、需要可分享 demo 时在几小时内出 MVP。", "生成代码定制深度有限；规模扩大后通常需重写为正规 Next.js/Expo 工程。",
    region="overseas", vendor="create-xyz", pricing="subscription",
    pitfalls=["生成代码定制深度有限；规模扩大后通常需重写为正规 Next.js/Expo 工程…"]))
link("create-xyz-e0", "create-xyz", "lovable", "alternative_to")
add(mk("softgen", "Softgen", "coding-cloud-builder", "fullstack-builder", "AI 全栈 Web 应用生成器", "https://softgen.ai",
    "Softgen 从自然语言生成含 Firebase/Stripe 集成的全栈 Web 应用，强调可视化编辑与一键部署。", "非技术创始人构建 SaaS MVP、可接受 Firebase 后端锁定换取速度时使用。", "Firebase 迁移成本高；安全规则与支付 webhook 必须人工审查。",
    region="overseas", vendor="softgen-ai", pricing="subscription",
    pitfalls=["Firebase 迁移成本高；安全规则与支付 webhook 必须人工审查。"]))
link("softgen-e0", "softgen", "firebase", "commonly_used_with")
add(mk("tempolabs", "Tempo", "coding-cloud-builder", "react-builder", "可视化 React 组件 AI 编辑器", "https://tempolabs.ai",
    "Tempo 提供面向 React 的可视化编辑器，结合 AI 生成与拖拽微调组件，输出可直接并入代码库的 TSX。", "设计工程师与前端协作、需在 Figma 与代码间快速迭代 marketing 组件时使用。", "复杂状态管理与路由仍需手写；不适合作为整应用架构工具。",
    region="overseas", vendor="tempolabs", pricing="freemium",
    pitfalls=["复杂状态管理与路由仍需手写；不适合作为整应用架构工具。"]))
link("tempolabs-e0", "tempolabs", "react", "commonly_used_with")
add(mk("databutton", "Databutton", "coding-cloud-builder", "python-app-builder", "Python 数据应用 AI 构建平台", "https://databutton.com",
    "Databutton 让用户用 AI 在浏览器中构建 Python 数据应用与 API，内置托管与 secrets 管理，面向数据科学家。", "快速搭建内部数据分析 dashboard 或 ML demo、团队 Python 技能强但前端弱时适用。", "厂商锁定与导出路径需提前验证；生产 SLA 依赖平台可用性。",
    region="overseas", vendor="databutton", pricing="subscription",
    pitfalls=["厂商锁定与导出路径需提前验证；生产 SLA 依赖平台可用性。"]))
link("databutton-e0", "databutton", "python", "commonly_used_with")
add(mk("codebuddy", "CodeBuddy", "coding-ide-agent", "ide-extension", "腾讯云 AI 编程助手", "https://copilot.tencent.com",
    "CodeBuddy 是腾讯云推出的 AI 编码助手，支持 VS Code/JetBrains，提供补全、评审与技术问答，集成腾讯混元等模型。", "已使用腾讯云、需要国产化合规 Copilot 的国内团队可评估；对个人开发者免费开放基础能力。", "国际化项目英文代码表现需实测；复杂 Agent 任务建议搭配 Cursor 人工复核。",
    region="domestic", vendor="tencent-codebuddy", pricing="freemium",
    pitfalls=["国际化项目英文代码表现需实测；复杂 Agent 任务建议搭配 Cursor 人工…"]))
link("codebuddy-e0", "codebuddy", "github-copilot", "domestic_equivalent_of")
add(mk("marscode", "MarsCode", "coding-ide-agent", "ide-extension", "字节跳动 AI 编程助手", "https://www.marscode.com",
    "MarsCode 由字节跳动推出，提供 IDE 插件与云端 AI 开发环境，支持代码补全、解释与云端项目托管。", "国内字节系技术栈团队、需要中文语境友好补全与在线 IDE 时使用；与豆包模型协同。", "海外访问与模型政策需确认；企业版功能与数据驻留条款要法务审核。",
    region="domestic", vendor="bytedance-marscode", pricing="freemium",
    pitfalls=["海外访问与模型政策需确认；企业版功能与数据驻留条款要法务审核。"]))
link("marscode-e0", "marscode", "cursor", "domestic_equivalent_of")
add(mk("pieces", "Pieces", "coding-ide-agent", "dev-productivity", "开发者片段管理与上下文 AI", "https://pieces.app",
    "Pieces 跨 IDE 保存代码片段、截图与链接，并用本地/云端 AI 建立可搜索的开发者记忆库，增强 Copilot 上下文。", "工程师频繁复用 boilerplate、需要在多设备间同步「可检索记忆」时作为 Copilot 增强层。", "额外客户端增加维护成本；敏感代码片段本地加密策略需团队规范。",
    region="overseas", vendor="pieces-app", pricing="freemium",
    pitfalls=["额外客户端增加维护成本；敏感代码片段本地加密策略需团队规范。"]))
link("pieces-e0", "pieces", "cursor", "commonly_used_with")
add(mk("blackbox", "Blackbox AI", "coding-ide-agent", "ide-extension", "多模型 AI 代码搜索与生成", "https://www.blackbox.ai",
    "Blackbox AI 提供 IDE 插件与 Web，支持代码搜索、自动补全与从截图/Voice 生成代码，聚合多家模型 API。", "需要快速尝试多种模型、或从 UI mockup 生成前端代码的原型阶段使用。", "免费层速率限制严格；代码质量需人工审查，勿直接用于生产。",
    region="overseas", vendor="blackbox-ai", pricing="freemium",
    pitfalls=["免费层速率限制严格；代码质量需人工审查，勿直接用于生产。"]))
link("blackbox-e0", "blackbox", "github-copilot", "alternative_to")
add(mk("goose", "Goose", "coding-cli-agent", "local-agent", "Block 开源本地 AI Agent 框架", "https://block.github.io/goose",
    "Goose 是 Block 开源的本地 AI Agent，可扩展 MCP 工具，在终端自主完成开发任务，强调开发者可控与可扩展。", "希望自研 Agent 工具链、基于 MCP 组装内部开发自动化的平台团队可 fork 定制。", "需要自行维护模型与工具连接；开箱体验不如商业 Cursor。",
    region="overseas", vendor="goose-ai", pricing="open-source",
    pitfalls=["需要自行维护模型与工具连接；开箱体验不如商业 Cursor。"]))
link("goose-e0", "goose", "cline", "alternative_to")
add(mk("emergent", "Emergent", "coding-cloud-builder", "agent-builder", "全栈 AI Agent 应用构建平台", "https://emergent.sh",
    "Emergent 让用户通过对话构建含前后端与 Agent 逻辑的 Web 应用，自动处理部署与数据库，面向 vibe coding 场景。", "创业者希望「一句话出产品」并快速拿到可分享 URL 做用户访谈时使用。", "底层抽象黑盒；规模增长后调试与性能优化困难，需计划迁移到 Next.js 等正规栈。",
    region="overseas", vendor="emergent-labs", pricing="subscription",
    pitfalls=["底层抽象黑盒；规模增长后调试与性能优化困难，需计划迁移到 Next.js 等正规…"]))
link("emergent-e0", "emergent", "lovable", "alternative_to")
add(mk("blink-new", "Blink.new", "coding-cloud-builder", "instant-deploy", "Prompt 到部署的一键 Web 应用", "https://blink.new",
    "Blink.new 强调从自然语言 prompt 到在线 URL 的极速路径，自动生成 UI 与简单后端并托管。", "黑客松、营销落地页或 internal tool 需要在分钟级验证想法时试用。", "定制化与 SEO/无障碍几乎需重做；勿直接承载付费核心业务。",
    region="overseas", vendor="blink-new", pricing="freemium",
    pitfalls=["定制化与 SEO/无障碍几乎需重做；勿直接承载付费核心业务。"]))
link("blink-new-e0", "blink-new", "v0", "alternative_to")
add(mk("same-new", "Same.new", "coding-cloud-builder", "clone-builder", "克隆并改造现有 Web 应用", "https://same.new",
    "Same.new 允许用户输入参考 URL 或描述，AI 生成相似功能的新应用，适合快速 mimic 竞品交互做 A/B 原型。", "产品团队需要「像 X 但改 Y」的 demo 给 stakeholder 评审，时间窗口极短时使用。", "版权与商标风险需法务把关；生成代码未必生产可用。",
    region="overseas", vendor="same-new", pricing="freemium",
    pitfalls=["版权与商标风险需法务把关；生成代码未必生产可用。"]))
link("same-new-e0", "same-new", "lovable", "alternative_to")
add(mk("morph", "Morph", "coding-ide-agent", "apply-model", "专为代码编辑优化的 Apply 模型", "https://morphllm.com",
    "Morph 提供针对 unified diff apply 优化的模型 API，供 Agent 工具快速可靠地将补丁合并到源文件，减少 merge 失败。", "自研编码 Agent 或 IDE 插件、受困于 GPT apply 不稳定时作为专用后端接入。", "仅解决 apply 环节；规划与生成仍需主 LLM，整体架构复杂度上升。",
    region="overseas", vendor="morph-llm", pricing="usage",
    pitfalls=["仅解决 apply 环节；规划与生成仍需主 LLM，整体架构复杂度上升。"]))
link("morph-e0", "morph", "cursor", "integrates_with")
add(llm_family("grok", "Grok", "xai", "https://x.ai", "xAI 实时联网对话大模型系列",
    "Grok 是 xAI 推出的大语言模型家族，强调实时信息访问、幽默风格与 X 平台生态集成，面向消费者与 API 开发者。", "需要实时新闻/社交信号、或已在 X Premium 订阅生态内的用户；API 可用于海外 SaaS 对话功能。", "政策与内容审核标准随地区变化；国内直连与合规需自行评估，生产环境注意 hallucination。",
    region="overseas", pricing="usage", pitfalls=["政策与内容审核标准随地区变化；国内直连与合规需自行评估，生产环境注意 hallu…"]))
link("grok-e0", "grok", "gpt", "alternative_to")
add(llm_family("mistral", "Mistral", "mistral-ai", "https://mistral.ai", "欧洲开源友好 LLM 模型家族",
    "Mistral AI 发布的多款开源与商用 LLM 家族，以高效 MoE 架构与欧洲数据合规定位著称，覆盖指令遵循与代码场景。", "希望欧洲数据驻留、或偏好 Apache/MIT 开源权重可自托管的团队；与 vLLM/Ollama 本地部署搭配常见。", "旗舰与开源型号能力差距大；选型需对照 context length 与 function calling 支持矩阵。",
    region="overseas", pricing="usage", pitfalls=["旗舰与开源型号能力差距大；选型需对照 context length 与 func…"]))
link("mistral-e0", "mistral", "llama", "alternative_to")
add(llm_family("llama", "Llama", "meta-llama", "https://llama.meta.com", "Meta 开源大模型家族",
    "Llama 是 Meta 发布的开源 LLM 系列，社区生态最繁荣之一，广泛用于微调、本地推理与云 API 托管。", "需要可自托管、可微调的基础模型做垂直领域或成本优化时首选；与 Hugging Face 工具链天然契合。", "许可证对超大规模商用有限制；安全对齐不如闭源 frontier，需额外 guardrails。",
    region="overseas", pricing="open-source", pitfalls=["许可证对超大规模商用有限制；安全对齐不如闭源 frontier，需额外 guar…"]))
link("llama-e0", "llama", "gpt", "open_source_alternative_to")
add(llm_family("doubao", "豆包", "volcengine", "https://www.volcengine.com/product/doubao", "字节火山引擎豆包大模型家族",
    "豆包是字节跳动火山引擎推出的大模型系列，覆盖对话、代码与多模态，深度集成国内云与企业应用生态。", "国内 SaaS、已使用火山引擎或需备案大模型 API 的企业应用优先考虑；中文语境表现稳定。", "国际场景与英文长文能力需 benchmark；模型版本迭代快，API 字段需锁定版本号。",
    region="domestic", pricing="usage", pitfalls=["国际场景与英文长文能力需 benchmark；模型版本迭代快，API 字段需锁定…"]))
link("doubao-e0", "doubao", "qwen", "alternative_to")
add(llm_family("minimax", "MiniMax", "minimax", "https://www.minimaxi.com", "MiniMax 文本与语音大模型家族",
    "MiniMax 提供 abab 系列大模型与语音能力，面向国内 ToB 与消费级应用，强调长上下文与角色扮演。", "国内互动娱乐、客服与语音合成场景；需要中文角色一致性或多模态产品时评估。", "海外节点与文档相对少；企业采购需确认 SLA 与数据不出境条款。",
    region="domestic", pricing="usage", pitfalls=["海外节点与文档相对少；企业采购需确认 SLA 与数据不出境条款。"]))
link("minimax-e0", "minimax", "glm", "alternative_to")
add(llm_family("wenxin", "文心", "baidu", "https://cloud.baidu.com/product/wenxinworkshop", "百度文心大模型家族",
    "文心是百度ERNIE 系列大模型品牌，覆盖千亿参数旗舰与轻量模型，集成千帆平台与企业工具链。建议结合团队现有栈、合规要求与成本模型做小规模 POC 后再定稿。", "百度云存量客户、需要国内合规大模型与搜索增强（RAG）一体方案时选用。", "国际化与开源权重有限；API 配额与计费模式随活动变化需财务对齐。",
    region="domestic", pricing="usage", pitfalls=["国际化与开源权重有限；API 配额与计费模式随活动变化需财务对齐。"]))
link("wenxin-e0", "wenxin", "qwen", "alternative_to")
add(llm_family("phi", "Phi", "microsoft", "https://azure.microsoft.com/products/phi", "Microsoft 小型高效 SLM 家族",
    "Phi 是 Microsoft Research 推出的小语言模型系列，参数小但推理与代码能力突出，适合端侧与低成本推理。", "边缘设备、手机端 AI、或需要极低延迟/成本的分类与提取任务；与 Azure AI 集成顺滑。", "复杂 Agent 与长上下文任务仍应使用 frontier LLM；小模型幻觉率需评测。",
    region="overseas", pricing="usage", pitfalls=["复杂 Agent 与长上下文任务仍应使用 frontier LLM；小模型幻觉率…"]))
link("phi-e0", "phi", "gemma", "alternative_to")
add(llm_family("gemma", "Gemma", "google-gemma", "https://ai.google.dev/gemma", "Google DeepMind 开源族 · 现至 Gemma 4 · 端侧到 31B",
    "Gemma 是 Google DeepMind 基于 Gemini 技术路线的开源模型系列。当前主力为 Gemma 4（E2B–31B，含 MoE），覆盖端侧到工作站；更早还有 Gemma 2/3 等版本。", "需要 Google 技术背书的开源权重、端侧/本地部署、研究微调或 Apache 2.0 友好许可时优先考虑。", "Gemma 4 起为 Apache 2.0，更早版本仍为 Gemma Terms；不等于 Gemini API 能力，勿直接替代付费 API。",
    region="overseas", pricing="open-source", pitfalls=["Gemma 4 起为 Apache 2.0，更早版本仍为 Gemma Terms；不等于 Gemini API 能力，勿直接替代付费 API。"]))
link("gemma-e0", "gemma", "llama", "alternative_to")
add(llm_family("cohere", "Command", "cohere", "https://cohere.com", "Cohere 企业级 LLM 家族",
    "Cohere 提供 Command 系列模型，专注企业 RAG、检索增强与多语言 embedding 一体，强调数据隐私与私有云部署。", "企业搜索、知识库问答、需要成熟 embed + rerank + generate 全栈的 B2B 场景。", "消费级 chat 体验不如 ChatGPT；定价面向企业，个人开发者成本偏高。",
    region="overseas", pricing="usage", pitfalls=["消费级 chat 体验不如 ChatGPT；定价面向企业，个人开发者成本偏高。"]))
link("cohere-e0", "cohere", "gpt", "alternative_to")
add(llm_family("yi", "Yi", "01-ai", "https://www.lingyiwanwu.com", "零一万物 Yi 开源与商用模型家族",
    "Yi 系列由零一万物发布，含长上下文开源权重与旗舰 API，中英文双语能力均衡，社区微调案例丰富。", "国内团队希望开源可自托管、同时有商业 API 兜底的双轨策略时可选用。", "版本命名较多；部署前确认 license 与参数规模是否匹配硬件。",
    region="both", pricing="usage", pitfalls=["版本命名较多；部署前确认 license 与参数规模是否匹配硬件。"]))
link("yi-e0", "yi", "qwen", "alternative_to")
add(llm_family("hunyuan", "混元", "tencent-hunyuan", "https://cloud.tencent.com/product/hunyuan", "腾讯混元大模型家族",
    "混元是腾讯云推出的大模型系列，覆盖文本、图像与代码，集成腾讯企微、云与企业应用生态。建议结合团队现有栈、合规要求与成本模型做小规模 POC 后再定稿。", "腾讯云客户、需要与微信/企微生态联动或国内合规大模型的一站式方案。", "开源权重有限；跨云迁移需重新评估 API 兼容层。",
    region="domestic", pricing="usage", pitfalls=["开源权重有限；跨云迁移需重新评估 API 兼容层。"]))
link("hunyuan-e0", "hunyuan", "qwen", "alternative_to")
add(llm_family("solar", "Solar", "upstage", "https://upstage.ai", "Upstage Solar 高效 LLM 家族",
    "Solar 是韩国 Upstage 发布的 LLM 系列，在同等规模下强调推理效率与韩语/英语表现，提供 API 与开源变体。", "亚太 SaaS 需要高性价比 API、或评估非中美系模型供应商时考虑。", "中文能力需实测；国内访问延迟与合规需网络评估。",
    region="overseas", pricing="usage", pitfalls=["中文能力需实测；国内访问延迟与合规需网络评估。"]))
link("solar-e0", "solar", "mistral", "alternative_to")
add(llm_family("falcon", "Falcon", "tii-falcon", "https://falconllm.tii.ae", "TII 开源 Falcon LLM 家族",
    "Falcon 由阿联酋 TII 发布，曾以开源许可与大规模预训练语料著称，提供多种参数规模的 base/instruct 模型。", "研究复现、中东/欧洲数据合规偏好、或需要非 Meta/Google 系开源基座时试用。", "社区热度已被 Llama/Qwen 超越；新 project 需确认最新版本维护状态。",
    region="overseas", pricing="open-source", pitfalls=["社区热度已被 Llama/Qwen 超越；新 project 需确认最新版本维护…"]))
link("falcon-e0", "falcon", "llama", "alternative_to")
add(llm_family("internlm", "InternLM", "shanghai-ai-lab", "https://internlm.intern-ai.org.cn", "上海 AI Lab 书生大模型家族",
    "InternLM（书生）是国内顶尖学术机构发布的大模型系列，开源权重与工具链完整，强调推理与代码能力。", "科研、国产化算力环境、或需要可复现论文基座的国内团队。", "企业 SLA 与商业 API 需通过合作方；国际英文 benchmark 需对照评测。",
    region="domestic", pricing="open-source", pitfalls=["企业 SLA 与商业 API 需通过合作方；国际英文 benchmark 需对照…"]))
link("internlm-e0", "internlm", "qwen", "alternative_to")
add(llm_family("baichuan", "Baichuan", "baichuan-inc", "https://www.baichuan-ai.com", "百川智能大模型家族",
    "Baichuan 系列专注中文大模型，提供开源与 API 双轨，在长上下文与医疗/legal 等垂直场景有案例。", "国内垂直行业应用、需要中文优先且可私有化权重的团队。", "国际知名度与生态小于 Qwen/Llama；版本更新需跟踪 API changelog。",
    region="domestic", pricing="usage", pitfalls=["国际知名度与生态小于 Qwen/Llama；版本更新需跟踪 API change…"]))
link("baichuan-e0", "baichuan", "qwen", "alternative_to")
add(llm_family("moonshot", "Moonshot", "moonshot-ai", "https://www.moonshot.cn", "月之暗面 Kimi 同源模型家族",
    "Moonshot（月之暗面）提供长上下文旗舰模型系列，Kimi 助手同款能力通过 API 开放，中文长文理解突出。", "超长文档分析、论文/合同阅读、国内 ToC 产品需要 200K 级上下文时优先考虑。", "海外访问受限；API 定价随上下文长度陡增，需成本模型测算。",
    region="domestic", pricing="usage", pitfalls=["海外访问受限；API 定价随上下文长度陡增，需成本模型测算。"]))
link("moonshot-e0", "moonshot", "kimi", "commonly_used_with")
add(llm_family("step", "Step", "stepfun", "https://www.stepfun.com", "阶跃星辰 Step 大模型家族",
    "Step 是阶跃星辰发布的模型系列，强调多模态与 Agent 能力，面向国内开发者提供 API 与开放平台。", "国内创新型 AI 应用、需要多模态+工具调用一体 API 的初创团队可 POC。", "生态仍在扩张；与成熟云厂商比企业支持体系较新。",
    region="domestic", pricing="usage", pitfalls=["生态仍在扩张；与成熟云厂商比企业支持体系较新。"]))
link("step-e0", "step", "glm", "alternative_to")
add(llm_line("grok-flagship", "Grok 3", "xai", "https://x.ai/api",
    "xAI 当前旗舰 Grok 模型", "Grok 3 是 xAI 旗舰大模型 line，提供最强推理与工具使用能力，面向 X Premium+ 与 API 企业客户。", "需要 xAI 生态内最强对话与实时搜索增强、且可接受 frontier 定价的海外产品。", "实时数据依赖 X 平台；API rate limit 与 region 限制需提前申请配额。",
    region="overseas", pricing="usage", pitfalls=["实时数据依赖 X 平台；API rate limit 与 region 限制需提…"], flagship=True))
link("grok-flagship-part", "grok-flagship", "grok", "part_of")
link("grok-flagship-e0", "grok-flagship", "gpt-4o", "alternative_to")
add(llm_line("mistral-large", "Mistral Large", "mistral-ai", "https://mistral.ai/news/mistral-large",
    "Mistral 商用旗舰 line", "Mistral Large 是 Mistral AI 商用旗舰 line，支持长上下文、function calling 与多语言，适合企业 API 集成。", "欧洲企业替代 GPT-4 类 API、或需要 GDPR 友好供应商时的主力模型。", "与 Mistral Small 价差大；简单任务应路由到小模型控成本。",
    region="overseas", pricing="usage", pitfalls=["与 Mistral Small 价差大；简单任务应路由到小模型控成本。"], flagship=True))
link("mistral-large-part", "mistral-large", "mistral", "part_of")
link("mistral-large-e0", "mistral-large", "claude-sonnet", "alternative_to")
add(llm_line("llama-flagship", "Llama 3.1 405B", "meta-llama", "https://llama.meta.com",
    "Llama 开源旗舰规模 line", "Llama 3.1 405B 是 Meta Llama 家族当前最大开源 instruct line，接近 frontier 能力，可自托管或通过云 API 调用。", "有 GPU 集群或预算购买 Together/Fireworks 托管、希望开源权重可审计的场景。", "405B 推理成本极高；多数产品应优先 70B 或更小 line。",
    region="overseas", pricing="usage", pitfalls=["405B 推理成本极高；多数产品应优先 70B 或更小 line。"], flagship=True))
link("llama-flagship-part", "llama-flagship", "llama", "part_of")
link("llama-flagship-e0", "llama-flagship", "gpt-4o", "alternative_to")
add(llm_line("doubao-flagship", "豆包 Pro", "volcengine", "https://www.volcengine.com/product/doubao",
    "豆包商用旗舰 line", "豆包 Pro 是火山引擎豆包家族旗舰 line，提供最强中文理解与代码能力，面向企业 API 与字节系应用。", "国内生产级 chat/agent 已选火山引擎、需要家族内最强能力时作为 default model。", "务必在控制台锁定 model endpoint 版本；beta 能力可能随时变更。",
    region="domestic", pricing="usage", pitfalls=["务必在控制台锁定 model endpoint 版本；beta 能力可能随时变更…"], flagship=True))
link("doubao-flagship-part", "doubao-flagship", "doubao", "part_of")
link("doubao-flagship-e0", "doubao-flagship", "qwen-max", "alternative_to")
add(llm_line("minimax-flagship", "abab 6.5", "minimax", "https://www.minimaxi.com",
    "MiniMax 旗舰 abab line", "abab 6.5 是 MiniMax 旗舰 line，支持超长上下文与高质量中文对话，广泛用于国内 AI 应用后端。", "国内角色扮演、长文本创作类 App 需要 MiniMax 家族最强表现时使用。", "国际语言与代码 benchmark 需自测；注意 token 计费与上下文分段策略。",
    region="domestic", pricing="usage", pitfalls=["国际语言与代码 benchmark 需自测；注意 token 计费与上下文分段策…"], flagship=True))
link("minimax-flagship-part", "minimax-flagship", "minimax", "part_of")
link("minimax-flagship-e0", "minimax-flagship", "glm-flagship", "alternative_to")
add(llm_line("wenxin-flagship", "ERNIE 4.0", "baidu", "https://cloud.baidu.com/product/wenxinworkshop",
    "文心千帆旗舰 line", "ERNIE 4.0 是文心家族旗舰 line，集成搜索增强与工具调用，面向百度智能云千帆平台企业客户。", "百度云一体化、需要文心最强能力与国内合规审计的企业应用。", "API 与控制台概念较多；新团队建议从官方 SDK quickstart 减少踩坑。",
    region="domestic", pricing="usage", pitfalls=["API 与控制台概念较多；新团队建议从官方 SDK quickstart 减少踩…"], flagship=True))
link("wenxin-flagship-part", "wenxin-flagship", "wenxin", "part_of")
link("wenxin-flagship-e0", "wenxin-flagship", "qwen-max", "alternative_to")
add(llm_line("claude-sonnet", "Claude Sonnet", "anthropic", "https://www.anthropic.com/claude/sonnet",
    "Anthropic 平衡性能与成本 line", "Claude Sonnet 是 Anthropic Claude 家族的高性能 line，在编码、分析与长上下文间取得平衡，Cursor 等工具默认常用。", "日常编码 Agent、企业知识库与批量文档处理需要 quality/cost 平衡时的主力选择。", "与 Opus 相比复杂推理仍弱；敏感数据需确认 Anthropic 企业数据条款。",
    region="overseas", pricing="usage", pitfalls=["与 Opus 相比复杂推理仍弱；敏感数据需确认 Anthropic 企业数据条款…"]))
link("claude-sonnet-part", "claude-sonnet", "claude", "part_of")
link("claude-sonnet-e0", "claude-sonnet", "gpt-4o", "alternative_to")
add(llm_line("gemini-flash", "Gemini Flash", "google-deepmind", "https://ai.google.dev/gemini-api/docs/models/gemini",
    "Google Gemini 低延迟高性价比 line", "Gemini Flash 是 Gemini 家族的速度优化 line，适合高 QPS、低延迟场景，多模态输入成本低于 Pro line。", "聊天机器人默认模型、分类/提取 pipeline、与 Google Cloud 生态集成的 SaaS。", "复杂推理与代码任务应升级 Pro；国内访问 Google API 需网络与合规方案。",
    region="overseas", pricing="usage", pitfalls=["复杂推理与代码任务应升级 Pro；国内访问 Google API 需网络与合规方…"]))
link("gemini-flash-part", "gemini-flash", "gemini", "part_of")
link("gemini-flash-e0", "gemini-flash", "gpt-mini", "alternative_to")
add(llm_line("gpt-mini", "GPT Luna", "openai", "https://openai.com/index/gpt-5-6/",
    "OpenAI 成本档 · Luna", "OpenAI GPT 产品族的成本优化选型档。当前版本为 GPT-5.6 Luna（同代 Terra 为均衡档，Sol 为旗舰）。", "海量用户产品的默认 chat、路由层 fallback、或高并发边缘任务；复杂推理与长链路 Agent 应升级 Sol/Terra。", "能力上限低于 Sol/Terra；关键路径应保留升级路由。",
    region="overseas", pricing="usage", pitfalls=["复杂 Agent / 前沿推理弱于 Sol；关键路径应保留升级路由。"]))
link("gpt-mini-part", "gpt-mini", "gpt", "part_of")
link("gpt-mini-e0", "gpt-mini", "gemini-flash", "alternative_to")
add(llm_line("phi-3", "Phi-3", "microsoft", "https://azure.microsoft.com/products/phi-3",
    "Phi-3 小模型 line", "Phi-3 是 Phi 家族主力 line，3B–14B 参数规模下提供超预期推理能力，适合 SLM 部署与 Azure AI 托管。", "移动端助手、本地 Ollama 部署、或云端高并发低成本的 NLP 微服务。", "不应承担复杂 multi-agent 编排；需与 frontier 模型组合使用。",
    region="overseas", pricing="usage", pitfalls=["不应承担复杂 multi-agent 编排；需与 frontier 模型组合使用…"]))
link("phi-3-part", "phi-3", "phi", "part_of")
link("phi-3-e0", "phi-3", "gemma-4", "alternative_to")
add(llm_line("gemma-4", "Gemma 4", "google-gemma", "https://ai.google.dev/gemma/docs/core/model_card_4",
    "Google 开源旗舰 · E2B–31B / Apache 2.0 · 多模态与端侧可跑", "Gemma 4 是 Gemma 家族当前开源旗舰 line（2026-04 发布），基于 Gemini 3 研究，首次以 Apache 2.0 授权。规格含 E2B / E4B（端侧）、12B Unified、26B A4B MoE 与 31B Dense，支持文本/图像（部分含音频），上下文最高 256K。", "自托管、端侧 Agent、研究微调，或需要明确商业友好开源许可的 Google 技术栈时优先选用。", "31B / 26B MoE 仍需较强 GPU；生产闭源能力请用 Gemini API，勿把 Gemma 4 等同于 Gemini 3。",
    region="overseas", pricing="open-source", pitfalls=["31B / 26B MoE 仍需较强 GPU；生产闭源能力请用 Gemini API，勿把 Gemma 4 等同于 Gemini 3。"], flagship=True))
link("gemma-4-part", "gemma-4", "gemma", "part_of")
link("gemma-4-e0", "gemma-4", "llama", "compatible_with")
add(llm_line("gemma-2", "Gemma 2", "google-gemma", "https://ai.google.dev/gemma/docs/core/model_card_2",
    "上一代开源 line · 9B/27B · 存量部署仍常见", "Gemma 2 是 Gemma 家族上一代开源 line（9B/27B），曾在 HF 热度与自托管场景中广泛使用；当前家族旗舰已切换至 Gemma 4。", "维护存量微调/部署、或对照历史 benchmark 时仍可参考。", "已非家族主力；新项目优先 Gemma 4。27B 仍需较强 GPU；生产 API 更常用 Gemini。",
    region="overseas", pricing="open-source", pitfalls=["已非家族主力；新项目优先 Gemma 4。27B 仍需较强 GPU；生产 API 更常用 Gemini。"]))
link("gemma-2-part", "gemma-2", "gemma", "part_of")
link("gemma-2-e0", "gemma-2", "gemma-4", "alternative_to")
add(llm_line("cohere-command-r", "Command R+", "cohere", "https://cohere.com/command",
    "Cohere RAG 优化旗舰 line", "Command R+ 是 Cohere 面向 RAG 与 tool use 的旗舰 line，内置检索 grounding 与多步推理优化。", "企业知识库 Bot、需要 cite 来源的客服与 internal search 场景。", "通用 chat 创造力不如 GPT；定价按 token+检索组件计费需看清账单。",
    region="overseas", pricing="usage", pitfalls=["通用 chat 创造力不如 GPT；定价按 token+检索组件计费需看清账单。"], flagship=True))
link("cohere-command-r-part", "cohere-command-r", "cohere", "part_of")
link("cohere-command-r-e0", "cohere-command-r", "claude-sonnet", "alternative_to")
add(llm_line("yi-large", "Yi-Large", "01-ai", "https://www.lingyiwanwu.com",
    "零一万物 Yi 旗舰 line", "Yi-Large 是 Yi 家族旗舰 API line，长上下文与双语能力均衡，适合国内出海双语文本产品。", "需要 01.AI API 家族内最强、或 Yi 开源权重微调后的云端 fallback。", "与 Qwen-Max 等竞品需横向 benchmark；注意 API 域名国内访问稳定性。",
    region="both", pricing="usage", pitfalls=["与 Qwen-Max 等竞品需横向 benchmark；注意 API 域名国内访…"], flagship=True))
link("yi-large-part", "yi-large", "yi", "part_of")
link("yi-large-e0", "yi-large", "qwen-max", "alternative_to")
add(llm_line("hunyuan-pro", "混元 Pro", "tencent-hunyuan", "https://cloud.tencent.com/product/hunyuan",
    "腾讯混元旗舰 line", "混元 Pro 是混元家族旗舰 line，支持复杂指令、插件与多模态，深度集成腾讯云与微信生态。建议结合团队现有栈、合规要求与成本模型做小规模 POC 后再定稿。", "腾讯云原生应用、企微 Bot 与游戏/社交类国内产品后端。", "跨平台导出模型困难；锁定腾讯生态后迁移成本需评估。",
    region="domestic", pricing="usage", pitfalls=["跨平台导出模型困难；锁定腾讯生态后迁移成本需评估。"], flagship=True))
link("hunyuan-pro-part", "hunyuan-pro", "hunyuan", "part_of")
link("hunyuan-pro-e0", "hunyuan-pro", "qwen-max", "alternative_to")
add(llm_line("solar-pro", "Solar Pro", "upstage", "https://upstage.ai",
    "Upstage Solar 旗舰 line", "Solar Pro 是 Solar 家族旗舰 API line，韩语英语优化，在多项 benchmark 表现接近 frontier 小模型。", "亚太市场 SaaS 需要非 OpenAI 供应商的主模型备选。", "中文与日文场景需自测；国内直连延迟可能较高。",
    region="overseas", pricing="usage", pitfalls=["中文与日文场景需自测；国内直连延迟可能较高。"], flagship=True))
link("solar-pro-part", "solar-pro", "solar", "part_of")
link("solar-pro-e0", "solar-pro", "mistral-large", "alternative_to")
add(llm_line("falcon-3", "Falcon 3", "tii-falcon", "https://falconllm.tii.ae",
    "Falcon 第三代 line", "Falcon 3 是 Falcon 家族更新 line，改进指令遵循与多语言，继续以开源许可服务研究与政企私有化。", "中东/欧洲政企私有化部署、或学术复现需要 TII 系权重时。", "Hugging Face 社区热度下降；配套工具链不如 Llama 丰富。",
    region="overseas", pricing="open-source", pitfalls=["Hugging Face 社区热度下降；配套工具链不如 Llama 丰富。"]))
link("falcon-3-part", "falcon-3", "falcon", "part_of")
link("falcon-3-e0", "falcon-3", "llama-flagship", "alternative_to")
add(llm_line("internlm-2", "InternLM2", "shanghai-ai-lab", "https://internlm.intern-ai.org.cn",
    "书生第二代开源 line", "InternLM2 是 InternLM 家族主力开源 line，提供 7B–20B 多规格，工具调用与代码能力提升明显。", "国产算力环境微调、高校科研与需要完全开源权重的政务项目。", "商业 API 需第三方；企业 support 不如云厂商一站式。",
    region="domestic", pricing="open-source", pitfalls=["商业 API 需第三方；企业 support 不如云厂商一站式。"]))
link("internlm-2-part", "internlm-2", "internlm", "part_of")
link("internlm-2-e0", "internlm-2", "qwen", "alternative_to")
add(llm_line("baichuan-4", "Baichuan 4", "baichuan-inc", "https://www.baichuan-ai.com",
    "百川第四代 API line", "Baichuan 4 是百川家族最新旗舰 line，中文理解与行业知识增强，面向 API 与行业解决方案。", "医疗、法律等中文垂直 SaaS 需要百川家族最强能力时。", "国际业务英文表现需验证；模型迭代期 API 兼容性留意 deprecation 公告。",
    region="domestic", pricing="usage", pitfalls=["国际业务英文表现需验证；模型迭代期 API 兼容性留意 deprecation …"], flagship=True))
link("baichuan-4-part", "baichuan-4", "baichuan", "part_of")
link("baichuan-4-e0", "baichuan-4", "wenxin-flagship", "alternative_to")
add(llm_line("moonshot-v1", "Moonshot v1", "moonshot-ai", "https://platform.moonshot.cn",
    "月之暗面 API 主力 line", "Moonshot v1 是月之暗面开放平台主力 line，提供 128K 级上下文与稳定中文输出，Kimi 同款引擎。", "国内文档问答、论文辅助与超长文本摘要类应用的后端首选之一。", "超长上下文成本高；应做 chunk 策略而非无脑塞全文。",
    region="domestic", pricing="usage", pitfalls=["超长上下文成本高；应做 chunk 策略而非无脑塞全文。"]))
link("moonshot-v1-part", "moonshot-v1", "moonshot", "part_of")
link("moonshot-v1-e0", "moonshot-v1", "kimi-k3", "alternative_to")
add(llm_line("step-2", "Step-2", "stepfun", "https://platform.stepfun.com",
    "阶跃 Step 第二代 line", "Step-2 是阶跃星辰主力 API line，强调 Agent 工具调用与视觉理解，适合国内创新型 multimodal 应用。", "国内 AI 原生 App 需要阶跃家族当前最强多模态+工具能力。", "平台较新，SDK 示例少于大厂；生产前需压测稳定性。",
    region="domestic", pricing="usage", pitfalls=["平台较新，SDK 示例少于大厂；生产前需压测稳定性。"]))
link("step-2-part", "step-2", "step", "part_of")
link("step-2-e0", "step-2", "glm-flagship", "alternative_to")
add(llm_line("mistral-small", "Mistral Small", "mistral-ai", "https://mistral.ai",
    "Mistral 高性价比 line", "Mistral Small 是 Mistral 家族轻量 line，适合高并发分类、提取与简单 chat，成本显著低于 Large。", "路由层默认模型、欧洲数据合规下的 bulk 任务处理。", "复杂代码生成与 multi-step Agent 应路由到 Large 或 frontier。",
    region="overseas", pricing="usage", pitfalls=["复杂代码生成与 multi-step Agent 应路由到 Large 或 fr…"]))
link("mistral-small-part", "mistral-small", "mistral", "part_of")
link("mistral-small-e0", "mistral-small", "gpt-mini", "alternative_to")
add(llm_line("llama-3-70b", "Llama 3.1 70B", "meta-llama", "https://llama.meta.com",
    "Llama 主力开源 line", "Llama 3.1 70B 是 Llama 家族最均衡的开源 line，性能/成本比极佳，广泛用于自托管与云 API。", "有中等 GPU 资源或购买 inference API、需要开源可审计的主模型时。", "70B 量化后仍占显存；边缘部署应选 8B line。",
    region="overseas", pricing="open-source", pitfalls=["70B 量化后仍占显存；边缘部署应选 8B line。"]))
link("llama-3-70b-part", "llama-3-70b", "llama", "part_of")
add(mk("vllm", "vLLM", "gateway-local", "inference-server", "高吞吐 LLM 推理与服务框架", "https://vllm.ai",
    "vLLM 是开源 LLM 推理引擎，采用 PagedAttention 实现高吞吐低延迟 serving，支持 OpenAI 兼容 API 与多种模型架构。", "自托管 Llama/Qwen 等权重、需要 GPU 集群上 production-grade serving 的 MLOps 团队首选。", "GPU 驱动与 CUDA 版本敏感；多租户隔离与 autoscaling 需自行编排 K8s。",
    region="overseas", pricing="open-source", vendor="vllm-inc", pitfalls=["GPU 驱动与 CUDA 版本敏感；多租户隔离与 autoscaling 需自行…"]))
link("vllm-e0", "vllm", "ollama", "alternative_to")
add(mk("llama-cpp", "llama.cpp", "gateway-local", "local-runtime", "纯 C++ 本地 LLM 推理", "https://github.com/ggerganov/llama.cpp",
    "llama.cpp 是轻量级 C/C++ LLM 推理项目，支持 CPU/GPU 量化与 Apple Silicon，是本地与边缘部署的事实标准之一。", "个人开发者 Mac/PC 本地跑模型、或嵌入式/无 GPU 服务器需要 GGUF 量化推理时。", "不适合大规模并发 serving；生产集群更常用 vLLM/TGI。",
    region="overseas", pricing="open-source", vendor="ggml-org", pitfalls=["不适合大规模并发 serving；生产集群更常用 vLLM/TGI。"]))
link("llama-cpp-e0", "llama-cpp", "ollama", "compatible_with")
add(mk("portkey", "Portkey", "gateway-router", "llm-gateway", "生产级 LLM 网关与可观测", "https://portkey.ai",
    "Portkey 提供 LLM 网关，统一路由多供应商 API、缓存、fallback、成本追踪与 guardrails，面向 enterprise AI 应用。", "生产环境同时用 OpenAI/Anthropic/开源托管、需要统一 observability 与 SLA 路由时。", "又一层 vendor 依赖；简单项目 OpenRouter/LiteLLM 可能足够。",
    region="overseas", pricing="usage", vendor="portkey-ai", pitfalls=["又一层 vendor 依赖；简单项目 OpenRouter/LiteLLM 可能…"]))
link("portkey-e0", "portkey", "litellm", "alternative_to")
add(mk("cloudflare-ai-gateway", "Cloudflare AI Gateway", "gateway-router", "edge-gateway", "边缘 LLM 请求缓存与审计", "https://developers.cloudflare.com/ai-gateway",
    "Cloudflare AI Gateway 在边缘代理 LLM API 调用，提供缓存、rate limit、日志与成本分析，兼容多家上游。", "已用 Cloudflare CDN/WAF、希望在全球边缘统一治理 AI API 出站流量的团队。", "本身不提供模型；上游 key 管理与数据合规仍需自行负责。",
    region="overseas", pricing="freemium", vendor="cloudflare-inc", pitfalls=["本身不提供模型；上游 key 管理与数据合规仍需自行负责。"]))
link("cloudflare-ai-gateway-e0", "cloudflare-ai-gateway", "openrouter", "alternative_to")
add(mk("vercel-ai-gateway", "Vercel AI Gateway", "gateway-router", "edge-gateway", "Vercel 统一 AI 模型路由", "https://vercel.com/docs/ai-gateway",
    "Vercel AI Gateway 为 Next.js/Vercel 应用提供统一模型 endpoint，简化多供应商 key 管理与 usage 追踪。", "Vercel 部署的 AI SaaS、已用 vercel-ai-sdk 且希望账单集中时自然启用。", "绑定 Vercel 生态；自托管或非 Vercel 栈收益有限。",
    region="overseas", pricing="usage", vendor="vercel-inc", pitfalls=["绑定 Vercel 生态；自托管或非 Vercel 栈收益有限。"]))
link("vercel-ai-gateway-e0", "vercel-ai-gateway", "vercel-ai-sdk", "integrates_with")
add(mk("together-ai", "Together AI", "gateway-router", "inference-api", "开源模型云端推理 API", "https://www.together.ai",
    "Together AI 托管数百开源模型（Llama、Qwen 等）的高性能 inference API，并提供 fine-tuning 与 GPU 集群。", "不想自运维 GPU、但需开源模型 API 与微调管道的 AI 初创公司。", "热门模型高峰 latency 波动；关键 SLA 需 reserved capacity 洽谈。",
    region="overseas", pricing="usage", vendor="together-ai-inc", pitfalls=["热门模型高峰 latency 波动；关键 SLA 需 reserved capa…"]))
link("together-ai-e0", "together-ai", "fireworks", "alternative_to")
add(mk("fireworks", "Fireworks AI", "gateway-router", "inference-api", "低延迟开源模型 API 平台", "https://fireworks.ai",
    "Fireworks AI 专注 fast inference API 与 fine-tuning，支持 Llama、Mixtral 等，强调 speed-optimized serving。", "需要比自托管更快上线、且 workload 以开源模型为主的 inference 场景。", "模型清单与定价常更新；复杂 Agent 仍可能需要 frontier closed API fallback。",
    region="overseas", pricing="usage", vendor="fireworks-ai", pitfalls=["模型清单与定价常更新；复杂 Agent 仍可能需要 frontier close…"]))
link("fireworks-e0", "fireworks", "together-ai", "alternative_to")
add(mk("groq", "Groq", "gateway-router", "inference-api", "LPU 超低延迟推理芯片 API", "https://groq.com",
    "Groq 提供基于自研 LPU 的 ultra-low latency inference API，适合 Llama/Mixtral 等模型的实时交互场景。", "语音对话、游戏 NPC、需要 <100ms token 延迟的实时 AI 功能。", "支持模型列表有限；长上下文与超大模型不如 GPU cloud 灵活。",
    region="overseas", pricing="usage", vendor="groq-inc", pitfalls=["支持模型列表有限；长上下文与超大模型不如 GPU cloud 灵活。"]))
link("groq-e0", "groq", "together-ai", "alternative_to")
add(mk("huggingface-inference", "Hugging Face Inference", "gateway-router", "inference-api", "HF 托管模型推理端点", "https://huggingface.co/inference-api",
    "Hugging Face Inference 提供 Serverless 与 Dedicated endpoint，一键部署 HF Hub 上数万模型，DevEx 极佳。", "快速试验 HF 上新模型、或 pipeline 已深度绑定 transformers 生态的团队。", "生产 SLA 与 cold start 需选 dedicated；免费 tier 限流严格。",
    region="overseas", pricing="usage", vendor="huggingface", pitfalls=["生产 SLA 与 cold start 需选 dedicated；免费 tier…"]))
link("huggingface-inference-e0", "huggingface-inference", "replicate", "alternative_to")
add(mk("aws-bedrock", "Amazon Bedrock", "gateway-router", "cloud-llm", "AWS 统一基础模型服务", "https://aws.amazon.com/bedrock",
    "Amazon Bedrock 在 AWS 内提供 Claude、Llama、Titan 等多模型统一 API，集成 IAM、VPC 与企业合规能力。", "已 all-in AWS、需要单一云账单与私有网络内调用 frontier/开源模型的企业。", "模型上线速度与 region 可用性滞后；非 AWS 栈跨云调用不经济。",
    region="overseas", pricing="usage", vendor="amazon", pitfalls=["模型上线速度与 region 可用性滞后；非 AWS 栈跨云调用不经济。"]))
link("aws-bedrock-e0", "aws-bedrock", "azure-openai", "alternative_to")
add(mk("vertex-ai", "Vertex AI", "gateway-router", "cloud-llm", "Google Cloud 统一 ML 与 Gemini 平台", "https://cloud.google.com/vertex-ai",
    "Vertex AI 提供 Gemini、PaLM 及开源模型托管、MLOps pipeline 与 grounding，深度集成 GCP 数据与 BigQuery。", "GCP 存量客户、需要 Gemini enterprise 与私有数据 grounding 的一体方案。", "国内直连 GCP 受限；多云策略需抽象层如 LiteLLM。",
    region="overseas", pricing="usage", vendor="google-vertex", pitfalls=["国内直连 GCP 受限；多云策略需抽象层如 LiteLLM。"]))
link("vertex-ai-e0", "vertex-ai", "aws-bedrock", "alternative_to")
add(mk("replicate", "Replicate", "gateway-router", "inference-api", "一行代码跑开源 ML 模型", "https://replicate.com",
    "Replicate 将开源模型（含 LLM、图像、音频）封装为 HTTP API，按秒计费，适合快速集成与原型验证。", "Indie hacker 需要调用 Stable Diffusion/Llama 等而不想运维 GPU 时。", "高 QPS 成本迅速上升；生产 scale 应迁移 dedicated/vLLM。",
    region="overseas", pricing="usage", vendor="replicate-inc", pitfalls=["高 QPS 成本迅速上升；生产 scale 应迁移 dedicated/vLLM…"]))
link("replicate-e0", "replicate", "huggingface-inference", "alternative_to")
add(mk("deepinfra", "DeepInfra", "gateway-router", "inference-api", "高性价比 GPU 推理 API", "https://deepinfra.com",
    "DeepInfra 提供 Llama、SD 等模型的低价 inference API，强调简单 REST 接口与透明定价。", "成本敏感、需要开源 LLM API 且 QPS 中等的 side project 或 internal tool。", "企业 support 与 compliance 文档弱于 Bedrock；关键业务需 SLA 评估。",
    region="overseas", pricing="usage", vendor="deepinfra-inc", pitfalls=["企业 support 与 compliance 文档弱于 Bedrock；关键业…"]))
link("deepinfra-e0", "deepinfra", "together-ai", "alternative_to")
add(mk("baseten", "Baseten", "gateway-router", "model-serving", "ML 模型部署与 Truss 框架", "https://www.baseten.co",
    "Baseten 帮助团队将自定义或开源模型部署为 production API，提供 autoscaling、监控与 Truss 打包格式。", "有自训练模型或 fine-tune 权重、需要比 Replicate 更 enterprise 的 serving 平台时。", "学习曲线高于纯 serverless API；小团队简单调用可能 overkill。",
    region="overseas", pricing="usage", vendor="baseten-inc", pitfalls=["学习曲线高于纯 serverless API；小团队简单调用可能 overkil…"]))
link("baseten-e0", "baseten", "vllm", "commonly_used_with")
add(mk("anyscale", "Anyscale", "gateway-router", "ray-platform", "Ray 生态分布式 AI 平台", "https://www.anyscale.com",
    "Anyscale 基于 Ray 提供分布式 training/inference 平台，适合 LLM fine-tune 与大规模 batch 推理编排。", "已有 Ray 投资、需要弹性 GPU 集群跑 training 或 offline inference pipeline。", "纯 API 调用场景用 Together 更简单；平台复杂度适合 MLOps 成熟团队。",
    region="overseas", pricing="usage", vendor="anyscale-inc", pitfalls=["纯 API 调用场景用 Together 更简单；平台复杂度适合 MLOps 成…"]))
link("anyscale-e0", "anyscale", "vllm", "commonly_used_with")
# modal 归 Wave2 cloud-paas，此处不重复
add(mk("cerebras", "Cerebras Inference", "gateway-router", "inference-api", "晶圆级芯片超快推理 API", "https://cerebras.ai",
    "Cerebras 提供基于 WSE 的超大规模模型 inference API，强调极快 token 生成速度。", "对 latency 极度敏感且模型在支持列表内的 experimental 产品。", "模型与支持面窄、价格高；一般团队优先 Groq/Together。",
    region="overseas", pricing="usage", vendor="cerebras", pitfalls=["模型与支持面窄、价格高；一般团队优先 Groq/Together。"]))
link("cerebras-e0", "cerebras", "groq", "alternative_to")
add(mk("sambanova", "SambaNova", "gateway-router", "inference-api", "企业级 AI 芯片与模型云", "https://sambanova.ai",
    "SambaNova 提供 RDU 加速的企业 AI 平台与 hosted LLM API，面向 Fortune 500 私有化与云托管。", "大型企业采购国产/非 NVIDIA 算力路线、或需要 vendor 全程 support 的 POC。", "开发者 self-serve 体验弱；初创团队不适合首选。",
    region="overseas", pricing="usage", vendor="sambanova", pitfalls=["开发者 self-serve 体验弱；初创团队不适合首选。"]))
link("sambanova-e0", "sambanova", "aws-bedrock", "alternative_to")
add(mk("novita-ai", "Novita AI", "gateway-router", "inference-api", "游戏与创意向 GPU API 平台", "https://novita.ai",
    "Novita AI 提供 SD、LLM 等模型的 API 与 GPU 租赁，定价灵活，在亚太 indie 开发者中较流行。", "AIGC 应用、需要 SD+LLM 组合 API 且预算有限的亚太团队。", "企业 compliance 与 uptime SLA 需自行验证；关键业务备 fallback。",
    region="both", pricing="usage", vendor="novita-ai", pitfalls=["企业 compliance 与 uptime SLA 需自行验证；关键业务备 f…"]))
link("novita-ai-e0", "novita-ai", "siliconflow", "alternative_to")
add(mk("java", "Java", "lang-language", "general-purpose", "企业级跨平台静态类型语言", "https://www.oracle.com/java",
    "Java 是 JVM 生态核心语言，以稳定性、成熟框架（Spring）与庞大人才库著称，长期主导银行、电商与企业后端。", "大型企业后端、Android 历史项目、需要强类型与成熟监控体系时仍是稳妥选择。", "启动与内存占用高于 Go/Rust；新项目若追求极致云原生轻量需评估 Quarkus 等。",
    region="overseas", pricing="free", vendor="oracle-java", pitfalls=["启动与内存占用高于 Go/Rust；新项目若追求极致云原生轻量需评估 Quark…"]))
link("java-e0", "java", "spring-boot", "commonly_used_with")
add(mk("kotlin", "Kotlin", "lang-language", "jvm-modern", "JVM 现代静态类型语言", "https://kotlinlang.org",
    "Kotlin 是 JetBrains 推出的 JVM 语言，与 Java 100% 互操作，语法简洁，是 Android 官方首选与 Spring 现代栈常用语言。", "Android 新 feature、Java 存量项目渐进迁移、或需要 coroutine 并发模型的后端。", "纯 Kotlin 团队仍需理解 Java 生态；Native/JS 目标场景社区小于 JVM。",
    region="overseas", pricing="free", vendor="kotlin-foundation", pitfalls=["纯 Kotlin 团队仍需理解 Java 生态；Native/JS 目标场景社区…"]))
link("kotlin-e0", "kotlin", "spring-boot", "commonly_used_with")
add(mk("swift", "Swift", "lang-language", "apple-platform", "Apple 平台现代系统语言", "https://swift.org",
    "Swift 是 Apple 开源的系统级语言，用于 iOS/macOS/watchOS 开发，强调安全、性能与 SwiftUI 声明式 UI。", "原生 Apple 生态 App、需要最佳系统 API 访问与 App Store 分发时必选。", "仅限 Apple 平台；跨平台方案需 Flutter/RN 或 CMP 另选。",
    region="overseas", pricing="free", vendor="apple-swift", pitfalls=["仅限 Apple 平台；跨平台方案需 Flutter/RN 或 CMP 另选。"]))
link("swift-e0", "swift", "react-native", "alternative_to")
add(mk("dart", "Dart", "lang-language", "flutter-lang", "Flutter 客户端与服务端语言", "https://dart.dev",
    "Dart 是 Google 为 Flutter 优化的语言，支持 AOT/JIT，也可用于 small server 与 CLI，语法类似 Java/TS。", "已选 Flutter 做跨平台 UI 时自然采用；单代码库移动+Web 场景。", "脱离 Flutter 生态独立使用场景少；纯后端不如 Go/TS 流行。",
    region="overseas", pricing="free", vendor="google-dart", pitfalls=["脱离 Flutter 生态独立使用场景少；纯后端不如 Go/TS 流行。"]))
link("dart-e0", "dart", "flutter", "commonly_used_with")
add(mk("php", "PHP", "lang-language", "web-scripting", "Web 服务端脚本语言", "https://www.php.net",
    "PHP 是 Web 时代最普及的服务端语言之一，WordPress/Laravel 生态庞大，适合 CMS 与快速 Web 开发。", "WordPress//magento 维护、共享主机部署、或 Laravel 现代 PHP 全栈项目。", "类型系统与性能弱于现代编译型语言；高并发需配合 Octane/Swoole 等。",
    region="overseas", pricing="free", vendor="php-foundation", pitfalls=["类型系统与性能弱于现代编译型语言；高并发需配合 Octane/Swoole 等。"]))
link("php-e0", "php", "laravel", "commonly_used_with")
add(mk("ruby", "Ruby", "lang-language", "dynamic-web", "强调生产力的动态语言", "https://www.ruby-lang.org",
    "Ruby 以优雅语法与 Rails 框架闻名，适合初创公司快速构建 CRUD Web 应用与 internal tool。", "Rails 全栈 MVP、脚本自动化与 devops 胶水代码；日本市场仍大量采用。", "CPU 性能与并发不如 Go/Java；超大流量需 horizontal scale 与 caching 策略。",
    region="overseas", pricing="free", vendor="ruby-central", pitfalls=["CPU 性能与并发不如 Go/Java；超大流量需 horizontal sca…"]))
link("ruby-e0", "ruby", "rails", "commonly_used_with")
add(mk("csharp", "C#", "lang-language", "dotnet", ".NET 平台主力语言", "https://dotnet.microsoft.com/languages/csharp",
    "C# 是 Microsoft .NET 生态核心语言，跨平台、强类型，适用于 Web（ASP.NET）、游戏（Unity）与企业应用。", "Windows/Azure 企业栈、Unity 游戏开发、或需要 C# 与 F# 共存的 .NET 8+ 项目。", "非 Windows 服务器生态小于 Linux/Go；Unity 运行时与引擎版本绑定需注意。",
    region="overseas", pricing="free", vendor="dotnet-foundation", pitfalls=["非 Windows 服务器生态小于 Linux/Go；Unity 运行时与引擎版…"]))
link("csharp-e0", "csharp", "spring-boot", "alternative_to")
add(mk("elixir", "Elixir", "lang-language", "beam-concurrent", "BEAM 虚拟机函数式并发语言", "https://elixir-lang.org",
    "Elixir 构建在 Erlang VM 上，提供 fault-tolerant 并发与 Phoenix 框架，适合 real-time 与高可用系统。", "聊天、实时协作、IoT  hub、需要百万连接 soft real-time 的后端。", "人才池小于 Java/Go；纯 CRUD 业务 ROI 可能不如 Rails。",
    region="overseas", pricing="free", vendor="elixir-lang", pitfalls=["人才池小于 Java/Go；纯 CRUD 业务 ROI 可能不如 Rails。"]))
link("elixir-e0", "elixir", "phoenix", "commonly_used_with")
add(mk("scala", "Scala", "lang-language", "jvm-functional", "JVM 函数式与 OO 混合语言", "https://www.scala-lang.org",
    "Scala 结合 FP 与 OO，Apache Spark/Kafka 生态深度使用，适合大数据与分布式系统。", "Spark 数据处理、Akka/Pekko actor 系统、或 JVM 上需要 FP 表达力的团队。", "编译慢、语法复杂；简单 Web API 更常用 Kotlin/Java。",
    region="overseas", pricing="free", vendor="scala-lang", pitfalls=["编译慢、语法复杂；简单 Web API 更常用 Kotlin/Java。"]))
link("scala-e0", "scala", "java", "compatible_with")
add(mk("zig", "Zig", "lang-language", "systems", "现代系统编程语言", "https://ziglang.org",
    "Zig 是面向 C 替代的系统语言，强调简单、无 hidden control flow 与 comptime，适合底层库与嵌入式。", "需要 C 级性能但拒绝 C++ 复杂度的新系统库、或与 C 互操作的 tooling。", "生态远小于 Rust；Web 后端与 AI 应用极少采用。",
    region="overseas", pricing="free", vendor="zig-lang", pitfalls=["生态远小于 Rust；Web 后端与 AI 应用极少采用。"]))
link("zig-e0", "zig", "rust", "alternative_to")
add(mk("lua", "Lua", "lang-language", "embedded-script", "轻量嵌入式脚本语言", "https://www.lua.org",
    "Lua 是极简嵌入式脚本语言，广泛用于游戏（Roblox/WoW）、Nginx OpenResty 与 Redis 脚本。", "游戏 mod、网关逻辑脚本、或需要在 C/C++ 宿主内嵌入配置化逻辑。", "大型应用全栈开发不适用；工程化工具链弱于 Python/TS。",
    region="overseas", pricing="free", pitfalls=["大型应用全栈开发不适用；工程化工具链弱于 Python/TS。"]))
link("lua-e0", "lua", "redis", "commonly_used_with")
add(mk("haskell", "Haskell", "lang-language", "pure-fp", "纯函数式学术向语言", "https://www.haskell.org",
    "Haskell 是 lazy 纯函数式语言，强类型系统与 GHC 生态在编译器、金融建模与形式验证领域有深度应用。", "需要高可靠抽象、DSL 编译器或团队 FP 背景深厚时；Cardano 等区块链生态组件。", "招聘困难、runtime 行为对新手不直观；一般 Web SaaS 不推荐首选。",
    region="overseas", pricing="free", pitfalls=["招聘困难、runtime 行为对新手不直观；一般 Web SaaS 不推荐首选。"]))
link("haskell-e0", "haskell", "rust", "alternative_to")
add(mk("clojure", "Clojure", "lang-language", "lisp-jvm", "Lisp 方言 JVM 语言", "https://clojure.org",
    "Clojure 是 Lisp 家族 JVM 语言，强调 immutable 数据与 REPL 驱动开发，Datomic 等数据系统同源。", "数据密集型后端、REPL 友好工具链、或 JVM 上需要 Lisp 表达力的团队。", "语法括号劝退；与 Spring 主流 Java 栈协作需桥接层。",
    region="overseas", pricing="free", pitfalls=["语法括号劝退；与 Spring 主流 Java 栈协作需桥接层。"]))
link("clojure-e0", "clojure", "java", "compatible_with")
add(mk("fsharp", "F#", "lang-language", "dotnet-fp", ".NET 函数式语言", "https://fsharp.org",
    "F# 是 .NET 上的函数式优先语言，适合数据脚本、量化与 ASP.NET Core 后端，与 C# 互操作无缝。", ".NET 团队希望 FP 风格处理数据 pipeline、或 Azure 生态内的 concise 后端。", "库与招聘以 C# 为主；UI 生态弱，前端通常另选 TS。",
    region="overseas", pricing="free", vendor="dotnet-foundation", pitfalls=["库与招聘以 C# 为主；UI 生态弱，前端通常另选 TS。"]))
link("fsharp-e0", "fsharp", "csharp", "compatible_with")
add(mk("nim", "Nim", "lang-language", "systems-script", "Python 语法 C 性能语言", "https://nim-lang.org",
    "Nim 编译为 C/C++/JS，语法类似 Python，适合编写高性能 CLI、游戏脚本与系统工具。建议结合团队现有栈、合规要求与成本模型做小规模 POC 后再定稿。", "需要单文件二进制分发、或从 Python 迁移追求性能的工具项目。", "社区与包生态小；生产 Web 后端案例有限。",
    region="overseas", pricing="free", pitfalls=["社区与包生态小；生产 Web 后端案例有限。"]))
link("nim-e0", "nim", "zig", "alternative_to")
add(mk("astro", "Astro", "fw-fullstack", "content-site", "内容优先的多框架静态站点", "https://astro.build",
    "Astro 是内容驱动 Web 框架，默认零 JS  shipped，可岛式集成 React/Vue/Svelte，适合博客、文档与营销站。", "SEO 敏感的内容站、文档站、或希望从 WordPress 迁移到 modern stack 时首选。", "强交互 SPA 场景不如 Next.js；动态 API 需配 server adapter 或外置 backend。",
    region="overseas", pricing="open-source", vendor="astro-inc", pitfalls=["强交互 SPA 场景不如 Next.js；动态 API 需配 server ad…"]))
link("astro-e0", "astro", "nextjs", "alternative_to")
add(mk("solidstart", "SolidStart", "fw-fullstack", "meta-framework", "SolidJS 全栈元框架", "https://start.solidjs.com",
    "SolidStart 基于 SolidJS 细粒度响应式，提供 SSR、路由与 server functions，性能接近 vanilla JS。", "追求极致运行时性能、团队熟悉 Solid 响应式模型的小型全栈 App。", "生态与招聘远小于 React；UI 库选择面窄。",
    region="overseas", pricing="open-source", vendor="solidjs", pitfalls=["生态与招聘远小于 React；UI 库选择面窄。"]))
link("solidstart-e0", "solidstart", "nextjs", "alternative_to")
add(mk("react-native", "React Native", "fw-fullstack", "mobile-cross", "React 语法跨平台原生 App", "https://reactnative.dev",
    "React Native 用 React 开发 iOS/Android 原生 UI，Facebook 维护，生态庞大，支持 OTA 与原生模块桥接。", "团队已有 React 技能、需要双端 App 且希望共享业务逻辑时主流选择。", "性能与平台一致性不如 Flutter 纯自绘；复杂动画需 native 模块。",
    region="overseas", pricing="open-source", pitfalls=["性能与平台一致性不如 Flutter 纯自绘；复杂动画需 native 模块。"]))
link("react-native-e0", "react-native", "expo", "commonly_used_with")
add(mk("expo", "Expo", "fw-fullstack", "mobile-toolchain", "React Native 开发构建平台", "https://expo.dev",
    "Expo 封装 RN 工具链，提供 EAS Build、OTA 更新与托管 workflow，大幅简化 App 上架流程。", "独立开发者或小团队快速发 iOS/Android、接受 managed workflow 限制时。", "重度 native 定制需 dev client/eject；Expo 版本与 RN 版本需对齐。",
    region="overseas", pricing="freemium", vendor="expo-dev", pitfalls=["重度 native 定制需 dev client/eject；Expo 版本与 …"]))
link("expo-e0", "expo", "react-native", "built_on")
add(mk("flutter", "Flutter", "fw-fullstack", "mobile-cross", "Dart 跨平台 UI 框架", "https://flutter.dev",
    "Flutter 用 Dart 自绘 UI 引擎，一套代码跑 iOS/Android/Web/Desktop，Google 维护，UI 一致性强。", "需要精美自定义 UI、多平台（含 desktop）一致体验的新 App 项目。", "包体积较大；与原生混合栈团队需评估 Platform Channel 成本。",
    region="overseas", pricing="open-source", vendor="flutter-dev", pitfalls=["包体积较大；与原生混合栈团队需评估 Platform Channel 成本。"]))
link("flutter-e0", "flutter", "react-native", "alternative_to")
add(mk("tauri", "Tauri", "fw-fullstack", "desktop", "Rust 轻量跨平台桌面壳", "https://tauri.app",
    "Tauri 用 Rust 做 desktop shell，WebView 渲染前端，二进制远小于 Electron，强调安全与资源占用低。", "需要 desktop 工具、内部客户端，且团队可接受 Rust 侧维护时替代 Electron。", "WebView 行为因 OS 而异；复杂 native API 需写 Rust plugin。",
    region="overseas", pricing="open-source", vendor="tauri-apps", pitfalls=["WebView 行为因 OS 而异；复杂 native API 需写 Rust …"]))
link("tauri-e0", "tauri", "electron", "alternative_to")
add(mk("electron", "Electron", "fw-fullstack", "desktop", "Chromium 跨平台桌面应用框架", "https://www.electronjs.org",
    "Electron 用 Chromium+Node 构建跨平台 desktop App，VS Code/Slack/Discord 等均采用，生态最成熟。", "需要快速复用 Web 技能做 desktop、或依赖大量 npm native 模块时。", "内存与包体积大；安全更新需跟踪 Chromium CVE。",
    region="overseas", pricing="open-source", vendor="electronjs", pitfalls=["内存与包体积大；安全更新需跟踪 Chromium CVE。"]))
link("electron-e0", "electron", "tauri", "alternative_to")
add(mk("capacitor", "Capacitor", "fw-fullstack", "mobile-hybrid", "Web 技术打包原生 App 壳", "https://capacitorjs.com",
    "Capacitor 是 Ionic 团队维护的 hybrid 运行时，将 Web App 包装为 iOS/Android 并暴露 native plugin API。", "已有 PWA/Next 营销站、需低成本上架 App Store 且交互不太复杂时。", "性能与 UX 不如 RN/Flutter；重度 native 功能依赖 plugin 质量。",
    region="overseas", pricing="open-source", vendor="ionic-team", pitfalls=["性能与 UX 不如 RN/Flutter；重度 native 功能依赖 plug…"]))
link("capacitor-e0", "capacitor", "react-native", "alternative_to")
add(mk("nestjs", "NestJS", "fw-fullstack", "node-backend", "Node.js 企业级结构化后端框架", "https://nestjs.com",
    "NestJS 用 TypeScript 提供 Angular 式模块/DI/装饰器，适合大型 Node API、GraphQL 与 microservices。", "TS 全栈团队需要可扩展后端架构、与 TypeORM/Prisma 等企业栈集成时。", "冷启动与简单 CRUD 偏重；小项目 Express/Hono 更轻。",
    region="overseas", pricing="open-source", vendor="nestjs", pitfalls=["冷启动与简单 CRUD 偏重；小项目 Express/Hono 更轻。"]))
link("nestjs-e0", "nestjs", "express", "alternative_to")
add(mk("hono", "Hono", "fw-fullstack", "edge-backend", "轻量边缘优先 Web 框架", "https://hono.dev",
    "Hono 是 ultrafast 小体积 Web 框架，运行在 Cloudflare Workers、Deno、Node 等多 runtime，API 类似 Express。", "Edge/serverless API、需要跨 runtime 复用同一 handler 代码的 TS 项目。", "大型 monolith 生态插件少于 Nest；ORM 集成需自行组装。",
    region="overseas", pricing="open-source", vendor="hono-dev", pitfalls=["大型 monolith 生态插件少于 Nest；ORM 集成需自行组装。"]))
link("hono-e0", "hono", "express", "alternative_to")
add(mk("fastapi", "FastAPI", "fw-fullstack", "python-api", "现代 Python 异步 API 框架", "https://fastapi.tiangolo.com",
    "FastAPI 基于 Starlette/Pydantic，自动生成 OpenAPI，原生 async，是 Python ML 服务与 REST API 首选。", "AI/数据团队暴露 model inference API、或需要类型安全 Python 后端时。", "CPU-bound 任务需 Celery 等 offload；WSGI 遗留 middleware 兼容需注意。",
    region="overseas", pricing="open-source", vendor="fastapi-tiangolo", pitfalls=["CPU-bound 任务需 Celery 等 offload；WSGI 遗留 m…"]))
link("fastapi-e0", "fastapi", "django", "alternative_to")
add(mk("django", "Django", "fw-fullstack", "python-fullstack", "Python 全栈 Web 框架", "https://www.djangoproject.com",
    "Django 是 batteries-included Python 框架，内置 ORM、admin、auth，适合 CMS、internal admin 与 rapid backend。", "需要自带 admin 面板、内容管理与成熟 auth 的中大型 Python Web 项目。", "async 支持与前端分离不如 FastAPI 现代；API-only 微服务可能过重。",
    region="overseas", pricing="open-source", vendor="django-software", pitfalls=["async 支持与前端分离不如 FastAPI 现代；API-only 微服务可…"]))
link("django-e0", "django", "fastapi", "alternative_to")
add(mk("express", "Express", "fw-fullstack", "node-backend", "Node.js 极简 Web 框架", "https://expressjs.com",
    "Express 是 Node 最普及的 minimalist HTTP 框架，中间件生态无限，适合 API 与 SSR 胶水层。", "Node 存量项目、快速 REST prototype、或需要最大 middleware 选择面时。", "缺乏内置结构，大项目需自律分层或迁移 Nest；callback 风格需 promisify。",
    region="overseas", pricing="open-source", vendor="expressjs", pitfalls=["缺乏内置结构，大项目需自律分层或迁移 Nest；callback 风格需 pro…"]))
link("express-e0", "express", "nestjs", "migration_path_to")
add(mk("spring-boot", "Spring Boot", "fw-fullstack", "java-backend", "Java 企业级快速启动框架", "https://spring.io/projects/spring-boot",
    "Spring Boot 简化 Spring 配置，提供 auto-configuration、actuator 与庞大生态，是企业 Java 后端事实标准。", "银行/政企 Java 栈、需要成熟 security/transaction/messaging 集成的后端。", "启动慢、内存高；serverless 形态需 GraalVM native 等额外工作。",
    region="overseas", pricing="open-source", vendor="vmware-spring", pitfalls=["启动慢、内存高；serverless 形态需 GraalVM native 等额…"]))
link("spring-boot-e0", "spring-boot", "java", "commonly_used_with")
add(mk("gin", "Gin", "fw-fullstack", "go-backend", "Go 高性能 HTTP Web 框架", "https://gin-gonic.com",
    "Gin 是 Go 最流行的 Web 框架之一，路由快、中间件简洁，适合 microservices 与高 QPS API。", "Go 微服务、云原生 sidecar API、或需要小内存 footprint 的 backend。", "缺少 batteries-included ORM；复杂业务层需自行架构。",
    region="overseas", pricing="open-source", vendor="gin-gonic", pitfalls=["缺少 batteries-included ORM；复杂业务层需自行架构。"]))
link("gin-e0", "gin", "go", "commonly_used_with")
add(mk("laravel", "Laravel", "fw-fullstack", "php-fullstack", "PHP 现代全栈 MVC 框架", "https://laravel.com",
    "Laravel 提供 elegant ORM（Eloquent）、queue、auth 与 Livewire/Inertia 前端集成，是 modern PHP 旗舰框架。", "PHP 团队构建 SaaS、需要快速迭代与丰富 package 生态时。", "超高并发需 Octane/Horizon 调优；与 Node/Go 比 CPU 密集任务弱。",
    region="overseas", pricing="open-source", vendor="laravel", pitfalls=["超高并发需 Octane/Horizon 调优；与 Node/Go 比 CPU …"]))
link("laravel-e0", "laravel", "php", "commonly_used_with")
add(mk("angular", "Angular", "fw-fullstack", "spa-framework", "Google 企业级前端框架", "https://angular.dev",
    "Angular 是完整 opinionated 前端框架，内置 routing/forms/HTTP/RxJS，TypeScript-first，适合大型 enterprise SPA。", "大型企业前端、需要强规范与长期 LTS 支持、团队规模大的项目。", "学习曲线陡、bundle 偏大；marketing 轻页不如 Astro/Next。",
    region="overseas", pricing="open-source", vendor="angular-team", pitfalls=["学习曲线陡、bundle 偏大；marketing 轻页不如 Astro/Nex…"]))
link("angular-e0", "angular", "react", "alternative_to")
add(mk("svelte", "Svelte", "fw-fullstack", "ui-compiler", "编译时响应式前端框架", "https://svelte.dev",
    "Svelte 将响应式编译为 vanilla JS，无 virtual DOM runtime，DX 简洁，SvelteKit 提供全栈能力。", "追求小 bundle、喜欢模板语法、或从 Vue 迁移的中小型项目。", "就业市场小于 React；复杂 enterprise 组件库选择少。",
    region="overseas", pricing="open-source", vendor="svelte-team", pitfalls=["就业市场小于 React；复杂 enterprise 组件库选择少。"]))
link("svelte-e0", "svelte", "sveltekit", "commonly_used_with")
add(mk("fastify", "Fastify", "fw-fullstack", "node-backend", "Node 高性能 JSON API 框架", "https://fastify.dev",
    "Fastify 强调 schema-based validation 与低开销 JSON 序列化，plugin 架构清晰，benchmark 优于 Express。", "高 QPS Node API、需要 JSON schema 文档与 hooks 体系的 microservice。", "生态 middleware 数量仍少于 Express；团队习惯 Express API 需适应。",
    region="overseas", pricing="open-source", vendor="fastify-team", pitfalls=["生态 middleware 数量仍少于 Express；团队习惯 Express…"]))
link("fastify-e0", "fastify", "express", "alternative_to")
add(mk("axum", "Axum", "fw-fullstack", "rust-backend", "Tokio 生态 Rust Web 框架", "https://github.com/tokio-rs/axum",
    "Axum 是基于 Tokio/Hyper 的 Rust async Web 框架，类型安全 extractor，与 Tower middleware 深度集成。", "Rust 后端 microservice、需要 memory safety 与极致性能的 API 层。", "编译时间长；ORM 与 DX 不如 TS/Python 成熟。",
    region="overseas", pricing="open-source", vendor="tokio-axum", pitfalls=["编译时间长；ORM 与 DX 不如 TS/Python 成熟。"]))
link("axum-e0", "axum", "rust", "commonly_used_with")
add(mk("phoenix", "Phoenix", "fw-fullstack", "elixir-web", "Elixir 实时 Web 框架", "https://www.phoenixframework.org",
    "Phoenix 提供 Channels 实时通信、LiveView 服务端渲染交互与 Ecto ORM，构建在 Elixir/OTP 之上。", "实时聊天、协作编辑、需要 WebSocket 大规模连接的后端。", "Elixir 人才少；纯 REST CRUD 不如 Rails 快捷。",
    region="overseas", pricing="open-source", vendor="phoenix-framework", pitfalls=["Elixir 人才少；纯 REST CRUD 不如 Rails 快捷。"]))
link("phoenix-e0", "phoenix", "elixir", "commonly_used_with")
add(mk("rails", "Ruby on Rails", "fw-fullstack", "ruby-fullstack", "Ruby 约定优于配置全栈框架", "https://rubyonrails.org",
    "Rails 以 convention over configuration 著称， scaffold 极快，ActiveRecord/ActionCable 一体，初创 MVP 经典选择。", "2–10 人团队快速构建 SaaS MVP、internal tool 或 content+commerce 站点。", "超大 monolith 性能需拆分；JavaScript 前端现代栈需配合 Hotwire/Stimulus。",
    region="overseas", pricing="open-source", vendor="rails-core", pitfalls=["超大 monolith 性能需拆分；JavaScript 前端现代栈需配合 Ho…"]))
link("rails-e0", "rails", "ruby", "commonly_used_with")
add(mk("adonisjs", "AdonisJS", "fw-fullstack", "node-fullstack", "Node Laravel 风格全栈框架", "https://adonisjs.com",
    "AdonisJS 提供类似 Laravel 的 MVC、Lucid ORM 与 auth，TypeScript-first，适合结构化 Node 全栈。", "喜欢 Laravel DX 但想用 Node/TS 全栈的 team；需要内置 ORM 与 CLI。", "社区小于 Nest；edge/serverless 部署非强项。",
    region="overseas", pricing="open-source", vendor="adonisjs", pitfalls=["社区小于 Nest；edge/serverless 部署非强项。"]))
link("adonisjs-e0", "adonisjs", "nestjs", "alternative_to")
add(mk("qwik", "Qwik", "fw-fullstack", "resumable-ssr", "可恢复 SSR 与零 JS 交互框架", "https://qwik.dev",
    "Qwik 通过 resumability 延迟加载 JS，实现 near-zero JS 首屏与极快 TTI，Builder.io 团队维护。", "营销页与 content 站追求 Core Web Vitals 满分、或从 heavy SPA 减负时。", "生态较新；复杂 dashboard 案例少于 Next/React。",
    region="overseas", pricing="open-source", vendor="qwik-dev", pitfalls=["生态较新；复杂 dashboard 案例少于 Next/React。"]))
link("qwik-e0", "qwik", "nextjs", "alternative_to")
add(mk("redwoodjs", "RedwoodJS", "fw-fullstack", "jamstack-fullstack", "React+GraphQL 全栈 Jamstack", "https://redwoodjs.com",
    "RedwoodJS 将 React UI、Prisma DB 与 GraphQL API 打包为 opinionated 全栈，适合 startup SaaS。", "全栈 TS 团队想快速 scaffold admin+API+web 且接受 GraphQL 时。", "GraphQL 复杂度与 cache 策略需团队经验；非 GraphQL 栈迁移成本高。",
    region="overseas", pricing="open-source", vendor="redwoodjs", pitfalls=["GraphQL 复杂度与 cache 策略需团队经验；非 GraphQL 栈迁移…"]))
link("redwoodjs-e0", "redwoodjs", "nextjs", "alternative_to")
add(mk("actix-web", "Actix Web", "fw-fullstack", "rust-backend", "Actix actor 系 Rust Web 框架", "https://actix.rs",
    "Actix Web 是高性能 Rust HTTP 框架，基于 actor 模型，benchmark 领先，适合 latency 敏感服务。", "Rust 微服务需要极致吞吐、或团队已有 Actix 投资时。", "与 Axum 社区分裂；async API 风格需团队统一选型。",
    region="overseas", pricing="open-source", vendor="actix-team", pitfalls=["与 Axum 社区分裂；async API 风格需团队统一选型。"]))
link("actix-web-e0", "actix-web", "axum", "alternative_to")
add(mk("mui", "MUI", "ui-kits", "react-material", "React Material Design 组件库", "https://mui.com",
    "MUI（Material UI）是 React 最流行的 Material Design 实现，提供完整组件、主题系统与 Data Grid 等 Pro 模块。", "企业 admin dashboard、B2B SaaS 需要成熟表格/表单/主题且团队熟悉 Material 时。", "默认 Material 视觉同质化；重度定制需投入 theme override。",
    region="overseas", pricing="freemium", vendor="mui", pitfalls=["默认 Material 视觉同质化；重度定制需投入 theme override…"]))
link("mui-e0", "mui", "react", "commonly_used_with")
add(mk("chakra-ui", "Chakra UI", "ui-kits", "react-accessible", "React 无障碍组件库", "https://chakra-ui.com",
    "Chakra UI 提供 composable、WAI-ARIA 友好的 React 组件，style props API 简洁，dark mode 开箱即用。", "需要快速搭建 accessible marketing/admin、且偏好 CSS-in-JS style props 的团队。", "Chakra v3 迁移变动大；大数据表格需另配 TanStack Table。",
    region="overseas", pricing="open-source", vendor="chakra-ui-inc", pitfalls=["Chakra v3 迁移变动大；大数据表格需另配 TanStack Table。"]))
link("chakra-ui-e0", "chakra-ui", "shadcn-ui", "alternative_to")
add(mk("heroui", "HeroUI", "ui-kits", "react-modern", "原 NextUI 现代 React 组件库", "https://www.heroui.com",
    "HeroUI（原 NextUI）基于 Tailwind+React Aria，提供精美 modern 组件，与 Next.js 集成文档丰富。", "Next.js marketing 与 SaaS 需要现成美观 UI、又不想从零写 Tailwind 时。", "组件数量少于 MUI；复杂 enterprise 数据组件需组合第三方。",
    region="overseas", pricing="open-source", vendor="heroui", pitfalls=["组件数量少于 MUI；复杂 enterprise 数据组件需组合第三方。"]))
link("heroui-e0", "heroui", "nextjs", "commonly_used_with")
add(mk("headless-ui", "Headless UI", "ui-primitives", "unstyled-primitives", "Tailwind 官方无样式组件", "https://headlessui.com",
    "Headless UI 由 Tailwind Labs 提供完全无样式的 accessible 组件（Dialog、Menu 等），样式完全自定义。", "已用 Tailwind、需要 a11y 行为正确又不想引入重型 UI 库时。", "不含任何默认美观样式；设计工作量高于 shadcn/HeroUI。",
    region="overseas", pricing="open-source", vendor="tailwind-labs", pitfalls=["不含任何默认美观样式；设计工作量高于 shadcn/HeroUI。"]))
link("headless-ui-e0", "headless-ui", "radix-ui", "alternative_to")
add(mk("framer-motion", "Framer Motion", "ui-composable", "animation", "React 声明式动画库", "https://www.framer.com/motion",
    "Framer Motion（现 Motion）是 React 最流行的 animation 库，提供 layout、gesture 与 SVG 动画 API。", "marketing 页 micro-interaction、组件库动效、或需要 spring 物理动画的 UI。", "bundle 对简单 fade 可能过重；纯 CSS 可解决的动画不必引入。",
    region="overseas", pricing="open-source", vendor="framer", pitfalls=["bundle 对简单 fade 可能过重；纯 CSS 可解决的动画不必引入。"]))
link("framer-motion-e0", "framer-motion", "react", "commonly_used_with")
add(mk("iconify", "Iconify", "ui-icons", "unified-icons", "统一 20 万+ 图标 JSON API", "https://iconify.design",
    "Iconify 聚合 IconifyJSON 格式图标集，可按需加载 Lucide/Material 等，支持 SVG/React/Vue 组件。", "需要混用多套图标风格、或 icon 按需 tree-shake 减 bundle 的项目。", "离线/air-gapped 需自托管 icon JSON；设计系统统一性需约束可用 icon set。",
    region="overseas", pricing="open-source", vendor="iconify", pitfalls=["离线/air-gapped 需自托管 icon JSON；设计系统统一性需约束可…"]))
link("iconify-e0", "iconify", "lucide", "alternative_to")
add(mk("heroicons", "Heroicons", "ui-icons", "svg-icons", "Tailwind 团队手工 SVG 图标", "https://heroicons.com",
    "Heroicons 是 Tailwind Labs 设计的 MIT SVG 图标集，outline/solid 双风格，与 Tailwind 视觉一致。", "Tailwind/shadcn 栈 marketing 与 admin 需要少量高质量 icon 时默认选择。", "数量远少于 Iconify；特殊行业 icon 可能缺失。",
    region="overseas", pricing="open-source", vendor="steve-donovan", pitfalls=["数量远少于 Iconify；特殊行业 icon 可能缺失。"]))
link("heroicons-e0", "heroicons", "lucide", "alternative_to")
add(mk("tabler-icons", "Tabler Icons", "ui-icons", "svg-icons", "开源 SVG 图标库", "https://tabler.io/icons",
    "Tabler Icons 提供 5000+ 一致 stroke 风格 MIT 图标，适合 dashboard 与 B2B UI。", "admin/SaaS 需要大量一致线性 icon、且不想付费 Font Awesome Pro 时。", "品牌识别度不如 Lucide 在 shadcn 生态；animated icon 需自行实现。",
    region="overseas", pricing="open-source", vendor="tabler", pitfalls=["品牌识别度不如 Lucide 在 shadcn 生态；animated icon…"]))
link("tabler-icons-e0", "tabler-icons", "lucide", "alternative_to")
add(mk("ark-ui", "Ark UI", "ui-primitives", "headless-primitives", "Chakra 系无样式 UI 原语", "https://ark-ui.com",
    "Ark UI 是 Chakra 团队出品的 framework-agnostic headless 组件，支持 React/Vue/Solid，行为与 a11y 一致。", "多框架 design system、或需要 headless 又想要 Chakra 团队质量的原语时。", "样式层完全自备；文档与社区小于 Radix。",
    region="overseas", pricing="open-source", vendor="chakra-ark", pitfalls=["样式层完全自备；文档与社区小于 Radix。"]))
link("ark-ui-e0", "ark-ui", "radix-ui", "alternative_to")
add(mk("vuetify", "Vuetify", "ui-kits", "vue-material", "Vue Material Design 组件库", "https://vuetifyjs.com",
    "Vuetify 是 Vue 生态最成熟的 Material Design 组件库，提供 Vuetify 3 + Vue 3 完整 enterprise 组件。", "Vue 企业 admin、需要 datatable/dialog 等开箱即用 Material 组件时。", "Material 视觉固定；与 Tailwind utility-first  workflow 冲突。",
    region="overseas", pricing="open-source", vendor="vuetify-team", pitfalls=["Material 视觉固定；与 Tailwind utility-first  …"]))
link("vuetify-e0", "vuetify", "vue", "commonly_used_with")
add(mk("quasar", "Quasar", "ui-kits", "vue-fullstack", "Vue 全平台 UI 框架", "https://quasar.dev",
    "Quasar 一套 Vue 组件同时构建 SPA、SSR、Mobile（Cordova/Capacitor）与 Electron desktop。", "Vue 团队希望单 UI 库覆盖 web+mobile+desktop 的多平台 internal tool。", "抽象层厚；只用 web 时不如 Nuxt+独立 UI 库灵活。",
    region="overseas", pricing="open-source", vendor="quasar-team", pitfalls=["抽象层厚；只用 web 时不如 Nuxt+独立 UI 库灵活。"]))
link("quasar-e0", "quasar", "vue", "commonly_used_with")
add(mk("naive-ui", "Naive UI", "ui-kits", "vue-typescript", "Vue 3 TypeScript 组件库", "https://www.naiveui.com",
    "Naive UI 是 Vue 3 全 TS 组件库，主题可调、文档中文友好，dashboard 组件齐全。", "Vue 3 + TS 国内团队构建 admin、需要中文文档与完整 form/table 组件时。", "国际化社区小于 Vuetify；design 偏默认需 theme 定制。",
    region="overseas", pricing="open-source", vendor="naive-ui", pitfalls=["国际化社区小于 Vuetify；design 偏默认需 theme 定制。"]))
link("naive-ui-e0", "naive-ui", "antd", "alternative_to")
add(mk("tamagui", "Tamagui", "ui-kits", "cross-platform-ui", "React Native+Web 统一 UI", "https://tamagui.dev",
    "Tamagui 用 optimizing compiler 统一 RN 与 Web 样式，一套组件跨 mobile/web，适合 universal app。", "Expo+Web 同构、希望共享 UI 层减少 duplicate 的 cross-platform 团队。", "学习曲线与配置复杂；生态小于纯 Web UI 库。",
    region="overseas", pricing="open-source", vendor="tamagui", pitfalls=["学习曲线与配置复杂；生态小于纯 Web UI 库。"]))
link("tamagui-e0", "tamagui", "react-native", "commonly_used_with")
add(mk("gluestack", "gluestack UI", "ui-kits", "react-native-web", "Universal 组件库", "https://gluestack.io",
    "gluestack UI 提供 styled 与 unstyled 层，支持 React Native 与 Next.js 共享组件，Tailwind 风格 token。", "RN+Next monorepo 需要 design token 统一与 copy-paste 组件 workflow。", "版本迭代快；复杂 web-only 组件仍不如 shadcn 丰富。",
    region="overseas", pricing="open-source", vendor="gluestack", pitfalls=["版本迭代快；复杂 web-only 组件仍不如 shadcn 丰富。"]))
link("gluestack-e0", "gluestack", "tamagui", "alternative_to")
add(mk("react-aria", "React Aria", "ui-primitives", "adobe-a11y", "Adobe 无障碍 React 原语", "https://react-spectrum.adobe.com/react-aria",
    "React Aria 提供 hooks 级 a11y 行为原语，Adobe 维护，被 HeroUI 等库底层采用。", "自建 design system 需要顶级 keyboard/screen reader 行为而不想从头实现 a11y。", "仅行为无视觉；需自行设计 CSS 或与 React Spectrum 配合。",
    region="overseas", pricing="open-source", vendor="adobe-react-aria", pitfalls=["仅行为无视觉；需自行设计 CSS 或与 React Spectrum 配合。"]))
link("react-aria-e0", "react-aria", "radix-ui", "alternative_to")
add(mk("fontawesome", "Font Awesome", "ui-icons", "icon-font", "经典图标字体与 SVG 套件", "https://fontawesome.com",
    "Font Awesome 是最老牌 icon 套件之一，提供 webfont 与 SVG React/Vue 组件，Pro 含更多 icon。", "legacy 项目、设计师熟悉 FA 命名、或需要特定品牌 icon 的存量维护。", "webfont 性能不如 SVG 按需加载；免费集同质化严重。",
    region="overseas", pricing="freemium", vendor="fontawesome", pitfalls=["webfont 性能不如 SVG 按需加载；免费集同质化严重。"]))
link("fontawesome-e0", "fontawesome", "lucide", "alternative_to")
add(mk("element-plus", "Element Plus", "ui-kits", "vue-enterprise", "Vue 3 企业级组件库", "https://element-plus.org",
    "Element Plus 是 Element UI 的 Vue 3 继任，提供完整 enterprise 组件，在国内 Vue admin 生态占主导。", "国内 Vue 后台、Element 存量升级 Vue 3、或需要成熟 table/form 中文文档时。", "视觉偏传统 enterprise；高度定制 marketing 页不如 Tailwind 自由。",
    region="both", pricing="open-source", vendor="element-plus", pitfalls=["视觉偏传统 enterprise；高度定制 marketing 页不如 Tail…"]))
link("element-plus-e0", "element-plus", "antd", "alternative_to")
add(mk("primevue", "PrimeVue", "ui-kits", "vue-rich", "Vue 富组件企业 UI 套件", "https://primevue.org",
    "PrimeVue 提供 90+ 组件含 advanced datatable、chart、galleria，PrimeTek 同时维护 React/Angular 版。", "Vue enterprise 需要复杂 datatable/tree/chart 一体、愿付费 Prime 支持时。", "默认 theme 需定制避免「Prime 脸」；bundle 较大需按需 import。",
    region="overseas", pricing="freemium", vendor="primefaces", pitfalls=["默认 theme 需定制避免「Prime 脸」；bundle 较大需按需 imp…"]))
link("primevue-e0", "primevue", "vuetify", "alternative_to")
add(mk("mantine-ui", "Mantine", "ui-kits", "react-hooks-rich", "React hooks 驱动组件库", "https://mantine.dev",
    "Mantine 提供 100+ React 组件与 hooks，内置 dark mode、form 管理与 notifications，DX 口碑好。", "React admin 需要 hooks API、form 与 dates 组件一体且 MIT 协议时。", "与 shadcn copy-paste 哲学不同；全量依赖包体积需 tree-shake。",
    region="overseas", pricing="open-source", pitfalls=["与 shadcn copy-paste 哲学不同；全量依赖包体积需 tree-s…"]))
link("mantine-ui-e0", "mantine-ui", "shadcn-ui", "alternative_to")
add(mk("bits-ui", "Bits UI", "ui-primitives", "svelte-headless", "Svelte 无样式原语", "https://bits-ui.com",
    "Bits UI 为 Svelte 提供 headless accessible 组件，API 类似 Radix，是 shadcn-svelte 底层。", "SvelteKit 项目构建 design system、需要 a11y 原语而非全家桶 UI 时。", "仅 Svelte 生态；React 团队应选 Radix/Ark。",
    region="overseas", pricing="open-source", pitfalls=["仅 Svelte 生态；React 团队应选 Radix/Ark。"]))
link("bits-ui-e0", "bits-ui", "radix-ui", "alternative_to")
add(mk("react-spring", "React Spring", "ui-composable", "animation", "弹簧物理 React 动画", "https://www.react-spring.dev",
    "React Spring 提供基于 spring physics 的 hook 动画，适合 gesture 与 layout transition，比 CSS 更自然。", "数据可视化 transition、拖拽排序动画、需要 physics-based motion 的 React UI。", "API 学习曲线高于 Framer Motion；简单 opacity 用 CSS 即可。",
    region="overseas", pricing="open-source", pitfalls=["API 学习曲线高于 Framer Motion；简单 opacity 用 CS…"]))
link("react-spring-e0", "react-spring", "framer-motion", "alternative_to")
add(mk("untitled-ui-icons", "Untitled UI Icons", "ui-icons", "figma-icons", "Figma 同源免费 icon", "https://www.untitledui.com/free-icons",
    "Untitled UI Icons 是与 Untitled UI Figma kit 配套的 free SVG icon，风格 modern minimal。", "使用 Untitled UI Figma 设计系统、需要设计与 dev icon 一致时。", "数量与社区小于 Lucide；长期维护依赖设计团队更新。",
    region="overseas", pricing="free", pitfalls=["数量与社区小于 Lucide；长期维护依赖设计团队更新。"]))
link("untitled-ui-icons-e0", "untitled-ui-icons", "heroicons", "alternative_to")
add(mk("pinecone", "Pinecone", "ai-vector", "managed-vector", "全托管向量数据库", "https://www.pinecone.io",
    "Pinecone 是 serverless 向量数据库，提供 metadata filtering、namespace 与 hybrid search，RAG SaaS 常用。", "不想运维 Milvus/Weaviate 集群、需要快速上线 RAG 且 QPS 中等的 AI 产品。", "vendor lock-in 与按量账单需监控；超大规模成本可能高于自托管。",
    region="overseas", pricing="usage", vendor="pinecone-io", pitfalls=["vendor lock-in 与按量账单需监控；超大规模成本可能高于自托管。"]))
link("pinecone-e0", "pinecone", "qdrant", "alternative_to")
add(mk("weaviate", "Weaviate", "ai-vector", "vector-db", "开源向量与混合搜索数据库", "https://weaviate.io",
    "Weaviate 提供 GraphQL API、内置 vectorizer 模块与 hybrid BM25+vector 搜索，可云托管或自部署。", "需要 hybrid search、multi-tenant RAG、或希望开源可自托管的 vector DB 时。", "运维复杂度高于 Pinecone；module 配置错误会导致 embedding 维度 mismatch。",
    region="overseas", pricing="freemium", vendor="weaviate-io", pitfalls=["运维复杂度高于 Pinecone；module 配置错误会导致 embeddin…"]))
link("weaviate-e0", "weaviate", "pinecone", "alternative_to")
add(mk("milvus", "Milvus", "ai-vector", "vector-db", "云原生开源向量数据库", "https://milvus.io",
    "Milvus 是 LF AI 基金会项目，支持 billion-scale 向量检索，Zilliz 提供云服务与 enterprise support。", "超大规模 embedding 检索、已有 K8s 运维能力、或国内 Zilliz Cloud 合规需求。", "组件多（etcd/pulsar 等），小团队运维重；低 QPS 用 pgvector 更简单。",
    region="both", pricing="open-source", vendor="zilliz", pitfalls=["组件多（etcd/pulsar 等），小团队运维重；低 QPS 用 pgvect…"]))
link("milvus-e0", "milvus", "pgvector", "alternative_to")
add(mk("chroma", "Chroma", "ai-vector", "embedded-vector", "嵌入式开发者友好向量库", "https://www.trychroma.com",
    "Chroma 是 embeddable vector store，API 极简，与 LangChain/LlamaIndex 集成顺滑，适合 prototype 与 small RAG。", "本地 RAG demo、side project、或 Python notebook 快速试验 retrieval 时。", "分布式与 enterprise SLA 弱于 Milvus；生产大规模需评估 hosted 版或迁移。",
    region="overseas", pricing="open-source", vendor="chroma-inc", pitfalls=["分布式与 enterprise SLA 弱于 Milvus；生产大规模需评估 h…"]))
link("chroma-e0", "chroma", "pgvector", "alternative_to")
add(mk("crewai", "CrewAI", "ai-agent-fw", "multi-agent", "角色扮演多 Agent 编排框架", "https://www.crewai.com",
    "CrewAI 让开发者定义 Agent role/goal/tool，以 crew 协作完成复杂任务，API 比 LangGraph 更 declarative。", "需要快速搭建 multi-agent demo、research crew 或 marketing content pipeline 时。", "生产 observability 与 error recovery 需自行补强；复杂 state machine 不如 LangGraph 灵活。",
    region="overseas", pricing="open-source", vendor="crewai-inc", pitfalls=["生产 observability 与 error recovery 需自行补强；…"]))
link("crewai-e0", "crewai", "langgraph", "alternative_to")
add(mk("pydantic-ai", "Pydantic AI", "ai-agent-fw", "typed-agent", "类型安全 Python Agent 框架", "https://ai.pydantic.dev",
    "Pydantic AI 由 Pydantic 团队出品，提供 typed agent、structured output 与 dependency injection，DX 现代。", "Python 后端已全面采用 Pydantic v2、需要可靠 structured LLM output 的 Agent 服务。", "生态较新；复杂 graph workflow 需与 LangGraph 等组合。",
    region="overseas", pricing="open-source", vendor="pydantic", pitfalls=["生态较新；复杂 graph workflow 需与 LangGraph 等组合。"]))
link("pydantic-ai-e0", "pydantic-ai", "langgraph", "alternative_to")
add(mk("flowise", "Flowise", "ai-rag", "visual-llm", "可视化 LangChain 流程构建", "https://flowiseai.com",
    "Flowise 提供 drag-drop UI 构建 LLM chain/agent flow，底层 LangChain，可 self-host，适合 rapid POC。", "非工程同事参与设计 chatbot flow、或需要可视化调试 prompt chain 时。", "复杂逻辑 version control 困难；生产应导出为 code 或限制在 POC。",
    region="overseas", pricing="open-source", vendor="flowise-ai", pitfalls=["复杂逻辑 version control 困难；生产应导出为 code 或限制在…"]))
link("flowise-e0", "flowise", "dify", "alternative_to")
add(mk("coze", "Coze", "ai-agent-fw", "bot-platform", "字节跳动 AI Bot 构建平台", "https://www.coze.com",
    "Coze（扣子）提供零代码 Bot 构建、插件市场与多渠道发布，支持国内外版本，适合运营向 chatbot。", "国内 ToC Bot、企微/飞书接入、或产品/运营主导的快速 bot 迭代。", "深度 custom code 与复杂 RAG pipeline 受限；enterprise 数据合规需选国内版。",
    region="both", pricing="freemium", vendor="coze", pitfalls=["深度 custom code 与复杂 RAG pipeline 受限；enter…"]))
link("coze-e0", "coze", "dify", "alternative_to")
add(mk("n8n", "n8n", "ai-rag", "workflow-automation", "可自托管工作流自动化", "https://n8n.io",
    "n8n 是 fair-code workflow 工具，节点连接 API/DB/LLM，可 self-host，适合 AI+ops 混合 automation。", "需要连接 Slack/GitHub/Postgres 与 OpenAI 做 internal automation、且重视 data residency 时。", "复杂 Agent reasoning 非其强项；应用层逻辑应用专用 Agent 框架。",
    region="overseas", pricing="freemium", vendor="n8n-io", pitfalls=["复杂 Agent reasoning 非其强项；应用层逻辑应用专用 Agent …"]))
link("n8n-e0", "n8n", "langchain", "commonly_used_with")
add(mk("helicone", "Helicone", "ai-llm-obs", "llm-proxy-obs", "开源 LLM 可观测与缓存代理", "https://www.helicone.ai",
    "Helicone 作为 LLM 请求代理，记录 latency/cost/token、提供 cache 与 prompt 管理，SDK 集成简单。", "需要比自建日志更完整的 LLM ops dashboard、又不想换 gateway vendor 时加一层 proxy。", "又一层网络 hop；敏感 payload 需确认 retention 与加密策略。",
    region="overseas", pricing="freemium", vendor="helicone-ai", pitfalls=["又一层网络 hop；敏感 payload 需确认 retention 与加密策略…"]))
link("helicone-e0", "helicone", "langfuse", "alternative_to")
add(mk("langsmith", "LangSmith", "ai-llm-obs", "llm-dev-platform", "LangChain 官方 LLM 调试与 eval 平台", "https://www.langchain.com/langsmith",
    "LangSmith 提供 trace、dataset eval、prompt hub 与 online monitoring，与 LangChain/LangGraph 深度集成。", "已选 LangChain 栈、需要 production trace 与 regression eval 闭环的 AI 团队。", "绑定 LangChain 生态；非 LC 项目用 Langfuse/Helicone 更中立。",
    region="overseas", pricing="usage", vendor="langchain-inc", pitfalls=["绑定 LangChain 生态；非 LC 项目用 Langfuse/Helico…"]))
link("langsmith-e0", "langsmith", "langfuse", "alternative_to")
add(mk("haystack", "Haystack", "ai-rag", "nlp-pipeline", "deepset 开源 NLP/RAG 框架", "https://haystack.deepset.ai",
    "Haystack 提供 modular pipeline（retriever+reader+generator），支持多种 vector DB 与 eval，enterprise 版可选。", "需要清晰 pipeline 抽象、on-prem RAG、或欧洲数据合规的 NLP 项目。", "与 LangChain 生态节点不互通；国内社区资源相对少。",
    region="overseas", pricing="open-source", vendor="deepset", pitfalls=["与 LangChain 生态节点不互通；国内社区资源相对少。"]))
link("haystack-e0", "haystack", "langchain", "alternative_to")
add(mk("langchain", "LangChain", "ai-rag", "llm-orchestration", "LLM 应用编排框架", "https://www.langchain.com",
    "LangChain 是最流行的 LLM 应用框架，提供 chain、agent、tool 与大量 integration，LangGraph 扩展 stateful workflow。", "快速集成 vector DB/tools/API 构建 RAG 与 Agent prototype 的默认起点（注意抽象层厚度）。", "过度抽象导致 debug 困难；生产应精简 dependency 并用 LangSmith 观测。",
    region="overseas", pricing="open-source", vendor="langchain-inc", pitfalls=["过度抽象导致 debug 困难；生产应精简 dependency 并用 Lang…"]))
link("langchain-e0", "langchain", "llamaindex", "alternative_to")
add(mk("autogen", "AutoGen", "ai-agent-fw", "multi-agent-ms", "Microsoft 多 Agent 对话框架", "https://microsoft.github.io/autogen",
    "AutoGen 让多个 Agent 通过 conversation 协作完成任务，支持 code execution 与 human-in-the-loop，研究社区活跃。", "研究 multi-agent、code interpreter 场景、或 Azure OpenAI 企业栈实验 Agent 编排。", "API 变动较快；生产 hardening 需自行封装 state 与 security sandbox。",
    region="overseas", pricing="open-source", vendor="autogen-ms", pitfalls=["API 变动较快；生产 hardening 需自行封装 state 与 secu…"]))
link("autogen-e0", "autogen", "crewai", "alternative_to")
add(mk("instructor", "Instructor", "ai-rag", "structured-output", "Pydantic structured LLM 输出库", "https://python.useinstructor.com",
    "Instructor 扩展 OpenAI/Anthropic 等 client，强制 LLM 输出符合 Pydantic model，减少 JSON parse 失败。", "Python 服务需要从 LLM 稳定抽取结构化数据（表单、entity、classification）时。", "仅解决 output parsing；Agent 编排需另选 LangGraph/Pydantic AI。",
    region="overseas", pricing="open-source", vendor="instructor-ai", pitfalls=["仅解决 output parsing；Agent 编排需另选 LangGraph…"]))
link("instructor-e0", "instructor", "pydantic-ai", "commonly_used_with")
add(mk("vespa", "Vespa", "ai-vector", "search-engine", "Yahoo 开源大数据搜索与向量引擎", "https://vespa.ai",
    "Vespa 是 JVM 搜索平台，统一 keyword、vector 与 ranking，适合 billion-document 级 retrieval。", "大型电商/媒体搜索、需要 custom ranking 与 vector hybrid 的自托管团队。", "运维与 JVM 调优门槛高；小 RAG 项目 overkill。",
    region="overseas", pricing="open-source", vendor="vespa-ai", pitfalls=["运维与 JVM 调优门槛高；小 RAG 项目 overkill。"]))
link("vespa-e0", "vespa", "weaviate", "alternative_to")
add(mk("lancedb", "LanceDB", "ai-vector", "embedded-vector", "基于 Lance 格式的嵌入式向量库", "https://lancedb.com",
    "LanceDB 基于 Apache Lance 列式格式，embeddable、serverless-friendly，适合 edge 与 Python data 栈 RAG。", "数据 science 团队在 notebook/local 跑 RAG、或需要与 pandas 生态紧密结合时。", "分布式 enterprise feature 仍在演进；超大规模需评估 cloud 版。",
    region="overseas", pricing="open-source", vendor="lancedb", pitfalls=["分布式 enterprise feature 仍在演进；超大规模需评估 clou…"]))
link("lancedb-e0", "lancedb", "chroma", "alternative_to")
add(mk("mem0", "Mem0", "ai-rag", "memory-layer", "LLM 应用长期记忆层", "https://mem0.ai",
    "Mem0 为 AI App 提供 user/session 级 memory 存储与检索，自动提取 fact 注入后续 prompt，减少 context 重复。", "个性化 chatbot、coach 类 App 需要跨 session 记住用户偏好时作为 memory middleware。", "隐私与 GDPR 删除权需设计；错误记忆会 persistent 污染后续对话。",
    region="overseas", pricing="usage", vendor="mem0-ai", pitfalls=["隐私与 GDPR 删除权需设计；错误记忆会 persistent 污染后续对话。"]))
link("mem0-e0", "mem0", "langchain", "commonly_used_with")
add(mk("letta", "Letta", "ai-agent-fw", "stateful-agent", "原 MemGPT 有状态 Agent 平台", "https://www.letta.com",
    "Letta（MemGPT）提供长期 memory 管理的 Agent 框架，支持 self-editing memory 与 tool use，适合 research agent。", "需要 Agent 自主管理 memory 层级、长运行 research assistant 实验时。", "生产 ready 程度需评估；与 Mem0 功能重叠需架构选型。",
    region="overseas", pricing="open-source", vendor="letta-ai", pitfalls=["生产 ready 程度需评估；与 Mem0 功能重叠需架构选型。"]))
link("letta-e0", "letta", "mem0", "alternative_to")
add(mk("unstructured", "Unstructured", "ai-rag", "document-etl", "非结构化文档 ETL 库", "https://unstructured.io",
    "Unstructured 解析 PDF/HTML/DOCX 等为 clean chunk，供 embedding pipeline 使用，是 RAG 数据预处理常用工具。", "企业 knowledge base 来源复杂（扫描件、slides）、需要 robust parsing 再入 vector DB 时。", "复杂版式 OCR 质量依赖上游；高 QPS batch 需配 queue 与 horizontal workers。",
    region="overseas", pricing="freemium", vendor="unstructured-io", pitfalls=["复杂版式 OCR 质量依赖上游；高 QPS batch 需配 queue 与 h…"]))
link("unstructured-e0", "unstructured", "llamaindex", "commonly_used_with")
add(mk("firecrawl", "Firecrawl", "ai-rag", "web-scrape-llm", "LLM 友好 Web 抓取 API", "https://www.firecrawl.dev",
    "Firecrawl 将 URL 转为 markdown/structured data，专为 RAG  ingest 设计，处理 JS 渲染站点。", "需要定期抓取文档站/竞品页入 knowledge base、或 agent 浏览网页工具 backend 时。", "反爬与 rate limit 可能导致失败；合规抓取需遵守 robots 与版权。",
    region="overseas", pricing="usage", vendor="firecrawl-dev", pitfalls=["反爬与 rate limit 可能导致失败；合规抓取需遵守 robots 与版权…"]))
link("firecrawl-e0", "firecrawl", "langchain", "integrates_with")
add(mk("jina", "Jina AI", "ai-rag", "embedding-search", "Embedding 与神经搜索框架", "https://jina.ai",
    "Jina AI 提供 embedding API、reranker 与 Jina Embeddings 模型，以及 DocArray 等搜索基础设施组件。", "需要多语言 embedding/rerank API、或构建 neural search pipeline 的 AI 应用。", "全栈 framework 认知度小于 LangChain；需组合而非替代 orchestration 层。",
    region="overseas", pricing="usage", vendor="jina-ai", pitfalls=["全栈 framework 认知度小于 LangChain；需组合而非替代 orc…"]))
link("jina-e0", "jina", "openrouter", "commonly_used_with")
add(mk("braintrust", "Braintrust", "ai-llm-obs", "eval-platform", "LLM 产品 eval 与回归平台", "https://www.braintrust.dev",
    "Braintrust 提供 dataset、online/offline eval、prompt playground 与 CI 集成，强调 product-grade LLM QA。", "AI feature 需要 systematic eval、A/B prompt 与 regression gate 的 product 团队。", "与 LangSmith 功能重叠需选型；小项目 spreadsheet eval 可能够用。",
    region="overseas", pricing="freemium", vendor="braintrust-data", pitfalls=["与 LangSmith 功能重叠需选型；小项目 spreadsheet eval…"]))
link("braintrust-e0", "braintrust", "langsmith", "alternative_to")
add(mk("arize", "Arize AI", "ai-llm-obs", "ml-observability", "ML 与 LLM 可观测平台", "https://arize.com",
    "Arize 提供 model monitoring、embedding drift 检测与 LLM trace 分析，面向 enterprise MLOps。", "已有传统 ML monitoring、扩展到 LLM/RAG production 监控的企业数据团队。", "实施与定价面向 enterprise；初创可用 lighter 工具如 Langfuse。",
    region="overseas", pricing="usage", vendor="arize-ai", pitfalls=["实施与定价面向 enterprise；初创可用 lighter 工具如 Lang…"]))
link("arize-e0", "arize", "langfuse", "alternative_to")
add(mk("promptlayer", "PromptLayer", "ai-llm-obs", "prompt-cms", "Prompt 版本管理与日志", "https://promptlayer.com",
    "PromptLayer 作为 LLM 调用中间层，记录 prompt 版本、latency 与 cost，支持 A/B 与 CMS 式 prompt 编辑。", "产品/非工程同事需要改 prompt 而不 redeploy 代码的协作 workflow。", "Agent 复杂 trace 不如 LangSmith；仅适合 prompt-centric 应用。",
    region="overseas", pricing="freemium", vendor="promptlayer", pitfalls=["Agent 复杂 trace 不如 LangSmith；仅适合 prompt-c…"]))
link("promptlayer-e0", "promptlayer", "langfuse", "alternative_to")
add(mk("turbopuffer", "Turbopuffer", "ai-vector", "serverless-vector", "S3 原生 Serverless 向量库", "https://turbopuffer.com",
    "Turbopuffer 将 vector index 存 S3，冷启动快、按查询付费，适合 spiky workload 与 multi-tenant SaaS。", "Serverless RAG、tenant 量大但单 tenant QPS 低、希望 vector 成本随用量近线性时。", "新兴 vendor；极端低 latency 场景需 benchmark 对比 Pinecone。",
    region="overseas", pricing="usage", vendor="turbopuffer", pitfalls=["新兴 vendor；极端低 latency 场景需 benchmark 对比 P…"]))
link("turbopuffer-e0", "turbopuffer", "pinecone", "alternative_to")
add(mk("agno", "Agno", "ai-agent-fw", "lightweight-agent", "极简 Python Agent 框架", "https://www.agno.com",
    "Agno（原 Phidata）提供轻量 Python Agent abstractions，内置 memory/knowledge/tool，强调 readable code 与 fast setup。", "Python 开发者想要比 LangChain 更薄的一层 Agent 框架快速 ship internal copilot。", "生态与 integration 少于 LangChain；复杂 graph 需自建。",
    region="overseas", pricing="open-source", vendor="agno-ai", pitfalls=["生态与 integration 少于 LangChain；复杂 graph 需自…"]))
link("agno-e0", "agno", "crewai", "alternative_to")
add(mk("semantic-kernel", "Semantic Kernel", "ai-agent-fw", "dotnet-agent", "Microsoft AI 编排 SDK", "https://learn.microsoft.com/semantic-kernel",
    "Semantic Kernel 是 Microsoft 跨语言 AI orchestration SDK，支持 planner、plugins 与 Azure OpenAI 深度集成。", ".NET/Azure 企业栈构建 copilot、需要 C# 一等公民 AI SDK 时。", "Python/TS 社区活跃度低于 LangChain；跨云 portable 性需验证。",
    region="overseas", pricing="open-source", vendor="microsoft", pitfalls=["Python/TS 社区活跃度低于 LangChain；跨云 portable …"]))
link("semantic-kernel-e0", "semantic-kernel", "langchain", "alternative_to")
add(mk("llamacloud", "LlamaCloud", "ai-rag", "managed-rag", "LlamaIndex 托管 RAG 服务", "https://www.llamaindex.ai",
    "LlamaCloud 提供 managed parsing、index 与 retrieval API，是 LlamaIndex 商业托管层，简化 enterprise RAG 运维。", "已用 LlamaIndex 本地 POC 成功、需要 SLA 与 scalable ingest pipeline 时升级。", "vendor 绑定 LlamaIndex；简单 RAG pgvector+LC 可能足够。",
    region="overseas", pricing="usage", pitfalls=["vendor 绑定 LlamaIndex；简单 RAG pgvector+LC …"]))
link("llamacloud-e0", "llamacloud", "llamaindex", "provides_access_to")
add(mk("langflow", "Langflow", "ai-rag", "visual-llm", "可视化 LangChain 兼容流程编辑器", "https://www.langflow.org",
    "Langflow 提供 drag-drop UI 构建 LLM flow，兼容 LangChain 组件，可导出 Python 代码并 self-host，比 Flowise 更偏开发者。", "需要可视化 prototyping 但最终要 export code 的 AI 工程师；与 LangChain 生态并用。", "复杂 production workflow 仍建议 code-first；版本升级可能 break 旧 flow JSON。",
    region="overseas", pricing="open-source", vendor="langchain-inc", pitfalls=["复杂 production workflow 仍建议 code-first；版本…"]))
link("langflow-e0", "langflow", "flowise", "alternative_to")

ENTRIES: list[dict] = _entries
VENDORS: list[dict] = _VENDORS
EDGES: list[dict] = _edges
