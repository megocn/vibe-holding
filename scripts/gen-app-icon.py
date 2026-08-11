#!/usr/bin/env python3
"""从满铺原稿生成 brand 图，并按 Apple macOS 图标网格套透明圆角。

macOS 规格（Apple Developer Forums 常用约定，与 HIG 配套）：
  画布 1024×1024
  本体 824×824 居中（约 80.5%）
  圆角半径 185.4（相对 824 ≈ 22.5%）

dev 态 `tauri:dev` 是裸二进制，Dock 不会像 iOS 那样替你裁；
须把圆角形状画进资源。正式 `.app` 打包同样用这份 icns。

改完后务必清缓存再编，否则二进制仍嵌旧图：
  rm -rf apps/desktop/src-tauri/target/debug/build/vibeholding-*
  rm -f apps/desktop/src-tauri/target/debug/vibeholding
  pnpm --filter @vh/desktop exec tauri icon public/brand/app-icon-1024.png -o src-tauri/icons
  pnpm --filter @vh/desktop tauri:dev
"""
from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

ROOT = Path(__file__).resolve().parents[1]
OUT_BRAND = ROOT / "apps/desktop/public/brand"
MASTER = OUT_BRAND / "logo-master.png"
FAVICON = ROOT / "apps/desktop/public/favicon.png"

# Apple macOS icon template proportions (1024 canvas)
GLYPH = 824 / 1024
RADIUS = 185.4 / 1024
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
        # Expand previous smaller mask to full-bleed by compositing on fill,
        # then scale content so glyph artwork again fills the canvas before re-masking.
        bg = Image.new("RGB", im.size, FILL_RGB)
        bg.paste(im, mask=im.split()[3])
        return bg
    return im.convert("RGB")


def apply_apple_shape(rgb: Image.Image, size: int) -> Image.Image:
    base = rgb.resize((size, size), Image.Resampling.LANCZOS).convert("RGBA")
    r, g, b, _ = base.split()
    return Image.merge("RGBA", (r, g, b, apple_mask(size)))


def main() -> None:
    if not MASTER.exists():
        raise SystemExit(f"missing master: {MASTER}")
    flat = flatten_rgb(Image.open(MASTER))
    # If previous export already had inset margins (mostly fill around edges),
    # trim transparent-looking margins by checking saturation — skip; use full flat.
    OUT_BRAND.mkdir(parents=True, exist_ok=True)
    master = apply_apple_shape(flat, 2048)
    master.save(OUT_BRAND / "logo-master.png", "PNG", optimize=True)
    for size, name in (
        (1024, "app-icon-1024.png"),
        (512, "logo-512.png"),
        (256, "logo-256.png"),
        (128, "logo-128.png"),
        (64, "logo-64.png"),
    ):
        path = OUT_BRAND / name
        apply_apple_shape(flat, size).save(path, "PNG", optimize=True)
        print(f"wrote {path}")
    apply_apple_shape(flat, 64).save(FAVICON, "PNG", optimize=True)
    print(f"wrote {FAVICON}")
    print("Apple grid: glyph=824/1024 corner_r=185.4/1024")


if __name__ == "__main__":
    main()
