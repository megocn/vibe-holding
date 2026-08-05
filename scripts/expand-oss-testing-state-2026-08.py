#!/usr/bin/env python3
"""测试与质量（oss-testing）、状态管理 / 数据请求（oss-state）扩种。

- oss-testing：Pytest / JUnit 5 / Mocha / k6 / Locust / Testcontainers /
  WebdriverIO / Maestro / Detox / Chromatic
- oss-state：Redux Toolkit / Zustand / Jotai / Valtio / MobX / XState /
  Pinia / SWR / Apollo Client / urql

用法:
  python3 scripts/expand-oss-testing-state-2026-08.py
  python3 scripts/expand-oss-testing-state-2026-08.py --overwrite
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
CAT_TEST = "oss-testing"
CAT_STATE = "oss-state"

GLOBAL_OSS = {
    "chinaAccessible": True,
    "needsCompany": False,
    "needsIcp": False,
    "regions": ["global"],
}


def save(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def entry(**kw) -> dict:
    e = {
        "pricing": {"model": "open-source"},
        "availability": dict(GLOBAL_OSS),
        "tags": ["open-source"],
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
    d = e.get("descriptionMd", "")
    assert 160 <= len(d) <= 360, (e["id"], len(d))
    assert 1 <= len(e.get("pitfalls") or []) <= 3, e["id"]
    assert e.get("subcategory"), e["id"]
    assert 3 <= len(e.get("tags") or []) <= 5, e["id"]
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


def mkt(*a, **kw):
    return mk(CAT_TEST, *a, **kw)


def mks(*a, **kw):
    return mk(CAT_STATE, *a, **kw)


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


ENTRIES_DATA: list[dict] = [
    # ———————————————— oss-testing ————————————————
    mkt(
        "pytest",
        "pytest",
        "unit-test",
        "Python 测试事实标准 · 裸 assert+fixture · 插件生态厚",
        "https://docs.pytest.org",
        "pytest 是 Python 生态事实标准的测试框架：用裸 `assert` 写断言、用 fixture 组织依赖与生命周期，参数化与插件（覆盖率、并行、异步、浏览器驱动）覆盖面很广。",
        "Python 服务、脚本或数据管线要写单元与集成测试时的默认起点；标准库 unittest 的用例也能被它直接收集运行，迁移成本低。",
        "fixture 作用域与 conftest 层级容易被滥用成隐式全局状态；插件版本与主版本升级偶有断裂，CI 建议锁定版本。",
        githubUrl="https://github.com/pytest-dev/pytest",
        maturity="mature",
        tags=["test", "python", "open-source", "unit-test"],
    ),
    mkt(
        "junit5",
        "JUnit 5",
        "unit-test",
        "JVM 测试基座 · Jupiter/Platform 分层 · 扩展模型替代 Runner",
        "https://junit.org",
        "JUnit 5 由 Platform、Jupiter、Vintage 三部分组成：Platform 是运行基座，Jupiter 提供新注解与断言，Vintage 兼容跑 JUnit 4 用例。扩展模型（Extension）取代了旧的 Runner/Rule。",
        "JVM 项目的测试底座，Spring Boot、Gradle、Maven 默认与之集成；容器化集成测试常再叠 Testcontainers。",
        "Runner/Rule 写法需改写成 Extension，老仓迁移不是纯升级依赖；模块拆分较细，依赖配错会出现「用例不被发现」。",
        githubUrl="https://github.com/junit-team/junit5",
        maturity="mature",
        tags=["test", "java", "jvm", "open-source"],
    ),
    mkt(
        "mocha",
        "Mocha",
        "unit-test",
        "老牌 Node 测试运行器 · 断言/桩件自选 · 组合而非全家桶",
        "https://mochajs.org",
        "Mocha 只做测试运行与报告，断言（Chai）、桩件（Sinon）、覆盖率（c8/nyc）都由使用者自行拼装，是「组合式」而非全家桶式的 Node 测试框架。",
        "偏好自选组件、或维护历史 Node 服务时仍然合用；新前端项目一般直接选自带断言与 mock 的 Vitest 或 Jest。",
        "开箱能力少，需要自行搭断言与覆盖率；ESM 与 TypeScript 配置比现代运行器繁琐，新项目起步成本偏高。",
        githubUrl="https://github.com/mochajs/mocha",
        maturity="mature",
        tags=["test", "nodejs", "javascript", "open-source"],
    ),
    mkt(
        "k6",
        "Grafana k6",
        "load-test",
        "JS 脚本写压测 · Go 引擎单机高并发 · 阈值即门禁",
        "https://k6.io",
        "k6 用 JavaScript 写压测脚本、由 Go 引擎执行，脚本里声明的 threshold 可直接作为流水线通过与否的门禁，指标能推给 Grafana / Prometheus 做长期观测。",
        "接口与服务端性能回归、容量摸底时使用；已在用 Grafana 观测栈的团队衔接成本最低。",
        "不渲染页面，测不出前端渲染耗时；单机并发受限于压测机资源，大规模需分布式或云端方案。",
        vendorId="grafana-labs",
        githubUrl="https://github.com/grafana/k6",
        tags=["test", "performance", "load-test", "open-source"],
    ),
    mkt(
        "locust",
        "Locust",
        "load-test",
        "Python 写压测行为 · 协程并发 · 自带实时 Web UI",
        "https://locust.io",
        "Locust 用 Python 代码描述用户行为，基于协程驱动并发，自带实时 Web UI 观察并发数与响应分布，支持 master/worker 分布式扩展压力。",
        "团队以 Python 为主、压测逻辑需要复杂分支或复用业务 SDK 时优先；纯接口基准压测用 k6 更轻。",
        "压测机本身可能先于被测服务成为瓶颈；默认 HTTP 客户端性能有限，高压场景需换用更快的客户端实现。",
        githubUrl="https://github.com/locustio/locust",
        tags=["test", "performance", "python", "open-source"],
    ),
    mkt(
        "testcontainers",
        "Testcontainers",
        "integration-test",
        "用真容器跑集成测试 · 用例内起停 · 多语言 SDK",
        "https://testcontainers.com",
        "Testcontainers 在测试代码里按需启动数据库、消息队列等真实依赖容器，用例结束自动回收，用真实中间件替代 mock 与手工维护的共享测试环境。",
        "集成测试要贴近生产依赖行为（SQL 方言、事务、索引）时使用；配合 JUnit 5 或 pytest 作为用例编排层。",
        "依赖本机或 CI 上可用的容器运行时；镜像拉取与启动会显著拉长测试时间，需复用容器并控制粒度。",
        githubUrl="https://github.com/testcontainers",
        tags=["test", "docker", "integration", "open-source"],
    ),
    mkt(
        "webdriverio",
        "WebdriverIO",
        "e2e-test",
        "WebDriver/DevTools 双协议 · Web 与移动端共用一套 · 服务插件多",
        "https://webdriver.io",
        "WebdriverIO 同时支持 W3C WebDriver 与 DevTools 协议，一套 API 覆盖桌面浏览器与 Appium 驱动的移动端，测试服务、报告器与云端设备平台以插件形式接入。",
        "需要真机/云设备矩阵、或 Web 与原生 App 共用一套自动化技术栈时评估；纯 Web E2E 用 Playwright 上手更快。",
        "配置文件与插件体系较重，调试链路比一体化框架长；跨协议行为差异需要在目标环境上实测确认。",
        githubUrl="https://github.com/webdriverio/webdriverio",
        tags=["test", "e2e", "webdriver", "open-source"],
    ),
    mkt(
        "maestro",
        "Maestro",
        "mobile-test",
        "YAML 描述移动端 UI 流 · 内建等待容错 · 跨原生与跨端框架",
        "https://github.com/mobile-dev-inc/Maestro",
        "Maestro 用 YAML 声明移动端 UI 流程，内建对元素加载与动画的等待容错，不要求把探针编译进 App，iOS/Android 原生与 React Native、Flutter 等跨端产物都能驱动。",
        "移动端冒烟与关键路径回归、希望非开发同学也能读懂用例时使用；需要深入 App 内部状态的白盒断言则另选。",
        "YAML 表达力有限，复杂条件与数据构造不便；黑盒驱动拿不到应用内部状态，定位失败原因依赖录屏与日志。",
        vendorId="mobile-dev-inc",
        tags=["test", "mobile", "e2e", "open-source"],
    ),
    mkt(
        "detox",
        "Detox",
        "mobile-test",
        "灰盒移动端 E2E · 与 App 同步等待 · React Native 生态深",
        "https://github.com/wix/Detox",
        "Detox 采用灰盒方式：探针随 App 一起构建，能感知网络请求与动画是否结束再执行下一步，从源头减少移动端 E2E 的随机失败，在 React Native 社区使用最广。",
        "React Native 应用要做稳定的端到端回归、且能接受把测试构建纳入发版流程时选用。",
        "需要为测试单独出构建产物，本地与 CI 环境配置较重；对非 RN 技术栈的适配与文档相对薄弱。",
        vendorId="wix",
        tags=["test", "mobile", "react-native", "open-source"],
    ),
    mkt(
        "chromatic",
        "Chromatic",
        "visual-test",
        "Storybook 官方托管 · 逐 story 视觉快照 · PR 里人工确认差异",
        "https://www.chromatic.com",
        "Chromatic 由 Storybook 团队提供，把每个 story 在云端截图并与基线逐像素比对，差异在 Pull Request 中以待确认状态呈现，同时托管可分享的 Storybook 供设计评审。",
        "组件库或设计系统需要防止视觉回归、并让设计侧参与验收时使用；纯逻辑断言仍由单元测试承担。",
        "按快照数计费，story 与浏览器矩阵一多成本上升明显；动画与随机内容需要冻结，否则误报会淹没真实差异。",
        vendorId="chromatic-com",
        pricing={"model": "freemium", "currency": "USD"},
        tags=["test", "visual", "storybook", "saas"],
    ),
    # ———————————————— oss-state ————————————————
    mks(
        "redux-toolkit",
        "Redux Toolkit",
        "state-management",
        "Redux 官方标准写法 · slice/immer 去样板 · DevTools 时间旅行",
        "https://redux-toolkit.js.org",
        "Redux Toolkit 是 Redux 官方推荐的标准写法：createSlice 收敛 action 与 reducer，内建 Immer 支持「看似可变」的更新，附带 RTK Query 处理服务端数据请求。",
        "多人协作的大型应用、状态变更需要可审计与时间旅行调试时优先；小型应用用它往往显得偏重。",
        "概念与文件层级仍比轻量 store 多；RTK Query 与 TanStack Query 职责重叠，同项目里不建议两套并存。",
        githubUrl="https://github.com/reduxjs/redux-toolkit",
        maturity="mature",
        tags=["state", "react", "redux", "open-source"],
    ),
    mks(
        "zustand",
        "Zustand",
        "state-management",
        "极简 hook store · 无 Provider 包裹 · 选择器订阅控重渲染",
        "https://github.com/pmndrs/zustand",
        "Zustand 用一个 create 函数定义 store，组件通过 hook 加选择器订阅切片，无需 Provider 包裹，也不强制 action/reducer 分层，API 面积非常小。",
        "中小型 React 应用需要跨组件共享客户端状态、又不想引入 Redux 那套约定时优先。",
        "缺乏强制约定，团队大了容易演化出风格各异的 store；选择器写得太粗会带来不必要的重渲染。",
        githubUrl="https://github.com/pmndrs/zustand",
        tags=["state", "react", "hooks", "open-source"],
    ),
    mks(
        "jotai",
        "Jotai",
        "state-management",
        "原子化状态 · 依赖自动派生 · 按原子粒度精确重渲染",
        "https://jotai.org",
        "Jotai 把状态拆成一个个原子，派生原子按依赖自动重算，组件只订阅用到的原子，重渲染范围天然收敛到最小，心智接近 useState 的自然扩展。",
        "状态零散、组件树深、希望避免大 store 引发广播式重渲染时选用；集中式审计与中间件需求更适合 Redux Toolkit。",
        "原子散落各文件后全局状态图不易概览；异步与 Suspense 组合的边界行为需要实测理解。",
        githubUrl="https://github.com/pmndrs/jotai",
        tags=["state", "react", "atomic", "open-source"],
    ),
    mks(
        "valtio",
        "Valtio",
        "state-management",
        "Proxy 可变式写法 · 直接赋值触发更新 · 快照保证渲染一致",
        "https://valtio.dev",
        "Valtio 基于 Proxy 提供可变式状态：直接给属性赋值即触发更新，组件侧通过快照读取以保证渲染一致性，写法上最接近普通 JavaScript 对象操作。",
        "偏好命令式赋值、或从 MobX 一类可变模型迁移到 React 时选用；追求显式不可变更新的团队则不合口味。",
        "隐式追踪让数据流不如显式 action 直观，调试与 code review 更依赖经验；Proxy 对部分特殊对象类型有限制。",
        githubUrl="https://github.com/pmndrs/valtio",
        tags=["state", "react", "proxy", "open-source"],
    ),
    mks(
        "mobx",
        "MobX",
        "state-management",
        "响应式可观察对象 · 依赖自动追踪 · 框架无关且面向对象友好",
        "https://mobx.js.org",
        "MobX 通过可观察对象与自动依赖追踪实现响应式更新：修改数据即精确触发相关视图重算，不依赖 React，也常见于 Angular 或纯 TypeScript 领域模型中。",
        "领域模型复杂、偏好面向对象组织业务状态，或需要在多框架间复用同一份状态逻辑时选用。",
        "自动追踪使更新来源不够显式，大团队排查数据流较费力；装饰器与严格模式配置在不同构建链上差异明显。",
        githubUrl="https://github.com/mobxjs/mobx",
        maturity="mature",
        tags=["state", "reactive", "typescript", "open-source"],
    ),
    mks(
        "xstate",
        "XState",
        "state-machine",
        "状态机/状态图建模 · 非法转移不可达 · 可视化与框架无关",
        "https://xstate.js.org",
        "XState 用有限状态机与状态图描述状态和转移：合法路径写进机器定义，非法转移在结构上不可达；机器可视化查看，核心与框架无关，另有 React、Vue 等绑定。",
        "多步表单、审批流、播放器、连接管理等「状态爆炸」场景，用它替代层层布尔标志位最划算。",
        "状态机概念有学习成本，简单开关状态用它属于杀鸡用牛刀；建模不当会把复杂度从组件搬进机器定义。",
        vendorId="stately",
        githubUrl="https://github.com/statelyai/xstate",
        tags=["state", "state-machine", "typescript", "open-source"],
    ),
    mks(
        "pinia",
        "Pinia",
        "state-management",
        "Vue 官方状态库 · 组合式 API 心智 · 无 mutation 且类型推断好",
        "https://pinia.vuejs.org",
        "Pinia 是 Vue 官方推荐的状态管理库，取消了 Vuex 的 mutation 概念，用组合式 API 的写法定义 store，TypeScript 类型推断与 Devtools 支持都比 Vuex 更完整。",
        "Vue 3 项目需要跨组件共享状态时的默认选择；Vuex 老项目可按 store 逐个迁移过来。",
        "生态与心智绑定 Vue，换框架无法复用；服务端数据的缓存与失效仍建议交给专门的数据请求库。",
        githubUrl="https://github.com/vuejs/pinia",
        tags=["state", "vue", "store", "open-source"],
    ),
    mks(
        "swr",
        "SWR",
        "data-fetching",
        "stale-while-revalidate · API 面积极小 · Next.js 同源顺手",
        "https://swr.vercel.app",
        "SWR 由 Vercel 维护，遵循 stale-while-revalidate 策略：先返回缓存再后台重新校验，核心就是一个 useSWR hook，配置项与概念都刻意保持精简。",
        "读多写少的页面数据、追求极小 API 面积、项目本身就在 Next.js 生态里时选用。",
        "复杂缓存失效、分页与并发变更的能力弱于 TanStack Query；重度数据编排场景后期可能需要换库。",
        vendorId="vercel-inc",
        githubUrl="https://github.com/vercel/swr",
        tags=["data-fetching", "react", "cache", "open-source"],
    ),
    mks(
        "apollo-client",
        "Apollo Client",
        "graphql-client",
        "GraphQL 规范化缓存 · 按实体归一 · 生态齐全但体积偏大",
        "https://www.apollographql.com",
        "Apollo Client 是功能最完整的 GraphQL 客户端：把响应按实体归一化进规范化缓存，一处更新处处生效，并提供本地状态、订阅、开发者工具与代码生成等配套。",
        "GraphQL 查询密集、多视图共享同一批实体、需要成熟工具链与商业支持时选用。",
        "包体积与配置复杂度明显高于轻量客户端；规范化缓存的 key 与更新策略配错时，排查缓存不一致相当耗时。",
        vendorId="apollo-graphql",
        githubUrl="https://github.com/apollographql/apollo-client",
        maturity="mature",
        tags=["graphql", "data-fetching", "cache", "open-source"],
    ),
    mks(
        "urql",
        "urql",
        "graphql-client",
        "轻量 GraphQL 客户端 · 默认文档缓存 · exchange 管道按需拼装",
        "https://github.com/urql-graphql/urql",
        "urql 是轻量 GraphQL 客户端，默认采用简单的文档缓存，功能通过 exchange 管道按需拼装；规范化缓存作为可选包引入，起步体积和概念负担都更小。",
        "GraphQL 用量适中、想避免规范化缓存复杂度、偏好按需扩展的项目选用；重度实体共享场景仍是 Apollo 更稳。",
        "默认文档缓存粒度粗，跨查询更新不会自动同步；exchange 组合顺序理解不对会出现难以复现的缓存行为。",
        githubUrl="https://github.com/urql-graphql/urql",
        tags=["graphql", "data-fetching", "react", "open-source"],
    ),
]

VENDORS_DATA: list[dict] = [
    vendor("grafana-labs", "Grafana Labs", url="https://grafana.com"),
    vendor("mobile-dev-inc", "mobile.dev", url="https://github.com/mobile-dev-inc"),
    vendor("wix", "Wix", url="https://www.wix.com"),
    vendor("chromatic-com", "Chromatic", url="https://www.chromatic.com"),
    vendor("stately", "Stately", url="https://stately.ai"),
    vendor("apollo-graphql", "Apollo GraphQL", url="https://www.apollographql.com"),
]

EDGES_DATA: list[dict] = [
    # ——— oss-testing：语言底座与跨叶挂接 ———
    edge(
        "e-pytest-dep-python",
        "pytest",
        "python",
        "depends_on",
        weight=0.9,
        note="运行在 Python 解释器上，版本支持范围随主版本推进",
    ),
    edge(
        "e-pytest-cw-playwright",
        "pytest",
        "playwright",
        "commonly_used_with",
        weight=0.6,
        note="Playwright 提供 pytest 插件：pytest 负责用例编排，浏览器驱动交给 Playwright",
    ),
    edge(
        "e-junit5-dep-java",
        "junit5",
        "java",
        "depends_on",
        weight=0.9,
        note="JVM 语言测试基座，Kotlin/Scala 亦可复用其 Platform",
    ),
    edge(
        "e-junit5-cw-spring-boot",
        "junit5",
        "spring-boot",
        "commonly_used_with",
        weight=0.8,
        note="spring-boot-starter-test 默认集成 JUnit 5，切片测试按注解裁剪上下文",
    ),
    edge(
        "e-mocha-dep-nodejs",
        "mocha",
        "nodejs",
        "depends_on",
        weight=0.85,
        note="Node 运行器，浏览器端需另行打包运行",
    ),
    edge(
        "e-mocha-alt-jest",
        "mocha",
        "jest",
        "alternative_to",
        note="Mocha 只做运行器需自拼断言与 mock；Jest 是自带快照与 mock 的全家桶",
    ),
    edge(
        "e-mocha-mig-vitest",
        "mocha",
        "vitest",
        "migration_path_to",
        weight=0.6,
        note="Mocha 老仓迁 Vitest 可换掉 ESM/TS 配置负担，断言需从 Chai 改写为内建 expect",
    ),
    # ——— 集成测试 ———
    edge(
        "e-testcontainers-dep-docker",
        "testcontainers",
        "docker",
        "depends_on",
        weight=0.9,
        note="需本机或 CI 上可用的容器运行时，无容器环境则整体不可用",
    ),
    edge(
        "e-testcontainers-cw-junit5",
        "testcontainers",
        "junit5",
        "commonly_used_with",
        weight=0.8,
        note="JUnit 5 编排用例生命周期，Testcontainers 负责起停真实依赖",
    ),
    edge(
        "e-testcontainers-cw-pytest",
        "testcontainers",
        "pytest",
        "commonly_used_with",
        weight=0.65,
        note="Python 侧以 fixture 管理容器生命周期，替代手工维护的共享测试库",
    ),
    # ——— 性能压测 ———
    edge(
        "e-k6-alt-locust",
        "k6",
        "locust",
        "alternative_to",
        note="k6 用 JS 脚本、Go 引擎单机吞吐高；Locust 用 Python 写行为、复杂业务分支更好表达",
    ),
    edge(
        "e-k6-int-grafana",
        "k6",
        "grafana",
        "integrates_with",
        weight=0.8,
        note="同属 Grafana Labs，压测指标可直接推入观测栈做长期对比",
    ),
    edge(
        "e-k6-int-github-actions",
        "k6",
        "github-actions",
        "integrates_with",
        weight=0.65,
        note="脚本内 threshold 未达标即非零退出，可当性能门禁卡流水线",
    ),
    edge(
        "e-locust-dep-python",
        "locust",
        "python",
        "depends_on",
        weight=0.9,
        note="用户行为用 Python 编写，可直接复用业务 SDK",
    ),
    # ——— E2E 与移动端 ———
    edge(
        "e-webdriverio-alt-playwright",
        "webdriverio",
        "playwright",
        "alternative_to",
        note="WebdriverIO 走 WebDriver 协议、能接真机与云设备矩阵；Playwright 自带三引擎与 trace，纯 Web 更快",
    ),
    edge(
        "e-webdriverio-alt-cypress",
        "webdriverio",
        "cypress",
        "alternative_to",
        note="WebdriverIO 覆盖 Web 与原生 App；Cypress 绑定浏览器内运行，调试体验好但跨端不可用",
    ),
    edge(
        "e-maestro-alt-detox",
        "maestro",
        "detox",
        "alternative_to",
        note="Maestro 黑盒跑 YAML 流、无需改构建；Detox 灰盒随 App 打包，等待更稳但要额外产物",
    ),
    edge(
        "e-detox-cw-react-native",
        "detox",
        "react-native",
        "commonly_used_with",
        weight=0.85,
        note="RN 生态最常用的 E2E 方案，探针需编入调试构建",
    ),
    edge(
        "e-maestro-cw-react-native",
        "maestro",
        "react-native",
        "commonly_used_with",
        weight=0.6,
        note="黑盒驱动，RN 与 Flutter 产物都能跑，不要求改动应用代码",
    ),
    edge(
        "e-maestro-cw-flutter",
        "maestro",
        "flutter",
        "commonly_used_with",
        weight=0.55,
        note="跨端产物同样以 UI 元素驱动，用例与技术栈解耦",
    ),
    # ——— 视觉回归 ———
    edge(
        "e-chromatic-dep-storybook",
        "chromatic",
        "storybook",
        "depends_on",
        weight=0.9,
        note="以 story 为快照单元，没有 Storybook 则无从取样",
    ),
    edge(
        "e-chromatic-int-github-actions",
        "chromatic",
        "github-actions",
        "integrates_with",
        weight=0.7,
        note="PR 上以待确认状态回写检查项，差异需人工判定通过",
    ),
    edge(
        "e-chromatic-cw-playwright",
        "chromatic",
        "playwright",
        "commonly_used_with",
        weight=0.5,
        note="组件层视觉快照 vs 跨页面流程断言，覆盖面互补而非二选一",
    ),
    edge(
        "e-chromatic-cw-testing-library",
        "chromatic",
        "testing-library",
        "commonly_used_with",
        weight=0.5,
        note="Testing Library 断言行为，Chromatic 盯像素变化，两者管不同失效",
    ),
    # ——— oss-state：客户端状态取舍 ———
    edge(
        "e-redux-toolkit-alt-zustand",
        "redux-toolkit",
        "zustand",
        "alternative_to",
        weight=0.85,
        note="RTK 有强约定与时间旅行调试、适合多人大仓；Zustand API 极小无 Provider，胜在轻但缺乏统一范式",
    ),
    edge(
        "e-zustand-alt-jotai",
        "zustand",
        "jotai",
        "alternative_to",
        note="Zustand 单一 store 加选择器；Jotai 原子化按依赖派生，重渲染粒度更细但全局图不易概览",
    ),
    edge(
        "e-jotai-alt-valtio",
        "jotai",
        "valtio",
        "alternative_to",
        note="同为 pmndrs 出品：Jotai 不可变原子、显式派生；Valtio 是 Proxy 可变式赋值，写法更命令式",
    ),
    edge(
        "e-mobx-alt-redux-toolkit",
        "mobx",
        "redux-toolkit",
        "alternative_to",
        note="MobX 自动追踪、面向对象领域模型友好；RTK 显式 action 流可审计，排查数据来源更直接",
    ),
    edge(
        "e-valtio-alt-mobx",
        "valtio",
        "mobx",
        "alternative_to",
        weight=0.6,
        note="都是 Proxy 响应式：Valtio 面向 React 且极轻；MobX 概念完整、框架无关但体量大",
    ),
    edge(
        "e-xstate-cw-react",
        "xstate",
        "react",
        "commonly_used_with",
        weight=0.7,
        note="核心与框架无关，React 绑定把机器接进组件；复杂流程用它替代散落的布尔标志",
    ),
    edge(
        "e-xstate-cw-zustand",
        "xstate",
        "zustand",
        "commonly_used_with",
        weight=0.5,
        note="流程状态交给状态机、零散共享数据留在 store；不是同一心智模型，勿直接互替",
    ),
    edge(
        "e-pinia-dep-vue",
        "pinia",
        "vue",
        "depends_on",
        weight=0.9,
        note="Vue 官方推荐状态库，心智与组合式 API 一致",
    ),
    edge(
        "e-zustand-cw-react",
        "zustand",
        "react",
        "commonly_used_with",
        weight=0.8,
        note="以 hook 加选择器订阅，无需 Provider 包裹根组件",
    ),
    edge(
        "e-redux-toolkit-cw-react",
        "redux-toolkit",
        "react",
        "commonly_used_with",
        weight=0.8,
        note="经 react-redux 接入，DevTools 支持时间旅行回放",
    ),
    # ——— 服务端数据请求 ———
    edge(
        "e-swr-alt-tanstack-query",
        "swr",
        "tanstack-query",
        "alternative_to",
        weight=0.85,
        note="SWR 概念少、读多写少页面够用；TanStack Query 在失效编排、分页与乐观更新上更完备，重数据编排选后者",
    ),
    edge(
        "e-swr-cw-nextjs",
        "swr",
        "nextjs",
        "commonly_used_with",
        weight=0.75,
        note="同为 Vercel 维护，常配合 Next.js 客户端侧增量刷新使用",
    ),
    edge(
        "e-apollo-client-alt-urql",
        "apollo-client",
        "urql",
        "alternative_to",
        weight=0.85,
        note="Apollo 默认规范化缓存、工具链全但体积大；urql 默认文档缓存、按 exchange 拼装，起步更轻",
    ),
    edge(
        "e-apollo-client-cw-react",
        "apollo-client",
        "react",
        "commonly_used_with",
        weight=0.75,
        note="以 hook 形式发起查询与订阅，缓存更新即触发相关组件重渲染",
    ),
    edge(
        "e-zustand-cw-tanstack-query",
        "zustand",
        "tanstack-query",
        "commonly_used_with",
        weight=0.7,
        note="服务端状态交给 Query 缓存、纯客户端状态留在 store，两者职责不重叠",
    ),
    edge(
        "e-redux-toolkit-cw-tanstack-query",
        "redux-toolkit",
        "tanstack-query",
        "commonly_used_with",
        weight=0.5,
        note="RTK Query 与 TanStack Query 职责重叠，同项目宜二选一，勿两套缓存并存",
    ),
    edge(
        "e-pinia-cw-tanstack-query",
        "pinia",
        "tanstack-query",
        "commonly_used_with",
        weight=0.6,
        note="Vue 侧常见组合：Pinia 管客户端状态，Query 管服务端缓存与失效",
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
    assert len(ids) == len(set(ids)), "entry id 重复"
    gids = [g["id"] for g in EDGES_DATA]
    assert len(gids) == len(set(gids)), "edge id 重复"

    wrote_e = wrote_v = wrote_g = 0
    skipped_e: list[str] = []
    for e in ENTRIES_DATA:
        path = ENTRIES / f"{e['id']}.json"
        if path.exists() and not args.overwrite:
            skipped_e.append(e["id"])
            continue
        save(path, e)
        wrote_e += 1
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

    if skipped_e:
        print("skip existing entries:", ", ".join(skipped_e))
    print(f"done entries={wrote_e} vendors={wrote_v} edges={wrote_g}")


if __name__ == "__main__":
    main()
