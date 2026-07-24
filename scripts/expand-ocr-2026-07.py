#!/usr/bin/env python3
"""OCR / 文档智能扩种：新叶 ai-ocr + 开源引擎 / 云 Document AI / 国内云。

用法:
  python3 scripts/expand-ocr-2026-07.py
  python3 scripts/expand-ocr-2026-07.py --overwrite
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
REVIEWED = "2026-07-24"


def save(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def entry(**kw) -> dict:
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
    assert len(e["oneLiner"]) <= 60, (e["id"], len(e["oneLiner"]), e["oneLiner"])
    assert len(e.get("descriptionMd", "")) >= 120, (e["id"], len(e.get("descriptionMd", "")))
    assert e.get("pitfalls"), e["id"]
    assert e.get("subcategory"), e["id"]
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
        "pitfalls": pitfalls or [caution[:80]],
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


CN = {
    "chinaAccessible": True,
    "needsCompany": False,
    "needsIcp": False,
    "regions": ["CN"],
}
US_BLOCKED = {
    "chinaAccessible": False,
    "needsCompany": False,
    "needsIcp": False,
    "regions": ["global"],
}

ENTRIES_DATA: list[dict] = [
    # —— 开源引擎 / 文档解析 ——
    mk(
        "paddleocr",
        "PaddleOCR",
        "ai-ocr",
        "ocr-engine",
        "开源 OCR 主力 · 中文/版面 · 可自托管",
        "https://github.com/PaddlePaddle/PaddleOCR",
        "PaddleOCR 是飞桨生态的开源 OCR 与文档解析工具包，覆盖检测、识别、版面分析与多语（含中文优势），可本地/私有化部署，也可走云端 API 形态。",
        "需要中文/复杂版面、扫描件进 RAG、或数据不出域自托管时优先评估；与 Tesseract/EasyOCR 同层对照。",
        "模型与依赖体积不小；高并发生产需自建服务化与 GPU 策略，勿当「装包即 SLA」。",
        vendorId="baidu",
        region="both",
        tags=["ocr", "open-source", "chinese", "layout"],
        pricing={"model": "open-source"},
        githubUrl="https://github.com/PaddlePaddle/PaddleOCR",
        maturity="mature",
    ),
    mk(
        "tesseract",
        "Tesseract",
        "ai-ocr",
        "ocr-engine",
        "经典开源 OCR · CPU 友好 · 基线方案",
        "https://github.com/tesseract-ocr/tesseract",
        "Tesseract 是历史最久的开源 OCR 引擎之一（现由社区维护），适合干净印刷体、多语基础识别与嵌入式/低成本 CPU 场景，常作管线基线。",
        "扫描质量高、预算为零、或要嵌入本地工具链做 baseline 时选用；复杂表格/手写应升级 PaddleOCR 或云 Document AI。",
        "对倾斜、噪声、复杂版面与手写较弱；生产前必须加图像预处理与置信度门槛。",
        tags=["ocr", "open-source", "baseline"],
        pricing={"model": "open-source"},
        githubUrl="https://github.com/tesseract-ocr/tesseract",
        maturity="mature",
    ),
    mk(
        "easyocr",
        "EasyOCR",
        "ai-ocr",
        "ocr-engine",
        "Python 易用 OCR · 多语原型快",
        "https://github.com/JaidedAI/EasyOCR",
        "EasyOCR 提供开箱即用的 Python OCR 接口与多语模型，上手快，适合原型与中小批量图片文字抽取。",
        "需要几天内跑通多语截图/证件文字抽取 POC 时评估；中文重版面场景再对照 PaddleOCR。",
        "大规模吞吐与版面结构化不如专用文档智能；依赖与模型下载需纳入部署。",
        vendorId="jaided-ai",
        tags=["ocr", "open-source", "python"],
        pricing={"model": "open-source"},
        githubUrl="https://github.com/JaidedAI/EasyOCR",
    ),
    mk(
        "mineru",
        "MinerU",
        "ai-ocr",
        "doc-parse",
        "文档→Markdown · 高保真解析 · 开源",
        "https://github.com/opendatalab/MinerU",
        "MinerU 专注把 PDF/文档转为结构清晰的 Markdown/内容块，强调版面与阅读顺序保真，常作 RAG/知识库入库前的文档智能层。",
        "论文、报告、复杂 PDF 需要「可读 Markdown」而非纯字符框时优先；可与向量库/Unstructured 管线衔接。",
        "资源占用与模型版本需锁定；扫描件质量差时仍依赖上游 OCR 能力。",
        vendorId="opendatalab",
        region="both",
        tags=["ocr", "doc-parse", "markdown", "open-source", "rag"],
        pricing={"model": "open-source"},
        githubUrl="https://github.com/opendatalab/MinerU",
    ),
    mk(
        "docling",
        "Docling",
        "ai-ocr",
        "doc-parse",
        "IBM 开源文档解析 · PDF→结构化",
        "https://github.com/docling-project/docling",
        "Docling 是面向开发者的开源文档转换/理解工具，把 PDF 等转为结构化表示，便于 LLM 与 RAG 消费，社区增长快。",
        "需要本地可控的文档解析、与 Python AI 栈集成时评估；可与云 Document AI 做成本对照。",
        "企业预置发票/证件模型不如 Azure/AWS；极端扫描件需另配 OCR 引擎。",
        vendorId="ibm",
        tags=["ocr", "doc-parse", "open-source", "rag"],
        pricing={"model": "open-source"},
        githubUrl="https://github.com/docling-project/docling",
    ),
    mk(
        "marker-pdf",
        "Marker",
        "ai-ocr",
        "doc-parse",
        "PDF→Markdown/JSON · 高速转换",
        "https://github.com/datalab-to/marker",
        "Marker 把 PDF 快速转为 Markdown/JSON 等，强调速度与结构保留，适合批量文献与知识库预处理。",
        "大批量 PDF 要进 Markdown 语料、自托管优先时评估；与 MinerU/Docling 同层试样张。",
        "表格/公式边界案例需抽检；许可证与商用条款以仓库为准。",
        vendorId="datalab-to",
        tags=["ocr", "doc-parse", "markdown", "open-source"],
        pricing={"model": "open-source"},
        githubUrl="https://github.com/datalab-to/marker",
    ),
    # —— 云 Document AI / Vision OCR ——
    mk(
        "aws-textract",
        "Amazon Textract",
        "ai-ocr",
        "document-ai",
        "AWS 表单/表格抽取 · 费用/证件 API",
        "https://aws.amazon.com/textract/",
        "Amazon Textract 在 OCR 之上提供表格、键值对、查询与费用/证件等专用分析，深度绑定 S3/Lambda/Step Functions，适合 AWS 原生文档流水线。",
        "单据、合同、发票已在 AWS，需要结构化字段而非纯文本时优先。",
        "按页/功能计费；非 AWS 栈迁移成本高；中文复杂版面需实测。",
        vendorId="amazon",
        tags=["ocr", "document-ai", "aws", "forms"],
        pricing={"model": "usage", "currency": "USD"},
        maturity="mature",
    ),
    mk(
        "google-document-ai",
        "Google Document AI",
        "ai-ocr",
        "document-ai",
        "GCP 文档处理器 · 预置/自定义抽取",
        "https://cloud.google.com/document-ai",
        "Google Document AI 提供文档拆分、分类与预置/自定义处理器，覆盖发票、合同等，并与 Vision OCR 能力互补，面向 GCP 企业文档自动化。",
        "已在 Google Cloud、需要处理器工作台与标签流程时评估；纯截图 OCR 也可看 Vision API。",
        "国内直连受限；定制处理器有学习与标注成本。",
        vendorId="google",
        tags=["ocr", "document-ai", "gcp"],
        pricing={"model": "usage", "currency": "USD"},
        availability=US_BLOCKED,
        maturity="mature",
    ),
    mk(
        "google-vision-ocr",
        "Google Cloud Vision OCR",
        "ai-ocr",
        "ocr-api",
        "GCP Vision 文字检测 · 图内 OCR",
        "https://cloud.google.com/vision/docs/ocr",
        "Google Cloud Vision 的 TEXT_DETECTION / DOCUMENT_TEXT_DETECTION 提供图内与密文 OCR，适合照片、截图与多语文字定位，常与 Document AI 分工（图 vs 业务文档）。",
        "移动端拍照识字、UI 截图抽取、多语自然场景文字时评估。",
        "复杂多栏业务 PDF 更宜 Document AI/Textract；国内可达性受限。",
        vendorId="google",
        tags=["ocr", "vision", "gcp"],
        pricing={"model": "usage", "currency": "USD"},
        availability=US_BLOCKED,
        maturity="mature",
    ),
    mk(
        "azure-document-intelligence",
        "Azure AI Document Intelligence",
        "ai-ocr",
        "document-ai",
        "微软文档智能 · 预置发票/证件 · Read OCR",
        "https://azure.microsoft.com/products/ai-services/ai-document-intelligence",
        "原 Form Recognizer，现 Azure AI Document Intelligence，提供 Read OCR 与发票、收据、证件等预置模型及自定义训练，适合微软生态企业文档自动化。",
        "已在 Azure、需要预置业务文档模型与身份合规一体时优先。",
        "与纯开源引擎比按页成本更高；非微软栈要评估锁定。",
        vendorId="microsoft",
        tags=["ocr", "document-ai", "azure", "forms"],
        pricing={"model": "usage", "currency": "USD"},
        maturity="mature",
    ),
    mk(
        "mistral-ocr",
        "Mistral OCR",
        "ai-ocr",
        "ocr-api",
        "Mistral 文档 OCR API · 版面理解",
        "https://mistral.ai/news/mistral-ocr",
        "Mistral OCR 以 API 形式提供文档/图像文字与结构理解，面向开发者把扫描件与 PDF 送入 LLM 工作流前的识别层，强调易用与质量。",
        "已用 Mistral 栈、需要云端文档 OCR 且不愿上三大云 Document AI 时评估。",
        "企业预置发票工作流与区域合规成熟度对照 Azure/AWS；价格与限速以控制台为准。",
        vendorId="mistral-ai",
        tags=["ocr", "api", "mistral"],
        pricing={"model": "usage", "currency": "USD"},
        availability=US_BLOCKED,
        maturity="beta",
    ),
    mk(
        "llamaparse",
        "LlamaParse",
        "ai-ocr",
        "doc-parse",
        "LlamaIndex 文档解析 · RAG 友好",
        "https://docs.cloud.llamaindex.ai/llamacloud/guides/parse",
        "LlamaParse 是 LlamaCloud/LlamaIndex 生态的文档解析服务，把复杂 PDF 转为 LLM 友好结构，常与 LlamaIndex 索引管线一体使用。",
        "已用 LlamaIndex 做 RAG、PDF 版面复杂需要托管解析时评估；可与 Unstructured/MinerU 对照。",
        "绑定 LlamaCloud 账单与配额；纯自托管需求应看开源解析器。",
        vendorId="llamaindex-inc",
        tags=["ocr", "doc-parse", "rag", "llamaindex"],
        pricing={"model": "usage", "currency": "USD"},
    ),
    # —— 国内云 OCR ——
    mk(
        "aliyun-ocr",
        "阿里云 OCR",
        "ai-ocr",
        "ocr-api",
        "阿里云文字识别 · 证件/票据 · 国内",
        "https://www.aliyun.com/product/ocr",
        "阿里云 OCR（文字识别）提供通用印刷体、手写、证件、票据、表格等 API，面向国内 App 与政企影像录入，可与百炼/OSS 同区落地。",
        "国内业务需要证件/发票结构化、备案业务同云时优先；开源自托管对照 PaddleOCR。",
        "按次计费与 QPS 套餐需测算；复杂版式与小语种效果要抽样评测。",
        vendorId="alibaba-cloud",
        region="domestic",
        tags=["ocr", "domestic", "forms"],
        pricing={"model": "usage", "currency": "CNY"},
        availability=CN,
        maturity="mature",
    ),
    mk(
        "tencent-ocr",
        "腾讯云 OCR",
        "ai-ocr",
        "ocr-api",
        "腾讯云文字识别 · 卡证/票据 · 国内",
        "https://cloud.tencent.com/product/ocr",
        "腾讯云 OCR 提供通用与卡证、票据、车牌等场景识别，适合微信/腾讯云生态内的影像与证照采集。",
        "已在腾讯云或微信小程序需要识字/证照时评估；与阿里云 OCR、百度 OCR 同层比价比效果。",
        "接口与套餐偏国内云风格；出海多语场景需另测国际引擎。",
        vendorId="tencent-cloud",
        region="domestic",
        tags=["ocr", "domestic"],
        pricing={"model": "usage", "currency": "CNY"},
        availability=CN,
        maturity="mature",
    ),
    mk(
        "baidu-ocr",
        "百度智能云 OCR",
        "ai-ocr",
        "ocr-api",
        "百度文字识别 · 与 PaddleOCR 同源叙事",
        "https://cloud.baidu.com/product/ocr",
        "百度智能云 OCR 提供通用与卡证票据等 API，技术栈与飞桨/PaddleOCR 叙事相邻，长期服务国内影像识别与 ToB 录入。",
        "存量百度云客户，或要云 API + 开源 PaddleOCR 双轨时评估。",
        "新产品也可直接自托管 PaddleOCR 降本；云 API 适合要 SLA 与证照模板的团队。",
        vendorId="baidu",
        region="domestic",
        tags=["ocr", "domestic"],
        pricing={"model": "usage", "currency": "CNY"},
        availability=CN,
        maturity="mature",
    ),
    mk(
        "huawei-ocr",
        "华为云 OCR",
        "ai-ocr",
        "ocr-api",
        "华为云文字识别 · 政企/行业向",
        "https://www.huaweicloud.com/product/ocr.html",
        "华为云 OCR 提供通用文字与卡证票据等识别能力，面向国内政企与行业云客户，强调合规落地与行业方案包装。",
        "已在华为云、招投标要求国产云栈或行业云时评估；效果用业务样张与阿里/腾讯对照。",
        "开发者社区与 indie 文档热度通常弱于阿里/腾讯；效果需用业务样张实测。",
        vendorId="huawei-cloud",
        region="domestic",
        tags=["ocr", "domestic", "enterprise"],
        pricing={"model": "usage", "currency": "CNY"},
        availability=CN,
    ),
    # —— 企业 / 垂直 IDP ——
    mk(
        "abbyy",
        "ABBYY",
        "ai-ocr",
        "document-ai",
        "企业 IDP · FineReader/Vantage · 合规向",
        "https://www.abbyy.com",
        "ABBYY 是传统企业文档智能（IDP）厂商，FineReader/Vantage 等产品覆盖高精 OCR、分类与人工审核工作流，受监管行业常见。",
        "银行/保险/大型共享服务中心需要审核台与合规交付时评估；创业团队通常先开源或三大云。",
        "许可与实施成本高；与现代 API-first 文档 AI 的 DX 不同。",
        vendorId="abbyy-inc",
        tags=["ocr", "document-ai", "enterprise", "idp"],
        pricing={"model": "subscription", "currency": "USD"},
        maturity="mature",
    ),
    mk(
        "nanonets",
        "Nanonets",
        "ai-ocr",
        "document-ai",
        "单据 AI 抽取 · 发票/表格 · 少样本",
        "https://nanonets.com",
        "Nanonets 面向发票、收据、表格等业务单据的 AI 抽取与自动化，强调少样本训练与工作流，属于现代 IDP/文档自动化赛道。",
        "中小团队要快速上线单据字段抽取、不愿自建标注平台时评估。",
        "深度定制与私有化弱于大型 IDP；中文单据效果需实测。",
        vendorId="nanonets-inc",
        tags=["ocr", "document-ai", "invoices"],
        pricing={"model": "subscription", "currency": "USD"},
    ),
]

VENDORS_DATA: list[dict] = [
    vendor("jaided-ai", "Jaided AI", url="https://www.jaided.ai"),
    vendor("opendatalab", "OpenDataLab / MinerU", region="both", url="https://opendatalab.com"),
    vendor("datalab-to", "Datalab", url="https://www.datalab.to"),
    vendor("llamaindex-inc", "LlamaIndex", url="https://www.llamaindex.ai"),
    vendor("abbyy-inc", "ABBYY", url="https://www.abbyy.com"),
    vendor("nanonets-inc", "Nanonets", url="https://nanonets.com"),
    vendor("huawei-cloud", "华为云", region="domestic", url="https://www.huaweicloud.com"),
]

EDGES_DATA: list[dict] = [
    edge("edge-paddleocr-tesseract-alt", "paddleocr", "tesseract", "alternative_to", note="现代深度学习 vs 经典基线"),
    edge("edge-paddleocr-easyocr-alt", "paddleocr", "easyocr", "alternative_to"),
    edge("edge-easyocr-tesseract-alt", "easyocr", "tesseract", "alternative_to"),
    edge("edge-mineru-docling-alt", "mineru", "docling", "alternative_to", note="文档→结构化/Markdown"),
    edge("edge-marker-mineru-alt", "marker-pdf", "mineru", "alternative_to"),
    edge("edge-docling-marker-alt", "docling", "marker-pdf", "alternative_to"),
    edge("edge-textract-docai-alt", "aws-textract", "google-document-ai", "alternative_to"),
    edge("edge-azure-di-textract-alt", "azure-document-intelligence", "aws-textract", "alternative_to"),
    edge("edge-azure-di-docai-alt", "azure-document-intelligence", "google-document-ai", "alternative_to"),
    edge("edge-vision-ocr-docai-with", "google-vision-ocr", "google-document-ai", "commonly_used_with", note="图内 OCR vs 业务文档处理器"),
    edge("edge-mistral-ocr-docai-alt", "mistral-ocr", "google-document-ai", "alternative_to", weight=0.55),
    edge("edge-llamaparse-unstructured-alt", "llamaparse", "unstructured", "alternative_to", note="RAG 文档预处理"),
    edge("edge-mineru-unstructured-alt", "mineru", "unstructured", "alternative_to"),
    edge("edge-docling-unstructured-alt", "docling", "unstructured", "alternative_to"),
    edge("edge-aliyun-ocr-textract-dom", "aliyun-ocr", "aws-textract", "domestic_equivalent_of"),
    edge("edge-tencent-ocr-azure-dom", "tencent-ocr", "azure-document-intelligence", "domestic_equivalent_of"),
    edge("edge-baidu-ocr-aliyun-alt", "baidu-ocr", "aliyun-ocr", "alternative_to"),
    edge("edge-huawei-ocr-aliyun-alt", "huawei-ocr", "aliyun-ocr", "alternative_to"),
    edge("edge-baidu-ocr-paddleocr-with", "baidu-ocr", "paddleocr", "commonly_used_with", note="云 API + 开源同源叙事"),
    edge("edge-abbyy-azure-di-alt", "abbyy", "azure-document-intelligence", "alternative_to", weight=0.55),
    edge("edge-nanonets-textract-alt", "nanonets", "aws-textract", "alternative_to", weight=0.6),
    edge("edge-paddleocr-aliyun-os", "paddleocr", "aliyun-ocr", "open_source_alternative_to"),
]


def write_item(dir_path: Path, item: dict, overwrite: bool) -> bool:
    path = dir_path / f"{item['id']}.json"
    if path.exists() and not overwrite:
        return False
    save(path, item)
    return True


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--overwrite", action="store_true")
    args = ap.parse_args()

    # ensure ibm vendor exists for docling
    if not (VENDORS / "ibm.json").exists():
        write_item(VENDORS, vendor("ibm", "IBM", url="https://www.ibm.com"), True)

    # llamaindex vendor — may already exist under different id
    existing_v = {p.stem for p in VENDORS.glob("*.json")}
    if "llamaindex-inc" not in existing_v and "llamaindex" in existing_v:
        for e in ENTRIES_DATA:
            if e.get("vendorId") == "llamaindex-inc":
                e["vendorId"] = "llamaindex"

    ea = va = eda = 0
    for e in ENTRIES_DATA:
        if write_item(ENTRIES, e, args.overwrite):
            ea += 1
    for v in VENDORS_DATA:
        if write_item(VENDORS, v, args.overwrite):
            va += 1
    for ed in EDGES_DATA:
        if write_item(EDGES, ed, args.overwrite):
            eda += 1

    print(
        f"done: +entries={ea} +vendors={va} +edges={eda} "
        f"total_entries={len(list(ENTRIES.glob('*.json')))} "
        f"total_edges={len(list(EDGES.glob('*.json')))} "
        f"total_vendors={len(list(VENDORS.glob('*.json')))}"
    )


if __name__ == "__main__":
    main()
