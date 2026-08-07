# 内容仓库（content/）

知识条目、关系边、厂商、概念、方案配方与订阅源。与凭据**物理隔离**——此处只放可公开的选型知识。  
本目录与应用代码一并采用 [Apache License 2.0](../LICENSE) 开源。

## 贡献最小路径（三步）

| 步 | 做啥 |
| --- | --- |
| **1. 改 content** | 一条一文件：`entries/<id>.json` · `edges/<edge-id>.json` · 可选 `recipes/`、`vendors/` 等（见下表） |
| **2. 校验** | 在仓库根：`pnpm validate`（必过）→ `pnpm gen:content`（改 content 后同步生成物并提交） |
| **3. 开 PR** | 说明来源与选型理由；勾 [PR 模板](../.github/pull_request_template.md) 自检。细节见 [CONTRIBUTING](../CONTRIBUTING.md) |

不要把 API Key、主密码、保险库备份写进任何 JSON。扩种前先读下方**扩种准入原则**；新手可领 [`docs/GOOD_FIRST_ISSUES.md`](../docs/GOOD_FIRST_ISSUES.md)。

## 目录

| 路径 | 说明 |
| --- | --- |
| `entries/<id>.json` | **一条一文件**（文件名 = `id`） |
| `edges/<edge-id>.json` | **一条一文件**（文件名 = 边 `id`，如 `e-cursor-powered-claude.json`） |
| `vendors/<id>.json` · `concepts/<id>.json` | **一条一文件**（文件名 = `id`） |
| `recipes/<id>.json` | StackRecipe，一条一文件 |
| `categories.json` | 分类元数据（根级数组） |
| `ranking-systems.json` | 各分类权威排行/标准体系（通常每类 1–2 套） |
| `feeds.json` | 情报 RSS/Atom（`entryId` + `url`） |
| `schema/*.schema.json` | 由 `pnpm gen:schema` 生成的 JSON Schema（编辑器自动补全/校验用，勿手改） |

> **为什么一条一文件**：便于社区并发贡献——每条独立 diff、可逐条 review、`git blame` 可追溯，避免多人改同一巨型数组时的 merge 冲突。构建脚本读取整个目录，单对象或数组文件都兼容。

改完后务必：

```bash
pnpm validate
pnpm gen:content   # 更新桌面端静态包（含预计算检索索引 searchDocs），并一并提交
```

## 编辑器支持（JSON Schema）

VS Code 已通过 `.vscode/settings.json` 的 `json.schemas` 关联 `content/schema/*.schema.json`：编辑 `entries/`、`edges/` 等目录下的 JSON 时自动补全字段、实时校验枚举与必填。

- schema 由 Zod 定义导出，**唯一真相在 `@vh/core`**；schema 变更后运行 `pnpm gen:schema` 重新生成。
- schema 开启了 `additionalProperties: false`，拼错字段名会即时飘红。
- 无需在条目里写 `$schema` 字段（关联走编辑器配置，且写了会被 `additionalProperties: false` 判为多余键）。

## 分类两级（section / leaf）

- **section（A–V）**：图廓导航地图，**不**直接挂条目、**不**挂排行。
- **leaf**：可比较单元（如 `ui-icons` vs `ui-kits`）；`Entry.category` 必须是 leaf id。
- 排行体系的 `categories[]` 挂 leaf；选型向导仍可传 section id（引擎按 section 聚合 leaf）。
- **`usageMd`（仅 leaf）**：用户视角——什么时候用、想干什么、一般怎么弄。语气偏口语短句，非站内可比方法论。选中叶且未点条目时右侧展示。批量：`scripts/enrich-leaf-usage-2026-08.py`。
- 维护脚本：`scripts/migrate-category-leaves.py`（结构变更时参考）。

### LLM 粒度约定（B 类）

上下层（不是并列叶类导航）：**产品族 › 选型档位 › 版本**。

| 粒度 | leaf | 例子 | 用途 |
| --- | --- | --- | --- |
| **产品族** | `llm-family` | Claude、GPT、通义千问、Kimi | 上层导航 /「用哪家」；**不挂 Arena** |
| **选型档位** | `llm-line` | Claude Opus、Kimi 旗舰、Qwen-Max | 下层可比 + Arena/定价 |
| **版本** | （不建条目） | Opus 5、K3、V3 | 写在档位的 `currentVersion` + `updates[]` |

档位用 `part_of` 边指向产品族。侧栏/列表按族展开档，**不要**把「产品族」「选型档位」当两个平级叶类点选。错误示例：把 `kimi-k3`（版本）与 `通义千问`（族）和 `Claude Opus`（档）并列同榜。

#### 产品族排序（榜单优先 · 综合分）

族列表序**不**按名称、**不**用编辑心智图 `llm-family-landscape`。规则摘要：

1. 从下属 `llm-line` 的权威榜快照聚合族实力分 \(S\)（每榜取族内最好一档，不取均值）。
2. **主权重**：Arena Text / WebDev / Agent、AA Index、SWE-bench 等（合计约 82%）；缺榜对有数据的榜重归一化，并加覆盖度惩罚。
3. **辅权**：OpenRouter 热度 · 外部突出度 · 成熟度（合计约 18%）。
4. 完全无榜的族沉底，再按突出度 / 成熟度 / 名称。

公式、权重表与并列规则见对内详设：`docs-internal/modules/01-知识库.md` §2.3（T-KB-10）。维护者只需保证档位 `rankings[]` 与 `part_of` 正确；**勿**为抬族序手写族级 Arena。

## 扩种准入原则（质量优先）

扩种目标是**短名单级、可拿来选型的优质条目**，不是 Awesome List 堆条目。宁缺毋滥。

| 门槛 | 要求 |
| --- | --- |
| **短名单否决** | 只收录同 leaf 里 202x 仍会进 3–8 强对比的工具；轴清晰（开源 vs SaaS、企业 vs Indie、API vs UI 等）。凑数、濒死、纯 SEO 站、过时默认项一律不进。 |
| **最新可复核** | `lastReviewed` 写实；关键事实（官网、许可、计费、主力能力）以**当前官方为准**；核对后再写，禁止凭记忆编造排行、份额、版本。 |
| **最新最优秀** | 优先「当下默认答案 + 各轴最佳」；历史旧王若仍是有效参照可留（如 Hootsuite 企业套件），但 **oneLiner 必须点明今日定位**，不可假扮新锐首选。开源动量星应与经典锚点成对出现。 |
| **写法优质** | `oneLiner` = 同叶可对比特点（· 串点），非品类简介；`descriptionMd` = 是什么 → 何时选 → 注意什么；`pitfalls` 写真实坑；`sources`/`officialUrl` 必填可点开的官方源。 |
| **叶不空、叶不滥** | 新 leaf 至少 3 条且每条有差异化轴；禁止同一产品改名重复、禁止不同可比层捏成一条。 |
| **先源后量** | 先写清对比轴与 3–5 个锚点，再补边；边表达真实选型关系，不为图密度硬连。 |

| **国内外对标** | 新叶与全球赛道扩种须**同步调研国内短名单**（能对标则 `domestic_equivalent_of`）；无短名单级产品时宁缺并在脚本注释写明，禁止硬凑。 |

批量脚本（`scripts/expand-*.py`）必须遵守上表；不达标宁可不落库。

## 条目最小字段

参见 `@vh/core` 的 `Entry` schema / SPEC §5。实用清单：

- `id` · `name` · `category` · `region` · `oneLiner`（≤80 字，选型一句话）
- `descriptionMd` · `officialUrl` · `pricing` · `availability`
- `maturity` · `sources` · `lastReviewed`（YYYY-MM-DD）
- 可选：`currentVersion`、`updates`（含 `release`+`version`）、`pitfalls`、`tags`、`vendorId`、`rankings`、`tutorialLinks`（平台精选/搜索词覆盖；详情页始终展示五大平台）、一等外链（`githubUrl`/`pricingUrl`/`statusUrl`/`consoleUrl`/`playgroundUrl`/`changelogUrl`/`loginUrl`）、`externalLinks`（认知/决策 chip 覆盖）

### `oneLiner` 写作约定

中间条目列表与详情标题下的**选型特点句**：帮助用户在同 leaf 里快速判断「点不点开」。批量脚本：`scripts/enrich-oneliners-2026-07.py`（以手写字典为准，勿再从说明第二段自动截取）。

| 要求 | 说明 |
| --- | --- |
| 篇幅 | **约 20–80 字** |
| 内容 | **同层差异化特点**——能力形态 / 生态绑定 / 约束与锁仓等可对比维度；用「·」串点 |
| 好例子 | `VS Code 系 · Agent/多文件/Rules·MCP；本机 IDE 主力` |
| 坏例子 | `AI 原生代码编辑器`（品类简介）；`适合日常写码的团队…`（适用场景，不是特点） |
| 禁止 | 只重复 `name`；「适合/需要…时优先」受众句；编造排行；把 LLM 产品族与档位混谈 |
| 分工 | 完整论述放 `descriptionMd`；风险短句放 `pitfalls[]` |

### `descriptionMd` 写作约定

详情页「说明」正文；**不要**只是把 `oneLiner` 再写一遍。批量加厚脚本：`scripts/enrich-descriptions-2026-07.py`。

| 要求 | 说明 |
| --- | --- |
| 篇幅 | 约 **120–350 字**（可两三段）；少于 ~80 字视为过薄 |
| 结构 | **是什么** → **何时选 / 栈中位置** → **注意什么**（地区、锁仓、粒度、合规等） |
| 口吻 | 中文、温润精确；可少量加粗关键词；勿感叹号堆砌 |
| 禁止 | 写 Schema 字段名（如 `currentVersion`）；编造不可核对的排行/份额；把 LLM **产品族**与**档位**混为一谈 |
| 分工 | 定价细节放 `pricing.notes`；操作步骤放 `usageGuideMd`；短风险放 `pitfalls[]`；谱系用边 + `LineageBar` |

- **tutorialLinks 维护约定**：可选；`platform` ∈ bilibili/youtube/geekbang/imooc/coursera；有 `url` 则直达，否则用 `query` 或条目名拼搜索页；勿编造不存在的课程页
- **externalLinks / 一等外链约定**：
  - 一等字段（`githubUrl` 等）：有则详情「延伸」chip 直达；热门条目优先补
  - `externalLinks`：可选精选/搜索词覆盖；`kind` ∈ what_is/wiki/github/pricing/status/console/playground/changelog/login/starter/community/spec
  - `what_is`/`wiki` 始终展示（无 url 时 Bing / Wikipedia 搜索，按地区）；其余 kind 无链接则隐藏
  - 精选 `url` 优先于一等字段；勿编造不存在的页面
- **updates 维护约定**：只记有选型意义的大版本与关键事件；P0 热门条目建议 3–5 个 `release` 节点；勿镜像官方完整 changelog；版本若已拆成多 Entry，用边表达谱系，避免双写
- **rankings 维护约定**：引用 `ranking-systems.json` 中的 `systemId`；填 `rank` / `score` / `tier` / `share` 至少一项 + `period` + `asOf`；只记可核对的公开榜快照，勿编造；同条目勿重复同一体系

## 扩种准入原则（质量优先）

扩种不是「把名单填满」。**质量与时效优先于数量**；达不到短名单级的条目宁可不进库。

### 1. 进叶门槛：短名单，不是百科

| 规则 | 说明 |
| --- | --- |
| **可比较单元** | 新条目必须落在某一 **leaf**；若无法在现有 leaf 内与同类硬比，先论证是否需要**新 leaf**，禁止硬塞、禁止跨叶塞凑。 |
| **轴上最优** | 每条应对该 leaf 内某一**选型轴**有明确理由（如：开源自托管标杆 / 企业默认 / DX 最优 / 成本最优 / 国内必达）。**同轴堆第二第三名**无独特差异则不进。 |
| **当年短名单** | 以**当下**（撰写/复核时的日历年）的公开产品、文档、榜单/社区共识为准；已淘汰、停更、被收购后归档、仅靠历史名气撑场的不进或标 `maturity: deprecated` 并说明继任。 |
| **宁缺毋滥** | 一叶 **3–8 条** 常比 15 条稀释信号更好；禁止为「显得覆盖全」而塞长尾测评边缘工具。 |

### 2. 事实与写法：优质可核对

| 规则 | 说明 |
| --- | --- |
| **先核实再落库** | `officialUrl`、许可证、是否仍在维护、定价模型，写前对照官网 / 文档 / GitHub；禁止臆造排行、份额、Star 数。 |
| **oneLiner** | 同叶**差异化特点**（形态 · 约束 · 绑定），不是品类简介、不是「适合 XXX」受众句。 |
| **descriptionMd** | **是什么 → 何时选 → 注意什么**；坑要具体（账单、锁仓、配额、合规），勿空话。 |
| **边** | 每条至少能挂上短名单里的对照边（`alternative_to` / `open_source_alternative_to` / `commonly_used_with`）；无关系的 orphan 不进。 |
| **来源与复核** | `sources` 至少官方；`lastReviewed` 为真实核对日。扩种脚本写完后务必 `pnpm validate` + `pnpm health`。 |

### 3. 禁止项

- 批量 scraped、无差异 oneLiner、互相复制的 `descriptionMd`
- 把「听说过」当入选理由；把过气产品当默认推荐而不写时代语境
- 同一 leaf 内堆 5 个定位几乎相同的二流 SaaS
- 未经验证的「国内神器」口头谣传

### 4. 操作顺序（推荐）

1. 定 leaf 与**选型轴**（本轮要回答哪几类对比问题）  
2. 列当年公开短名单并对轴验收（官网 + 1–2 份近时对比/文档）  
3. 写条目与边 → validate / gen:content / health  
4. 记入 `log.md`；基线有意增长时 `pnpm health --write-baseline`

批次脚本（`scripts/expand-*.py`）只是落地工具：**脚本不能降低门槛**。每一条仍按上表验收。

## 边

- 新增一条边 = 新建一个 `edges/<edge-id>.json`（`id` 建议 `e-<from>-<type简写>-<to>`），**勿再往单个数组文件追加**
- `from` / `to` 必须引用已存在的 entry / concept / vendor id
- `type` 见 SPEC 关系表；对称关系勿重复建反向边（引擎会推导）
- **国内外对标**：只写 `国内 --domestic_equivalent_of--> 国外`（如 `trae → cursor`）；反向「国内平替」由引擎推导，勿手写反向边
- **开源↔商业**：只写 `开源 --open_source_alternative_to--> 商业`；反向「开源平替」由引擎推导
- `weight` ∈ [0,1]；`confidence`：`verified` | `community` | `inferred`
- 尽量填 `sources`；冲突边（`conflicts_with`）需特别谨慎

## 审核期望

维护者会核对：引用完整性、命名、来源、是否与现有边重复/矛盾。批量「 scraped 无来源」条目通常会被要求补来源或拆 PR。

## 本地覆盖 vs 上游

桌面端「编辑 / 情报确认」默认写入**本机覆盖层**，不会自动改 `content/`。要贡献回公共库，请把核对后的 JSON 整理进本目录并发 PR。
