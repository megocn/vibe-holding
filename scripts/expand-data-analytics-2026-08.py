#!/usr/bin/env python3
"""检索 / 分析 / 时序三叶扩种（db-search · db-analytics · db-timeseries）。

- 检索：Algolia / OpenSearch / Solr / Manticore / Orama / Pagefind / ZincSearch / Quickwit / 阿里云 OpenSearch
- 分析：ClickHouse / DuckDB / Doris / StarRocks / Databend / MotherDuck / BigQuery / Snowflake / Redshift / Hologres
- 时序：InfluxDB / QuestDB / VictoriaMetrics / TDengine / GreptimeDB / IoTDB

用法:
  python3 scripts/expand-data-analytics-2026-08.py
  python3 scripts/expand-data-analytics-2026-08.py --overwrite
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

CAT_SEARCH = "db-search"
CAT_OLAP = "db-analytics"
CAT_TS = "db-timeseries"


def save(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def entry(**kw) -> dict:
    e = {
        "pricing": {"model": "open-source"},
        "availability": {
            "chinaAccessible": True,
            "needsCompany": False,
            "needsIcp": False,
            "regions": ["global"],
        },
        "tags": ["database", "oss"],
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
    body = e["descriptionMd"].strip()
    assert 160 <= len(body) <= 380, (e["id"], len(body))
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


GLOBAL_BLOCKED = {
    "chinaAccessible": False,
    "needsCompany": False,
    "needsIcp": False,
    "regions": ["global"],
}

DOMESTIC = {
    "chinaAccessible": True,
    "needsCompany": False,
    "needsIcp": False,
    "regions": ["CN"],
}

DOMESTIC_CLOUD = {
    "chinaAccessible": True,
    "needsCompany": True,
    "needsIcp": False,
    "regions": ["CN"],
}


SEARCH_ENTRIES: list[dict] = [
    mk(
        "algolia",
        "Algolia",
        CAT_SEARCH,
        "hosted-search",
        "托管检索 SaaS · 排序规则可视化配置 · InstantSearch 前端组件齐",
        "https://www.algolia.com",
        "Algolia 是托管式站内搜索服务：索引与查询全部托管在其云上，排序、同义词与业务规则在后台配置，前端配套 InstantSearch 组件库，把自动补全、分面筛选做成开箱即用的产品能力。",
        "电商与内容站要快速上线站内搜索、团队不想承担集群运维时优先；日志检索与大规模聚合分析仍看 Elasticsearch 一侧。",
        "计费与记录条数、检索次数强相关，流量涨上去成本敏感；排序规则与前端组件都绑在平台上，迁出等于重做检索层。",
        pitfalls=["按记录数与检索量计费，规模上来后成本跳升", "排序规则与前端组件绑定平台，迁移成本高"],
        vendorId="algolia-inc",
        pricing={"model": "subscription", "currency": "USD"},
        maturity="mature",
        tags=["search", "saas", "hosted", "frontend"],
    ),
    mk(
        "opensearch",
        "OpenSearch",
        CAT_SEARCH,
        "search-cluster",
        "Elasticsearch 7.10 分叉 · Apache-2.0 授权 · 含 Dashboards 套件",
        "https://opensearch.org",
        "OpenSearch 是 2021 年从 Elasticsearch 7.10 分叉出的开源检索与分析套件，含可视化端 OpenSearch Dashboards，采用 Apache-2.0 协议并交由基金会治理，云厂商多提供同源托管形态。",
        "要 ELK 式全文检索与日志分析、又希望规避商业授权约束时选它；已在 AWS 栈内的日志平台通常默认走这条线。",
        "与 Elasticsearch 新版能力已明显分叉，插件、客户端与查询特性并不通用；升级或双栈并存前先核对版本矩阵。",
        pitfalls=["与 Elasticsearch 新版特性分叉，客户端不通用", "集群容量与分片规划仍需专门运维"],
        maturity="mature",
        tags=["search", "open-source", "log", "analytics"],
    ),
    mk(
        "apache-solr",
        "Apache Solr",
        CAT_SEARCH,
        "search-cluster",
        "老牌 Lucene 检索服务 · 分面与打分可控 · SolrCloud 依赖 ZooKeeper",
        "https://solr.apache.org",
        "Apache Solr 是 Lucene 之上的老牌开源检索服务器，以显式索引结构定义、分面检索与丰富的查询解析器见长；集群形态 SolrCloud 依靠 ZooKeeper 做分片协调与选主。",
        "已有 Java 企业检索资产、需要精细可控的打分与分面，或做目录、文献、政企内检索时评估。",
        "云上托管选择与社区热度都少于 Elasticsearch；额外维护 ZooKeeper 是实打实的成本，新项目要先掂量团队熟悉度。",
        pitfalls=["SolrCloud 需额外维护 ZooKeeper", "托管服务与新生代生态支持少于 Elasticsearch"],
        maturity="mature",
        tags=["search", "open-source", "java", "lucene"],
    ),
    mk(
        "manticore-search",
        "Manticore Search",
        CAT_SEARCH,
        "search-engine",
        "Sphinx 血统 C++ 引擎 · MySQL 协议直接查 · 单机资源占用低",
        "https://manticoresearch.com",
        "Manticore Search 由 Sphinx 分支演进而来，用 C++ 实现全文检索内核，既能通过 MySQL 协议以 SQL 语法查询，也提供 HTTP JSON 接口，定位是轻量、低资源占用的自托管检索引擎。",
        "单机或小集群、希望沿用 SQL 心智做全文检索、又在意内存与 CPU 开销时评估。",
        "社区与插件生态远小于 Elasticsearch，托管服务选择少；中文分词与业务排序方案需要自己验证落地。",
        pitfalls=["生态与社区规模小，问题排查资料少", "中文分词与排序需自行验证"],
        vendorId="manticore-software",
        maturity="stable",
        tags=["search", "open-source", "sql", "self-hosted"],
    ),
    mk(
        "orama",
        "Orama",
        CAT_SEARCH,
        "embedded-search",
        "TypeScript 内嵌检索 · 浏览器与边缘可跑 · 全文加向量混合查",
        "https://orama.com",
        "Orama 是用 TypeScript 写的轻量搜索引擎，索引可以直接跑在浏览器、Node 与边缘运行时里，支持全文、向量与混合检索，另有面向团队的云端托管产品线。",
        "文档站与前端应用要把小体量索引随包分发，或在 Serverless、边缘节点就近完成检索时选它。",
        "索引需要整体装入内存，语料一大就不适用；开源核心与云服务能力有差别，API 迭代较快，升级要读变更说明。",
        pitfalls=["索引常驻内存，不适合大规模语料", "开源核心与云端托管能力并不等同"],
        vendorId="orama-inc",
        pricing={"model": "freemium", "currency": "USD"},
        maturity="stable",
        tags=["search", "open-source", "javascript", "edge"],
    ),
    mk(
        "pagefind",
        "Pagefind",
        CAT_SEARCH,
        "static-search",
        "静态站构建期建索引 · 索引分片按需下载 · 零后端全文搜索",
        "https://pagefind.app",
        "Pagefind 在静态站点构建完成后扫描产物生成分片索引，浏览器只下载命中所需的片段即可完成全文检索，整个链路不需要任何检索服务端，由 CloudCannon 开源维护。",
        "文档站、博客等纯静态站要「零后端」站内搜索，且可接受索引随构建产出时首选。",
        "内容一改就得重新构建；不支持实时增量索引、复杂聚合与按用户个性化的排序策略。",
        pitfalls=["索引随构建产生，内容更新需重新构建", "不支持实时索引与个性化排序"],
        vendorId="cloudcannon-inc",
        maturity="stable",
        tags=["search", "open-source", "static-site", "frontend"],
    ),
    mk(
        "zincsearch",
        "ZincSearch",
        CAT_SEARCH,
        "log-search",
        "Go 单二进制检索 · 自带 Web 界面 · 小规模自托管低资源",
        "https://github.com/zincsearch/zincsearch",
        "ZincSearch 是 Go 实现的轻量搜索引擎，单二进制即可部署、自带 Web 管理界面，定位是小规模日志与文档检索场景里 Elasticsearch 的低资源替代品。",
        "个人项目或中小自托管环境要一份能搜的日志库，又不愿为 JVM 集群付出内存与运维成本时评估。",
        "功能覆盖与大规模稳定性都不及 Elasticsearch；社区维护节奏偏慢，上生产前务必按真实数据量压测上限。",
        pitfalls=["功能与大规模稳定性弱于 Elasticsearch", "社区维护节奏偏慢，需评估长期可用性"],
        vendorId="zinclabs-inc",
        maturity="beta",
        tags=["search", "open-source", "log", "self-hosted"],
    ),
    mk(
        "quickwit",
        "Quickwit",
        CAT_SEARCH,
        "log-search",
        "索引直落对象存储 · 存算分离压低留存成本 · 日志与追踪向",
        "https://quickwit.io",
        "Quickwit 是 Rust 实现的搜索引擎，把索引直接放在对象存储上、计算与存储彻底分离，专为日志与链路追踪这类只追加的海量数据设计，并提供部分 Elasticsearch 接入兼容。",
        "日志与 Trace 留存周期长、想把冷数据成本压到对象存储级别，且能接受查询延迟高于本地磁盘方案时评估。",
        "定位是可观测数据检索而非通用应用搜索；项目归属与商业支持路径几经变化，长期投入前请确认维护状态。",
        pitfalls=["对象存储读取带来更高查询延迟", "项目归属变动过，长期维护节奏需确认"],
        vendorId="quickwit-inc",
        maturity="beta",
        tags=["search", "open-source", "log", "observability"],
    ),
    mk(
        "aliyun-opensearch",
        "阿里云 OpenSearch",
        CAT_SEARCH,
        "hosted-search",
        "阿里云托管检索 · 行业增强与大模型检索版 · 国内同区合规",
        "https://www.aliyun.com/product/opensearch",
        "阿里云 OpenSearch 是托管型检索服务，除通用检索外提供面向电商、内容等场景的行业增强能力，并延伸出服务大模型问答的检索版本，分词、索引与排序均在控制台配置。",
        "国内业务需要合规同区的托管检索、已在阿里云栈内且不想自建 Elasticsearch 集群时评估。",
        "与开源 OpenSearch 项目同名但并非同一产品，勿混选；能力与计费以控制台为准，跨云迁移要重建索引与排序配置。",
        pitfalls=["与开源 OpenSearch 同名不同物，易选错", "索引与排序配置绑定阿里云，跨云迁移需重建"],
        vendorId="alibaba-cloud",
        region="domestic",
        pricing={"model": "usage", "currency": "CNY"},
        availability=DOMESTIC_CLOUD,
        maturity="stable",
        tags=["search", "domestic", "cloud", "hosted"],
    ),
]


OLAP_ENTRIES: list[dict] = [
    mk(
        "clickhouse",
        "ClickHouse",
        CAT_OLAP,
        "olap-engine",
        "列存 MPP 分析库 · 向量化执行与物化视图 · 自托管或官方云",
        "https://clickhouse.com",
        "ClickHouse 是面向分析查询的开源列式数据库，依靠向量化执行、稀疏主键索引与物化视图支撑大宽表聚合，可自托管集群，也有官方托管的 ClickHouse Cloud 形态。",
        "事件日志、行为埋点与实时报表需要秒级聚合、写多改少时优先；高频单行更新与事务仍交给 PostgreSQL 这类在线库。",
        "更新与删除代价高，去重和多表关联要顺着引擎特性设计表；分区键与排序键定错后重建数据的代价很大。",
        pitfalls=["更新删除代价高，不适合事务型写入", "分区键与排序键设计失误后重建成本大"],
        vendorId="clickhouse-inc",
        maturity="mature",
        tags=["olap", "database", "columnar", "open-source"],
    ),
    mk(
        "duckdb",
        "DuckDB",
        CAT_OLAP,
        "embedded-olap",
        "进程内分析 SQL · 单文件零依赖 · 直查 Parquet 与 DataFrame",
        "https://duckdb.org",
        "DuckDB 是嵌入进程内运行的分析型数据库，无需服务端、单文件即是一个库，可以直接对 Parquet、CSV 与内存中的 DataFrame 跑列式 SQL，常被称作「分析界的 SQLite」。",
        "本地数据探索、笔记本分析、数据管道中间层与单机中等规模离线计算首选；多用户并发写入与在线服务另择数仓。",
        "单进程模型不提供多客户端并发写与高可用；数据量超出本机内存与磁盘上限时必须换分布式方案。",
        pitfalls=["单进程模型不支持多客户端并发写", "受限于单机内存与磁盘容量"],
        vendorId="duckdb-labs",
        maturity="mature",
        tags=["olap", "database", "embedded", "open-source"],
    ),
    mk(
        "apache-doris",
        "Apache Doris",
        CAT_OLAP,
        "olap-engine",
        "MPP 实时数仓 · MySQL 协议直连 · 国产起源的 Apache 项目",
        "https://doris.apache.org",
        "Apache Doris 起源于百度 Palo，是 MPP 架构的开源实时分析数据库，对外兼容 MySQL 协议与语法，内置多种数据模型与物化视图，在国内有较厚的社区与商业支持。",
        "既要高并发点查又要实时聚合、希望沿用 MySQL 客户端与既有 BI 连接时评估。",
        "前后端节点角色与副本布局需要提前规划；版本迭代快，生产升级务必先在预发环境验证兼容性。",
        pitfalls=["节点角色与副本规划需前置设计", "版本迭代快，升级需回归验证"],
        region="both",
        maturity="mature",
        tags=["olap", "database", "mpp", "open-source"],
    ),
    mk(
        "starrocks",
        "StarRocks",
        CAT_OLAP,
        "olap-engine",
        "全面向量化 MPP · 免预聚合多表 JOIN · 可直读 Iceberg 湖表",
        "https://www.starrocks.io",
        "StarRocks 由 Apache Doris 分叉演进而来，主打全面向量化执行与代价优化器，强调多表关联现场算而不靠预聚合，同时可作为查询引擎直读 Iceberg、Hudi、Hive 等湖上表。",
        "已有数据湖、希望一套引擎兼顾湖上查询与实时数仓，报表里多表关联复杂时评估。",
        "与 Doris 语法相近但生态已分叉，工具链并不通用；大查询的资源隔离与治理需要持续运维投入。",
        pitfalls=["与 Doris 同源但已分叉，工具链不通用", "大查询资源隔离需运维治理"],
        region="both",
        maturity="stable",
        tags=["olap", "database", "lakehouse", "open-source"],
    ),
    mk(
        "databend",
        "Databend",
        CAT_OLAP,
        "cloud-warehouse",
        "Rust 云原生数仓 · 存算分离跑对象存储 · Snowflake 式用法",
        "https://www.databend.com",
        "Databend 是 Rust 实现的开源云原生数据仓库，存算分离、数据落在对象存储上、按需拉起计算，SQL 语义与使用方式明显向 Snowflake 靠拢，另有 Databend Cloud 托管形态。",
        "想要 Snowflake 式弹性、又希望开源自控并用对象存储压低长期留存成本时评估。",
        "周边工具链与生态成熟度不及老牌数仓；对象存储访问延迟直接决定小查询体验，交互式 BI 场景务必实测。",
        pitfalls=["生态与工具链成熟度弱于老牌数仓", "对象存储延迟影响交互式查询体验"],
        vendorId="databend-labs",
        region="both",
        maturity="stable",
        tags=["olap", "database", "cloud-native", "open-source"],
    ),
    mk(
        "motherduck",
        "MotherDuck",
        CAT_OLAP,
        "serverless-warehouse",
        "DuckDB 托管上云 · 本地与云端混合执行 · 小团队免运维",
        "https://motherduck.com",
        "MotherDuck 把 DuckDB 搬到云端，提供托管存储、共享与协作能力，并支持让同一条查询在本地 DuckDB 与云端之间混合执行，使单机分析平滑扩展成团队共享的数据环境。",
        "已经用 DuckDB 做本地分析，需要共享数据集、定时任务与团队协作，但不想搭一套大型数仓时选它。",
        "与 DuckDB 版本节奏耦合较紧；数据托管到境外后需确认合规边界，国内访问延迟明显。",
        pitfalls=["能力随 DuckDB 版本节奏变化", "数据托管境外，国内访问延迟与合规需评估"],
        vendorId="motherduck-inc",
        pricing={"model": "freemium", "currency": "USD"},
        maturity="stable",
        tags=["olap", "cloud", "duckdb", "serverless"],
    ),
    mk(
        "bigquery",
        "Google BigQuery",
        CAT_OLAP,
        "cloud-warehouse",
        "Serverless 数仓 · 按扫描量或槽位计价 · 与 GCP 生态深绑",
        "https://cloud.google.com/bigquery",
        "BigQuery 是 Google Cloud 的 Serverless 数据仓库，不需要管理节点，存储与计算分离，既可按查询扫描的数据量付费，也能购买槽位容量，并内建 BI 加速、地理分析与机器学习等扩展。",
        "团队已在 Google Cloud、数据量大且查询波峰明显、希望把运维降到零时优先。",
        "按扫描量计费的模式下，没做好分区与列裁剪的查询会直接烧钱；国内使用需走跨境方案，深度绑定后迁出成本高。",
        pitfalls=["未做分区裁剪的查询按扫描量计费易超支", "国内不可直连，需跨境方案与合规评估"],
        vendorId="google-cloud",
        pricing={"model": "usage", "currency": "USD"},
        availability=GLOBAL_BLOCKED,
        maturity="mature",
        tags=["olap", "cloud", "serverless", "warehouse"],
    ),
    mk(
        "snowflake",
        "Snowflake",
        CAT_OLAP,
        "cloud-warehouse",
        "多云托管数仓 · 虚拟仓库按运行时长计费 · 数据共享生态",
        "https://www.snowflake.com",
        "Snowflake 是可跑在 AWS、Azure 与 GCP 上的托管数据仓库，存储与计算彻底分离，计算以可独立伸缩的虚拟仓库形式按用量计费，并以跨账号数据共享、数据市场与应用生态见长。",
        "多云或跨组织共享数据、需要按团队隔离计算资源并要求稳定服务水平的中大型企业优先。",
        "计算按运行时长计费，自动挂起策略没配好很容易超支；专有 SQL 方言与生态绑定深，退出成本高。",
        pitfalls=["虚拟仓库闲置策略配置不当易超支", "专有方言与生态绑定深，迁出成本高"],
        vendorId="snowflake-inc",
        pricing={"model": "usage", "currency": "USD"},
        maturity="mature",
        tags=["olap", "cloud", "warehouse", "multi-cloud"],
    ),
    mk(
        "amazon-redshift",
        "Amazon Redshift",
        CAT_OLAP,
        "cloud-warehouse",
        "AWS 老牌 MPP 数仓 · 存算分离与 Serverless 形态 · 直查 S3",
        "https://aws.amazon.com/redshift/",
        "Amazon Redshift 是 AWS 的 MPP 数据仓库，早期以固定节点集群为主，如今提供存算分离节点与 Serverless 形态，可直接查询 S3 上的外部表，与 AWS 的数据与权限体系天然打通。",
        "数据与 ETL 已在 AWS、希望数仓和身份权限、对象存储、元数据目录同栈治理时评估。",
        "集群形态下扩缩容、分布键与清理维护仍需经验；跨云使用或迁出会牵动整套权限与数据管道。",
        pitfalls=["集群形态下分布键与维护作业仍需 DBA 经验", "与 AWS 权限和管道耦合，迁出牵连面广"],
        vendorId="amazon-web-services",
        pricing={"model": "usage", "currency": "USD"},
        maturity="mature",
        tags=["olap", "cloud", "warehouse", "aws"],
    ),
    mk(
        "aliyun-hologres",
        "阿里云 Hologres",
        CAT_OLAP,
        "realtime-warehouse",
        "阿里云实时数仓 · 兼容 PostgreSQL 生态 · 与离线数仓同栈",
        "https://www.aliyun.com",
        "Hologres 是阿里云的实时交互式分析服务，对外兼容 PostgreSQL 协议与生态，支持写入即可查与行列共存的存储形态，常与 MaxCompute、Flink 一起组成国内实时数仓链路。",
        "国内业务要合规同区的实时报表与在线分析、且已在阿里云数据栈内时评估。",
        "与云厂商数据栈耦合紧，跨云迁移要重做整条链路；实例规格与存储按量累积计费，需提前做容量与成本预估。",
        pitfalls=["与阿里云数据栈耦合紧，跨云迁移代价大", "实例与存储按量计费，需提前测算成本"],
        vendorId="alibaba-cloud",
        region="domestic",
        pricing={"model": "usage", "currency": "CNY"},
        availability=DOMESTIC_CLOUD,
        maturity="stable",
        tags=["olap", "domestic", "cloud", "realtime"],
    ),
]


TS_ENTRIES: list[dict] = [
    mk(
        "influxdb",
        "InfluxDB",
        CAT_TS,
        "timeseries-db",
        "老牌专用时序库 · 新代际转向列存与 SQL · 版本差异明显",
        "https://www.influxdata.com",
        "InfluxDB 是使用最广的专用时序数据库之一，早期以自有查询语言与时序存储引擎为主，新一代内核转向列式文件格式并重新拥抱 SQL，同时提供开源版与云托管版本。",
        "监控指标、设备采集与业务时序数据需要专用存储、保留策略与降采样管理时评估。",
        "不同大版本的查询语言与生态差异很大，选版本前先确认客户端与仪表盘是否兼容；开源版与云版能力并不等同。",
        pitfalls=["大版本间查询语言与生态不兼容", "开源版与云版能力有差距"],
        vendorId="influxdata-inc",
        pricing={"model": "freemium", "currency": "USD"},
        maturity="mature",
        tags=["timeseries", "database", "metrics", "iot"],
    ),
    mk(
        "questdb",
        "QuestDB",
        CAT_TS,
        "timeseries-db",
        "高频写入时序库 · SQL 加时间连接扩展 · 兼容行协议接入",
        "https://questdb.com",
        "QuestDB 是面向高频写入的开源时序数据库，用列式存储与时间分区支撑吞吐，查询侧提供标准 SQL 以及面向时间的连接与采样扩展，写入与访问兼容常见时序行协议和数据库有线协议。",
        "行情、传感器等写入密集又要即席分析的场景，且团队希望直接用 SQL 而非专用查询语言时评估。",
        "集群与高可用能力主要放在企业版；工具生态与社区规模小于 InfluxDB 和 Prometheus 体系。",
        pitfalls=["集群与高可用能力集中在企业版", "生态与社区规模小于主流时序方案"],
        vendorId="questdb-inc",
        pricing={"model": "freemium", "currency": "USD"},
        maturity="stable",
        tags=["timeseries", "database", "sql", "open-source"],
    ),
    mk(
        "victoriametrics",
        "VictoriaMetrics",
        CAT_TS,
        "metrics-store",
        "兼容 Prometheus 协议 · 压缩率与内存占用友好 · 单机集群双形态",
        "https://victoriametrics.com",
        "VictoriaMetrics 是兼容 Prometheus 写入与查询协议的开源时序数据库，以压缩率和资源占用见长，提供单机二进制与集群两种形态，常被用作 Prometheus 的远端长期存储与跨集群统一查询层。",
        "指标量级增长到 Prometheus 单机吃紧、需要长期留存或跨多集群统一查询时接上。",
        "查询语言存在方言扩展，跨实现迁移时告警规则要重新回归；集群版组件较多，容量规划需提前做。",
        pitfalls=["查询语言方言扩展会影响跨实现迁移", "集群版组件多，容量规划需前置"],
        vendorId="victoriametrics-inc",
        maturity="mature",
        tags=["timeseries", "metrics", "prometheus", "open-source"],
    ),
    mk(
        "tdengine",
        "TDengine",
        CAT_TS,
        "iot-timeseries",
        "国产物联网时序库 · 一个采集点一张表 · 内置流式与订阅",
        "https://www.taosdata.com",
        "TDengine 由涛思数据开发，面向物联网与工业设备场景，采用「一个采集点一张表」的建模方式压缩时间与标签维度，并内置缓存、流式计算与数据订阅，减少外挂组件的拼装。",
        "设备测点多、写入持续、需要按设备与标签维度聚合的国内工业、能源与车联网场景优先评估。",
        "建模范式与通用时序库差异大，迁移时写入侧要重写；开源版与企业版在集群、备份与多副本能力上有分界。",
        pitfalls=["建模范式特殊，迁入迁出需改写入侧", "集群与备份等能力集中在企业版"],
        vendorId="taosdata",
        region="both",
        pricing={"model": "freemium", "currency": "CNY"},
        maturity="mature",
        tags=["timeseries", "iot", "domestic", "database"],
    ),
    mk(
        "greptimedb",
        "GreptimeDB",
        CAT_TS,
        "timeseries-db",
        "Rust 云原生时序库 · 指标日志事件同栈 · 对象存储存算分离",
        "https://greptime.com",
        "GreptimeDB 是 Rust 实现的开源云原生时序数据库，走存算分离路线把数据放在对象存储上，试图用同一套 SQL 与指标查询接口容纳指标、日志和事件，另提供托管云服务。",
        "云原生环境要低成本长期留存时序数据，并希望少维护一套日志系统时评估。",
        "项目仍在快速演进，接口与部署形态可能变化；大规模生产案例少于老牌时序库，上线前需按自身负载压测。",
        pitfalls=["项目演进快，接口与部署形态可能变动", "大规模生产案例较少，需自行压测"],
        vendorId="greptime-inc",
        region="both",
        pricing={"model": "freemium", "currency": "CNY"},
        maturity="beta",
        tags=["timeseries", "cloud-native", "domestic", "open-source"],
    ),
    mk(
        "apache-iotdb",
        "Apache IoTDB",
        CAT_TS,
        "iot-timeseries",
        "工业时序 Apache 项目 · 树状测点建模 · 端边云同源文件格式",
        "https://iotdb.apache.org",
        "Apache IoTDB 源自清华大学的研究工作，面向工业物联网的时序数据管理，用树状层次组织设备与测点，配套列式时序文件格式，可在设备端、边缘与云端之间沿用同一套存储格式。",
        "工厂、电力、轨道交通等测点层级清晰、需要端边云一体采集与归档的场景评估。",
        "树状模型与标签式时序库思路不同，选定后调整层级代价高；周边报表与告警生态需要自行对接建设。",
        pitfalls=["树状测点模型调整代价高", "周边 BI 与告警生态需自建对接"],
        region="both",
        maturity="stable",
        tags=["timeseries", "iot", "apache", "open-source"],
    ),
]


ENTRIES_DATA: list[dict] = SEARCH_ENTRIES + OLAP_ENTRIES + TS_ENTRIES


VENDORS_DATA: list[dict] = [
    vendor("algolia-inc", "Algolia", url="https://www.algolia.com"),
    vendor("manticore-software", "Manticore Software", url="https://manticoresearch.com"),
    vendor("orama-inc", "Orama", url="https://orama.com"),
    vendor("cloudcannon-inc", "CloudCannon", url="https://cloudcannon.com"),
    vendor("zinclabs-inc", "Zinc Labs", url="https://github.com/zincsearch"),
    vendor("quickwit-inc", "Quickwit", url="https://quickwit.io"),
    vendor("clickhouse-inc", "ClickHouse, Inc.", url="https://clickhouse.com"),
    vendor("duckdb-labs", "DuckDB Labs", url="https://duckdblabs.com"),
    vendor("motherduck-inc", "MotherDuck", url="https://motherduck.com"),
    vendor("databend-labs", "Databend Labs", region="domestic", url="https://www.databend.com"),
    vendor("snowflake-inc", "Snowflake", url="https://www.snowflake.com"),
    vendor("influxdata-inc", "InfluxData", url="https://www.influxdata.com"),
    vendor("questdb-inc", "QuestDB", url="https://questdb.com"),
    vendor("victoriametrics-inc", "VictoriaMetrics", url="https://victoriametrics.com"),
    vendor("taosdata", "涛思数据", region="domestic", url="https://www.taosdata.com"),
    vendor("greptime-inc", "Greptime", region="domestic", url="https://greptime.com"),
]


EDGES_DATA: list[dict] = [
    # ——— 检索叶：与已有 elasticsearch / meilisearch / typesense 互挂 ———
    edge(
        "e-opensearch-osalt-elasticsearch",
        "opensearch",
        "elasticsearch",
        "open_source_alternative_to",
        weight=0.9,
        confidence="verified",
        note="2021 年自 7.10 分叉，Apache-2.0 规避商业授权；新版特性与客户端已分道",
    ),
    edge(
        "e-opensearch-osalt-algolia",
        "opensearch",
        "algolia",
        "open_source_alternative_to",
        weight=0.6,
        note="自托管开源检索集群 vs 托管搜索 SaaS：省订阅费但换来集群运维",
    ),
    edge(
        "e-typesense-osalt-algolia",
        "typesense",
        "algolia",
        "open_source_alternative_to",
        weight=0.8,
        note="开源可自托管、API 极简 vs 托管 SaaS 的规则与组件生态",
    ),
    edge(
        "e-meilisearch-osalt-algolia",
        "meilisearch",
        "algolia",
        "open_source_alternative_to",
        weight=0.8,
        note="开源即时搜索、DX 接近 vs 托管 SaaS 的排序规则与分析后台",
    ),
    edge(
        "e-pagefind-osalt-algolia",
        "pagefind",
        "algolia",
        "open_source_alternative_to",
        weight=0.55,
        note="构建期静态索引、零后端 vs 托管检索 SaaS；只覆盖小体量站内搜索",
    ),
    edge(
        "e-apache-solr-alt-elasticsearch",
        "apache-solr",
        "elasticsearch",
        "alternative_to",
        weight=0.75,
        note="同为 Lucene 之上：Solr 显式结构与分面可控、依赖 ZooKeeper；ES 生态与托管更全",
    ),
    edge(
        "e-manticore-search-alt-elasticsearch",
        "manticore-search",
        "elasticsearch",
        "alternative_to",
        weight=0.6,
        note="C++ 轻量内核、MySQL 协议 SQL 查询 vs JVM 集群与完整分析生态",
    ),
    edge(
        "e-manticore-search-alt-meilisearch",
        "manticore-search",
        "meilisearch",
        "alternative_to",
        weight=0.5,
        note="自托管轻量检索两条路：SQL 心智接入 vs typo 容错的 REST 应用搜索",
    ),
    edge(
        "e-quickwit-alt-elasticsearch",
        "quickwit",
        "elasticsearch",
        "alternative_to",
        weight=0.6,
        note="索引落对象存储、按留存成本优化 vs 本地磁盘倒排、低延迟通用检索",
    ),
    edge(
        "e-quickwit-alt-loki",
        "quickwit",
        "loki",
        "alternative_to",
        weight=0.55,
        note="日志留存两种索引策略：全文倒排可搜正文 vs 仅索引标签、正文靠扫描",
    ),
    edge(
        "e-zincsearch-alt-elasticsearch",
        "zincsearch",
        "elasticsearch",
        "alternative_to",
        weight=0.5,
        note="单二进制低资源、适合小规模自托管 vs 大规模集群与完整插件体系",
    ),
    edge(
        "e-orama-alt-meilisearch",
        "orama",
        "meilisearch",
        "alternative_to",
        weight=0.55,
        note="索引内嵌进浏览器与边缘运行时 vs 独立检索服务；量级与部署形态不同",
    ),
    edge(
        "e-orama-alt-pagefind",
        "orama",
        "pagefind",
        "alternative_to",
        weight=0.6,
        note="前端侧检索两条路：运行时内嵌可动态建索引 vs 构建期生成静态分片",
    ),
    edge(
        "e-aliyun-opensearch-domeq-algolia",
        "aliyun-opensearch",
        "algolia",
        "domestic_equivalent_of",
        weight=0.7,
        note="国内合规同区的托管检索服务，对应海外托管搜索 SaaS 的位置",
    ),
    edge(
        "e-aliyun-opensearch-alt-opensearch",
        "aliyun-opensearch",
        "opensearch",
        "alternative_to",
        weight=0.4,
        note="同名不同物：阿里云托管检索产品 vs 基金会治理的开源 OpenSearch 项目",
    ),
    # ——— 分析叶 ———
    edge(
        "e-clickhouse-cuw-postgresql",
        "clickhouse",
        "postgresql",
        "commonly_used_with",
        weight=0.7,
        note="常见分工：PostgreSQL 承接事务写入，变更同步到 ClickHouse 做聚合分析",
    ),
    edge(
        "e-clickhouse-cuw-kafka",
        "clickhouse",
        "kafka",
        "commonly_used_with",
        weight=0.7,
        note="Kafka 做实时摄入缓冲，ClickHouse 落列存并对外提供秒级聚合",
    ),
    edge(
        "e-clickhouse-cuw-grafana",
        "clickhouse",
        "grafana",
        "commonly_used_with",
        weight=0.65,
        note="ClickHouse 作为 Grafana 数据源出大盘，适合埋点与业务指标而非纯 Prom 指标",
    ),
    edge(
        "e-clickhouse-alt-elasticsearch",
        "clickhouse",
        "elasticsearch",
        "alternative_to",
        weight=0.6,
        note="日志分析的两条路线：列存聚合与成本占优 vs 倒排全文检索与即席查错占优",
    ),
    edge(
        "e-duckdb-alt-clickhouse",
        "duckdb",
        "clickhouse",
        "alternative_to",
        weight=0.6,
        note="同为列存分析：DuckDB 进程内单机、随代码走；ClickHouse 是常驻服务与集群",
    ),
    edge(
        "e-motherduck-builton-duckdb",
        "motherduck",
        "duckdb",
        "built_on",
        weight=0.95,
        confidence="verified",
        note="把 DuckDB 引擎托管上云，并支持本地与云端混合执行同一条查询",
    ),
    edge(
        "e-apache-doris-domeq-clickhouse",
        "apache-doris",
        "clickhouse",
        "domestic_equivalent_of",
        weight=0.7,
        note="国产起源的 MPP 实时数仓：MySQL 协议直连、高并发点查更顺手",
    ),
    edge(
        "e-starrocks-domeq-clickhouse",
        "starrocks",
        "clickhouse",
        "domestic_equivalent_of",
        weight=0.65,
        note="国产起源的向量化 MPP：多表 JOIN 现场算，不必靠宽表预聚合",
    ),
    edge(
        "e-starrocks-alt-apache-doris",
        "starrocks",
        "apache-doris",
        "alternative_to",
        weight=0.8,
        note="同源分叉：StarRocks 侧重向量化与湖上直查，Doris 留在 Apache 社区演进",
    ),
    edge(
        "e-databend-domeq-snowflake",
        "databend",
        "snowflake",
        "domestic_equivalent_of",
        weight=0.65,
        note="国内团队主导的开源实现，对齐 Snowflake 的存算分离与弹性计算语义",
    ),
    edge(
        "e-bigquery-alt-snowflake",
        "bigquery",
        "snowflake",
        "alternative_to",
        weight=0.8,
        note="Serverless 按扫描量、深绑 GCP vs 多云虚拟仓库按时长计费、数据共享生态",
    ),
    edge(
        "e-amazon-redshift-alt-snowflake",
        "amazon-redshift",
        "snowflake",
        "alternative_to",
        weight=0.75,
        note="AWS 同栈治理与既有权限复用 vs 跨云中立、计算资源按团队隔离",
    ),
    edge(
        "e-aliyun-hologres-domeq-bigquery",
        "aliyun-hologres",
        "bigquery",
        "domestic_equivalent_of",
        weight=0.6,
        note="国内云上实时数仓位，对应海外云原生数仓；侧重写入即查与同区合规",
    ),
    edge(
        "e-aliyun-hologres-cuw-postgresql",
        "aliyun-hologres",
        "postgresql",
        "commonly_used_with",
        weight=0.5,
        note="兼容 PostgreSQL 协议，可复用 PG 客户端与 BI 连接；内核与用途仍是分析型",
    ),
    # ——— 时序叶：与已有 timescaledb / prometheus / grafana 互挂 ———
    edge(
        "e-victoriametrics-cuw-prometheus",
        "victoriametrics",
        "prometheus",
        "commonly_used_with",
        weight=0.85,
        note="常作 Prometheus 的远端长期存储与跨集群统一查询层，采集仍由 Prom 完成",
    ),
    edge(
        "e-victoriametrics-cuw-grafana",
        "victoriametrics",
        "grafana",
        "commonly_used_with",
        weight=0.7,
        note="以 Prometheus 兼容数据源接入 Grafana 出图，面板可基本沿用",
    ),
    edge(
        "e-influxdb-alt-timescaledb",
        "influxdb",
        "timescaledb",
        "alternative_to",
        weight=0.75,
        note="专用时序内核与保留策略 vs 留在 PostgreSQL 生态里用扩展做时序",
    ),
    edge(
        "e-questdb-alt-influxdb",
        "questdb",
        "influxdb",
        "alternative_to",
        weight=0.7,
        note="SQL 优先、写入吞吐取向，并兼容常见时序行协议接入，便于从 Influx 侧切换",
    ),
    edge(
        "e-tdengine-domeq-influxdb",
        "tdengine",
        "influxdb",
        "domestic_equivalent_of",
        weight=0.75,
        note="国内工业时序主力：一个采集点一张表的建模，内置流式与订阅",
    ),
    edge(
        "e-greptimedb-domeq-influxdb",
        "greptimedb",
        "influxdb",
        "domestic_equivalent_of",
        weight=0.6,
        note="国内团队的云原生实现：数据落对象存储，指标与日志共用一套接口",
    ),
    edge(
        "e-greptimedb-cuw-prometheus",
        "greptimedb",
        "prometheus",
        "commonly_used_with",
        weight=0.6,
        note="可承接 Prometheus 指标写入并用兼容查询接口读回，作长期存储层",
    ),
    edge(
        "e-tdengine-cuw-grafana",
        "tdengine",
        "grafana",
        "commonly_used_with",
        weight=0.65,
        note="通过数据源插件在 Grafana 出设备与产线大盘，是国内工业监控常见搭配",
    ),
    edge(
        "e-apache-iotdb-alt-tdengine",
        "apache-iotdb",
        "tdengine",
        "alternative_to",
        weight=0.7,
        note="国产工业时序两种建模：树状层次组织测点 vs 一个采集点一张表加标签",
    ),
]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--overwrite", action="store_true")
    args = ap.parse_args()

    ENTRIES.mkdir(parents=True, exist_ok=True)
    VENDORS.mkdir(parents=True, exist_ok=True)
    EDGES.mkdir(parents=True, exist_ok=True)

    ids = [e["id"] for e in ENTRIES_DATA]
    assert len(ids) == len(set(ids)), "duplicate entry id"
    gids = [g["id"] for g in EDGES_DATA]
    assert len(gids) == len(set(gids)), "duplicate edge id"

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
        print("entry", e["category"], e["id"])

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

    per_leaf = {}
    for e in ENTRIES_DATA:
        per_leaf[e["category"]] = per_leaf.get(e["category"], 0) + 1
    print(f"planned per leaf: {per_leaf}")
    print(
        f"done entries={wrote_e} (skipped {skipped_e}) "
        f"vendors={wrote_v} edges={wrote_g} (skipped {skipped_g})"
    )


if __name__ == "__main__":
    main()
