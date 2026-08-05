#!/usr/bin/env python3
"""框架三叶扩种（fw-backend / fw-cross-platform / fw-docs-site）。

- 后端框架 / API：Flask / Koa / Midway / Litestar / Echo / Fiber / Quarkus / Ktor / ASP.NET Core / Symfony
- 跨端 / 移动 / 桌面：Taro / uni-app / Ionic / Kotlin Multiplatform / Compose Multiplatform /
  .NET MAUI / NativeScript / Wails / Lynx / Flet
- 文档站 / 静态站：Docusaurus / VitePress / Mintlify / Nextra / Starlight / MkDocs /
  GitBook / Fumadocs / Hugo / Hexo

用法:
  python3 scripts/expand-framework-2026-08.py
  python3 scripts/expand-framework-2026-08.py --overwrite
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

CAT_BACKEND = "fw-backend"
CAT_CROSS = "fw-cross-platform"
CAT_DOCS = "fw-docs-site"


def save(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def entry(**kw) -> dict:
    e = {
        "pricing": {"model": "open-source"},
        "availability": {
            "chinaAccessible": True,
            "needsCompany": False,
            "needsIcp": False,
            "regions": ["global"],
        },
        "tags": ["framework", "open-source"],
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
    assert 20 <= len(one) <= 58, ("oneLiner", e["id"], len(one), one)
    body = e.get("descriptionMd", "").strip()
    assert 160 <= len(body) <= 360, ("descriptionMd", e["id"], len(body))
    assert e.get("pitfalls"), e["id"]
    assert e.get("subcategory"), e["id"]
    assert 3 <= len(e["tags"]) <= 5, ("tags", e["id"], e["tags"])
    assert e["region"] in ("overseas", "domestic", "both"), e["id"]
    assert e["maturity"] in ("experimental", "beta", "stable", "mature"), e["id"]
    assert e["pricing"]["model"] in ("free", "freemium", "subscription", "usage", "open-source")
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

OSS = {"model": "open-source"}
OSS_CN = {"model": "open-source", "currency": "CNY"}


BACKEND: list[dict] = [
    mk(
        CAT_BACKEND,
        "flask",
        "Flask",
        "python-backend",
        "Python WSGI 微框架 · 内核只留路由与模板 · 能力靠扩展自拼",
        "https://flask.palletsprojects.com",
        "Flask 是 Python 的 WSGI 微框架，核心只保留路由、请求上下文与模板渲染，数据库、表单、鉴权等一律交给 Flask-SQLAlchemy 一类扩展按需拼装。",
        "适合小型服务、内部工具与既有 Python 栈的延续；要原生异步与自动生成的接口文档看 FastAPI，要一站式后台与 ORM 看 Django。",
        "同步模型下承接高并发要靠多进程部署或改走 ASGI 适配；扩展质量参差，拼装口径不统一会推高长期维护成本。",
        vendorId="pallets-projects",
        githubUrl="https://github.com/pallets/flask",
        maturity="mature",
        tags=["python", "backend", "wsgi", "micro-framework"],
        pitfalls=[
            "同步 WSGI 模型在高并发 I/O 场景需额外部署调优",
            "扩展生态质量参差，需自行核对维护活跃度",
        ],
    ),
    mk(
        CAT_BACKEND,
        "koa",
        "Koa",
        "node-backend",
        "Express 原班团队后继 · 洋葱中间件 · 极简内核需自拼装",
        "https://koajs.com",
        "Koa 由 Express 原班团队打造，用 async/await 与洋葱模型重写中间件机制，内核不含路由与模板，一切能力由 koa-router 等中间件按需引入。",
        "想要比 Express 更干净的异步中间件、且愿意自建技术栈约定时选；要开箱的分层与依赖注入看 NestJS，要边缘运行时看 Hono。",
        "官方不提供路由等标配，团队约定不一致时项目容易分化；社区活跃度低于 Express，第三方中间件更新偏慢。",
        vendorId="koajs",
        githubUrl="https://github.com/koajs/koa",
        tags=["nodejs", "backend", "middleware", "minimal"],
        pitfalls=[
            "无官方路由等标配，技术栈由团队自行拼装",
            "社区体量与中间件更新节奏弱于 Express",
        ],
    ),
    mk(
        CAT_BACKEND,
        "midway",
        "Midway",
        "node-backend",
        "阿里开源 Node 企业框架 · IoC 装饰器分层 · 兼顾函数计算形态",
        "https://midwayjs.org",
        "Midway 是阿里巴巴开源的 Node.js 企业级框架，提供依赖注入容器、装饰器路由与组件体系，同一套代码可输出常驻服务或函数计算形态，与阿里云生态衔接紧密。",
        "国内团队做中后台 BFF、需要企业级分层约定，或想让服务与 Serverless 共用代码时评估；纯轻量 API 用 Express/Koa 更省事。",
        "生态与文档以中文社区为主，海外资料与第三方组件较少；与阿里云函数计算耦合较深，换云需评估适配成本。",
        vendorId="alibaba",
        githubUrl="https://github.com/midwayjs/midway",
        region="domestic",
        availability=DOMESTIC,
        pricing=OSS_CN,
        tags=["nodejs", "backend", "domestic", "serverless"],
        pitfalls=[
            "中文社区为主，海外资料与第三方组件较少",
            "Serverless 形态与阿里云函数计算耦合较深",
        ],
    ),
    mk(
        CAT_BACKEND,
        "litestar",
        "Litestar",
        "python-backend",
        "Python ASGI 框架 · 内建 DI 与分层 · FastAPI 的电池齐备对照",
        "https://litestar.dev",
        "Litestar 是 Python 的 ASGI 框架，把依赖注入、数据传输对象、分层控制器与 SQLAlchemy 集成做进内核，走类型优先且电池齐备的路线。",
        "已用 FastAPI 但被中大型项目的目录分层与依赖拼装困扰、想要更成体系的框架约定时评估；小脚本级接口仍是 FastAPI 更轻。",
        "社区规模与教程量远小于 FastAPI，排障更依赖官方文档；项目早期改过名且有破坏性变更，升级需通读迁移说明。",
        vendorId="litestar-org",
        githubUrl="https://github.com/litestar-org/litestar",
        maturity="stable",
        tags=["python", "backend", "asgi", "type-safe"],
        pitfalls=[
            "社区与教程规模远小于 FastAPI",
            "跨大版本有破坏性变更，升级需读迁移说明",
        ],
    ),
    mk(
        CAT_BACKEND,
        "echo-go",
        "Echo",
        "go-backend",
        "Go 高性能 HTTP 框架 · 中间件开箱齐 · API 风格贴近 Gin",
        "https://echo.labstack.com",
        "Echo 是 Go 的轻量高性能 Web 框架，路由分组、参数绑定与中间件一应俱全，另内建 JWT、限流与自动 TLS 等常用件，整体 API 风格与 Gin 高度相似。",
        "Go 服务想要比 Gin 更多开箱中间件、又不愿引入大型企业框架时评估；两者迁移成本相近，团队熟悉度往往是决定项。",
        "生态广度与招聘心智不及 Gin，中文教程较少；历史上换过模块导入路径，老代码跨大版本升级要批量改 import。",
        vendorId="labstack",
        githubUrl="https://github.com/labstack/echo",
        tags=["go", "backend", "http", "middleware"],
        pitfalls=[
            "生态与中文资料规模不及 Gin",
            "跨大版本模块路径变更需批量改 import",
        ],
    ),
    mk(
        CAT_BACKEND,
        "fiber-go",
        "Fiber",
        "go-backend",
        "Go 框架 · fasthttp 内核 · Express 风 API · 与标准库生态有隔阂",
        "https://gofiber.io",
        "Fiber 建立在 fasthttp 而非标准库 net/http 之上，用类 Express 的链式 API 换取更低的内存分配与更高吞吐，写法对 Node 背景的开发者相当友好。",
        "追求极致吞吐、团队来自 Node 背景、且依赖链不强绑标准库时评估；常规业务服务用 Gin 或 Echo 更稳妥。",
        "fasthttp 与 net/http 接口不兼容，大量标准库中间件与 HTTP/2 等能力无法直接复用，选它基本等于锁定生态。",
        vendorId="gofiber",
        githubUrl="https://github.com/gofiber/fiber",
        tags=["go", "backend", "performance", "fasthttp"],
        pitfalls=[
            "基于 fasthttp，标准库 net/http 中间件不可直接复用",
            "HTTP/2 等标准能力支持受底层限制",
        ],
    ),
    mk(
        CAT_BACKEND,
        "quarkus",
        "Quarkus",
        "java-backend",
        "Red Hat 云原生 Java · 构建期优化与原生镜像 · 冷启与内存友好",
        "https://quarkus.io",
        "Quarkus 是 Red Hat 主导的云原生 Java 框架，把大量工作前移到构建期并支持 GraalVM 原生镜像，显著压低启动时间与内存占用，同时保留 CDI、JAX-RS 等标准写法。",
        "Java 栈要上 Kubernetes、在意容器密度与冷启动，或想做函数计算时评估；常规单体与人才储备仍以 Spring Boot 为主。",
        "原生镜像编译耗时且对反射敏感，部分老库需额外配置；第三方能力需走官方 extension，生态广度不及 Spring。",
        vendorId="red-hat",
        githubUrl="https://github.com/quarkusio/quarkus",
        tags=["java", "backend", "cloud-native", "graalvm"],
        pitfalls=[
            "原生镜像编译慢且对反射敏感，老库需配置适配",
            "扩展需官方 extension 支持，生态广度不及 Spring",
        ],
    ),
    mk(
        CAT_BACKEND,
        "ktor",
        "Ktor",
        "kotlin-backend",
        "JetBrains Kotlin 服务端 · 协程原生 · 插件式装配 · 企业件需自补",
        "https://ktor.io",
        "Ktor 是 JetBrains 出品的 Kotlin 服务端框架，全链路基于协程与挂起函数，能力以插件形式按需装配，并提供可跨平台复用的 HTTP 客户端。",
        "团队以 Kotlin 为主语言、想避开 Spring 的注解与反射心智，或要与 Kotlin Multiplatform 客户端共享代码时评估。",
        "事务、批处理、安全等企业级组件需自行拼装，深度不及 Spring Boot；DSL 式配置在跨大版本时改动较多。",
        vendorId="jetbrains",
        githubUrl="https://github.com/ktorio/ktor",
        tags=["kotlin", "backend", "coroutines", "jvm"],
        pitfalls=[
            "企业级组件深度不及 Spring Boot，需自行拼装",
            "DSL 配置跨大版本改动较多",
        ],
    ),
    mk(
        CAT_BACKEND,
        "aspnet-core",
        "ASP.NET Core",
        "dotnet-backend",
        "微软跨平台服务端 · Minimal API/MVC/gRPC · 工具链与性能强",
        "https://dotnet.microsoft.com",
        "ASP.NET Core 是微软的跨平台服务端框架，覆盖 Minimal API、MVC、SignalR 与 gRPC，配合 Entity Framework Core 与内建依赖注入构成完整的企业开发栈。",
        "团队以 C#/.NET 为主，或需要与 Windows、Azure 生态深度衔接时是默认答案；纯 Linux 微服务同样可用，但要接受 .NET 运行时与工具链。",
        "大版本节奏快，LTS 与非 LTS 混用会积累升级压力；国内云厂商与中间件的官方 SDK 覆盖弱于 Java 生态。",
        vendorId="microsoft",
        githubUrl="https://github.com/dotnet/aspnetcore",
        maturity="mature",
        tags=["dotnet", "csharp", "backend", "enterprise"],
        pitfalls=[
            ".NET 大版本节奏快，LTS 与非 LTS 混用增加升级压力",
            "国内云与中间件官方 SDK 覆盖弱于 Java",
        ],
    ),
    mk(
        CAT_BACKEND,
        "symfony",
        "Symfony",
        "php-backend",
        "PHP 组件化企业框架 · 组件可单取 · 是 Laravel 的底层来源",
        "https://symfony.com",
        "Symfony 是 PHP 的组件化企业框架，数十个解耦组件既能整框架使用，也可被别的项目单独引入——Laravel 的 HTTP、路由与控制台底层大量取自 Symfony。",
        "做长周期企业系统、需要严格分层与可替换组件时选；追求快速交付与内建全家桶体验，Laravel 通常更顺手。",
        "配置与抽象层次多，上手曲线比 Laravel 陡；Bundle 生态偏欧洲，国内中文资料与招聘面较窄。",
        vendorId="symfony-sas",
        githubUrl="https://github.com/symfony/symfony",
        maturity="mature",
        tags=["php", "backend", "enterprise", "components"],
        pitfalls=[
            "抽象层次多，上手曲线陡于 Laravel",
            "国内中文资料与招聘面较窄",
        ],
    ),
]


CROSS: list[dict] = [
    mk(
        CAT_CROSS,
        "taro",
        "Taro",
        "miniprogram-cross",
        "京东开源跨端 · React 语法编译到多家小程序 · 兼顾 H5 与 RN",
        "https://github.com/NervJS/taro",
        "Taro 是京东凹凸实验室开源的跨端框架，用 React（也支持 Vue）语法写一次，编译产出微信、支付宝、抖音等各家小程序，以及 H5 与 React Native 应用。",
        "国内业务要同时铺多家小程序、团队又以 React 技术栈为主时是主力选择；只做微信一端时原生开发反而更省事。",
        "各端 API 差异仍需条件编译兜底；跨大版本编译内核切换的改造成本高，第三方 UI 库对新版本跟进不一。",
        vendorId="jd-nervjs",
        githubUrl="https://github.com/NervJS/taro",
        region="domestic",
        availability=DOMESTIC,
        pricing=OSS_CN,
        tags=["cross-platform", "miniprogram", "react", "domestic"],
        pitfalls=[
            "各端小程序 API 差异仍需条件编译兜底",
            "跨大版本编译内核切换改造成本高",
        ],
    ),
    mk(
        CAT_CROSS,
        "uni-app",
        "uni-app",
        "miniprogram-cross",
        "DCloud 跨端 · Vue 语法一码多端 · 插件市场大 · 工具链绑定强",
        "https://uniapp.dcloud.net.cn",
        "uni-app 是 DCloud 推出的跨端框架，用 Vue 语法一套代码发布到各家小程序、H5 与 iOS/Android 原生 App，配套 HBuilderX 工具、插件市场与云打包服务形成闭环。",
        "国内中小团队要低成本铺满小程序与 App、团队又熟悉 Vue 时优先；React 栈团队通常转向 Taro。",
        "生态与工具高度绑定 DCloud，云打包与部分插件为付费项；复杂原生能力仍需写原生插件，性能受运行时限制。",
        vendorId="dcloud",
        region="domestic",
        availability=DOMESTIC,
        pricing=OSS_CN,
        tags=["cross-platform", "miniprogram", "vue", "domestic"],
        pitfalls=[
            "工具链与云服务高度绑定 DCloud，部分能力付费",
            "复杂原生能力需自写原生插件",
        ],
    ),
    mk(
        CAT_CROSS,
        "ionic",
        "Ionic",
        "mobile-hybrid",
        "Web 技术做移动 UI · 组件贴合平台观感 · 配 Capacitor 上原生",
        "https://ionicframework.com",
        "Ionic 提供一整套贴近 iOS/Android 观感的 Web 组件，可与 Angular、React、Vue 任一框架搭配，再交由同团队的 Capacitor 打包为原生应用或 PWA。",
        "团队是 Web 背景、界面以表单与列表为主、要快速出移动端时选；重动效与图形性能的场景看 Flutter 或 React Native。",
        "本质仍是 WebView 渲染，长列表与复杂手势体验有天花板；企业级构建与部分工具属付费服务。",
        vendorId="ionic-team",
        githubUrl="https://github.com/ionic-team/ionic-framework",
        maturity="mature",
        tags=["cross-platform", "hybrid", "webview", "ui"],
        pitfalls=[
            "WebView 渲染，复杂交互与长列表性能有天花板",
            "企业级构建与部分配套工具需付费",
        ],
    ),
    mk(
        CAT_CROSS,
        "kotlin-multiplatform",
        "Kotlin Multiplatform",
        "shared-logic",
        "只共享业务逻辑 · UI 各端保留原生 · 编译到 JVM/iOS/Web",
        "https://kotlinlang.org",
        "Kotlin Multiplatform 把网络、存储与领域逻辑写一次，编译到 Android、iOS、桌面与 Web，界面层则各端保留原生实现，走的是共享逻辑而非共享 UI 的路线。",
        "已有原生双端团队、想复用数据层与业务层又不愿牺牲原生体验时最合适；要连界面一起复用则看 Compose Multiplatform。",
        "iOS 侧仍需 Swift 工程能力与互操作调试；构建配置复杂，第三方库必须专门支持多平台目标才能引入。",
        vendorId="jetbrains",
        githubUrl="https://github.com/JetBrains/kotlin",
        tags=["cross-platform", "kotlin", "mobile", "shared-code"],
        pitfalls=[
            "iOS 侧仍需原生工程能力与互操作调试",
            "第三方库须支持多平台目标才可引入",
        ],
    ),
    mk(
        CAT_CROSS,
        "compose-multiplatform",
        "Compose Multiplatform",
        "shared-ui",
        "Compose 声明式 UI 跨端 · 建在 KMP 之上 · iOS 与 Web 仍在追赶",
        "https://github.com/JetBrains/compose-multiplatform",
        "Compose Multiplatform 由 JetBrains 把 Android 的 Jetpack Compose 延伸到 iOS、桌面与 Web，在 Kotlin Multiplatform 的共享逻辑之上再共享一层声明式界面。",
        "已选 KMP、团队熟悉 Compose 且希望界面也复用时评估；只想共享逻辑、界面保留原生的项目留在 KMP 即可。",
        "iOS 与 Web 目标的成熟度落后于 Android 与桌面；自绘 UI 与系统控件、无障碍能力的融合需逐项验证。",
        vendorId="jetbrains",
        githubUrl="https://github.com/JetBrains/compose-multiplatform",
        maturity="beta",
        tags=["cross-platform", "kotlin", "ui", "compose"],
        pitfalls=[
            "iOS/Web 目标成熟度落后于 Android 与桌面",
            "自绘 UI 的无障碍与系统控件融合需逐项验证",
        ],
    ),
    mk(
        CAT_CROSS,
        "dotnet-maui",
        ".NET MAUI",
        "mobile-cross",
        "微软跨端 UI · C# 一套代码出四端 · Xamarin.Forms 继任者",
        "https://github.com/dotnet/maui",
        ".NET MAUI 是微软 Xamarin.Forms 的继任框架，用 C# 与 XAML 写一套界面并映射到各平台原生控件，输出 Android、iOS、macOS 与 Windows 应用。",
        "团队已是 .NET 栈、要把内部业务应用铺到桌面与移动端时评估；面向消费者的高动效产品通常仍选 Flutter。",
        "平台特性覆盖与工具链稳定性历来是社区抱怨点，iOS 构建仍依赖 Mac；第三方控件生态远小于 Flutter 与 React Native。",
        vendorId="microsoft",
        githubUrl="https://github.com/dotnet/maui",
        tags=["cross-platform", "dotnet", "csharp", "mobile"],
        pitfalls=[
            "平台特性覆盖与工具链稳定性常被诟病",
            "第三方控件生态远小于 Flutter / React Native",
        ],
    ),
    mk(
        CAT_CROSS,
        "nativescript",
        "NativeScript",
        "mobile-cross",
        "JS 直调原生 API · 不走 WebView · Angular/Vue 可用 · 社区偏小",
        "https://nativescript.org",
        "NativeScript 让 JavaScript/TypeScript 直接访问 iOS 与 Android 原生 API 并渲染原生控件，不经过 WebView，可搭配 Angular、Vue 或纯 TypeScript 编写。",
        "想用 Web 语言写原生渲染应用、又要绕开 React 生态时评估；主流选择仍是 React Native 或 Flutter。",
        "社区与插件生态明显小于 React Native，长期维护风险需评估；原生 API 直调虽灵活，类型定义与系统版本适配常要自己补。",
        vendorId="nativescript-team",
        githubUrl="https://github.com/NativeScript/NativeScript",
        tags=["cross-platform", "mobile", "javascript", "native"],
        pitfalls=[
            "社区与插件生态规模小，长期维护存在风险",
            "原生 API 类型定义与系统适配常需自行补齐",
        ],
    ),
    mk(
        CAT_CROSS,
        "wails",
        "Wails",
        "desktop",
        "Go 桌面框架 · 系统 WebView 渲染前端 · 产物小 · Tauri 的 Go 对照",
        "https://wails.io",
        "Wails 用 Go 编写后端逻辑、系统 WebView 渲染前端界面，并把两者绑定编译为单个可执行文件，思路与 Tauri 相近，只是把语言换成了 Go。",
        "后端团队以 Go 为主、要给命令行工具或本地服务加一层桌面壳时最顺手；Rust 栈选 Tauri，需要统一 Chromium 行为选 Electron。",
        "依赖系统 WebView，各平台渲染差异需实测；移动端支持仍属实验阶段，文档与生态规模小于 Tauri。",
        vendorId="wails-io",
        githubUrl="https://github.com/wailsapp/wails",
        tags=["desktop", "go", "webview", "cross-platform"],
        pitfalls=[
            "依赖系统 WebView，跨平台渲染差异需实测",
            "生态与文档规模小于 Tauri / Electron",
        ],
    ),
    mk(
        CAT_CROSS,
        "lynx",
        "Lynx",
        "mobile-cross",
        "字节开源跨端 · 双线程架构 · Web 语法出原生视图 · 生态尚新",
        "https://lynxjs.org",
        "Lynx 是字节跳动开源的跨端框架，用 Web 风格的语法与样式描述界面，经自研的双线程架构渲染为原生视图，已在其自家超级 App 的大流量页面中长期使用。",
        "关注首屏与滚动性能、愿意尝试新生态，或想在 React Native 之外多一个对照方案时评估。",
        "开源时间短，第三方库与中英文档积累有限；周边工具链以字节内部实践为准，生产落地需自建兜底方案。",
        vendorId="bytedance",
        githubUrl="https://github.com/lynx-family/lynx",
        region="both",
        maturity="beta",
        tags=["cross-platform", "mobile", "domestic", "performance"],
        sources=["https://lynxjs.org", "https://github.com/lynx-family/lynx"],
        pitfalls=[
            "开源时间短，第三方库与文档积累有限",
            "工具链以字节内部实践为主，生产落地需兜底",
        ],
    ),
    mk(
        CAT_CROSS,
        "flet",
        "Flet",
        "shared-ui",
        "用 Python 写 Flutter 界面 · 免前端知识 · 内部工具与原型向",
        "https://flet.dev",
        "Flet 让 Python 开发者直接用 Python 代码构建由 Flutter 渲染的界面，无需接触 Dart 与前端工具链，可输出桌面、移动与 Web 应用。",
        "数据、算法或运维团队要给脚本加图形界面、做内部工具或演示原型时非常省事；面向用户的正式应用仍建议原生 Flutter。",
        "控件与主题受封装层限制，复杂交互不如直接写 Flutter；状态与性能模型偏简单，不适合大型消费级产品。",
        vendorId="flet-dev",
        githubUrl="https://github.com/flet-dev/flet",
        maturity="beta",
        tags=["cross-platform", "python", "ui", "prototyping"],
        pitfalls=[
            "控件与主题能力受封装层限制",
            "不适合大型消费级应用的性能与状态需求",
        ],
    ),
]


DOCS: list[dict] = [
    mk(
        CAT_DOCS,
        "docusaurus",
        "Docusaurus",
        "docs-generator",
        "Meta 开源文档框架 · React/MDX · 版本化与多语内建 · 构建偏重",
        "https://docusaurus.io",
        "Docusaurus 是 Meta 开源的文档站框架，基于 React 与 MDX，把多版本文档、国际化、站内搜索与博客模块做成开箱能力，最终产出纯静态站点。",
        "开源项目或产品要长期维护带版本与多语的文档时，是最稳妥的默认选择；只做一份轻量说明则显得偏重。",
        "依赖与构建较重，大站增量构建慢；深度定制主题需要理解 React 与 swizzle 机制，改造成本不低。",
        vendorId="meta",
        githubUrl="https://github.com/facebook/docusaurus",
        maturity="mature",
        tags=["docs", "react", "static-site", "mdx"],
        pitfalls=[
            "依赖较重，大型站点构建耗时长",
            "深度定制主题需掌握 swizzle 机制",
        ],
    ),
    mk(
        CAT_DOCS,
        "vitepress",
        "VitePress",
        "docs-generator",
        "Vue 团队文档站 · Vite 驱动启动极快 · 主题克制 · 版本化需自拼",
        "https://vitepress.dev",
        "VitePress 由 Vue 团队维护，以 Vite 为构建内核、Vue 单文件组件为主题层，Markdown 中可直接书写组件，开发启动与热更新几乎无等待。",
        "中小型文档、组件库文档，或 Vue 生态项目要快速起一个干净的站点时最合适。",
        "内建的版本化与多语能力弱于 Docusaurus，需按目录约定自行组织；默认主题定制空间有限，重设计要自写主题。",
        vendorId="vuejs-team",
        githubUrl="https://github.com/vuejs/vitepress",
        tags=["docs", "vue", "vite", "static-site"],
        pitfalls=[
            "版本化与国际化需自行按目录约定拼装",
            "默认主题定制空间有限",
        ],
    ),
    mk(
        CAT_DOCS,
        "mintlify",
        "Mintlify",
        "hosted-docs",
        "托管式开发者文档 · 开箱 AI 问答与 API 页 · 按席位订阅",
        "https://mintlify.com",
        "Mintlify 是面向开发者文档的托管产品：内容以 MDX 存放在 Git 仓库，平台负责构建、部署、搜索与 AI 问答，并能依据 OpenAPI 规范自动生成接口文档页。",
        "团队想要一套观感专业的产品文档、又不愿自养前端与运维时评估；纯开源项目文档用自建生成器成本更低。",
        "主题与交互只能在平台框架内定制，深度改版受限；按席位与站点计费，自托管与数据出境需按合规口径确认。",
        vendorId="mintlify-inc",
        pricing={"model": "freemium", "currency": "USD"},
        tags=["docs", "hosted", "saas", "api-docs"],
        pitfalls=[
            "定制自由度受平台框架限制",
            "按席位计费，规模扩大后成本需测算",
        ],
    ),
    mk(
        CAT_DOCS,
        "nextra",
        "Nextra",
        "docs-generator",
        "建在 Next.js 上的文档框架 · MDX 约定式 · 与 Vercel 部署顺路",
        "https://nextra.site",
        "Nextra 是构建在 Next.js 之上的文档与博客框架，用文件路由与 MDX 约定生成站点，同时保留完整的 Next.js 能力，可在文档中混用 React 组件与服务端渲染。",
        "项目本就是 Next.js 栈、希望文档与主站同仓同栈同部署时最省事。",
        "Next.js 大版本升级的负担会传导到文档站；主题体系较薄，复杂布局与组件常需自己写。",
        vendorId="vercel-inc",
        githubUrl="https://github.com/shuding/nextra",
        tags=["docs", "nextjs", "mdx", "react"],
        pitfalls=[
            "随 Next.js 大版本升级带来维护负担",
            "主题体系较薄，复杂需求需自写布局",
        ],
    ),
    mk(
        CAT_DOCS,
        "starlight",
        "Starlight",
        "docs-generator",
        "Astro 官方文档主题 · 默认近零 JS · 可混用任意前端框架组件",
        "https://starlight.astro.build",
        "Starlight 是 Astro 官方的文档站方案，借岛屿架构默认输出近乎零 JavaScript 的页面，同时允许在页面内嵌入 React、Vue 或 Svelte 组件，并内建多语与站内搜索。",
        "追求加载性能与轻量产物，或团队前端框架不统一、希望文档不被某一框架绑死时是很好的折中。",
        "生态围绕 Astro，插件数量少于 Docusaurus；版本化文档需借助社区方案，不如内建能力省心。",
        vendorId="astro-inc",
        githubUrl="https://github.com/withastro/starlight",
        tags=["docs", "astro", "static-site", "performance"],
        pitfalls=[
            "插件生态规模小于 Docusaurus",
            "多版本文档需依赖社区方案",
        ],
    ),
    mk(
        CAT_DOCS,
        "mkdocs",
        "MkDocs",
        "docs-generator",
        "Python 静态文档生成器 · 一份 YAML 配置 · Material 主题近乎标配",
        "https://www.mkdocs.org",
        "MkDocs 用 Markdown 与一份 YAML 配置生成静态文档站，本体极简，实际项目几乎都会搭配 Material for MkDocs 主题来获得导航、搜索与版本切换等能力。",
        "Python 项目文档、运维手册或内部知识库要低成本起站、且不希望引入 Node 工具链时选。",
        "交互与组件化能力弱，页面里无法像 MDX 那样直接写组件；Material 主题的部分高级特性仅对赞助者开放。",
        vendorId="mkdocs-team",
        githubUrl="https://github.com/mkdocs/mkdocs",
        maturity="mature",
        tags=["docs", "python", "static-site", "markdown"],
        sources=["https://www.mkdocs.org", "https://squidfunk.github.io/mkdocs-material/"],
        pitfalls=[
            "页面内无法像 MDX 那样嵌入组件",
            "Material 主题部分高级特性仅赞助者可用",
        ],
    ),
    mk(
        CAT_DOCS,
        "gitbook",
        "GitBook",
        "hosted-docs",
        "在线协作写作平台 · 可视化编辑 · Git 双向同步 · 非技术同事友好",
        "https://www.gitbook.com",
        "GitBook 是托管的文档协作平台，提供可视化编辑器、评论审阅与空间权限，同时支持与 Git 仓库双向同步，让产品、运营与研发在同一处维护内容。",
        "文档作者中有较多非技术同事、需要审阅流程与细粒度权限时优先；纯工程文档用生成器更自由。",
        "站点结构与样式的定制自由度低于自建生成器；按成员与空间计费，内容迁出与导出格式建议提前验证。",
        vendorId="gitbook-inc",
        pricing={"model": "freemium", "currency": "USD"},
        maturity="mature",
        tags=["docs", "hosted", "collaboration", "saas"],
        pitfalls=[
            "样式与结构定制自由度低",
            "迁出与导出格式需提前验证，避免锁仓",
        ],
    ),
    mk(
        CAT_DOCS,
        "fumadocs",
        "Fumadocs",
        "docs-generator",
        "Next.js 文档框架 · 内容源与 UI 分层可换 · 组件现代 · 生态年轻",
        "https://fumadocs.dev",
        "Fumadocs 是 Next.js 生态中较新的文档框架，把内容源、界面组件与搜索拆成可替换的层，默认主题现代，也支持依据 OpenAPI 生成接口文档页。",
        "要在 Next.js 上做文档站、又嫌 Nextra 定制空间不足且愿意跟进较快迭代时评估。",
        "项目年轻，API 与目录约定仍在演进，升级需读迁移文档；中文资料与线上案例较少。",
        vendorId="fumadocs-team",
        githubUrl="https://github.com/fuma-nama/fumadocs",
        maturity="beta",
        tags=["docs", "nextjs", "mdx", "react"],
        pitfalls=[
            "版本迭代快，约定仍在演进",
            "中文资料与生产案例较少",
        ],
    ),
    mk(
        CAT_DOCS,
        "hugo",
        "Hugo",
        "static-site-generator",
        "Go 静态站生成器 · 构建极快 · 万页站点友好 · 模板语法独特",
        "https://gohugo.io",
        "Hugo 是用 Go 编写的静态站生成器，单二进制、无运行时依赖，万级页面也能在数秒内构建完成，内容与主题高度依赖它自有的模板语法与目录约定。",
        "内容量大的文档站、博客或站群，追求构建速度与部署简单时选；需要在页面里做复杂交互则考虑前端框架系方案。",
        "Go 模板语法与前端组件化心智差异大，交互需自行写脚本；主题质量参差，深度定制往往要通读主题源码。",
        vendorId="hugo-team",
        githubUrl="https://github.com/gohugoio/hugo",
        maturity="mature",
        tags=["static-site", "go", "docs", "blog"],
        pitfalls=[
            "Go 模板语法上手心智与前端生态差异大",
            "主题质量参差，深度定制需读主题源码",
        ],
    ),
    mk(
        CAT_DOCS,
        "hexo",
        "Hexo",
        "static-site-generator",
        "Node 静态博客生成器 · 中文社区厚 · 主题插件多 · 偏博客而非文档",
        "https://hexo.io",
        "Hexo 是基于 Node.js 的静态站生成器，以博客场景起家，命令行一键生成与部署，主题与插件数量庞大，在中文技术圈积累了很深的使用惯性。",
        "个人博客、技术周刊等以时间流为主的内容站，想沿用成熟中文教程与现成主题时选；产品文档更适合交给 Docusaurus 或 VitePress。",
        "定位偏博客，多版本文档与接口文档能力弱；不少老主题与插件久未更新，Node 大版本升级容易踩坑。",
        vendorId="hexo-team",
        githubUrl="https://github.com/hexojs/hexo",
        region="both",
        maturity="mature",
        tags=["static-site", "blog", "nodejs", "markdown"],
        pitfalls=[
            "面向博客，版本化文档能力弱",
            "老主题与插件更新滞后，Node 升级易踩坑",
        ],
    ),
]


ENTRIES_DATA: list[dict] = BACKEND + CROSS + DOCS


VENDORS_DATA: list[dict] = [
    vendor("pallets-projects", "Pallets", url="https://palletsprojects.com"),
    vendor("koajs", "Koa Team", url="https://koajs.com"),
    vendor("litestar-org", "Litestar Org", url="https://litestar.dev"),
    vendor("labstack", "LabStack", url="https://labstack.com"),
    vendor("gofiber", "Fiber Team", url="https://gofiber.io"),
    vendor("symfony-sas", "Symfony SAS", url="https://symfony.com"),
    vendor("jd-nervjs", "京东凹凸实验室", region="domestic", url="https://github.com/NervJS"),
    vendor("dcloud", "DCloud", region="domestic", url="https://dcloud.io"),
    vendor("nativescript-team", "NativeScript", url="https://nativescript.org"),
    vendor("wails-io", "Wails", url="https://wails.io"),
    vendor("flet-dev", "Flet", url="https://flet.dev"),
    vendor("vuejs-team", "Vue.js Team", url="https://vuejs.org"),
    vendor("mintlify-inc", "Mintlify", url="https://mintlify.com"),
    vendor("gitbook-inc", "GitBook", url="https://www.gitbook.com"),
    vendor("mkdocs-team", "MkDocs", url="https://www.mkdocs.org"),
    vendor("fumadocs-team", "Fumadocs", url="https://fumadocs.dev"),
    vendor("hugo-team", "Hugo", url="https://gohugo.io"),
    vendor("hexo-team", "Hexo", url="https://hexo.io"),
]


EDGES_DATA: list[dict] = [
    # ——— 后端：同层横比 ———
    edge("e-flask-alt-fastapi", "flask", "fastapi", "alternative_to",
         note="同为 Python 微框架：同步 WSGI 扩展拼装 vs 异步类型优先且自动出接口文档"),
    edge("e-flask-alt-django", "flask", "django", "alternative_to",
         note="Python 后端两条路线：微内核自选组件 vs 全家桶与内建后台"),
    edge("e-litestar-alt-fastapi", "litestar", "fastapi", "alternative_to",
         note="同为 Python ASGI：Litestar 内建 DI 与分层约定，FastAPI 更轻但需自建工程结构"),
    edge("e-koa-suc-express", "koa", "express", "succeeds",
         note="Express 原班团队的后继设计：以 async/await 洋葱模型替代回调式中间件", weight=0.75),
    edge("e-koa-alt-fastify", "koa", "fastify", "alternative_to",
         note="Node 轻量后端：Koa 极简需自拼装，Fastify 内建 schema 校验与更高吞吐"),
    edge("e-midway-de-nestjs", "midway", "nestjs", "domestic_equivalent_of",
         note="国内企业级 Node 框架：同为 IoC/装饰器分层，Midway 额外覆盖函数计算与阿里云生态"),
    edge("e-echo-go-alt-gin", "echo-go", "gin", "alternative_to",
         note="Go Web 框架同层：API 风格相近，Echo 开箱中间件更多，Gin 生态与心智更广"),
    edge("e-fiber-go-alt-gin", "fiber-go", "gin", "alternative_to",
         note="Gin 基于标准库 net/http，Fiber 走 fasthttp 换吞吐但牺牲标准库生态兼容"),
    edge("e-fiber-go-alt-echo-go", "fiber-go", "echo-go", "alternative_to",
         note="同为 Gin 之外的 Go 选项：Fiber 换内核求性能，Echo 保持标准库兼容", weight=0.65),
    edge("e-quarkus-alt-spring-boot", "quarkus", "spring-boot", "alternative_to",
         note="Java 服务端：Quarkus 面向容器与原生镜像的冷启/内存，Spring Boot 胜在生态与人才"),
    edge("e-ktor-alt-spring-boot", "ktor", "spring-boot", "alternative_to",
         note="JVM 服务端：Ktor 协程与插件式轻装，Spring Boot 企业组件完备"),
    edge("e-symfony-alt-laravel", "symfony", "laravel", "alternative_to",
         note="PHP 两大框架：Symfony 组件化可单取且约定严格，Laravel 开发体验与全家桶更顺"),
    edge("e-laravel-bo-symfony", "laravel", "symfony", "built_on",
         note="Laravel 的 HTTP、路由与控制台等底层大量取自 Symfony 组件", weight=0.8,
         confidence="verified"),
    edge("e-aspnet-core-alt-spring-boot", "aspnet-core", "spring-boot", "alternative_to",
         note="企业服务端两大栈：.NET 与 JVM，工具链与云生态绑定不同", weight=0.6),
    # ——— 后端：跨叶挂靠语言 ———
    edge("e-flask-bo-python", "flask", "python", "built_on"),
    edge("e-litestar-bo-python", "litestar", "python", "built_on"),
    edge("e-koa-bo-nodejs", "koa", "nodejs", "built_on"),
    edge("e-midway-bo-nodejs", "midway", "nodejs", "built_on"),
    edge("e-echo-go-bo-go", "echo-go", "go", "built_on"),
    edge("e-fiber-go-bo-go", "fiber-go", "go", "built_on"),
    edge("e-quarkus-bo-java", "quarkus", "java", "built_on"),
    edge("e-ktor-bo-kotlin", "ktor", "kotlin", "built_on"),
    edge("e-aspnet-core-bo-csharp", "aspnet-core", "csharp", "built_on"),
    edge("e-symfony-bo-php", "symfony", "php", "built_on"),
    # ——— 跨端：同层横比与国内镜像 ———
    edge("e-taro-alt-uni-app", "taro", "uni-app", "alternative_to",
         note="国内小程序跨端两强：Taro 走 React 语法，uni-app 走 Vue 语法与 DCloud 工具闭环"),
    edge("e-taro-de-react-native", "taro", "react-native", "domestic_equivalent_of",
         note="同为 React 语法跨端，Taro 主战场是各家小程序与 H5，RN 面向原生双端"),
    edge("e-uni-app-de-react-native", "uni-app", "react-native", "domestic_equivalent_of",
         note="国内一码多端方案：uni-app 以小程序为核心并兼顾 App，RN 只做原生双端"),
    edge("e-lynx-alt-react-native", "lynx", "react-native", "alternative_to",
         note="字节双线程架构与自研渲染，对照 RN 新架构；生态成熟度差距明显"),
    edge("e-ionic-cuw-capacitor", "ionic", "capacitor", "commonly_used_with",
         note="同团队产物：Ionic 提供 Web UI 组件，Capacitor 负责原生打包与插件桥", weight=0.85,
         confidence="verified"),
    edge("e-ionic-alt-react-native", "ionic", "react-native", "alternative_to",
         note="WebView 渲染的混合方案 vs 原生控件渲染，性能与开发心智取舍不同"),
    edge("e-compose-multiplatform-po-kotlin-multiplatform", "compose-multiplatform",
         "kotlin-multiplatform", "part_of",
         note="Compose Multiplatform 是 KMP 之上的共享 UI 层，先有共享逻辑再谈共享界面",
         weight=0.85, confidence="verified"),
    edge("e-compose-multiplatform-alt-flutter", "compose-multiplatform", "flutter",
         "alternative_to",
         note="同为自绘跨端 UI：Kotlin/Compose 栈 vs Dart/Flutter 栈，iOS 成熟度尚有差距"),
    edge("e-kotlin-multiplatform-alt-flutter", "kotlin-multiplatform", "flutter",
         "alternative_to",
         note="共享逻辑保留原生 UI vs 连界面一起共享，取舍在原生体验与复用率", weight=0.6),
    edge("e-dotnet-maui-alt-flutter", "dotnet-maui", "flutter", "alternative_to",
         note=".NET 栈映射原生控件 vs Dart 自绘引擎，生态规模差距明显"),
    edge("e-nativescript-alt-react-native", "nativescript", "react-native", "alternative_to",
         note="同为 JS 直调原生：NativeScript 不绑 React，但社区与插件规模小得多"),
    edge("e-wails-alt-tauri", "wails", "tauri", "alternative_to",
         note="同为系统 WebView + 原生后端的轻量桌面壳：后端语言 Go vs Rust"),
    edge("e-wails-alt-electron", "wails", "electron", "alternative_to",
         note="系统 WebView 换取小体积 vs 自带 Chromium 换取渲染一致性", weight=0.65),
    edge("e-flet-bo-flutter", "flet", "flutter", "built_on",
         note="Flet 界面最终由 Flutter 渲染，用 Python 描述控件树", weight=0.85,
         confidence="verified"),
    # ——— 跨端：跨叶挂靠语言 ———
    edge("e-taro-bo-react", "taro", "react", "built_on"),
    edge("e-uni-app-bo-vue", "uni-app", "vue", "built_on"),
    edge("e-kotlin-multiplatform-bo-kotlin", "kotlin-multiplatform", "kotlin", "built_on"),
    edge("e-dotnet-maui-bo-csharp", "dotnet-maui", "csharp", "built_on"),
    edge("e-wails-bo-go", "wails", "go", "built_on"),
    edge("e-flet-bo-python", "flet", "python", "built_on"),
    # ——— 文档站：同层横比 ———
    edge("e-vitepress-alt-docusaurus", "vitepress", "docusaurus", "alternative_to",
         note="VitePress 启动快、主题克制；Docusaurus 内建版本化与多语，适合长期维护的大站"),
    edge("e-mkdocs-alt-docusaurus", "mkdocs", "docusaurus", "alternative_to",
         note="Python/YAML 极简栈 vs React/MDX 可组件化，取决于是否愿引入 Node 工具链"),
    edge("e-fumadocs-alt-nextra", "fumadocs", "nextra", "alternative_to",
         note="同在 Next.js 上做文档：Fumadocs 分层可替换、组件更新，Nextra 约定更成熟"),
    edge("e-starlight-alt-docusaurus", "starlight", "docusaurus", "alternative_to",
         note="岛屿架构近零 JS 且不绑前端框架 vs React 生态与内建版本化"),
    edge("e-hexo-alt-hugo", "hexo", "hugo", "alternative_to",
         note="Node 生态与厚重中文主题 vs Go 单二进制与极快构建，均偏博客/内容站"),
    edge("e-mintlify-alt-gitbook", "mintlify", "gitbook", "alternative_to",
         note="托管文档两类：Mintlify 偏开发者与 API 文档，GitBook 偏协作写作与权限"),
    edge("e-docusaurus-osa-mintlify", "docusaurus", "mintlify", "open_source_alternative_to",
         note="自建开源文档站替代托管 SaaS：省订阅费但需自担构建、搜索与运维"),
    edge("e-mkdocs-osa-gitbook", "mkdocs", "gitbook", "open_source_alternative_to",
         note="自托管极简文档站替代托管协作平台，代价是失去可视化编辑与审阅流"),
    # ——— 文档站：跨叶挂靠底座与部署 ———
    edge("e-docusaurus-bo-react", "docusaurus", "react", "built_on"),
    edge("e-vitepress-bo-vue", "vitepress", "vue", "built_on"),
    edge("e-vitepress-bo-vite", "vitepress", "vite", "built_on",
         note="以 Vite 为构建与开发服务器内核", weight=0.85, confidence="verified"),
    edge("e-nextra-bo-nextjs", "nextra", "nextjs", "built_on",
         note="以 Next.js 文件路由与渲染能力为底座", weight=0.85, confidence="verified"),
    edge("e-fumadocs-bo-nextjs", "fumadocs", "nextjs", "built_on",
         note="同样构建在 Next.js 之上，但内容源与 UI 层可替换", weight=0.85,
         confidence="verified"),
    edge("e-starlight-bo-astro", "starlight", "astro", "built_on",
         note="Astro 官方文档主题，随 Astro 岛屿架构一同演进", weight=0.85,
         confidence="verified"),
    edge("e-mkdocs-bo-python", "mkdocs", "python", "built_on"),
    edge("e-hugo-bo-go", "hugo", "go", "built_on"),
    edge("e-hexo-bo-nodejs", "hexo", "nodejs", "built_on"),
    edge("e-nextra-cuw-vercel", "nextra", "vercel", "commonly_used_with",
         note="Next.js 系文档站在 Vercel 上部署最顺路，也可导出静态托管别处", weight=0.7),
    edge("e-docusaurus-cuw-cloudflare-pages", "docusaurus", "cloudflare-pages",
         "commonly_used_with",
         note="纯静态产物，常托管到 Pages 类平台以获得国内外可访问的 CDN", weight=0.6),
    edge("e-hugo-cuw-cloudflare-pages", "hugo", "cloudflare-pages", "commonly_used_with",
         note="单二进制构建 + 静态托管，是低成本内容站的常见组合", weight=0.6),
]


def check_duplicates() -> None:
    ids = [e["id"] for e in ENTRIES_DATA]
    assert len(ids) == len(set(ids)), "duplicate entry id"
    gids = [g["id"] for g in EDGES_DATA]
    assert len(gids) == len(set(gids)), "duplicate edge id"
    pairs = {}
    for g in EDGES_DATA:
        key = tuple(sorted((g["from"], g["to"])))
        pairs.setdefault(key, []).append(g["type"])
    for key, types in pairs.items():
        if "conflicts_with" in types and "commonly_used_with" in types:
            raise AssertionError(f"conflicting edge semantics: {key}")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--overwrite", action="store_true")
    args = ap.parse_args()

    check_duplicates()

    ENTRIES.mkdir(parents=True, exist_ok=True)
    VENDORS.mkdir(parents=True, exist_ok=True)
    EDGES.mkdir(parents=True, exist_ok=True)

    wrote_e = wrote_v = wrote_g = 0
    per_cat: dict[str, int] = {}
    for e in ENTRIES_DATA:
        path = ENTRIES / f"{e['id']}.json"
        if path.exists() and not args.overwrite:
            print("skip entry exists", e["id"])
            continue
        save(path, e)
        wrote_e += 1
        per_cat[e["category"]] = per_cat.get(e["category"], 0) + 1
        print("entry", e["id"])

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

    print(f"done entries={wrote_e} vendors={wrote_v} edges={wrote_g} per_cat={per_cat}")


if __name__ == "__main__":
    main()
