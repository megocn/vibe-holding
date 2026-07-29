<p align="center">
  <img src="apps/desktop/public/brand/logo-256.png" width="96" height="96" alt="墨台" />
</p>

<h1 align="center">墨台 · VibeHolding</h1>

<p align="center">
  <strong>AI 时代的选型擂台</strong><br/>
  <span style="color:#8B1A1A">新时代的基建维基百科</span><br/>
  从 Agent 选到支付，对照平替、追踪变局。<br/>
  结构化知识库 · 关系拓扑 · 方案组合 · 情报追踪 · 本地凭据
</p>

<p align="center">
  <a href="https://vibeholding.pages.dev">在线体验</a>
  ·
  <a href="#使用教程">使用教程</a>
  ·
  <a href="docs/使用教程.md">完整教程</a>
  ·
  <a href="#为什么是墨台">产品理念</a>
  ·
  <a href="CONTRIBUTING.md">贡献指南</a>
  ·
  <a href="LICENSE">Apache-2.0</a>
</p>

<p align="center">
  <img alt="license" src="https://img.shields.io/badge/License-Apache%202.0-blue?style=flat-square" />
  <img alt="entries" src="https://img.shields.io/badge/条目-735-8B1A1A?style=flat-square" />
  <img alt="edges" src="https://img.shields.io/badge/关系边-897-2F5D62?style=flat-square" />
  <img alt="vendors" src="https://img.shields.io/badge/厂商-378-5C4033?style=flat-square" />
  <img alt="recipes" src="https://img.shields.io/badge/方案模板-5-6B4F3A?style=flat-square" />
  <img alt="stack" src="https://img.shields.io/badge/TypeScript-Tauri·React·Expo-111?style=flat-square" />
</p>

<p align="center">
  <!-- 仓库：https://github.com/megocn/vibe-holding -->
  <a href="https://vercel.com/new/clone?repository-url=https://github.com/megocn/vibe-holding&project-name=vibe-holding&repository-name=vibe-holding"><img src="https://vercel.com/button" alt="Deploy with Vercel" /></a>
  &nbsp;
  <a href="https://app.netlify.com/start/deploy?repository=https://github.com/megocn/vibe-holding"><img src="https://www.netlify.com/img/deploy/button.svg" alt="Deploy to Netlify" /></a>
  &nbsp;
  <a href="https://deploy.workers.cloudflare.com/?url=https://github.com/megocn/vibe-holding"><img src="https://deploy.workers.cloudflare.com/button" alt="Deploy to Cloudflare" /></a>
</p>

<p align="center">
  <sub>一键部署 Web 只读壳（不含凭据）。构建：<code>pnpm build:web</code> → <code>apps/desktop/dist</code> · 详见 <a href="docs/部署.md">docs/部署.md</a></sub>
</p>

---

## 为什么是墨台

Vibe Coding 让「想做什么」变得前所未有地快 —— 但要把一个想法真正**跑起来、上线、收钱、可维护**，仍要打通一整条基建链路：

Coding Agent → 大模型 → 框架 → 云与部署 → 数据库 / BaaS → 支付 → 分发 → 可观测性 → …

这条链路上的信息却极度碎片化：官网、推文、测评、踩坑帖、国内镜像与出海合规，散落各处；工具几乎每周变价、变能力、变政策；国内外方案割裂；账号与密钥散落在 `.env`、便签与密码箱里。

更致命的是：**只见点，不见网**。现有资源多是 Awesome List 或目录站 —— 看得见单个工具，却看不清替代、依赖、搭配、国内对标与冲突。

**墨台**（读音 *mò tái*）因此而生：

> **墨** = 书写与知识沉淀；**台** = 工作台 / 驾驶舱。  
> 上墨台选栈、对照平替、追踪变局、管好自己的钥。

它不是又一个导航站，而是把碎片组织成**可关联、可对比、可遍历的知识拓扑网络**，并逐步演进为「选型 + 情报 + 本地凭据」一体的个人基建驾驶舱。设计气质走「墨图 · Ink Atlas」—— 宣纸为底、墨为字、朱砂点睛；温润其表，精确其里。

---

## 核心理念

| 原则 | 含义 |
| --- | --- |
| **边驱动选型** | 条目之间的替代 / 常搭配 / 国内对标 / 冲突校验，是一等公民，不只是标签 |
| **国内 ↔ 海外镜像** | 可用性、合规、支付与网络差异被显式建模，而非事后补丁 |
| **分类可比较** | A–V 图廓 section + 可比较 leaf；排行只挂 leaf，避免图标库与组件库同榜 |
| **本地优先** | 公共内容走 Git；个人笔记 / 收藏 / 凭据本地加密，凭据默认不上 Web |
| **键盘优先** | ⌘K 命令面板贯穿浏览、跳转、对比与设置 |
| **可追溯** | 条目与边尽量带来源；情报可复核；过期有复核提醒 |

---

## 你能用它做什么

### 知识库 · 全链路地图

按卷浏览 AI 编码 / 应用开发 / 云与数据 / 运维安全等分区；按地区、定价、成熟度筛选；打开条目看说明、排行、学习资源与关联面板。

### 图谱 · 看见关系

焦点邻域、生态景观、替代族、依赖 DAG、学习路径…… 用边（而非清单）回答：「和谁相关？」「平替是谁？」「国内对标是什么？」

### 方案 · 可落地的航路

出海 SaaS、国内双端 + 微信生态、AI RAG、Cloudflare 零成本出海等分层模板：每一层选什么、为什么、有什么坑、大致成本。

### 对比 · 并观差异

最多四列并排；差异行以赭石淡染标出 —— 定价模型、国内可达、选型一句话、权威榜，一眼分清。

### 情报 · 跟上变局

版本 / 定价 / 政策更新时间线；关注流；待确认草稿队列。让「最近变了什么」不再靠刷时间线碰运气。

### 凭据 · 本地管家（桌面 / CLI）

多账号保险库、空闲锁定、脱敏展示；后续对接系统钥匙串与 CLI 环境注入。与云端 Secrets 错位：你的钥，留在你这台机器上。

---

## 三端掠影

同一套共享核心（`@vh/core`）驱动多端：桌面全功能主端、Web 只读浏览、窄屏 / 移动只读速查。  
下列截图以**深色主题**为主（默认气质：暖墨夜色）；浅色为宣纸日间模式，顶栏一键切换。

### 双主题 · 深色 / 浅色

墨图设计令牌一套两貌：深色偏暖墨、浅色偏宣纸 —— 信息密度与语义色一致，只换底与墨。

<table>
  <tr>
    <td width="50%" align="center">
      <img src="docs/screenshots/themes/home-dark.webp" alt="首页 · 深色" /><br/>
      <em>首页 · 深色</em>
    </td>
    <td width="50%" align="center">
      <img src="docs/screenshots/themes/home-light.webp" alt="首页 · 浅色" /><br/>
      <em>首页 · 浅色</em>
    </td>
  </tr>
  <tr>
    <td width="50%" align="center">
      <img src="docs/screenshots/themes/knowledge-dark.webp" alt="知识库 · 深色" /><br/>
      <em>知识库 · 深色</em>
    </td>
    <td width="50%" align="center">
      <img src="docs/screenshots/themes/knowledge-light.webp" alt="知识库 · 浅色" /><br/>
      <em>知识库 · 浅色</em>
    </td>
  </tr>
  <tr>
    <td width="50%" align="center">
      <img src="docs/screenshots/themes/graph-dark.webp" alt="图谱 · 深色" /><br/>
      <em>图谱 · 深色</em>
    </td>
    <td width="50%" align="center">
      <img src="docs/screenshots/themes/graph-light.webp" alt="图谱 · 浅色" /><br/>
      <em>图谱 · 浅色</em>
    </td>
  </tr>
</table>

<p align="center">
  <img src="docs/screenshots/themes/mobile-home-dark.webp" width="280" alt="移动首页 · 深色" />
  &nbsp;
  <img src="docs/screenshots/themes/mobile-home-light.webp" width="280" alt="移动首页 · 浅色" />
</p>
<p align="center"><em>移动首页 · 深色 / 浅色</em></p>

### 桌面 · Desktop（主端 · 深色）

全功能：知识库 / 图谱 / 方案 / 对比 / 情报 / 凭据（Tauri）/ ⌘K。

<p align="center">
  <img src="docs/screenshots/desktop/01-home.webp" width="100%" alt="桌面 · 首页驾驶舱" /><br/>
  <em>首页 · 续读航线与最近更新</em>
</p>

<p align="center">
  <img src="docs/screenshots/desktop/02-knowledge.webp" width="100%" alt="桌面 · 知识库详情" /><br/>
  <em>知识库 · 三栏浏览与条目详情</em>
</p>

<table>
  <tr>
    <td width="50%"><img src="docs/screenshots/desktop/03-graph.webp" alt="桌面 · 知识图谱" /><br/><em>图谱 · 焦点邻域与关系透镜</em></td>
    <td width="50%"><img src="docs/screenshots/desktop/04-recipes.webp" alt="桌面 · 方案模板" /><br/><em>方案 · 分层组合与选型理由</em></td>
  </tr>
  <tr>
    <td width="50%"><img src="docs/screenshots/desktop/05-intel.webp" alt="桌面 · 情报流" /><br/><em>情报 · 版本 / 定价 / 政策时间线</em></td>
    <td width="50%"><img src="docs/screenshots/desktop/06-compare.webp" alt="桌面 · 并观对比" /><br/><em>对比 · 差异高亮并观</em></td>
  </tr>
</table>

### Web · 浏览器（只读 · 深色）

自托管静态壳，适合随时查阅与分享；默认不含凭据，安全边界清晰。  
在线预览：[vibeholding.pages.dev](https://vibeholding.pages.dev)

<p align="center">
  <img src="docs/screenshots/web/01-home.webp" width="100%" alt="Web · 首页" /><br/>
  <em>Web · 同款驾驶舱，随时打开</em>
</p>

<table>
  <tr>
    <td width="50%"><img src="docs/screenshots/web/02-knowledge.webp" alt="Web · 知识库" /><br/><em>知识库</em></td>
    <td width="50%"><img src="docs/screenshots/web/03-graph.webp" alt="Web · 图谱" /><br/><em>图谱</em></td>
  </tr>
  <tr>
    <td width="50%"><img src="docs/screenshots/web/04-recipes.webp" alt="Web · 方案" /><br/><em>方案</em></td>
    <td width="50%"><img src="docs/screenshots/web/06-compare.webp" alt="Web · 对比" /><br/><em>对比</em></td>
  </tr>
</table>

### 移动 · Mobile（只读速查 · 深色）

窄屏栈式布局 + 底部 Tab：通勤路上查条目、扫更新、看关联。

<p align="center">
  <img src="docs/screenshots/mobile/01-home.webp" width="280" alt="移动 · 首页" />
  &nbsp;
  <img src="docs/screenshots/mobile/02-knowledge.webp" width="280" alt="移动 · 详情" />
  &nbsp;
  <img src="docs/screenshots/mobile/03-graph.webp" width="280" alt="移动 · 图谱" />
</p>

<p align="center">
  <img src="docs/screenshots/mobile/04-recipes.webp" width="280" alt="移动 · 方案" />
  &nbsp;
  <img src="docs/screenshots/mobile/05-intel.webp" width="280" alt="移动 · 情报" />
</p>

---

## 使用教程

不必先读完全部文档。按下面路径，大约五分钟就能把墨台当成日常驾驶舱来用。更细的场景与 FAQ 见 [`docs/使用教程.md`](docs/使用教程.md)。

### 打开墨台

| 方式 | 命令 / 地址 | 说明 |
| --- | --- | --- |
| **在线** | [vibeholding.pages.dev](https://vibeholding.pages.dev) | 只读浏览，免安装 |
| **浏览器本地** | `pnpm --filter @vh/desktop dev` | 无需 Rust，开发与自用皆可 |
| **桌面窗口** | `pnpm --filter @vh/desktop tauri:dev` | 需 [rustup](https://rustup.rs/)；含凭据管家 |

### 界面一览

左侧（或窄屏底部）导航：**首页 → 知识库 → 图谱 → 方案 → 对比 → 情报 → 设置**；桌面另有 **凭据**。  
顶栏搜索或 **⌘K**（Windows / Linux：`Ctrl+K`）可直达分区与任意条目。

| 快捷键 | 作用 |
| --- | --- |
| `⌘K` / `Ctrl+K` | 命令面板 |
| `⌘B` / `Ctrl+B` | 知识库分类抽屉 |
| `⌘\` / `Ctrl+\` | 折叠条目列表 |
| 顶栏 ☀ / ☾ | 深色 ↔ 浅色 |

### 五分钟路径

1. **搜**：`⌘K` 输入 `Cursor` / `Supabase` / `Stripe`，回车打开详情。  
2. **读**：看选型一句话、地区与定价、说明；顺着**关联**跳到平替或常搭配。  
3. **比**：详情或列表点「加入对比」（最多 4 个）→ **对比**页看赭石高亮差异行。  
4. **逛图**：进 **图谱**，设焦点，切换「生态全景 / 替代族 / 依赖 DAG」，调邻域跳数。  
5. **跟新**：详情点「关注更新」→ **情报** 看「我的更新流」；或直接刷「全部更新」。  
6. **选栈**：进 **方案**，打开模板（出海 SaaS、国内双端、RAG…）或 **选型向导** 生成组合。  
7. **管钥**（仅桌面）：**凭据** 设主密码建保险库，按条目挂多账号 —— 主密码无法找回，请牢记。

### 三条常用航路

**从 0 上线**  
方案模板选一条接近的航路 → 对拿不准的层进知识库 / 对比 / 图谱核对 → 存入「我的技术栈」。

**只查一个工具**  
`⌘K` 直达 → 关联面板看平替与国内对标 → 需要时加入对比或关注更新。

**终端里速查**

```bash
pnpm vh search "claude" --limit 8
pnpm vh show cursor
pnpm vh alt supabase          # 替代 / 国内平替
pnpm vh recipe                # 方案模板列表
pnpm vh related nextjs
```

### 请记住

- **Web / 窄屏没有凭据入口** —— 敏感材料只留在桌面与本机。  
- 收藏、笔记、踩坑、关注、我的栈都在**本地**；要贡献公共知识请改 `content/` 并走 PR（见 [`CONTRIBUTING.md`](CONTRIBUTING.md)）。  
- 完整教程、场景拆解与 FAQ：[`docs/使用教程.md`](docs/使用教程.md)。

---

## Roadmap · 渐进展望

我们按里程碑滚动交付，先让作者自己每天用得上，再把能力摊开给社区。

```text
M0 地基 ──●── M1 知识库 MVP ──●── M2 凭据管家 ──◇── M3 图谱·选型·情报 ──◇── M4 多端·同步·登录
           ✅                ✅              🔶                  🔶                    ⬜
```

### 已经站稳的岸（Now）

- ✅ Monorepo / Zod schema / 内容校验 / 设计令牌（墨图 · Ink Atlas）
- ✅ 知识库浏览、搜索、筛选、关联、本地编辑与个性化
- ✅ 图谱多视图、Worker 布局、聚类与沿图选型
- ✅ 方案模板、选型向导、并观对比
- ✅ 情报时间线、关注与草稿确认队列
- ✅ 桌面壳 + 浏览器窄屏适配；内容库 **623 条目 / 755 边 / 22 类全覆盖**

### 正在铺的桥（Next）

- 🔶 凭据：系统钥匙串 + SPEC 级加密（Argon2id / XChaCha20）+ 加密 SQLite
- 🔶 CLI `vh`：凭据切换与环境变量注入
- 🔶 情报：LLM 摘要与更丰富的订阅源
- ⬜ 自建 E2EE 同步服务（零知识，仅存密文）
- ⬜ 独立 Web（Next SSG）与 Expo 移动端只读壳
- ⬜ 快捷登录（deep link / 剪贴板 / 浏览器扩展填充）

### 更远的海平线（Later）

- 内容库正式开源与社区治理（条目 / 边 / Recipe 众包）✓ 代码+内容已 Apache-2.0；治理与审核流程持续完善
- 半自动情报抓取与共现挖 Recipe
- 团队共享「我的技术栈」与冲突校验协作
- 更完整的 dogfooding：用墨台自己的选型数据，反哺墨台本身的栈

细节与任务编号见本地 `docs-internal/开发计划.md`（对内，未随公开仓发布）。

---

## 快速开始（开发）

```bash
pnpm install
pnpm validate                 # 内容仓库 SPEC §6 校验
pnpm gen:content              # 生成前端 content.json
pnpm --filter @vh/desktop dev # 浏览器预览（无需 Rust）
```

日常用法见上文 [使用教程](#使用教程) 与 [`docs/使用教程.md`](docs/使用教程.md)。

桌面原生窗口需本机 [Rust / rustup](https://rustup.rs/)：

```bash
pnpm --filter @vh/desktop tauri:dev
```

Web 部署（详见 [`docs/部署.md`](docs/部署.md)）：

```bash
pnpm build:web
pnpm deploy:pages   # Cloudflare Pages；需已 wrangler login
```

亦可使用 README 顶部的 **Vercel / Netlify / Cloudflare** 一键部署按钮（部署后请确认 SPA 回退与 Node 22）。

更多命令：`pnpm test` · `pnpm typecheck` · `pnpm lint` · `pnpm vh`（CLI）。

### 仓库结构

```text
apps/
  desktop/     桌面主端（Vite + React + Tailwind v4，Tauri 2）
  cli/         vh 命令行
packages/
  core/        @vh/core  schema / loader / search / 图引擎 / crypto
  ui/          @vh/ui    设计令牌 / 字体 / Phosphor 映射
content/       知识内容：entries · edges · recipes · vendors · categories
docs/          对外文档：使用教程 / 部署 / screenshots
docs-internal/ 对内设计（PRD·SPEC·UI·模块·调研；已 gitignore，仅本地）
```

文档入口：[使用教程](docs/使用教程.md) · [部署](docs/部署.md) · [docs 索引](docs/README.md)

---

## 欢迎 PR · 一起把舆图画完

墨台的骨架可以靠一个人搭；**舆图要靠很多人一起画**。

无论你是：

- 补一条踩过坑的条目或一条可靠的关系边  
- 修正过时定价 / 国内可达性 / 学习资源链接  
- 贡献一个可复用的方案模板（Recipe）  
- 改进图谱性能、无障碍或键盘流  
- 帮忙升级凭据加密、CLI、同步或移动壳  
- 润色文档、截图或翻译  

—— 都非常欢迎。

### 怎么参与

1. 阅读 [`CONTRIBUTING.md`](CONTRIBUTING.md) 与 [`content/README.md`](content/README.md)  
2. Fork → 短分支（`content/…` · `feat/…` · `fix/…`）→ 打开 PR  
3. 内容变更请跑通：`pnpm validate` + `pnpm gen:content`  
4. CI 会检查 lint / typecheck / test / 内容校验 / `content.json` 同步  

**我们更看重**：可追溯来源、克制建边、命名规范、以及**绝不把密钥 / 保险库备份带进仓库**。

安全问题请走 [`SECURITY.md`](SECURITY.md)，勿在公开 Issue 贴出密钥。

## 许可

**代码与 `content/` 知识内容**均采用 [Apache License 2.0](LICENSE)。第三方字体等声明见 [NOTICE](NOTICE)。

> 向本仓库提交 Contribution，即按 Apache-2.0 授权（许可证第 5 条）。

---

<p align="center">
  <strong>上墨台，把选型写成可通行的路。</strong><br/>
  <sub>墨台 · VibeHolding · Ink Atlas</sub>
</p>
