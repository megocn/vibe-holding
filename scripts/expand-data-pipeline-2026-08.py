#!/usr/bin/env python3
"""图数据库（db-graph）与数据管道 / ETL（db-pipeline）扩种。

- 图数据库：Neo4j / NebulaGraph / Dgraph / ArangoDB / Memgraph / JanusGraph / Kùzu
- 数据管道：Airbyte / Fivetran / dbt / Airflow / Dagster / Prefect / Flink / SeaTunnel / DataX / Debezium

用法:
  python3 scripts/expand-data-pipeline-2026-08.py
  python3 scripts/expand-data-pipeline-2026-08.py --overwrite
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
CAT_GRAPH = "db-graph"
CAT_PIPE = "db-pipeline"


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
        "tags": ["database", "data"],
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
    dm = e.get("descriptionMd", "")
    assert 160 <= len(dm) <= 360, (e["id"], len(dm))
    assert 1 <= len(e["pitfalls"]) <= 3, (e["id"], len(e["pitfalls"]))
    assert 3 <= len(e["tags"]) <= 5, (e["id"], e["tags"])
    assert e.get("subcategory"), e["id"]
    assert e["category"] in (CAT_GRAPH, CAT_PIPE), e["id"]
    return e


def desc(what: str, when: str, caution: str) -> str:
    return f"{what}\n\n{when}\n\n{caution}\n"


def mk(cat, eid, name, sub, one, url, what, when, caution, **extra):
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


GLOBAL = {
    "chinaAccessible": True,
    "needsCompany": False,
    "needsIcp": False,
    "regions": ["global"],
}

SAAS_OVERSEAS = {
    "chinaAccessible": True,
    "needsCompany": True,
    "needsIcp": False,
    "regions": ["global"],
}

DOMESTIC = {
    "chinaAccessible": True,
    "needsCompany": False,
    "needsIcp": False,
    "regions": ["CN"],
}


GRAPH_ENTRIES: list[dict] = [
    mk(
        CAT_GRAPH,
        "neo4j",
        "Neo4j",
        "native-graph",
        "原生属性图 · Cypher 与图算法工具链最全 · 社区版单机、集群走商业授权",
        "https://neo4j.com",
        "Neo4j 是原生属性图数据库，以节点与关系为一等模型，用 Cypher 表达多跳遍历、路径与模式匹配，"
        "配套可视化、图算法库与大量学习资料，是图库里生态最完整的一支。",
        "关系推理、反欺诈、权限链路、知识图谱与 GraphRAG 这类「多跳查询比 JOIN 更自然」的场景优先；"
        "只是偶尔查两层关联，关系库配递归查询往往更省事。",
        "社区版为单机且采用 GPL，集群与企业特性在商业版；托管的 Aura 会带来地区与出网约束，国内落地需先确认合规路径。",
        vendorId="neo4j-inc",
        pricing={"model": "freemium", "currency": "USD"},
        maturity="mature",
        tags=["database", "graph", "cypher", "oss"],
        pitfalls=[
            "社区版单机，集群与企业特性需商业授权",
            "Cypher 与配套工具链绑定深，迁出成本高",
            "超大规模写入吞吐需要专门调优",
        ],
    ),
    mk(
        CAT_GRAPH,
        "nebulagraph",
        "NebulaGraph",
        "distributed-graph",
        "国产开源分布式图库 · 存算分离可独立扩缩 · nGQL 部分兼容 openCypher",
        "https://www.nebula-graph.io",
        "NebulaGraph 是开源分布式图数据库，查询层、存储层与元数据层分离部署、可各自扩缩，"
        "面向超大规模点边与高并发多跳查询，查询语言为 nGQL 并部分兼容 openCypher 语法。",
        "点边规模到十亿量级、需要横向扩容并希望有国内商业支持时，作为 Neo4j 的分布式对照评估；"
        "小图单机场景用 Neo4j 或嵌入式方案更轻。",
        "多组件部署与运维复杂度明显高于单机图库；nGQL 与 Cypher 并不等价，迁移时语句需逐条改写。",
        vendorId="vesoft",
        pricing={"model": "open-source", "currency": "CNY"},
        region="domestic",
        availability=GLOBAL,
        maturity="stable",
        tags=["database", "graph", "distributed", "domestic", "oss"],
        pitfalls=[
            "三类组件分开部署，运维成本高于单机图库",
            "nGQL 与 Cypher 不等价，迁移需逐条改写",
        ],
        sources=["https://www.nebula-graph.io", "https://github.com/vesoft-inc/nebula"],
    ),
    mk(
        CAT_GRAPH,
        "dgraph",
        "Dgraph",
        "distributed-graph",
        "分布式原生图 · GraphQL 优先接口 · 自有 DQL 查询 · 数据按谓词分片",
        "https://dgraph.io",
        "Dgraph 是分布式原生图数据库，对外主打 GraphQL 风格接口，内部用自有的 DQL 查询语言，"
        "数据按谓词分片并支持分布式事务，可以把图库直接当作 API 后端使用。",
        "团队已经在用 GraphQL、希望后端接口与图存储共用一套模型时评估；"
        "重图算法与成熟可视化工具链仍是 Neo4j 更强。",
        "查询语言与主流 Cypher 生态不互通，选型即锁定；项目治理与商业实体几经变动，长期维护节奏需自行跟踪。",
        vendorId="dgraph-labs",
        pricing={"model": "open-source"},
        maturity="stable",
        tags=["database", "graph", "graphql", "oss"],
        pitfalls=[
            "DQL 与 Cypher 生态不互通，选型即锁定",
            "项目治理与商业实体变动过，需跟踪社区活跃度",
        ],
        sources=["https://dgraph.io", "https://github.com/hypermodeinc/dgraph"],
    ),
    mk(
        CAT_GRAPH,
        "arangodb",
        "ArangoDB",
        "multi-model",
        "多模型库 · 文档/图/键值共用一套 AQL · 图只是其中一种能力",
        "https://arangodb.com",
        "ArangoDB 是多模型数据库，文档、图与键值共用同一套存储与 AQL 查询语言，"
        "可以在一条语句里既过滤文档字段又做图遍历，省去在文档库与图库之间同步数据。",
        "数据既有文档形态又需要关系遍历、且不愿维护两套库时评估；"
        "纯粹的深度图分析与图算法生态仍以专用图库更强。",
        "多模型意味着每一面都不是最优解；许可与发行策略调整过，商业条款需按当前版本核对。",
        vendorId="arangodb-inc",
        pricing={"model": "freemium", "currency": "USD"},
        maturity="stable",
        tags=["database", "graph", "multi-model", "oss"],
        pitfalls=[
            "多模型换来的是各面都非最优",
            "许可与发行策略调整过，条款需按当前版本核对",
        ],
    ),
    mk(
        CAT_GRAPH,
        "memgraph",
        "Memgraph",
        "native-graph",
        "内存优先图库 · 兼容 Cypher · 流式摄入与图上实时触发",
        "https://memgraph.com",
        "Memgraph 是内存优先的图数据库，兼容 Cypher 查询，内置从消息流持续摄入并在图上触发计算的能力，"
        "配套图算法库与可视化界面，主打低延迟的实时图查询。",
        "需要在毫秒级延迟下对不断变化的图做查询与算法（风控、网络拓扑、实时推荐）时，"
        "作为 Neo4j 的低延迟对照评估。",
        "内存驻留意味着容量受机器内存限制，成本随图规模线性上升；持久化与恢复策略需在压测阶段就验证。",
        vendorId="memgraph-inc",
        pricing={"model": "freemium", "currency": "USD"},
        maturity="stable",
        tags=["database", "graph", "streaming", "cypher"],
        pitfalls=[
            "内存驻留，容量与成本随图规模线性上升",
            "持久化与恢复策略需在压测阶段验证",
        ],
    ),
    mk(
        CAT_GRAPH,
        "janusgraph",
        "JanusGraph",
        "graph-on-storage",
        "存算分离图引擎 · Gremlin/TinkerPop · 存储与索引都靠外部组件",
        "https://janusgraph.org",
        "JanusGraph 是开源分布式图引擎，自身不带存储：数据落在宽列存储上，索引交给搜索引擎，"
        "查询走 TinkerPop 生态的 Gremlin 语言，本质是给已有大数据底座加一层图遍历能力。",
        "已有大数据存储集群、希望复用现有底座做图查询，或团队必须走 Gremlin 生态时评估；"
        "没有底座就直接选自带存储的图库。",
        "运维等于同时维护图引擎与后端存储两套系统；社区发版节奏较慢，疑难问题常需自己读源码定位。",
        vendorId="linux-foundation",
        pricing={"model": "open-source"},
        maturity="stable",
        tags=["database", "graph", "gremlin", "oss"],
        pitfalls=[
            "需同时运维图引擎与后端存储、索引组件",
            "社区发版节奏偏慢，疑难问题定位成本高",
        ],
        sources=["https://janusgraph.org", "https://github.com/JanusGraph/janusgraph"],
    ),
    mk(
        CAT_GRAPH,
        "kuzu",
        "Kùzu",
        "embedded-graph",
        "嵌入式图库 · 进程内跑、数据落本地文件 · Cypher + 列存向量化执行",
        "https://kuzudb.com",
        "Kùzu 是嵌入式图数据库，以库的形式跑在应用进程内、数据落成本地文件，支持 Cypher 并采用列式向量化执行，"
        "常被类比为「图领域的 DuckDB」，长于分析型的批量遍历。",
        "做本地图分析、笔记本实验、单机 GraphRAG，或想把图能力嵌进应用而不额外部署服务时评估；"
        "多写并发的在线业务仍需服务端图库。",
        "嵌入式定位不提供集群与多写并发；项目迭代快，版本间存储格式与接口可能变动。",
        vendorId=None,
        pricing={"model": "open-source"},
        maturity="beta",
        tags=["database", "graph", "embedded", "oss"],
        pitfalls=[
            "嵌入式定位，不提供集群与多写并发",
            "版本间存储格式与接口可能变动",
            "维护主体与发布节奏有过调整，长期依赖前先看仓库活跃度",
        ],
        sources=["https://kuzudb.com", "https://github.com/kuzudb/kuzu"],
    ),
]


PIPE_ENTRIES: list[dict] = [
    mk(
        CAT_PIPE,
        "airbyte",
        "Airbyte",
        "elt-connector",
        "开源 ELT · 连接器目录最广 · 自托管或云托管 · CDK 可自建连接器",
        "https://airbyte.com",
        "Airbyte 是开源 ELT 平台，提供数百个来源与目的地连接器，支持全量与增量同步，"
        "既可自托管在自己的集群里，也可用官方云版本；连接器开发套件让自建长尾数据源的门槛不高。",
        "要把 SaaS 与业务库的数据搬进数仓，又想避开按行计费或要求数据不出内网时，"
        "作为 Fivetran 的开源对照评估；转换环节交给 dbt。",
        "长尾连接器成熟度参差，生产前需逐个压测；自托管的调度与资源治理成本会随任务数明显上升。",
        vendorId="airbyte-inc",
        pricing={"model": "open-source", "currency": "USD"},
        maturity="stable",
        tags=["data", "elt", "etl", "oss"],
        pitfalls=[
            "长尾连接器成熟度参差，上线前需逐个压测",
            "自托管调度与资源治理成本随任务数上升",
        ],
        sources=["https://airbyte.com", "https://github.com/airbytehq/airbyte"],
    ),
    mk(
        CAT_PIPE,
        "fivetran",
        "Fivetran",
        "elt-connector",
        "全托管 ELT · 连接器由厂商维护随上游变更 · 按月活跃行计费",
        "https://www.fivetran.com",
        "Fivetran 是全托管的数据同步服务，连接器由厂商维护并跟随上游 API 变更自动适配，"
        "数据落仓后再由 dbt 做转换，是把抽取与加载整体外包出去的典型代表。",
        "团队没有专职数据工程、希望连接器坏了有人兜底，且数据可以出网到托管服务时优先；"
        "内网合规要求高就看开源自托管方案。",
        "按月活跃行计费，宽表与高频变更容易让账单失控；连接器行为不可改，定制需求只能等厂商排期。",
        vendorId="fivetran-inc",
        pricing={"model": "usage", "currency": "USD"},
        availability=SAAS_OVERSEAS,
        maturity="mature",
        tags=["data", "elt", "saas", "managed"],
        pitfalls=[
            "按月活跃行计费，高频变更易致账单失控",
            "连接器行为不可改，定制需求依赖厂商排期",
            "数据需出网到托管服务，国内合规需评估",
        ],
    ),
    mk(
        CAT_PIPE,
        "dbt",
        "dbt",
        "transform",
        "仓内 SQL 转换 · 模型血缘/测试/文档一体 · Core 开源 + Cloud 托管",
        "https://www.getdbt.com",
        "dbt 把数仓里的 SQL 转换工程化：模型之间通过引用自动推导依赖与血缘，"
        "附带数据测试、快照与文档生成，命令行版本开源，调度、协作与权限在云版本。",
        "数据已经落进仓库、需要把散落的 SQL 变成可复用可测试的模型层时几乎是默认选择；"
        "抽取加载由 Airbyte / Fivetran 负责，两者分工明确。",
        "只做转换不做抽取，编排仍需 Airflow 或 Dagster；模型层膨胀后编译与全量重跑会成为新瓶颈。",
        vendorId="dbt-labs",
        pricing={"model": "freemium", "currency": "USD"},
        maturity="mature",
        tags=["data", "transform", "sql", "oss"],
        pitfalls=[
            "只做转换，抽取与编排需另配组件",
            "模型层膨胀后编译与全量重跑耗时明显",
        ],
        sources=["https://www.getdbt.com", "https://github.com/dbt-labs/dbt-core"],
    ),
    mk(
        CAT_PIPE,
        "apache-airflow",
        "Apache Airflow",
        "orchestration",
        "Python 定义 DAG 的调度中枢 · 算子生态最广 · 以任务而非数据资产为中心",
        "https://airflow.apache.org",
        "Apache Airflow 用 Python 代码定义有向无环图来编排批处理任务，调度、重试、回填与依赖管理成熟，"
        "算子与 Provider 生态覆盖主流云与数据组件，是数据平台事实上的调度底座。",
        "已有多条批处理链路需要统一调度、依赖关系复杂且团队熟悉 Python 时选它；"
        "应用侧的事件触发与后台任务不必用这么重的底座。",
        "自托管需维护调度器、执行器与元数据库，运维成本不低；以任务为中心，数据血缘与质量要靠外部补齐。",
        vendorId="apache-software-foundation",
        pricing={"model": "open-source"},
        maturity="mature",
        tags=["data", "orchestration", "python", "oss"],
        pitfalls=[
            "自托管需维护调度器、执行器与元数据库",
            "以任务为中心，数据血缘与质量需外部补齐",
        ],
        sources=["https://airflow.apache.org", "https://github.com/apache/airflow"],
    ),
    mk(
        CAT_PIPE,
        "dagster",
        "Dagster",
        "orchestration",
        "以数据资产为中心的编排 · 内建血缘与新鲜度 · 本地可测试",
        "https://dagster.io",
        "Dagster 把编排的核心从「任务」换成「数据资产」：声明每张表由什么产出、依赖谁，"
        "平台据此推导血缘、按需物化并展示新鲜度，配套类型系统与较好的本地测试体验。",
        "关心数据资产血缘与新鲜度、希望编排层本身就能回答「这张表怎么来的」时，"
        "作为 Airflow 的现代对照评估，与 dbt 组合尤其顺手。",
        "资产模型需要重构既有 DAG 思路，迁移不是逐条搬运；集成组件的广度仍不及 Airflow。",
        vendorId="dagster-labs",
        pricing={"model": "freemium", "currency": "USD"},
        maturity="stable",
        tags=["data", "orchestration", "python", "oss"],
        pitfalls=[
            "资产模型与既有 DAG 思路不同，迁移非逐条搬运",
            "集成组件广度不及 Airflow",
        ],
        sources=["https://dagster.io", "https://github.com/dagster-io/dagster"],
    ),
    mk(
        CAT_PIPE,
        "prefect",
        "Prefect",
        "orchestration",
        "Python 原生流编排 · 运行时动态生成 DAG · 装饰器改造现有脚本",
        "https://www.prefect.io",
        "Prefect 用装饰器把普通 Python 函数变成可观测的任务与流，依赖图在运行时动态生成而非静态声明，"
        "可自托管服务端，也可用云版本做控制面而计算仍留在自己的算力上。",
        "流程分支高度动态、或团队想以最小改造把现有 Python 脚本纳入调度与重试体系时评估。",
        "版本之间接口变化较大，旧教程容易失效；数据资产血缘与数仓集成不如 Dagster、dbt 那条线成熟。",
        vendorId="prefect-tech",
        pricing={"model": "freemium", "currency": "USD"},
        maturity="stable",
        tags=["data", "orchestration", "python", "oss"],
        pitfalls=[
            "跨大版本接口变化较大，旧教程易失效",
            "数据资产血缘与数仓集成成熟度一般",
        ],
        sources=["https://www.prefect.io", "https://github.com/PrefectHQ/prefect"],
    ),
    mk(
        CAT_PIPE,
        "apache-flink",
        "Apache Flink",
        "stream-processing",
        "有状态流处理引擎 · 事件时间与检查点 · 流批一体 · Flink SQL/CDC 生态",
        "https://flink.apache.org",
        "Apache Flink 是有状态的分布式流处理引擎，以事件时间、窗口与检查点支撑容错语义，"
        "同一套运行时既跑流也跑批，Flink SQL 与其 CDC 生态把实时同步和实时数仓的门槛拉低了不少。",
        "需要秒级延迟的实时聚合、实时风控或实时数仓，且状态较大需要容错时选它；"
        "只是定时搬数就别引入常驻集群。",
        "集群与状态后端运维、反压与检查点调优都需要专门经验；作业升级时的状态兼容是长期维护主要痛点。",
        vendorId="apache-software-foundation",
        pricing={"model": "open-source"},
        maturity="mature",
        tags=["data", "streaming", "realtime", "oss"],
        pitfalls=[
            "集群与状态后端运维、调优需要专门经验",
            "作业升级的状态兼容是长期维护痛点",
        ],
        sources=["https://flink.apache.org", "https://github.com/apache/flink"],
    ),
    mk(
        CAT_PIPE,
        "apache-seatunnel",
        "Apache SeaTunnel",
        "elt-connector",
        "国内孵化的 Apache 顶级数据集成项目 · 自带 Zeta 引擎，也可跑 Flink/Spark",
        "https://seatunnel.apache.org",
        "Apache SeaTunnel 是国内孵化并进入 Apache 顶级项目的数据集成平台，连接器覆盖主流数据库、消息与湖仓，"
        "既能用自带引擎独立运行，也能提交到 Flink 或 Spark 集群，支持整库同步与变更捕获。",
        "国内团队要做大批量的批流一体同步、又不想额外引入完整大数据栈时评估；"
        "小规模 SaaS 数据接入用 Airbyte 的连接器目录更省事。",
        "SaaS 类连接器广度不及 Airbyte；三种执行引擎带来配置分叉，压测结论不能跨引擎照搬。",
        vendorId="apache-software-foundation",
        pricing={"model": "open-source", "currency": "CNY"},
        region="both",
        maturity="stable",
        tags=["data", "elt", "sync", "domestic", "oss"],
        pitfalls=[
            "SaaS 类连接器广度不及 Airbyte",
            "多执行引擎导致配置分叉，压测结论不可跨引擎照搬",
        ],
        sources=["https://seatunnel.apache.org", "https://github.com/apache/seatunnel"],
    ),
    mk(
        CAT_PIPE,
        "datax",
        "DataX",
        "elt-connector",
        "阿里开源离线同步 · 单进程多线程 · Reader/Writer 插件式 · 不含调度",
        "https://github.com/alibaba/DataX",
        "DataX 是阿里开源的离线数据同步工具，以单进程多线程把源端读插件与目标端写插件拼起来，"
        "一份配置即一个作业，部署极轻、跑批稳定，在国内传统数仓迁移场景里沉淀很深。",
        "要在内网做库到库的定时全量或分片增量同步、且已有现成调度系统时用它；"
        "实时变更捕获与 SaaS 数据接入不在其覆盖范围。",
        "单机架构无法横向扩展，超大表需自己切分并发；仓库更新节奏放缓，新数据源插件多来自社区分支。",
        vendorId="alibaba",
        pricing={"model": "open-source", "currency": "CNY"},
        region="domestic",
        availability=DOMESTIC,
        maturity="stable",
        tags=["data", "etl", "sync", "domestic", "oss"],
        pitfalls=[
            "单机架构不能横向扩展，超大表需手工切分",
            "上游更新节奏放缓，新插件多靠社区分支",
            "不含调度与实时 CDC，需另配组件",
        ],
    ),
    mk(
        CAT_PIPE,
        "debezium",
        "Debezium",
        "cdc",
        "开源 CDC · 读事务日志捕获行级变更 · 以连接器形态部署，也可嵌入应用",
        "https://debezium.io",
        "Debezium 通过读取数据库事务日志把行级变更转成事件流，常见形态是作为消息平台的连接器运行，"
        "也提供可嵌入应用的引擎与独立服务，是事件驱动架构里最常用的变更捕获组件。",
        "要做近实时同步、缓存失效、审计或事件驱动集成，且不能接受轮询扫表的延迟与压力时选它；"
        "下游通常接流处理引擎或数仓。",
        "对源库的日志保留、账号权限与复制槽有硬要求，配置不当会撑爆磁盘；模式变更处理与初始快照必须上线前演练。",
        vendorId="red-hat",
        pricing={"model": "open-source"},
        maturity="stable",
        tags=["data", "cdc", "streaming", "oss"],
        pitfalls=[
            "对源库日志保留与复制槽有硬要求，配置不当会撑爆磁盘",
            "模式变更与初始快照需上线前演练",
        ],
        sources=["https://debezium.io", "https://github.com/debezium/debezium"],
    ),
]

ENTRIES_DATA: list[dict] = GRAPH_ENTRIES + PIPE_ENTRIES

VENDORS_DATA: list[dict] = [
    vendor("neo4j-inc", "Neo4j, Inc.", url="https://neo4j.com"),
    vendor("vesoft", "悦数科技（VEsoft）", region="domestic", url="https://www.nebula-graph.io"),
    vendor("dgraph-labs", "Dgraph Labs", url="https://dgraph.io"),
    vendor("arangodb-inc", "ArangoDB", url="https://arangodb.com"),
    vendor("memgraph-inc", "Memgraph", url="https://memgraph.com"),
    vendor("linux-foundation", "Linux Foundation", url="https://www.linuxfoundation.org"),
    vendor("apache-software-foundation", "Apache 软件基金会", url="https://www.apache.org"),
    vendor("airbyte-inc", "Airbyte", url="https://airbyte.com"),
    vendor("fivetran-inc", "Fivetran", url="https://www.fivetran.com"),
    vendor("dbt-labs", "dbt Labs", url="https://www.getdbt.com"),
    vendor("dagster-labs", "Dagster Labs", url="https://dagster.io"),
    vendor("prefect-tech", "Prefect", url="https://www.prefect.io"),
]

EDGES_DATA: list[dict] = [
    # ——— 图数据库：叶内可比 ———
    edge(
        "e-nebulagraph-dom-neo4j",
        "nebulagraph",
        "neo4j",
        "domestic_equivalent_of",
        weight=0.8,
        note="国产分布式图库对标 Neo4j：存算分离横向扩容、国内支持，代价是 nGQL 与 Cypher 不等价",
    ),
    edge(
        "e-memgraph-alt-neo4j",
        "memgraph",
        "neo4j",
        "alternative_to",
        weight=0.75,
        note="同用 Cypher，但内存优先主打毫秒级实时图查询；容量受内存限制",
    ),
    edge(
        "e-dgraph-alt-neo4j",
        "dgraph",
        "neo4j",
        "alternative_to",
        weight=0.65,
        note="GraphQL 优先接口 + 自有 DQL 与分布式分片，换掉了 Cypher 与图算法工具链",
    ),
    edge(
        "e-arangodb-alt-neo4j",
        "arangodb",
        "neo4j",
        "alternative_to",
        weight=0.6,
        note="多模型库把文档与图放在一套 AQL 里；深度图分析与算法生态弱于专用图库",
    ),
    edge(
        "e-kuzu-alt-neo4j",
        "kuzu",
        "neo4j",
        "alternative_to",
        weight=0.55,
        note="嵌入式进程内、单文件落盘，适合本地分析；不提供集群与多写并发",
    ),
    edge(
        "e-janusgraph-alt-nebulagraph",
        "janusgraph",
        "nebulagraph",
        "alternative_to",
        weight=0.6,
        note="同为分布式图：JanusGraph 复用外部存储与 Gremlin，NebulaGraph 自带存储与 nGQL",
    ),
    # ——— 图数据库：跨叶挂接 ———
    edge(
        "e-janusgraph-dep-elasticsearch",
        "janusgraph",
        "elasticsearch",
        "depends_on",
        weight=0.7,
        note="全文与混合索引需外接搜索引擎，索引后端属于必选依赖而非可选增强",
    ),
    edge(
        "e-memgraph-int-kafka",
        "memgraph",
        "kafka",
        "integrates_with",
        weight=0.7,
        note="从消息流持续摄入并在图上触发计算，是其实时定位的关键一环",
    ),
    edge(
        "e-neo4j-cuw-langchain",
        "neo4j",
        "langchain",
        "commonly_used_with",
        weight=0.65,
        note="GraphRAG 常见组合：图库存实体关系，编排框架负责检索与提示拼装",
    ),
    edge(
        "e-nebulagraph-cuw-llamaindex",
        "nebulagraph",
        "llamaindex",
        "commonly_used_with",
        weight=0.55,
        note="知识图谱索引场景的国内常见搭配；图 schema 设计比框架选择更影响效果",
    ),
    edge(
        "e-neo4j-cuw-postgresql",
        "neo4j",
        "postgresql",
        "commonly_used_with",
        weight=0.45,
        note="业务主库仍在关系库，关系遍历旁路到图库；别把图库当唯一真相源，同步链路要有兜底",
    ),
    # ——— 数据管道：叶内可比 ———
    edge(
        "e-airbyte-osalt-fivetran",
        "airbyte",
        "fivetran",
        "open_source_alternative_to",
        weight=0.85,
        note="开源自托管换掉按行计费与数据出网，代价是连接器质量与运维要自己扛",
    ),
    edge(
        "e-apache-seatunnel-osalt-fivetran",
        "apache-seatunnel",
        "fivetran",
        "open_source_alternative_to",
        weight=0.65,
        note="偏大批量库到库与湖仓同步的开源替代；SaaS 连接器覆盖远不如托管服务",
    ),
    edge(
        "e-datax-dom-airbyte",
        "datax",
        "airbyte",
        "domestic_equivalent_of",
        weight=0.7,
        note="国内离线同步的老牌选择：部署更轻、内网友好，但单机不可扩且不含调度与实时 CDC",
    ),
    edge(
        "e-apache-seatunnel-alt-datax",
        "apache-seatunnel",
        "datax",
        "alternative_to",
        weight=0.8,
        note="同为国产同步工具：SeaTunnel 可分布式并支持流与 CDC，DataX 是单进程离线跑批",
    ),
    edge(
        "e-dagster-alt-apache-airflow",
        "dagster",
        "apache-airflow",
        "alternative_to",
        weight=0.8,
        note="以数据资产为中心 vs 以任务为中心；血缘与新鲜度内建，但集成广度不及 Airflow",
    ),
    edge(
        "e-prefect-alt-apache-airflow",
        "prefect",
        "apache-airflow",
        "alternative_to",
        weight=0.75,
        note="运行时动态生成依赖图、装饰器改造脚本更轻；Provider 生态与企业沉淀不如 Airflow",
    ),
    edge(
        "e-dbt-cuw-apache-airflow",
        "dbt",
        "apache-airflow",
        "commonly_used_with",
        weight=0.8,
        note="dbt 只管仓内转换，触发时机与上下游依赖交给调度器，是最常见的分工",
    ),
    edge(
        "e-dbt-cuw-fivetran",
        "dbt",
        "fivetran",
        "commonly_used_with",
        weight=0.75,
        note="EL 与 T 的经典组合：托管同步负责落仓，dbt 负责建模、测试与血缘",
    ),
    edge(
        "e-dagster-int-dbt",
        "dagster",
        "dbt",
        "integrates_with",
        weight=0.75,
        note="dbt 模型可直接映射成编排层的数据资产，血缘在一处呈现，无需两套依赖图",
    ),
    edge(
        "e-apache-seatunnel-int-apache-flink",
        "apache-seatunnel",
        "apache-flink",
        "integrates_with",
        weight=0.7,
        note="可把同步作业提交到 Flink 集群执行，复用已有的实时计算底座",
    ),
    edge(
        "e-debezium-dep-kafka",
        "debezium",
        "kafka",
        "depends_on",
        weight=0.8,
        note="最常见部署形态依赖消息平台的连接器运行时；嵌入式引擎可绕开但需自己保证投递",
    ),
    edge(
        "e-debezium-cuw-apache-flink",
        "debezium",
        "apache-flink",
        "commonly_used_with",
        weight=0.75,
        note="变更事件进流处理引擎做实时宽表与实时数仓，是实时链路的标准两段",
    ),
    edge(
        "e-debezium-int-postgresql",
        "debezium",
        "postgresql",
        "integrates_with",
        weight=0.8,
        note="基于逻辑复制读取变更；复制槽未消费会累积 WAL，磁盘水位需单独告警",
    ),
    edge(
        "e-airbyte-int-postgresql",
        "airbyte",
        "postgresql",
        "integrates_with",
        weight=0.7,
        note="既可作来源也可作目的地，增量同步模式的选择直接决定源库压力",
    ),
    edge(
        "e-dbt-int-postgresql",
        "dbt",
        "postgresql",
        "integrates_with",
        weight=0.6,
        note="通过适配器把关系库当轻量数仓用；数据量上来后仍需迁往列存仓库",
    ),
    edge(
        "e-apache-flink-int-apache-pulsar",
        "apache-flink",
        "apache-pulsar",
        "integrates_with",
        weight=0.6,
        note="除 Kafka 外的消息源选择；连接器成熟度与社区活跃度需按版本核对",
    ),
    edge(
        "e-apache-flink-cuw-grafana",
        "apache-flink",
        "grafana",
        "commonly_used_with",
        weight=0.55,
        note="作业指标外送后用看板盯反压与检查点耗时，是流作业可观测的常规做法",
    ),
    edge(
        "e-apache-seatunnel-int-nebulagraph",
        "apache-seatunnel",
        "nebulagraph",
        "integrates_with",
        weight=0.5,
        confidence="inferred",
        note="批量把关系数据灌进图库的常见路径；点边映射与去重规则需在作业里自行约定",
    ),
    # ——— 与应用侧任务编排划清界限（不同层，勿混比）———
    edge(
        "e-apache-airflow-alt-n8n",
        "apache-airflow",
        "n8n",
        "alternative_to",
        weight=0.4,
        note="不同层：Airflow 是数据工程批处理调度，n8n 是应用与 SaaS 之间的自动化连线，勿横向比吞吐",
    ),
    edge(
        "e-apache-airflow-alt-inngest",
        "apache-airflow",
        "inngest",
        "alternative_to",
        weight=0.4,
        note="不同层：批处理 DAG 回填重跑 vs 应用事件驱动的持久化函数，选型问题不同",
    ),
    edge(
        "e-dagster-alt-trigger-dev",
        "dagster",
        "trigger-dev",
        "alternative_to",
        weight=0.4,
        note="不同层：数据资产编排 vs 应用后台任务；同叫「编排」但关心的对象不是一回事",
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
    for e in ENTRIES_DATA:
        path = ENTRIES / f"{e['id']}.json"
        if path.exists() and not args.overwrite:
            print("skip entry", e["id"])
            continue
        save(path, e)
        wrote_e += 1
        print("entry", e["id"])

    for v in VENDORS_DATA:
        path = VENDORS / f"{v['id']}.json"
        if path.exists() and not args.overwrite:
            print("skip vendor", v["id"])
            continue
        save(path, v)
        wrote_v += 1
        print("vendor", v["id"])

    known_new = {x["id"] for x in ENTRIES_DATA}
    for g in EDGES_DATA:
        path = EDGES / f"{g['id']}.json"
        if path.exists() and not args.overwrite:
            print("skip edge", g["id"])
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
