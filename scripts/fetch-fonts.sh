#!/usr/bin/env bash
# 拉取桌面端开发用字体到 apps/desktop/public/fonts（woff2）。
# 依赖：curl、unzip、fonttools（pip/brew: fonttools + brotli）
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
OUT="$ROOT/apps/desktop/public/fonts"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

mkdir -p "$OUT"
cd "$TMP"

echo "→ 下载霞鹜文楷 Lite Regular / Medium…"
curl -fsSL -o WenKai-Regular.ttf \
  "https://github.com/lxgw/LxgwWenKai-Lite/releases/download/v1.522/LXGWWenKaiLite-Regular.ttf"
curl -fsSL -o WenKai-Medium.ttf \
  "https://github.com/lxgw/LxgwWenKai-Lite/releases/download/v1.522/LXGWWenKaiLite-Medium.ttf"

echo "→ 下载霞鹜臻楷 GB…"
curl -fsSL -o ZhenKai-Regular.ttf \
  "https://github.com/lxgw/LxgwZhenKai/releases/download/v0.825/LXGWZhenKaiGB-Regular.ttf"

echo "→ 下载 Maple Mono Woff2…"
curl -fsSL -o MapleMono-Woff2.zip \
  "https://github.com/subframe7536/maple-font/releases/download/v7.9/MapleMono-Woff2.zip"
unzip -qo MapleMono-Woff2.zip MapleMono-Regular.ttf.woff2 LICENSE.txt

echo "→ 压缩 CJK → woff2（较慢）…"
fonttools ttLib.woff2 compress -o "$OUT/LXGWWenKai-Regular.woff2" WenKai-Regular.ttf
fonttools ttLib.woff2 compress -o "$OUT/LXGWWenKai-Bold.woff2" WenKai-Medium.ttf
fonttools ttLib.woff2 compress -o "$OUT/LXGWZhenKai-Regular.woff2" ZhenKai-Regular.ttf
cp MapleMono-Regular.ttf.woff2 "$OUT/MapleMono-Regular.woff2"
cp LICENSE.txt "$OUT/MapleMono-LICENSE.txt"

curl -fsSL -o "$OUT/LXGW-OFL.txt" \
  "https://raw.githubusercontent.com/lxgw/LxgwWenKai-Lite/master/OFL.txt" || true

ls -lh "$OUT"/*.woff2
echo "✓ 全量字体已写入 $OUT"

# 归档母本并子集化（Web 部署体积 ~1–2MB，而非 20MB）
FULL="$ROOT/apps/desktop/assets/fonts-full"
mkdir -p "$FULL"
cp "$OUT"/*.woff2 "$FULL/" 2>/dev/null || true
if command -v python3 >/dev/null 2>&1; then
  echo "→ 子集化 Web 用字体…"
  python3 "$ROOT/scripts/prepare-web-fonts.py" || echo "⚠ 子集化失败（可稍后 pnpm gen:fonts:subset）"
fi
echo "✓ 完成（public 应为子集；母本在 assets/fonts-full）"
