<p align="center">
  <img src="apps/desktop/public/brand/logo-256.png" width="96" height="96" alt="墨台" />
</p>

<h1 align="center">墨台 · VibeHolding</h1>

<p align="center">
  <span style="color:#8B1A1A"><strong>新时代的基建维基百科</strong></span><br/>
  <sub>从 Agent 写代码，到上线、收钱、出海 —— 整条链路按同一套图廓选完</sub>
</p>

<p align="center">
  一个开源的 <strong>AI 时代全链路基建选型知识库</strong>，外加用它的桌面 / Web 客户端。<br/>
  <strong>22 卷图廓 · 132 个可比较类 · 1201 条目 · 1717 条关系边</strong>，按「想法 → 上线 → 变现」的真实顺序铺开，而不是按字母堆目录。<br/>
  它记的不只是工具，更是工具<strong>之间</strong>的边：谁能平替谁、国内对标是哪个、哪两个放一起会打架。<br/>
  免注册、免后端，打开即用；API Key 只留在你自己的机器上。
</p>

<p align="center">
  <a href="https://vibeholding.pages.dev">在线体验</a>
  ·
  <a href="#上线路程--av-图廓">A–V 图廓</a>
  ·
  <a href="#墨台是什么">30 秒看懂</a>
  ·
  <a href="#使用教程">使用教程</a>
  ·
  <a href="#为什么是墨台">产品理念</a>
  ·
  <a href="#选型擂台--群英论剑">选型擂台</a>
  ·
  <a href="CONTRIBUTING.md">贡献指南</a>
  ·
  <a href="LICENSE">Apache-2.0</a>
</p>

<p align="center">
  <img alt="license" src="https://img.shields.io/badge/License-Apache%202.0-blue?style=flat-square" />
  <img alt="entries" src="https://img.shields.io/badge/条目-1201-8B1A1A?style=flat-square" />
  <img alt="edges" src="https://img.shields.io/badge/关系边-1717-2F5D62?style=flat-square" />
  <img alt="sections" src="https://img.shields.io/badge/图廓-A–V·22卷-5C4033?style=flat-square" />
  <img alt="vendors" src="https://img.shields.io/badge/厂商-673-5C4033?style=flat-square" />
  <img alt="leaves" src="https://img.shields.io/badge/可比较类-132-5C4033?style=flat-square" />
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

## 上线路程 · A–V 图廓

墨台的主结构不是「又一个工具导航」，而是按真实上线顺序铺开的 **22 卷 section（A–V）**。同类落在同一 **leaf** 上才能比、才能上榜；卷与卷之间靠 **边**（平替 / 国内对标 / 常搭配 / 冲突）连通。

```text
── 写出来 ──────────────────────────────────────────────
A 编码代理与 IDE          Cursor · Claude Code · 补全 / PR Agent
B 大语言模型与多模态      Claude / GPT / Kimi · 选型档位
C 模型接入层              云端网关 · 本地推理
D 编程语言与运行时        TypeScript · Python · Go · Node…
E 应用框架                Next.js · 后端 / 跨端 / 文档站
F UI / 组件库 / 设计系统  组件库 · 原语 · 图标

── 跑起来 ──────────────────────────────────────────────
G 云与部署平台            PaaS · 公有云 · 自托管
H 数据库与数据存储        关系 / NoSQL / 缓存 / 对象 / 数仓 / 图
I 后端即服务与鉴权        BaaS · 纯鉴权
J AI 应用基础设施         Agent 编排 · RAG · 向量 · 评测 · GPU…

── 上线、收钱、长出来 ──────────────────────────────────
K 支付与计费              Stripe · MoR · 订阅与用量
L 应用分发与应用商店      iOS / Android · 扩展 · 小程序
M 开源组件与生态          构建 · 测试 · 状态 / 数据请求
N 可观测性                错误 · 日志 · 可用性 · 平台标准
O CI/CD 与 DevOps         流水线与容器
P 通知与消息              邮件 · 短信 · IM · 实时协同
Q 增长与分析              网站分析 · SEO · 实验 · 生命周期
R 域名 / DNS / CDN / 网络 边缘网络与域名
S 安全与合规              Secrets · 扫描 · 隐私 · 验证码
T 设计与素材              设计工具 · AI 生图/视频 · 字体…
U 协作与项目管理          文档 · CMS · 客服工单
V 出海与本地化            跨境收款 · 主体路径 · i18n · EOR
```

| | 和 Awesome List 差在哪 |
| --- | --- |
| **按上线路程，不是按字母** | 打开就知道「现在该选到哪一层」，而不是先猜关键词 |
| **section + 可比较 leaf** | 图标库不跟组件库同榜；排行、对比只发生在同 leaf 内 |
| **边是一等公民** | 替代、国内对标、常搭配、冲突，全是可遍历的边，不只是标签 |

数量只是结果：当前 **1201 条目 / 1717 边 / 673 厂商 / 132 可比较类 / 5 套方案模板**，覆盖 A–V 全卷。

---

## 墨台是什么

要把一个 Vibe Coding 的想法真正**跑起来、上线、收钱**，你得把上表那条链路挨层选完。而信息散落在官网、推文、测评和踩坑帖里，每周变价变政策，国内外方案还各说各话。

墨台把这条链路做成**有出处、可关联、可对比**的知识库，并配客户端来用它。图谱、方案、对比、情报、凭据，都挂在同一套 A–V 图廓上，而不是平行的一堆功能。

| 你想…… | 打开墨台的 |
| --- | --- |
| 沿着 A–V 逛某一层，查靠不靠谱 / 怎么收费 / 国内能不能用 | **知识库**（图廓 + 条目） |
| 知道它的平替、国内对标、常见搭配 | **图谱**（或详情页关联面板） |
| 从零搭一套栈（出海 SaaS、国内双端、RAG…） | **方案** 模板与选型向导 |
| 把 2–4 个同类候选摊开看差异 | **对比**（同 leaf 才有意义） |
| 跟上「最近谁又变价 / 发版 / 改政策了」 | **情报** |
| 管好一堆 API Key 与账号 | **凭据**（仅桌面，本机加密） |
| 搞明白大模型排行「权重凭什么这么定」 | **[选型擂台](#选型擂台--群英论剑)** —— 挂在 **B 卷**上的可交互解释器 |

三种打开方式，都不用注册、不用后端：在线只读 [vibeholding.pages.dev](https://vibeholding.pages.dev) · 本地浏览器 `pnpm --filter @vh/desktop dev` · 桌面应用 `pnpm --filter @vh/desktop tauri:dev`（需 Rust，含凭据管家）。

<p align="center">
  <img src="docs/screenshots/desktop/02-knowledge.webp" width="100%" alt="墨台 · 知识库与图廓" /><br/>
  <em>知识库 · 左栏即 A–V 图廓，中间条目，右侧详情与关联</em>
</p>

---

## 为什么是墨台

**墨台**（读音 *mò tái*）的名字，说的就是它想成为的东西：

> **墨** = 书写与知识沉淀；**台** = 工作台 / 驾驶舱。  
> 上墨台选栈、对照平替、追踪变局、管好自己的钥。

目标不止是「把碎片查清楚」，而是逐步长成「选型 + 情报 + 本地凭据」一体的个人基建驾驶舱：你在 A–V 哪一层拿不准，就在那一层沿着边走下去。设计气质走「墨图 · Ink Atlas」—— 宣纸为底、墨为字、朱砂点睛；温润其表，精确其里。

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

### 知识库 · 沿图廓选型

左侧是 A–V 图廓，中间是当前 leaf 下的条目，右侧是详情：选型一句话、地区与定价、说明、权威榜、学习资源与关联面板。按地区、定价模型、成熟度筛选；同类 leaf 内可以自信地比。

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

## 选型擂台 · 群英论剑

> 挂在图廓 **B · 大语言模型** 卷上的可交互解释器，不是墨台的主产品定义。  
> **[在线像素论剑](https://vibeholding-arena.pages.dev/pixel.html)** —— 免登录；主站首页「像素论剑」亦指向同一地址。

把知识库里该卷的**权威榜名次、token 单价、流行度**折算成角色属性，让选型档位在水墨像素战场上打一架 —— 打完得到的是一份**每次伤害都能点回榜单出处**的选型战报。

<p align="center">
  <img src="docs/screenshots/arena/arena-lobby.webp" width="100%" alt="选型擂台 · 大厅" /><br/>
  <em>先选擂，再点将 —— 13 张擂台卡、37 位侠客，卡面直接摊开八维属性</em>
</p>

**为什么值得做成一场架。** 你看排行榜时大概会想：「WebDev 榜权重 0.20 凭什么？」「贵的是不是就一定好？」这些问题在一张静态榜单上无法回答。擂台把排序公式变成可交互的解释器：

- **规则即权重。** 每个擂台就是一组伤害权重向量 —— 换擂台就是换「哪些榜说了算」。大厅里还能拉 10 条权重滑块**自己造一个擂台**，实时预览「若按此规则，当前排序会变成什么样」，然后把它编成分享码发给别人 —— 把文本榜从 20 拉到 93，Qwen-Max 就越过 Kimi 上了第 3。这一步本身就是产品价值：它让人看见排行榜的权重是可以辩论的选择，而不是天启。
- **价格是内力上限。** 性价比擂给每人 $20 预算，按该档位真实 token 单价扣内力 —— 贵档位放两招就脱力，「贵的是不是更好」自己会有答案。
- **数据缺失会走火入魔。** 榜单覆盖不足的档位在战斗中看得见地虚，把「coverage 惩罚系数」这种抽象概念演出来。

**它怎么映射现实。** 厂商是**宗门**，产品族（Claude / Gemini）是**门派**，选型档位（Opus / Sonnet / K3）才是上场的**侠客**，当前版本是他手里的**兵器**。角色的八维属性全部取自该档位**自己的**榜单快照，不做跨档位聚合 —— 所以战报里每一次伤害都能点回对应的榜单 ID、名次、分数与采集日期。同一个 `seed` 在任何设备重跑，事件序列逐帧一致。

<table>
  <tr>
    <td width="50%"><img src="docs/screenshots/arena/arena-battle.webp" alt="擂台 · 四人混战" /><br/><em>四人混战 · 暴击与血条实时结算</em></td>
    <td width="50%"><img src="docs/screenshots/arena/arena-ultimate.webp" alt="擂台 · 终结技分镜" /><br/><em>终结技分镜「深潜 · 探骊」</em></td>
  </tr>
</table>

<p align="center">
  <img src="docs/screenshots/arena/arena-report.webp" width="100%" alt="擂台 · 战报" /><br/>
  <em>战报：名场面、数据对照、选型结论，以及每一条「可查证出手」背后的榜单与日期</em>
</p>

**能打什么、怎么打。**

| 维度 | 内容 |
| --- | --- |
| 擂台（13 张 + 自造） | 纯能力擂 · 性价比擂 · **同门内战**（Opus / Sonnet / Fable 同场打预算局，回答「我该用哪个档」）· 造物擂 · 工巧擂 · 门派战 · 楚河阵营战 · 疾风擂 · 万象擂 · 中原擂 · 义军擂 · 越级擂 · 守擂车轮战 · **UGC 造擂台** |
| 战斗模式 | **论势**（ATB 站桩，行动条决定出手先后）· **乱斗**（实时走位，射程决定能否打中）· **手势指挥**（摄像头识别挥砍出招，画面只在本机处理、不上传） |
| 产出 | 一份带出处的战报 + 名场面切片；固定声明「换权重即换结论 —— 这不是官方排名」 |

**开源边界。** 擂台的玩法代码、数值表与美术资产**不在本仓库**（`private/`，闭源）；它消费的知识内容 —— 榜单、条目、关系边 —— 全部来自本仓 Apache-2.0 的 `content/`。公开仓里只保留首页入口与 `package.json` 里的几条脚本别名（`arena` / `arena:dev` / `deploy:arena`），克隆本仓不会得到游戏代码，也不影响其余功能。

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

1. **逛图廓**：进 **知识库**，从 A 卷一路看到你此刻卡住的那一层（支付？分发？RAG？）。  
2. **搜**：`⌘K` 输入 `Cursor` / `Supabase` / `Stripe`，回车打开详情。  
3. **读**：看选型一句话、地区与定价、说明；顺着**关联**跳到平替或常搭配。  
4. **比**：详情或列表点「加入对比」（最多 4 个，宜同 leaf）→ **对比**页看赭石高亮差异行。  
5. **逛图**：进 **图谱**，设焦点，切换「生态全景 / 替代族 / 依赖 DAG」，调邻域跳数。  
6. **跟新**：详情点「关注更新」→ **情报** 看「我的更新流」；或直接刷「全部更新」。  
7. **选栈**：进 **方案**，打开模板（出海 SaaS、国内双端、RAG…）或 **选型向导** 生成组合。  
8. **管钥**（仅桌面）：**凭据** 设主密码建保险库 —— 主密码无法找回，请牢记。  
9. **（可选）歇口气**：点「像素论剑」进 [选型擂台](#选型擂台--群英论剑)，用打架搞懂 B 卷榜单权重。

### 三条常用航路

**从 0 上线**  
打开 A–V 图廓或方案模板选一条接近的航路 → 对拿不准的层进知识库 / 对比 / 图谱核对 → 存入「我的技术栈」。

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
- ✅ 桌面壳 + 浏览器窄屏适配；内容库 **A–V 22 卷 / 132 leaf / 1201 条目 / 1717 边**
- ✅ 选型擂台（挂 B 卷）：13 擂台 / 三模式 / 造擂分享码（闭源，[可玩](https://vibeholding-arena.pages.dev/pixel.html)）

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
  <sub>A → V 一整条链路 · 墨台 · VibeHolding · Ink Atlas</sub>
</p>
