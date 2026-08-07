# 贡献指南（CONTRIBUTING）

感谢关注 VibeHolding / 墨台。本仓库包含**应用代码**与**知识内容**（`content/`），一并在 **Apache License 2.0** 下开源。凭据与个人数据**永不**进入本仓库。

## 贡献最小路径（只改 content）

> 十次里有九次，你只需要改 JSON 知识库，不必碰应用代码。

| 步 | 做啥 |
| --- | --- |
| **1. 改** | 在 `content/entries/<id>.json` 或 `content/edges/<edge-id>.json` 新增 / 修正一条（规范见 [`content/README.md`](content/README.md)） |
| **2. 校** | 仓库根目录：`pnpm install`（首次）→ **`pnpm validate`** → 改内容时再 **`pnpm gen:content`**，把生成的 `apps/desktop/src/generated/content.json` 一并提交 |
| **3. PR** | 分支名建议 `content/…` → 打开 PR，用默认模板勾自检；来源写进 `sources`，**不要**提交密钥 / 保险库 |

可选：本地浏览器预览 `pnpm --filter @vh/desktop dev`（无需 Rust）。  
报缺口请用 [Issue 模板](.github/ISSUE_TEMPLATE/)；可领任务草稿见 [`docs/GOOD_FIRST_ISSUES.md`](docs/GOOD_FIRST_ISSUES.md)。

## 开发快速开始（含代码）

```bash
pnpm install
pnpm validate          # 内容 SPEC §6 校验（错误阻断）
pnpm test && pnpm typecheck && pnpm lint
pnpm gen:content       # 同步 apps/desktop/src/generated/content.json
pnpm --filter @vh/desktop dev   # 浏览器预览（无需 Rust）
```

更细的内容规范与**扩种准入原则（质量优先）**见 [`content/README.md`](content/README.md)。

## 贡献类型

| 类型 | 路径 | 要求 |
| --- | --- | --- |
| 条目 / 边 / Recipe / feeds | `content/` | `pnpm validate` 通过；改内容后 `pnpm gen:content` 并提交生成物 |
| 核心逻辑 | `packages/core` | 单测 + typecheck |
| 桌面 UI | `apps/desktop` | typecheck + lint；遵循 Ink Atlas 设计规范 |
| 文档（对外） | `docs/` | 使用教程 / 部署 / 截图；与实现一致 |
| 设计稿（对内） | `docs-internal/` | **不进公开仓**；维护者本地保留 PRD/SPEC/UI/模块 |

请用 Issue / PR 模板填写来源与自检清单。CI（`.github/workflows/ci.yml`）会对 PR 跑 lint、typecheck、test、`validate`，并检查 `content.json` 是否与 `content/` 同步。

## 审核原则（维护者）

1. **质量优先**：是否满足 `content/README.md`「扩种准入原则」——短名单级、最新可复核、写法优质；低质凑数 PR 直接要求删或拆。
2. **可追溯**：条目 `sources` / 边 `sources` 尽量有官方或可复核链接。
3. **克制建边**：优先 `verified` / `community`；`inferred` 需说明推导，避免图膨胀。
4. **命名**：ID 小写 kebab-case（见 SPEC 附录 A）。
5. **安全**：拒绝任何 API Key、密码、保险库备份、个人笔记混入 PR。
6. **时效**：更新 `lastReviewed`；过期警告（`E_CONTENT_STALE`）不阻断合并，但新条目应尽量新鲜。

## 分支与提交

- 从 `main` 拉分支：`content/…`、`fix/…`、`feat/…`
- 提交说明简洁写清「为什么」；中英文均可
- 一个 PR 聚焦一类变更（内容与大范围重构分开）

## 行为准则

默认假设善意协作。辱骂、spam、批量低质条目将被关闭。安全问题请私下联系维护者，勿在公开 Issue 贴出密钥。

## 许可

本仓库（含 `apps/`、`packages/`、`content/`、文档等）采用 [Apache License 2.0](LICENSE)。  
向本仓库提交 Contribution，即表示你同意按 Apache-2.0 授权（见许可证第 5 条），并保留署名习惯。第三方字体等见 [NOTICE](NOTICE)。
