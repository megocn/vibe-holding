# 桌面端 / Web 字体资源

| 文件 | 字族角色 | 说明 |
| --- | --- | --- |
| `LXGWWenKai-Regular.woff2` | 正文 `--font-body` | **UI 字表子集**（~数百 KB） |
| `LXGWWenKai-Bold.woff2` | 正文粗体 `font-weight: 700` | 子集（源为 Lite Medium） |
| `LXGWZhenKai-Regular.woff2` | 展示 `--font-display` | 子集 |
| `MapleMono-Regular.woff2` | 等宽 `--font-mono` | 全量很小，原样 |

全量母本在 `apps/desktop/assets/fonts-full/`（本地，宜 gitignore）。

```bash
# 从上游拉全量 woff2 到 public（慢）
bash scripts/fetch-fonts.sh
# 归档母本（若尚未）并子集化 public（部署用）
mkdir -p apps/desktop/assets/fonts-full
cp apps/desktop/public/fonts/*.woff2 apps/desktop/assets/fonts-full/
python3 scripts/prepare-web-fonts.py
```

或一键：`pnpm gen:fonts`（fetch + subset）。

许可见同目录 `LXGW-OFL.txt`、`MapleMono-LICENSE.txt`（均为 OFL）。
