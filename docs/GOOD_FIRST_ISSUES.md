# Good First Issues · 草稿清单

> 维护者可逐条复制下方 **标题 + 正文** 到 GitHub Issues。  
> 难度均为**入门**（只改 `content/`，不碰应用核心逻辑）。  
> 验收通则：`pnpm validate` 通过；有可复核 `sources`；**无密钥 / 保险库 / 个人数据**；改 content 后 `pnpm gen:content` 并提交生成物。

标签建议：`content` + `good first issue`  
模板：优先选 [补条目或边](../.github/ISSUE_TEMPLATE/entry-or-edge.yml) / [信息过期](../.github/ISSUE_TEMPLATE/stale-info.yml) / [Recipe 需求](../.github/ISSUE_TEMPLATE/recipe-request.yml)

数据快照（仓库内统计，非用户数）：`content/entries` 约 1214 条 · `content/edges` 约 1739 条 · `content/recipes` 5 套 · `content/feeds.json` 约 26 路。缺口以打开目录时为准。

---

## 1. [content] msg-sms：补国内短信短名单轴（候选 Submail / 云片等）

### 背景
叶 `msg-sms` 目前仅 3 条：`twilio`、`aliyun-sms`、`tencent-sms`。海外主轴已有 Twilio，国内仅大厂控制台短信，缺「独立短信 SaaS / 聚合」对比轴。

### 改哪些路径
- 新建 `content/entries/<id>.json`（仅收录**当前仍进 3–8 强短名单**的产品；不达标则开 Issue 说明调研后不进库，勿硬凑）
- 边：`content/edges/` 至少一条 `domestic_equivalent_of`（国内 → twilio）或与阿里云/腾讯云的 `alternative_to`（注意方向约定见 content/README）
- 可选：对应 `content/vendors/<id>.json`

### 验收
- [ ] 符合扩种准入：同叶差异化 oneLiner，descriptionMd 是什么→何时选→注意什么
- [ ] `sources` / `officialUrl` 可点开；`lastReviewed` 为真实核对日
- [ ] `pnpm validate` · `pnpm gen:content` 通过
- [ ] 无密钥

### 难度
入门

---

## 2. [content] msg-sms：补海外第二轴（MessageBird / Vonage / Plivo 择一）

### 背景
同叶海外目前只有 Twilio。若某家仍是 2026 短名单级 CPaaS，可补一条可比较的定价/可达/开发者体验轴。

### 改哪些路径
- `content/entries/<id>.json`
- `content/edges/e-*-alternative-to-twilio.json`（或对称推导规则允许的单方向）
- 勿编造与 Twilio 的份额对比

### 验收
- [ ] 写清与 Twilio 的**差异化轴**（区域覆盖 / 定价模型 / 可编程语音 vs 短信侧重），非品类简介
- [ ] `pnpm validate` · `pnpm gen:content`
- [ ] 有 sources；无密钥

### 难度
入门

---

## 3. [content] design-motion：补 Web 动画库轴（Motion One / anime.js / Theatre.js 择一）

### 背景
叶 `design-motion` 现为 LottieFiles · Rive · GSAP。缺「轻量 timeline / 开源动画 API」轴，便于和 GSAP 对比。

### 改哪些路径
- `content/entries/<id>.json`（`category`: `design-motion`）
- `content/edges/`：`alternative_to` → `gsap` 和/或 `commonly_used_with` → 前端框架条目（需已存在）
- 确认 id 不与 `framer-motion`（在 `ui-composable`）混淆层级

### 验收
- [ ] leaf 正确；不与 React 组件动效叶重复定位时，oneLiner 点明分层
- [ ] `pnpm validate` · `pnpm gen:content`；有 sources

### 难度
入门

---

## 4. [content] collab-help：补国内帮助中心 / 知识库产品轴

### 背景
叶 `collab-help` 现为 Archbee · GitBook · Document360。仓库已有 `yuque` 等协作文档类条目，但**可能不在该 leaf**。需要调研：若语雀/飞书知识库等以「对外帮助中心」定位仍短名单，则入库本叶或建 `domestic_equivalent_of` → `gitbook`。

### 改哪些路径
- 优先：检查 `content/entries/yuque.json` 的 `category` 是否应迁 leaf / 是否另建帮助中心向条目（**禁止**同一产品双 id 水军）
- 新建或改边：`content/edges/*domestic*gitbook*.json` 等
- 更新 `lastReviewed`

### 验收
- [ ] 不重复建条目；边方向符合 domestic / open_source 约定
- [ ] `pnpm validate` · `pnpm gen:content`；有 sources

### 难度
入门（需先搜现有 entries 避免重复）

---

## 5. [content] collab-scheduling：补国内预约 / 会议排程短名单（腾讯会议开放能力等 · 需核实）

### 背景
叶 `collab-scheduling` 仅 Calendly · Cal.com · SavvyCal，全是海外。缺国内「预约链接 / 会议排程」轴；**仅收录仍活跃、可官方文档核对的产品**，不达标则评论关闭并写明原因。

### 改哪些路径
- `content/entries/<id>.json`（`category`: `collab-scheduling`）
- `domestic_equivalent_of` → `calendly` 或 `cal-com`
- 勿把纯 IM 或企业套件硬塞本叶

### 验收
- [ ] 轴清晰（排程 / 公开预订页 / 日历集成）
- [ ] `pnpm validate` · `pnpm gen:content`；有 sources

### 难度
入门

---

## 6. [content] 低度数条目补边：`tolgee` / `checkout-com` / `basecamp` 任选 1–2 条

### 背景
若干条目当前关系度数为 1，图上几乎是死胡同。在不滥建的前提下，各补 1–2 条**真实选型关系**边（平替 / 常搭配 / 开源对标）。

### 改哪些路径
- 只改 `content/edges/<edge-id>.json`（及必要时刷新条目 `lastReviewed`）
- 示例方向（需你核实后落库，勿照抄未核边）：
  - `tolgee` ↔ 已有 `lokalise` / `crowdin` / `phrase` 的 `alternative_to` 或 `open_source_alternative_to`
  - `checkout-com` ↔ `stripe` / `adyen` 等已有支付条目
  - `basecamp` ↔ `linear` / 飞书等协作（仅当真实可平替场景）

### 验收
- [ ] `confidence` 合理；`sources` 尽量有
- [ ] 无重复对称边（见 content/README）
- [ ] `pnpm validate` · `pnpm gen:content`

### 难度
入门

---

## 7. [content] feeds：为热门条目补 RSS/Atom（cursor / figma 等）

### 背景
`content/feeds.json` 目前约 26 路；`nextjs` / `supabase` 等已有，但 **`cursor`、`figma` 等热门条目尚无 feed**（以文件为准）。有助于情报页关注更新。

### 改哪些路径
- 仅 `content/feeds.json`：为**已存在**的 `entryId` 增加稳定的官方 changelog / blog feed URL
- 先浏览器打开 feed 确认仍是合法 Atom/RSS

### 验收
- [ ] URL 可拉到条目；`entryId` 与 `content/entries` 一致
- [ ] `pnpm validate`；若 gen 流水线包含 feeds 则 `pnpm gen:content`
- [ ] 无密钥

### 难度
入门

---

## 8. [content] Recipe：提议「可观测 / 错误追踪极速版」方案模板

### 背景
现有 5 套 recipe（出海 SaaS、国内双端/小程序、RAG、CF 零成本）均偏上线形态，缺少「错误 + 日志 + 产品分析」向的分层模板。

### 改哪些路径
- 新建 `content/recipes/<id>.json`，`layers` 只引用**已有** entry id（如 `sentry`、`posthog`、`openreplay` 等，以仓库实存为准）
- `rationaleMd` / `caveats` / `estimatedCost` 写可核对量级，勿写假账单

### 验收
- [ ] 与现有 5 套差异明确
- [ ] 缺层时先补条目 Issue，勿写幽灵 id
- [ ] `pnpm validate` · `pnpm gen:content`

### 难度
入门（略需选型判断）

---

## 9. [content] global-i18n：补「商业 TMS 国内可达 / 开源自托管」缺口边或条目

### 背景
叶 `global-i18n` 已有 i18next、Crowdin、Lokalise、Phrase、Tolgee 等。常见缺口是：**边**（开源自托管 ↔ 商业 SaaS）写全但 sources 弱，或某短名单工具缺失。先读现有 entries/edges，再选择一：补边 **或** 补一条不重复的产品。

### 改哪些路径
- `content/edges/e-*-open-source-alternative-to-*.json` 和/或
- `content/entries/<id>.json`（确认 id 未占用）

### 验收
- [ ] 开源对标方向：`开源 --open_source_alternative_to--> 商业`（单向）
- [ ] `pnpm validate` · `pnpm gen:content`；有 sources

### 难度
入门

---

## 10. [stale] 抽查并刷新 3 个低度数条目的 lastReviewed 与定价备注

### 背景
下列条目边稀疏、事实易过时：`softgen`、`csm-ai`、`rodin`（设计/云 builder 域）。请打开官网与定价页，修正 `pricing` / `availability` / `oneLiner`，更新 `lastReviewed`。

### 改哪些路径
- `content/entries/softgen.json`
- `content/entries/csm-ai.json`
- `content/entries/rodin.json`
- （可选）若官网改名/停运：标 `maturity` 并写清继任，勿静默删除关联边而不说明

### 验收
- [ ] 每个改动字段有对应 sources 或官网 URL
- [ ] 三个文件 `lastReviewed` 均为本次核对日
- [ ] `pnpm validate` · `pnpm gen:content`；无密钥

### 难度
入门

---

## 维护者 checklist（贴出后）

- [ ] 十条已建成 GitHub Issue，并打上 `good first issue`
- [ ] 仓库 About 勾选 Issues；Discussions 按 [`开源元数据.md`](./开源元数据.md) 决定是否开启
- [ ] README / CONTRIBUTING 链接仍指向本文件
