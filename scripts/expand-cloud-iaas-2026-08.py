#!/usr/bin/env python3
"""公有云本体与自托管面板扩种（cloud-iaas / cloud-self-host）。

库里长期只有云上单品（aws-s3、aliyun-fc…）而没有云厂商本体，导致「选哪朵云」
这层判断无处落脚，单品也挂不上归属边。本批补齐 14 朵云 + 9 个自托管面板，
并给存量单品补 part_of 归属边。

用法:
  python3 scripts/expand-cloud-iaas-2026-08.py
  python3 scripts/expand-cloud-iaas-2026-08.py --overwrite
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
        "pricing": {"model": "usage"},
        "availability": {
            "chinaAccessible": True,
            "needsCompany": False,
            "needsIcp": False,
            "regions": ["global"],
        },
        "tags": ["cloud"],
        "maturity": "mature",
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


def mk(eid, name, sub, one, url, what, when, caution, cat, **extra):
    pitfalls = extra.pop("pitfalls", None)
    kw = {
        "id": eid,
        "name": name,
        "category": cat,
        "subcategory": sub,
        "oneLiner": one,
        "officialUrl": url,
        "descriptionMd": f"{what}\n\n{when}\n\n{caution}\n",
        "pitfalls": pitfalls or [caution[:90]],
    }
    kw.update(extra)
    return entry(**kw)


def iaas(*a, **kw):
    return mk(*a, cat="cloud-iaas", **kw)


def panel(*a, **kw):
    return mk(*a, cat="cloud-self-host", **kw)


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


DOMESTIC = {"chinaAccessible": True, "needsCompany": True, "needsIcp": True, "regions": ["CN"]}
GLOBAL_OK = {"chinaAccessible": True, "needsCompany": False, "needsIcp": False, "regions": ["global"]}
GLOBAL_HARD = {
    "chinaAccessible": False,
    "needsCompany": False,
    "needsIcp": False,
    "regions": ["global"],
}

ENTRIES_DATA: list[dict] = [
    # ——— 超大规模云 ———
    iaas(
        "aws",
        "AWS",
        "hyperscaler",
        "服务面最广 · 生态与人才最厚；计费维度与 IAM 复杂度也最高",
        "https://aws.amazon.com",
        "AWS 是服务品类最全的公有云，从计算、对象存储到托管数据库、消息队列与模型平台一应俱全，第三方集成与运维人才储备同样最厚。",
        "跨区域部署、需要齐全合规资质、或团队已有 AWS 经验时的稳妥默认解；栈中通常与 aws-lambda、aws-s3、amazon-rds 这些单品一起出现。",
        "服务命名与计费维度极碎，**出网与跨可用区流量**常是账单意外的来源；中国区由本地伙伴独立运营，账号与服务清单和 Global 并不互通。",
        vendorId="amazon",
        pricing={"model": "usage", "currency": "USD"},
        availability=GLOBAL_OK,
        tags=["cloud", "iaas", "hyperscaler", "enterprise"],
        pitfalls=[
            "出网与跨可用区流量费常被低估",
            "中国区由本地伙伴独立运营，服务清单与 Global 不同步",
        ],
    ),
    iaas(
        "google-cloud",
        "Google Cloud",
        "hyperscaler",
        "数据与 AI 一等公民 · BigQuery/Vertex 强；大陆直连受限",
        "https://cloud.google.com",
        "Google Cloud 以数据分析与 AI 见长，BigQuery、Vertex AI 与 Kubernetes 相关能力是主要卖点，网络与全球调度素质也在第一梯队。",
        "做大规模数据分析、想用 Gemini 系模型托管、或团队偏好 GKE 时优先评估；与 google-cloud-run、bigquery 等单品同栈。",
        "中国大陆直连不稳，控制台与部分 API 需自备网络方案；产品线更迭较快，早期服务被弃用的历史让部分团队心存顾虑。",
        vendorId="google",
        pricing={"model": "usage", "currency": "USD"},
        availability=GLOBAL_HARD,
        tags=["cloud", "iaas", "hyperscaler", "data"],
        pitfalls=[
            "中国大陆访问不稳，需自备网络方案",
            "历史上有服务下线记录，长周期项目需看产品承诺",
        ],
    ),
    iaas(
        "azure",
        "Microsoft Azure",
        "hyperscaler",
        "贴合 AD/Office 企业生态 · Azure OpenAI 独立档位与配额",
        "https://azure.microsoft.com",
        "Azure 与 Entra ID（原 Azure AD）、Microsoft 365 及 Windows 体系深度咬合，企业采购与身份治理路径顺畅，Azure OpenAI 亦是独立的模型接入通道。",
        "企业已在微软生态、需要合规采购通道、或要以独立配额调用 OpenAI 系模型时优先；常与 azure-openai、azure-functions 同栈。",
        "门户信息密度高、术语自成一套，学习成本不低；中国区由世纪互联独立运营，功能与 Global 存在时间差。",
        vendorId="microsoft",
        pricing={"model": "usage", "currency": "USD"},
        availability=GLOBAL_OK,
        tags=["cloud", "iaas", "hyperscaler", "enterprise"],
        pitfalls=[
            "中国区由世纪互联运营，功能落后 Global 若干版本",
            "Azure OpenAI 配额需单独申请，非开通即用",
        ],
    ),
    # ——— 国内综合云 ———
    iaas(
        "aliyun",
        "阿里云",
        "domestic-hyperscaler",
        "国内服务面最全 · 文档与工单成熟；备案与实名是前置",
        "https://www.aliyun.com",
        "阿里云是国内产品线最完整的公有云，计算、存储、数据库、CDN 到通义系模型与 PAI 平台自成闭环，中文文档与工单体系也相对成熟。",
        "面向国内用户、要走备案与合规路径、或已在用 aliyun-oss / aliyun-fc 等单品时的默认解；出海业务可用其国际站但要另算账号体系。",
        "国内 Web 服务必须完成 ICP 备案，主体与域名需实名；促销价与续费价差距明显，长期成本要按标准价测算。",
        vendorId="alibaba",
        pricing={"model": "usage", "currency": "CNY"},
        availability=DOMESTIC,
        region="domestic",
        tags=["cloud", "iaas", "domestic", "hyperscaler"],
        pitfalls=[
            "国内 Web 服务需先完成 ICP 备案",
            "首购促销价与续费价差距大，按标准价测算长期成本",
        ],
    ),
    iaas(
        "tencent-cloud",
        "腾讯云",
        "domestic-hyperscaler",
        "微信/小程序链路顺 · 音视频与 IM 强；备案同样前置",
        "https://cloud.tencent.com",
        "腾讯云在音视频、实时通信与微信生态打通上有天然优势，云开发（CloudBase）让小程序后端几乎零运维，混元系模型与文档能力也在其内。",
        "做小程序、公众号或音视频业务时优先；与 tencent-cloudbase、tencent-cos、tencent-trtc 这些单品天然同栈。",
        "国内 Web 服务同样需要备案；部分产品线更新节奏与文档完备度不及阿里云，选冷门服务前先看控制台实际可用性。",
        vendorId="tencent",
        pricing={"model": "usage", "currency": "CNY"},
        availability=DOMESTIC,
        region="domestic",
        tags=["cloud", "iaas", "domestic", "wechat"],
        pitfalls=[
            "国内 Web 服务需先完成 ICP 备案",
            "冷门产品线文档与迭代不如主力线，选型前核实控制台现状",
        ],
    ),
    iaas(
        "huawei-cloud",
        "华为云",
        "domestic-hyperscaler",
        "政企与信创路径顺 · 鲲鹏/昇腾自有芯；生态偏企业侧",
        "https://www.huaweicloud.com",
        "华为云在政企、信创与国产化替代路径上准备最足，鲲鹏与昇腾芯片形成自有算力栈，盘古系模型与鸿蒙生态亦在同一体系内。",
        "项目对信创合规、国产芯片或政企采购有硬性要求时优先；做鸿蒙应用可与 huawei-agc 一并考虑。",
        "面向个人开发者的自助体验与社区活跃度弱于阿里云、腾讯云；不少能力偏解决方案交付而非自助开通，采购与实施周期要提前预留。",
        vendorId="huawei",
        pricing={"model": "usage", "currency": "CNY"},
        availability=DOMESTIC,
        region="domestic",
        tags=["cloud", "iaas", "domestic", "enterprise"],
        pitfalls=[
            "个人开发者自助体验与社区活跃度偏弱",
            "部分能力走解决方案交付，非开箱自助",
        ],
    ),
    iaas(
        "volcengine",
        "火山引擎",
        "domestic-hyperscaler",
        "字节自用技术外供 · 豆包与推荐/视频链路强；起步较晚",
        "https://www.volcengine.com",
        "火山引擎把字节内部的推荐、视频与大模型技术对外输出，豆包系模型、视频云与增长分析是主要抓手，价格策略也较进取。",
        "要用豆包系模型、做内容/视频类业务或看重增长分析工具链时评估；与 volcengine-speech、doubao 系条目同栈。",
        "起步晚于阿里云、腾讯云，通用 IaaS 的区域与产品广度仍在补齐；部分能力需商务对接而非自助开通。",
        vendorId="bytedance",
        pricing={"model": "usage", "currency": "CNY"},
        availability=DOMESTIC,
        region="domestic",
        tags=["cloud", "iaas", "domestic", "ai"],
        pitfalls=[
            "通用 IaaS 的区域与产品广度仍在补齐",
            "部分能力需商务对接，非自助开通",
        ],
    ),
    # ——— 开发者友好型云 ———
    iaas(
        "digitalocean",
        "DigitalOcean",
        "developer-cloud",
        "定价直白可预估 · 文档教程一流；企业级服务面较窄",
        "https://www.digitalocean.com",
        "DigitalOcean 面向开发者与中小团队，Droplet、托管数据库与 Spaces 的定价直白可预估，社区教程质量长期是同行标杆。",
        "个人项目、小团队 SaaS 或不想被超大规模云账单吓到时优先；与 digitalocean-app-platform、digitalocean-spaces 同栈。",
        "企业级服务面（专线、复杂合规、区域覆盖）明显窄于超大规模云；业务长到一定规模后迁移成本要提前想清。",
        vendorId="digitalocean-inc",
        pricing={"model": "usage", "currency": "USD"},
        availability=GLOBAL_OK,
        tags=["cloud", "iaas", "developer", "vps"],
        pitfalls=["企业级服务面与区域覆盖窄于超大规模云", "规模上去后迁移成本需提前评估"],
    ),
    iaas(
        "hetzner",
        "Hetzner",
        "developer-cloud",
        "欧洲机房性价比标杆 · 独服/云主机便宜；风控偏严",
        "https://www.hetzner.com",
        "Hetzner 是德国老牌托管商，云主机与独立服务器的性价比长期是行业参照点，欧洲机房网络质量稳定，也提供对象存储与备份。",
        "预算敏感、用户主要在欧洲、或要跑自托管服务与 GPU 之外的常驻负载时优先；常配 Coolify、Dokploy 这类面板自建 PaaS。",
        "开户风控偏严，新账号可能被要求补充身份材料；托管服务面窄，数据库与队列多需自己运维。",
        vendorId="hetzner-inc",
        pricing={"model": "usage", "currency": "EUR"},
        availability=GLOBAL_OK,
        tags=["cloud", "iaas", "vps", "value"],
        pitfalls=["新账号风控偏严，可能要求补充身份材料", "托管型服务少，中间件基本要自运维"],
    ),
    iaas(
        "vultr",
        "Vultr",
        "developer-cloud",
        "全球节点多 · 按小时计费灵活；托管服务面较薄",
        "https://www.vultr.com",
        "Vultr 提供覆盖面广的云主机与裸金属节点，按小时计费、开机即用，近年也补上了托管 Kubernetes 与 GPU 实例。",
        "需要在冷门地区落节点、做多地部署测试或短期算力时评估；与 DigitalOcean、Linode 属同层可直接横比。",
        "托管型中间件与数据库选择少，运维仍靠自己；部分节点的网络质量随机房差异明显，上线前先实测。",
        vendorId="vultr-inc",
        pricing={"model": "usage", "currency": "USD"},
        availability=GLOBAL_OK,
        tags=["cloud", "iaas", "vps", "global"],
        pitfalls=["托管型中间件少，运维靠自己", "各机房网络质量差异明显，上线前实测"],
    ),
    iaas(
        "linode",
        "Akamai Linode",
        "developer-cloud",
        "并入 Akamai 后接边缘网络 · 老牌 VPS 心智；产品迭代偏稳",
        "https://www.linode.com",
        "Linode 是老牌开发者 VPS 品牌，被 Akamai 收购后与其边缘网络与安全能力整合，定价结构依旧简单直白。",
        "看重稳定与简单计价、又希望顺带用上 Akamai 边缘分发时评估；与 DigitalOcean、Vultr 同层可直接横比。",
        "产品迭代节奏偏稳，新兴能力（如 GPU、Serverless）跟进慢于超大规模云；品牌整合期文档与控制台入口有新旧并存。",
        vendorId="akamai",
        pricing={"model": "usage", "currency": "USD"},
        availability=GLOBAL_OK,
        tags=["cloud", "iaas", "vps", "edge"],
        pitfalls=["新兴能力跟进慢于超大规模云", "品牌整合期文档与入口新旧并存"],
    ),
    iaas(
        "ovhcloud",
        "OVHcloud",
        "developer-cloud",
        "欧洲主权云取向 · 自有机房与裸金属；控制台体验一般",
        "https://www.ovhcloud.com",
        "OVHcloud 是法国大型托管商，自建机房与裸金属规模可观，主打欧洲数据主权与本地合规，同时提供公有云与私有云托管。",
        "业务需落在欧盟境内、对数据主权有明确要求，或需要成规模裸金属而非弹性实例时评估；也常被当作 Hetzner 之外的第二欧洲选项。",
        "控制台与文档体验不如英美同行顺手；历史上有机房火灾导致数据丢失的事故，备份策略必须自己做实。",
        vendorId="ovhcloud-inc",
        pricing={"model": "usage", "currency": "EUR"},
        availability=GLOBAL_OK,
        tags=["cloud", "iaas", "europe", "bare-metal"],
        pitfalls=["控制台与文档体验一般", "历史机房事故提醒：异地备份必须自建"],
    ),
    iaas(
        "oracle-cloud",
        "Oracle Cloud",
        "developer-cloud",
        "永久免费额度大方 · Arm 实例慷慨；开通与风控门槛高",
        "https://www.oracle.com/cloud",
        "Oracle Cloud Infrastructure 以慷慨的永久免费额度（尤其 Arm 计算）在开发者中出名，企业侧则主打 Oracle 数据库与 ERP 同栈。",
        "想低成本跑常驻小服务、或企业已深度使用 Oracle 数据库时评估。",
        "免费实例常因区域容量不足而长期开不出来，账号也可能因风控被回收；控制台概念（区间、策略）自成一套，上手成本高。",
        vendorId="oracle",
        pricing={"model": "usage", "currency": "USD"},
        availability=GLOBAL_OK,
        tags=["cloud", "iaas", "free-tier", "enterprise"],
        pitfalls=[
            "免费 Arm 实例常因容量不足开不出来",
            "风控较严，账号存在被回收的社区反馈",
        ],
    ),
    iaas(
        "scaleway",
        "Scaleway",
        "developer-cloud",
        "法国云 · Serverless 与 GPU 起步早；区域集中在欧洲",
        "https://www.scaleway.com",
        "Scaleway 是法国云厂商，在 Serverless 容器、托管 Kubernetes 与 GPU 实例上动作较早，定价与控制台对开发者友好。",
        "业务面向欧洲、想要欧盟主体的云服务，或要用其 Serverless 与 GPU 能力时评估；与 scaleway-serverless 同栈。",
        "区域基本集中在欧洲，亚太与美洲覆盖有限；生态与第三方集成远不如超大规模云丰富。",
        vendorId="scaleway-inc",
        pricing={"model": "usage", "currency": "EUR"},
        availability=GLOBAL_OK,
        tags=["cloud", "iaas", "europe", "serverless"],
        pitfalls=["区域集中欧洲，亚太覆盖有限", "第三方生态集成少于超大规模云"],
    ),
    # ——— 自托管面板 ———
    panel(
        "dokploy",
        "Dokploy",
        "self-hosted-paas",
        "Docker/Compose 原生 · 多服务器纳管；社区年轻",
        "https://dokploy.com",
        "Dokploy 是开源自托管 PaaS，把 VPS 变成带 Git 部署、域名与证书自动化的应用平台，原生支持 Docker Compose 与多服务器纳管。",
        "想在 Hetzner、Vultr 这类便宜 VPS 上获得近似 Vercel 的部署体验、又不愿被平台计价绑定时评估。",
        "项目年轻、版本迭代快，升级前务必备份；平台可用性由你自己负责，出问题没有 SLA 兜底。",
        pricing={"model": "open-source"},
        maturity="beta",
        availability=GLOBAL_OK,
        tags=["self-hosted", "paas", "docker", "open-source"],
        pitfalls=["项目年轻、迭代快，升级前先备份", "无 SLA，可用性由自己兜底"],
    ),
    panel(
        "dokku",
        "Dokku",
        "self-hosted-paas",
        "单机 Heroku 心智 · git push 部署；插件即能力边界",
        "https://dokku.com",
        "Dokku 是最早一批「迷你 Heroku」，用 Buildpack 与 git push 完成部署，插件体系覆盖数据库、证书与备份，占用极轻。",
        "单台服务器上跑若干小应用、喜欢 Heroku 那套心智又想自己掌控成本与数据时评估；也常作为学习容器化部署的过渡。",
        "多机编排与图形界面不是它的强项；能力上限基本由插件生态决定，冷门需求要自己写插件。",
        pricing={"model": "open-source"},
        maturity="stable",
        availability=GLOBAL_OK,
        tags=["self-hosted", "paas", "buildpack", "open-source"],
        pitfalls=["多机编排能力弱，偏单机场景", "能力受插件生态限制"],
    ),
    panel(
        "portainer",
        "Portainer",
        "container-ui",
        "容器与 K8s 图形管控 · 不做构建；偏运维视角",
        "https://www.portainer.io",
        "Portainer 给 Docker、Swarm 与 Kubernetes 提供图形化管控台，覆盖容器、镜像、卷、网络与权限，社区版免费、商业版补企业治理。",
        "已有容器环境、需要一个可视化面板给团队用，而不是要一套「从 Git 到上线」的部署流水线时选它。",
        "它不负责构建与 CI，Git 到镜像那段仍要另配；社区版与商业版功能边界需事先看清，别在 POC 后才发现要付费。",
        pricing={"model": "freemium"},
        maturity="mature",
        availability=GLOBAL_OK,
        tags=["self-hosted", "docker", "kubernetes", "ops"],
        pitfalls=["不含构建与 CI，需另配流水线", "社区版与商业版功能边界要提前确认"],
    ),
    panel(
        "1panel",
        "1Panel",
        "domestic-panel",
        "国产现代面板 · 容器优先/应用商店；社区偏国内",
        "https://1panel.cn",
        "1Panel 是飞致云开源的现代化 Linux 运维面板，以容器为一等公民，配套应用商店可一键装常见开源服务，中文界面与文档完整。",
        "国内服务器上要一个比宝塔更贴近容器时代的面板、又希望中文支持到位时评估；也常被用来托管开源自建服务。",
        "社区与插件生态以国内为主，英文材料少；面板本身暴露在公网是常见风险面，务必限制访问来源并及时升级。",
        pricing={"model": "open-source", "currency": "CNY"},
        maturity="stable",
        availability={"chinaAccessible": True, "needsCompany": False, "needsIcp": False, "regions": ["CN"]},
        region="domestic",
        tags=["self-hosted", "panel", "domestic", "open-source"],
        pitfalls=["面板暴露公网风险大，需限制来源并及时升级", "英文材料与海外社区少"],
    ),
    panel(
        "baota",
        "宝塔面板",
        "domestic-panel",
        "国内装机量大 · LNMP 一键起；插件商业化与安全争议并存",
        "https://www.bt.cn",
        "宝塔面板是国内使用面极广的服务器运维面板，一键部署 LNMP/LAMP、站点、数据库与证书，把传统虚拟主机的操作习惯搬到了 VPS 上。",
        "面向国内、以 PHP/传统 Web 栈为主、需要快速把站点跑起来且团队习惯图形操作时评估。",
        "历史上出现过面板自身的安全漏洞与默认端口暴露事件；不少能力走付费插件，长期成本要算进来。",
        pricing={"model": "freemium", "currency": "CNY"},
        maturity="mature",
        availability={"chinaAccessible": True, "needsCompany": False, "needsIcp": False, "regions": ["CN"]},
        region="domestic",
        tags=["self-hosted", "panel", "domestic", "lnmp"],
        pitfalls=[
            "历史上有面板自身安全漏洞，须及时升级并限制访问",
            "较多能力依赖付费插件",
        ],
    ),
    panel(
        "cloudron",
        "Cloudron",
        "app-hosting",
        "自托管应用商店 · 备份/账号统一托管；按应用数收费",
        "https://www.cloudron.io",
        "Cloudron 把自托管做成「应用商店 + 平台」：应用一键安装，账号、备份、证书与更新由平台统一管理，运维心智接近托管 SaaS。",
        "想自建一套 Nextcloud、邮件、Wiki 等内部服务，又不愿逐个折腾配置与备份时评估。",
        "面向的是打包好的应用而非自研代码部署；按应用数量收费，装得多成本不低，且离开平台迁移不算轻松。",
        pricing={"model": "subscription", "currency": "USD"},
        maturity="stable",
        availability=GLOBAL_OK,
        tags=["self-hosted", "app-store", "backup", "ops"],
        pitfalls=["面向打包应用，不适合自研代码部署", "按应用数收费，规模上去成本明显"],
    ),
    panel(
        "easypanel",
        "Easypanel",
        "self-hosted-paas",
        "界面清爽的单机 PaaS · 模板丰富；商业授权非开源",
        "https://easypanel.io",
        "Easypanel 在单台服务器上提供接近托管 PaaS 的体验：Git 部署、数据库模板、域名证书与监控都在一个清爽界面里。",
        "只有一两台服务器、想尽快获得部署体验又不愿啃 Docker 细节时评估；与 Dokploy、Coolify 属同层可直接横比。",
        "并非完全开源，商业授权与免费额度的边界要先看清；单机取向决定了横向扩展能力有限。",
        pricing={"model": "freemium", "currency": "USD"},
        maturity="stable",
        availability=GLOBAL_OK,
        tags=["self-hosted", "paas", "docker", "ui"],
        pitfalls=["非完全开源，授权边界需先确认", "单机取向，横向扩展能力有限"],
    ),
    panel(
        "yunohost",
        "YunoHost",
        "app-hosting",
        "个人自主托管发行版 · 邮件/账号开箱；面向自建而非生产",
        "https://yunohost.org",
        "YunoHost 是面向个人自主托管的 Debian 衍生发行版，内置账号体系、邮件与应用目录，让非专业运维者也能在家用机或小 VPS 上跑起自己的服务。",
        "做个人数字主权实践、家庭服务器或小型社群服务时评估；与 Cloudron 的差别在于完全免费但要多担一些运维。",
        "定位是个人自建而非商业生产环境，性能与高可用不在设计目标内；自建邮件的投递率问题依旧要自己面对。",
        pricing={"model": "open-source"},
        maturity="stable",
        availability=GLOBAL_OK,
        tags=["self-hosted", "personal", "debian", "open-source"],
        pitfalls=["面向个人自建，不以生产高可用为目标", "自建邮件投递率仍需自行解决"],
    ),
    panel(
        "plesk",
        "Plesk",
        "hosting-panel",
        "老牌商业主机面板 · 多站点/多租户成熟；按许可证计费",
        "https://www.plesk.com",
        "Plesk 是老牌商业主机控制面板，覆盖多站点托管、邮件、DNS、备份与多租户权限，在主机商与代运维场景中长期是标准件。",
        "要给客户做多租户虚拟主机托管、或接手已用 Plesk 的存量环境时评估；自研应用部署更适合看 Dokploy 这类现代面板。",
        "按许可证订阅计费，成本随站点与功能档位上涨；心智偏传统主机运维，与容器化工作流不太合拍。",
        pricing={"model": "subscription", "currency": "USD"},
        maturity="mature",
        availability=GLOBAL_OK,
        tags=["hosting", "panel", "multi-tenant", "commercial"],
        pitfalls=["按许可证计费，成本随档位上涨", "心智偏传统主机，与容器工作流不合拍"],
    ),
]

VENDORS_DATA: list[dict] = [
    vendor("hetzner-inc", "Hetzner Online", url="https://www.hetzner.com"),
    vendor("vultr-inc", "Vultr", url="https://www.vultr.com"),
    vendor("akamai", "Akamai", url="https://www.akamai.com"),
    vendor("ovhcloud-inc", "OVHcloud", url="https://www.ovhcloud.com"),
    vendor("scaleway-inc", "Scaleway", url="https://www.scaleway.com"),
]

# 云上单品 -> 云本体（part_of）；不存在的 from 会被自动跳过
MEMBERS: dict[str, list[str]] = {
    "aws": [
        "aws-s3", "aws-lambda", "aws-cloudfront", "aws-ses", "aws-msk",
        "aws-secrets-manager", "aws-waf", "aws-app-runner", "aws-elastic-beanstalk",
        "aws-amplify", "aws-bedrock", "aws-textract", "amazon-polly",
        "amazon-transcribe", "amazon-elasticache", "amazon-rds", "aurora-mysql",
        "dynamodb", "route53",
    ],
    "google-cloud": [
        "google-cloud-run", "google-cloud-sql", "google-cloud-storage",
        "google-cloud-speech", "google-cloud-dns", "google-document-ai",
        "google-vision-ocr", "vertex-ai", "google-app-engine",
    ],
    "azure": [
        "azure-functions", "azure-blob-storage", "azure-database-postgresql",
        "azure-document-intelligence", "azure-openai", "azure-speech",
        "azure-static-web",
    ],
    "aliyun": [
        "aliyun-oss", "aliyun-fc", "aliyun-cdn", "aliyun-esa", "aliyun-ocr",
        "aliyun-sms", "aliyun-directmail", "aliyun-wanwang", "aliyun-sls",
        "aliyun-pai", "aliyun-content-safety",
    ],
    "tencent-cloud": [
        "tencent-cos", "tencent-scf", "tencent-cloudbase", "tencent-ocr",
        "tencent-sms", "tencent-speech", "tencent-trtc", "tencent-cls", "edgeone",
    ],
    "huawei-cloud": ["huawei-ocr", "huawei-agc"],
    "volcengine": ["volcengine-fcn", "volcengine-speech", "volcengine-avatar", "datatester"],
    "digitalocean": ["digitalocean-app-platform", "digitalocean-spaces"],
    "scaleway": ["scaleway-serverless"],
}

EDGES_DATA: list[dict] = [
    # 超大规模云互比
    edge("e-aws-alt-google-cloud", "aws", "google-cloud", "alternative_to",
         note="服务广度与生态 vs 数据分析与 AI 取向", weight=0.8),
    edge("e-aws-alt-azure", "aws", "azure", "alternative_to",
         note="独立云生态 vs 企业微软生态内采购", weight=0.8),
    edge("e-google-cloud-alt-azure", "google-cloud", "azure", "alternative_to",
         note="数据/AI 强项 vs 身份治理与合规采购", weight=0.7),
    # 国内 ↔ 海外镜像
    edge("e-aliyun-dom-aws", "aliyun", "aws", "domestic_equivalent_of",
         note="国内服务面最全的综合云，对标 AWS 的通用云位置", weight=0.85),
    edge("e-tencent-cloud-dom-aws", "tencent-cloud", "aws", "domestic_equivalent_of",
         note="国内综合云；音视频与微信链路是其差异点", weight=0.75),
    edge("e-huawei-cloud-dom-azure", "huawei-cloud", "azure", "domestic_equivalent_of",
         note="政企与合规采购路径的国内对应", weight=0.7),
    edge("e-volcengine-dom-google-cloud", "volcengine", "google-cloud", "domestic_equivalent_of",
         note="以自研 AI 与数据能力外供，对应 GCP 的取向", weight=0.65),
    # 国内三云互比
    edge("e-aliyun-alt-tencent-cloud", "aliyun", "tencent-cloud", "alternative_to",
         note="产品面最全 vs 微信/音视频链路顺", weight=0.8),
    edge("e-aliyun-alt-huawei-cloud", "aliyun", "huawei-cloud", "alternative_to",
         note="通用云主力 vs 信创与政企路径", weight=0.7),
    edge("e-tencent-cloud-alt-volcengine", "tencent-cloud", "volcengine", "alternative_to",
         note="老牌综合云 vs 后发的 AI/内容取向云", weight=0.65),
    # 开发者云互比
    edge("e-digitalocean-alt-vultr", "digitalocean", "vultr", "alternative_to",
         note="文档与生态更厚 vs 节点覆盖更广", weight=0.75),
    edge("e-digitalocean-alt-linode", "digitalocean", "linode", "alternative_to",
         note="同层开发者 VPS；Linode 侧接 Akamai 边缘", weight=0.75),
    edge("e-hetzner-alt-ovhcloud", "hetzner", "ovhcloud", "alternative_to",
         note="欧洲性价比 vs 欧洲主权云与裸金属规模", weight=0.7),
    edge("e-hetzner-alt-vultr", "hetzner", "vultr", "alternative_to",
         note="单价更低但区域集中 vs 全球节点多", weight=0.65),
    edge("e-scaleway-alt-hetzner", "scaleway", "hetzner", "alternative_to",
         note="托管服务更全 vs 裸机性价比更高", weight=0.65),
    edge("e-oracle-cloud-alt-digitalocean", "oracle-cloud", "digitalocean", "alternative_to",
         note="免费额度诱人但开通与风控门槛高", weight=0.55),
    # 跨叶：云本体 ↔ PaaS
    edge("e-vercel-built-on-aws", "vercel", "aws", "built_on",
         note="托管平台跑在超大规模云之上，选 PaaS 不等于绕开底层云", weight=0.6),
    edge("e-aws-alt-vercel", "aws", "vercel", "alternative_to",
         note="自己拼装 vs 平台化托管；心智与账单结构完全不同", weight=0.6),
    # 自托管面板
    edge("e-dokploy-alt-coolify", "dokploy", "coolify", "alternative_to",
         note="同为开源自托管 PaaS，Compose 原生 vs 功能面更全", weight=0.8),
    edge("e-dokploy-oss-vercel", "dokploy", "vercel", "open_source_alternative_to",
         note="自备服务器换取无平台计价与冷启动限制", weight=0.7),
    edge("e-dokku-oss-heroku", "dokku", "heroku", "open_source_alternative_to",
         note="Buildpack 与 git push 心智的自托管版", weight=0.8),
    edge("e-dokku-alt-dokploy", "dokku", "dokploy", "alternative_to",
         note="命令行单机 vs 图形界面多机", weight=0.7),
    edge("e-easypanel-alt-dokploy", "easypanel", "dokploy", "alternative_to",
         note="商业授权单机 vs 完全开源多机", weight=0.7),
    edge("e-1panel-dom-plesk", "1panel", "plesk", "domestic_equivalent_of",
         note="国产容器优先面板，对应老牌商业主机面板的位置", weight=0.6),
    edge("e-baota-alt-1panel", "baota", "1panel", "alternative_to",
         note="传统 LNMP 心智 vs 容器优先；同为国内主力面板", weight=0.8),
    edge("e-portainer-alt-1panel", "portainer", "1panel", "alternative_to",
         note="纯容器管控 vs 面板 + 应用商店", weight=0.6),
    edge("e-portainer-cuw-docker", "portainer", "docker", "commonly_used_with",
         note="给 Docker 环境补一层图形管控", weight=0.8),
    edge("e-cloudron-alt-yunohost", "cloudron", "yunohost", "alternative_to",
         note="订阅制托管体验 vs 完全免费的个人自建发行版", weight=0.7),
    edge("e-coolify-cuw-hetzner", "coolify", "hetzner", "commonly_used_with",
         note="便宜 VPS + 自托管 PaaS 是常见的省钱组合", weight=0.7),
    edge("e-dokploy-cuw-hetzner", "dokploy", "hetzner", "commonly_used_with",
         note="同上：把独服变成可 git 部署的平台", weight=0.65),
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

    all_edges = list(EDGES_DATA)
    for cloud, members in MEMBERS.items():
        for m in members:
            all_edges.append(
                edge(
                    f"e-{m}-part-of-{cloud}",
                    m,
                    cloud,
                    "part_of",
                    weight=0.9,
                    confidence="verified",
                    note="该云厂商旗下产品",
                )
            )

    skipped = []
    for g in all_edges:
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
