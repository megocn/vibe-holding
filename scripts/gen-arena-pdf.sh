#!/usr/bin/env bash
# 生成「选型擂台 · 群英论剑」产品方案 PDF（通俗版）
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
HTML="$ROOT/docs-internal/modules/13-选型擂台-产品方案.html"
PDF="$ROOT/docs-internal/modules/13-选型擂台-产品方案.pdf"

CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
if [[ ! -x "$CHROME" ]]; then
  echo "未找到 Google Chrome，请安装后重试。" >&2
  exit 1
fi

"$CHROME" \
  --headless=new \
  --disable-gpu \
  --no-pdf-header-footer \
  --print-background \
  --virtual-time-budget=10000 \
  --print-to-pdf="$PDF" \
  "file://$HTML"

echo "已生成: $PDF"
