# 内容仓库（content/）

知识条目、关系边、厂商、概念、方案配方与订阅源。与凭据**物理隔离**——此处只放可公开的选型知识。  
本目录与应用代码一并采用 [Apache License 2.0](../LICENSE) 开源。

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
- 维护脚本：`scripts/migrate-category-leaves.py`（结构变更时参考）。

### LLM 粒度约定（B 类）

上下层（不是并列叶类导航）：**产品族 › 选型档位 › 版本**。

| 粒度 | leaf | 例子 | 用途 |
| --- | --- | --- | --- |
| **产品族** | `llm-family` | Claude、GPT、通义千问、Kimi | 上层导航 /「用哪家」；**不挂 Arena** |
| **选型档位** | `llm-line` | Claude Opus、Kimi 旗舰、Qwen-Max | 下层可比 + Arena/定价 |
| **版本** | （不建条目） | Opus 5、K3、V3 | 写在档位的 `currentVersion` + `updates[]` |

档位用 `part_of` 边指向产品族。侧栏/列表按族展开档，**不要**把「产品族」「选型档位」当两个平级叶类点选。错误示例：把 `kimi-k3`（版本）与 `通义千问`（族）和 `Claude Opus`（档）并列同榜。

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
