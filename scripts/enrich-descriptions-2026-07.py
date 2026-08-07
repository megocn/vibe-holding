#!/usr/bin/env python3
"""加厚条目 descriptionMd：选型向说明，不重复 oneLiner，不写 Schema 字段名。

幂等：以本文件 DESCRIPTIONS 为准写回 JSON；内容已与 2026-07-23 加厚结果对齐。
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ENTRIES = ROOT / "content" / "entries"

# 目标：约 120–350 字；说清「是什么 / 何时选 / 注意什么」；LLM 族/档保持粒度约定。
DESCRIPTIONS: dict[str, str] = {
    "aider": "基于 Git 工作区的**终端结对编程**工具：把 diff、提交与对话绑在一起，适合习惯 CLI、希望改动可审计的开发者。\n\n相对 IDE Agent，Aider 更「仓库感知、提交驱动」——适合在已有仓库上做可控增量，而不是从零搭原型。可接多家模型；本地/远程仓库权限与密钥暴露面需自行约束。\n\n适合「小步提交」纪律好的仓库；大爆炸式重构仍建议拆任务并人工审 diff。",
    "airwallex": "空中云汇提供多币种全球账户、收款与虚拟卡，适合需要**多平台结汇、多主体资金归集**的团队（应用商店、广告、跨境电商等）。\n\n大陆主体出海时，常与万里汇并列评估：比 MoR（Paddle/Polar）更偏「账户层」能力。注意各场景开户材料、费率与风控策略差异，大额/新行业审核可能较严。\n\n虚拟卡与多币种账户能简化广告/云账单；开户与年费按主体地区核算。",
    "alipay": "支付宝是国内综合支付与商家服务的主渠道之一，覆盖网页、APP、小程序与当面付等场景。\n\n做国内 C 端变现时，通常与微信支付并列接入；企业主体、签约产品与分账能力决定复杂度。纯出海收款一般不会以支付宝为主路径。\n\n签约产品（电脑网站/手机网站/小程序）决定接入形态；分账与会员需额外能力。",
    "aliyun-fc": "阿里云函数计算是国内主流的**事件驱动 Serverless**：按调用计费，适合国内合规、低延迟、与阿里云生态（OSS、API 网关、消息）联动的后端。\n\n对标国外的 Vercel/Cloudflare Workers 时，优势在国内网络与备案友好；DX 与边缘生态相对分散。注意冷启动、并发配额与厂商锁定。\n\n事件源绑定（OSS/定时/HTTP）是核心用法；冷启动敏感路径考虑预留实例。",
    "aliyun-wanwang": "万网（阿里云域名）是国内域名注册与续费的常见入口，并与**备案、解析、证书**流程深度绑定。\n\n若站点面向中国大陆用户且需要 ICP 备案，域名常落在阿里云/腾讯云等国内注册商。出海纯 Cloudflare 栈可不必强绑万网，但双市场产品往往仍要备国内域名链路。\n\n域名过户与备案主体一致最省事；出海品牌域名也可分开注册商管理。",
    "antd": "Ant Design 是蚂蚁开源的企业级 React 组件库，中文文档、设计语言与国内中后台生态极为成熟。\n\n适合管理后台、B 端表单与「开箱即用」的视觉一致性；相对 Radix/shadcn 路线，定制成本与包体叙事不同。不要与图标集或无样式原语同榜硬比。\n\n中后台表单/表格效率高；营销落地页或高度品牌化产品可能觉得「太后台」。",
    "apple-app-store": "Apple App Store 是 iOS/macOS 应用的主分发渠道，伴随开发者账号、审核、隐私清单与抽成规则。\n\nIndie 上架前应用 TestFlight 做灰度；国内用户可达性好，但收款与税务需按主体规划。桌面端若走直接分发，可并列评估 GitHub Releases + 公证。\n\n审核拒绝常见于权限说明与元数据；隐私营养标签与账号删除入口是近年高频项。",
    "appwrite": "Appwrite 是可自托管的开源 BaaS：Auth、数据库、存储与函数一体，云托管与私有部署可选。\n\n适合希望「Firebase 式能力」但不想完全锁云厂商、或有数据驻留要求的团队。相对 Supabase（Postgres 叙事），Appwrite 更偏自研文档库与全套 API；选型时看团队是否吃开源运维成本。\n\n自托管要规划备份与升级窗口；功能面广，按模块启用避免一次铺太开。",
    "auth0": "Auth0（Okta）是成熟的企业级 IDaaS：协议覆盖广、合规叙事强，适合 B2B、复杂组织与审计要求高的场景。\n\n相对 Clerk/Better Auth，价格与配置复杂度通常更高；Indie 早期往往过重。若已有 Okta 企业合同或强合规需求，Auth0 仍是稳妥选项。\n\n企业 SSO/SAML 是强项；Indie 早期用它容易为用不到的能力付费。",
    "axiom": "Axiom 面向开发者的日志与高基数事件查询，对 Serverless/边缘场景友好，查询体验偏「分析型」而非传统日志检索。\n\n适合事件量大、维度多的产品与边缘函数可观测。与 Sentry（错误）/OpenTelemetry（标准采集）互补；注意定价随事件量上涨。\n\n查询语言与仪表盘适合事件分析；与日志长期归档策略一起设计，避免只当「临时尾巴」。",
    "azure-openai": "在 Azure 上托管 OpenAI 模型，强调企业合同、区域合规、私网与配额治理，而不是 C 端 ChatGPT 体验。\n\n国内直连常不可用或需企业通道；选型动机多为合规与采购，而非纯价格。应用侧仍建议经网关（OpenRouter/自建）抽象模型供应商。\n\n区域配额与内容过滤策略按订阅配置；应用层仍做重试与模型降级。",
    "better-auth": "Better Auth 是 TypeScript 优先的开源鉴权框架：Email/OAuth/组织/2FA 等能力齐全，框架无关、可自托管。\n\nIndie starter 高频选项：相对 Clerk 少锁仓、相对手写 NextAuth 更完整。代价是自己运维会话存储与安全基线；适合已有 Postgres/自建后端的团队。\n\n插件式扩展账号能力；会话存储与 CSRF/cookie 设置按部署域名仔细核对。",
    "biome": "Biome 用 Rust 实现统一的 lint + format，目标是替代「ESLint + Prettier」组合，换更快反馈与更简单配置。\n\n适合新项目或愿意收敛工具链的 TS/JS 仓；存量超大 ESLint 规则集迁移需评估。与 pnpm/Vite 等同属现代前端工具链常见拼图。\n\n规则集相对 ESLint 插件世界更收敛；迁入时先在 CI 开 warn 再变 error。",
    "bolt-new": "Bolt.new（StackBlitz）是浏览器内的**全栈原型**工具：WebContainers 带来接近本机的 Node 体验，偏营销页与快速演示。\n\n属 Vibe Coding 的 Flavor B（云端 Builder）：出活快，但部署与运行时仍偏平台。触及真实用户/支付/生产凭据前，应规划「毕业」到可移植仓库。\n\n演示与获客页很快；数据库与鉴权一旦绑死平台，毕业要排期，不要拖到有收入。",
    "bun": "Bun 是高速 all-in-one JS 运行时：兼容 Node API，并内置打包、测试与包管理，强调 DX 与启动速度。\n\n适合新服务、脚本与工具链实验；生产关键路径需确认兼容性与运维成熟度。与 Node/Deno 并列评估，而不是「再学一门语言」。\n\n测试与打包内置省工具链；生产关键服务上线前用真实流量打兼容性。",
    "chrome-web-store": "Chrome Web Store 是 Chromium 扩展的主分发渠道；Manifest V3、权限最小化与审核策略是硬约束。\n\n扩展产品常与官网/桌面端并列分发。国内访问与企业策略可能影响安装转化；若只服务自家站点，也可评估不经过商店的加载方式（受限）。\n\n权限申请文案影响通过率；MV3 service worker 生命周期要按扩展模式重写假设。",
    "claude-code": "Claude Code 是 Anthropic 官方的**终端编程 Agent**：在仓库上下文中多文件改动、跑命令、理解项目结构。\n\n在本机/终端跑仓库级任务：可控、贴近真实 Git 工作流，但受本机额度、网络与并行能力限制。国内直连常不稳定，需企业通道或兼容网关。\n\n仓库级任务强；与 IDE 内联编辑可组合，按「终端编排 + 编辑器微调」分工。",
    "claude-opus": "Anthropic Claude 产品族中的**旗舰选型档**。当前版本以 Opus 4.8 为代表，偏复杂推理、长链路 Agent 与高质量编码协作。\n\n应与其他族的旗舰档（如 Kimi 旗舰、Qwen-Max、GPT 旗舰）对比，而不是与「通义千问产品族」等上层节点同列。定价按量，适合高价值任务而非全文检索式滥调用。\n\n贵但稳的复杂任务档；批量便宜活应降级到同族中低档，避免旗舰打杂。",
    "claude": "Claude 是 Anthropic 的大模型**产品族**。族下再分 Opus / Sonnet / Haiku 等**选型档位**；具体版本（如 Opus 4.8）写在对应档位条目上。\n\n选型时先定「用哪家」再定「哪一档」；不要把产品族与其他家的旗舰档、或某次版本发布名直接同列对比。\n\nAnthropic 系工具链（含 Claude Code）协同好；采购与区域可用性是落地前提。",
    "clerk": "Clerk 提供开箱即用的登录 UI、用户与组织/多租户能力，对 Next.js 等前端栈非常友好。\n\n适合要快速上线 Auth 的 SaaS；代价是厂商锁定与按 MAU 计费。数据驻留、中国区可用性与退出成本应在早期评估；开源替代常见 Better Auth / Supabase Auth。\n\n组织/成员邀请流程省心；中国区延迟与合规若敏感，预留 Better Auth 退出方案。",
    "cloudflare-cdn": "Cloudflare 把 DNS、CDN、WAF 与 Workers 边缘计算收成一体网络，是 Indie「零成本出海」高频底座。\n\n适合全球静态/边缘加速与基础安全；国内访问与备案场景需另备国内 CDN/域名策略。与 Pages/R2/Workers 组合可搭轻量全栈，注意厂商能力边界与企业套餐差异。\n\nDNS 切过去前先降低 TTL；WAF 规则误杀要用日志放行，别一上线就全拦截。",
    "cloudflare-pages": "Cloudflare Pages 在全球 CDN 上托管静态与 SSR/适配器应用，与 Workers、R2 集成紧密，性价比高。\n\n常与 Next/SvelteKit/TanStack Start 等适配器搭配；相对 Vercel，偏「边缘+成本」叙事。构建限额、运行时差异与调试体验是选型时的主要权衡。\n\n与 Workers 绑定做全栈时注意绑定名与环境差异；构建缓存可显著加速。",
    "cloudflare-r2": "R2 是 Cloudflare 的 S3 兼容对象存储，主打**无出口流量费**，与 Workers/Pages 同生态。\n\n适合存用户上传、静态资源与备份；需要强一致性事务或复杂查询时仍应回关系库。国内上传/下载延迟与合规要求需实测。\n\n公共桶与签名 URL 策略要分清；需要图片变换时另接专用服务。",
    "continue": "Continue 是开源 IDE 扩展（VS Code / JetBrains），可接任意模型与自定义 Agent，强调可自托管、可组装。\n\n适合已有模型渠道、希望避开单一 AI IDE 订阅的团队。体验取决于你接的模型与规则质量；相对 Cursor 等「产品完整度」更偏工具箱。\n\n可接本地 Ollama 做隐私优先；规则与上下文质量决定体验上限。",
    "creem": "Creem 是面向独立开发者的 Merchant of Record（MoR），代收税与全球结账，常作 Lemon Squeezy / Paddle 的备选。\n\n大陆主体低月销验证产品时，MoR 通常优于直接冲 Stripe。选型时对比费率、覆盖国家、退款与政策稳定性，并预留迁移路径。\n\n当备选 MoR 时先跑一遍沙盒订阅/退款；政策变化快，保持可迁移的客户与商品模型。",
    "cursor": "Cursor 是基于 VS Code 的 AI 原生编辑器：Agent、多文件编辑、规则与 MCP 是核心卖点，在本地仓库上结对改码。\n\n适合日常写码与中等规模重构；注意订阅额度、Privacy Mode 与「难过夜并行」的天花板。与 Claude Code / Copilot / Windsurf 等同层对比工作流，而非与 Lovable 等云端 Builder 混比。\n\nRules/MCP 是杠杆；把仓库约定写进规则，比每次口头提醒 Agent 更有效。",
    "daisyui": "DaisyUI 在 Tailwind 之上提供语义化组件类，用类名拼出按钮、卡片等，适合快速出界面、少写自定义 CSS。\n\n相对完整设计系统（Ant/Mantine）更轻；相对 shadcn（复制源码）更「类名驱动」。主题与可访问性深度不如原语级方案，适合营销页与中小后台。\n\n类名语义化上手快；深度品牌定制时可能感到主题变量不够细。",
    "deepseek-family": "DeepSeek（深度求索）是国产大模型**产品族**，以高性价比推理与代码能力著称；旗舰对话/代码档见「DeepSeek 旗舰」，R1 等为特化线。\n\n国内可访问、API 生态活跃；选型时用下属档位与其他族旗舰对比，勿把族名与某次版本标签混为一谈。\n\n性价比与代码场景口碑高；企业采购与开源权重许可分开评估。",
    "deepseek-v3": "DeepSeek 产品族的**旗舰对话/代码选型档**。当前版本标签为 V3（具体 API 名以控制台为准），主打性价比与编码场景。\n\n与 Claude Opus、Qwen-Max 等同属档位粒度。注意开源权重线与官方 API 的能力/许可差异，生产调用以官方渠道配额与条款为准。\n\n旗舰对话/代码档，适合成本敏感的高质量任务；关键合规行业核对数据路径。",
    "deno": "Deno 是安全优先、TS-first 的运行时：默认权限沙箱、原生 TypeScript，并有 Deno Deploy 等边缘部署叙事。\n\n适合新服务与边缘脚本；与 Node 生态互操作在改善但仍有摩擦。若团队重度依赖 npm 历史包，需评估兼容成本。\n\n权限旗标适合不信任脚本场景；npm 兼容改善中，关键依赖需提前验证。",
    "dify": "Dify 是开源的 LLM 应用可视化平台：工作流、RAG、Agent 可编排，国内团队采用多，可自托管。\n\n适合产品/运营共建 AI 功能、或快速验证流程；复杂工程化 Agent 仍可能落到 Mastra/LangGraph 代码栈。注意版本升级与插件生态锁仓。\n\n可视化利于跨职能协作；版本与环境（开发/生产）要隔离，避免编排误发。",
    "dnspod": "DNSPod（腾讯云 DNS）是国内常用的权威解析服务，与腾讯云产品、备案与安全能力联动方便。\n\n国内站解析的常见选择；出海主站亦可继续用 Cloudflare DNS。双市场产品往往「国内 DNSPod/阿里云 DNS + 海外 Cloudflare」并行。\n\n解析与监控告警可同云；切换 DNS 前同样先降 TTL。",
    "docker": "Docker 是容器镜像构建与运行的事实标准，把「本地可跑」变成「环境可复现」，是 CI 与云原生部署的底座。\n\n几乎所有 PaaS/K8s 路径都会碰到镜像；注意多架构构建、镜像体积与密钥勿打进镜像。桌面 Docker 与 CI 远程 Builder 的资源成本需单独规划。\n\n本地与 CI 用同一 Dockerfile 可减少「在我机器能跑」；注意构建缓存与密钥挂载。",
    "doppler": "Doppler 是托管型开发者 Secrets：按项目/环境同步密钥，常用 `doppler run` 注入子进程，减少「.env 满天飞」。\n\n适合小团队快速治理环境变量；相对 Infisical/Vault，偏 SaaS 便捷。关键生产仍建议配合权限审计与轮换策略。\n\n按环境同步减少「错环境密钥」；本地与 CI 用同一项目结构命名。",
    "drizzle": "Drizzle 是贴近 SQL 的 TypeScript ORM：类型安全、轻量，与 Neon/Turso/Postgres 搭配极多。\n\n适合希望「看见 SQL」又要类型推导的团队；相对 Prisma 更少魔法、迁移与关系表达风格不同。与 Zod 常一起出现在现代 TS 后端。\n\n迁移与 SQL 可见性好；复杂查询可退回原生 SQL 而不失去类型边界。",
    "edgeone": "腾讯 EdgeOne 是国内边缘安全加速产品，覆盖 CDN、防护与边缘能力，对标 Cloudflare 的部分场景。\n\n面向中国大陆用户的站点/API，常作为海外 CDN 的国内镜像层。选型看节点覆盖、套餐与和控制台复杂度，并与备案域名绑定。\n\n国内合规站点的边缘层常见选择；与源站回源协议和证书配置一起验收。",
    "feishu-bot": "飞书群机器人与开放平台是国内团队**通知、审批回调、简易互动**的常用入口。\n\n适合把 CI 失败、值班告警、表单审批推到群里；复杂交互需走开放平台权限与事件订阅。与企业微信机器人场景类似，选型看公司已用哪套 IM。\n\n签名校验与频率限制别省；把告警分级，避免群消息噪声导致忽略。",
    "feishu": "飞书是国内一站式协作套件（文档、日历、IM、审批、多维表），许多团队的默认协作面。\n\n做内部工具与审批流时，开放平台与机器人是关键集成点。出海团队可能并行 Slack/Linear；纯国内团队飞书往往是「系统中枢」。\n\n多维表 + 审批可撑不少内部运营；对外产品协作用户若在海外需并行其他工具。",
    "figma": "Figma 是协作式界面设计与原型的事实标准，Dev Mode、变量与组件库支撑设计到工程的交接。\n\nAI/工程工作流里常作为设计源；与代码生成工具（v0 等）可衔接，但设计系统治理仍靠人工约定。注意席位费用与文件权限。\n\n组件命名与 token 约定越早统一，工程落地越少返工；评审用评论而非截图群传。",
    "firebase-fcm": "Firebase Cloud Messaging 提供 Android/iOS/Web 推送，是跨平台推送的常见默认选项。\n\n推送链路依赖 Google 服务；国内安卓通道往往还需厂商推送或友盟等方案并行。与短信/邮件组成完整触达矩阵。\n\n与 APNs/厂商通道的配置是隐藏工作量；失败重试与失效 token 清理别忘。",
    "firebase": "Firebase 是 Google 的移动/Web 后端套件：Auth、Firestore、Hosting 等一体化，移动端生态强。\n\n适合快速做 App 后端；数据模型与查询范式偏 Firebase 风格，迁出成本需提前想。国内直连与合规常成问题，双市场产品慎作唯一后端。\n\n移动端 SDK 成熟；Firestore 数据模型后期难迁，早期就要有边界。",
    "fly-io": "Fly.io 把容器跑在靠近用户的区域，适合需要低延迟后端、又不想自建 K8s 的团队。\n\n相对 Railway/Vercel：更「你带 Dockerfile」。注意区域选择、卷存储与定价模型；中国大陆访问与备案仍需另案。\n\n按区域放置服务贴近用户；持久卷与数据库选址要和延迟目标一致。",
    "ga4": "Google Analytics 4 是事件模型的主流网站/应用分析，报表与广告生态绑定深。\n\n隐私合规（Cookie/同意）、国内可用性与数据驻留是主要顾虑；Indie 常并行或改用 Plausible/Umami/PostHog。埋点设计比工具本身更影响价值。\n\n事件命名规范比报表模板更重要；国内流量采集完整性要单独验收。",
    "gemini-pro": "Google Gemini 产品族中的 **Pro 主力/旗舰选型档**，与 Flash 等轻量、低成本档区分。\n\n适合需要更强推理或多模态的任务；成本与延迟通常高于 Flash。与 Claude Opus、GPT 旗舰同层比较能力与价。\n\n主力智能档；批量分类/抽取可考虑同族更轻量档降本。",
    "gemini": "Gemini 是 Google DeepMind 的大模型**产品族**。族下有 Pro / Flash 等档位；长上下文与多模态是常见的族级叙事。\n\n选型先定族再定档；具体对比用 Pro 等档位条目，避免与他族旗舰或版本名混列。\n\n多模态与长上下文是族级卖点；落地仍按 Pro/Flash 档位算成本和延迟。",
    "github-actions": "GitHub Actions 是 GitHub 原生 CI/CD：YAML 工作流与 PR/Release 深度集成，Indie 与开源默认选择。\n\n适合构建、测试、发布与简单部署；复杂多云编排可再引入专用平台。注意分钟数配额、自托管 Runner 与 secrets 管理。\n\n复用 composite action 减少复制粘贴；密钥最小权限，避免把云钥写进日志。",
    "github-copilot": "GitHub Copilot 覆盖多 IDE 的 AI 结对，企业可预测计费与合规叙事较强。\n\n适合已在 GitHub 生态、需要采购友好的团队；Agent 能力随产品线演进，需与 Cursor 等「AI 原生 IDE」按工作流对比，而非只比补全。\n\n企业版叙事强；个人订阅则对比 Cursor 等按「补全 vs Agent」工作流试一周。",
    "github-projects": "GitHub Projects 把看板/表格嵌在仓库上下文，与 Issues、PR、Actions 同仓，减少工具跳转。\n\n适合小团队与开源协作；复杂产品管理可能仍转向 Linear 等。与「文档型 Wiki」不同，偏工程交付追踪。\n\n自动化可把 PR/Issue 状态推进看板；复杂路线图仍可能外挂专用 PM 工具。",
    "github-releases": "通过 GitHub Releases 分发二进制/安装包，常配合 Tauri、Electron 或脚本的自动更新。\n\n适合桌面端、CLI 与开源直接分发；要触达大众消费者仍可能需要各应用商店。注意签名、公证与更新通道安全。\n\n资产命名与 changelog 规范便于自动更新器对接；签名校验是桌面分发底线。",
    "glm-flagship": "智谱 GLM 产品族的**旗舰选型档**（当前版本如 GLM-4.x，以官方控制台为准）。\n\n面向国内低延迟与合规友好的旗舰调用；与 Qwen-Max、DeepSeek 旗舰、Kimi 旗舰同层评估效果、价与配额。\n\n国内低延迟与中文场景是加分项；用同一评测集对齐其他国产/海外旗舰档。",
    "glm": "智谱 GLM 是国产大模型**产品族**；旗舰能力与版本见下属选型档位（如 GLM 旗舰）。\n\n国内可访问、政企与教育场景常见。对比时用档位对齐其他族旗舰，勿用族名与 Arena 单项直接混比。\n\n政企采购与国内专有云叙事常见；效果对比仍应落到具体旗舰档与场景集。",
    "go": "Go 是简洁、高并发友好的语言，广泛用于 CLI、网关、基础设施与云原生服务。\n\n适合要单一二进制、部署简单、并发模型清晰的后端；相对 TS 全栈，生态更偏系统与平台工程。与 Rust 比：上手快、抽象少，极致性能与零成本抽象则让位于 Rust。\n\n单二进制与交叉编译友好；错误处理显式，适合平台型服务而非快速 CRUD 原型。",
    "google-play": "Google Play 是全球 Android 主应用商店，伴随开发者账号、审核、账单与政策约束。\n\n国内用户常无法直达，需华为应用市场等国内渠道并行。收款与税务按主体规划；与 App Store 一样，抽成与合规是产品成本的一部分。\n\n账单与政策地区差异大；国内包体常需单独渠道包与隐私合规文案。",
    "gpt-4o": "OpenAI GPT 产品族的**旗舰选型档**。历史上以 GPT-4o 等为代表命名，实际可用模型 id 以 OpenAI/Azure 控制台为准。\n\n与 Claude Opus、Gemini Pro 同层比能力、价与工具调用；「4o」是版本/产品名 Impetus，不要把它当成与「GPT 产品族」同级的节点。\n\n旗舰档用于难任务；日常辅助用同族低价档，建立「路由策略」比死磕一档重要。",
    "gpt": "GPT 是 OpenAI 对话/多模态模型的**产品族**。旗舰档与 mini 档是选型单元；具体版本写在对应档位上，不单独建「某次发布名」条目。\n\n工具链与插件生态深厚；国内直连受限，常经 Azure/网关。对比用档位对齐，勿把族与他族旗舰混列。\n\n生态与工具调用资料最多；区域与账单主体常是比模型本身更大的约束。",
    "grafana": "Grafana 是开源可观测可视化与告警中枢，常与 Prometheus、Loki、Tempo 等组合。\n\n适合已有指标/日志管道、需要统一仪表盘的团队；纯 SaaS 错误监控可先 Sentry。运维与数据源配置是主要成本。\n\n先统一标签规范再画仪表盘；告警路由到飞书/Slack 比堆图表更值钱。",
    "hashicorp-vault": "Vault 提供动态密钥、加密即服务与精细策略，是企业级 secrets 的重型方案。\n\n运维与学习曲线明显高于 Doppler/Infisical；适合中大型团队与强合规。Indie 早期通常过重，除非已有平台组承接。\n\n动态数据库凭证是经典价值；小团队可先托管 Secrets 再视合规升级。",
    "huawei-appgallery": "华为应用市场是国内安卓重要分发渠道之一，常需软著、资质与适配要求。\n\n做国内安卓覆盖时，往往与多家应用商店并行上架。与 Google Play 用户群不重叠，不能互相替代。\n\n上架材料、隐私合规与机型适配成本常被低估；国内安卓覆盖是「多市场作战」，不是单点发布。",
    "infisical": "Infisical 是开源开发者 Secrets 平台：按项目/环境组织密钥，CLI 可注入进程，并可自托管。\n\n适合想要 Doppler 式体验又要数据自控的团队。与 1Password（偏密码库）互补；生产仍需权限模型与审计。\n\n自托管时备份与升级通道要设计好；本地开发用 CLI 注入代替共享 .env。",
    "jimeng": "即梦是字节系 AI 图像生成与设计辅助，国内可访问，适合营销图、创意草稿等场景。\n\n商用授权、品牌安全与内容合规条款需核对。与 Midjourney 同属设计资产层，按地区可用性与风格偏好选择。\n\n活动视觉与电商主图是高频用法；输出需过品牌与广告法审核。",
    "kimi-k3": "月之暗面 Kimi 产品族的**旗舰选型档**。当前版本为 K3（约 2.8T MoE、百万级上下文、原生多模态等能力叙事，以官方为准）。\n\n与 Claude Opus、Qwen-Max、DeepSeek 旗舰同属档位粒度，可对齐 Arena/定价；不要与「通义千问产品族」等上层节点直接同列。\n\n旗舰档对齐海外旗舰做评测；上下文很长也不要无脑塞整仓，仍要检索与摘要。",
    "kimi": "Kimi 是月之暗面面向 C 端与 API 的大模型**产品族**。旗舰档当前版本为 K3，见「Kimi 旗舰」条目。\n\n长上下文与国内可访问是常见叙事；对比请用旗舰档对齐 Claude Opus / Qwen-Max，勿把「K3」当成与产品族同级的品牌。\n\n长上下文产品叙事强；API 与 C 端产品能力可能不同步，以控制台为准。",
    "langfuse": "Langfuse 开源提供 LLM 追踪、评分、数据集与 Prompt 管理，可自托管，是 AI 应用可观测的常见选择。\n\n适合把线上质量做成可迭代闭环；与应用框架（Mastra/LangGraph）互补。注意采集隐私与自托管成本。\n\n把线上失败样本沉淀成数据集，评测才闭环；注意提示词版本与发布对齐。",
    "langgraph": "LangGraph 是 LangChain 生态的有状态 Agent **图编排**（Python 强）：分支、循环、人机回路与持久化是长项。\n\n适合复杂工作流与生产态 Agent；TS 团队可评估 Mastra。学习曲线与抽象层是主要成本，简单 RAG 不必上图。\n\n状态持久化让长任务可恢复；图太复杂时可读性下降，需文档化节点契约。",
    "lemonsqueezy": "Lemon Squeezy 曾是创作者友好的 MoR（税务托管、数字商品与订阅）。被 Stripe 收购后，**存量**账户多可继续，但**新大陆独立开发者**申请收紧。\n\n新项目更建议优先评估 Paddle / Polar / Creem，并把迁移路径写进商务预案。\n\n存量可续用；新商户把迁移演练（商品/订阅/Webhook）写进 checklist。",
    "linear": "Linear 是工程师友好的项目管理：高速 issue、键盘流与 GitHub/Agent 工作流契合。\n\n适合产品+工程一体的小团队；相对 GitHub Projects 更「产品化」，相对 Jira 更轻。文档型知识仍常外挂 Notion/飞书。\n\n快捷键与循环（cycle）适合节奏型团队；大型多产品组合权限模型要提前规划。",
    "litellm": "LiteLLM 用统一的 OpenAI 兼容接口代理上百种模型，可自托管，适合网关、路由与落库。\n\n常与 OpenRouter（托管聚合）对照：要自控与内网选 LiteLLM，要免运维选托管。注意各上游限速、账单与失败重试策略。\n\n可做落库与预算路由；上游故障时的 fallback 链比「接更多模型」更重要。",
    "llamaindex": "LlamaIndex 专注文档索引、检索与 RAG/数据代理，Python/TS 均有，适合「把私有知识接进模型」。\n\n简单 RAG 也可 pgvector + 自研；复杂解析与检索流水线时框架价值更高。与 Agent 编排框架分工：它偏数据面。\n\n解析质量决定 RAG 上限；先把文档清洗与切片策略做对，再调检索参数。",
    "lm-studio": "LM Studio 提供图形化本机模型管理与对话，降低非 CLI 用户跑本地模型的门槛。\n\n适合试用、演示与隐私敏感草稿；生产服务更常见 Ollama/自建推理。模型许可与硬件门槛需自查。\n\n下载的权重许可可能与「可商用 API」不同；对外服务勿默认本地试用条款。",
    "lottiefiles": "Lottie 是轻量矢量动效格式生态；LottieFiles 提供资源、工具与协作，Web/移动端常用。\n\n适合营销与微交互；注意运行时体积与复杂动画性能。与「图标集」不同层，不要和图标库同榜对比。\n\n设计交付用 JSON；工程侧控制播放次数与降级静态图，避免首屏卡顿。",
    "lovable": "Lovable 是「提示即全栈应用」的云端 Builder（Flavor B）：浏览器内从描述到部署，默认意见栈（如 React/Supabase）。\n\n出活极快，但 auth/DB/deploy 锁仓风险高。有真实用户与收入前，应规划导出到可移植仓库与自有云。\n\n适合验证交互与信息架构；数据库规则与密钥一旦进生产，迁移成本陡增。",
    "lucide": "Lucide 是基于 Feather 演进的开源图标集，线条清晰，React 等多框架封装齐全。\n\n适合产品 UI 图标层；与 Phosphor（多字重）按视觉体系二选一或分工。不可与 Ant Design 等完整组件库同榜硬比。\n\n图标语义保持一致比「多一个风格」重要；与文案、空状态插画统一视觉权重。",
    "mantine": "Mantine 提供功能丰富的 React 组件、hooks 与主题体系，适合快速搭后台与 SaaS。\n\n相对 Ant Design 更「现代 hooks」；相对 shadcn 更「库式依赖」。选型看是否接受组件库视觉与包体。\n\n表单与日期等复杂控件省时间；深度定制主题前先确认设计是否接受其默认。",
    "mastra": "Mastra 是 TypeScript 全栈 Agent 框架：agents、工作流、memory、RAG、evals 一体，面向生产。\n\n常建在 Vercel AI SDK 原语之上；适合 TS 团队不想拼装一堆库。Python 复杂图编排可对照 LangGraph。\n\nTypeScript 类型贯穿工具与工作流；观测（evals）建议从第一天就接上。",
    "midjourney": "Midjourney 以高质量文生图著称，品牌与营销视觉常用；交互经 Discord/Web。\n\n订阅制；商用与品牌安全条款需核对。国内可用性与支付方式可能影响采用；可与即梦等国内工具并行。\n\n提示词与风格一致性靠工作流沉淀；品牌项目建议固定种子与审核环节。",
    "mongodb-atlas": "MongoDB Atlas 是托管文档数据库，灵活 schema，与 Node 生态契合。\n\n适合文档型、快速迭代的数据模型；强事务与复杂关系场景更常选 Postgres。注意索引设计与成本随存储/IO 增长。\n\n灵活文档模型利于早期迭代；报表与多文档事务复杂时评估是否迁关系库。",
    "neon": "Neon 提供 Serverless Postgres：分支数据库、自动休眠，契合按量与预览环境。\n\nIndie/SaaS 高频选项；与 Supabase（BaaS 一体）分工：Neon 更「纯数据库」。冷启动与连接池策略需按运行时配置。\n\n预览分支让每个 PR 有独立库；注意连接数与 Serverless driver 的搭配。",
    "netlify": "Netlify 是 Jamstack 部署与边缘函数平台，静态站、表单与身份插件丰富，DX 友好。\n\n适合营销站与中等前端应用；重后端或强边缘可用 Cloudflare/Fly 对照。注意构建时长与函数限额。\n\n分支预览对营销协作友好；大型 SSR/高流量时核算函数与带宽。",
    "next-intl": "next-intl 为 Next.js（尤其 App Router）提供类型友好的国际化消息与路由辅助。\n\n出海产品的常见 i18n 选择；与 CMS/文案流程如何协作比库本身更关键。不要忘记日期/货币/时区等格式化。\n\n路由国际化与文案拆分要尽早约定；避免业务字符串散落组件各处。",
    "nextjs": "Next.js 是基于 React 的全栈元框架，支持 SSR/SSG/RSC 等模式，与 Vercel 一等集成。当前 Active LTS 为 16.x 线。\n\n多数 Vibe/Indie Web 默认起点；也可适配自托管或其他平台。注意跨大版本（App Router/Turbopack）带来的教程过时问题。",
    "nodejs": "Node.js 是最主流的 JS/TS 服务端运行时，npm 生态中心，前后端同语言的基础。\n\n几乎所有全栈 TS 工具链的默认假设；与 Bun/Deno 对比时看兼容性、运维成熟度与团队熟悉度，而不是微基准。\n\nLTS 版本线是生产默认；与前端同语言降低上下文切换，是全栈 TS 的底座。",
    "notion": "Notion 把文档、数据库与 Wiki 合在一起，适合团队知识沉淀与轻量业务表。\n\n工程交付追踪更常 Linear/GitHub；Notion 偏「写清楚与对齐」。API 可做轻集成，但不要当高并发业务库。\n\n轻量 CMS/发布日历可行；高并发内容库或权限复杂场景易撞墙。",
    "nuxt": "Nuxt 是基于 Vue 的全栈元框架，文件路由与 SSR 体验成熟，中文社区友好。\n\nVue 技术栈的默认全栈选择；与 Next（React）按团队前端栈二选一。部署可多平台，不绑单一云。\n\nNitro 服务端与模块生态是加分项；迁移自纯 Vue SPA 时注意渲染模式选择。",
    "ollama": "Ollama 让本机一键拉取并服务开源模型，适合隐私、离线与本地 Agent 试验。\n\n开发机常用；生产推理需另看 GPU 与编排。与 LM Studio（GUI）互补，与云端 API 网关是不同部署模型。\n\n本地 OpenAI 兼容接口方便接 Agent；模型更新与显存规划是日常成本。",
    "one-api": "New API / One API 是国内社区常用的**渠道聚合与令牌分发**系统，可私有部署，统一管理多家模型上游。\n\n适合团队内部分发额度、对账与切换渠道；安全上必须管好管理端与令牌泄露面。与 OpenRouter（托管）对照运维成本。\n\n令牌分发适合团队共享渠道；管理端必须二次验证，泄露等于公开钱包。",
    "onepassword": "1Password 是成熟的密码库，并提供 CLI（`op run`）与开发者 Secrets 注入。\n\n适合个人/团队凭据与少量自动化；重型动态密钥与策略引擎可看 Vault。与 VibeHolding 本地凭据管家是互补而非替代：一个偏通用密码库，一个偏选型条目绑定。\n\n团队保险库 + 开发者注入可减少口令口口相传；自动化账号用服务账户隔离。",
    "openai-codex": "OpenAI Codex 产品线强调异步云端编码 Agent：跨 CLI/Web 等面保持任务状态，沙箱执行，适合并行、过夜类任务。\n\n相对本地 IDE 结对（如 Cursor），更偏云端异步执行；注意沙箱限制、仓库权限与账单。\n\n异步任务适合「丢进去稍后再看」；仓库权限与密钥注入策略要按最小权限。",
    "openrouter": "OpenRouter 用一个 API Key 路由多家模型，便于比价、切换与兜底，适合原型与多模型策略。\n\n托管聚合，免自建网关；生产需评估可用性、数据路径与限速。与 LiteLLM（自建）按运维能力选择。\n\n同一提示在多模型间 A/B 很方便；生产要设超时、降级与成本告警。",
    "opentelemetry": "OpenTelemetry 是 Traces/Metrics/Logs 的开放采集标准，避免应用绑死单一 APM 厂商。\n\n适合要长期可观测架构的团队；落地成本在埋点与后端选型（Grafana、云 APM 等）。小项目可先 Sentry 再逐步引入。\n\n先打通一条关键路径的 trace，再铺全量；半吊子埋点比没有更误导。",
    "paddle": "Paddle 是面向 SaaS/软件的 Merchant of Record：代收税、全球结账与合规，适合独立开发者卖软件与订阅。\n\n大陆主体低月销验证时的主流 MoR 选项之一；对比 Polar/Creem 的费率、品类政策与开发者体验。要 Stripe Checkout 体验则需另规划主体。\n\n买家体验与税务合规是 MoR 价值；订阅升级/降级与退款政策写入产品FAQ。",
    "pgvector": "pgvector 是 Postgres 向量扩展，可在 Supabase/Neon/自建 PG 上做向量检索，Indie RAG 的首选「先不加新数据库」。\n\n适合中小规模嵌入检索；超大规模或复杂过滤可评估 Qdrant 等专用库。注意索引类型、维度与维护 vacuum。\n\n先验证召回再上重排；嵌入模型一换，旧向量通常要全量重算。",
    "phosphor-icons": "Phosphor Icons 提供多种字重的 SVG/React/RN 图标，灵活且一致。VibeHolding 设计规范将其作为硬性图标系统。\n\n属 UI 图标叶类，不应与 Ant Design 等完整组件库、或 Lottie 动效同榜对比。\n\nRegular/Bold/Duotone 按交互态切换，避免同一界面混用无关字重。",
    "pingpong": "PingPong 面向跨境电商与部分开发者场景的收款与资金服务，国内团队较熟悉。\n\n大额与新行业风控需注意；与万里汇/Airwallex 按场景（店铺、广告、应用商店）对比开户与结汇体验。\n\n店铺收款与开发者软件订阅不是同一审核口径；按真实业务类目准备材料。",
    "planetscale": "PlanetScale 基于 Vitess 提供 Serverless MySQL 体验，分支工作流与扩缩是卖点。\n\n适合熟悉 MySQL、需要水平扩展叙事的团队；Postgres 生态（Neon 等）是常见对照。注意免费档与限制变更历史。\n\n分支工作流对 schema 变更友好；SQL 兼容性以 Vitess 限制为准，勿假设完整 MySQL。",
    "plausible": "Plausible 主打隐私友好、无 Cookie 墙的网站分析，可云可自托管，页面简洁。\n\n适合营销站与合规敏感产品；相对 GA4 功能更少但心智负担低。与 Umami 同层，按托管偏好选择。\n\n脚本轻、隐私叙事清晰；要广告归因深度时可能仍需补强其他工具。",
    "pnpm": "pnpm 用内容寻址存储与严格依赖提升磁盘效率，Monorepo 友好，是现代 JS 仓常见默认包管理器。\n\n与 npm/yarn 互操作需约定 lockfile；CI 缓存策略要按 pnpm store 配置。与 workspace 协议搭配效果最佳。\n\nshamefully-hoist 等兼容开关能救老项目，但新仓尽量保持严格依赖。",
    "polar": "Polar 强调开源项目与数字产品变现，带 MoR/税务托管叙事，常作 LS/Paddle 备选。\n\n适合开源+付费、赞助与商品化并行的作者。对比竞品时看品类支持、开发者 API 与政策稳定性。\n\n开源赞助与商业化同仓是特色；品类与地区覆盖以官方政策为准并定期复核。",
    "postgresql": "PostgreSQL 是功能强大的开源关系库，扩展丰富（含向量等），是多数 BaaS 与云库的底座。\n\n默认优先于「先上 NoSQL」；文档库/缓存再用 Mongo/Redis。托管选型（Neon/Supabase/RDS）决定运维体验。\n\n先用好索引与EXPLAIN；扩展（向量、全文）按需加，避免一上来过度设计。",
    "posthog": "PostHog 开源提供产品分析、Session、Feature flags 等，可云可自托管，横跨可观测与增长。\n\n适合要快速验证功能开关与漏斗的产品团队；事件量上涨后关注成本。与「纯错误监控」Sentry、「纯网页统计」Plausible 分工不同。\n\n功能旗标 + 分析同库便于闭环；自托管要评估事件量与磁盘。",
    "pulumi": "Pulumi 用 TypeScript/Python 等通用语言写基础设施，相对 HCL 对前端/全栈更友好。\n\n适合想把 IaC 留在同一语言工具链的团队；状态后端与权限设计仍关键。小项目用平台 UI 可能更简单。\n\n与应用同语言复用类型与 CI；状态锁与 Secret 加密配置是上线前必查项。",
    "python": "Python 是 AI Agent、数据与脚本的通用语言，后端与自动化也很常见。\n\n做 AI 基础设施（LangGraph/LlamaIndex）时几乎默认；Web 全栈 TS 团队可把 Python 限在模型/数据面。包装与部署（venv/uv/容器）需约定。\n\nAI 样例代码大多是 Python；与 Node 服务并存时用清晰的 API 边界，避免双栈逻辑漂移。",
    "qdrant": "Qdrant 是高性能开源向量数据库，过滤与检索能力强，可云可自托管。\n\n当 pgvector 不够（规模、过滤、独立扩缩）时上专用向量库。注意与嵌入模型维度、距离度量一致。\n\n过滤条件 + 向量混合检索是强项；云托管适合少运维，自托管适合数据驻留。",
    "qwen-max": "通义千问产品族的**旗舰选型档（Max）**。具体子版本与 API 名以阿里云百炼控制台为准。\n\n与 Claude Opus、Kimi 旗舰、DeepSeek 旗舰同层评估。开源 Qwen 权重线与云上 Max API 是不同交付形态。\n\n中文与国内业务场景常见首选档之一；成本敏感流量可降级到 Plus/Turbo 档。",
    "qwen": "通义千问是阿里云大模型**产品族**（含 Max / Plus / Turbo 等档与开源权重线）。选型对比请用下属档位（如 Qwen-Max）。\n\n国内百炼生态与云产品联动是优势；勿与具体版本或其他族旗舰混为同一粒度。\n\n云上档位与开源权重线并行；企业采购常走阿里云，效果评测仍应对齐场景。",
    "radix-ui": "Radix 提供无样式、可访问性优先的组件原语，是现代设计系统与 shadcn 一类方案的底座。\n\n适合要完全掌控视觉的团队；不直接给「漂亮默认 UI」。与完整组件库（Ant/Mantine）是不同抽象层。\n\n无障碍行为正确是核心价值；样式完全交给你，需自备设计 token。",
    "railway": "Railway 主打从仓库到数据库的一站式 PaaS，部署全栈与托管 DB 的 DX 友好。\n\n适合快速上线与预览环境；成本随常驻服务上涨时对照 Serverless/边缘。中国大陆访问与合规需另案。\n\n数据库与服务同平台省心；生产要关注单区域故障与备份策略。",
    "react": "React 是声明式组件 UI 库，生态庞大，是多数全栈元框架（Next/Remix 等）的基础。\n\n本身不含路由/数据方案，需自行组合或采用框架。与 Vue 按团队栈选择；「只要 UI 库」与「要全栈框架」是不同选型问题。\n\n生态选择多也意味着决策成本高；小项目可用框架约定（Next）减少拼装。",
    "redis": "Redis 是内存数据结构存储，常作缓存、会话、队列、限流与实时排行榜底座。\n\n几乎每条高并发链路的标配；托管可选 Upstash（Serverless）或云厂商。注意持久化策略与热 key。\n\n先明确是缓存还是主存：持久化与淘汰策略决定能否当队列/会话源。",
    "remix": "Remix 强调 Web 标准、嵌套路由、表单与渐进增强，可部署多端，偏「回归平台能力」。\n\n适合重视可访问性与渐进增强的应用；与 Next 同属 React 全栈，生态体量不同。选型看团队是否认同其数据加载模型。\n\n表单与 progressive enhancement 心智清晰；习惯 RSC/Next 数据模型的团队需适应。",
    "replit-agent": "Replit Agent 在 Replit IDE/运行时内完成编写与部署，「接着写完」体验强，属 Flavor B。\n\n锁 Replit runtime 与托管模型；毕业到独立仓库/云的成本要提前评估。适合学习与原型，谨慎直接承接生产凭据。\n\n教学与黑客马拉松很合适；客户数据与支付密钥不要长期放在共享 runtime。",
    "resend": "Resend 提供现代 DX 的事务邮件 API，常与 React Email 模板配套，适合产品通知与魔术链接。\n\n出海 Indie 高频；国内到达率与备案域名策略需实测。与短信/IM 推送组成触达组合。\n\n域名 SPF/DKIM/DMARC 配齐前别指望到达率；模板变更走代码评审更稳。",
    "rust": "Rust 提供内存安全与高性能，无 GC，适合系统、工具链与性能敏感组件（如 Tauri 底层、部分运行时）。\n\n学习曲线陡；全栈业务逻辑更常 TS/Go。在「性能/安全边界」上引入，而不是默认业务语言。\n\nCLI/扩展/性能热点是合理切口；业务 CRUD 用 Rust 往往得不偿失。",
    "sentry": "Sentry 做异常聚合、性能与 Session Replay，前后端 SDK 成熟，是错误监控默认选项之一。\n\n适合尽快看见线上故障；完整可观测再补 OTel/指标。注意 PII 脱敏与配额。\n\nSource map 与 release 绑定后排障效率显著提升；注意免费档事件配额。",
    "shadcn-ui": "shadcn/ui 不是传统 npm 组件包，而是把 Radix + Tailwind 的高质量组件**复制进仓库**，可改源码。\n\n适合要定制设计系统又想起点高的 TS/React 项目；升级靠再同步而非锁版本库。与 Ant Design「安装即用」路线不同。\n\n组件源码在仓内，设计变更可直接改；团队需约定「哪些可改、如何回同步」。",
    "siliconflow": "SiliconFlow（硅基流动）聚合开源/国产模型推理，强调国内低延迟与性价比调用。\n\n适合国内访问友好的模型网关/推理层；与 OpenRouter 按地区与模型目录对照。注意账单、限速与模型版本。\n\n适合国内调用开源权重的「推理层」；模型目录与限速以控制台为准。",
    "stripe-atlas": "Stripe Atlas 帮创业者注册美国公司并开通 Stripe，是「要美主体 + Stripe」的一站式路径。\n\n成本高，且银行侧（如 Mercury）、EIN 等近年变难；能用港/新主体或 MoR 时不必默认 Atlas。\n\n适合明确要美股银行与 Stripe 的路径；只是想收款，优先算 MoR/港新主体总成本。",
    "stripe": "Stripe 是全球在线支付与订阅基础设施，开发者体验与生态（Billing、Connect 等）领先。\n\n大陆主体**不能直接**当默认方案：通常需港/新/美等主体，或先走 MoR。产品技术选型可按 Stripe 设计，商务主体另案。\n\nWebhook 与幂等是接入关键；商务主体未就绪时，工程可先沙盒，收款走 MoR。",
    "supabase": "Supabase 以 Postgres 为核心，提供 Auth、Storage、Realtime 等，常被称作开源 Firebase 替代。\n\nIndie 全栈高频 BaaS；要纯数据库也可只用其 PG 或改 Neon。注意 RLS 设计与供应商锁定面。\n\nRLS 是安全默认；关掉 RLS 图省事等于把数据敞口，上线前必审策略。",
    "sveltekit": "SvelteKit 是 Svelte 的全栈框架，编译期优化带来更小包体与简洁心智，性能口碑好。\n\n生态体量小于 React/Next；适合认可 Svelte 模型的团队。部署适配多平台。\n\n适配器决定部署目标（Node/CF/Vercel 等）；选型时先定托管再定适配器。",
    "tanstack-query": "TanStack Query 管理服务端状态：缓存、重试、失效与乐观更新，是 React/Vue 等数据层主流。\n\n几乎每个非玩具前端都会碰到；与 tRPC/REST 客户端配合。不要用它取代表单本地状态库的职责边界。\n\n约定 queryKey 与失效策略，比纠结用不用全局 store 更重要。",
    "tanstack-start": "TanStack Start 整合 Router/Query 等，提供全栈起步，并可部署到 Cloudflare 等目标。\n\n适合想要 TanStack 一体心智、又要出海边缘部署的团队；相对 Next 生态更年轻，评估社区与示例成熟度。\n\n与 Cloudflare 等目标组合时，先跑通适配器与环境变量注入再铺业务。",
    "testflight": "TestFlight 是 Apple 官方 Beta 通道，用于上架前验证与小范围灰度。\n\niOS 发布流水线的标准一环；与正式 App Store 审核仍是两回事。席位与构建有效期有限制。\n\n外测需注意构建过期与名额；反馈收集建议绑 Issue/表格，避免只靠邮件。",
    "trae": "Trae 是字节跳动推出的 AI IDE，面向中文开发者，强调国内可访问与协作体验，常作 Cursor 的国内对标。\n\n能力与模型策略随版本变化，需按实际工作流评测。企业数据策略与隐私模式同样关键。\n\n中文场景与国内网络是主要动机；安全策略（代码上传范围）按公司规范配置。",
    "trpc": "tRPC 让客户端与服务端共享 TypeScript 类型，少写 schema 重复，常与 Next/Monorepo 同用。\n\n适合全 TS 仓；对外公共 API 或多语言客户端时 REST/GraphQL 可能更合适。与 Zod 校验搭配常见。\n\n端到端类型爽，但对外 API 版本化弱；公开集成面预留 REST/OpenAPI。",
    "turso": "Turso 基于 libSQL 提供分布式/边缘 SQLite，与 Cloudflare 等边缘部署搭配自然。\n\n适合读多写少、要边缘低延迟的数据；复杂事务与分析型负载仍看 Postgres。注意复制与一致性模型。\n\n边缘副本降低读延迟；写入路由与冲突策略要在架构图里写清楚。",
    "twilio": "Twilio 提供全球短信、语音与 Verify 等 API，出海通知与二次验证常用。\n\n按量计费；国内短信到达通常还需国内服务商。注意合规（退订、发送者身份）与成本控制。\n\nVerify 产品可降低自建验证码成本；价格按国家/通道差异大，上线前用目标市场测算。",
    "typescript": "TypeScript 为 JavaScript 加上静态类型，是 Vibe Coding 与全栈 Web 的事实标准语言层。\n\n几乎所有现代前端/Node 工具链默认假设 TS；配置严格度（strict）与生成类型策略影响长期可维护性。\n\n把 `strict` 打开的成本在前期，收益在重构期；生成类型与手写类型边界要清晰。",
    "umami": "Umami 是开源、自托管优先的轻量网站统计，常作 GA 的简单替代。\n\n适合要数据自控的营销站；功能深度不如 GA/PostHog。与 Plausible 同层，按 UI 与托管偏好选。\n\n默认指标足够看趋势；要漏斗/会话回放需另选 PostHog 一类产品分析。",
    "upstash": "Upstash 提供按请求计费的 Serverless Redis、QStash 等，边缘与 Serverless 函数友好。\n\n适合不宜常驻 Redis 实例的架构；延迟与定价模型需按热点键实测。与自建 Redis 对照运维成本。\n\n按请求计费匹配突发流量；热 key 与大 value 仍可能把账单打满，需监控。",
    "v0": "v0 是 Vercel 的 UI 生成原语：从描述/设计生成 React+Tailwind 组件，常嵌入其他 vibe 工作流。\n\n偏「界面层加速」，不是完整全栈 Builder；产出需纳入设计系统治理。与 Lovable/Bolt 的锁仓面不同。\n\n生成结果当草稿，合入前过设计规范与可访问性检查；不要直接当设计系统源。",
    "vercel-ai-sdk": "Vercel AI SDK 提供 TS 流式模型输出、工具调用与 UI 钩子等原语，是 TS AI 应用的地基库之一。\n\nMastra 等框架常建其上；只做简单聊天 UI 时可直接用 SDK。与 Python 生态框架不对等替换，按语言栈选。\n\nUI 流式原语省事；多 Agent 与持久记忆上升到框架层（如 Mastra）再组装。",
    "vercel": "Vercel 是前端与 Serverless 部署平台，与 Next.js 一等集成，预览部署与边缘网络成熟。\n\nIndie Web 默认托管之一；成本随团队与超出发火流量上涨时对照 Cloudflare/自建。中国大陆访问需另备策略。\n\n预览 URL 利于评审；团队席位与商业功能是成本拐点，提前算清楚。",
    "vite": "Vite 基于原生 ESM 提供极速开发服务器与滚动打包，是 Vue/React 等前端的默认开发体验之一。\n\n库模式、SSR 与 Monorepo 都有成熟实践；与框架内置打包（如 Next）分工：应用框架可能封装 Vite 或自有管道。\n\n库模式与应用模式配置不同；Monorepo 下注意预构建与工作区依赖解析。",
    "vue": "Vue 是渐进式前端框架，易上手，中文生态与文档友好。\n\n与 React 按团队选择；全栈用 Nuxt。渐进式意味着可以从小组件用到完整 SPA，不必一次性上全家桶。\n\n国内文档与社区活跃，教学成本低；若团队已是 React，不必为了「新潮」强行切换。",
    "wechat-pay": "微信支付覆盖公众号、小程序、APP 等国内主支付场景，用户覆盖广。\n\n国内 C 端变现几乎必评；商户号、类目与结算周期是商务关键。出海收款不靠微信支付替代 Stripe/MoR。\n\n小程序内支付体验最佳；H5/APP 场景注意授权域名与开放标签限制。",
    "wecom": "企业微信承担国内 B2B 触达、客户联系与内部通知，并与微信生态打通。\n\nToB 产品常需对接；与飞书按公司协作套件二选一或并行。开放能力与权限包较细，集成成本高于「只发群机器人」。\n\n客户联系与活码适合私域；内部机器人通知则更轻，按场景选开放能力包。",
    "windsurf": "Windsurf（Codeium）是面向 Agent 工作流的 IDE，强调级联编辑与上下文感知。\n\n与 Cursor/Copilot 同层比 Agent 完成度、定价与隐私模式。国内网络与账号策略需实测。\n\n级联编辑适合大范围重构预览；仍需人工审查与测试兜底，勿盲信一键应用。",
    "wise": "Wise 提供多币种账户与相对透明的换汇，Indie 常用作跨境收付款中转。\n\n不是应用内支付收银台；与 Stripe/MoR、万里汇等按「账户层 vs 收款层」分工。开户与限额看主体与国家。\n\n个人与公司账户能力不同；大额结汇与证明材料要求随地区变化。",
    "worldfirst": "万里汇（WorldFirst，蚂蚁国际）支持应用商店、广告等场景的跨境收款与结汇，个人开发者叙事友好。\n\n大陆主体出海收款决策树中，常与 Airwallex 并列于「商店/广告变现」分支；低月销软件订阅则优先看 MoR。\n\n店铺/广告场景材料相对清晰；软件订阅类收款未必是其最佳路径，先看类目。",
    "zod": "Zod 把运行时校验与 TypeScript 类型推导合一体，是 API、表单与配置校验的事实标准之一。\n\n与 OpenAPI/JSON Schema 互通方案多；在 tRPC、Server Actions、环境变量解析里几乎随处可见。\n\n错误信息面向用户时要映射文案；与 OpenAPI 同步时选好单一事实来源。",
}


def main() -> None:
    missing = []
    updated = 0
    too_short = []
    for path in sorted(ENTRIES.glob("*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        eid = data["id"]
        if eid not in DESCRIPTIONS:
            missing.append(eid)
            continue
        new = DESCRIPTIONS[eid].strip() + "\n"
        if len(new.strip()) < 80:
            too_short.append((eid, len(new.strip())))
        if data.get("descriptionMd") == new:
            continue
        data["descriptionMd"] = new
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        updated += 1

    print(f"updated={updated} total_defs={len(DESCRIPTIONS)}")
    if missing:
        print("MISSING", missing)
        raise SystemExit(1)
    if too_short:
        print("TOO_SHORT", too_short)
        raise SystemExit(1)
    on_disk = {p.stem for p in ENTRIES.glob("*.json")}
    extra = set(DESCRIPTIONS) - on_disk
    if extra:
        print("EXTRA", sorted(extra))
        raise SystemExit(1)


if __name__ == "__main__":
    main()
