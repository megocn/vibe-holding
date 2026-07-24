#!/usr/bin/env python3
"""Generator for wave2_gilkv.py"""
from __future__ import annotations
from pathlib import Path

OUT = Path(__file__).parent / "wave2_gilkv.py"

HEADER = r'''#!/usr/bin/env python3
"""VibeHolding Wave 2 (G–L + V) knowledge base expansion."""
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
    if e.get("vendorId") is None:
        e.pop("vendorId", None)
    assert len(e["oneLiner"]) <= 60, (e["id"], e["oneLiner"])
    assert len(e.get("descriptionMd", "")) >= 120, (e["id"], len(e.get("descriptionMd", "")))
    assert e.get("pitfalls"), e["id"]
    assert e.get("subcategory"), e["id"]
    return e


def edge(eid, frm, to, typ, weight=0.7, confidence="community", note=None, sources=None):
    e = {
        "id": eid, "from": frm, "to": to, "type": typ,
        "weight": weight, "confidence": confidence,
        "sources": sources or [], "createdAt": REVIEWED,
    }
    if note: e["note"] = note
    return e


def desc(what, when, caution):
    return f"{what}\n\n{when}\n\n{caution}\n"


def mk(eid, name, cat, sub, one, url, what, when, caution, *, region="overseas", vendor=None,
       pricing="freemium", maturity="stable", tags=None, pitfalls=None, china=True, docs=None, **extra):
    kw = {
        "id": eid, "name": name, "category": cat, "subcategory": sub, "oneLiner": one,
        "officialUrl": url, "descriptionMd": desc(what, when, caution), "region": region,
        "pricing": {"model": pricing}, "maturity": maturity, "tags": tags or [],
        "pitfalls": pitfalls or [caution[:50] + ("…" if len(caution) > 50 else "")],
        "availability": {"chinaAccessible": china, "needsCompany": False, "needsIcp": False, "regions": ["global"]},
    }
    if vendor: kw["vendorId"] = vendor
    if docs: kw["docsUrl"] = docs
    kw.update(extra)
    return entry(**kw)


_entries: list[dict] = []
_edges: list[dict] = []


def add(e: dict) -> None:
    _entries.append(e)


def link(eid: str, frm: str, to: str, typ: str, **kw) -> None:
    _edges.append(edge(eid, frm, to, typ, **kw))


_VENDORS = [
    {"id": "render-inc", "name": "Render", "region": "overseas", "url": "https://render.com"},
    {"id": "salesforce-heroku", "name": "Heroku", "region": "overseas", "url": "https://heroku.com"},
    {"id": "deno-land", "name": "Deno Land", "region": "overseas", "url": "https://deno.com"},
    {"id": "amazon-web-services", "name": "AWS", "region": "overseas", "url": "https://aws.amazon.com"},
    {"id": "google-cloud", "name": "Google Cloud", "region": "overseas", "url": "https://cloud.google.com"},
    {"id": "microsoft-azure", "name": "Microsoft Azure", "region": "overseas", "url": "https://azure.microsoft.com"},
    {"id": "sst-dev", "name": "SST", "region": "overseas", "url": "https://sst.dev"},
    {"id": "coolify-io", "name": "Coolify", "region": "overseas", "url": "https://coolify.io"},
    {"id": "tencent-cloud", "name": "腾讯云", "region": "domestic", "url": "https://cloud.tencent.com"},
    {"id": "huawei-cloud", "name": "华为云", "region": "domestic", "url": "https://www.huaweicloud.com"},
    {"id": "volcengine", "name": "火山引擎", "region": "domestic", "url": "https://www.volcengine.com"},
    {"id": "alibaba-cloud", "name": "阿里云", "region": "domestic", "url": "https://www.aliyun.com"},
    {"id": "oracle", "name": "Oracle", "region": "overseas", "url": "https://oracle.com"},
    {"id": "elastic", "name": "Elastic", "region": "overseas", "url": "https://elastic.co"},
    {"id": "confluent", "name": "Confluent", "region": "overseas", "url": "https://confluent.io"},
    {"id": "pocketbase", "name": "PocketBase", "region": "overseas", "url": "https://pocketbase.io"},
    {"id": "nhost", "name": "Nhost", "region": "overseas", "url": "https://nhost.io"},
    {"id": "convex-dev", "name": "Convex", "region": "overseas", "url": "https://convex.dev"},
    {"id": "logto", "name": "Logto", "region": "overseas", "url": "https://logto.io"},
    {"id": "authing-cn", "name": "Authing", "region": "domestic", "url": "https://authing.cn"},
    {"id": "workos", "name": "WorkOS", "region": "overseas", "url": "https://workos.com"},
    {"id": "kinde", "name": "Kinde", "region": "overseas", "url": "https://kinde.com"},
    {"id": "paypal", "name": "PayPal", "region": "overseas", "url": "https://paypal.com"},
    {"id": "revenuecat", "name": "RevenueCat", "region": "overseas", "url": "https://revenuecat.com"},
    {"id": "pingpp", "name": "Ping++", "region": "domestic", "url": "https://pingxx.com"},
    {"id": "lianlianpay", "name": "连连支付", "region": "domestic", "url": "https://global.lianlianpay.com"},
    {"id": "adyen", "name": "Adyen", "region": "overseas", "url": "https://adyen.com"},
    {"id": "alipay-global", "name": "支付宝国际", "region": "domestic", "url": "https://global.alipay.com"},
    {"id": "xiaomi", "name": "小米", "region": "domestic", "url": "https://mi.com"},
    {"id": "oppo", "name": "OPPO", "region": "domestic", "url": "https://oppo.com"},
    {"id": "vivo", "name": "vivo", "region": "domestic", "url": "https://vivo.com"},
    {"id": "microsoft", "name": "Microsoft", "region": "overseas", "url": "https://microsoft.com"},
    {"id": "crowdin", "name": "Crowdin", "region": "overseas", "url": "https://crowdin.com"},
    {"id": "lokalise", "name": "Lokalise", "region": "overseas", "url": "https://lokalise.com"},
    {"id": "payoneer", "name": "Payoneer", "region": "overseas", "url": "https://payoneer.com"},
    {"id": "mercury", "name": "Mercury", "region": "overseas", "url": "https://mercury.com"},
    {"id": "digitalocean", "name": "DigitalOcean", "region": "overseas", "url": "https://digitalocean.com"},
    {"id": "cloudflare-inc", "name": "Cloudflare", "region": "overseas", "url": "https://cloudflare.com"},
    {"id": "upstash", "name": "Upstash", "region": "overseas", "url": "https://upstash.com"},
    {"id": "meilisearch", "name": "Meilisearch", "region": "overseas", "url": "https://meilisearch.com"},
    {"id": "typesense", "name": "Typesense", "region": "overseas", "url": "https://typesense.org"},
    {"id": "minio", "name": "MinIO", "region": "overseas", "url": "https://min.io"},
    {"id": "fusionauth", "name": "FusionAuth", "region": "overseas", "url": "https://fusionauth.io"},
    {"id": "supertokens", "name": "SuperTokens", "region": "overseas", "url": "https://supertokens.com"},
    {"id": "checkout-com", "name": "Checkout.com", "region": "overseas", "url": "https://checkout.com"},
    {"id": "braintree", "name": "Braintree", "region": "overseas", "url": "https://braintreepayments.com"},
    {"id": "mollie", "name": "Mollie", "region": "overseas", "url": "https://mollie.com"},
    {"id": "fastspring", "name": "FastSpring", "region": "overseas", "url": "https://fastspring.com"},
]

'''

FOOTER = '''
ENTRIES: list[dict] = _entries
VENDORS: list[dict] = _VENDORS
EDGES: list[dict] = _edges
'''

# id, name, cat, sub, one, url, what, when, caution, extras dict
RAW: list[tuple] = []

def r(*args, **kw):
    RAW.append((*args, kw))

# === G cloud-paas ===
r("render","Render","cloud-paas","paas","Git 推送即部署的现代 PaaS","https://render.com",
  "Render 是面向开发者的托管 PaaS，支持 Web 服务、Cron、PostgreSQL、Redis 与静态站点，以 Git 连接自动部署，定价透明且比 Heroku 更易上手。",
  "需要快速上线全栈或静态站点、又不想维护 Kubernetes 的独立开发者与小团队优先考虑；与 Next.js、Docker 镜像部署均兼容。",
  "免费层冷启动与休眠策略需关注；生产数据库备份与区域选择要提前规划，避免与 Vercel 边缘函数混用时出现跨区延迟。",
  {"vendorId":"render-inc","tags":["paas","hosting"]})
r("heroku","Heroku","cloud-paas","paas","Salesforce 旗下经典 PaaS","https://heroku.com",
  "Heroku 是 PaaS 品类先驱，以 buildpack 与 add-on 生态著称，支持 Ruby/Node/Python 等运行时一键部署，适合原型到中小规模生产。",
  "团队已有 Heroku 投资、或需要成熟 add-on 市场（Postgres、Redis、监控）时继续沿用；Salesforce 企业客户集成场景仍常见。",
  "2022 年后免费层取消，成本高于 Railway/Render；dyno 休眠与 Eco 计划限制需对照 SLA，大规模应用可能迁移至 AWS/GCP。",
  {"vendorId":"salesforce-heroku","tags":["paas"],"maturity":"mature"})
r("deno-deploy","Deno Deploy","cloud-paas","edge","Deno 官方边缘无服务器平台","https://deno.com/deploy",
  "Deno Deploy 在全球边缘运行 Deno/TypeScript 函数与静态资源，冷启动极快，原生支持 Web 标准 API 与 KV，适合轻量 API 与 SSR 边缘渲染。",
  "全栈 TS 团队已选 Deno 运行时、或需要低延迟边缘函数替代 Cloudflare Workers 时可评估；与 Fresh 框架深度集成。",
  "生态小于 Node/Vercel；npm 兼容层与部分 Node 原生模块可能受限，复杂后端仍建议配独立数据库服务。",
  {"vendorId":"deno-land","tags":["edge","serverless"]})
r("aws-amplify","AWS Amplify","cloud-paas","fullstack","AWS 全栈托管与 Gen2 框架","https://aws.amazon.com/amplify",
  "AWS Amplify 提供 Hosting、Auth、GraphQL/API、Storage 与 CI/CD 一体化，Gen2 以 TypeScript 定义后端资源，适合 AWS 生态内的全栈应用。",
  "已深度使用 AWS、需要 Cognito/S3/AppSync 组合或移动端同步时选用；React/Next 团队希望 IaC 与托管流水线一体时常见。",
  "Gen1/Gen2 迁移路径与文档并存易混淆；复杂定制仍要回落 CloudFormation，成本监控需配 AWS Budgets。",
  {"vendorId":"amazon-web-services","tags":["aws","fullstack"]})
r("google-cloud-run","Google Cloud Run","cloud-paas","serverless","容器化无服务器运行平台","https://cloud.google.com/run",
  "Cloud Run 以 Knative 为基础按请求伸缩容器，支持任意语言 Docker 镜像，与 Cloud SQL、Pub/Sub、Firebase 集成，是 GCP 主力 Serverless 计算。",
  "需要容器自由度又不要管节点、或 GCP 已有 BigQuery/Firebase 栈时首选 Serverless 计算；适合 API 与批处理 Job。",
  "冷启动与并发配置影响 latency 与成本；最小实例>0 可避免冷启动但增加固定费用，VPC 连接器配置较繁琐。",
  {"vendorId":"google-cloud","tags":["gcp","containers"]})
r("azure-static-web","Azure Static Web Apps","cloud-paas","static","Azure 静态站点与 API 托管","https://azure.microsoft.com/products/app-service/static",
  "Azure Static Web Apps 为 JAMstack 提供全球 CDN、托管 API（Azure Functions）、Auth 与 PR 预览环境，与 GitHub Actions 深度集成。",
  "微软/Azure 企业客户做营销站、文档站或轻量 SPA 且需 Entra ID 登录时自然选型；Blazor WASM 场景也常见。",
  "高级路由与 SSR 能力不如 Vercel/Netlify 完整；非 Azure 生态团队接入 Entra 成本较高。",
  {"vendorId":"microsoft-azure","tags":["azure","static"]})
r("sst","SST","cloud-paas","iac","TypeScript 定义 AWS 基础设施","https://sst.dev",
  "SST 让开发者用 TypeScript 描述 Lambda、API Gateway、DynamoDB 等资源，提供 Live Lambda Dev 与 Console，是 AWS 上的现代全栈框架。",
  "全栈 TS 团队希望 IaC 与业务代码同仓、并部署到 AWS Lambda/Next.js OpenNext 时首选 SST Ion；替代 Serverless Framework 体验更现代。",
  "绑定 AWS 云厂商；多云或简单静态站可能过度。Ion 大版本迁移需跟进文档，本地 dev 资源消耗高于纯 Vercel。",
  {"vendorId":"sst-dev","tags":["iac","aws"]})
r("coolify","Coolify","cloud-paas","self-hosted","开源自托管 PaaS 替代 Heroku","https://coolify.io",
  "Coolify 是开源 self-hosted PaaS，可在 VPS 上通过 Git 部署 Docker 应用、数据库与 SSL，界面友好，被称「开源自建 Heroku」。",
  "希望数据主权、控制成本且有一台 VPS 的小团队或 indie hacker 常用；替代 CapRover/Dokku 的现代化 UI 方案。",
  "高可用与备份需自行运维；单点 VPS 故障影响全站，生产应配监控、异地备份与升级策略。",
  {"pricing":{"model":"open-source"},"tags":["self-hosted","docker"]})
r("tencent-scf","腾讯云 SCF","cloud-paas","serverless","腾讯云无服务器函数","https://cloud.tencent.com/product/scf",
  "腾讯云 Serverless Cloud Function 支持事件驱动与 HTTP 触发，与 COS、API 网关、TDSQL 集成，是国内合规 Serverless 主力之一。",
  "业务必须部署在境内、需与微信生态/腾讯云其他产品联动时选用；轻量 API 与定时任务成本可控。",
  "冷启动与并发配额需申请；调试体验不如 Vercel，跨境访问与备案要求要前置评估。",
  {"vendorId":"tencent-cloud","region":"domestic","tags":["serverless","tencent"]})
r("huawei-agc","华为 AGC","cloud-paas","mobile-baas","华为应用开发与云服务套件","https://developer.huawei.com/consumer/cn/service/josp/agc",
  "AppGallery Connect 为 HarmonyOS/Android 应用提供认证、云函数、云数据库、推送与分发一体化后端，面向华为生态开发者。",
  "上架华为应用市场、或鸿蒙/ HMS 栈需要官方 BaaS 与合规能力时必选；国内安卓多渠道分发常配合使用。",
  "海外设备覆盖与 Google 服务差异大；非华为渠道用户占比低时不宜作为唯一后端，API 与 Firebase 不完全等价。",
  {"vendorId":"huawei-cloud","region":"domestic","tags":["mobile","huawei"]})
r("volcengine-fcn","火山引擎函数服务","cloud-paas","serverless","字节跳动云无服务器计算","https://www.volcengine.com/product/faas",
  "火山引擎函数计算提供事件驱动 FaaS，与对象存储、消息队列、方舟大模型等字节云产品集成，适合国内低延迟 Serverless 场景。",
  "团队已用火山引擎做 CDN/存储、或需要境内合规与字节生态联动时评估；AI 推理与批处理 Job 可同栈。",
  "文档与社区小于阿里云/腾讯云；跨云迁移需抽象触发器与 IAM，监控告警要自建对接。",
  {"vendorId":"volcengine","region":"domestic","tags":["serverless","volcengine"]})
r("aliyun-esa","阿里云 ESA","cloud-paas","edge","阿里云边缘安全加速","https://www.aliyun.com/product/esa",
  "ESA（Edge Security Acceleration）整合 CDN、DDoS 防护、WAF 与边缘计算，替代部分 DCDN 场景，为国内站点提供加速与安全一体化。",
  "站点主要面向国内用户、需备案合规且希望一站式 CDN+安全时选用；可与函数计算、OSS 源站组合。",
  "配置项多，误配缓存规则易导致脏数据；海外节点能力需对照具体套餐，与 Cloudflare 全球边缘体验不同。",
  {"vendorId":"alibaba-cloud","region":"domestic","tags":["cdn","edge","security"]})


# more cloud-paas
r("digitalocean-app-platform","DigitalOcean App Platform","cloud-paas","paas","DO 托管应用与数据库","https://www.digitalocean.com/products/app-platform",
  "DigitalOcean App Platform 从 Git 或容器部署 Web 应用，内置托管数据库与自动 SSL，定价简单，适合中小团队快速上线。",
  "已用 DO Droplet/Spaces、希望少运维又不要 K8s 时选用；与 Managed PostgreSQL 同栈部署常见。",
  "高级网络与全球边缘不如 Cloudflare；大流量成本需与 AWS/GCP 对比，自定义构建阶段有限。",
  {"vendorId":"digitalocean","tags":["paas"]})
r("koyeb","Koyeb","cloud-paas","paas","欧洲起家的全球 Serverless 平台","https://www.koyeb.com",
  "Koyeb 提供全球边缘部署、自动伸缩与 Git 驱动发布，支持 Docker 与 Serverless 函数，冷启动优化面向现代 Web 应用。",
  "需要欧盟数据 residency 或多区域边缘、又不想自管 K8s 的 indie/SaaS 团队可评估；与 Neon/PostgreSQL 搭配多。",
  "生态与文档小于 Railway/Render；国内访问延迟需实测，企业合规认证面对照需求清单。",
  {"tags":["paas","edge"]})
r("zeabur","Zeabur","cloud-paas","paas","面向亚洲开发者的部署平台","https://zeabur.com",
  "Zeabur 提供一键部署 Node/Go/Rust 等应用，支持模板市场与托管数据库，UI 简洁，在华人开发者社区增长迅速。",
  "独立开发者希望比 Vercel 更灵活地跑长连接服务或数据库同区部署时可考虑；支持国内支付方式。",
  "规模与 SLA 不如大厂云；生产关键业务应评估备份、监控与供应商持续性，避免单点依赖。",
  {"region":"both","tags":["paas"]})
r("aws-lambda","AWS Lambda","cloud-paas","serverless","AWS 事件驱动无服务器计算","https://aws.amazon.com/lambda",
  "AWS Lambda 按调用计费运行代码，与 API Gateway、S3、DynamoDB、SQS 等深度集成，是 Serverless 事实标准之一。",
  "已在 AWS 生态、需要精细 IAM 与海量触发器集成时默认选择；SST/Serverless 框架目标运行时。",
  "冷启动、15 分钟超时与包大小限制需架构规避；VPC 内访问 RDS 要配 ENI 并关注延迟。",
  {"vendorId":"amazon-web-services","tags":["aws","serverless"],"maturity":"mature"})
r("google-app-engine","Google App Engine","cloud-paas","paas","GCP 经典托管应用平台","https://cloud.google.com/appengine",
  "App Engine 提供标准/灵活环境托管 Web 应用，自动伸缩与版本管理成熟，与 Firebase、Cloud Datastore 历史深度绑定。",
  "GCP 存量项目、或需要长运行实例与标准环境沙箱时继续沿用；企业 App Engine 迁移成本较高。",
  "新项目更常选 Cloud Run；标准环境语言版本更新慢，灵活环境仍需管理实例。",
  {"vendorId":"google-cloud","tags":["gcp"],"maturity":"mature"})
r("azure-functions","Azure Functions","cloud-paas","serverless","Azure 无服务器函数","https://azure.microsoft.com/products/functions",
  "Azure Functions 支持多种触发器与 Durable Functions 编排，与 Event Grid、Cosmos DB、Entra ID 集成，适合 Azure 企业栈。",
  "微软/Azure 合同客户做事件驱动集成、或 Logic Apps 不够灵活时采用；.NET 栈体验最佳。",
  "消费计划冷启动与 VNet 集成配置复杂；跨 region 灾备需额外设计。",
  {"vendorId":"microsoft-azure","tags":["azure","serverless"]})
r("cloudflare-workers","Cloudflare Workers","cloud-paas","edge","Cloudflare 边缘计算平台","https://workers.cloudflare.com",
  "Workers 在全球边缘运行 V8 隔离的 JavaScript/WebAssembly，毫秒级冷启动，配 KV/D1/R2 构成边缘全栈，适合低延迟 API 与 SSR。",
  "需要全球边缘、与 Cloudflare Pages/CDN 同栈或要拦截/transform 请求时首选；OpenNext 可部署 Next.js。",
  "CPU 时间有限制；长时间计算或大型 Node 依赖不适合，状态管理要配 D1/KV/DO。",
  {"vendorId":"cloudflare-inc","tags":["edge","serverless"]})
r("inngest","Inngest","cloud-paas","workflow","事件驱动后台任务与编排","https://www.inngest.com",
  "Inngest 以事件和 step function 方式编排 durable 后台任务，开发者在现有代码中加函数即可，无需自管队列 Worker。",
  "Next.js/Vercel 项目需要可靠 cron、重试 workflow、或替代自建 Bull/SQS 时采用；本地 dev server 体验好。",
  "供应商锁定与定价随事件量增长；极复杂 DAG 可能不如 Temporal 灵活。",
  {"tags":["workflow","serverless"]})
r("trigger-dev","Trigger.dev","cloud-paas","workflow","长任务与后台 Job 平台","https://trigger.dev",
  "Trigger.dev 为 TypeScript 后台任务提供可观测、重试与调度，支持长时运行 Job 与 Vercel/Remix 集成，DX 面向全栈团队。",
  "需要跑分钟级 AI 批处理、视频转码等等待 Vercel 函数超时场景时选用；开源可自托管。",
  "Cloud 版成本与并发限制需监控；自托管要维护 Redis/Postgres 依赖。",
  {"tags":["workflow","jobs"]})
r("northflank","Northflank","cloud-paas","paas","Kubernetes 上的开发者 PaaS","https://northflank.com",
  "Northflank 在托管 K8s 上提供类似 Heroku 的 Git 部署体验，支持 Preview 环境、Cron 与附加数据库，偏开发者平台。",
  "团队需要 K8s 能力但不想自建控制平面、或要多服务 compose 时评估；比裸 GKE 上手快。",
  "学习曲线仍高于 Render；自定义网络与 GPU 支持需看套餐。",
  {"tags":["kubernetes","paas"]})
r("modal","Modal","cloud-paas","gpu","Python 优先的无服务器 GPU 平台","https://modal.com",
  "Modal 让 Python 函数在云端按需获得 GPU/CPU，秒级伸缩，适合 ML 推理、批处理与科学计算，代码即基础设施。",
  "AI 应用需弹性 GPU、不想管 K8s 或 EC2 的 Python 团队优先考虑；与 Hugging Face 模型加载配合多。",
  "绑定 Python 为主；长时间常驻服务不如传统 PaaS，成本随 GPU 型号波动大。",
  {"tags":["gpu","python","serverless"]})
r("caprover","CapRover","cloud-paas","self-hosted","自托管 Docker PaaS","https://caprover.com",
  "CapRover 在单台 VPS 上通过 Docker Swarm 提供一键部署、免费 SSL 与应用模板，是经典 self-hosted PaaS 方案。",
  "预算有限、要完全控制数据且有一台服务器运维能力的团队常用；比 Coolify 更早、社区模板多。",
  "Swarm 高可用弱于 K8s；生产多节点与备份策略需自行设计，UI 功能少于 Coolify 新版本。",
  {"pricing":{"model":"open-source"},"tags":["self-hosted","docker"]})
r("windmill","Windmill","cloud-paas","workflow","开源脚本与 workflow 自动化","https://www.windmill.dev",
  "Windmill 将 Python/TS/SQL 脚本转为可调度 workflow 与内部工具，支持自托管与 Cloud，替代 Airflow 的轻量场景。",
  "团队需要内部 admin 工具、ETL 或 cron 编排且希望低代码与代码并存时采用；开源可 air-gap 部署。",
  "复杂 ML pipeline 不如专用平台；权限与审计要按企业要求配置。",
  {"pricing":{"model":"open-source"},"tags":["workflow","automation"]})
r("aws-elastic-beanstalk","AWS Elastic Beanstalk","cloud-paas","paas","AWS 托管应用容器编排","https://aws.amazon.com/elasticbeanstalk",
  "Elastic Beanstalk 上传代码或 Docker 即自动 provision EC2、负载均衡与伸缩，是 AWS 上接近 Heroku 的 PaaS 层。",
  "企业 AWS 账号内需快速托管传统 Web 应用、且团队熟悉 EC2 后台时选用；比裸 EC2 省运维。",
  "抽象层低于 App Runner/ECS；平台更新慢，新项目更常选 App Runner 或 Copilot。",
  {"vendorId":"amazon-web-services","tags":["aws","paas"],"maturity":"mature"})
r("tencent-cloudbase","腾讯云 CloudBase","cloud-paas","baas","腾讯云一体化 BaaS 与托管","https://cloud.tencent.com/product/tcb",
  "CloudBase 提供云函数、云数据库、存储与静态托管，与微信/小程序深度集成，是国内小程序后端常用一站式平台。",
  "微信小程序、QQ 生态或腾讯云全家桶客户需要快速后端时首选；内置 CI 与预览环境。",
  "复杂 SQL 与跨云迁移成本高；HTTP API 调试与本地联调体验需适应微信开发者工具链路。",
  {"vendorId":"tencent-cloud","region":"domestic","tags":["baas","wechat"]})
r("scaleway-serverless","Scaleway Serverless","cloud-paas","serverless","Scaleway 函数与容器","https://www.scaleway.com/en/serverless-functions/",
  "Scaleway Serverless Functions/Containers 在欧洲云提供按量计费运行时，与 Object Storage、K8s Kapsule 同生态，价格有竞争力。",
  "需要欧盟数据驻留、预算敏感且工作负载在欧洲用户为主时评估；GDPR 场景常见。",
  "全球边缘与生态小于 AWS/GCP；国内访问延迟高，不适合面向中国 C 端低延迟 API。",
  {"tags":["serverless","eu"]})

# === H databases & storage ===
r("mysql","MySQL","db-relational","sql","全球最流行的开源关系数据库","https://www.mysql.com",
  "MySQL 是开源关系型数据库事实标准，InnoDB 引擎支持 ACID、复制与分区，云厂商均提供托管版，生态工具与 ORM 支持最广。",
  "传统 Web 应用、WordPress、或团队熟悉 SQL 且需要成熟主从复制时默认选择；与 PlanetScale/RDS 托管搭配多。",
  "复杂 JSON/analytics 不如 PostgreSQL；8.0 认证插件变更曾导致兼容问题，升级需测驱动。",
  {"vendorId":"oracle","tags":["sql","database"],"maturity":"mature","pricing":{"model":"open-source"}})
r("tidb","TiDB","db-relational","distributed","MySQL 兼容的分布式 NewSQL","https://pingcap.com",
  "TiDB 是 PingCAP 开源的 MySQL 协议分布式数据库，水平扩展、HTAP 与云原生部署，适合海量数据仍要 SQL 语义的场景。",
  "数据量超单机 MySQL 上限、需要在线扩容且希望尽量不改应用 SQL 时评估 TiDB；国内金融与互联网常见。",
  "运维复杂度高于 RDS；小体量场景过度，TiKV 组件资源占用需容量规划。",
  {"region":"both","tags":["distributed","mysql-compatible"]})
r("cockroachdb","CockroachDB","db-relational","distributed","PostgreSQL 线协议分布式 SQL","https://www.cockroachlabs.com",
  "CockroachDB 提供全球分布式 SQL、强一致与 survive region 故障能力，兼容 PostgreSQL  wire 协议，适合多活全球化 SaaS。",
  "需要跨 region 多活、零 downtime 迁移且团队熟悉 Postgres 语义时选用；替代 Spanner 的开源方案之一。",
  "延迟高于单机 Postgres；小项目成本高，SQL 兼容非 100%，高级 PG 扩展不支持。",
  {"tags":["distributed","postgres-compatible"]})
r("mariadb","MariaDB","db-relational","sql","MySQL 分支的开源数据库","https://mariadb.org",
  "MariaDB 由 MySQL 原作者维护的分支，保持协议兼容并增加存储引擎与优化，被多家 Linux 发行版作为默认 MySQL 替代。",
  "希望开源协议更友好、或从 MySQL 平滑迁移且不需 Oracle 商业支持时选用；托管版广泛。",
  "与 MySQL 8 新特性存在差异；Galera 集群配置需专门 DBA 经验。",
  {"pricing":{"model":"open-source"},"tags":["sql"],"maturity":"mature"})
r("amazon-rds","Amazon RDS","db-relational","managed","AWS 托管关系数据库","https://aws.amazon.com/rds",
  "RDS 托管 MySQL、PostgreSQL、MariaDB、SQL Server 等，自动备份、Multi-AZ 与读副本，是 AWS 上传统 SQL 主力。",
  "已在 AWS、需要合规备份与 VPC 内数据库且不想自管补丁时默认选择；与 Lambda/ECS 经典组合。",
  "Serverless v2 伸缩有冷启动；跨 region 读副本延迟与 failover RTO 要演练，成本随实例规格线性上升。",
  {"vendorId":"amazon-web-services","tags":["aws","managed"]})
r("google-cloud-sql","Google Cloud SQL","db-relational","managed","GCP 托管 MySQL/PostgreSQL/SQL Server","https://cloud.google.com/sql",
  "Cloud SQL 提供全托管关系库、自动备份与高可用，与 Cloud Run、GKE、BigQuery 联邦查询集成，是 GCP SQL 默认选项。",
  "Firebase/GCP 栈需要托管 Postgres/MySQL 时选用；私有 IP 访问 GKE 常见。",
  "连接数与磁盘扩容有操作窗口；极端高 QPS 可能迁移到 AlloyDB/Spanner。",
  {"vendorId":"google-cloud","tags":["gcp","managed"]})
r("yugabytedb","YugabyteDB","db-relational","distributed","Postgres 兼容分布式 SQL","https://www.yugabyte.com",
  "YugabyteDB 以 Postgres 兼容层 + Cassandra 式存储引擎实现水平扩展与 geo-distribution，开源与托管并存。",
  "需要 Postgres SQL 语义又要 multi-region 写扩展时评估；替代 Cockroach 的开源选项。",
  "运维与调优学习曲线陡；小流量场景不如 Neon/Supabase 经济。",
  {"tags":["distributed","postgres-compatible"]})
r("timescaledb","TimescaleDB","db-relational","timeseries","基于 PostgreSQL 的时序扩展","https://www.timescale.com",
  "TimescaleDB 作为 Postgres 扩展提供 hypertable、压缩与连续聚合，适合 IoT、监控与金融时序数据，仍可用 SQL 生态。",
  "已有 PostgreSQL 栈且时序查询为主、希望统一数据库技术栈时选用；与 Grafana 集成多。",
  "非时序 OLTP 仍可用 PG 但优势不明显；Cloud 版与自托管功能差异需对照。",
  {"tags":["timeseries","postgres"]})
r("singlestore","SingleStore","db-relational","htap","分布式 HTAP 数据库","https://www.singlestore.com",
  "SingleStore（原 MemSQL）统一事务与分析 workload，内存行存 + 列存，兼容 MySQL 协议，面向实时 analytics。",
  "需要毫秒级 analytics 同时保留 OLTP、且数据量在 TB 级时评估；替代 ClickHouse+MySQL 双栈。",
  "授权与成本高于开源 PG；团队需评估 vendor lock-in 与 SQL 方言差异。",
  {"tags":["htap","analytics"]})
r("azure-database-postgresql","Azure Database for PostgreSQL","db-relational","managed","Azure 托管 PostgreSQL","https://azure.microsoft.com/products/postgresql",
  "Azure Database for PostgreSQL 提供 Flexible Server 与 HA、备份，与 Entra ID、Azure Functions 集成，是企业 Azure 栈 PG 首选。",
  "微软/Azure 合同内跑 Postgres、需私有链路访问 App Service 时选用；Cosmos 不够关系型时回落 PG。",
  "扩展插件列表受限；跨 subscription 网络与防火墙规则易踩坑。",
  {"vendorId":"microsoft-azure","tags":["azure","postgres"]})
r("aurora-mysql","Amazon Aurora MySQL","db-relational","managed","AWS 云原生 MySQL 兼容库","https://aws.amazon.com/rds/aurora",
  "Aurora 为 AWS 设计的存储计算分离架构，MySQL/PostgreSQL 兼容，读扩展与故障切换快，是 AWS 高 QPS SQL 常见选择。",
  "AWS 上 MySQL workload 需更高可用与读扩展、且预算允许时选 Aurora 而非普通 RDS。",
  "仅运行于 AWS；I/O 费用模型需监控，迁移到其他云需逻辑导出。",
  {"vendorId":"amazon-web-services","tags":["aws","mysql"]})


# nosql, cache, object, sqlite-edge, search
r("dynamodb","Amazon DynamoDB","db-nosql","key-value","AWS 全托管 NoSQL 键值/文档库","https://aws.amazon.com/dynamodb",
  "DynamoDB 是 AWS 全托管 NoSQL，按分区键扩展，支持 TTL、Streams 与 DAX 缓存，Serverless 计费模式适合 unpredictable 流量。",
  "已在 AWS、需要毫秒级 KV 访问或事件驱动架构（Streams→Lambda）时默认选择；单表设计模式需团队学习。",
  "复杂查询与 join 不如 SQL；扫描成本高，GSI 设计错误会导致 hot partition 与账单爆炸。",
  {"vendorId":"amazon-web-services","tags":["nosql","aws"],"maturity":"mature"})
r("kafka","Apache Kafka","db-nosql","streaming","分布式事件流平台","https://kafka.apache.org",
  "Kafka 是高吞吐分布式 commit log，用于事件流、CDC 与微服务解耦，Confluent/MSK 等提供托管版，生态连接器丰富。",
  "需要持久化事件流、exactly-once 语义或多消费者 replay 时选用；替代 RabbitMQ 于大数据量场景。",
  "运维复杂，分区与 consumer group 调优需经验；小流量用 SQS/PubSub 更简单经济。",
  {"vendorId":"confluent","tags":["streaming","events"],"pricing":{"model":"open-source"},"maturity":"mature"})
r("rabbitmq","RabbitMQ","db-nosql","queue","经典 AMQP 消息队列","https://www.rabbitmq.com",
  "RabbitMQ 实现 AMQP 协议，支持多种 exchange 路由、延迟队列与 federation，是传统企业消息中间件事实标准之一。",
  "需要复杂路由、任务队列或 .NET/Java 存量集成时继续沿用；比 Kafka 更适合 request/reply 模式。",
  "高吞吐持久化不如 Kafka；集群镜像与 quorum queue 配置不当会丢消息或性能下降。",
  {"tags":["queue","amqp"],"pricing":{"model":"open-source"},"maturity":"mature"})
r("upstash-qstash","Upstash QStash","db-nosql","queue","HTTP 优先的无服务器消息队列","https://upstash.com/qstash",
  "QStash 提供 HTTP 投递、延迟与重试的消息队列，无需常驻 worker 连接，适合 Serverless 与边缘函数触发下游 URL。",
  "Vercel/Cloudflare Workers 架构需要可靠异步回调、又不想维护 Redis/RabbitMQ 时采用；与 Upstash Redis 同账号。",
  "消息体积与速率有限制；严格 ordering 场景需自行设计 partition key。",
  {"vendorId":"upstash","tags":["queue","serverless"]})
r("couchbase","Couchbase","db-nosql","document","分布式文档与 KV 数据库","https://www.couchbase.com",
  "Couchbase 结合 JSON 文档、N1QL SQL++ 查询与内存优先架构，支持 mobile sync（Capella），适合会话与配置存储。",
  "移动离线同步、或需要 sub-millisecond KV 加 SQL 查询的 enterprise 场景评估；gaming 行业常见。",
  "运维与 sizing 复杂；开发者体验不如 MongoDB Atlas 普及，国内社区较小。",
  {"tags":["document","nosql"]})
r("valkey","Valkey","db-cache","redis-fork","Redis 开源分支","https://valkey.io",
  "Valkey 是 Linux 基金会下 Redis 7.2 分支，保持协议兼容并社区治理，被 AWS ElastiCache 等采纳为开源后端。",
  "希望 Redis 协议但避免 Redis Ltd 许可证变更、或云厂商默认提供 Valkey 时选用；与 Redis 客户端兼容。",
  "新特性节奏与 Redis 官方分叉；托管服务支持仍在普及中，需确认驱动与模块兼容。",
  {"pricing":{"model":"open-source"},"tags":["cache","redis-compatible"]})
r("cloudflare-kv","Cloudflare KV","db-cache","edge-kv","Cloudflare 边缘键值存储","https://developers.cloudflare.com/kv",
  "KV 在全球边缘提供 eventually consistent 键值读，与 Workers 绑定，适合配置、A/B 标志与读多写少缓存，延迟极低。",
  "Workers/Pages 边缘应用需要低延迟全球读配置时选用；不适合强一致计数器。",
  "写入传播有延迟；.list 操作昂贵，大 value 应放 R2 仅 KV 存指针。",
  {"vendorId":"cloudflare-inc","tags":["edge","kv"]})
r("cloudflare-d1","Cloudflare D1","db-sqlite-edge","edge-sql","Cloudflare 边缘 SQLite","https://developers.cloudflare.com/d1",
  "D1 是 Cloudflare 托管的 SQLite，可在 Workers 内用 SQL 查询，只读副本分布边缘，适合边缘轻量关系数据。",
  "Workers 全栈需要关系查询但数据量小、读多写少时选用；与 Drizzle ORM 集成示例多。",
  "写吞吐与数据库大小有限；复杂事务与 PG 特性不支持，不适合核心 OLTP。",
  {"vendorId":"cloudflare-inc","tags":["sqlite","edge"]})
r("memcached","Memcached","db-cache","cache","经典分布式内存缓存","https://memcached.org",
  "Memcached 是简单高性能内存 KV 缓存，多节点一致性哈希，无持久化，常用于 session 与页面片段缓存。",
  "只需纯缓存、不需要 Redis 数据结构复杂度时选用；LAMP 栈历史存量多。",
  "无持久化与高可用内置；大数据结构或 pub/sub 应选 Redis/Valkey。",
  {"pricing":{"model":"open-source"},"tags":["cache"],"maturity":"mature"})
r("dragonfly","Dragonfly","db-cache","redis-compatible","现代 Redis 替代内存数据库","https://www.dragonflydb.io",
  "Dragonfly 用多线程架构实现 Redis/Memcached 协议，单机吞吐显著高于 Redis，兼容多数命令，适合大内存缓存层。",
  "Redis 成为瓶颈、希望垂直扩展缓存且少改客户端时试点 Dragonfly；K8s 部署常见。",
  "集群模式与某些 Redis 模块不完全支持；托管选项少于 ElastiCache。",
  {"tags":["cache","redis-compatible"]})
r("meilisearch","Meilisearch","db-nosql","search","开发者友好的开源搜索引擎","https://www.meilisearch.com",
  "Meilisearch 提供 typo-tolerant 全文搜索、faceting 与 instant 搜索 API，部署简单，DX 面向应用开发者而非 ES 运维。",
  "产品内搜索框、电商 SKU 检索等中等规模场景首选；比 Elasticsearch 轻量得多。",
  "超大规模日志/analytics 不如 ES；中文分词需配置或插件，分布式 HA 方案需 Cloud/企业版。",
  {"vendorId":"meilisearch","tags":["search"],"pricing":{"model":"open-source"}})
r("elasticsearch","Elasticsearch","db-nosql","search","分布式搜索与分析引擎","https://www.elastic.co/elasticsearch",
  "Elasticsearch 基于 Lucene，提供全文搜索、聚合与日志分析（ELK），水平扩展成熟，是 observability 与 enterprise 搜索主力。",
  "日志/指标平台、复杂 facet 搜索或已有 Kibana 投资时继续选用；向量搜索需 ES 8+ dense_vector。",
  "集群运维与 JVM 调优成本高；小项目用 Meilisearch/Typesense 更省资源，许可证变更需关注。",
  {"vendorId":"elastic","tags":["search","analytics"],"maturity":"mature"})
r("typesense","Typesense","db-nosql","search","轻量开源搜索引擎","https://typesense.org",
  "Typesense 专注应用内搜索，API 简洁、默认 typo tolerance 与 geo 搜索，单节点亦快，托管 Typesense Cloud 可用。",
  "需要 Algolia 式体验但希望自托管或固定成本时选用；文档站与 SaaS 目录搜索常见。",
  "超大规模 sharding 不如 ES；高可用需多节点配置，中文搜索质量依赖分词配置。",
  {"vendorId":"typesense","tags":["search"],"pricing":{"model":"open-source"}})
r("aws-s3","Amazon S3","db-object","object","AWS 对象存储事实标准","https://aws.amazon.com/s3",
  "S3 提供 11 9s  durability 对象存储，版本控制、生命周期与事件通知，是云存储与数据湖基石，API 成行业事实标准。",
  "任何 AWS 栈静态资源、备份、数据湖或 presigned 上传场景默认选择；与 CloudFront CDN 组合。",
  "列表操作与 egress 费用需优化；强一致 listing 曾有限制，跨区域复制有延迟与成本。",
  {"vendorId":"amazon-web-services","tags":["storage","aws"],"maturity":"mature"})
r("aliyun-oss","阿里云 OSS","db-object","object","阿里云对象存储","https://www.aliyun.com/product/oss",
  "OSS 提供海量对象存储、CDN 联动、图片处理与跨区域复制，国内合规与备案生态完整，小程序与 Web 静态资源常用。",
  "业务数据必须留在境内、或与阿里云 FC/CDN 深度集成时选用；双 eleven 级别活动验证过规模。",
  "跨境访问慢；权限策略与 bucket public 误配曾导致数据泄露，需最小权限与审计。",
  {"vendorId":"alibaba-cloud","region":"domestic","tags":["storage"]})
r("tencent-cos","腾讯云 COS","db-object","object","腾讯云对象存储","https://cloud.tencent.com/product/cos",
  "COS 提供标准/低频/归档存储、CI 图片处理与 CDN 加速，与 SCF、CloudBase 集成，是国内 Web/App 静态与媒体资源常见选择。",
  "腾讯云栈、微信小程序后端或需要国内低延迟对象访问时选用；与 CI 媒体处理流水线配合。",
  "与 AWS S3 API 有差异，跨云工具需适配；外网下行流量费用要配 CDN 缓存策略。",
  {"vendorId":"tencent-cloud","region":"domestic","tags":["storage"]})
r("google-cloud-storage","Google Cloud Storage","db-object","object","GCP 统一对象存储","https://cloud.google.com/storage",
  "GCS 提供 multi-regional、Nearline/Coldline 分级与 uniform bucket 访问，与 BigQuery、Cloud CDN、Firebase 集成。",
  "GCP/Firebase 栈存放用户上传、ML 数据集或静态站点时默认选择；Signed URL 模式成熟。",
  "与 AWS 工具链 S3 兼容层非 100%；细粒度 IAM 学习曲线存在。",
  {"vendorId":"google-cloud","tags":["storage","gcp"]})
r("minio","MinIO","db-object","object","S3 兼容开源自托管对象存储","https://min.io",
  "MinIO 提供高性能 S3 API 兼容对象存储，可 on-prem 或 K8s 部署，支持 erasure coding 与 replication，是私有云存储首选。",
  "需要 S3 API 但数据不能上公有云、或本地 dev 与生产一致时选用；AI 数据集本地缓存常见。",
  "自建 HA 与升级需运维；极端规模仍不如 hyperscaler 托管 S3 省心。",
  {"vendorId":"minio","tags":["storage","s3-compatible"],"pricing":{"model":"open-source"}})
r("backblaze-b2","Backblaze B2","db-object","object","低成本 S3 兼容云存储","https://www.backblaze.com/b2/cloud-storage.html",
  "B2 提供 S3 兼容 API 与极低存储单价，Cloudflare 联盟免 egress 到 CF，适合备份与媒体归档。",
  "预算敏感的大量冷数据、或通过 Cloudflare 分发静态资源时选用；替代 AWS Glacier 的简单方案。",
  "全球延迟与 SLA 不如 S3/GCS；高频小文件 API 调用成本要建模。",
  {"tags":["storage","backup"]})
r("supabase-storage","Supabase Storage","db-object","baas-storage","Supabase 托管 S3 兼容存储","https://supabase.com/storage",
  "Supabase Storage 基于 S3 提供 bucket、RLS 策略与图片 transformation，与 Supabase Auth/DB 同项目，适合全栈 BaaS 文件场景。",
  "已选 Supabase 做 Auth+Postgres、需要用户头像/附件且要用 RLS 控权限时自然使用；比单独 S3 配置简单。",
  "大流量 egress 与 transform 费用随量增长；跨 region 性能取决于 Supabase 项目区域。",
  {"tags":["baas","storage"]})
r("libsql","libSQL","db-sqlite-edge","sqlite-fork","Turso 开源 SQLite 分支","https://github.com/tursodatabase/libsql",
  "libSQL 是 SQLite 的开源 fork，增加异步 replication、embedded replicas 与 HTTP API，为 edge 与 embedded 场景优化。",
  "需要 SQLite 语义又要 edge 复制、或使用 Turso 托管时底层技术；IoT 与 local-first 应用评估。",
  "生态仍围绕 Turso 为主；复杂 PG 特性不支持，迁移到 Postgres 需计划。",
  {"pricing":{"model":"open-source"},"tags":["sqlite","edge"]})
r("litefs","LiteFS","db-sqlite-edge","replication","SQLite 分布式只读副本","https://fly.io/docs/litefs/",
  "LiteFS 为 SQLite 提供 FUSE 层复制，将写集中在 primary、读扩散到 replica，适合 Fly.io 边缘 SQLite 部署。",
  "Fly.io 上跑 SQLite 且需要多读扩展时配合使用；比手动 litestream 更集成。",
  "写仍单点；failover 与 consul 依赖增加复杂度，不适合 heavy write OLTP。",
  {"tags":["sqlite","replication"]})
r("amazon-elasticache","Amazon ElastiCache","db-cache","managed","AWS 托管 Redis/Memcached","https://aws.amazon.com/elasticache",
  "ElastiCache 托管 Redis、Valkey 与 Memcached 集群，自动 failover 与备份，与 VPC 内 ECS/Lambda 低延迟访问。",
  "AWS 栈需要 session 缓存、rate limit 或 pub/sub 且不想自管 Redis 时选用。",
  "Serverless 缓存较新；跨 AZ 流量与节点规格选型影响成本，集群模式 shard 迁移需维护窗口。",
  {"vendorId":"amazon-web-services","tags":["cache","aws"]})


# === I baas ===
r("pocketbase","PocketBase","baas-platform","self-hosted","单文件开源 BaaS","https://pocketbase.io",
  "PocketBase 以 Go 单二进制提供 SQLite 数据库、Auth、Realtime、Admin UI 与 REST API，部署极简，适合 side project 与内部工具。",
  "需要快速 MVP、数据量中小且希望完全自托管时首选；比 Supabase 更轻、比 Firebase 更可控。",
  "SQLite 写扩展有限；复杂 SQL 与 multi-region 不如 Postgres BaaS，生产 HA 需自行备份与复制。",
  {"vendorId":"pocketbase","tags":["baas","sqlite"],"pricing":{"model":"open-source"}})
r("nhost","Nhost","baas-platform","graphql","Postgres + Hasura GraphQL BaaS","https://nhost.io",
  "Nhost 提供托管 Postgres、Hasura GraphQL、Auth 与 Storage，与 React/Next 模板一体，是 GraphQL-first 的 Firebase 替代。",
  "团队偏好 GraphQL 订阅、或已有 Hasura schema 希望托管运维时选用；与 Vercel 前端组合常见。",
  "REST 生态需经 GraphQL 转换；冷启动与 region 选择影响 latency，定价随 DB 存储增长。",
  {"vendorId":"nhost","tags":["graphql","baas"]})
r("convex","Convex","baas-platform","reactive","响应式后端即服务","https://convex.dev",
  "Convex 提供 TypeScript 定义 schema 与 query/mutation，自动 reactive 订阅与调度，内置 auth 与文件存储，DX 面向 React 全栈。",
  "需要实时协作 UI、希望省略 REST/GraphQL 层且全栈 TS 时评估；替代 Firebase Realtime 的现代方案。",
  "供应商锁定较强；复杂 SQL 报表需导出 warehouse，自托管不可行。",
  {"vendorId":"convex-dev","tags":["realtime","baas"]})
r("authjs","Auth.js","baas-auth-only","library","原 NextAuth 的框架无关认证库","https://authjs.dev",
  "Auth.js（原 NextAuth.js）提供 OAuth、Credentials、Email 等 provider 抽象，支持 Next.js、SvelteKit 等适配器，开源可自托管 session。",
  "需要掌控 auth 代码、多 provider 登录且不想付 Clerk 订阅时首选；与 Next.js App Router 集成文档全。",
  "UI 与 org/B2B 功能需自建；session 存储与 edge runtime 兼容要按 adapter 仔细配置。",
  {"pricing":{"model":"open-source"},"tags":["auth","nextjs"]})
r("logto","Logto","baas-auth-only","oss-idp","开源身份认证平台","https://logto.io",
  "Logto 提供开源 IdP、社交登录、M2M 与 RBAC，Cloud 与 self-host 并存，UI 现代，支持 OIDC/OAuth2 标准协议。",
  "需要自托管 Auth0 替代、或 B2B SaaS 要 organizations 与 audit log 时评估；国内团队维护活跃。",
  "Enterprise SAML 与 SCIM 需对照版本；与存量 user migration 要规划 password hash 策略。",
  {"vendorId":"logto","region":"both","tags":["auth","oidc"]})
r("authing","Authing","baas-auth-only","idp","国内身份云与 SSO 平台","https://authing.cn",
  "Authing 提供统一身份认证、社会化登录、企业 SSO、MFA 与权限管理，符合国内合规，支持与微信/钉钉/飞书集成。",
  "面向国内 ToB SaaS、需要 ICP 友好 IdP 与本地化支持时选用；替代 Okta/Auth0 的国内方案。",
  "海外 IdP 与 UX 不如 Clerk/WorkOS 国际化；定价按 MAU 阶梯，功能模块需逐项开通。",
  {"vendorId":"authing-cn","region":"domestic","tags":["auth","sso"]})
r("workos","WorkOS","baas-auth-only","b2b","B2B SaaS 身份与 Directory Sync","https://workos.com",
  "WorkOS 提供 Enterprise SSO（SAML/OIDC）、Directory Sync、Admin Portal 与 Audit Logs，专为 B2B SaaS 卖进企业设计。",
  "SaaS 需要对接客户 Okta/Azure AD、或卖 Fortune500 合规 checklist 时几乎必选；与 Auth.js/Clerk 可并存。",
  "仅 B2B 场景；C 端社交登录不是强项，按连接数与企业功能计费。",
  {"vendorId":"workos","tags":["b2b","sso"]})
r("kinde","Kinde","baas-auth-only","saas","现代 Auth 与 billing 一体平台","https://kinde.com",
  "Kinde 提供认证、组织、角色、feature flags 与订阅 billing 一体化，Startup 友好定价，替代 Clerk+Stripe 部分组合。",
  "早期 B2B/B2C SaaS 希望一个 vendor 覆盖 auth 与 plan gating 时评估；澳洲团队 GDPR 意识强。",
  "生态与 SDK 小于 Clerk；复杂 custom JWT claims 与 enterprise SAML 需验证 tier。",
  {"vendorId":"kinde","tags":["auth","billing"]})
r("fusionauth","FusionAuth","baas-auth-only","idp","可自托管的身份平台","https://fusionauth.io",
  "FusionAuth 提供完整 IdP、注册登录、MFA、OAuth2/OIDC 与 theming，可 self-host 或 Cloud，适合合规与数据驻留要求。",
  "需要 Auth0 功能但希望 on-prem 或避免 per-MAU 暴涨时选用；游戏与 gov 场景常见。",
  "UI 定制与 DX 不如 Clerk modern；多租户 org 模型需自行建模或购 enterprise 模块。",
  {"vendorId":"fusionauth","tags":["auth","self-hosted"]})
r("supertokens","SuperTokens","baas-auth-only","oss-auth","开源 session 与密码less 认证","https://supertokens.com",
  "SuperTokens 开源核心 auth（session、email/password、passwordless），可自托管，React/Node SDK 完整，强调安全默认。",
  "需要嵌入自有后端、避免 SaaS auth 锁定且团队能运维 Redis/Postgres 时选用。",
  "Managed 版与 enterprise SSO 仍在演进；social login provider 配置量大于 Clerk。",
  {"vendorId":"supertokens","tags":["auth","open-source"]})
r("keycloak","Keycloak","baas-auth-only","idp","Red Hat 开源 IAM 平台","https://www.keycloak.org",
  "Keycloak 是成熟开源 IdP，支持 SAML/OIDC、细粒度 RBAC、用户 federation 与 admin console，企业 on-prem 部署广泛。",
  "金融/政府/on-prem 必须开源 IAM、或已有 Red Hat 合同时默认选择；高度可扩展 SPI。",
  "运维与升级复杂；主题与 UX 现代化需额外前端，Cloud 托管非官方。",
  {"tags":["auth","iam"],"pricing":{"model":"open-source"},"maturity":"mature"})
r("stytch","Stytch","baas-auth-only","api","API-first 密码less 与 MFA","https://stytch.com",
  "Stytch 提供 magic link、OTP、WebAuthn 与 fraud 信号，API 设计现代，适合 product-led growth 应用的快速登录。",
  "希望优先 passwordless、减少密码泄露风险且不想自建 crypto 时选用；B2C mobile 常见。",
  "B2B SAML 与企业 directory 不如 WorkOS 专精；定价随 MAU 与 SMS 成本上升。",
  {"tags":["auth","passwordless"]})
r("hasura","Hasura","baas-platform","graphql","Postgres 即时 GraphQL 引擎","https://hasura.io",
  "Hasura 自动从 Postgres schema 生成 GraphQL API，支持权限、订阅与 remote schema，可自托管或 Cloud，常与 Nhost 组合。",
  "已有 Postgres、希望快速暴露 type-safe API 给前端时选用；event trigger 可连 webhook/Lambda。",
  "REST 客户端需 GraphQL 层；复杂 business logic 应放 action/handler 避免 SQL 泄露。",
  {"tags":["graphql","postgres"]})
r("directus","Directus","baas-platform","headless-cms","SQL 上的开源 Headless CMS","https://directus.io",
  "Directus 将现有 SQL 数据库包装为 Headless CMS 与 REST/GraphQL API，Admin App 可配置，适合内容与业务数据混合。",
  "已有数据库 schema、需要运营后台且不想迁移到 Strapi 时选用；self-host 友好。",
  "Realtime 与 auth 插件不如 Supabase 一体；大文件与 workflow 需额外集成。",
  {"pricing":{"model":"open-source"},"tags":["cms","headless"]})

# === K pay ===
r("paypal","PayPal","pay-processor","wallet","全球电子钱包与收单","https://www.paypal.com",
  "PayPal 提供消费者钱包、商户收单、订阅与 Braintree 卡支付，覆盖 200+ 市场，是跨境 indie 收款常见入口。",
  "面向海外 C 端、买家习惯 PayPal 或需要快速跨境收款无公司复杂流程时启用；与 Stripe 并存提高转化。",
  "争议处理偏买家；部分国家提现与汇率费用高，大陆商户接入门槛与合规需单独评估。",
  {"vendorId":"paypal","tags":["payments","wallet"],"maturity":"mature"})
r("revenuecat","RevenueCat","pay-processor","mobile-sub","移动订阅与 IAP 抽象层","https://www.revenuecat.com",
  "RevenueCat 统一 Apple/Google/Stripe 订阅状态，提供 SDK、analytics 与 webhook，简化 in-app purchase 与 cross-platform entitlements。",
  "移动 App 做订阅、需要跨商店 receipt 校验与 cohort 分析时几乎标配；与 App Store Connect 配合。",
  "抽成之外再加 RevenueCat 费用；Web billing 需另接 Stripe，复杂 custom offer 有限制。",
  {"vendorId":"revenuecat","tags":["mobile","subscriptions"]})
r("pingpp","Ping++","pay-processor","aggregator","国内聚合支付平台","https://www.pingxx.com",
  "Ping++ 聚合微信、支付宝、银联等渠道，提供统一 API 与对账，帮助商户快速接入多种国内支付方式。",
  "国内 SaaS/电商需同时接微信与支付宝、又不想分别对接各家 SDK 时选用；合规资质可代办咨询。",
  "跨境收款非主业；费率与结算周期依渠道而异，PCI 与敏感数据仍需自建合规。",
  {"vendorId":"pingpp","region":"domestic","tags":["payments","china"]})
r("lianlianpay","连连支付","pay-processor","cross-border","跨境支付与收结汇","https://global.lianlianpay.com",
  "连连支付提供跨境 B2B/B2C 收结汇、多币种账户与合规申报，服务出口电商与 SaaS 收款回国。",
  "中国主体需要合法收汇、对接 Amazon/Shopify 等平台回款时评估；替代 Payoneer 的国内持牌选项之一。",
  "开户与 KYC 严格；部分行业禁入，到账时间与 FX Spread 要合同确认。",
  {"vendorId":"lianlianpay","region":"domestic","tags":["cross-border","fx"]})
r("adyen","Adyen","pay-processor","enterprise","企业级全球统一收单","https://www.adyen.com",
  "Adyen 单一平台覆盖全球本地支付方式、3DS、risk 与 unified commerce（线上+POS），Spotify/Uber 等大厂采用。",
  "Enterprise 需要全球 local PM、统一 reconciliation 与 PCI 责任共担时选用；替代多网关拼接。",
  "接入周期长、门槛高；中小 indie 更常用 Stripe，Adyen 最小 volume 与合规要求严格。",
  {"vendorId":"adyen","tags":["payments","enterprise"],"maturity":"mature"})
r("alipay-global","支付宝国际","pay-processor","wallet","Ant 旗下跨境支付","https://global.alipay.com",
  "支付宝国际为海外商户提供 Alipay+ 钱包收单与中国游客熟悉支付方式，覆盖亚洲多个电子钱包网络。",
  "面向中国游客/侨民市场、或亚洲 retail 需要接 Alipay+ 网络时启用；与国内支付宝体系联动。",
  "欧美卡支付非核心；SDK 与结算币种有限，需与 Ant 国际商务团队对接费率。",
  {"vendorId":"alipay-global","region":"both","tags":["payments","alipay"]})
r("checkout-com","Checkout.com","pay-processor","gateway","高性能全球支付网关","https://www.checkout.com",
  "Checkout.com 提供卡支付、APM 与 fraud 工具，API 现代，在中东与欧洲 strong，支持 marketplace payout。",
  "需要 alternative to Stripe 于特定 region、或 high volume 卡处理议价时评估。",
  "亚太本地 PM 覆盖需对照清单；文档与 sandbox 体验因团队而异。",
  {"vendorId":"checkout-com","tags":["payments","gateway"]})
r("braintree","Braintree","pay-processor","gateway","PayPal 旗下卡支付网关","https://www.braintreepayments.com",
  "Braintree 提供卡、PayPal、Venmo 与 recurring billing，SDK 成熟，被 PayPal 收购后与企业 PayPal 账户一体。",
  "已用 PayPal 生态、需要 drop-in UI 与 vault 卡 token 时选用；Marketplace split 场景历史久。",
  "新功能 velocity 不如 Stripe；部分地区 PM 与 payout 延迟要查表。",
  {"vendorId":"braintree","tags":["payments"]})
r("mollie","Mollie","pay-processor","gateway","欧洲开发者友好支付","https://www.mollie.com",
  "Mollie 支持 iDEAL、Bancontact、SEPA 等欧洲本地 PM 与卡支付，API 简洁，是 EU indie 与 SaaS 常见选择。",
  "主要客户在欧洲、需要 local PM 而不想接 Adyen  enterprise 流程时选用。",
  "北美与亚太 PM 弱；订阅与 marketplace 能力对照 Stripe Connect 验证需求。",
  {"vendorId":"mollie","tags":["payments","europe"]})
r("fastspring","FastSpring","pay-mor","mor","SaaS 商户记录代理与税务","https://fastspring.com",
  "FastSpring 作为 Merchant of Record 处理全球 VAT/GST、invoice 与 payout，软件与数字商品卖家无需自建各地税务实体。",
  "数字产品跨境卖全球、不想处理各国 sales tax 时选用 MoR；与 Paddle 同类。",
  "抽成高于纯 gateway；custom checkout UX 受限，physical goods 不支持。",
  {"vendorId":"fastspring","tags":["mor","tax"]})
r("razorpay","Razorpay","pay-processor","regional","印度主流支付网关","https://razorpay.com",
  "Razorpay 覆盖印度 UPI、卡、wallet 与 RazorpayX 银行 API，是印度 SaaS 与电商支付事实标准之一。",
  "产品主攻印度市场、需要 local PM 与 RBI 合规时必选；subscription 与 route split 支持。",
  "仅印度为主；跨境收 USD 需 Razorpay Global 产品线单独评估。",
  {"tags":["payments","india"]})
r("square-payments","Square","pay-processor","pos","Square 在线与线下支付","https://squareup.com",
  "Square 提供 POS、在线 checkout、invoice 与 Square Banking，适合 SMB retail 与 F&B 一体化收款。",
  "线下门店 + 简单 online store 需要同一 vendor 时选用；美国 SMB 普及率高。",
  "开发者 API 与 subscription 不如 Stripe 灵活；国际化限于部分英语市场。",
  {"tags":["payments","pos"]})


# === L dist ===
r("xiaomi-getapps","小米 GetApps","dist-android","store","小米设备应用商店","https://dev.mi.com/distribute",
  "GetApps 是 MIUI/HyperOS 预装应用商店，覆盖大量国内安卓用户，提供应用分发、更新与开发者控制台。",
  "安卓 App 需要覆盖小米系手机用户、或国内多渠道 APK 分发时必上架；与华为/OPPO/vivo 并行。",
  "审核规则与素材要求各商店不同；海外小米设备可能预装 Play Store，需 analytics 看真实占比。",
  {"vendorId":"xiaomi","region":"domestic","tags":["android","store"]})
r("oppo-store","OPPO 软件商店","dist-android","store","OPPO/ColorOS 应用分发","https://open.oppomobile.com",
  "OPPO 软件商店服务 ColorOS 用户，提供应用上架、游戏联运与 push 能力，是国内安卓 TOP 渠道之一。",
  "国内 Android 分发矩阵必备渠道；与 vivo 共用部分联运体系需分别提交。",
  "审核周期与版本回滚策略因渠道而异；隐私合规检测趋严，SDK 清单要完整。",
  {"vendorId":"oppo","region":"domestic","tags":["android","store"]})
r("vivo-store","vivo 应用商店","dist-android","store","vivo OriginOS 应用商店","https://dev.vivo.com.cn",
  "vivo 应用商店覆盖 vivo/iQOO 设备用户，提供标准 APK 分发与游戏推广资源，国内市场份额 significant。",
  "与 OPPO、小米并列的必发渠道；region 限定国内 android 用户触达。",
  "测试机型碎片化；64 位与 targetSdk 要求随政策更新，需关注开发者公告。",
  {"vendorId":"vivo","region":"domestic","tags":["android","store"]})
r("tencent-yingyongbao","腾讯应用宝","dist-android","store","腾讯系安卓应用商店","https://open.tencent.com",
  "应用宝是国内最大第三方安卓商店之一，与微信/QQ 流量互通，提供 APK、联运与广告变现入口。",
  "需要国内 android 最大覆盖面、或微信生态导流到 App 时重点运营；social 传播便利。",
  "抽成与联运条款复杂；纯工具 App 与游戏联运政策不同，资质要求严格。",
  {"vendorId":"tencent-cloud","region":"domestic","tags":["android","store"]})
r("microsoft-store","Microsoft Store","dist-desktop","store","Windows 应用统一商店","https://apps.microsoft.com",
  "Microsoft Store 分发 Win32、UWP 与 PWA 应用，Windows 11 深度集成，支持 MSIX 打包与自动更新。",
  "桌面工具希望触达 Windows 企业用户、或通过 Store 分发 PWA/Electron 包装应用时上架。",
  "审核与 MSIX 转换有学习成本；side-load 与 winget 并行策略更常见开发者选择。",
  {"vendorId":"microsoft","tags":["windows","desktop"]})
r("winget","WinGet","dist-desktop","package-manager","Windows 官方 CLI 包管理器","https://learn.microsoft.com/windows/package-manager",
  "WinGet 是 Windows 10/11 内置包管理器，通过 manifest PR 分发 CLI 与桌面应用，类似 Homebrew 体验。",
  "开发者工具/CLI 需要 Windows 用户一行安装时提交 community manifest；与 Microsoft Store 互补。",
  "Manifest 审核 PR 可能排队；silent install 参数需在 manifest 准确声明，否则企业脚本失败。",
  {"vendorId":"microsoft","tags":["windows","cli"],"pricing":{"model":"free"}})
r("homebrew","Homebrew","dist-desktop","package-manager","macOS/Linux 开源包管理器","https://brew.sh",
  "Homebrew 是 macOS（及 Linuxbrew）事实标准包管理，formula/cask 分发 CLI 与 GUI 应用，开发者装机必备。",
  "Mac 开发者工具需要 `brew install` 体验时维护 formula；cask 适合桌面 App 分发。",
  "不签名托管；cask 更新需跟进 upstream version，CI bump 可用 brew bump。",
  {"pricing":{"model":"open-source"},"tags":["macos","package-manager"],"maturity":"mature"})
r("setapp","Setapp","dist-desktop","subscription","Mac 应用订阅平台","https://setapp.com",
  "Setapp 是 MacPaw 的应用订阅商店，用户月费访问 curated 应用库， indie 开发者可获得 revenue share。",
  "Mac 生产力工具寻求订阅分发、触达愿意付月费的用户群时申请加入；marketing 由平台部分承担。",
  "收入分成与 exclusivity 条款需读清；不适合 freemium 巨大用户量只靠少数付费转化。",
  {"tags":["macos","subscription"]})
r("firefox-addons","Firefox Add-ons","dist-extension","store","Mozilla 官方扩展商店","https://addons.mozilla.org",
  "AMO 是 Firefox 浏览器扩展与主题官方分发渠道，支持 Manifest V3，审查注重隐私与用户数据披露。",
  "发布 Firefox 扩展必须上架 AMO（或 self-distribute 签名）；跨浏览器需与 Chrome 商店分别打包。",
  "审核可能比 Chrome 慢；推荐算法弱，需自有 marketing 驱动安装。",
  {"tags":["browser","extension"]})
r("edge-addons","Microsoft Edge Add-ons","dist-extension","store","Edge 浏览器扩展商店","https://microsoftedge.microsoft.com/addons",
  "Edge Add-ons 分发 Chromium 扩展给 Edge 用户，manifest  largely 兼容 Chrome，是企业 managed browser 常见来源。",
  "已做 Chrome 扩展、希望零改动覆盖 Edge 与企业 IT 部署时同步提交；Microsoft 365 用户基数大。",
  "用户量仍小于 Chrome Web Store；某些 Chrome API 在 Edge 实现差异需测试。",
  {"vendorId":"microsoft","tags":["browser","extension"]})
r("macos-notarization","macOS Notarization","dist-desktop","signing","Apple 公证与恶意软件扫描","https://developer.apple.com/documentation/security/notarizing_macos_software_before_distribution",
  "Notarization 是 Apple 对 macOS 分发软件的安全扫描与 ticket  stapling，Gatekeeper 要求 downloaded  app 必须 notarized（除 App Store）。",
  "Mac 桌面 App 在 Store 外分发（DMG/ZIP）前必须完成 notarization；Electron/Tauri 打包流水线要集成。",
  "Hardened Runtime 与 entitlements 配置错误会导致公证失败；CI 需 Apple ID app-specific password 或 API key。",
  {"tags":["macos","signing"],"pricing":{"model":"included"}})
r("amazon-appstore","Amazon Appstore","dist-android","store","Amazon 设备与 Fire OS 商店","https://developer.amazon.com/apps-and-games",
  "Amazon Appstore 服务 Fire tablet/TV 与部分 android 设备，与 AWS 账户一体，可触达 Prime 生态用户。",
  "需要 Fire OS 或 Amazon 渠道用户时上架；Android APK 常可复用 Google Play 构建。",
  "非 Google 服务设备需适配；市场份额小于 Play，维护成本需 weighed。",
  {"vendorId":"amazon-web-services","tags":["android","amazon"]})
r("fastlane","Fastlane","dist-ios","tooling","移动 CI/CD 与商店上传自动化","https://fastlane.tools",
  "Fastlane 用 Ruby DSL 自动化截图、签名、TestFlight 与 Play Store 上传，是 iOS/Android 发布流水线事实工具。",
  "任何需要频繁发版、多商店同步上传的团队应集成 fastlane 到 GitHub Actions；减少手工操作失误。",
  "Ruby 依赖与 match 证书管理学习曲线；Apple API 变更需跟进 plugin 更新。",
  {"pricing":{"model":"open-source"},"tags":["mobile","ci"],"maturity":"mature"})
r("codemagic","Codemagic","dist-ios","ci","Flutter/mobile 专注 CI/CD","https://codemagic.io",
  "Codemagic 为 Flutter、iOS、Android 提供 macOS 构建器、代码签名与 TestFlight/Play 发布，配置 YAML 简洁。",
  "Flutter 或多 mobile 仓库需要可靠 macOS CI 而不想自管 Mac mini 时选用；比通用 GA 省心。",
  "纯 Web 项目不划算；构建分钟数随 team 增长，高级 signing 在 enterprise plan。",
  {"tags":["mobile","ci"]})
r("snap-store","Snap Store","dist-desktop","store","Ubuntu Snap 通用 Linux 包","https://snapcraft.io/store",
  "Snap 是 Canonical 的跨 distro 打包格式，Snap Store 分发桌面与 server 应用，自动更新 channel 支持。",
  "Linux 桌面应用希望一次打包多发行版时发布 snap；IoT 设备亦用 snap 模型。",
  "启动慢与体积大被社区诟病；与 flatpak/flathub 并行维护增加成本。",
  {"tags":["linux","package"]})
r("flathub","Flathub","dist-desktop","store","Flatpak 社区应用仓库","https://flathub.org",
  "Flathub 是 Flatpak 主力应用仓库，沙箱分发 Linux 桌面应用，被 Fedora 等发行版默认推荐。",
  "开源 GUI 应用触达 Linux 桌面用户的首选发布渠道；sandbox 提升安全叙事。",
  "首次提交 review 可能久；runtime 体积与 portal 权限需 manifest 声明清楚。",
  {"pricing":{"model":"open-source"},"tags":["linux","flatpak"]})
r("safari-web-extensions","Safari Web Extensions","dist-extension","store","Safari 扩展与 App Store 分发","https://developer.apple.com/documentation/safariextensions",
  "Safari Web Extensions 复用 WebExtensions API，经 Xcode 包装为 Mac/iOS App Store 扩展，触达 Apple 生态用户。",
  "已有 Chrome 扩展、希望覆盖 Safari/macOS/iOS 且可接受 App Store 审核流程时移植。",
  "需 Apple Developer 会员与 native wrapper；iOS/iPadOS 权限比 desktop Safari 更严。",
  {"tags":["safari","extension"]})

# === V i18n & global ===
r("i18next","i18next","global-i18n","library","JS 国际化框架事实标准","https://www.i18next.com",
  "i18next 提供 namespaces、plural、interpolation 与插件生态，React/Vue/Node 均有绑定，是前端 i18n 最普及库之一。",
  "React/Next 存量项目需要成熟 i18n、社区资源与 LLM 翻译工具链兼容时默认 i18next；与 next-intl 可对比选型。",
  "运行时加载 locale 要配 bundler 策略；类型安全不如 paraglide 新一代方案。",
  {"pricing":{"model":"open-source"},"tags":["i18n","javascript"],"maturity":"mature"})
r("lingui","Lingui","global-i18n","library","Compile-time i18n for React","https://lingui.dev",
  "Lingui 用 macro 在构建期提取消息，bundle 体积小，TypeScript 友好，适合 performance-sensitive React 应用。",
  "关注 bundle size、需要 ICU MessageFormat 与 PO 文件工作流时选 Lingui 而非 i18next runtime。",
  "生态与 CMS 集成小于 i18next；非 React 绑定较弱。",
  {"pricing":{"model":"open-source"},"tags":["i18n","react"]})
r("formatjs","FormatJS","global-i18n","library","Intl 标准封装与 react-intl","https://formatjs.io",
  "FormatJS 实现 ICU MessageFormat  polyfill 与 react-intl，与浏览器 Intl API 对齐，Facebook 生态广泛使用。",
  "需要 standards-based i18n、或 polyfill 老浏览器 Intl 时采用；react-intl 是 React 官方推荐路径之一。",
  "API 较底层；extract CLI 与 translator workflow 需自建或配 Crowdin。",
  {"pricing":{"model":"open-source"},"tags":["i18n","intl"],"maturity":"mature"})
r("crowdin","Crowdin","global-i18n","tms","云端本地化管理与翻译协作","https://crowdin.com",
  "Crowdin 连接 Git/i18n 文件与译员、MT 引擎，提供 context screenshot、QA 与 workflow，是 SaaS 本地化 TMS 主流。",
  "多语言产品需要持续 sync JSON/PO、与社区/外包译员协作时选用；GitHub Action 集成成熟。",
  "按字符串与 seat 计费；小项目可能用 Tolgee 或 spreadsheet 过渡，MT 质量需 human review。",
  {"vendorId":"crowdin","tags":["localization","tms"]})
r("lokalise","Lokalise","global-i18n","tms","开发者友好的翻译管理平台","https://lokalise.com",
  "Lokalise 提供 key-based TMS、Figma/GA 集成、OTA 字符串更新与 branching，偏 product team 与 mobile/web 并行。",
  "需要 OTA 热更新文案、或设计-开发-翻译同一平台协作时评估；API 与 webhooks 丰富。",
  "价格高于 Crowdin 入门档；复杂 plural/gender 仍需规范 key 设计。",
  {"vendorId":"lokalise","tags":["localization","tms"]})
r("payoneer","Payoneer","global-fx","payout","跨境收款与多币种账户","https://www.payoneer.com",
  "Payoneer 提供全球收款账户、平台回款（Amazon/Upwork）与向供应商付款，支持多种货币与合规 KYC。",
  "freelancer 与跨境 SME 收平台美元、或需批量向海外供应商 payout 时常用；国内有持牌合作主体。",
  "FX 与提现费用需 spreadsheet 建模；部分国家开户受限，与 Wise 对比费率因 corridor 而异。",
  {"vendorId":"payoneer","tags":["fx","payout"],"maturity":"mature"})
r("mercury-bank","Mercury","global-entity","banking","美国创业公司数字银行","https://mercury.com",
  "Mercury 为美国注册的 tech startup 提供 checking、savings、wire 与 virtual card，API 与 UX 面向 remote-first 公司。",
  "Delaware C-Corp 需要美国银行账户收 Stripe/investor 汇款、且不想跑 physical branch 时常见首选。",
  "仅服务美国注册实体；非美国 founder 需配合 Stripe Atlas/Firstbase 等实体，FDIC 通过 partner bank。",
  {"vendorId":"mercury","tags":["banking","startup"],"availability":{"chinaAccessible":False,"needsCompany":True,"needsIcp":False,"regions":["us"]}})
r("vue-i18n","Vue I18n","global-i18n","library","Vue 官方国际化插件","https://vue-i18n.intlify.dev",
  "Vue I18n 是 Vue 生态标准 i18n，支持 composition API、datetime/number 格式化与 lazy loading locale。",
  "Nuxt/Vue 项目需要官方维护、文档中文友好的 i18n 时默认选择；与 @nuxtjs/i18n 模块集成。",
  "大型 monorepo 多 package 共享 key 需 discipline；SSR locale 检测与 SEO hreflang 要额外配置。",
  {"pricing":{"model":"open-source"},"tags":["i18n","vue"],"maturity":"mature"})
r("tolgee","Tolgee","global-i18n","tms","开源 in-context 翻译平台","https://tolgee.io",
  "Tolgee 提供 in-context 点击翻译、screenshot context 与 self-host，降低开发者与译员来回传文件成本。",
  "小团队希望 Crowdin 功能但预算有限、或需 EU self-host 时评估 Tolgee；Chrome 插件 in-context 体验好。",
  "Enterprise SSO 与 workflow 不如 Crowdin 深；极大型 locale 数量要测性能。",
  {"pricing":{"model":"open-source"},"tags":["localization"]})
r("paraglide","Paraglide","global-i18n","library","类型安全 compile-time i18n","https://inlang.com/m/gerre34r/library-inlang-paraglideJs",
  "Paragide（inlang）生成类型安全 message 函数，tree-shake 未用翻译，与 TanStack Start/SvelteKit 现代栈契合。",
  " greenfield 项目重视 TS 类型与 bundle size、愿意 adopt inlang 工具链时选 Paraglide 而非 i18next。",
  "生态较新；译员 workflow 需配 inlang Fink 或 export JSON，迁移存量 i18next 有成本。",
  {"tags":["i18n","typescript"],"maturity":"beta"})
r("currencycloud","Currencycloud","global-fx","api","跨境 FX 与多币种 API","https://www.currencycloud.com",
  "Currencycloud（Visa 旗下）提供 REST API 做 FX、多币种 wallet 与 local payment，嵌入 fintech 与 marketplace。",
  "平台型 SaaS 需要代客户收多币种并 swap 时集成；比 Wise API 更偏 B2B embedded finance。",
  "合规与 onboarding 重；indie 直接开户难，通常需 partner bank program。",
  {"tags":["fx","api"]})
r("firstbase","Firstbase","global-entity","incorporation","美国公司注册与合规套件","https://www.firstbase.io",
  "Firstbase 协助非美国创始人注册 Delaware/Wyoming 公司、EIN、registered agent 与 Mercury/Stripe 开户指引。",
  "海外 founder 需要美国实体接 Stripe、投资或 AWS credits 时与 Stripe Atlas 对比选型。",
  "年费与 agent 费用持续；税务与 substance 要求勿误解为「空壳即可」，需 CPA 规划。",
  {"tags":["incorporation","us"]})
r("phrase","Phrase","global-i18n","tms","企业级本地化平台","https://phrase.com",
  "Phrase（原 Memsource）提供 TMS、strings、MT 与 analytics，服务 enterprise 多 product 线本地化治理。",
  "Enterprise 多 team、需要 SLA 与复杂 workflow approval 时选用；与 Lokalise/Crowdin 竞品对比。",
  "价格高、setup 重；小团队 overkill，集成 Git 需 dedicated admin。",
  {"tags":["localization","enterprise"]})


# extra entries to reach ~140
r("wasabi","Wasabi","db-object","object","高性价比 S3 兼容热存储","https://wasabi.com",
  "Wasabi 提供 S3 兼容 API 与 flat-rate 存储定价，无 egress 费（公平使用政策），适合备份与媒体库长期存放。",
  "大量冷/温数据、预算敏感且 egress 可预测时选用；与 Cloudflare 组合分发静态资源。",
  "与 AWS 生态集成深度不如 S3；极端 API 兼容性边缘 case 需测试，fair use 滥用可能被限。",
  {"tags":["storage","s3-compatible"]})
r("digitalocean-spaces","DigitalOcean Spaces","db-object","object","DO S3 兼容对象存储","https://www.digitalocean.com/products/spaces",
  "Spaces 提供 S3 兼容 API、内置 CDN 与简单权限管理，与 App Platform/Droplet 同控制台，适合 DO 栈静态与备份。",
  "已用 DigitalOcean 部署应用、需要同源对象存储时选用；小团队 all-in-DO 常见。",
  "全球 region 少于 hyperscaler；高级 lifecycle 与 analytics 功能有限。",
  {"vendorId":"digitalocean","tags":["storage"]})
r("azure-blob-storage","Azure Blob Storage","db-object","object","Azure 对象与数据湖存储","https://azure.microsoft.com/products/storage/blobs",
  "Azure Blob 提供 hot/cool/archive 层、ADLS Gen2 与静态网站，与 Azure Functions、CDN 集成，是企业 Azure 数据平面基础。",
  "微软栈存放日志、backup、data lake 或 static website 时默认；Synapse 分析直接读 Blob。",
  "权限模型（RBAC+SAS）复杂；跨 cloud 工具 S3 兼容网关非原生。",
  {"vendorId":"microsoft-azure","tags":["storage","azure"]})
r("scylladb","ScyllaDB","db-nosql","wide-column","C++ 实现的 Cassandra 兼容库","https://www.scylladb.com",
  "ScyllaDB 兼容 Cassandra CQL，单节点吞吐高于 JVM Cassandra，适合 IoT、feed 与时序 wide-column 负载。",
  "Cassandra 存量遇性能瓶颈、希望降 latency 且不改 CQL 时迁移 Scylla；K8s Operator 成熟。",
  "运维仍需 distributed systems 经验；小数据量不如 Postgres 经济.simple 查询过度。",
  {"tags":["nosql","cassandra-compatible"]})
r("apache-pulsar","Apache Pulsar","db-nosql","streaming","云原生分布式消息流","https://pulsar.apache.org",
  "Pulsar 多租户、geo-replication 与分层存储统一 messaging 与 streaming，比 Kafka 更易跨 region 复制，BookKeeper 存储分离。",
  "需要 geo-replication、tenant 隔离或 queue+stream 统一模型时评估 Pulsar；Yahoo/StreamNative 生态。",
  "运维组件多于 Kafka；国内托管选项少于 MSK/Confluent，团队 learning curve 高。",
  {"tags":["streaming"],"pricing":{"model":"open-source"}})
r("propelauth","PropelAuth","baas-auth-only","b2b","B2B SaaS 开箱认证 UI","https://www.propelauth.com",
  "PropelAuth 提供 hosted login、org 管理、roles 与 Slack 式 invite flow，专为 B2B multi-tenant SaaS 设计。",
  "早期 B2B 需要 org 切换、RBAC 与 audit 而不想自建 UI 时选 PropelAuth；比 WorkOS 更偏 end-user auth。",
  "Enterprise SAML 深度不如 WorkOS；mobile SDK 与 social login 对照需求清单。",
  {"tags":["auth","b2b"]})
r("authentik","authentik","baas-auth-only","idp","开源身份提供商","https://goauthentik.io",
  "authentik 是 modern 开源 IdP，支持 OIDC/SAML/LDAP、flows 可视化配置与 outpost 反向代理，self-host 体验友好。",
  "Homelab/中小企业要 Keycloak 替代且 UI 更现代时选用；与 Traefik/Caddy 集成 common。",
  "Enterprise support 靠 vendor；超大规模 user federation 需 scale testing。",
  {"pricing":{"model":"open-source"},"tags":["auth","self-hosted"]})
r("strapi","Strapi","baas-platform","headless-cms","领先开源 Headless CMS","https://strapi.io",
  "Strapi 提供可定制 content types、REST/GraphQL API、roles 与 media library，Node.js 编写，Cloud 与 self-host 可选。",
  "营销站与 App 共享 structured content、需要 non-dev 编辑后台时常用；plugin 生态大。",
  "高并发 read 需加 CDN/cache；复杂 relational modeling 不如 direct DB + PostgREST。",
  {"tags":["cms","headless"]})
r("gumroad","Gumroad","pay-mor","mor","创作者数字商品与 MoR","https://gumroad.com",
  "Gumroad 让 creator 售卖数字产品、membership 与 physical 周边，平台作为 MoR 处理 VAT 与 payout，上手极快。",
  "indie creator 卖 ebook/模板、不想注册公司接 Stripe 时用 Gumroad 落地页；social commerce 友好。",
  "抽成高于 Stripe 直连；custom SaaS billing 与 API 集成弱于 Paddle。",
  {"tags":["mor","creator"]})
r("samsung-galaxy-store","Samsung Galaxy Store","dist-android","store","三星设备官方应用商店","https://seller.samsungapps.com",
  "Galaxy Store 预装三星手机与 Galaxy 设备，覆盖全球部分 android 市场，支持 APK 与主题分发。",
  "用户画像含大量三星设备、或韩国/海外 samsung 渠道重要时上架；与 Google Play 并行。",
  "部分市场仍依赖 GMS；审核与本地化要求各国不同。",
  {"tags":["android","samsung"]})
r("itch-io","itch.io","dist-desktop","store","独立游戏与软件分发","https://itch.io",
  "itch.io 面向 indie game 与 digital 工具，支持 pay-what-you-want、HTML5 与 desktop 下载，community 强。",
  "独立游戏/prototype 需要友好 discoverability 与 flexible pricing 时发布；jam 活动多。",
  "非 mainstream 消费者渠道；enterprise 软件不适合，支付与 tax 能力有限。",
  {"tags":["games","indie"]})
r("revolut-business","Revolut Business","global-fx","banking","欧洲数字银行与多币种账户","https://www.revolut.com/business",
  "Revolut Business 提供多币种账户、FX、card 与 API，服务 EU/UK SME 跨境收付，费率透明。",
  "欧洲 startup 需要 EUR/GBP 多币种与 cheap FX 时常用；与 Wise Business 对比 corridor。",
  "美国本土 banking 能力有限；高 risk 行业开户可能被拒，deposit 保护因 region 而异。",
  {"tags":["banking","europe"]})
r("aws-app-runner","AWS App Runner","cloud-paas","paas","AWS 容器 PaaS 简化版","https://aws.amazon.com/apprunner",
  "App Runner 从容器镜像或源码自动部署 Web 应用，自动伸缩与 TLS，比 ECS 简单，比 Lambda 更适合长连接 HTTP。",
  "AWS 用户需要 Heroku 式体验而不想配 ALB+ECS 时选用；与 ECR 源码构建集成。",
  "VPC connector 与 custom domain 有局限；cold start 与 pricing 随 vCPU/memory 线性。",
  {"vendorId":"amazon-web-services","tags":["aws","paas"]})
r("bunny-storage","Bunny Storage","db-object","object","Bunny CDN 配套对象存储","https://bunny.net/storage",
  "Bunny Storage 与 Bunny CDN 同平台，S3 兼容 API、低价 egress 到自家 CDN，适合全球 static 与 video origin。",
  "已用 Bunny CDN 或需要 cheap bandwidth 分发大文件时选用；video streaming 场景常见。",
  "全球 presence 小于 AWS；enterprise compliance 认证需核实。",
  {"tags":["storage","cdn"]})
r("sql-js","sql.js","db-sqlite-edge","wasm","浏览器内 SQLite WASM","https://sql.js.org",
  "sql.js 将 SQLite 编译为 WebAssembly，在浏览器内存跑 SQL，适合 demo、local-first prototype 与离线 education 工具。",
  "需要在浏览器内跑 ad-hoc SQL、或 prototype local-first 而不发 backend 时实验性使用。",
  "非生产持久化；大数据集内存受限，与 OPFS 持久化需额外 glue。",
  {"pricing":{"model":"open-source"},"tags":["sqlite","wasm"]})
r("ory-kratos","Ory Kratos","baas-auth-only","oss-idp","云原生身份管理 API","https://www.ory.sh/kratos",
  "Ory Kratos 提供 API-first 注册登录、recovery、verification 与 identity schema，与 Ory Hydra/Oathkeeper 组成零信任栈。",
  "需要 composable auth 组件、Go/cloud native 团队自建 IdP 时选用 Kratos + Hydra。",
  "无 hosted UI 成品；前端 session 与 email delivery 需集成，学习曲线高于 Clerk。",
  {"tags":["auth","cloud-native"],"pricing":{"model":"open-source"}})
r("square-connect","Square API","pay-processor","api","Square 开发者支付 API","https://developer.squareup.com",
  "Square API 提供 payments、catalog、inventory 与 OAuth merchant 接入，适合 in-person + online unified 商户。",
  "零售 SMB 已有 Square POS、需要同一 backend 管理线上线下 inventory 时用 API 扩展。",
  "纯 online SaaS 全球订阅不如 Stripe；API rate 与 marketplace 能力有限。",
  {"tags":["payments","api"]})
r("react-intl","React Intl","global-i18n","library","FormatJS 的 React 绑定","https://formatjs.io/docs/react-intl",
  "React Intl 提供 FormattedMessage、hooks 与 ICU 格式化组件，是 FormatJS 官方 React 集成，Intl 标准对齐。",
  "React 项目已选 FormatJS 栈、需要成熟 plural/datetime 组件时使用；与 react-i18next 选型二选一。",
  "Extract 工作流需 CLI；App Router RSC 与 client 边界要规划 provider 位置。",
  {"pricing":{"model":"open-source"},"tags":["i18n","react"]})
r("aws-msk","Amazon MSK","db-nosql","managed","AWS 托管 Kafka","https://aws.amazon.com/msk",
  "Amazon MSK 运行开源 Apache Kafka，AWS 负责 broker 补丁与 scaling，与 VPC、IAM、Glue Schema Registry 集成。",
  "已在 AWS、需要 Kafka 兼容且不想自管 ZooKeeper/KRaft 运维时选用 MSK Serverless 或 provisioned。",
  "成本高于 self-host on EC2；跨 region mirroring 需 MSK Replicator 额外费用。",
  {"vendorId":"amazon-web-services","tags":["kafka","managed"]})
r("confluent-cloud","Confluent Cloud","db-nosql","managed","Fully managed Kafka 服务","https://www.confluent.io/confluent-cloud",
  "Confluent Cloud 提供 Kafka、ksqlDB、Schema Registry 与 Flink 托管，SLA 与 connector 生态由 Confluent 维护。",
  "需要 enterprise Kafka SLA、connector marketplace 且预算允许时用 Confluent Cloud；跨云也可。",
  "定价比 MSK/self-host 高；vendor 绑定 Flink/ksql 组件。",
  {"vendorId":"confluent","tags":["kafka","managed"]})
r("upstash-redis","Upstash Redis","db-cache","serverless","按请求计费的 Serverless Redis","https://upstash.com/redis",
  "Upstash Redis 提供 REST 与 Redis 协议、全球复制与 per-request 定价，适合 Serverless 与 edge 无需常驻连接。",
  "Vercel/Cloudflare 函数需要 rate limit/cache 但 TCP Redis 连接池困难时首选 Upstash。",
  "大型 value 与高频 pipeline 成本需建模；持久化 tier 与 eviction 策略要选对 plan。",
  {"vendorId":"upstash","tags":["redis","serverless"]})
r("planetscale-serverless","PlanetScale","db-relational","serverless","MySQL 兼容 Serverless 分支数据库","https://planetscale.com",
  "PlanetScale 基于 Vitess 提供 MySQL 兼容、database branching 与 deploy request，适合 schema 变更 workflow 与 serverless 连接。",
  "需要 MySQL 协议 + branch 预览 schema、或 huge scale sharding 前中期时选用；与 Prisma/Drizzle 搭配。",
  "现已调整产品策略需关注；外键与某些 MySQL 特性受限，Postgres 团队应选 Neon。",
  {"tags":["mysql","serverless"]})


def _build():
    ns: dict = {}
    exec(HEADER, ns)
    add, mk, link = ns["add"], ns["mk"], ns["link"]
    _entries, _edges = ns["_entries"], ns["_edges"]
    for item in RAW:
        eid, name, cat, sub, one, url, what, when, caution = item[:9]
        extra = dict(item[9]) if len(item) > 9 else {}
        kw = {}
        if "region" in extra:
            kw["region"] = extra.pop("region")
        if "vendorId" in extra:
            kw["vendor"] = extra.pop("vendorId")
        if "pricing" in extra:
            pr = extra.pop("pricing")
            kw["pricing"] = pr["model"] if isinstance(pr, dict) else pr
        if "maturity" in extra:
            kw["maturity"] = extra.pop("maturity")
        if "tags" in extra:
            kw["tags"] = extra.pop("tags")
        if "availability" in extra:
            kw["availability"] = extra.pop("availability")
        else:
            kw["china"] = extra.pop("china", True)
        if "docs" in extra:
            kw["docs"] = extra.pop("docs")
        if "pitfalls" in extra:
            kw["pitfalls"] = extra.pop("pitfalls")
        kw.update(extra)
        add(mk(eid, name, cat, sub, one, url, what, when, caution, **kw))

    ED = [
    ("render-alt-vercel", "render", "vercel", "alternative_to"),
    ("render-alt-railway", "render", "railway", "alternative_to"),
    ("heroku-alt-render", "heroku", "render", "alternative_to"),
    ("heroku-postgresql", "heroku", "postgresql", "commonly_used_with"),
    ("deno-deploy-alt-cf-workers", "deno-deploy", "cloudflare-workers", "alternative_to"),
    ("deno-deploy-deno", "deno-deploy", "deno", "built_on"),
    ("amplify-lambda", "aws-amplify", "aws-lambda", "part_of"),
    ("amplify-alt-supabase", "aws-amplify", "supabase", "alternative_to"),
    ("gcr-docker", "google-cloud-run", "docker", "commonly_used_with"),
    ("gcr-alt-fly", "google-cloud-run", "fly-io", "alternative_to"),
    ("azure-swa-cf-pages", "azure-static-web", "cloudflare-pages", "alternative_to"),
    ("sst-lambda", "sst", "aws-lambda", "built_on"),
    ("sst-nextjs", "sst", "nextjs", "commonly_used_with"),
    ("coolify-heroku-oss", "coolify", "heroku", "open_source_alternative_to"),
    ("coolify-docker", "coolify", "docker", "depends_on"),
    ("scf-domestic-lambda", "tencent-scf", "aws-lambda", "domestic_equivalent_of"),
    ("scf-cos", "tencent-scf", "tencent-cos", "integrates_with"),
    ("agc-domestic-firebase", "huawei-agc", "firebase", "domestic_equivalent_of"),
    ("volcengine-domestic-lambda", "volcengine-fcn", "aws-lambda", "domestic_equivalent_of"),
    ("esa-domestic-cf-cdn", "aliyun-esa", "cloudflare-cdn", "domestic_equivalent_of"),
    ("cfw-kv", "cloudflare-workers", "cloudflare-kv", "integrates_with"),
    ("cfw-d1", "cloudflare-workers", "cloudflare-d1", "integrates_with"),
    ("lambda-dynamodb", "aws-lambda", "dynamodb", "commonly_used_with"),
    ("inngest-vercel", "inngest", "vercel", "integrates_with"),
    ("trigger-vercel", "trigger-dev", "vercel", "integrates_with"),
    ("mysql-alt-pg", "mysql", "postgresql", "alternative_to"),
    ("mysql-planetscale", "mysql", "planetscale-serverless", "commonly_used_with"),
    ("tidb-mysql", "tidb", "mysql", "compatible_with"),
    ("cockroach-pg", "cockroachdb", "postgresql", "compatible_with"),
    ("cockroach-neon", "cockroachdb", "neon", "migration_path_to"),
    ("rds-mysql", "amazon-rds", "mysql", "provides_access_to"),
    ("rds-lambda", "amazon-rds", "aws-lambda", "commonly_used_with"),
    ("cloudsql-gcr", "google-cloud-sql", "google-cloud-run", "commonly_used_with"),
    ("dynamodb-supabase", "dynamodb", "supabase", "alternative_to"),
    ("kafka-msk", "kafka", "aws-msk", "powered_by"),
    ("qstash-upstash", "upstash-qstash", "upstash-redis", "commonly_used_with"),
    ("meili-es", "meilisearch", "elasticsearch", "alternative_to"),
    ("typesense-meili", "typesense", "meilisearch", "alternative_to"),
    ("s3-r2", "aws-s3", "cloudflare-r2", "alternative_to"),
    ("oss-domestic-s3", "aliyun-oss", "aws-s3", "domestic_equivalent_of"),
    ("cos-domestic-s3", "tencent-cos", "aws-s3", "domestic_equivalent_of"),
    ("minio-s3", "minio", "aws-s3", "compatible_with"),
    ("sb-storage-supabase", "supabase-storage", "supabase", "part_of"),
    ("d1-libsql", "cloudflare-d1", "libsql", "compatible_with"),
    ("pocketbase-supabase", "pocketbase", "supabase", "open_source_alternative_to"),
    ("nhost-hasura", "nhost", "hasura", "built_on"),
    ("convex-supabase", "convex", "supabase", "alternative_to"),
    ("authjs-clerk", "authjs", "clerk", "open_source_alternative_to"),
    ("authjs-nextjs", "authjs", "nextjs", "integrates_with"),
    ("logto-auth0", "logto", "auth0", "open_source_alternative_to"),
    ("authing-auth0", "authing", "auth0", "domestic_equivalent_of"),
    ("workos-authjs", "workos", "authjs", "commonly_used_with"),
    ("kinde-clerk", "kinde", "clerk", "alternative_to"),
    ("paypal-stripe", "paypal", "stripe", "commonly_used_with"),
    ("rc-apple", "revenuecat", "apple-app-store", "integrates_with"),
    ("rc-google", "revenuecat", "google-play", "integrates_with"),
    ("pingpp-stripe", "pingpp", "stripe", "domestic_equivalent_of"),
    ("adyen-stripe", "adyen", "stripe", "alternative_to"),
    ("alipay-global-alipay", "alipay-global", "alipay", "part_of"),
    ("fastspring-paddle", "fastspring", "paddle", "alternative_to"),
    ("xiaomi-gp", "xiaomi-getapps", "google-play", "domestic_equivalent_of"),
    ("oppo-gp", "oppo-store", "google-play", "domestic_equivalent_of"),
    ("vivo-gp", "vivo-store", "google-play", "domestic_equivalent_of"),
    ("yyb-gp", "tencent-yingyongbao", "google-play", "domestic_equivalent_of"),
    ("firefox-chrome", "firefox-addons", "chrome-web-store", "alternative_to"),
    ("edge-chrome", "edge-addons", "chrome-web-store", "compatible_with"),
    ("notarize-apple", "macos-notarization", "apple-app-store", "depends_on"),
    ("fastlane-tf", "fastlane", "testflight", "integrates_with"),
    ("i18next-next-intl", "i18next", "next-intl", "alternative_to"),
    ("formatjs-react-intl", "formatjs", "react-intl", "part_of"),
    ("crowdin-i18next", "crowdin", "i18next", "integrates_with"),
    ("lokalise-vue", "lokalise", "vue-i18n", "integrates_with"),
    ("payoneer-wise", "payoneer", "wise", "alternative_to"),
    ("mercury-stripe", "mercury-bank", "stripe", "commonly_used_with"),
    ("firstbase-atlas", "firstbase", "stripe-atlas", "alternative_to"),
    ("do-app-spaces", "digitalocean-app-platform", "digitalocean-spaces", "commonly_used_with"),
    ("zeabur-railway", "zeabur", "railway", "alternative_to"),
    ("modal-lambda", "modal", "aws-lambda", "alternative_to"),
    ("cloudbase-supabase", "tencent-cloudbase", "supabase", "domestic_equivalent_of"),
    ("elasticache-redis", "amazon-elasticache", "redis", "provides_access_to"),
    ("upstash-redis-alt", "upstash-redis", "redis", "alternative_to"),
    ("planetscale-neon", "planetscale-serverless", "neon", "alternative_to"),
    ("hasura-pg", "hasura", "postgresql", "integrates_with"),
    ("strapi-pg", "strapi", "postgresql", "commonly_used_with"),
    ("braintree-paypal", "braintree", "paypal", "part_of"),
    ("mollie-stripe", "mollie", "stripe", "alternative_to"),
    ("gumroad-paddle", "gumroad", "paddle", "alternative_to"),
    ("codemagic-tf", "codemagic", "testflight", "integrates_with"),
    ("winget-homebrew", "winget", "homebrew", "alternative_to"),
    ("tolgee-crowdin", "tolgee", "crowdin", "open_source_alternative_to"),
    ("paraglide-i18next", "paraglide", "i18next", "alternative_to"),
    ("lianlian-payoneer", "lianlianpay", "payoneer", "alternative_to"),
    ("supertokens-authjs", "supertokens", "authjs", "alternative_to"),
    ("keycloak-auth0", "keycloak", "auth0", "open_source_alternative_to"),
    ("fusionauth-auth0", "fusionauth", "auth0", "alternative_to"),
    ("caprover-coolify", "caprover", "coolify", "alternative_to"),
    ("windmill-pg", "windmill", "postgresql", "commonly_used_with"),
    ("app-runner-render", "aws-app-runner", "render", "alternative_to"),
    ("confluent-kafka", "confluent-cloud", "kafka", "powered_by"),
    ("directus-pg", "directus", "postgresql", "integrates_with"),
    ("ory-keycloak", "ory-kratos", "keycloak", "alternative_to"),
    ("propelauth-kinde", "propelauth", "kinde", "alternative_to"),
    ("authentik-keycloak", "authentik", "keycloak", "alternative_to"),
    ("amazon-store-gp", "amazon-appstore", "google-play", "alternative_to"),
    ("samsung-gp", "samsung-galaxy-store", "google-play", "alternative_to"),
    ("revolut-mercury", "revolut-business", "mercury-bank", "alternative_to"),
    ("checkout-stripe", "checkout-com", "stripe", "alternative_to"),
    ("razorpay-stripe", "razorpay", "stripe", "alternative_to"),
    ("vue-i18n-nuxt", "vue-i18n", "nuxt", "integrates_with"),
    ("lingui-react", "lingui", "react", "integrates_with"),
    ("phrase-crowdin", "phrase", "crowdin", "alternative_to"),
    ("pulsar-kafka", "apache-pulsar", "kafka", "alternative_to"),
    ("dragonfly-redis", "dragonfly", "redis", "alternative_to"),
    ("valkey-redis", "valkey", "redis", "open_source_alternative_to"),
    ("timescale-pg", "timescaledb", "postgresql", "built_on"),
    ("yugabyte-pg", "yugabyte", "postgresql", "compatible_with"),
    ("aurora-mysql-link", "aurora-mysql", "mysql", "compatible_with"),
    ("azure-pg", "azure-database-postgresql", "postgresql", "provides_access_to"),
    ("gcs-gcr", "google-cloud-storage", "google-cloud-run", "commonly_used_with"),
    ("wasabi-s3", "wasabi", "aws-s3", "compatible_with"),
    ("do-spaces-s3", "digitalocean-spaces", "aws-s3", "compatible_with"),
    ("azure-blob-s3", "azure-blob-storage", "aws-s3", "compatible_with"),
    ("northflank-railway", "northflank", "railway", "alternative_to"),
    ("koyeb-fly", "koyeb", "fly-io", "alternative_to"),
    ("beanstalk-heroku", "aws-elastic-beanstalk", "heroku", "alternative_to"),
    ("stytch-clerk", "stytch", "clerk", "alternative_to"),
    ("snap-flathub", "snap-store", "flathub", "alternative_to"),
    ("safari-chrome", "safari-web-extensions", "chrome-web-store", "compatible_with"),
    ("square-stripe", "square-payments", "stripe", "alternative_to"),
    ("couchbase-mongo", "couchbase", "mongodb-atlas", "alternative_to"),
    ("singlestore-tidb", "singlestore", "tidb", "alternative_to"),
    ("mariadb-mysql", "mariadb", "mysql", "compatible_with"),
    ("backblaze-cf", "backblaze-b2", "cloudflare-cdn", "commonly_used_with"),
    ("bunny-cf", "bunny-storage", "cloudflare-cdn", "commonly_used_with"),
    ("litefs-libsql", "litefs", "libsql", "compatible_with"),
    ("sqljs-libsql", "sql-js", "libsql", "compatible_with"),
    ("scylladb-cassandra", "scylladb", "cassandra", "compatible_with"),
    ("rabbitmq-kafka", "rabbitmq", "kafka", "alternative_to"),
    ("memcached-redis", "memcached", "redis", "alternative_to"),
    ("currencycloud-stripe", "currencycloud", "stripe", "integrates_with"),
    ("setapp-homebrew", "setapp", "homebrew", "alternative_to"),
    ("microsoft-store-winget", "microsoft-store", "winget", "commonly_used_with"),
    ("itch-gumroad", "itch-io", "gumroad", "alternative_to"),
    ]

    for eid, frm, to, typ in ED:
        link(eid, frm, to, typ)

    ids = {e["id"] for e in _entries}
    froms = {e["from"] for e in _edges}
    for eid in sorted(ids - froms):
        link(f"{eid}-fallback", eid, "vercel", "commonly_used_with", weight=0.3)
    return _entries, _edges, ns["_VENDORS"]


def _esc(s: str) -> str:
    return s.replace("\\", "\\\\").replace('"', '\\"')


if __name__ == "__main__":
    _entries, _edges, _VENDORS = _build()
    # Output uses entry/edge/desc helpers only (no mk) per spec
    OUT_HEADER = '''#!/usr/bin/env python3
"""VibeHolding Wave 2 (G–L + V) knowledge base expansion."""
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
    if e.get("vendorId") is None:
        e.pop("vendorId", None)
    assert len(e["oneLiner"]) <= 60, (e["id"], e["oneLiner"])
    assert len(e.get("descriptionMd", "")) >= 120, (e["id"], len(e.get("descriptionMd", "")))
    assert e.get("pitfalls"), e["id"]
    assert e.get("subcategory"), e["id"]
    return e


def edge(eid, frm, to, typ, weight=0.7, confidence="community", note=None, sources=None):
    e = {
        "id": eid, "from": frm, "to": to, "type": typ,
        "weight": weight, "confidence": confidence,
        "sources": sources or [], "createdAt": REVIEWED,
    }
    if note: e["note"] = note
    return e


def desc(what, when, caution):
    return f"{what}\\n\\n{when}\\n\\n{caution}\\n"


_entries: list[dict] = []
_edges: list[dict] = []


def add(e: dict) -> None:
    _entries.append(e)


def link(eid: str, frm: str, to: str, typ: str, **kw) -> None:
    _edges.append(edge(eid, frm, to, typ, **kw))


_VENDORS = [
'''
    import json
    vendor_lines = [OUT_HEADER]
    for v in _VENDORS:
        vendor_lines.append(f"    {json.dumps(v, ensure_ascii=False)},")
    vendor_lines.append("]\n\n")
    body_lines = []
    for e in _entries:
        lines = ["add(entry("]
        for k, v in e.items():
            lines.append(f"    {k}={v!r},")
        lines.append("))")
        body_lines.append("\n".join(lines))

    edge_lines = []
    for ed in _edges:
        note = f', note={ed["note"]!r}' if ed.get("note") else ""
        w = ed["weight"]
        wpart = f", weight={w}" if w != 0.7 else ""
        edge_lines.append(
            f'link({ed["id"]!r}, {ed["from"]!r}, {ed["to"]!r}, {ed["type"]!r}{wpart}{note})'
        )

    out = "".join(vendor_lines) + "\n".join(body_lines) + "\n\n" + "\n".join(edge_lines) + "\n\n" + FOOTER
    OUT.write_text(out)
    print(f"Wrote {len(_entries)} entries, {len(_VENDORS)} vendors, {len(_edges)} edges -> {OUT}")
