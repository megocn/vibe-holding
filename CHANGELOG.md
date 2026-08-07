# Changelog

本文件记录**用户可见**的能力变化与面向贡献者的说明。细粒度 dogfooding / 日更流水见仓库根 [`log.md`](./log.md)（若存在）。版本号与 `package.json` 对齐思路：当前仍为 **0.x** 预发阶段。

数字（条目 / 边）以贡献当时 `content/` 与 `pnpm validate` 为准；勿在文案中虚构 Star 与用户数。

---

## [Unreleased]

### 计划（下版 ≤3 条 · 草案）

1. 凭据管家：系统钥匙串 + 更明确的桌面加密路径（不影响 Web 只读边界）
2. CLI `vh`：凭据切换与环境变量注入（桌面 / 终端场景）
3. 内容治理：社区 PR 审核节奏 + 情报草稿确认体验

---

## [0.1.0] · 2026-08 · 社区门面与内容库公开基线

> 面向「30 秒看懂 + 容易贡献 content」的开源门面整理版。能力主体在此前已陆续落地于 main。

### 用户可见能力

- **知识库**：A–V 图廓（22 section）+ 可比较 leaf；条目详情含选型一句话、地区与定价、说明、权威榜与关联
- **图谱**：焦点邻域 / 替代 / 依赖等关系视图（边为一等公民）
- **方案**：内置方案模板（Recipe，当前 5 套）与选型向导
- **对比**：最多四列并观，差异高亮
- **情报**：更新时间线与关注；feeds 驱动的公共情报源
- **凭据**：仅桌面 / CLI 本机路径（Web 默认不含）
- **多端**：桌面（Tauri）完整能力；Web 静态只读（[vibeholding.pages.dev](https://vibeholding.pages.dev)）；窄屏适配
- **选型擂台**：挂 B 卷的可交互解释器——**玩法代码不在本仓**（`private/`）；消费本仓 `content/` 中的榜与条目。在线：[vibeholding-arena.pages.dev](https://vibeholding-arena.pages.dev/pixel.html)

### 贡献者相关

- 贡献最小路径：[`CONTRIBUTING.md`](./CONTRIBUTING.md) · [`content/README.md`](./content/README.md)
- 校验脚本（根 `package.json`）：`pnpm validate` · `pnpm gen:content` · 可选 `pnpm health`
- Issue 模板：补条目或边 / 信息过期 / Recipe 需求（`.github/ISSUE_TEMPLATE/`）
- 入门任务草稿：[`docs/GOOD_FIRST_ISSUES.md`](./docs/GOOD_FIRST_ISSUES.md)
- GitHub About / Topics 建议：[`docs/开源元数据.md`](./docs/开源元数据.md)
- 许可：代码与 `content/` 均为 **Apache-2.0**

### 已知边界

- 擂台与内部 aqua 流水等在 `private/`，克隆本仓不会得到闭源玩法代码
- 内容数量与排行会持续日更；勿将 README 徽章当作实时精确计数 API

---

## 如何更新本文件

- 用户能感知的功能 / 默认体验 / 贡献流程变更 → 记一条
- 纯内部脚本、未发布私有仓改动 → 优先 `log.md`，不必写入本 Changelog
- Breaking：schema 或 content 字段不兼容时单独加 `### Breaking` 小节
