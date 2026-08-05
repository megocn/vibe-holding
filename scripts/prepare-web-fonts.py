#!/usr/bin/env python3
"""
墨台 Web/桌面壳字体子集化：apps/desktop/public/fonts

母本：apps/desktop/assets/fonts-full/*.woff2
字表：content + apps/desktop + packages + 根文档中的 CJK/ASCII

用法：
  python3 scripts/prepare-web-fonts.py
  # 或更新字表/母本后重建
"""
from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FULL = ROOT / "apps" / "desktop" / "assets" / "fonts-full"
OUT = ROOT / "apps" / "desktop" / "public" / "fonts"
CHAR_FILE = ROOT / "scripts" / ".web-font-subset-chars.txt"

EXTRA = (
    "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    " ·—–‐…“”‘’「」『』【】（）()[]{}.,;:!?！？，。、；：·•@#%/\\'\"`~^_+*=<>|"
    "→←↑↓★☆※○●◎◇◆□■△▲▽▼℃°±×÷√∞≈≠≤≥✓✗"
    "〇零一二三四五六七八九十百千万亿兆"
    "墨台选型知识库凭据关系图谱仪表盘搜索筛选标签分类目录"
    "开源工具模型框架协议许可证版本排行榜更新笔记"
    "桌面客户端登录同步导入导出设置主题浅色深色"
    "隐私安全本地优先非官方无关联无赞助"
    "安装依赖构建部署开发调试文档贡献"
)

FONT_JOBS = [
    "LXGWWenKai-Regular.woff2",
    "LXGWWenKai-Bold.woff2",
    "LXGWZhenKai-Regular.woff2",
]


def collect_chars() -> str:
    chars: set[str] = set(EXTRA)
    roots = [
        ROOT / "content",
        ROOT / "apps" / "desktop" / "src",
        ROOT / "packages",
        ROOT / "README.md",
        ROOT / "CONTRIBUTING.md",
        ROOT / "docs",
    ]
    skip = {"node_modules", "dist", ".git", "fonts-full", "mediapipe"}
    for base in roots:
        if not base.exists():
            continue
        paths = [base] if base.is_file() else base.rglob("*")
        for p in paths:
            if p.is_dir():
                continue
            if p.suffix not in {".json", ".ts", ".tsx", ".css", ".md", ".html", ".yml", ".yaml"}:
                continue
            if any(s in p.parts for s in skip):
                continue
            try:
                text = p.read_text(encoding="utf-8", errors="ignore")
            except OSError:
                continue
            for ch in text:
                o = ord(ch)
                if (
                    0x4E00 <= o <= 0x9FFF
                    or 0x3400 <= o <= 0x4DBF
                    or 0x3000 <= o <= 0x303F
                    or 0xFF00 <= o <= 0xFFEF
                    or (ch.isascii() and ch.isprintable())
                ):
                    chars.add(ch)
    return "".join(sorted(chars, key=ord))


def ensure_pyft() -> list[str]:
    which = shutil.which("pyftsubset")
    if which:
        return [which]
    try:
        import fontTools  # noqa: F401

        return [sys.executable, "-m", "fontTools.subset"]
    except ImportError as e:
        raise SystemExit(
            "[prepare-web-fonts] 需要 fonttools（brew install fonttools 或 pip install fonttools brotli）"
        ) from e


def subset(src: Path, dest: Path, char_file: Path, cmd_prefix: list[str]) -> None:
    cmd = [
        *cmd_prefix,
        str(src),
        f"--text-file={char_file}",
        "--flavor=woff2",
        "--layout-features=*",
        "--notdef-glyph",
        "--notdef-outline",
        "--recommended-glyphs",
        f"--output-file={dest}",
    ]
    print(f"[prepare-web-fonts] subset {src.name}")
    subprocess.run(cmd, check=True)
    print(
        f"  → {dest.relative_to(ROOT)}  {dest.stat().st_size / 1024:.0f} KB"
        f"（母本 {src.stat().st_size / 1024:.0f} KB）"
    )


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)

    # 若无母本，尝试从当前 public 归档大文件
    FULL.mkdir(parents=True, exist_ok=True)
    for name in FONT_JOBS:
        src = FULL / name
        pub = OUT / name
        if not src.exists() and pub.exists() and pub.stat().st_size > 1_500_000:
            shutil.copy2(pub, src)
            print(f"[prepare-web-fonts] 归档母本 {name}")

    if not any((FULL / n).exists() for n in FONT_JOBS):
        if any((OUT / n).exists() for n in FONT_JOBS):
            print("[prepare-web-fonts] 无母本，沿用现有 public/fonts")
            return
        raise SystemExit(f"[prepare-web-fonts] 缺少母本 {FULL}")

    try:
        cmd_prefix = ensure_pyft()
    except SystemExit as e:
        if any((OUT / n).exists() for n in FONT_JOBS):
            print(f"[prepare-web-fonts] 跳过（{e}）")
            return
        raise

    text = collect_chars()
    CHAR_FILE.write_text(text, encoding="utf-8")
    print(f"[prepare-web-fonts] 字表 {len(text)} 字 → {CHAR_FILE.relative_to(ROOT)}")

    maple_src = FULL / "MapleMono-Regular.woff2"
    maple_pub = OUT / "MapleMono-Regular.woff2"
    if maple_src.exists():
        shutil.copy2(maple_src, maple_pub)
    elif not maple_pub.exists() and (OUT / "MapleMono-Regular.woff2").exists():
        pass
    else:
        pub_m = OUT / "MapleMono-Regular.woff2"
        if not pub_m.exists():
            print("[prepare-web-fonts] warn: MapleMono 缺失")

    for name in FONT_JOBS:
        src = FULL / name
        if not src.exists():
            print(f"[prepare-web-fonts] skip 缺母本 {name}")
            continue
        subset(src, OUT / name, CHAR_FILE, cmd_prefix)

    total = sum(p.stat().st_size for p in OUT.glob("*.woff2"))
    print(f"[prepare-web-fonts] public/fonts 合计 {total / 1024 / 1024:.2f} MB")


if __name__ == "__main__":
    main()
