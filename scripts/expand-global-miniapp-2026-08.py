#!/usr/bin/env python3
"""远程雇佣 / EOR（global-hire）与 小程序 / 快应用（dist-miniapp）扩种。

- global-hire：Deel / Remote / Oyster / Rippling / Papaya Global / Velocity Global / Multiplier
  口径：跨境雇佣、EOR 名义雇主与全球薪资发放；与 global-entity（注册主体路径）用边区分。
- dist-miniapp：微信 / 支付宝 / 抖音 / 百度 / 快手小程序、快应用联盟、微信开放平台、鸿蒙元服务
  口径：免安装的国内轻应用分发平台，补齐「国内 ↔ 海外镜像」里长期缺失的一块。

用法:
  python3 scripts/expand-global-miniapp-2026-08.py
  python3 scripts/expand-global-miniapp-2026-08.py --overwrite
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
CAT_HIRE = "global-hire"
CAT_MINIAPP = "dist-miniapp"


def save(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def entry(**kw) -> dict:
    e = {
        "pricing": {"model": "subscription"},
        "availability": {
            "chinaAccessible": True,
            "needsCompany": True,
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
    one = e["oneLiner"]
    assert 20 <= len(one) <= 58, (e["id"], len(one), one)
    body = e.get("descriptionMd", "").replace("\n", "")
    assert 160 <= len(body) <= 360, (e["id"], len(body))
    assert 1 <= len(e.get("pitfalls") or []) <= 3, e["id"]
    assert e.get("subcategory"), e["id"]
    assert 3 <= len(e.get("tags") or []) <= 5, e["id"]
    return e


def desc(what: str, when: str, caution: str) -> str:
    return f"{what}\n\n{when}\n\n{caution}\n"


def mk(eid, name, cat, sub, one, url, what, when, caution, **extra):
    pitfalls = extra.pop("pitfalls", None)
    kw = {
        "id": eid,
        "name": name,
        "category": cat,
        "subcategory": sub,
        "oneLiner": one,
        "officialUrl": url,
        "descriptionMd": desc(what, when, caution),
        "pitfalls": pitfalls or [caution[:90]],
    }
    kw.update(extra)
    return entry(**kw)


def edge(eid, frm, to, typ, weight=0.7, confidence="community", note=None, sources=None):
    e = {
        "id": eid,
        "from": frm,
        "to": to,
        "type": typ,
        "weight": weight,
        "confidence": confidence,
        "sources": sources or [],
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


GLOBAL_B2B = {
    "chinaAccessible": True,
    "needsCompany": True,
    "needsIcp": False,
    "regions": ["global"],
}

# 国内小程序：企业主体 + 小程序备案
MINIAPP_CN = {
    "chinaAccessible": True,
    "needsCompany": True,
    "needsIcp": True,
    "regions": ["CN"],
}

HIRE_ENTRIES: list[dict] = [
    mk(
        "deel",
        "Deel",
        CAT_HIRE,
        "eor",
        "EOR 代雇与承包商合规一体 · 覆盖国家多 · 自助开通快 · 按人月订阅",
        "https://www.deel.com",
        "Deel 是覆盖面很广的全球雇佣平台：以名义雇主（EOR）身份在当地合规雇人，同时管理承包商合同、全球薪资发放与个税申报，让你不必在每个用人国注册公司。",
        "团队要在海外招一两个人试水，或分布式团队跨多国用人时优先评估；如果目的只是拿一个海外主体去收款开户，那属于注册公司路径，不是同一件事。",
        "按人/月计费，人数上来后成本可观；各国终止条款、竞业与知识产权归属需逐国确认，覆盖国家与费用形态以官方最新政策为准。",
        vendorId="deel-inc",
        pricing={"model": "subscription", "currency": "USD", "notes": "按雇员/承包商人月计费，具体以官网报价为准"},
        availability=GLOBAL_B2B,
        maturity="mature",
        tags=["eor", "payroll", "global-hiring", "compliance"],
        pitfalls=[
            "按人月计费，规模化后单人成本可能高于自建当地主体",
            "各国劳动法差异大，解雇补偿与 IP 归属条款需逐国确认",
        ],
    ),
    mk(
        "remote-com",
        "Remote",
        CAT_HIRE,
        "eor",
        "自有实体网络 · EOR/承包商/全球薪资闭环 · 合规链条不层层转包",
        "https://remote.com",
        "Remote 在多国自建本地实体来提供 EOR、承包商管理与全球薪资，强调用自有实体而非第三方转包承接雇佣关系，合同、福利与个税在同一后台闭环。",
        "当你在意「服务商在当地是否有自有实体」「数据与责任链条是否层层外包」时，把它与 Deel 放在一起横向比；它位于用人合规层，不替代主体注册与跨境收款工具。",
        "覆盖国家清单与自有实体分布会随时间变化；小众国家的福利包可能受限，签约前索要目标国的具体方案、终止条款与数据处理方名单。",
        vendorId="remote-com-inc",
        pricing={"model": "subscription", "currency": "USD", "notes": "EOR 与承包商分别按人月计费，以官网报价为准"},
        availability=GLOBAL_B2B,
        maturity="mature",
        tags=["eor", "payroll", "global-hiring", "compliance"],
        pitfalls=[
            "自有实体覆盖并非全球均等，小众国家仍可能走合作方",
            "福利包与终止条款逐国不同，需要书面确认目标国方案",
        ],
    ),
    mk(
        "oyster-hr",
        "Oyster",
        CAT_HIRE,
        "eor",
        "远程优先小团队向 EOR · 自助流程轻 · 本地福利与承包商合规",
        "https://www.oysterhr.com",
        "Oyster 是面向分布式团队的全球雇佣平台，提供 EOR 代雇、承包商合规与本地福利方案，产品语境偏「远程优先的小团队也能合规地跨国雇人」。",
        "早期公司要在少数几个国家招远程同事、更看重上手成本与自助流程时评估；如果是多国实体、要把工资单统一收敛成报表，偏企业级的薪资方案更合适。",
        "企业级薪资深度与本地 HR 服务不如老牌方案；覆盖国家、福利细节与费用形态以官方最新政策为准，勿按宣传页默认全球一致。",
        vendorId="oyster-hr-inc",
        pricing={"model": "subscription", "currency": "USD", "notes": "按雇员/承包商人月计费，以官网报价为准"},
        availability=GLOBAL_B2B,
        tags=["eor", "remote-work", "global-hiring", "payroll"],
        pitfalls=[
            "企业级薪资与本地 HR 服务深度弱于老牌方案",
            "各国福利与覆盖情况差异大，不要按宣传页默认全球一致",
        ],
    ),
    mk(
        "rippling",
        "Rippling",
        CAT_HIRE,
        "unified-hr",
        "HR+IT+财务统一中台 · 全球雇佣只是其中一模块 · 入职即配号发设备",
        "https://www.rippling.com",
        "Rippling 把人事、IT 设备与账号权限、财务支出统一到一套员工数据中台，全球雇佣与薪资是其中一个模块：员工入职即自动开通账号、寄送设备并配好权限。",
        "当员工全生命周期（账号、设备、报销）本身就是核心痛点、跨境雇佣只是顺带需求时评估；只要一两个国家的 EOR，专做 EOR 的平台更轻更快。",
        "模块化售卖，实际报价随开通模块累加；深度绑定其员工数据模型后迁移成本高，跨境雇佣的国家覆盖以官方最新政策为准。",
        vendorId="rippling-inc",
        pricing={"model": "subscription", "currency": "USD", "notes": "按模块与人数组合计费，以官网报价为准"},
        availability=GLOBAL_B2B,
        maturity="mature",
        tags=["eor", "hr", "payroll", "it-management"],
        pitfalls=[
            "模块化售卖，开通越多报价越高，需先算总账",
            "员工数据模型绑定深，后续迁移成本高",
        ],
    ),
    mk(
        "papaya-global",
        "Papaya Global",
        CAT_HIRE,
        "global-payroll",
        "全球薪资与跨境付款见长 · 多国工资单统一报表 · 偏企业级采购",
        "https://www.papayaglobal.com",
        "Papaya Global 以全球薪资与跨境付款见长，把多国工资单、福利与合规数据汇成一套报表和付款流，同时也提供 EOR 与承包商雇佣形态。",
        "已经在多国有实体、需要把分散的当地薪资服务商收敛成统一口径时优先；只在海外招零星几人的小团队用它偏重，自助式 EOR 更合适。",
        "偏企业级采购，实施周期与最低规模门槛较高；付款链路涉及银行合规审查，上线要预留时间，费用形态以官方最新政策为准。",
        vendorId="papaya-global-inc",
        pricing={"model": "subscription", "currency": "USD", "notes": "按人月与模块计费，偏企业级报价"},
        availability=GLOBAL_B2B,
        tags=["payroll", "eor", "global-hiring", "enterprise"],
        pitfalls=[
            "实施周期与最低规模门槛较高，不适合零星雇佣",
            "跨境付款涉及银行合规审查，上线时间需预留",
        ],
    ),
    mk(
        "velocity-global",
        "Velocity Global",
        CAT_HIRE,
        "eor",
        "顾问式跨国雇佣 · EOR/外派/复杂税务架构 · 报价多为一事一议",
        "https://velocityglobal.com",
        "Velocity Global 提供 EOR 名义雇主、全球薪资与承包商合规服务，风格更接近传统企业外包交付，常在需要顾问式支持与复杂跨国用工架构时出现。",
        "跨国集团要处理并购留任、员工外派、复杂税务架构等非标场景，且愿意走客户经理沟通路径时评估；追求自助开通与透明定价请看新一代平台。",
        "自助化程度与产品体验弱于新一代平台；条款与定价多为一事一议，比价时务必拿到书面报价、SLA 与终止条款。",
        vendorId="velocity-global-inc",
        pricing={"model": "subscription", "currency": "USD", "notes": "多为一事一议报价，需索取书面方案"},
        availability=GLOBAL_B2B,
        tags=["eor", "global-hiring", "payroll", "enterprise"],
        pitfalls=[
            "自助化与产品体验弱于新一代平台",
            "定价多为一事一议，比价前需拿到书面报价与终止条款",
        ],
    ),
    mk(
        "multiplier",
        "Multiplier",
        CAT_HIRE,
        "eor",
        "亚太覆盖为主的新一代 EOR · 开通快、界面轻 · 价格敏感型候选",
        "https://www.usemultiplier.com",
        "Multiplier 提供 EOR、承包商管理与全球薪资，主打亚太与新兴市场覆盖和快速开通，界面轻、上手门槛低，是新一代 EOR 里价格敏感型团队的常见候选。",
        "预算有限、招人重心在亚太或新兴市场、希望短时间内完成一名员工合规入职时纳入横向比较；欧美复杂福利与集团级架构另看老牌方案。",
        "品牌与规模不及头部，个别国家依赖本地合作伙伴而非自有实体；SLA、数据处理方与终止条款要在合同里写清。",
        vendorId="multiplier-inc",
        pricing={"model": "subscription", "currency": "USD", "notes": "按人月计费，以官网报价为准"},
        availability=GLOBAL_B2B,
        tags=["eor", "global-hiring", "payroll", "apac"],
        pitfalls=[
            "部分国家依赖本地合作伙伴而非自有实体",
            "规模与品牌不及头部，SLA 与数据处理方需写进合同",
        ],
    ),
]

MINIAPP_ENTRIES: list[dict] = [
    mk(
        "wechat-miniprogram",
        "微信小程序",
        CAT_MINIAPP,
        "wechat",
        "社交关系链与线下扫码入口 · 国内最大免安装生态 · 主体资质与类目审核严",
        "https://mp.weixin.qq.com",
        "微信小程序是国内最大的免安装轻应用生态：依托社交关系链、公众号、搜一搜与线下扫码等入口分发，用平台自有的语法与组件体系开发，能力边界由开放接口决定。",
        "产品要触达微信内的社交分享、线下扫码或公众号沉淀下来的流量时，它几乎是国内默认的第一站；需要长期驻留、后台任务与系统级权限，则仍要做原生 App。",
        "注册需要主体资质并通过类目审核，小程序还需完成备案，个人主体可用能力有限；平台规则与接口调整频繁，诱导分享类玩法容易触发处罚。",
        vendorId="tencent",
        pricing={"model": "free", "currency": "CNY", "notes": "开发免费；主体认证与部分能力的费用按官方最新政策为准"},
        availability=MINIAPP_CN,
        region="domestic",
        maturity="mature",
        tags=["miniapp", "wechat", "domestic", "distribution"],
        pitfalls=[
            "主体资质与类目审核门槛高，个人主体可用能力受限",
            "小程序需完成备案，未备案无法正式上线",
            "平台规则与接口调整频繁，营销玩法边界随时收紧",
        ],
    ),
    mk(
        "alipay-miniprogram",
        "支付宝小程序",
        CAT_MINIAPP,
        "alipay",
        "交易与生活服务语境 · 支付/信用/政务开放能力强 · 企业主体门槛高",
        "https://open.alipay.com",
        "支付宝小程序生长在交易与生活服务的语境里：用户往往带着支付、信用、政务或本地生活的明确意图进入，平台开放能力也偏交易、营销与信用等金融基建方向。",
        "业务与支付、会员卡券、政务民生或线下商户经营强相关时优先考虑；纯内容型、靠社交分享裂变的产品在这里拿不到微信那样的关系链分发。",
        "多数类目要求企业主体与行业资质，金融、医疗等强监管类目审核更严；备案与平台经营规则会持续调整，费用形态以官方最新政策为准。",
        vendorId="ant-group",
        pricing={"model": "free", "currency": "CNY", "notes": "开发免费；资质认证与交易相关费用按官方最新政策为准"},
        availability=MINIAPP_CN,
        region="domestic",
        maturity="mature",
        tags=["miniapp", "alipay", "domestic", "payment"],
        pitfalls=[
            "多数类目要求企业主体与行业资质，个人开发者路径窄",
            "金融、医疗等强监管类目审核严格且周期长",
        ],
    ),
    mk(
        "douyin-miniprogram",
        "抖音小程序",
        CAT_MINIAPP,
        "douyin",
        "短视频与直播内容流入口 · 种草即转化 · 强依赖投放与内容运营",
        "https://open.douyin.com",
        "抖音小程序挂在短视频与直播的内容流里：从视频挂载、直播间组件、评论区与个人主页等入口唤起，天然服务于「内容种草到当场转化」的链路。",
        "增长依赖短视频与直播投放、需要在内容旁边直接承接下单或留资时评估；它与微信的社交关系链分发是两种完全不同的流量逻辑，通常不互相替代。",
        "强依赖内容与投放能力，没有内容运营的团队很难拿到自然流量；类目资质与经营规则调整频繁，服务费与结算政策以官方最新说明为准。",
        vendorId="bytedance",
        pricing={"model": "free", "currency": "CNY", "notes": "开发免费；交易类目服务费按官方最新政策为准"},
        availability=MINIAPP_CN,
        region="domestic",
        tags=["miniapp", "douyin", "domestic", "commerce"],
        pitfalls=[
            "没有内容与投放能力时几乎拿不到自然流量",
            "类目资质与经营规则调整频繁，需要专人跟进",
        ],
    ),
    mk(
        "baidu-smartprogram",
        "百度智能小程序",
        CAT_MINIAPP,
        "baidu",
        "搜索与信息流入口 · 结果页直达服务 · 多宿主开放 · 生态热度一般",
        "https://smartprogram.baidu.com",
        "百度智能小程序以搜索与信息流为主要入口，用户从搜索结果直接进入服务页，并可开放给百度系的多个宿主 App，适合把已有内容与服务能力接进搜索场景。",
        "业务本身有明确的搜索需求——工具查询、垂类内容、本地服务——且希望承接搜索流量时评估；社交分享与内容裂变不是它的强项。",
        "生态活跃度与平台投入近年不如微信、抖音，长期维护成本要单独权衡；开发者同样需完成主体认证、类目审核与备案。",
        vendorId="baidu",
        pricing={"model": "free", "currency": "CNY", "notes": "开发免费；认证与商业化费用按官方最新政策为准"},
        availability=MINIAPP_CN,
        region="domestic",
        tags=["miniapp", "baidu", "domestic", "search"],
        pitfalls=[
            "生态活跃度与平台投入不如头部，长期维护回报需评估",
            "主体认证、类目审核与备案流程一样不能少",
        ],
    ),
    mk(
        "kuaishou-miniprogram",
        "快手小程序",
        CAT_MINIAPP,
        "kuaishou",
        "快手直播与短视频入口 · 本地生活与电商承接 · 常与抖音并行投放",
        "https://mp.kuaishou.com",
        "快手小程序依托快手的短视频与直播生态，从视频、直播间与私信等入口承接交易与服务，用户结构与内容语境和抖音有明显差异，转化路径也更偏信任型成交。",
        "投放与达人合作的重心在快手、需要在本地生活或电商链路里承接直播间流量时纳入；实践中通常与抖音小程序并行铺设，而不是二选一。",
        "开放能力与文档完善度不及头部平台，部分接口需要单独申请；类目资质与经营规则变动频繁，费用形态以官方最新政策为准。",
        vendorId="kuaishou",
        pricing={"model": "free", "currency": "CNY", "notes": "开发免费；交易类目相关费用按官方最新政策为准"},
        availability=MINIAPP_CN,
        region="domestic",
        tags=["miniapp", "kuaishou", "domestic", "commerce"],
        pitfalls=[
            "开放能力与文档完善度不及头部平台，部分接口需申请",
            "经营类目规则变动频繁，需持续跟进平台公告",
        ],
    ),
    mk(
        "quickapp-alliance",
        "快应用联盟",
        CAT_MINIAPP,
        "quickapp",
        "厂商联盟免安装标准 · 系统负一屏与全局搜索入口 · 一次开发多家提审",
        "https://www.quickapp.cn",
        "快应用是国内主流安卓手机厂商联合推出的免安装轻应用标准：由厂商在系统负一屏、全局搜索与应用商店等系统级位置提供入口，开发者一次开发、多厂商分发。",
        "想覆盖安卓的系统级入口、又不希望用户先下载安装包时评估；它绑定的是手机厂商终端，而不是某个超级 App 的流量池，与微信/抖音小程序是并行选择。",
        "各厂商的实现与审核标准并不完全一致，需要逐家提审与回归；生态热度不及超级 App 小程序，入口曝光高度依赖厂商推荐位。",
        vendorId=None,
        pricing={"model": "free", "currency": "CNY", "notes": "标准与工具链免费；各厂商上架政策以官方最新说明为准"},
        availability=MINIAPP_CN,
        region="domestic",
        tags=["quickapp", "android", "domestic", "distribution"],
        pitfalls=[
            "各厂商审核标准不一致，需逐家提审与回归验证",
            "入口曝光高度依赖厂商推荐位，自然流量不稳定",
        ],
    ),
    mk(
        "wechat-open-platform",
        "微信开放平台",
        CAT_MINIAPP,
        "open-platform",
        "微信账号与开放能力底座 · UnionID 打通多应用 · 非小程序日常发布后台",
        "https://open.weixin.qq.com",
        "微信开放平台是微信生态的账号与开放能力底座：在这里管理移动应用、网站应用与第三方平台接入，把多个 App 与小程序绑定到同一开放平台账号后即可打通 UnionID。",
        "需要微信登录与分享回调、多个小程序或 App 共用一套用户体系，或做服务商代开发第三方平台时进入这里；单个小程序的日常开发与发布仍在小程序后台完成。",
        "开放平台账号认证需要企业主体，认证费用与周期按官方最新政策为准；它与公众平台的职责容易混淆，账号归属与权限要在团队内提前约定。",
        vendorId="tencent",
        pricing={"model": "free", "currency": "CNY", "notes": "平台能力免费；账号认证费用按官方最新政策为准"},
        availability={
            "chinaAccessible": True,
            "needsCompany": True,
            "needsIcp": False,
            "regions": ["CN"],
        },
        region="domestic",
        maturity="mature",
        tags=["wechat", "open-platform", "domestic", "identity"],
        pitfalls=[
            "与微信公众平台职责易混淆，账号归属需提前约定",
            "开放平台账号认证需企业主体，且有年度认证要求",
        ],
    ),
    mk(
        "harmonyos-atomic-service",
        "鸿蒙元服务",
        CAT_MINIAPP,
        "harmonyos",
        "鸿蒙免安装轻形态 · 卡片与服务中心入口 · ArkTS 同栈 · 经 AGC 上架",
        "https://developer.huawei.com",
        "元服务是 HarmonyOS 上的免安装轻量形态：以桌面卡片、服务中心与碰一碰等系统级入口触达用户，与鸿蒙应用共用 ArkTS 技术栈，经 AppGallery Connect 提交上架。",
        "已经在做鸿蒙原生应用、想用卡片和系统入口做轻量触达时顺带评估；纯 Android/iOS 团队接入意味着额外引入一套鸿蒙技术栈与发布流程。",
        "设备存量与生态仍在扩张期，投入产出需按目标用户盘算；上架要求企业主体与类目资质，接口规范随系统版本演进较快。",
        vendorId="huawei",
        pricing={"model": "free", "currency": "CNY", "notes": "开发工具免费；开发者账号与上架政策以官方最新说明为准"},
        availability=MINIAPP_CN,
        region="domestic",
        tags=["harmonyos", "miniapp", "domestic", "distribution"],
        pitfalls=[
            "需额外投入鸿蒙 ArkTS 技术栈与独立发布流程",
            "接口与规范随系统版本演进较快，需跟随升级",
            "上架要求企业主体与类目资质",
        ],
    ),
]

ENTRIES_DATA: list[dict] = HIRE_ENTRIES + MINIAPP_ENTRIES

VENDORS_DATA: list[dict] = [
    vendor("deel-inc", "Deel", url="https://www.deel.com"),
    vendor("remote-com-inc", "Remote Technology", url="https://remote.com"),
    vendor("oyster-hr-inc", "Oyster HR", url="https://www.oysterhr.com"),
    vendor("rippling-inc", "Rippling", url="https://www.rippling.com"),
    vendor("papaya-global-inc", "Papaya Global", url="https://www.papayaglobal.com"),
    vendor("velocity-global-inc", "Velocity Global", url="https://velocityglobal.com"),
    vendor("multiplier-inc", "Multiplier", url="https://www.usemultiplier.com"),
]

EDGES_DATA: list[dict] = [
    # ——— global-hire 叶内横向对照 ———
    edge(
        "e-deel-alt-remote-com",
        "deel",
        "remote-com",
        "alternative_to",
        weight=0.85,
        note="同为 EOR 头部：Deel 覆盖广、自助流程快；Remote 强调自有实体、合规链条不层层转包",
    ),
    edge(
        "e-oyster-hr-alt-remote-com",
        "oyster-hr",
        "remote-com",
        "alternative_to",
        weight=0.75,
        note="Oyster 偏远程优先小团队的自助体验；Remote 偏自有实体与合规纵深",
    ),
    edge(
        "e-multiplier-alt-deel",
        "multiplier",
        "deel",
        "alternative_to",
        weight=0.7,
        note="Multiplier 亚太与新兴市场为主、价格敏感；Deel 覆盖更广、生态与集成更多",
    ),
    edge(
        "e-rippling-alt-deel",
        "rippling",
        "deel",
        "alternative_to",
        weight=0.6,
        note="Rippling 是 HR+IT+财务统一中台，全球雇佣只是模块；Deel 是 EOR 优先的专用平台",
    ),
    edge(
        "e-papaya-global-alt-velocity-global",
        "papaya-global",
        "velocity-global",
        "alternative_to",
        weight=0.65,
        note="同为企业级路线：Papaya 偏全球薪资与付款报表，Velocity 偏顾问式非标用工架构",
    ),
    # ——— 跨叶：不注册主体雇人 vs 注册主体 ———
    edge(
        "e-deel-alt-stripe-atlas",
        "deel",
        "stripe-atlas",
        "alternative_to",
        weight=0.55,
        note="两条不同路径：EOR 不注册当地主体也能合规雇人；Atlas 是注册美国公司并绑定收款，解决的是主体与收单",
    ),
    edge(
        "e-remote-com-alt-firstbase",
        "remote-com",
        "firstbase",
        "alternative_to",
        weight=0.5,
        note="先想清楚要「雇人」还是要「主体」：Remote 提供当地合规雇佣，Firstbase 提供公司注册与合规维护",
    ),
    edge(
        "e-velocity-global-alt-firstbase",
        "velocity-global",
        "firstbase",
        "alternative_to",
        weight=0.4,
        note="跨国用工外包 vs 自注册主体自行雇佣；前者省实体、后者省长期人均成本",
    ),
    # ——— 跨叶：雇佣平台与跨境收付 ———
    edge(
        "e-deel-cuw-wise",
        "deel",
        "wise",
        "commonly_used_with",
        weight=0.5,
        confidence="inferred",
        note="平台负责雇佣合规与出账，个人侧常再用多币种账户落地收款；具体可用提现渠道以平台为准",
    ),
    edge(
        "e-oyster-hr-cuw-wise",
        "oyster-hr",
        "wise",
        "commonly_used_with",
        weight=0.4,
        confidence="inferred",
        note="承包商拿到跨境付款后常经多币种账户结汇，两者分处雇佣层与收款层",
    ),
    edge(
        "e-multiplier-cuw-payoneer",
        "multiplier",
        "payoneer",
        "commonly_used_with",
        weight=0.4,
        confidence="inferred",
        note="亚太承包商侧常见的收款落地方式；雇佣合规与收款账户是两层，勿混为一谈",
    ),
    edge(
        "e-papaya-global-cuw-airwallex",
        "papaya-global",
        "airwallex",
        "commonly_used_with",
        weight=0.4,
        confidence="inferred",
        note="Papaya 解决多国工资单与付款流，Airwallex 解决企业跨境收付与换汇，二者常并存于同一财务栈",
    ),
    # ——— dist-miniapp 叶内横向对照 ———
    edge(
        "e-alipay-miniprogram-alt-wechat-miniprogram",
        "alipay-miniprogram",
        "wechat-miniprogram",
        "alternative_to",
        weight=0.85,
        note="交易与生活服务意图流量 vs 社交关系链与线下扫码流量；开放能力一偏金融、一偏社交",
    ),
    edge(
        "e-douyin-miniprogram-alt-wechat-miniprogram",
        "douyin-miniprogram",
        "wechat-miniprogram",
        "alternative_to",
        weight=0.8,
        note="内容流投放即转化 vs 社交分享与私域沉淀；抖音靠内容与投放，微信靠关系链",
    ),
    edge(
        "e-baidu-smartprogram-alt-wechat-miniprogram",
        "baidu-smartprogram",
        "wechat-miniprogram",
        "alternative_to",
        weight=0.55,
        note="搜索结果页直达服务 vs 社交生态内分发；搜索意图明确但生态热度较低",
    ),
    edge(
        "e-kuaishou-miniprogram-alt-douyin-miniprogram",
        "kuaishou-miniprogram",
        "douyin-miniprogram",
        "alternative_to",
        weight=0.8,
        note="同为短视频生态承接页，用户结构与达人生态不同，实践中常并行铺设而非二选一",
    ),
    edge(
        "e-quickapp-alliance-alt-wechat-miniprogram",
        "quickapp-alliance",
        "wechat-miniprogram",
        "alternative_to",
        weight=0.6,
        note="厂商系统级入口（负一屏/全局搜索）vs 超级 App 内流量池；同为免安装，但流量来源完全不同",
    ),
    edge(
        "e-harmonyos-atomic-service-alt-quickapp-alliance",
        "harmonyos-atomic-service",
        "quickapp-alliance",
        "alternative_to",
        weight=0.65,
        note="同属厂商侧免安装形态：元服务绑定 HarmonyOS 与 ArkTS，快应用是多厂商安卓联盟标准",
    ),
    edge(
        "e-wechat-miniprogram-iw-wechat-open-platform",
        "wechat-miniprogram",
        "wechat-open-platform",
        "integrates_with",
        weight=0.8,
        confidence="verified",
        note="小程序绑定同一开放平台账号后可打通 UnionID 与多应用用户体系；日常发布仍在小程序后台",
    ),
    # ——— 跨叶：小程序与支付 ———
    edge(
        "e-wechat-miniprogram-iw-wechat-pay",
        "wechat-miniprogram",
        "wechat-pay",
        "integrates_with",
        weight=0.9,
        confidence="verified",
        note="小程序内交易走微信支付，需商户号与对应类目资质；费率与结算政策以官方最新说明为准",
    ),
    edge(
        "e-alipay-miniprogram-iw-alipay",
        "alipay-miniprogram",
        "alipay",
        "integrates_with",
        weight=0.9,
        confidence="verified",
        note="小程序内交易走支付宝支付能力，与开放平台账号、商户资质同一套体系",
    ),
    # ——— 跨叶：分发渠道对照 ———
    edge(
        "e-wechat-miniprogram-deq-apple-app-store",
        "wechat-miniprogram",
        "apple-app-store",
        "domestic_equivalent_of",
        weight=0.45,
        note="小程序是免安装分发、寄生于超级 App，与应用商店的安装型分发不是一回事，仅作分发渠道对照",
    ),
    edge(
        "e-quickapp-alliance-alt-google-play",
        "quickapp-alliance",
        "google-play",
        "alternative_to",
        weight=0.35,
        note="国内厂商联盟的免安装轻应用入口 vs 海外安卓商店的安装型分发；形态不同，仅作渠道对照",
    ),
    edge(
        "e-harmonyos-atomic-service-iw-huawei-agc",
        "harmonyos-atomic-service",
        "huawei-agc",
        "integrates_with",
        weight=0.8,
        note="元服务通过 AppGallery Connect 完成创建、认证与上架，与鸿蒙应用共用同一套发布控制台",
    ),
    edge(
        "e-harmonyos-atomic-service-alt-huawei-appgallery",
        "harmonyos-atomic-service",
        "huawei-appgallery",
        "alternative_to",
        weight=0.5,
        note="同在华为生态内的两种形态：元服务免安装、走卡片与服务中心；应用市场是安装型应用分发",
    ),
    # ——— 跨端框架（由另一批创建，未就位时会被跳过）———
    edge(
        "e-wechat-miniprogram-cuw-taro",
        "wechat-miniprogram",
        "taro",
        "commonly_used_with",
        weight=0.7,
        note="用 React 语法一套代码编译到多端小程序，避免为每个平台重写业务层",
    ),
    edge(
        "e-wechat-miniprogram-cuw-uni-app",
        "wechat-miniprogram",
        "uni-app",
        "commonly_used_with",
        weight=0.7,
        note="用 Vue 语法多端编译，常与微信小程序原生开发二选一",
    ),
    edge(
        "e-alipay-miniprogram-cuw-taro",
        "alipay-miniprogram",
        "taro",
        "commonly_used_with",
        weight=0.6,
        note="多端编译可复用业务代码，但支付与信用等平台专有能力仍需分支处理",
    ),
    edge(
        "e-douyin-miniprogram-cuw-uni-app",
        "douyin-miniprogram",
        "uni-app",
        "commonly_used_with",
        weight=0.6,
        note="跨端框架覆盖抖音端编译，直播间与视频挂载等专有能力仍需按平台适配",
    ),
]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--overwrite", action="store_true")
    args = ap.parse_args()

    ENTRIES.mkdir(parents=True, exist_ok=True)
    VENDORS.mkdir(parents=True, exist_ok=True)
    EDGES.mkdir(parents=True, exist_ok=True)

    wrote_e = wrote_v = wrote_g = 0
    skipped_e = skipped_g = 0
    for e in ENTRIES_DATA:
        path = ENTRIES / f"{e['id']}.json"
        if path.exists() and not args.overwrite:
            skipped_e += 1
            print("skip entry exists", e["id"])
            continue
        save(path, e)
        wrote_e += 1
        print("entry", e["id"])

    for v in VENDORS_DATA:
        path = VENDORS / f"{v['id']}.json"
        if path.exists() and not args.overwrite:
            continue
        save(path, v)
        wrote_v += 1
        print("vendor", v["id"])

    known_new = {x["id"] for x in ENTRIES_DATA}
    for g in EDGES_DATA:
        path = EDGES / f"{g['id']}.json"
        if path.exists() and not args.overwrite:
            skipped_g += 1
            print("skip edge exists", g["id"])
            continue
        frm_ok = (ENTRIES / f"{g['from']}.json").exists() or g["from"] in known_new
        to_ok = (ENTRIES / f"{g['to']}.json").exists() or g["to"] in known_new
        if not frm_ok:
            skipped_g += 1
            print("skip edge missing from", g["id"], g["from"])
            continue
        if not to_ok:
            skipped_g += 1
            print("skip edge missing to", g["id"], g["to"])
            continue
        save(path, g)
        wrote_g += 1
        print("edge", g["id"])

    print(
        f"done entries={wrote_e}(skip {skipped_e}) vendors={wrote_v} "
        f"edges={wrote_g}(skip {skipped_g})"
    )


if __name__ == "__main__":
    main()
