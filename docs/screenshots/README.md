# README 截图

由本地 `pnpm --filter @vh/desktop dev` 实机抓取，经缩放与 WebP 压缩后用于根目录 README。

**默认展示深色主题**；`themes/` 存放深色 / 浅色对照，用于双主题并排。

| 目录 | 视口 | 主题 | 说明 |
| --- | --- | --- | --- |
| `desktop/` | 1440×900 | 深色 | 桌面主端全功能 |
| `web/` | 1100×720 | 深色 | 浏览器宽屏只读 |
| `mobile/` | 390×844 | 深色 | 窄屏底部 Tab |
| `themes/` | 桌面 + 移动 | 深色 + 浅色 | 首页 / 知识库 / 图谱对照 |
| `arena/` | 1600×1000 | — | 选型擂台：大厅 / 混战 / 终结技 / 战报 |

重抓时可对 `http://localhost:5280` 用 Playwright：设置里切换「深色」「浅色」，按导航分区截图后压缩替换本目录文件。

`arena/` 抓自线上 `https://vibeholding-arena.pages.dev/pixel.html`（擂台本体闭源，不在本仓构建）。用 Playwright + `--use-angle=swiftshader` 走「点将 → 踏入竹林 → 查看完整战报」流程连拍；战斗帧用 `.app-shell` 元素截图去掉上下留白，终结技分镜需在演出瞬间抓取（该帧渲染重，整页截图易超时）。
