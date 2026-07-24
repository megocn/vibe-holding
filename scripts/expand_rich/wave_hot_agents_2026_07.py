#!/usr/bin/env python3
"""热门编码 Agent 补扩：Codex Web、Mistral Vibe、Jules、Devin 等。"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ENTRIES = ROOT / "content" / "entries"
EDGES = ROOT / "content" / "edges" / "seed.json"
VENDORS = ROOT / "content" / "vendors" / "seed.json"
REVIEWED = "2026-07-24"


def entry(**kw):
    e = {
        "pricing": {"model": "freemium"},
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
        "region": "overseas",
    }
    e.update(kw)
    if "officialUrl" in e and not e["sources"]:
        e["sources"] = [e["officialUrl"]]
    if e.get("vendorId") is None:
        e.pop("vendorId", None)
    assert len(e["oneLiner"]) <= 60, (e["id"], e["oneLiner"])
    assert len(e.get("descriptionMd", "")) >= 120, e["id"]
    assert e.get("pitfalls") and e.get("subcategory"), e["id"]
    return e


def edge(eid, frm, to, typ, weight=0.7, confidence="community", note=None):
    e = {
        "id": eid,
        "from": frm,
        "to": to,
        "type": typ,
        "weight": weight,
        "confidence": confidence,
        "sources": [],
        "createdAt": REVIEWED,
    }
    if note:
        e["note"] = note
    return e


def desc(what: str, when: str, caution: str) -> str:
    return f"{what}\n\n{when}\n\n{caution}\n"


ENTRIES_NEW = [
    entry(
        id="codex-web",
        name="Codex Web",
        category="coding-ide-agent",
        subcategory="async-cloud-agent",
        vendorId="openai",
        oneLiner="ChatGPT 侧 Codex 云端异步编码 Agent",
        descriptionMd=desc(
            "**Codex Web**（chatgpt.com/codex）是 OpenAI Codex 产品线的云端异步面：任务在云端沙箱跑，适合过夜并行、跨设备查看进度；与本机 **Codex CLI** 互补而非互替。",
            "当你需要「丢任务后离开本机」、或要在浏览器里管多路 Agent 时选 Web；日常结对改仓仍以 Codex CLI / Cursor 更顺手。",
            "云端仓库权限与密钥注入策略要按最小权限；与 Jules/Devin 同属异步 PR 叙事，对比时看 GitHub 集成深度与账号生态。",
        ),
        officialUrl="https://chatgpt.com/codex",
        docsUrl="https://developers.openai.com/codex/",
        pricing={"model": "subscription", "notes": "随 ChatGPT 套餐；企业另议", "currency": "USD"},
        tags=["codex", "codex-web", "async", "openai", "agent"],
        pitfalls=[
            "依赖云端沙箱与账号区域，国内可达性不稳定",
            "交互不如本地 CLI 即时；复杂调试仍要拉回本机",
        ],
    ),
    entry(
        id="mistral-vibe",
        name="Mistral Vibe",
        category="coding-cli-agent",
        subcategory="cli-agent",
        vendorId="mistral-inc",
        oneLiner="Mistral 编码 Agent · CLI / IDE / Web 一体",
        descriptionMd=desc(
            "**Mistral Vibe**（含 Vibe Code；原 Le Chat 编码能力并入）提供终端 CLI、VS Code/JetBrains 扩展与 Web Code Mode：读仓、改文件、跑命令并开 PR，与 Claude Code / Codex 同层。",
            "适合已在欧洲/ Mistral 生态、或需要 EU 数据驻留叙事的团队；本地 CLI（如 `mistral-vibe` / 官方安装脚本）适合终端优先工作流。",
            "模型与套餐（Free/Pro/Team）决定长任务额度；企业可自托管，但运维与模型更新节奏要单独评估。",
        ),
        officialUrl="https://mistral.ai/products/vibe/code/",
        docsUrl="https://docs.mistral.ai/vibe/code/overview",
        pricing={"model": "freemium", "currency": "EUR"},
        tags=["mistral", "vibe", "cli-agent", "eu", "agent"],
        pitfalls=[
            "品牌从 Le Chat 迁到 Vibe，文档与安装入口可能仍有旧链",
            "相对 Claude Code / Codex，中文社区资料与插件生态更薄",
        ],
        region="overseas",
    ),
    entry(
        id="google-jules",
        name="Jules",
        category="coding-ide-agent",
        subcategory="async-cloud-agent",
        vendorId="google",
        oneLiner="Google 异步编码 Agent · GitHub Issue→PR",
        descriptionMd=desc(
            "**Jules** 是 Google Labs 的异步编码 Agent：绑定 GitHub 仓库，在云端 VM 克隆代码、做计划、改多文件并开 PR，还可接 CI 失败回流修复，偏「后台同事」而非 IDE 结对。",
            "适合 GitHub 工作流成熟、想把修 bug/补测试/小功能丢给异步 Agent 的团队；与 Codex Web、Devin 同属异步象限，和 Cursor/Claude Code 的交互式结对不同。",
            "强绑 GitHub；复杂架构决策仍需人审 PR。额度按 Free/Pro/Ultra 任务数计，注意并发上限。",
        ),
        officialUrl="https://jules.google/",
        pricing={"model": "freemium", "notes": "Free 有日任务上限；Pro/Ultra 提并发与模型档", "currency": "USD"},
        tags=["jules", "google", "async", "github", "agent"],
        pitfalls=[
            "几乎只吃 GitHub 工作流，非 GitHub 主仓不适合",
            "异步交付依赖清晰 Issue/验收标准，提示含糊易出跑偏 PR",
        ],
    ),
    entry(
        id="cognition-devin",
        name="Devin",
        category="coding-ide-agent",
        subcategory="async-cloud-agent",
        vendorId="cognition-inc",
        oneLiner="Cognition 自主软件工程 Agent",
        descriptionMd=desc(
            "**Devin**（Cognition）是早期出圈的自主软件工程 Agent：云端环境里规划、编码、调试并交付，面向「把任务交给 Agent 工程师」而非补全插件。",
            "适合预算充足、愿意接受云端代理工作区与较高单价、要跑多步工程任务的团队；Indie 日常结对通常仍优先 Cursor / Claude Code / Codex CLI。",
            "价格与准入门槛高于大众 CLI；效果随任务清晰度与仓库质量波动大，务必人工审 PR 与权限边界。",
        ),
        officialUrl="https://devin.ai/",
        pricing={"model": "subscription", "notes": "个人/团队价显著高于主流 CLI Agent", "currency": "USD"},
        tags=["devin", "cognition", "async", "agent"],
        pitfalls=[
            "单价高，不适合作为 Indie 默认日常结对工具",
            "自主代理权限面大，生产密钥与合规要单独治理",
        ],
        maturity="beta",
    ),
    entry(
        id="iflycode",
        name="iFlyCode",
        category="coding-ide-agent",
        subcategory="ide-agent",
        region="domestic",
        oneLiner="科大讯飞国内 IDE 编码助手",
        descriptionMd=desc(
            "**iFlyCode** 是科大讯飞面向国内开发者的 AI 编码助手，提供补全、对话改码与 IDE 集成，强调国内可访问与政企场景。",
            "已在讯飞/国内合规采购路径上的团队可评估；与通义灵码、CodeGeeX、Trae 同属国内 IDE Agent 对比池。",
            "模型能力与生态插件相对 Cursor/Claude Code 国际线有差距；选型看网络可达、数据驻留与招标名单，而非只看演示。",
        ),
        officialUrl="https://iflycode.xfyun.cn/",
        pricing={"model": "freemium"},
        tags=["domestic", "ide-agent", "iflytek"],
        pitfalls=["生态与英文开源栈资料少于国际 Agent", "企业版能力与个人版差异大，需按采购包确认"],
    ),
]

VENDORS_NEW = [
    {"id": "cognition-inc", "name": "Cognition", "region": "overseas", "url": "https://cognition.ai"},
]

# mistral-inc / google / openai 多半已存在

EDGES_NEW = [
    edge("e-codex-web-part-codex", "codex-web", "openai-codex", "part_of", 0.85, "verified"),
    edge("e-codex-web-alt-jules", "codex-web", "google-jules", "alternative_to", 0.65),
    edge("e-codex-cli-alt-claude", "openai-codex", "claude-code", "alternative_to", 0.85, "verified"),
    edge("e-codex-cli-alt-gemini-cli", "openai-codex", "gemini-cli", "alternative_to", 0.75),
    edge("e-codex-cli-alt-vibe", "openai-codex", "mistral-vibe", "alternative_to", 0.7),
    edge("e-mistral-vibe-alt-claude", "mistral-vibe", "claude-code", "alternative_to", 0.75),
    edge("e-mistral-vibe-powered", "mistral-vibe", "mistral-large", "powered_by", 0.55, note="旗舰档随产品迭代，以控制台为准"),
    edge("e-jules-alt-devin", "google-jules", "cognition-devin", "alternative_to", 0.7),
    edge("e-jules-alt-codex-web", "google-jules", "codex-web", "alternative_to", 0.7),
    edge("e-jules-powered-gemini", "google-jules", "gemini-pro", "powered_by", 0.6),
    edge("e-devin-alt-codex-web", "cognition-devin", "codex-web", "alternative_to", 0.6),
    edge("e-iflycode-dom-copilot", "iflycode", "github-copilot", "domestic_equivalent_of", 0.55),
    edge("e-iflycode-alt-trae", "iflycode", "trae", "alternative_to", 0.65),
]


def main() -> None:
    vendors = json.loads(VENDORS.read_text(encoding="utf-8"))
    edges = json.loads(EDGES.read_text(encoding="utf-8"))
    entry_ids = {p.stem for p in ENTRIES.glob("*.json")}
    vendor_ids = {v["id"] for v in vendors}
    edge_ids = {e["id"] for e in edges}

    # ensure mistral vendor exists under non-colliding id
    if "mistral-inc" not in vendor_ids and "mistral" in entry_ids:
        vendors.append(
            {"id": "mistral-inc", "name": "Mistral AI", "region": "overseas", "url": "https://mistral.ai"}
        )
        vendor_ids.add("mistral-inc")
    if "google" not in vendor_ids:
        vendors.append({"id": "google", "name": "Google", "region": "overseas", "url": "https://google.com"})
        vendor_ids.add("google")

    added_e = added_v = added_edge = 0
    for e in ENTRIES_NEW:
        path = ENTRIES / f"{e['id']}.json"
        if path.exists():
            print("skip entry", e["id"])
            continue
        # vendor collision guard
        if e.get("vendorId") == e["id"]:
            e["vendorId"] = f"{e['id']}-inc"
        path.write_text(json.dumps(e, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        added_e += 1
        print("wrote", e["id"])

    for v in VENDORS_NEW:
        if v["id"] in vendor_ids or v["id"] in entry_ids:
            continue
        vendors.append(v)
        vendor_ids.add(v["id"])
        added_v += 1

    # drop obsolete edge that pointed openai-codex as ide-only narrative if we add better ones
    # merge edges; skip dups by id and by from|type|to
    seen_triple = {(e["from"], e["type"], e["to"]) for e in edges}
    for ed in EDGES_NEW:
        # skip if ends missing (e.g. mistral-large)
        if ed["from"] not in entry_ids and ed["from"] not in {e["id"] for e in ENTRIES_NEW}:
            # after writes, refresh
            pass
        ends_ok = (ENTRIES / f"{ed['from']}.json").exists() and (ENTRIES / f"{ed['to']}.json").exists()
        if not ends_ok:
            print("skip edge missing ends", ed["id"], ed["from"], ed["to"])
            continue
        triple = (ed["from"], ed["type"], ed["to"])
        if ed["id"] in edge_ids or triple in seen_triple:
            print("skip edge", ed["id"])
            continue
        edges.append(ed)
        edge_ids.add(ed["id"])
        seen_triple.add(triple)
        added_edge += 1

    # Retarget old powered_by gpt-4o if still present — keep; add cli alt edges may dup e-codex-alt-claude-code
    VENDORS.write_text(json.dumps(vendors, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    EDGES.write_text(json.dumps(edges, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"done +entries={added_e} +vendors={added_v} +edges={added_edge} total={len(list(ENTRIES.glob('*.json')))}")


if __name__ == "__main__":
    main()
