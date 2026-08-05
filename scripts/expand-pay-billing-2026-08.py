#!/usr/bin/env python3
"""订阅与用量计费（pay-billing）扩种。

pay-processor 回答「钱怎么收到」，pay-mor 回答「税谁来担」，这一叶回答的是第三个问题：
「按什么规则算钱」——订阅档位、用量计量、权益开关与账单生成。AI 产品普遍按 token 计费，
这一层从可选项变成了必答题，因此单独成叶。

用法:
  python3 scripts/expand-pay-billing-2026-08.py
  python3 scripts/expand-pay-billing-2026-08.py --overwrite
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTENT = ROOT / "content"
ENTRIES = CONTENT / "entries"
VENDORS = CONTENT / "vendors"
EDGES = CONTENT / "edges"
REVIEWED = "2026-08-05"


def save(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def entry(**kw) -> dict:
    e = {
        "pricing": {"model": "open-source"},
        "availability": {
            "chinaAccessible": True,
            "needsCompany": False,
            "needsIcp": False,
            "regions": ["global"],
        },
        "tags": ["billing"],
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
    assert 20 <= len(e["oneLiner"]) <= 58, (e["id"], len(e["oneLiner"]))
    assert 160 <= len(e["descriptionMd"]) <= 380, (e["id"], len(e["descriptionMd"]))
    assert e["pitfalls"], e["id"]
    assert e.get("subcategory"), e["id"]
    return e


def mk(eid, name, sub, one, url, what, when, caution, **extra):
    pitfalls = extra.pop("pitfalls", None)
    kw = {
        "id": eid,
        "name": name,
        "category": "pay-billing",
        "subcategory": sub,
        "oneLiner": one,
        "officialUrl": url,
        "descriptionMd": f"{what}\n\n{when}\n\n{caution}\n",
        "pitfalls": pitfalls or [caution[:90]],
    }
    kw.update(extra)
    return entry(**kw)


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


def vendor(vid, name, region="overseas", url=None):
    v = {"id": vid, "name": name, "region": region}
    if url:
        v["url"] = url
    return v


OSS = {"model": "open-source"}
SAAS = {"model": "freemium", "currency": "USD"}
USAGE = {"model": "usage", "currency": "USD"}
ENTERPRISE = {"model": "subscription", "currency": "USD", "notes": "定价不公开，需商务沟通"}
ENTERPRISE_USAGE = {"model": "usage", "currency": "USD", "notes": "定价不公开，需商务沟通"}


VENDORS_DATA = [
    vendor("orb-inc", "Orb", url="https://www.withorb.com"),
    vendor("metronome-inc", "Metronome", url="https://metronome.com"),
    vendor("getlago", "Lago", url="https://www.getlago.com"),
    vendor("chargebee-inc", "Chargebee", url="https://www.chargebee.com"),
    vendor("openmeter-io", "OpenMeter", url="https://openmeter.io"),
    vendor("stigg-inc", "Stigg", url="https://www.stigg.io"),
]


ENTRIES_DATA = [
    # ——————— 通用订阅计费 ———————
    mk(
        "stripe-billing", "Stripe Billing", "subscription",
        "跟着 Stripe 一起来的订阅引擎 · 起步最省事；深度定制受限",
        "https://stripe.com/billing",
        "Stripe Billing 在 Stripe 支付之上补齐订阅生命周期：价目表、试用、按席位或用量计费、代金券、失败重试与发票，配套的 Customer Portal 让用户自助升降级。",
        "已经用 Stripe 收款、计费模型还落在「几档订阅 + 少量用量」范围内时，它几乎是零额外集成成本的默认解。",
        "计费规则一旦超出档位组合（阶梯定价、混合计量、合同期内改价），配置会迅速变复杂；深度绑定 Stripe 后，换支付通道意味着连计费一起重做。",
        vendorId="stripe-inc", pricing=USAGE,
        tags=["billing", "subscription", "saas", "stripe"],
        pitfalls=[
            "复杂计量与合同期改价的表达能力有限",
            "与 Stripe 深度绑定，换通道要连计费一起重做",
        ],
    ),
    mk(
        "chargebee", "Chargebee", "subscription",
        "老牌订阅计费中台 · 支付通道可换；配置面偏重",
        "https://www.chargebee.com",
        "Chargebee 是独立于支付通道的订阅计费平台，覆盖价目管理、试用与折扣、发票与催收、收入确认与报表，可同时挂 Stripe、Adyen、PayPal 等多个通道。",
        "SaaS 已经跑起来、订阅套餐和折扣策略越来越碎，或需要多币种多通道并存、财务要能出规范报表时评估。",
        "功能面广也意味着配置项繁多，落地通常要拉上财务一起定义口径；按营收抽成的定价在规模上来后并不便宜。",
        vendorId="chargebee-inc", pricing=ENTERPRISE,
        tags=["billing", "subscription", "saas", "finance"],
        pitfalls=[
            "配置项繁多，落地需财务一起定义口径",
            "按营收比例计费，规模上来后成本明显",
        ],
    ),
    mk(
        "recurly", "Recurly", "subscription",
        "订阅计费与挽留 · 催收能力见长；偏中大型客户",
        "https://recurly.com",
        "Recurly 专做订阅计费，除常规的价目与发票外，把重心放在续费失败的智能重试与流失挽留上，并提供订阅指标看板给增长和财务共用。",
        "订阅是主要收入形态、被动流失（扣款失败）已经吃掉可观营收，需要专门的催收与挽留机制时评估。",
        "面向中大型客户，小团队起步成本偏高；挽留策略的效果依赖历史数据积累，接入初期不会立刻见效。",
        pricing=ENTERPRISE,
        tags=["billing", "subscription", "retention", "saas"],
        pitfalls=[
            "面向中大型客户，小团队起步成本偏高",
            "挽留策略依赖数据积累，短期效果有限",
        ],
    ),
    mk(
        "maxio", "Maxio", "subscription",
        "B2B SaaS 财务向计费 · 强收入确认；不适合 to C 高频",
        "https://www.maxio.com",
        "Maxio 由 Chargify 与 SaaSOptics 合并而来，把订阅计费和 SaaS 财务分析放在一起，覆盖合同、开票、收入确认与 ARR、留存等指标口径。",
        "B2B SaaS 走合同制销售、财务需要合规的收入确认与投资人口径报表，而不只是把钱收上来时评估。",
        "产品重心偏财务，工程侧的实时计量能力不如用量计费专精工具；两套系统合并留下的使用体验割裂仍在改善中。",
        pricing=ENTERPRISE,
        tags=["billing", "subscription", "b2b", "finance"],
        pitfalls=[
            "实时用量计量能力弱于专精工具",
            "两套产品合并后的体验一致性仍在改善",
        ],
    ),
    mk(
        "zuora", "Zuora", "subscription",
        "企业级订阅商业化平台 · 合同复杂度上限高；实施周期长",
        "https://www.zuora.com",
        "Zuora 面向大型企业的订阅商业化，覆盖报价到收款的全链路：复杂合同条款、分级折扣、多实体多币种、收入确认与 ERP 对接都在其射程内。",
        "上市公司或大型企业、订阅合同条款复杂且要与 ERP、CRM 打通，审计口径不能有含糊时才值得考虑。",
        "实施周期以季度计，通常需要外部顾问参与；对中小团队而言功能与价格都严重过剩，属于典型的杀鸡用牛刀。",
        pricing=ENTERPRISE, tags=["billing", "subscription", "enterprise", "erp"],
        pitfalls=[
            "实施周期长，通常需外部顾问参与",
            "对中小团队功能与价格双重过剩",
        ],
    ),
    # ——————— 用量 / AI 计费 ———————
    mk(
        "orb", "Orb", "usage-based",
        "用量计费专精 · 事件流即账单；需先理清计量口径",
        "https://www.withorb.com",
        "Orb 以事件流为输入做用量计费：原始事件进来，按可版本化的定价规则聚合成账单，支持阶梯、封顶、预付额度与合同价，并保留可回溯的计算过程。",
        "AI 或基础设施类产品按 token、请求、时长这类连续量计费，且价目会频繁调整、需要对账可解释时优先。",
        "价值高度依赖上游事件采集的完整与准确，埋点漏了账就不准；面向成长期以上团队，早期项目容易觉得偏重。",
        vendorId="orb-inc", pricing=ENTERPRISE_USAGE,
        tags=["billing", "usage-based", "ai", "saas"],
        pitfalls=[
            "结果准确性完全依赖上游事件采集质量",
            "面向成长期团队，早期项目偏重",
        ],
    ),
    mk(
        "metronome", "Metronome", "usage-based",
        "实时用量计费 · 面向大额合同；小客户不划算",
        "https://metronome.com",
        "Metronome 做实时用量计费，账单随事件即时更新，支持自定义定价维度、承诺消费额度与合同折扣，也把用量数据回吐给销售侧做扩张与预警。",
        "客户以年度承诺额合同为主、销售需要随时看到「这个客户消耗了多少额度」时，比事后出账的方案更合适。",
        "定位偏中大型 B2B，定价与实施门槛对小团队不友好；实时性带来的架构复杂度也会传导到你的上游埋点。",
        vendorId="metronome-inc", pricing=ENTERPRISE_USAGE,
        tags=["billing", "usage-based", "b2b", "realtime"],
        pitfalls=[
            "定位中大型 B2B，小团队不划算",
            "实时计费对上游埋点架构要求更高",
        ],
    ),
    mk(
        "lago", "Lago", "usage-based",
        "开源用量计费引擎 · 可自托管；边缘能力需自补",
        "https://www.getlago.com",
        "Lago 是开源的用量计费引擎，提供计量、套餐与附加项、优惠券、发票与钱包额度，既有云托管版也可完整自托管，API 与 Webhook 覆盖主要流程。",
        "计费逻辑敏感或数据不能出境、希望自己掌控计费内核而不是绑定闭源 SaaS 时，是这一叶里最现实的自托管选项。",
        "自托管要自己扛住计量写入的峰值与数据一致性；相比闭源竞品，税务、收入确认这些边缘能力仍需自行补齐。",
        vendorId="getlago", pricing=OSS,
        tags=["billing", "usage-based", "open-source", "self-host"],
        pitfalls=[
            "自托管需自行承担计量写入峰值与一致性",
            "税务与收入确认等边缘能力需自补",
        ],
    ),
    mk(
        "openmeter", "OpenMeter", "metering",
        "只做计量这一层 · 高吞吐聚合；不出账单",
        "https://openmeter.io",
        "OpenMeter 专注计费链路的前半段：高吞吐地接收用量事件、按窗口聚合成可查询的指标，再把结果交给下游的计费或额度系统，本身不生成账单。",
        "已有计费或自研出账逻辑，缺的只是一个可靠的用量计量与配额层，尤其是 AI 产品的 token 统计时选它。",
        "不出账单意味着还要另配计费侧，链路多一跳；事件定义与幂等策略要提前想清楚，改口径后历史数据难以回溯重算。",
        vendorId="openmeter-io", pricing=OSS,
        tags=["billing", "metering", "ai", "open-source"],
        pitfalls=[
            "只做计量不出账单，仍需搭配计费系统",
            "事件口径变更后历史数据难以重算",
        ],
    ),
    mk(
        "amberflo", "Amberflo", "metering",
        "计量优先的用量计费 · 指标粒度细；生态偏小",
        "https://www.amberflo.io",
        "Amberflo 从计量出发做用量计费，提供事件采集 SDK、实时用量仪表与基于计量结果的定价配置，也能把用量指标推给下游做成本分析。",
        "产品定价维度多、又要给客户展示细粒度的用量明细，同时不打算自建计量管道时评估。",
        "生态与社区规模不及头部方案，遇到冷门问题可参考的资料很少；深度绑定其计量模型之后，迁移成本也不低。",
        pricing=ENTERPRISE_USAGE, tags=["billing", "metering", "usage-based", "saas"],
        pitfalls=[
            "生态与社区规模小，疑难问题资料少",
            "绑定其计量模型后迁移成本高",
        ],
    ),
    # ——————— 权益 / 自建 ———————
    mk(
        "stigg", "Stigg", "entitlement",
        "权益与套餐开关层 · 改套餐不改代码；仍需配计费",
        "https://www.stigg.io",
        "Stigg 把「这个用户能用什么、能用多少」从业务代码里抽出来做成独立的权益层，套餐与限额在后台配置即时生效，配套付费墙与用量提示组件。",
        "套餐经常调整、每次改价都要动代码发版，或想做定价实验却被工程排期卡住时，这一层的收益最直接。",
        "它管权益不管收钱，仍要搭配 Stripe Billing 一类计费系统；权益判断进入关键路径后，其可用性就成了你的可用性。",
        vendorId="stigg-inc", pricing=SAAS,
        tags=["billing", "entitlement", "pricing", "saas"],
        pitfalls=[
            "只管权益不管收款，需搭配计费系统",
            "权益判断进关键路径，可用性风险需兜底",
        ],
    ),
    mk(
        "kill-bill", "Kill Bill", "self-host",
        "老牌开源计费平台 · 插件化可深改；Java 栈运维重",
        "https://killbill.io",
        "Kill Bill 是运行多年的开源订阅与计费平台，核心提供目录、订阅、发票与支付插件框架，几乎所有环节都能通过插件替换，被不少自建计费的团队当作底座。",
        "计费规则特殊到 SaaS 产品表达不了、团队又有能力长期自维护一套计费系统时，它比从零写要稳妥得多。",
        "Java 技术栈与插件体系的学习曲线陡峭，运维和升级都要专人负责；界面与开箱体验明显落后于商业方案。",
        pricing=OSS, tags=["billing", "subscription", "open-source", "self-host"],
        pitfalls=[
            "Java 插件体系学习曲线陡，需专人维护",
            "界面与开箱体验落后于商业方案",
        ],
    ),
]


EDGES_DATA = [
    # 与支付/MoR 分层：这一叶算钱，隔壁两叶收钱与担税
    edge("e-stripe-billing-part-of-stripe", "stripe-billing", "stripe", "part_of",
         note="Stripe 支付之上的订阅计费模块", weight=0.9, confidence="verified"),
    edge("e-chargebee-cuw-stripe", "chargebee", "stripe", "commonly_used_with",
         note="计费中台在上、支付通道在下的常见组合", weight=0.75),
    edge("e-stripe-billing-alt-paddle", "stripe-billing", "paddle", "alternative_to",
         note="自己管订阅与税务 vs 交给 MoR 一并托管", weight=0.7),
    edge("e-revenuecat-cuw-stripe-billing", "revenuecat", "stripe-billing", "commonly_used_with",
         note="移动内购走 RevenueCat、Web 订阅走 Stripe 的双轨常态", weight=0.65),
    # 订阅叶内互比
    edge("e-chargebee-alt-recurly", "chargebee", "recurly", "alternative_to",
         note="配置面更全 vs 催收与挽留见长", weight=0.85),
    edge("e-chargebee-alt-stripe-billing", "chargebee", "stripe-billing", "alternative_to",
         note="通道无关的计费中台 vs 绑定 Stripe 的省事方案", weight=0.8),
    edge("e-maxio-alt-chargebee", "maxio", "chargebee", "alternative_to",
         note="B2B 财务口径优先 vs 通用订阅能力优先", weight=0.7),
    edge("e-zuora-alt-chargebee", "zuora", "chargebee", "alternative_to",
         note="企业级合同复杂度 vs 中小团队可自助落地", weight=0.7),
    edge("e-kill-bill-oss-chargebee", "kill-bill", "chargebee", "open_source_alternative_to",
         note="用自维护成本换计费内核的完全可控", weight=0.75),
    # 用量计费叶内互比
    edge("e-orb-alt-metronome", "orb", "metronome", "alternative_to",
         note="定价规则表达力优先 vs 实时额度与销售协同优先", weight=0.85),
    edge("e-lago-oss-orb", "lago", "orb", "open_source_alternative_to",
         note="可自托管的用量计费内核", weight=0.8),
    edge("e-amberflo-alt-metronome", "amberflo", "metronome", "alternative_to",
         note="计量粒度与用量展示优先 vs 大额合同场景优先", weight=0.65),
    edge("e-orb-alt-stripe-billing", "orb", "stripe-billing", "alternative_to",
         note="复杂用量定价 vs 档位订阅，超出档位组合时才需要换", weight=0.7),
    # 计量与权益是计费链路的前后两段
    edge("e-openmeter-cuw-lago", "openmeter", "lago", "commonly_used_with",
         note="计量在前、出账在后，自建计费链路的常见拼法", weight=0.7),
    edge("e-openmeter-alt-amberflo", "openmeter", "amberflo", "alternative_to",
         note="开源自托管计量 vs 托管计量与计费一体", weight=0.7),
    edge("e-stigg-cuw-stripe-billing", "stigg", "stripe-billing", "commonly_used_with",
         note="权益开关在上、收款出账在下", weight=0.75),
    edge("e-stigg-cuw-openmeter", "stigg", "openmeter", "commonly_used_with",
         note="限额判断要读计量结果", weight=0.6),
    # 与 AI 侧的连接：token 计费是这一叶近年的主要增量需求
    edge("e-openmeter-cuw-litellm", "openmeter", "litellm", "commonly_used_with",
         note="网关侧统计 token，计量层聚合成可计费用量", weight=0.6),
    edge("e-orb-cuw-litellm", "orb", "litellm", "commonly_used_with",
         note="把网关吐出的 token 用量转成对外账单", weight=0.55),
]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--overwrite", action="store_true")
    args = ap.parse_args()

    new_ids = {e["id"] for e in ENTRIES_DATA}

    def exists(nid: str) -> bool:
        return (ENTRIES / f"{nid}.json").exists() or nid in new_ids

    wrote_e = wrote_v = wrote_g = 0
    for v in VENDORS_DATA:
        path = VENDORS / f"{v['id']}.json"
        if path.exists() and not args.overwrite:
            continue
        save(path, v)
        wrote_v += 1

    for e in ENTRIES_DATA:
        path = ENTRIES / f"{e['id']}.json"
        if path.exists() and not args.overwrite:
            print("skip entry", e["id"])
            continue
        save(path, e)
        wrote_e += 1

    skipped = []
    for g in EDGES_DATA:
        path = EDGES / f"{g['id']}.json"
        if path.exists() and not args.overwrite:
            continue
        if not exists(g["from"]) or not exists(g["to"]):
            skipped.append(f"{g['from']}->{g['to']}")
            continue
        save(path, g)
        wrote_g += 1

    print(f"done entries={wrote_e} vendors={wrote_v} edges={wrote_g}")
    if skipped:
        print(f"skipped edges ({len(skipped)}): {', '.join(skipped)}")


if __name__ == "__main__":
    main()
