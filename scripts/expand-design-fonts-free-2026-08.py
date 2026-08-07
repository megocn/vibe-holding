#!/usr/bin/env python3
"""design-fonts 叶：扩种优秀免费/开源商用字体（2026-08-07）。

轴：
- 开源楷体正文 / 展示（霞鹜文楷、臻楷 · 本项目 UI 体系同系）
- 开源 CJK 宋体（思源宋体）
- 开源标题黑体（得意黑）
- 大厂免费 UI 黑体（MiSans）
- 大厂免费标题美术字（钉钉进步体）
- 开源代码等宽（Maple Mono · 本项目 mono）

已有锚点：思源黑体 · 普惠体 · Google Fonts · Fontshare · Adobe Fonts。

用法:
  python3 scripts/expand-design-fonts-free-2026-08.py
  python3 scripts/expand-design-fonts-free-2026-08.py --overwrite
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ENTRIES = ROOT / "content" / "entries"
VENDORS = ROOT / "content" / "vendors"
EDGES = ROOT / "content" / "edges"
REVIEWED = "2026-08-07"


def save(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def entry(**kw) -> dict:
    e: dict = {
        "pricing": {"model": "open-source"},
        "availability": {
            "chinaAccessible": True,
            "needsCompany": False,
            "needsIcp": False,
            "regions": ["global"],
        },
        "tags": [],
        "maturity": "stable",
        "pitfalls": [],
        "updates": [],
        "rankings": [],
        "sources": [],
        "lastReviewed": REVIEWED,
        "region": "both",
        "category": "design-fonts",
        "subcategory": "cjk-fonts",
    }
    e.update(kw)
    if "officialUrl" in e and not e["sources"]:
        e["sources"] = [e["officialUrl"]]
    if e.get("vendorId") is None:
        e.pop("vendorId", None)
    if e.get("githubUrl") is None:
        e.pop("githubUrl", None)
    return e


def validate_entry(e: dict) -> None:
    assert 20 <= len(e["oneLiner"]) <= 80, (e["id"], len(e["oneLiner"]), e["oneLiner"])
    assert 120 <= len(e["descriptionMd"]) <= 380, (e["id"], len(e["descriptionMd"]))
    assert 1 <= len(e["pitfalls"]) <= 3, e["id"]
    assert 3 <= len(e["tags"]) <= 6, e["id"]
    assert e.get("subcategory"), e["id"]


def edge(
    eid: str,
    frm: str,
    to: str,
    typ: str,
    weight: float = 0.75,
    confidence: str = "community",
) -> dict:
    return {
        "id": eid,
        "from": frm,
        "to": to,
        "type": typ,
        "weight": weight,
        "confidence": confidence,
        "sources": [],
        "createdAt": REVIEWED,
    }


VENDORS_DATA = [
    {
        "id": "lxgw",
        "name": "落霞孤鹜 LXGW",
        "region": "domestic",
        "url": "https://github.com/lxgw",
    },
    {
        "id": "atelier-anchor",
        "name": "atelierAnchor",
        "region": "domestic",
        "url": "https://atelier-anchor.com",
    },
    {
        "id": "subframe7536",
        "name": "subframe7536",
        "region": "domestic",
        "url": "https://github.com/subframe7536",
    },
]

# 钉钉进步体挂 alibaba（与 entries/dingtalk 同源厂商；勿新建 id=dingtalk vendor，会与 entry 冲突）

ENTRIES_DATA = [
    entry(
        id="lxgw-wenkai",
        name="霞鹜文楷",
        vendorId="lxgw",
        oneLiner="OFL 人文楷体 · 屏显长文 · 墨台正文用字",
        officialUrl="https://github.com/lxgw/LxgwWenKai",
        githubUrl="https://github.com/lxgw/LxgwWenKai",
        sources=[
            "https://github.com/lxgw/LxgwWenKai",
            "https://fonts.google.com/specimen/LXGW+WenKai",
        ],
        pricing={"model": "open-source", "notes": "SIL OFL 1.1；禁止单独出售字体文件"},
        maturity="mature",
        tags=["fonts", "cjk", "open-source", "kai", "ofl"],
        pitfalls=[
            "全量 woff2 体积大，Web 须子集化或动态切分，否则首屏成本高。",
            "楷体小字识别弱于黑体；界面建议 ≥13px 并配更宽行距。",
            "衍生字体不可使用保留名称「霞鹜 / LXGW」。",
        ],
        descriptionMd=(
            "霞鹜文楷（LXGW WenKai）基于 Fontworks Klee One 补全的开源中文楷体，"
            "SIL OFL 1.1 可个人与企业自由商用、随应用分发。字形温润偏人文，"
            "适合阅读向正文与「书卷」气质产品，为社区下载量最高的开源汉字楷体之一。\n\n"
            "需要免费可内置的 CJK 楷体正文、或追求纸墨 humanist 气质时优先；"
            "墨台（VibeHolding）设计规范以文楷作 `--font-body`。"
            "可与臻楷配展示标题，与 Maple Mono 配代码列。\n\n"
            "全量字库偏重，Web 必须子集/按需加载；楷体不适合过小 UI 字号。"
            "Google Fonts 亦有托管但国内可达与隐私仍可能需自托管。\n"
        ),
    ),
    entry(
        id="lxgw-zhenkai",
        name="霞鹜臻楷",
        vendorId="lxgw",
        oneLiner="文楷加粗屏显优化 · 展示/Hero 用 · 墨台标题",
        officialUrl="https://github.com/lxgw/LxgwZhenKai",
        githubUrl="https://github.com/lxgw/LxgwZhenKai",
        sources=["https://github.com/lxgw/LxgwZhenKai"],
        pricing={"model": "open-source", "notes": "SIL OFL 1.1；衍生自霞鹜文楷"},
        maturity="stable",
        tags=["fonts", "cjk", "open-source", "kai", "display"],
        pitfalls=[
            "字数与维护节奏不及文楷主线；新字/西文以 GB / Slab 通道为准，使用前核当前 Release 说明。",
            "展示用宜大字号；作正文易显「过粗」且字重选择少于文楷家族。",
        ],
        descriptionMd=(
            "霞鹜臻楷（LXGW ZhenKai）是基于霞鹜文楷的加粗屏显优化开源楷体，"
            "手工与 AI 辅助补字，目标让标题与 Hero 在屏幕上更挺拔、笔画不糊。"
            "SIL OFL 1.1，可商用与随包分发。与文楷同属 LXGW 生态但独立仓库与版本线。\n\n"
            "需要「楷体展示标题 + 文楷正文」成套气质、又不想买商用书法体时评估；"
            "墨台规范以臻楷作 `--font-display`。"
            "工程上常与文楷子集一并内置。\n\n"
            "字符覆盖与更新策略以作者 GitHub Release 为准（GB/Slab 等通道分化）；"
            "勿当文楷的简单 Bold 变量替换而不做渲染测试。\n"
        ),
    ),
    entry(
        id="source-han-serif",
        name="思源宋体",
        vendorId="adobe",
        oneLiner="Adobe+Google 开源 CJK 宋体 · Noto Serif CJK",
        officialUrl="https://github.com/adobe-fonts/source-han-serif",
        githubUrl="https://github.com/adobe-fonts/source-han-serif",
        sources=["https://github.com/adobe-fonts/source-han-serif"],
        pricing={"model": "open-source", "notes": "SIL OFL 1.1"},
        maturity="mature",
        tags=["fonts", "cjk", "open-source", "serif", "ofl"],
        pitfalls=[
            "完整多语言字库极大，Web 与客户端须按语言/子集裁切，否则包体失控。",
            "宋体屏上正文可读性格局不同于黑体；小字与 UI 控件仍常见思源/系统黑体。",
        ],
        descriptionMd=(
            "思源宋体（Source Han Serif / Noto Serif CJK）是 Adobe 与 Google 联合开源的"
            "跨中日韩宋体家族，与思源黑体同属 Source Han / Noto CJK 体系，SIL OFL 1.1。"
            "多字重、区域字形（简/繁/日/韩）齐全，出版与文档排版默认开源宋体。\n\n"
            "需要印刷感标题/正文、电子书/文档 PDF 正文字、或与 Noto 西文 serif 对齐的多语产品时优先；"
            "与黑体二选一或分角色配对。\n\n"
            "体积极大，必须子集化与按区加载；嵌入 App 同样要裁字重与字符集。\n"
        ),
    ),
    entry(
        id="smiley-sans",
        name="得意黑",
        vendorId="atelier-anchor",
        oneLiner="OFL 人文几何标题黑 · 海报/品牌短文案出彩",
        officialUrl="https://atelier-anchor.com/typefaces/smiley-sans/",
        githubUrl="https://github.com/atelier-anchor/smiley-sans",
        sources=[
            "https://github.com/atelier-anchor/smiley-sans",
            "https://atelier-anchor.com/typefaces/smiley-sans/",
        ],
        pricing={"model": "open-source", "notes": "SIL OFL 1.1；保留名「Smiley / 得意黑」"},
        maturity="stable",
        tags=["fonts", "cjk", "open-source", "display", "title"],
        pitfalls=[
            "偏标题/海报气质，长文正文与密集 UI 可读性通常不如中性 UI 黑体。",
            "字重/变体少于思源黑体等完整 UI 家族；覆盖以常用简体与拉丁为主。",
        ],
        descriptionMd=(
            "得意黑（Smiley Sans）由 atelierAnchor 发布，在人文手绘感与几何黑体之间找平衡，"
            "窄斜字身、适合标题与短文案的视觉冲击。SIL OFL 1.1，可商用、可改二次发行（须遵守保留名规则）。\n\n"
            "需要一张「有设计感」的中文标题字、又不愿走方正/汉仪付费库时优先；"
            "与普惠体/思源黑体分工：前者作展示标题，后者作界面与长读。\n\n"
            "不宜当作系统级全站 UI 黑体；小字号下细节可能糊，务必在目标端实测。\n"
        ),
    ),
    entry(
        id="misans",
        name="MiSans",
        vendorId="xiaomi",
        region="domestic",
        oneLiner="小米免费商用 UI 黑体 · 多语言/可变字重",
        officialUrl="https://hyperos.mi.com/font/zh/",
        sources=[
            "https://hyperos.mi.com/font/zh/",
            "https://hyperos.mi.com/font/zh/download",
        ],
        pricing={
            "model": "free",
            "notes": "官方 IP 协议免费商用；非 OFL，禁改编分发字体本身",
        },
        maturity="mature",
        availability={
            "chinaAccessible": True,
            "needsCompany": False,
            "needsIcp": False,
            "regions": ["CN", "global"],
        },
        tags=["fonts", "cjk", "free", "ui", "xiaomi"],
        pitfalls=[
            "协议非 OFL：嵌入软件须注明使用 MiSans；不得对字库做外观改编/二次开发后发布。",
            "不得单独再分发/售卖字体文件；须从官方渠道获取最新包与协议全文。",
        ],
        descriptionMd=(
            "MiSans 是小米 HyperOS 体系的屏显中文字体家族，可自官网免费下载并声明面向全社会免费商用。"
            "覆盖多字重、可变字体与 MiSans Global 多书写系统，偏清晰中性 UI 气质，"
            "补齐开源思源体系之外「大厂商用白名单黑体」需求。\n\n"
            "国内 App/运营物料要正版可商用黑体、且倾向手机屏可读规格时评估；"
            "与普惠体同属大厂免费轴，但协议与语言覆盖面不同。\n\n"
            "使用前务必通读当期《MiSans 字体知识产权许可协议》；嵌入分发与二次改字规则明显严于 OFL 字体。\n"
        ),
    ),
    entry(
        id="dingtalk-jinbuti",
        name="钉钉进步体",
        vendorId="alibaba",
        region="domestic",
        subcategory="cjk-fonts",
        oneLiner="钉钉免费商用标题体 · 科技人文 · 官方渠道分发",
        officialUrl="https://page.dingtalk.com/wow/dingtalk/default/dingtalk/y-W5aF3_ZJwzulU0nceIl",
        sources=[
            "https://page.dingtalk.com/wow/dingtalk/default/dingtalk/y-W5aF3_ZJwzulU0nceIl",
        ],
        pricing={
            "model": "free",
            "notes": "永久免费商用（钉钉指定官方渠道）；禁修改与单独转售",
        },
        maturity="stable",
        availability={
            "chinaAccessible": True,
            "needsCompany": False,
            "needsIcp": False,
            "regions": ["CN"],
        },
        tags=["fonts", "cjk", "free", "title", "alibaba"],
        pitfalls=[
            "须从钉钉指定官方渠道下载；未经授权不得上传/转载字体文件本身。",
            "禁修改、反编译与单独定价出售；偏标题/美术字场景，不适合整站 UI 长文。",
        ],
        descriptionMd=(
            "钉钉进步体是钉钉联合字体团队推出的中英标题/美术字型，宣称个人与组织永久免费商用。"
            "气质偏科技活力又带书写温度，字符集覆盖常用场景约七千余字，定位运营标题、海报与品牌短句。\n\n"
            "国内中小团队要「可商用的出彩标题字」且不想买库时评估；"
            "与得意黑同属展示轴——前者大厂协议免费，后者 OFL 开源可改二次发行。\n\n"
            "商用前以钉钉当期法律声明为准；禁止再分发字体包给非授权渠道。\n"
        ),
    ),
    entry(
        id="maple-mono",
        name="Maple Mono",
        vendorId="subframe7536",
        subcategory="mono-fonts",
        oneLiner="OFL 编程等宽 · Nerd Font/连字 · 中英 2:1 · 墨台 mono",
        officialUrl="https://font.subf.dev",
        githubUrl="https://github.com/subframe7536/maple-font",
        sources=[
            "https://github.com/subframe7536/maple-font",
            "https://font.subf.dev",
        ],
        pricing={"model": "open-source", "notes": "SIL OFL 1.1"},
        maturity="stable",
        tags=["fonts", "mono", "open-source", "coding", "ofl"],
        pitfalls=[
            "变体与构建选项多（NF/ligature/hint 等），团队应固定一种构建以免环境不一致。",
            "CJK 等宽打包体积随字形范围增大；非代码区仍应用文楷/黑体，避免整站等宽。",
        ],
        descriptionMd=(
            "Maple Mono 是面向代码与终端的开源等宽字体（SIL OFL 1.1），"
            "提供手写感斜体、细粒度 OpenType 配置、可选 Nerd Font 图标与中英 2:1 等宽思路，"
            "社区下载与二次构建活跃。气质偏温暖，和 LXGW 系人文 UI 同搭自然。\n\n"
            "需要密钥/数值对齐、终端+编辑器一致等宽、且想开源可内置时优先；"
            "墨台规范以 Maple Mono 为 `--font-mono`（回退 JetBrains Mono 等）。\n\n"
            "选构建通道（variable / NF / Normal 预设）时文档先行；勿把连字默认强加给密钥展示场景。\n"
        ),
    ),
]

EDGES_DATA = [
    edge("e-lxgw-zhenkai-built-wenkai", "lxgw-zhenkai", "lxgw-wenkai", "built_on", 0.9, "verified"),
    edge("e-lxgw-wenkai-cuw-zhenkai", "lxgw-wenkai", "lxgw-zhenkai", "commonly_used_with", 0.9),
    edge("e-lxgw-wenkai-cuw-maple-mono", "lxgw-wenkai", "maple-mono", "commonly_used_with", 0.85),
    edge("e-lxgw-wenkai-cuw-google-fonts", "lxgw-wenkai", "google-fonts", "commonly_used_with", 0.7),
    edge(
        "e-source-han-serif-alt-source-han-sans",
        "source-han-serif",
        "source-han-sans",
        "alternative_to",
        0.8,
    ),
    edge(
        "e-source-han-serif-cuw-google-fonts",
        "source-han-serif",
        "google-fonts",
        "commonly_used_with",
        0.7,
    ),
    edge("e-smiley-sans-alt-source-han-sans", "smiley-sans", "source-han-sans", "alternative_to", 0.65),
    edge("e-smiley-sans-alt-alibaba-puhuiti", "smiley-sans", "alibaba-puhuiti", "alternative_to", 0.6),
    edge("e-misans-alt-source-han-sans", "misans", "source-han-sans", "alternative_to", 0.75),
    edge("e-misans-alt-alibaba-puhuiti", "misans", "alibaba-puhuiti", "alternative_to", 0.8),
    edge(
        "e-dingtalk-jinbuti-alt-smiley-sans",
        "dingtalk-jinbuti",
        "smiley-sans",
        "alternative_to",
        0.7,
    ),
]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--overwrite", action="store_true")
    args = ap.parse_args()

    for v in VENDORS_DATA:
        path = VENDORS / f"{v['id']}.json"
        if path.exists() and not args.overwrite:
            print(f"skip vendor {v['id']}")
            continue
        save(path, v)
        print(f"vendor {v['id']}")

    for e in ENTRIES_DATA:
        validate_entry(e)
        path = ENTRIES / f"{e['id']}.json"
        if path.exists() and not args.overwrite:
            print(f"skip entry {e['id']}")
            continue
        save(path, e)
        print(f"entry {e['id']} · oneLiner={len(e['oneLiner'])} desc={len(e['descriptionMd'])}")

    for ed in EDGES_DATA:
        path = EDGES / f"{ed['id']}.json"
        if path.exists() and not args.overwrite:
            print(f"skip edge {ed['id']}")
            continue
        save(path, ed)
        print(f"edge {ed['id']}")


if __name__ == "__main__":
    main()
