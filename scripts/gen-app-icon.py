#!/usr/bin/env python3
"""按 Apple macOS 图标网格导出，并给内部图案留出安全边距。

网格（画布 1024）：
  本体 824×824 居中，圆角半径 185.4
内部图案：
  CONTENT 相对 824 的缩放比（默认 0.72），避免贴边

输入：apps/desktop/public/brand/logo-master.png（或满铺 RGB 原稿）
输出：brand 各尺寸 + favicon；圆角透明蒙版已烤进 PNG。

随后：
  pnpm --filter @vh/desktop exec tauri icon public/brand/app-icon-1024.png -o src-tauri/icons
  # 必须清 vibeholding 构建缓存，否则二进制仍嵌旧图
  rm -rf apps/desktop/src-tauri/target/debug/build/vibeholding-*
  rm -f apps/desktop/src-tauri/target/debug/vibeholding
  pnpm --filter @vh/desktop tauri:dev
"""
from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

ROOT = Path(__file__).resolve().parents[1]
OUT_BRAND = ROOT / "apps/desktop/public/brand"
MASTER = OUT_BRAND / "logo-master.png"
FAVICON = ROOT / "apps/desktop/public/favicon.png"

GLYPH = 824 / 1024
RADIUS = 185.4 / 1024
CONTENT = 0.72  # of glyph box
FILL_RGB = (179, 11, 10)


def apple_mask(size: int) -> Image.Image:
    mask = Image.new("L", (size, size), 0)
    d = ImageDraw.Draw(mask)
    g = size * GLYPH
    r = size * RADIUS
    x0 = (size - g) / 2
    y0 = (size - g) / 2
    d.rounded_rectangle([x0, y0, x0 + g - 1, y0 + g - 1], radius=r, fill=255)
    return mask.filter(ImageFilter.GaussianBlur(radius=max(0.5, size / 1024)))


def flatten_rgb(im: Image.Image) -> Image.Image:
    if im.mode == "RGBA":
        bg = Image.new("RGB", im.size, FILL_RGB)
        bg.paste(im, mask=im.split()[3])
        return bg
    return im.convert("RGB")


def compose(size: int, art: Image.Image) -> Image.Image:
    canvas = Image.new("RGB", (size, size), FILL_RGB)
    content = max(1, int(size * GLYPH * CONTENT))
    art_s = art.resize((content, content), Image.Resampling.LANCZOS)
    ox = (size - content) // 2
    oy = (size - content) // 2
    canvas.paste(art_s, (ox, oy))
    r, g, b, _ = canvas.convert("RGBA").split()
    return Image.merge("RGBA", (r, g, b, apple_mask(size)))


def main() -> None:
    if not MASTER.exists():
        raise SystemExit(f"missing master: {MASTER}")
    art = flatten_rgb(Image.open(MASTER))
    # If master already has outer transparent plate, flatten used fill — OK.
    # Prefer treating entire image as full plate art.
    OUT_BRAND.mkdir(parents=True, exist_ok=True)
    master = compose(2048, art)
    master.save(OUT_BRAND / "logo-master.png", "PNG", optimize=True)
    for size, name in (
        (1024, "app-icon-1024.png"),
        (512, "logo-512.png"),
        (256, "logo-256.png"),
        (128, "logo-128.png"),
        (64, "logo-64.png"),
    ):
        path = OUT_BRAND / name
        compose(size, art).save(path, "PNG", optimize=True)
        print(f"wrote {path}")
    compose(64, art).save(FAVICON, "PNG", optimize=True)
    print(f"wrote {FAVICON}")
    print(f"Apple grid glyph={GLYPH:.4f} r={RADIUS:.4f}; content={CONTENT}")


if __name__ == "__main__":
    main()
