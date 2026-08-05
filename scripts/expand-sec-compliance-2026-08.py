#!/usr/bin/env python3
"""安全合规扩种（两个叶类：sec-compliance / sec-bot-captcha）。

- 合规认证 / 隐私（sec-compliance）：
  合规自动化 Vanta / Drata / Secureframe / Sprinto；
  隐私与同意管理 OneTrust / iubenda / Termly / Cookiebot
- 验证码 / Bot 防护（sec-bot-captcha）：
  Cloudflare Turnstile / hCaptcha / reCAPTCHA / 极验 GeeTest /
  Friendly Captcha / ALTCHA / Arcjet / DataDome

用法:
  python3 scripts/expand-sec-compliance-2026-08.py
  python3 scripts/expand-sec-compliance-2026-08.py --overwrite
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
CAT_COMPLIANCE = "sec-compliance"
CAT_BOT = "sec-bot-captcha"


def save(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def entry(**kw) -> dict:
    e = {
        "pricing": {"model": "subscription", "currency": "USD"},
        "availability": {
            "chinaAccessible": True,
            "needsCompany": False,
            "needsIcp": False,
            "regions": ["global"],
        },
        "tags": ["security", "compliance"],
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
    assert 20 <= len(e["oneLiner"]) <= 58, (e["id"], len(e["oneLiner"]), e["oneLiner"])
    dlen = len(e.get("descriptionMd", ""))
    assert 160 <= dlen <= 360, (e["id"], dlen)
    assert e.get("pitfalls"), e["id"]
    assert e.get("subcategory"), e["id"]
    assert 3 <= len(e["tags"]) <= 5, (e["id"], e["tags"])
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


GLOBAL_OK = {
    "chinaAccessible": True,
    "needsCompany": False,
    "needsIcp": False,
    "regions": ["global"],
}

CN_BLOCKED = {
    "chinaAccessible": False,
    "needsCompany": False,
    "needsIcp": False,
    "regions": ["global"],
}

EU_FIRST = {
    "chinaAccessible": True,
    "needsCompany": False,
    "needsIcp": False,
    "regions": ["EU", "global"],
}

DOMESTIC = {
    "chinaAccessible": True,
    "needsCompany": True,
    "needsIcp": False,
    "regions": ["CN"],
}


COMPLIANCE_ENTRIES: list[dict] = [
    # ——— 合规自动化（SOC 2 / ISO 27001） ———
    mk(
        "vanta",
        "Vanta",
        CAT_COMPLIANCE,
        "compliance-automation",
        "合规自动化老牌 · 控制项持续取证 · 审计师与集成生态最广",
        "https://www.vanta.com",
        "Vanta 把 SOC 2、ISO 27001、HIPAA 等框架拆成可执行控制项，接入云账号、身份系统与设备管理后持续采集证据，并把政策模板、安全培训与供应商风险收进同一后台。",
        "出海 SaaS 要在数月内拿下第一张 SOC 2、团队又没有专职合规岗时，用它替代人工整理证据表格；它位于云与身份系统之上的流程编排层，不改变基础设施本身。",
        "工具只是流程助手，认证仍要审计机构出具报告；国内团队常卡在设备管理代理装机与英文政策落地，且国内等保测评是另一套路径，两边不互认。",
        vendorId="vanta-inc",
        pitfalls=[
            "Vanta 自身不出证，审计报告仍需另付费请审计机构执行。",
            "需要在每台员工设备装监控代理，远程与外包成员推行阻力大。",
        ],
        pricing={"model": "subscription", "currency": "USD"},
        tags=["compliance", "soc2", "security", "saas"],
        maturity="mature",
    ),
    mk(
        "drata",
        "Drata",
        CAT_COMPLIANCE,
        "compliance-automation",
        "合规自动化 · 控制测试颗粒度细 · 多框架并行 · 审计师协作区",
        "https://drata.com",
        "Drata 同样做安全合规自动化，把 SOC 2、ISO 27001、GDPR、PCI DSS 等框架的控制项接到云、代码仓库与人事系统做持续测试，并提供审计师协作工作区与对外信任中心页面。",
        "需要同时准备多张证书、希望控制测试更细且审计过程留痕完整时，与 Vanta 一起进短名单做 POC；两者能力重叠度高，差别多在集成覆盖与服务方式。",
        "工具只是流程助手，出证仍由审计机构完成；按框架与人数计价，团队扩张后续费涨幅明显，退订前务必先导出证据留存。",
        vendorId="drata-inc",
        pitfalls=[
            "按框架与员工数计价，团队扩张后续费成本上升明显。",
            "更换平台时历史证据迁移麻烦，退订前要先完成导出。",
        ],
        pricing={"model": "subscription", "currency": "USD"},
        tags=["compliance", "soc2", "security", "audit"],
    ),
    mk(
        "secureframe",
        "Secureframe",
        CAT_COMPLIANCE,
        "compliance-automation",
        "合规自动化 · 策略模板与顾问陪跑 · 首次认证上手门槛低",
        "https://secureframe.com",
        "Secureframe 提供 SOC 2、ISO 27001、HIPAA、GDPR 等框架的自动化合规平台，强调开箱的策略模板、员工安全培训与顾问式陪跑，把首次认证的准备动作模板化。",
        "第一次做合规、内部缺人带节奏，希望供应商顺带给实施建议时评估；与 Vanta、Drata 属同层可比单元，选择前先对齐各自的集成清单。",
        "工具只是流程助手，认证要审计机构出具报告；集成覆盖面不如头部平台广，自研组件与国内云资源常需手工补证据。",
        vendorId="secureframe-inc",
        pitfalls=[
            "集成清单不如头部平台长，国内云与自研系统多为手工取证。",
            "顾问陪跑服务通常绑定较高档套餐，低档位体验接近纯工具。",
        ],
        pricing={"model": "subscription", "currency": "USD"},
        tags=["compliance", "soc2", "iso27001", "security"],
    ),
    mk(
        "sprinto",
        "Sprinto",
        CAT_COMPLIANCE,
        "compliance-automation",
        "合规自动化 · 实施节奏轻 · 亚太时区响应好 · 多框架覆盖",
        "https://sprinto.com",
        "Sprinto 面向成长型 SaaS 做合规自动化，覆盖 SOC 2、ISO 27001、GDPR、HIPAA 等框架，用自动化检查替代人工收证，并把整改任务直接派发到责任人。",
        "团队规模不大、想用较轻的实施节奏跑完第一次认证，且希望对接方在亚太时区随叫随应时，与 Vanta、Drata 同批评估。",
        "工具只是流程助手，证书仍由审计机构出具；企业级定制与深度集成弱于头部平台，复杂云架构下的自动化覆盖率要先实测再签约。",
        vendorId="sprinto-inc",
        pitfalls=[
            "复杂或多云架构下自动化覆盖率参差，签约前应做真实环境验证。",
            "企业级定制、SSO 与高级报表能力弱于头部平台。",
        ],
        pricing={"model": "subscription", "currency": "USD"},
        tags=["compliance", "soc2", "security", "startup"],
    ),
    # ——— 隐私政策 / Cookie 同意 ———
    mk(
        "onetrust",
        "OneTrust",
        CAT_COMPLIANCE,
        "privacy-consent",
        "企业级隐私治理 · 同意管理/数据地图/数据主体请求全覆盖",
        "https://www.onetrust.com",
        "OneTrust 是企业级隐私与治理平台，覆盖 Cookie 同意管理、数据地图、数据主体请求处理、第三方风险与合规评估，是大型组织落地 GDPR、CCPA 等法规的常见底座。",
        "组织已有法务与隐私岗、要统一治理多品牌多站点的同意与数据流时选它；只想生成一份隐私政策与 Cookie 横幅的小团队，用 iubenda、Termly 更划算。",
        "工具只是流程助手，合规责任与审计结论仍在组织与审计机构一侧；模块多、实施与培训成本高，同意脚本体积对首屏性能有实际影响。",
        vendorId="onetrust-inc",
        pitfalls=[
            "模块化销售，实施与培训周期长，小团队用不满模块仍要付整包价。",
            "同意脚本较重，会拖慢首屏并影响埋点采集口径。",
        ],
        pricing={"model": "subscription", "currency": "USD"},
        tags=["privacy", "gdpr", "consent", "compliance"],
        maturity="mature",
    ),
    mk(
        "iubenda",
        "iubenda",
        CAT_COMPLIANCE,
        "privacy-consent",
        "隐私政策生成 + 同意管理 · 多语种欧盟条款 · 嵌一段脚本即可",
        "https://www.iubenda.com",
        "iubenda 提供隐私政策与 Cookie 政策生成、同意管理和内部合规记录，条款模板由法务团队维护并随法规更新，站点嵌一段脚本即可挂上横幅与政策页。",
        "面向欧盟用户的独立开发者或中小出海站点，需要一份能自动跟进法规、且支持多语种的政策与 GDPR 同意横幅时优先。",
        "工具只是流程助手，模板不等于法律意见，敏感业务仍应请律师复核；按站点与语言分档计费，多站点多语场景成本会明显叠加。",
        vendorId="iubenda-srl",
        pitfalls=[
            "模板化条款不等于法律意见，业务特殊时需律师复核。",
            "按站点与语言计费，多站点、多语种叠加后成本上升快。",
        ],
        pricing={"model": "freemium", "currency": "EUR"},
        availability=EU_FIRST,
        tags=["privacy", "gdpr", "consent", "legal"],
    ),
    mk(
        "termly",
        "Termly",
        CAT_COMPLIANCE,
        "privacy-consent",
        "政策生成器 + Cookie 扫描 · 偏美国州级隐私法口径 · 有免费档",
        "https://termly.io",
        "Termly 提供隐私政策、服务条款与 Cookie 政策生成器，配套 Cookie 扫描与同意横幅，法规口径侧重 CCPA/CPRA 等美国州级隐私法，同时兼顾 GDPR。",
        "主要面向美国用户的小型站点，想低成本挂上合规政策与同意条时评估；欧盟精细化同意与多语场景可对照 iubenda、Cookiebot。",
        "工具只是流程助手，生成文本必须按真实数据流改写；免费档在横幅样式与扫描频次上有限制，政策更新是否随法规同步要定期自查。",
        vendorId="termly-inc",
        pitfalls=[
            "生成的政策是通用模板，未按真实数据流改写反而形成合规风险。",
            "免费档会在横幅上带品牌标识，扫描频次与页面数也有上限。",
        ],
        pricing={"model": "freemium", "currency": "USD"},
        tags=["privacy", "consent", "ccpa", "legal"],
    ),
    mk(
        "cookiebot",
        "Cookiebot",
        CAT_COMPLIANCE,
        "privacy-consent",
        "Cookie 自动扫描分类 · 同意日志可留痕 · 欧盟 CMP 老牌",
        "https://www.cookiebot.com",
        "Cookiebot 专注 Cookie 与追踪脚本的自动扫描、分类与同意管理，生成可审计的同意日志，并支持与 Google Consent Mode 等标签体系联动，现属 Usercentrics。",
        "站点埋点复杂、需要定期扫描清点第三方脚本并留存同意证据时选它；只要一份静态政策文本、没有追踪脚本的站点则不必上 CMP。",
        "工具只是流程助手，合规结论仍取决于真实数据处理与审计机构判断；阻断式加载会让统计口径明显变化，上线前要和数据团队对齐。",
        vendorId="usercentrics",
        pitfalls=[
            "开启阻断式加载后统计数据会明显下降，需提前与数据团队对齐口径。",
            "按域名与页面量计价，多子域站群成本容易超出预算。",
        ],
        pricing={"model": "freemium", "currency": "EUR"},
        availability=EU_FIRST,
        tags=["privacy", "gdpr", "consent", "cookies"],
        maturity="mature",
    ),
]


BOT_ENTRIES: list[dict] = [
    # ——— 人机验证挂件 ———
    mk(
        "cloudflare-turnstile",
        "Cloudflare Turnstile",
        CAT_BOT,
        "captcha-widget",
        "无感人机验证 · 免打勾免拼图 · 站点不必整体迁 Cloudflare",
        "https://www.cloudflare.com/application-services/products/turnstile/",
        "Turnstile 是 Cloudflare 的免打勾人机验证组件，用浏览器信号与轻量挑战替代拼图点选，前端嵌 widget、后端校验 token 即可接入，站点不必把流量整体迁到 Cloudflare。",
        "要给注册、登录、留言等表单加一层低摩擦人机校验时首选；它在应用表单层，与 Cloudflare WAF 的规则与速率限制不是一层，两者可叠加使用。",
        "它只挡自动化脚本，业务欺诈与撞库仍需风控规则配合；国内访问 Cloudflare 边缘偶有抖动，校验请求变慢时要有降级放行路径。",
        vendorId="cloudflare",
        pitfalls=[
            "只解决「是不是机器」，账号欺诈与撞库仍需业务风控。",
            "国内链路偶有抖动，需为校验超时准备降级或重试策略。",
        ],
        pricing={"model": "freemium", "currency": "USD"},
        docsUrl="https://developers.cloudflare.com/turnstile/",
        tags=["captcha", "bot", "security", "cloudflare"],
    ),
    mk(
        "hcaptcha",
        "hCaptcha",
        CAT_BOT,
        "captcha-widget",
        "隐私导向验证码 · 难度可调 · 企业风险评分 · 不用于广告画像",
        "https://www.hcaptcha.com",
        "hCaptcha 是 reCAPTCHA 之外使用面较广的人机验证服务，提供可调难度、企业级风险评分与无障碍通道，接入方式与主流验证码基本一致，迁移成本低。",
        "想替换 reCAPTCHA、又需要成熟挑战题库与企业支持时评估；国内访问链路需实测，以海外用户为主的站点更合适。",
        "它只挡自动化流量，账号与支付风控仍要另建；免费档挑战偶尔偏难会压低转化，无障碍体验需要专门回归测试。",
        vendorId="hcaptcha-inc",
        pitfalls=[
            "挑战难度偏高时会明显影响注册转化，需要按场景调档。",
            "国内加载速度不稳定，面向大陆用户前必须实测链路。",
        ],
        pricing={"model": "freemium", "currency": "USD"},
        tags=["captcha", "bot", "privacy", "security"],
    ),
    mk(
        "recaptcha",
        "reCAPTCHA",
        CAT_BOT,
        "captcha-widget",
        "Google 老牌验证码 · v3 无感打分 · 中国大陆加载不畅",
        "https://www.google.com/recaptcha/",
        "reCAPTCHA 是 Google 的人机验证服务：v2 走勾选与图片挑战，v3 用行为打分返回风险值交业务决策，文档与各语言框架封装最齐全，Enterprise 版走 Google Cloud 计费。",
        "站点主要面向海外、希望用最常见方案快速接入时选它；国内站点要么改用 recaptcha.net 域名，要么直接换极验或 Turnstile。",
        "google.com 域在中国大陆访问不畅，国内用户会卡在验证码加载不出——这是国内站点的真实坑；v3 只给分数，拦不拦仍要自己写策略。",
        vendorId="google",
        pitfalls=[
            "中国大陆访问 google.com 资源不畅，国内用户常见验证码不加载；换 recaptcha.net 域也不保证稳定。",
            "v3 只返回风险分数，阈值与拦截动作要业务自行实现和调优。",
        ],
        pricing={"model": "freemium", "currency": "USD"},
        availability=CN_BLOCKED,
        docsUrl="https://developers.google.com/recaptcha",
        tags=["captcha", "bot", "google", "security"],
        maturity="mature",
    ),
    mk(
        "geetest",
        "极验 GeeTest",
        CAT_BOT,
        "captcha-widget",
        "国内行为验证码 · 滑块/点选多形态 · 境内节点稳 · 本地化支持",
        "https://www.geetest.com",
        "极验（GeeTest）是国内使用面较广的行为验证服务，提供滑动拼图、文字点选、无感验证等多种形态，服务节点与资质在境内，同时也有面向出海业务的海外节点。",
        "国内 App 与网站要在注册、登录、抢购等环节挡住脚本，且要求验证资源加载稳定、能对接本地化风控与人工支持时选它，用来替代加载不畅的 reCAPTCHA。",
        "它只挡自动化，打码平台与真人众包仍能穿透，关键场景要叠加设备指纹与业务规则；海外节点的覆盖与延迟需按目标市场实测。",
        vendorId="geetest-inc",
        pitfalls=[
            "打码平台与众包接单能绕过验证，高价值场景需叠加设备指纹与风控。",
            "海外节点覆盖不如国际厂商，出海业务要按目标市场实测延迟。",
        ],
        pricing={"model": "freemium", "currency": "CNY"},
        availability=DOMESTIC,
        region="domestic",
        tags=["captcha", "bot", "domestic", "security"],
    ),
    mk(
        "friendly-captcha",
        "Friendly Captcha",
        CAT_BOT,
        "captcha-widget",
        "工作量证明验证 · 用户零交互 · 数据留在欧盟 · 无障碍友好",
        "https://friendlycaptcha.com",
        "Friendly Captcha 用浏览器端工作量证明替代图形挑战，用户全程无需点选，服务由德国团队运营且数据处理留在欧盟，常见于对 GDPR 与无障碍要求严格的站点。",
        "欧洲市场站点、政府与公共部门项目，需要可访问性好、数据不出欧盟的人机验证时优先；对抗强度要求高的电商风控另选行为决策类产品。",
        "它只抬高自动化成本，面对定向攻击的防护强度不如商业风控；低端设备上计算挑战会增加等待，移动端体验要实测。",
        vendorId="friendly-captcha-gmbh",
        pitfalls=[
            "面对有算力的定向刷量，工作量证明的拦截效果有限。",
            "老旧移动设备上求解挑战耗时可感知，需实测再全量。",
        ],
        pricing={"model": "freemium", "currency": "EUR"},
        availability=EU_FIRST,
        tags=["captcha", "bot", "privacy", "gdpr"],
    ),
    mk(
        "altcha",
        "ALTCHA",
        CAT_BOT,
        "captcha-widget",
        "开源工作量证明验证码 · 可自托管 · 无第三方请求与 Cookie",
        "https://altcha.org",
        "ALTCHA 是开源的工作量证明人机验证组件，前端 widget 与服务端校验库都能自托管，默认不发起第三方请求、不写 Cookie，也提供可选的托管服务与插件。",
        "自建可控、不愿把用户请求交给第三方验证码厂商，或有数据本地化要求时选它；代价是防护调优与运维要自己承担。",
        "它只抬高脚本成本，挡不住有算力的定向刷量；开源项目的迭代与安全响应依赖社区，生产使用前要盯紧版本与依赖更新。",
        vendorId=None,
        pitfalls=[
            "自托管后规则调优、监控与版本跟进全部由自己承担。",
            "工作量证明对有算力的攻击者威慑有限，高风险场景需叠加风控。",
        ],
        pricing={"model": "open-source"},
        maturity="beta",
        githubUrl="https://github.com/altcha-org/altcha",
        sources=["https://altcha.org", "https://github.com/altcha-org/altcha"],
        tags=["captcha", "bot", "open-source", "self-hosted"],
    ),
    # ——— 自动化流量决策 ———
    mk(
        "arcjet",
        "Arcjet",
        CAT_BOT,
        "bot-defense",
        "开发者向防护 SDK · Bot 检测/限流/邮箱校验一体 · 规则随代码走",
        "https://arcjet.com",
        "Arcjet 以 SDK 形式把 Bot 检测、速率限制、邮箱有效性校验与敏感信息拦截放进应用代码，规则跟着仓库走版本管理，对 Next.js、Node、Bun 等运行时提供一等封装。",
        "前后端同仓、希望防护规则和业务代码一起 review 与灰度，而不是在云控制台点配置时评估；它补的是应用层，不替代边缘 WAF。",
        "产品较新，规则库与生态积累不如老牌厂商厚；防护跑在应用进程内，大流量攻击仍要靠边缘先扛，别把它当 DDoS 方案。",
        vendorId="arcjet-inc",
        pitfalls=[
            "防护逻辑在应用进程内执行，扛不住需要边缘清洗的大流量攻击。",
            "产品仍在快速迭代，API 与规则集变动需跟进版本说明。",
        ],
        pricing={"model": "freemium", "currency": "USD"},
        maturity="beta",
        tags=["bot", "rate-limit", "security", "sdk"],
    ),
    mk(
        "datadome",
        "DataDome",
        CAT_BOT,
        "bot-defense",
        "企业级 Bot 防护 · 边缘毫秒决策 · 必要时才弹验证码",
        "https://datadome.co",
        "DataDome 是企业级 Bot 与自动化欺诈防护，在 CDN 或服务端边缘对每个请求做毫秒级机器学习判定，只在必要时才弹出验证挑战，覆盖爬虫、撞库、抢购囤货与广告作弊。",
        "电商、票务、媒体等被规模化爬虫与自动化下单困扰、单靠验证码已挡不住时评估；它属于流量决策层，比表单验证挂件重得多。",
        "按请求量计价且偏企业采购，小站点成本不划算；误判会直接挡掉真实用户与合作方爬虫，上线务必先跑一段观察模式再开拦截。",
        vendorId="datadome-inc",
        pitfalls=[
            "按请求量计费、走企业采购流程，中小团队性价比不高。",
            "误杀会直接影响真实用户与合作方抓取，需先跑观察模式调参。",
        ],
        pricing={"model": "usage", "currency": "USD"},
        tags=["bot", "security", "enterprise", "fraud"],
    ),
]

ENTRIES_DATA: list[dict] = COMPLIANCE_ENTRIES + BOT_ENTRIES


VENDORS_DATA: list[dict] = [
    vendor("vanta-inc", "Vanta", url="https://www.vanta.com"),
    vendor("drata-inc", "Drata", url="https://drata.com"),
    vendor("secureframe-inc", "Secureframe", url="https://secureframe.com"),
    vendor("sprinto-inc", "Sprinto", url="https://sprinto.com"),
    vendor("onetrust-inc", "OneTrust", url="https://www.onetrust.com"),
    vendor("iubenda-srl", "iubenda", url="https://www.iubenda.com"),
    vendor("termly-inc", "Termly", url="https://termly.io"),
    vendor("usercentrics", "Usercentrics", url="https://usercentrics.com"),
    vendor("hcaptcha-inc", "Intuition Machines (hCaptcha)", url="https://www.hcaptcha.com"),
    vendor("arcjet-inc", "Arcjet", url="https://arcjet.com"),
    vendor("geetest-inc", "极验", region="domestic", url="https://www.geetest.com"),
    vendor("datadome-inc", "DataDome", url="https://datadome.co"),
    vendor("friendly-captcha-gmbh", "Friendly Captcha", url="https://friendlycaptcha.com"),
]


EDGES_DATA: list[dict] = [
    # ——— 合规自动化同层对照 ———
    edge(
        "e-drata-alt-vanta",
        "drata",
        "vanta",
        "alternative_to",
        weight=0.85,
        note="同为合规自动化：Drata 控制测试更细、审计协作区完整；Vanta 集成与审计师生态更广",
    ),
    edge(
        "e-secureframe-alt-vanta",
        "secureframe",
        "vanta",
        "alternative_to",
        weight=0.75,
        note="Secureframe 偏模板+顾问陪跑，首次认证上手更轻；Vanta 集成清单更长",
    ),
    edge(
        "e-sprinto-alt-drata",
        "sprinto",
        "drata",
        "alternative_to",
        weight=0.7,
        note="Sprinto 实施节奏轻、亚太时区响应好；Drata 更适合多框架并行与企业级留痕",
    ),
    # ——— 隐私 / 同意管理同层对照 ———
    edge(
        "e-iubenda-alt-termly",
        "iubenda",
        "termly",
        "alternative_to",
        weight=0.75,
        note="iubenda 偏欧盟 GDPR 与多语种条款；Termly 偏美国州级隐私法口径",
    ),
    edge(
        "e-cookiebot-alt-iubenda",
        "cookiebot",
        "iubenda",
        "alternative_to",
        weight=0.7,
        note="Cookiebot 强在脚本自动扫描与同意日志留痕；iubenda 强在政策文本生成一体化",
    ),
    edge(
        "e-onetrust-alt-cookiebot",
        "onetrust",
        "cookiebot",
        "alternative_to",
        weight=0.65,
        note="OneTrust 是覆盖数据地图与数据主体请求的企业治理套件；Cookiebot 只做 Cookie 同意这一段",
    ),
    # ——— 合规叶内部：安全认证线 vs 隐私治理线 ———
    edge(
        "e-vanta-cuw-onetrust",
        "vanta",
        "onetrust",
        "commonly_used_with",
        weight=0.5,
        note="SOC 2/ISO 认证与隐私同意治理是两条并行的线，大团队常同时铺",
    ),
    # ——— 合规跨叶：主体、扫描工具 ———
    edge(
        "e-vanta-cuw-stripe-atlas",
        "vanta",
        "stripe-atlas",
        "commonly_used_with",
        weight=0.45,
        note="出海路径：先用 Atlas 落地美国主体，再用合规自动化准备客户要的 SOC 2",
    ),
    edge(
        "e-vanta-cuw-snyk",
        "vanta",
        "snyk",
        "commonly_used_with",
        weight=0.5,
        note="合规控制项要求漏洞管理证据，扫描结果常作为 Vanta 的取证来源",
    ),
    edge(
        "e-drata-cuw-sonarqube",
        "drata",
        "sonarqube",
        "commonly_used_with",
        weight=0.4,
        note="代码质量与安全门禁的执行记录，可作为变更管理控制项的证据",
    ),
    # ——— 验证码同层对照 ———
    edge(
        "e-hcaptcha-alt-recaptcha",
        "hcaptcha",
        "recaptcha",
        "alternative_to",
        weight=0.85,
        note="接入方式接近、迁移成本低；hCaptcha 主打不做广告画像，reCAPTCHA 胜在生态与文档",
    ),
    edge(
        "e-cloudflare-turnstile-alt-recaptcha",
        "cloudflare-turnstile",
        "recaptcha",
        "alternative_to",
        weight=0.85,
        note="Turnstile 免打勾、无广告绑定，且在国内可加载；reCAPTCHA 面向大陆用户常卡加载",
    ),
    edge(
        "e-friendly-captcha-alt-hcaptcha",
        "friendly-captcha",
        "hcaptcha",
        "alternative_to",
        weight=0.6,
        note="工作量证明零交互、数据留欧盟；hCaptcha 用挑战题库，对抗强度更高",
    ),
    edge(
        "e-geetest-domeq-recaptcha",
        "geetest",
        "recaptcha",
        "domestic_equivalent_of",
        weight=0.9,
        confidence="verified",
        note="国内镜像位：极验境内节点加载稳、支持本地化风控，替代在大陆加载不畅的 reCAPTCHA",
    ),
    edge(
        "e-altcha-osalt-hcaptcha",
        "altcha",
        "hcaptcha",
        "open_source_alternative_to",
        weight=0.75,
        note="开源自托管、无第三方请求；对抗强度与运营支持不及商业验证码",
    ),
    edge(
        "e-altcha-osalt-cloudflare-turnstile",
        "altcha",
        "cloudflare-turnstile",
        "open_source_alternative_to",
        weight=0.65,
        note="同为低摩擦验证：ALTCHA 全自托管，Turnstile 依赖 Cloudflare 边缘服务",
    ),
    # ——— Bot 决策层对照与层次差异 ———
    edge(
        "e-datadome-alt-arcjet",
        "datadome",
        "arcjet",
        "alternative_to",
        weight=0.6,
        note="DataDome 是边缘企业级流量决策；Arcjet 是写在应用代码里的开发者向 SDK",
    ),
    edge(
        "e-datadome-alt-hcaptcha",
        "datadome",
        "hcaptcha",
        "alternative_to",
        weight=0.45,
        note="层次不同：DataDome 按请求实时判定并按需弹挑战，hCaptcha 只是表单处的验证挂件",
    ),
    # ——— 与 WAF / 边缘防护的层次关系 ———
    edge(
        "e-cloudflare-turnstile-part-cloudflare-cdn",
        "cloudflare-turnstile",
        "cloudflare-cdn",
        "part_of",
        weight=0.9,
        confidence="verified",
        note="Turnstile 属 Cloudflare 应用安全产品线，但可独立于 CDN 单独接入站点",
    ),
    edge(
        "e-cloudflare-turnstile-cuw-cloudflare-waf",
        "cloudflare-turnstile",
        "cloudflare-waf",
        "commonly_used_with",
        weight=0.7,
        note="分层：WAF 在边缘按规则与速率拦截，Turnstile 在表单处判人机，二者叠加不冲突",
    ),
    edge(
        "e-datadome-cuw-aws-waf",
        "datadome",
        "aws-waf",
        "commonly_used_with",
        weight=0.55,
        note="WAF 规则层先过滤已知恶意特征，DataDome 再做行为级 Bot 判定",
    ),
    edge(
        "e-geetest-cuw-edgeone",
        "geetest",
        "edgeone",
        "commonly_used_with",
        weight=0.5,
        note="国内组合：EdgeOne 做边缘防护与限速，极验补表单处的人机验证",
    ),
    # ——— 与应用栈的集成 ———
    edge(
        "e-arcjet-int-nextjs",
        "arcjet",
        "nextjs",
        "integrates_with",
        weight=0.8,
        confidence="verified",
        note="对 Next.js 路由与中间件提供一等封装，防护规则随应用代码部署",
    ),
    edge(
        "e-clerk-int-cloudflare-turnstile",
        "clerk",
        "cloudflare-turnstile",
        "integrates_with",
        weight=0.7,
        note="登录注册流内置的 Bot 防护基于 Turnstile，无需自行嵌 widget",
    ),
    edge(
        "e-auth0-int-recaptcha",
        "auth0",
        "recaptcha",
        "integrates_with",
        weight=0.65,
        note="Auth0 的 Bot Detection 可挂接 reCAPTCHA 挑战；面向大陆用户要注意加载问题",
    ),
    edge(
        "e-friendly-captcha-cuw-cookiebot",
        "friendly-captcha",
        "cookiebot",
        "commonly_used_with",
        weight=0.4,
        note="欧盟站点常见搭配：无 Cookie 的人机验证 + 同意管理，减少同意前的追踪面",
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
    for e in ENTRIES_DATA:
        path = ENTRIES / f"{e['id']}.json"
        if path.exists() and not args.overwrite:
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
            continue
        frm_ok = (ENTRIES / f"{g['from']}.json").exists() or g["from"] in known_new
        to_ok = (ENTRIES / f"{g['to']}.json").exists() or g["to"] in known_new
        if not frm_ok:
            print("skip edge missing from", g["id"], g["from"])
            continue
        if not to_ok:
            print("skip edge missing to", g["id"], g["to"])
            continue
        save(path, g)
        wrote_g += 1
        print("edge", g["id"])

    print(f"done entries={wrote_e} vendors={wrote_v} edges={wrote_g}")


if __name__ == "__main__":
    main()
